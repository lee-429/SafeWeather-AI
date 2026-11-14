
import os
import json
import time
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv


# 프로젝트 최상위 경로
ROOT_DIR = Path(__file__).resolve().parents[2]

# 환경변수 불러오기
load_dotenv(ROOT_DIR / ".env")

# 원본 데이터 저장 경로
RAW_DIR = ROOT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.safetydata.go.kr"

# API 설정
API_CONFIG = {
    "heat_shelter": {
        "name": "무더위쉼터",
        "url": f"{BASE_URL}/V2/api/DSSP-IF-10942",
        "key": os.getenv("HEAT_SHELTER_API_KEY"),
        "filename": "heat_shelter.json"
    },
    "cold_shelter": {
        "name": "한파쉼터",
        "url": f"{BASE_URL}/V2/api/DSSP-IF-10804",
        "key": os.getenv("COLD_SHELTER_API_KEY"),
        "filename": "cold_shelter.json"
    }
}


def collect_shelter_data(config, num_of_rows=1000):
    """쉼터 API의 전체 데이터를 페이지 단위로 수집한다."""

    name = config["name"]
    api_key = config["key"]

    if not api_key:
        raise ValueError(f"{name} API 인증키를 찾을 수 없습니다.")

    print(f"\n===== {name} 데이터 수집 시작 =====")

    all_records = []
    page_no = 1
    total_count = None

    with requests.Session() as session:
        while True:
            params = {
                "serviceKey": api_key,
                "returnType": "json",
                "pageNo": page_no,
                "numOfRows": num_of_rows
            }

            response = session.get(
                config["url"],
                params=params,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            header = result.get("header", {})
            result_code = str(header.get("resultCode", ""))

            if result_code != "00":
                raise RuntimeError(
                    f"{name} API 오류: {header}"
                )

            body = result.get("body", [])

            if not isinstance(body, list):
                raise ValueError(f"{name} API의 body 형식이 예상과 다릅니다.")

            if total_count is None:
                total_count = int(result.get("totalCount", 0))
                print(f"전체 데이터: {total_count:,}건")

            if not body:
                print("응답 데이터가 없어 수집을 종료합니다.")
                break

            all_records.extend(body)

            print(
                f"{page_no}페이지 수집 완료 "
                f"({len(all_records):,}/{total_count:,}건)"
            )

            if len(all_records) >= total_count:
                break

            page_no += 1

            # API에 과도한 요청을 보내지 않도록 잠시 대기
            time.sleep(0.2)

    # JSON 원본 저장
    output = {
        "name": name,
        "totalCount": total_count,
        "collectedCount": len(all_records),
        "collectedAt": datetime.now().isoformat(timespec="seconds"),
        "records": all_records
    }

    output_path = RAW_DIR / config["filename"]

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print(f"{name} 수집 완료!")
    print(f"실제 수집 건수: {len(all_records):,}건")
    print(f"저장 위치: {output_path}")

    return all_records


def collect_all_shelters():
    """무더위쉼터와 한파쉼터 데이터를 모두 수집한다."""

    for config in API_CONFIG.values():
        try:
            collect_shelter_data(config)

        except Exception as e:
            print(f"\n{config['name']} 수집 실패: {e}")


if __name__ == "__main__":
    collect_all_shelters()
