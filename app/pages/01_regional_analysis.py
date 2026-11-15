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

# 메인 화면과 같은 등급 색상
GRADE_ORDER = ["일반", "관심", "주의", "우선지원"]
GRADE_COLORS = {
    "일반": "#34D399",
    "관심": "#38BDF8",
    "주의": "#FBBF24",
    "우선지원": "#F87171",
}


# 2. 스타일 (메인 화면과 동일한 톤)
CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');

html, body, [class*="css"], .stMarkdown, .stDataFrame {
    font-family: 'Pretendard Variable', Pretendard, -apple-system, sans-serif;
}
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

.hero {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 28px 34px 26px 34px;
    position: relative;
    overflow: hidden;
    margin-bottom: 24px;
}
.hero::before {
    content: "";
    position: absolute;
    left: 0; top: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, #38BDF8 0%, #FBBF24 55%, #F87171 100%);
}
.hero h1 {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0 0 8px 0;
    padding: 0;
}
.hero .desc {
    color: #9AA4B2;
    line-height: 1.7;
    font-size: 0.95rem;
}

.sec-title {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 28px 0 4px 0;
}
.sec-desc {
    color: #9AA4B2;
    font-size: 0.9rem;
    margin-bottom: 16px;
}

.kpi {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 22px;
    height: 100%;
}
.kpi .label { color: #9AA4B2; font-size: 0.85rem; margin-bottom: 8px; }
.kpi .value {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.kpi .unit { font-size: 1rem; font-weight: 600; color: #9AA4B2; margin-left: 4px; }
.kpi.alert { border-color: rgba(248,113,113,0.45); }
.kpi.alert .value { color: #F87171; }

.grade {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--c);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.grade .name { font-weight: 700; color: var(--c); font-size: 0.95rem; }
.grade .share { color: #9AA4B2; font-size: 0.8rem; margin-top: 2px; }
.grade .count { font-size: 1.3rem; font-weight: 800; }
.grade .count span { font-size: 0.85rem; font-weight: 600; color: #9AA4B2; margin-left: 3px; }

.panel-title {
    font-weight: 700;
    font-size: 1rem;
    margin: 18px 0 10px 0;
}

.rank-wrap {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    overflow: hidden;
}
.rank-table { width: 100%; border-collapse: collapse; }
.rank-table th {
    text-align: left;
    color: #9AA4B2;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 9px 12px;
    background: rgba(255,255,255,0.03);
    white-space: nowrap;
}
.rank-table td {
    padding: 9px 12px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.88rem;
    white-space: nowrap;
}
.rank-table .rk { font-weight: 700; color: #9AA4B2; width: 40px; }
.rank-table .num { font-weight: 700; text-align: right; }
.rank-table .chip {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--c);
    background: color-mix(in srgb, var(--c) 16%, transparent);
}

/* 지도 테두리 */
div[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    overflow: hidden;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# 3. 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    gdf = gpd.read_file(GEOJSON_PATH)

    return df, gdf


df, gdf = load_data()


# 4. 페이지 제목
st.markdown(
    """
<div class="hero">
<h1>🗺️ 지역별 기후복지 취약지역 분석</h1>
<div class="desc">전국 229개 시군구의 기후 위험과 복지 취약성을 분석해 지역별 지원 우선순위를 보여줍니다.</div>
</div>
""",
    unsafe_allow_html=True,
)


# 5. 필터
col1, col2 = st.columns(2, gap="medium")

with col1:
    sido_list = ["전체"] + sorted(df["시도"].dropna().unique().tolist())
    selected_sido = st.selectbox("시도 선택", sido_list)

with col2:
    grade_list = ["전체"] + GRADE_ORDER
    selected_grade = st.selectbox("지원 우선순위 등급", grade_list)


# 6. 데이터 필터링
filtered_df = df.copy()
filtered_gdf = gdf.copy()

# 등급 카드는 시도만 반영한 데이터로 계산 (등급 필터와 상관없이 비교 가능)
sido_df = df.copy()

if selected_sido != "전체":
    sido_df = sido_df[sido_df["시도"] == selected_sido]

    filtered_df = filtered_df[filtered_df["시도"] == selected_sido]
    filtered_gdf = filtered_gdf[filtered_gdf["시도"] == selected_sido]

if selected_grade != "전체":
    filtered_df = filtered_df[filtered_df["지원_우선순위_등급"] == selected_grade]
    filtered_gdf = filtered_gdf[filtered_gdf["지원_우선순위_등급"] == selected_grade]


# 7. 지도와 요약
map_title = "전국" if selected_sido == "전체" else selected_sido
st.markdown(
    f'<div class="sec-title">{map_title} 지원 우선순위 지도</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sec-desc">지역에 마우스를 올리면 점수와 등급을 볼 수 있습니다.</div>',
    unsafe_allow_html=True,
)

if filtered_gdf.empty or filtered_df.empty:
    st.warning("선택한 조건에 해당하는 지역이 없습니다.")
    st.stop()

# 요약 카드
priority_n = int((filtered_df["지원_우선순위_등급"] == "우선지원").sum())
avg_score = filtered_df["지원_우선순위_점수"].mean()

k1, k2, k3 = st.columns(3, gap="medium")
k1.markdown(
    f'<div class="kpi"><div class="label">표시 중인 지역</div>'
    f'<div class="value">{len(filtered_df):,}<span class="unit">개</span></div></div>',
    unsafe_allow_html=True,
)
k2.markdown(
    f'<div class="kpi alert"><div class="label">우선지원 지역</div>'
    f'<div class="value">{priority_n:,}<span class="unit">개</span></div></div>',
    unsafe_allow_html=True,
)
k3.markdown(
    f'<div class="kpi"><div class="label">평균 지원 우선순위 점수</div>'
    f'<div class="value">{avg_score:.2f}<span class="unit">점</span></div></div>',
    unsafe_allow_html=True,
)

st.write("")

map_col, side_col = st.columns([2.3, 1], gap="large")

with map_col:
    filtered_gdf = filtered_gdf.copy()
    geojson_data = filtered_gdf.__geo_interface__

    # 배경 지도(다른 나라 포함) 없이 시군구 경계만 그려서 한국만 표시
    fig = px.choropleth(
        filtered_gdf,
        geojson=geojson_data,
        locations=filtered_gdf.index.astype(str),
        featureidkey="id",
        color="지원_우선순위_등급",
        color_discrete_map=GRADE_COLORS,
        category_orders={"지원_우선순위_등급": GRADE_ORDER},
        hover_name="시군구",
        hover_data={
            "시도": True,
            "지원_우선순위_점수": ":.2f",
            "지원_우선순위_등급": True
        },
        projection="mercator"
    )

    # 보이는 지역에 맞춰 자동으로 확대, 나머지 세계 지도는 숨김
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_traces(
        marker_line_width=0.6,
        marker_line_color="#0E1117"
    )

    fig.update_layout(
        height=640,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="#161B26",
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(22,27,38,0.85)",
            font=dict(size=13, color="#E5E9F0"),
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": True},
    )

with side_col:
    st.markdown('<div class="panel-title" style="margin-top:0">등급별 지역 수</div>', unsafe_allow_html=True)

    counts = (
        sido_df["지원_우선순위_등급"]
        .value_counts()
        .reindex(GRADE_ORDER, fill_value=0)
    )
    total = len(sido_df)

    cards = ""
    for grade in reversed(GRADE_ORDER):
        n = int(counts[grade])
        share = n / total * 100 if total else 0
        cards += (
            f'<div class="grade" style="--c:{GRADE_COLORS[grade]}">'
            f'<div><div class="name">{grade}</div>'
            f'<div class="share">{share:.1f}%</div></div>'
            f'<div class="count">{n:,}<span>개</span></div></div>'
        )
    st.markdown(cards, unsafe_allow_html=True)

    st.markdown('<div class="panel-title">점수 상위 5개 지역</div>', unsafe_allow_html=True)

    top5 = (
        filtered_df.sort_values("지원_우선순위_점수", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    rows = ""
    for i, r in top5.iterrows():
        color = GRADE_COLORS.get(r["지원_우선순위_등급"], "#9AA4B2")
        rows += (
            f'<tr style="--c:{color}">'
            f'<td class="rk">{i + 1}위</td>'
            f'<td>{r["시군구"]}</td>'
            f'<td class="num">{r["지원_우선순위_점수"]:.2f}</td>'
            f'<td><span class="chip">{r["지원_우선순위_등급"]}</span></td>'
            f'</tr>'
        )
    st.markdown(
        '<div class="rank-wrap"><table class="rank-table">'
        '<thead><tr><th>순위</th><th>지역</th><th>점수</th><th>등급</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )