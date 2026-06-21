from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")

end_date = datetime.today()
start_date = end_date - timedelta(days=7)

url = "https://opendart.fss.or.kr/api/list.json"

all_reports = []
page_no = 1

while True:

    params = {
        "crtfc_key": DART_API_KEY,
        "bgn_de": start_date.strftime("%Y%m%d"),
        "end_de": end_date.strftime("%Y%m%d"),
        "page_no": page_no,
        "page_count": 100,
        "last_reprt_at": "Y"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if page_no == 1:
        print("상태코드:", data.get("status"))
        print("메시지:", data.get("message"))
        print("전체 페이지:", data.get("total_page"))
        print("전체 건수:", data.get("total_count"))

    reports = data.get("list", [])

    if not reports:
        break

    all_reports.extend(reports)

    total_page = int(data.get("total_page", 1))

    if page_no >= total_page:
        break

    page_no += 1

print()
print("수집된 공시 수:", len(all_reports))
print()

for item in all_reports:

    filer = item.get("flr_nm", "")

    if filer == "국민연금공단":

        print("-----")
        print("회사:", item.get("corp_name"))
        print("공시:", item.get("report_nm"))
        print("제출자:", filer)
        print("접수일:", item.get("rcept_dt"))