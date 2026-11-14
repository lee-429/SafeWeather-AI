"""
SafeWeather AI - 데이터 전처리 모듈

대상 데이터
1. 65세 이상 고령인구
2. 노인 1인가구
3. 일별 최고·최저기온
4. 폭염일수
5. 한파일수

사용 방법
--------
import pandas as pd
from preprocessing import (
    preprocess_elderly_population,
    preprocess_elderly_single_household,
    preprocess_daily_temperature,
    preprocess_heatwave_days,
    preprocess_coldwave_days,
)

각 함수는 원본 데이터프레임을 입력받아 전처리된 데이터프레임을 반환한다.
파일 읽기/저장은 호출하는 쪽에서 수행한다.

주의
----
- 이 모듈은 기존 Notebook에서 확인한 처리 기준을 함수로 옮긴 초안이다.
- 고령인구/노인 1인가구 원본의 세부 컬럼 구조 및 예외 행은 실제 CSV와 대조해야 한다.
- 폭염/한파일수 최종값은 기존 Notebook과 동일하게 기상 데이터에서 기준 온도로 계산한다.
"""

from __future__ import annotations

import calendar
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------
# 공통 상수
# ---------------------------------------------------------------------

SIDO_LIST = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시",
    "광주광역시", "대전광역시", "울산광역시", "세종특별자치시",
    "경기도", "강원특별자치도", "충청북도", "충청남도",
    "전북특별자치도", "전라남도", "경상북도", "경상남도",
    "제주특별자치도",
]

GENERAL_GU = [
    "장안구", "권선구", "팔달구", "영통구",
    "수정구", "중원구", "분당구",
    "만안구", "동안구",
    "원미구", "소사구", "오정구",
    "상록구", "단원구",
    "덕양구", "일산동구", "일산서구",
    "처인구", "기흥구", "수지구",
    "상당구", "서원구", "흥덕구", "청원구",
    "동남구", "서북구",
    "완산구", "덕진구",
    "의창구", "성산구", "마산합포구", "마산회원구", "진해구",
]

EXCLUDE_BRANCH = [
    "중구영종출장소", "중구용유출장소", "서구검단출장소",
    "북부출장소", "송탄출장소", "안중출장소", "풍양출장소",
    "화성시동부출장소", "화성시동탄출장소", "동해출장소",
    "전주시효자출장소", "익산시함열출장소", "사천남양출장소",
    "장유출장소", "양산시웅상출장소",
]

YEAR_COLUMNS = ["2021", "2022", "2023", "2024", "2025"]

ELDERLY_AGE_GROUPS = [
    "65~69세", "70~74세", "75~79세", "80~84세", "85세이상",
]


def _require_columns(df: pd.DataFrame, columns: Iterable[str], dataset_name: str) -> None:
    """필수 컬럼 존재 여부를 확인한다."""
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(
            f"{dataset_name} 데이터에 필요한 컬럼이 없습니다: {missing}\n"
            f"현재 컬럼: {df.columns.tolist()}"
        )


def _add_sido_from_region(
    df: pd.DataFrame,
    region_col: str = "행정구역(시군구)별",
) -> pd.DataFrame:
    """
    원본 지역 행을 위에서부터 읽어 시도명을 부여한다.
    SIDO_LIST에 해당하는 행을 만나면 현재 시도를 갱신한다.
    """
    _require_columns(df, [region_col], "지역 데이터")

    result = df.copy()
    current_sido = None
    sido_values = []

    for value in result[region_col].astype(str):
        region = value.strip()
        if region in SIDO_LIST:
            current_sido = region
        sido_values.append(current_sido)

    result["시도"] = sido_values
    return result


