import os
from datetime import datetime

# --- 설정 값 읽어오기 ---
# GitHub Secrets에서 값을 가져와 변수에 저장합니다.
# 만약 값을 못 찾으면 "Not Found" 라는 글자를 대신 사용합니다.
to_email_address = os.environ.get("TO_EMAIL", "TO_EMAIL Not Found")
from_email_address = os.environ.get("FROM_EMAIL", "FROM_EMAIL Not Found")
openai_key = os.environ.get("OPENAI_API_KEY", "OPENAI_KEY Not Found")
sendgrid_key = os.environ.get("SENDGRID_API_KEY", "SENDGRID_KEY Not Found")

print("==============================================")
print("      <<< GitHub Secrets 값 확인 테스트 >>>     ")
print("==============================================")
print(f"현재 시간: {datetime.now()}")
print(f"받는 사람 (TO_EMAIL): {to_email_address}")
print(f"보내는 사람 (FROM_EMAIL): {from_email_address}")

# 실제 API 키 값 대신, 키가 제대로 읽혔는지 여부만 출력합니다.
if "Not Found" in openai_key:
    print("OpenAI API 키: 🔴 찾지 못했습니다!")
else:
    print("OpenAI API 키: 🟢 성공적으로 읽었습니다.")

if "Not Found" in sendgrid_key:
    print("SendGrid API 키: 🔴 찾지 못했습니다!")
else:
    print("SendGrid API 키: 🟢 성공적으로 읽었습니다.")
    
print("\n테스트가 성공적으로 완료되었습니다.")
print("만약 위 모든 값이 제대로 보인다면, 이제 원래 코드로 되돌려도 좋습니다.")
print("==============================================")
