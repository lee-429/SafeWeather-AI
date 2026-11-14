
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
from pathlib import Path

# 1. 기본 설정
st.set_page_config(
    page_title="지역별 지원 우선순위 분석",
    page_icon="🗺️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

CSV_PATH = BASE_DIR / "data" / "processed" / "지역별_지원우선순위.csv"

GEOJSON_PATH = (
    BASE_DIR / "data" / "processed"
    / "지역별_지원우선순위_지도_간소화.geojson"
)


# 2. 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    gdf = gpd.read_file(GEOJSON_PATH)

    return df, gdf


df, gdf = load_data()


# 3. 페이지 제목
st.title("🗺️ 지역별 기후복지 취약지역 분석")

st.markdown(
    "전국 229개 시군구의 기후 위험과 복지 취약성을 분석하여 "
    "지역별 지원 우선순위를 확인합니다."
)

st.divider()


# 4. 필터
col1, col2 = st.columns(2)

with col1:
    sido_list = ["전체"] + sorted(df["시도"].dropna().unique().tolist())
    selected_sido = st.selectbox("시도 선택", sido_list)

with col2:
    grade_list = ["전체", "일반", "관심", "주의", "우선지원"]
    selected_grade = st.selectbox("지원 우선순위 등급", grade_list)


# 5. 데이터 필터링
filtered_df = df.copy()
filtered_gdf = gdf.copy()

if selected_sido != "전체":
    filtered_df = filtered_df[
        filtered_df["시도"] == selected_sido
    ]

    filtered_gdf = filtered_gdf[
        filtered_gdf["시도"] == selected_sido
    ]

if selected_grade != "전체":
    filtered_df = filtered_df[
        filtered_df["지원_우선순위_등급"] == selected_grade
    ]

    filtered_gdf = filtered_gdf[
        filtered_gdf["지원_우선순위_등급"] == selected_grade
    ]



# 6. 지도
st.subheader("전국 지원 우선순위 지도")

if filtered_gdf.empty:
    st.warning("선택한 조건에 해당하는 지역이 없습니다.")

else:
    # 등급별 고정 색상
    color_map = {
        "일반": "#4CAF50",
        "관심": "#93C5FD",
        "주의": "#FBBF24",
        "우선지원": "#EF4444"
    }

    filtered_gdf = filtered_gdf.copy()

    filtered_gdf["지도색상"] = filtered_gdf[
        "지원_우선순위_등급"
    ].map(color_map)

    geojson_data = filtered_gdf.__geo_interface__

    fig = px.choropleth_map(
        filtered_gdf,
        geojson=geojson_data,
        locations=filtered_gdf.index.astype(str),
        featureidkey="id",
        color="지원_우선순위_등급",
        color_discrete_map=color_map,
        category_orders={
            "지원_우선순위_등급": [
                "일반", "관심", "주의", "우선지원"
            ]
        },
        hover_name="시군구",
        hover_data={
            "시도": True,
            "지원_우선순위_점수": ":.2f",
            "지원_우선순위_등급": True
        },
        map_style="carto-positron",
        center={"lat": 36.5, "lon": 127.8},
        zoom=5,
        opacity=0.75
    )

    fig.update_layout(
        height=700,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend_title_text="지원 우선순위 등급"
    )

    st.plotly_chart(fig, use_container_width=True)

