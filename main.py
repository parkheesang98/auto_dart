from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta

try:
    from anthropic import Anthropic
except:
    Anthropic = None

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=30
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)


# =========================
# 테스트 메시지
# =========================
send_telegram("✅ GitHub Actions Telegram Test")
print("Telegram test sent")


def summarize_with_claude(text):

    if not ANTHROPIC_API_KEY or Anthropic is None:
        return None

    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"""
다음 DART 공시 정보를 투자자 관점에서 3줄 이내로 요약해줘.

{text}
"""
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        print("Claude Error:", e)
        return None


end_date = datetime.today()
start_date = end_date - timedelta(days=1)

url = "https://opendart.fss.or.kr/api/list.json"

params = {
    "crtfc_key": DART_API_KEY,
    "bgn_de": start_date.strftime("%Y%m%d"),
    "end_de": end_date.strftime("%Y%m%d"),
    "page_no": 1,
    "page_count": 100,
    "last_reprt_at": "Y"
}

response = requests.get(url, params=params, timeout=30)
data = response.json()

print("DART status:", data.get("status"))
print("DART message:", data.get("message"))

reports = data.get("list", [])

print("Reports count:", len(reports))

for item in reports:

    corp_name = item.get("corp_name")
    report_nm = item.get("report_nm")
    filer = item.get("flr_nm")

    message = f"""
[DART 테스트]

종목: {corp_name}
공시: {report_nm}
제출자: {filer}
"""

    send_telegram(message)

    print(message)

    break

    corp_name = item.get("corp_name")
    rcept_dt = item.get("rcept_dt")
    rcept_no = item.get("rcept_no")

    base_text = f"""
[국민연금 신규 공시]

종목: {corp_name}
공시: {report_nm}
접수일: {rcept_dt}
접수번호: {rcept_no}
"""

    summary = summarize_with_claude(base_text)

    if summary:
        message = f"{base_text}\n\n[Claude 요약]\n{summary}"
    else:
        message = base_text

    send_telegram(message)

    print(message)