def _clean_region_rows(
    df: pd.DataFrame,
    region_col: str = "행정구역(시군구)별",
) -> pd.DataFrame:
    """전국/시도 합계, 일반구, 출장소 및 시도 매핑 실패 행을 제외한다."""
    result = df.copy()
    region = result[region_col].astype(str).str.strip()

    result = result[
        result["시도"].notna()
        & (region != "전국")
        & ~region.isin(SIDO_LIST)
        & ~region.isin(GENERAL_GU)
        & ~region.isin(EXCLUDE_BRANCH)
    ].copy()

    result["행정구역명"] = result[region_col].astype(str).str.strip()
    return result


# ---------------------------------------------------------------------
# 1. 65세 이상 고령인구
# ---------------------------------------------------------------------

def preprocess_elderly_population(
    df: pd.DataFrame,
    region_col: str = "행정구역(시군구)별",
    year_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    65세 이상 고령인구 원본을 지역별·연도별 합계로 정리한다.

    참고:
    기존 Notebook에서 처리한 군위군의 대구 통합, 포항 남구/북구 제외,
    세종특별자치시 별도 처리 기준을 반영한다.
    """
    years = year_columns or YEAR_COLUMNS
    _require_columns(df, [region_col, *years], "고령인구")

    result = df.copy()
    result = _add_sido_from_region(result, region_col)
    result = _clean_region_rows(result, region_col)

    for year in years:
        result[year] = pd.to_numeric(result[year], errors="coerce")

    # 지역별 연도 합계
    result = (
        result.groupby(["시도", "행정구역명"], as_index=False)[years]
        .sum(min_count=1)
    )

    # 군위군은 대구광역시로 통합
    gunwi = result["행정구역명"].eq("군위군")
    if gunwi.any():
        result.loc[gunwi, "시도"] = "대구광역시"

    # 포항시 일반구(남구/북구)는 제외
    result = result[
        ~result["행정구역명"].isin(["남구", "북구"])
    ].copy()

    # 군위군이 이미 대구에 포함된 형태로 중복될 가능성에 대비해 재집계
    result = (
        result.groupby(["시도", "행정구역명"], as_index=False)[years]
        .sum(min_count=1)
    )

    # 세종은 원본에서 시도 행을 제외했더라도 별도 지역으로 유지
    # 원본에 세종특별자치시 행이 있다면 위 필터에서 제외될 수 있으므로,
    # 원본의 세종 행을 직접 추출해 별도 행으로 추가한다.
    raw_region = df[region_col].astype(str).str.strip()
    sejong_rows = df.loc[raw_region.eq("세종특별자치시"), years].copy()
    if not sejong_rows.empty:
        for year in years:
            sejong_rows[year] = pd.to_numeric(sejong_rows[year], errors="coerce")
        sejong_values = sejong_rows[years].sum(min_count=1)
        sejong_record = {"시도": "세종특별자치시", "행정구역명": "세종특별자치시"}
        sejong_record.update(sejong_values.to_dict())

        result = result[
            ~(
                result["시도"].eq("세종특별자치시")
                | result["행정구역명"].eq("세종특별자치시")
            )
        ]
        result = pd.concat(
            [result, pd.DataFrame([sejong_record])],
            ignore_index=True,
        )

    result = result.sort_values(["시도", "행정구역명"]).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------
# 2. 노인 1인가구
# ---------------------------------------------------------------------

def preprocess_elderly_single_household(
    df: pd.DataFrame,
    region_col: str = "행정구역(시군구)별",
    age_col: str = "연령별",
    year_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    노인 1인가구 원본을 지역별·연도별 65세 이상 합계로 정리한다.

    기존 Notebook의 첫 행 중복 헤더 제거, 연령대 필터, 지역 합산,
    군위군/포항 남구·북구 처리 기준을 반영한다.
    """
    years = year_columns or YEAR_COLUMNS

    # 기존 파일은 첫 행이 중복 헤더이므로 제거
    result = df.iloc[1:].copy().reset_index(drop=True)
    _require_columns(result, [region_col, age_col, *years], "노인 1인가구")

    result = _add_sido_from_region(result, region_col)
    result = _clean_region_rows(result, region_col)

    result[age_col] = result[age_col].astype(str).str.strip()
    result = result[result[age_col].isin(ELDERLY_AGE_GROUPS)].copy()

    for year in years:
        result[year] = pd.to_numeric(result[year], errors="coerce")

    result = (
        result.groupby(["시도", "행정구역명"], as_index=False)[years]
        .sum(min_count=1)
    )

    # 군위군을 대구광역시 소속으로 정리
    result.loc[result["행정구역명"].eq("군위군"), "시도"] = "대구광역시"

    # 포항시 일반구 제외
    result = result[
        ~result["행정구역명"].isin(["남구", "북구"])
    ].copy()

    result = (
        result.groupby(["시도", "행정구역명"], as_index=False)[years]
        .sum(min_count=1)
    )

    # 기존 Notebook에서 창원시(통합) 표기를 창원시로 변경
    result["행정구역명"] = result["행정구역명"].replace(
        {"창원시(통합)": "창원시"}
    )

    result = result.sort_values(["시도", "행정구역명"]).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------
# 3. 일별 최고·최저기온
# ---------------------------------------------------------------------

STATION_SIDO = {
    "서울": "서울특별시",
    "부산": "부산광역시", "북부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시", "강화": "인천광역시", "백령도": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "동두천": "경기도", "파주": "경기도", "수원": "경기도",
    "양평": "경기도", "이천": "경기도",
    "속초": "강원특별자치도", "북춘천": "강원특별자치도",
    "철원": "강원특별자치도", "대관령": "강원특별자치도",
    "춘천": "강원특별자치도", "북강릉": "강원특별자치도",
    "강릉": "강원특별자치도", "동해": "강원특별자치도",
    "원주": "강원특별자치도", "영월": "강원특별자치도",
    "인제": "강원특별자치도", "홍천": "강원특별자치도",
    "태백": "강원특별자치도", "정선군": "강원특별자치도",
    "충주": "충청북도", "청주": "충청북도", "추풍령": "충청북도",
    "서청주": "충청북도", "제천": "충청북도", "보은": "충청북도",
    "서산": "충청남도", "홍성": "충청남도", "천안": "충청남도",
    "보령": "충청남도", "부여": "충청남도", "금산": "충청남도",
    "군산": "전북특별자치도", "전주": "전북특별자치도",
    "고창": "전북특별자치도", "부안": "전북특별자치도",
    "임실": "전북특별자치도", "정읍": "전북특별자치도",
    "남원": "전북특별자치도", "장수": "전북특별자치도",
    "고창군": "전북특별자치도", "순창군": "전북특별자치도",
    "목포": "전라남도", "여수": "전라남도", "흑산도": "전라남도",
    "완도": "전라남도", "순천": "전라남도", "영광군": "전라남도",
    "보성군": "전라남도", "강진군": "전라남도", "장흥": "전라남도",
    "해남": "전라남도", "고흥": "전라남도", "광양시": "전라남도",
    "진도군": "전라남도",
    "울릉도": "경상북도", "울진": "경상북도", "안동": "경상북도",
    "상주": "경상북도", "포항": "경상북도", "봉화": "경상북도",
    "영주": "경상북도", "문경": "경상북도", "청송군": "경상북도",
    "영덕": "경상북도", "의성": "경상북도", "구미": "경상북도",
    "영천": "경상북도", "경주시": "경상북도",
    "창원": "경상남도", "통영": "경상남도", "진주": "경상남도",
    "북창원": "경상남도", "김해시": "경상남도", "양산시": "경상남도",
    "의령군": "경상남도", "함양군": "경상남도", "거창": "경상남도",
    "합천": "경상남도", "밀양": "경상남도", "산청": "경상남도",
    "거제": "경상남도", "남해": "경상남도",
    "제주": "제주특별자치도", "고산": "제주특별자치도",
    "성산": "제주특별자치도", "서귀포": "제주특별자치도",
}


def preprocess_daily_temperature(
    df: pd.DataFrame,
    station_sido: dict[str, str] | None = None,
) -> pd.DataFrame:
    """일별 최고·최저기온 데이터에 시도 정보를 부여하고 정렬한다."""
    required = ["지점", "지점명", "일시", "최저기온(°C)", "최고기온(°C)"]
    _require_columns(df, required, "일별 기온")

    result = df.copy()
    result["일시"] = pd.to_datetime(result["일시"], errors="coerce")
    result["시도"] = result["지점명"].map(station_sido or STATION_SIDO)

    unmapped = result.loc[result["시도"].isna(), "지점명"].dropna().unique()
    if len(unmapped):
        raise ValueError(f"시도 매핑이 되지 않은 관측소가 있습니다: {unmapped.tolist()}")

    result = result[
        ["지점", "지점명", "시도", "일시", "최저기온(°C)", "최고기온(°C)"]
    ].copy()

    result = result.sort_values(["지점", "일시"]).reset_index(drop=True)
    return result


# ---------------------------------------------------------------------
# 4. 폭염일수
# ---------------------------------------------------------------------

def preprocess_heatwave_days(
    heat_df: pd.DataFrame,
    temperature_df: pd.DataFrame,
    threshold: float = 33,
) -> pd.DataFrame:
    """
    기상 데이터의 최고기온 기준으로 관측소별·연도별 폭염일수를 계산한다.

    heat_df는 원본 폭염일수 목록 비교용이다.
    최종 폭염일수는 기존 Notebook과 동일하게 temperature_df에서 계산한다.
    """
    _require_columns(
        temperature_df,
        ["지점", "지점명", "시도", "일시", "최고기온(°C)"],
        "기온 데이터",
    )

    # 원본 폭염 목록 구조 확인 및 비교용 집계
    heat = heat_df.iloc[34:, :3].copy()
    heat.columns = ["연도", "날짜", "지점명"]
    heat["연도"] = heat["연도"].astype(str).str.strip()
    heat["날짜"] = heat["날짜"].astype(str).str.zfill(4)
    heat["일시"] = pd.to_datetime(
        heat["연도"] + heat["날짜"],
        format="%Y%m%d",
        errors="coerce",
    )
    heat = heat.drop_duplicates()
    source_count = (
        heat.groupby(["지점명", "연도"])
        .size()
        .reset_index(name="목록_폭염일수")
    )

    temp = temperature_df.copy()
    temp["일시"] = pd.to_datetime(temp["일시"], errors="coerce")
    temp["연도"] = temp["일시"].dt.year.astype("Int64").astype(str)

    hot = temp[temp["최고기온(°C)"] >= threshold]
    hot_count = (
        hot.groupby(["지점명", "연도"])
        .size()
        .reset_index(name="폭염일수")
    )

    # 전체 관측일수: 기존 Notebook과 동일하게 전체 행 수 사용
    obs = (
        temp.groupby(["지점", "지점명", "시도", "연도"])
        .size()
        .reset_index(name="관측일수")
    )

    result = obs.merge(hot_count, on=["지점명", "연도"], how="left")
    result["폭염일수"] = result["폭염일수"].fillna(0).astype(int)

    # 6~9월 최고기온이 관측된 날짜 수
    summer = temp[temp["일시"].dt.month.between(6, 9)]
    summer_obs = (
        summer.dropna(subset=["최고기온(°C)"])
        .groupby(["지점명", "연도"])
        .size()
        .reset_index(name="여름관측일수")
    )

    result = result.merge(summer_obs, on=["지점명", "연도"], how="left")
    result["여름관측일수"] = result["여름관측일수"].fillna(0).astype(int)
    result["여름부족일수"] = 122 - result["여름관측일수"]
    result["여름관측_주의"] = result["여름부족일수"] >= 5

    result = result[
        [
            "지점", "지점명", "시도", "연도", "폭염일수",
            "관측일수", "여름관측일수", "여름부족일수", "여름관측_주의",
        ]
    ]
    result = result.sort_values(["지점", "연도"]).reset_index(drop=True)

    # 비교 결과는 함수 반환값에 섞지 않고 필요 시 별도 확인할 수 있도록 속성으로 보관
    result.attrs["source_list_comparison"] = source_count.merge(
        hot_count, on=["지점명", "연도"], how="outer"
    )
    return result


# ---------------------------------------------------------------------
# 5. 한파일수
# ---------------------------------------------------------------------

def preprocess_coldwave_days(
    cold_df: pd.DataFrame,
    temperature_df: pd.DataFrame,
    threshold: float = -12,
) -> pd.DataFrame:
    """
    기상 데이터의 최저기온 기준으로 관측소별·연도별 한파일수를 계산한다.

    cold_df는 원본 한파일수 목록 비교용이다.
    최종 한파일수는 기존 Notebook과 동일하게 temperature_df에서 계산한다.
    """
    _require_columns(
        temperature_df,
        ["지점", "지점명", "시도", "일시", "최저기온(°C)"],
        "기온 데이터",
    )

    # 원본 한파일수 목록 비교용 집계
    cold = cold_df.copy()
    if cold.shape[1] < 3:
        raise ValueError("한파일수 원본은 최소 3개 컬럼이 필요합니다.")

    cold = cold.iloc[16:, :3].copy()
    cold.columns = ["연도", "날짜", "지점명"]
    cold["연도"] = cold["연도"].astype(str).str.strip()
    cold["날짜"] = cold["날짜"].astype(str).str.zfill(4)
    cold["일시"] = pd.to_datetime(
        cold["연도"] + cold["날짜"],
        format="%Y%m%d",
        errors="coerce",
    )
    source_count = (
        cold.groupby(["지점명", "연도"])
        .size()
        .reset_index(name="목록_한파일수")
    )

    temp = temperature_df.copy()
    temp["일시"] = pd.to_datetime(temp["일시"], errors="coerce")
    temp["연도"] = temp["일시"].dt.year.astype("Int64").astype(str)

    cold_days = temp[temp["최저기온(°C)"] <= threshold]
    cold_count = (
        cold_days.groupby(["지점명", "연도"])
        .size()
        .reset_index(name="한파일수")
    )

    obs = (
        temp.groupby(["지점", "지점명", "시도", "연도"])
        .size()
        .reset_index(name="관측일수")
    )

    result = obs.merge(cold_count, on=["지점명", "연도"], how="left")
    result["한파일수"] = result["한파일수"].fillna(0).astype(int)

    # 기존 Notebook과 동일하게 11~3월을 각 달력 연도 그룹으로 집계
    winter = temp[temp["일시"].dt.month.isin([11, 12, 1, 2, 3])]
    winter_obs = (
        winter.dropna(subset=["최저기온(°C)"])
        .groupby(["지점명", "연도"])
        .size()
        .reset_index(name="겨울관측일수")
    )

    result = result.merge(winter_obs, on=["지점명", "연도"], how="left")
    result["겨울관측일수"] = result["겨울관측일수"].fillna(0).astype(int)

    def expected_winter_days(year: str) -> int:
        return 152 if calendar.isleap(int(year)) else 151

    result["겨울일수"] = result["연도"].apply(expected_winter_days)
    result["겨울부족일수"] = result["겨울일수"] - result["겨울관측일수"]
    result["겨울관측_주의"] = result["겨울부족일수"] >= 5

    result = result[
        [
            "지점", "지점명", "시도", "연도", "한파일수",
            "관측일수", "겨울관측일수", "겨울부족일수", "겨울관측_주의",
        ]
    ]
    result = result.sort_values(["지점", "연도"]).reset_index(drop=True)

    result.attrs["source_list_comparison"] = source_count.merge(
        cold_count, on=["지점명", "연도"], how="outer"
    )
    return result


# ---------------------------------------------------------------------
# 파일 실행 예시
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("SafeWeather AI preprocessing 모듈입니다.")
    print("각 전처리 함수에 pandas DataFrame을 전달해 사용하세요.")
