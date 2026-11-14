import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.safetydata.go.kr"

apis = {
    "무더위쉼터": {
        "url": f"{BASE_URL}/V2/api/DSSP-IF-10942",
        "key": os.getenv("HEAT_SHELTER_API_KEY")
    },
    "한파쉼터": {
        "url": f"{BASE_URL}/V2/api/DSSP-IF-10804",
        "key": os.getenv("COLD_SHELTER_API_KEY")
    }
}

for name, api in apis.items():
    print(f"\n===== {name} API 테스트 =====")

    if not api["key"]:
        print("인증키를 찾을 수 없습니다.")
        continue

    params = {
        "serviceKey": api["key"],
        "returnType": "json",
        "pageNo": 1,
        "numOfRows": 5
    }

    try:
        response = requests.get(
            api["url"],
            params=params,
            timeout=30
        )

        print("HTTP 상태 코드:", response.status_code)
        response.raise_for_status()

        print("응답 데이터:")
        print(response.text[:3000])

    except requests.RequestException as e:
        print("API 요청 실패:", e)