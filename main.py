from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


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


# Telegram 테스트
send_telegram("✅ GitHub Actions Telegram Test")
print("Telegram test sent")

end_date = datetime.today()
start_date = end_date - timedelta(days=7)

url = "https://opendart.fss.or.kr/api/list.json"

params = {
    "crtfc_key": DART_API_KEY,
    "bgn_de": start_date.strftime("%Y%m%d"),
    "end_de": end_date.strftime("%Y%m%d"),
    "page_no": 1,
    "page_count": 100,
    # "last_reprt_at": "Y"
}

response = requests.get(url, params=params, timeout=30)
data = response.json()

print("DART status:", data.get("status"))
print("DART message:", data.get("message"))

reports = data.get("list", [])

print("Reports count:", len(reports))

print("\n===== 최근 공시 10건 =====")

for item in reports[:10]:
    print(
        item.get("corp_name"),
        "|",
        item.get("report_nm"),
        "|",
        item.get("flr_nm")
    )

for item in reports:

    filer = item.get("flr_nm", "")
    report_nm = item.get("report_nm", "")

    if filer != "국민연금공단":
        continue

    if "주식등의대량보유상황보고서" not in report_nm:
        continue

    corp_name = item.get("corp_name")
    rcept_dt = item.get("rcept_dt")

    message = f"""
[국민연금 신규 공시]

종목: {corp_name}
공시: {report_nm}
접수일: {rcept_dt}
"""

    send_telegram(message)

    print(message)

print("=========================\n")

if reports:
    item = reports[0]

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

else:
    print("조회된 공시 없음")
