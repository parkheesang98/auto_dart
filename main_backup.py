from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")

end_date = datetime.today()
start_date = end_date - timedelta(days=7)

url = "https://opendart.fss.or.kr/api/list.json"

params = {
"crtfc_key": DART_API_KEY,
"bgn_de": start_date.strftime("%Y%m%d"),
"end_de": end_date.strftime("%Y%m%d"),
"page_no": 1,
"page_count": 100,
"last_reprt_at": "Y"
}

response = requests.get(url, params=params)
data = response.json()

print("상태코드:", data.get("status"))
print("메시지:", data.get("message"))
print("전체 페이지:", data.get("total_page"))
print("전체 건수:", data.get("total_count"))

print()
print("=== 국민/연금 포함 제출자 검색 ===")
for item in data.get("list", []):

    filer = item.get("flr_nm", "")

    if "국민" in filer or "연금" in filer:

        print("-----")
        print("회사:", item.get("corp_name"))
        print("공시:", item.get("report_nm"))
        print("제출자:", filer)
        print("접수일:", item.get("rcept_dt"))
