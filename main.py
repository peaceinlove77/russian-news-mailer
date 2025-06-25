import os
import feedparser
import openai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

# --- 설정 부분 ---
openai.api_key = os.environ.get("OPENAI_API_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")

RUSSIAN_NEWS_FEEDS = {
    "리아노보스티 (경제)": "https://ria.ru/export/rss2/economy/index.xml",
    "인테르팍스 (주요뉴스)": "https://www.interfax.ru/rss.asp",
    "코메르산트 (주요뉴스)": "https://www.kommersant.ru/RSS/main.xml",
    "메두자 (독립언론)": "https://meduza.io/rss/all"
}
# --- 설정 끝 ---

def get_latest_news(feed_url, limit=3):
    print(f"'{feed_url}'에서 뉴스 가져오는 중...")
    feed = feedparser.parse(feed_url)
    return feed.entries[:limit]

def translate_and_summarize(article_title, article_link):
    print(f"'{article_title}' 번역 및 요약 중...")
    try:
        prompt = f"""
        러시아어 뉴스 기사 제목과 링크가 주어집니다.
        1. 제목을 자연스러운 한국어로 번역해주세요.
        2. 기사 내용을 상상하여, 한국인 독자가 이해하기 쉽게 한두 문장으로 핵심 내용을 요약해주세요.

        - 기사 제목: {article_title}
        - 기사 링크: {article_link}

        결과는 아래 형식에 맞춰 한국어로만 작성해주세요:

        - 번역된 제목: [여기에 번역된 제목]
        - 핵심 요약: [여기에 요약 내용]
        """
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 러시아 뉴스를 한국어로 번역하고 요약하는 전문 에디터입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API 오류 발생: {e}")
        return f"- 번역된 제목: {article_title} (번역 실패)\n- 핵심 요약: 내용을 가져오는 데 실패했습니다."

def create_html_email(news_data):
    print("HTML 이메일 본문 생성 중...")
    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #555; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
            .news-item {{ margin-bottom: 20px; }}
            .news-item h3 {{ margin-bottom: 5px; }}
            .news-item a {{ color: #007BFF; text-decoration: none; }}
            .summary {{ color: #666; }}
            .footer {{ margin-top: 30px; font-size: 0.8em; color: #999; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🇷🇺 오늘의 러시아 주요 뉴스 ({today_str})</h1>
    """
    for source, articles in news_data.items():
        html_content += f"<h2>{source}</h2>"
        for article in articles:
            translated_title = "제목을 가져오지 못했습니다."
            summary_text = "요약을 가져오지 못했습니다."
            try:
                lines = article['summary'].split('\n')
                for line in lines:
                    if line.startswith("- 번역된 제목:"):
                        translated_title = line.replace("- 번역된 제목:", "").strip()
                    elif line.startswith("- 핵심 요약:"):
                        summary_text = line.replace("- 핵심 요약:", "").strip()
            except Exception:
                pass
            html_content += f"""
            <div class="news-item">
                <h3><a href="{article['link']}" target="_blank">{translated_title}</a></h3>
                <p class="summary">{summary_text}</p>
            </div>
            """
    html_content += """
            <p class="footer">이 메일은 Python 스크립트를 통해 자동 발송되었습니다.</p>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(subject, html_body):
    print(f"'{TO_EMAIL}' 주소로 이메일 발송 시도...")
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,
            subject=subject,
            html_content=html_body
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"이메일 발송 성공! (상태 코드: {response.status_code})")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

if __name__ == "__main__":
    all_news = {}
    for source_name, feed_url in RUSSIAN_NEWS_FEEDS.items():
        latest_articles = get_latest_news(feed_url, limit=3)
        translated_articles = []
        for article in latest_articles:
            summary = translate_and_summarize(article.title, article.link)
            translated_articles.append({
                "title": article.title,
                "link": article.link,
                "summary": summary
            })
        all_news[source_name] = translated_articles
    email_html = create_html_email(all_news)
    email_subject = f"📰 {datetime.now().strftime('%Y-%m-%d')} 러시아 뉴스 브리핑"
    send_email(email_subject, email_html)
    print("\n모든 작업이 완료되었습니다.")
