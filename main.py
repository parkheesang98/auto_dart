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

SENT_FILE = "sent_reports.txt"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=30
    )


def summarize_with_claude(text):

    if not ANTHROPIC_API_KEY or Anthropic is None:
        return None

    try:
        client = Anthropic(
            api_key=ANTHROPIC_API_KEY
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"""
아래 공시를 투자자 관점에서 3줄 이내로 요약해줘.

{text}
"""
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        print("Claude Error:", e)
        return None


def load_sent_reports():

    if not os.path.exists(SENT_FILE):
        return set()

    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return set(
            line.strip()
            for line in f.readlines()
            if line.strip()
        )


def save_sent_report(rcept_no):

    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{rcept_no}\n")


sent_reports = load_sent_reports()

end_date = datetime.today()
start_date = end_date - timedelta(days=7)

url = "https://opendart.fss.or.kr/api/list.json"

params = {
    "crtfc_key": DART_API_KEY,
    "bgn_de": start_date.strftime("%Y%m%d"),
    "end_de": end_date.strftime("%Y%m%d"),
    "page_no": 1,
    "page_count": 100
}

response = requests.get(
    url,
    params=params,
    timeout=30
)

data = response.json()

reports = data.get("list", [])

print("Reports:", len(reports))

for item in reports:

    filer = item.get("flr_nm", "")
    report_nm = item.get("report_nm", "")

    if filer != "국민연금공단":
        continue

    if "주식등의대량보유상황보고서" not in report_nm:
        continue

    rcept_no = item.get("rcept_no")

    if rcept_no in sent_reports:
        continue

    corp_name = item.get("corp_name")
    rcept_dt = item.get("rcept_dt")

    base_text = f"""
[국민연금 신규 공시]

종목: {corp_name}
공시: {report_nm}
접수일: {rcept_dt}
접수번호: {rcept_no}
"""

    summary = summarize_with_claude(base_text)

    if summary:
        message = (
            f"{base_text}\n\n"
            f"[Claude 요약]\n"
            f"{summary}"
        )
    else:
        message = base_text

    send_telegram(message)

    save_sent_report(rcept_no)

    print(
        f"Sent: {corp_name} / {rcept_no}"
    )
