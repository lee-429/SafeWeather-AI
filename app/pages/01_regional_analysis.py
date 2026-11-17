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

:root {
    --bg: #0A0E16;
    --glass: rgba(255,255,255,0.045);
    --glass-strong: rgba(255,255,255,0.07);
    --line: rgba(255,255,255,0.09);
    --text: #F1F4F9;
    --muted: #8F9AAB;
    --ease: cubic-bezier(.22,.61,.36,1);
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

.stApp {
    background:
        radial-gradient(900px 480px at 8% -8%, rgba(56,189,248,0.13), transparent 60%),
        radial-gradient(900px 480px at 96% -4%, rgba(248,113,113,0.13), transparent 60%),
        var(--bg);
    color: var(--text);
}
html, body, [class*="css"], .stMarkdown, .stApp {
    font-family: 'Pretendard Variable', Pretendard, -apple-system, sans-serif;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1120px;
}

/* ---------- 히어로 ---------- */
.hero { padding: 36px 0 26px 0; animation: rise .7s var(--ease) both; }
.hero .pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 999px;
    background: var(--glass); border: 1px solid var(--line);
    color: var(--muted); font-size: 0.82rem; font-weight: 500;
    margin-bottom: 18px;
}
.hero .pill i {
    width: 8px; height: 8px; border-radius: 50%;
    background: linear-gradient(90deg, #38BDF8, #F87171);
}
.hero h1 {
    font-size: 2.5rem; font-weight: 800; letter-spacing: -0.035em;
    line-height: 1.15; margin: 0 0 12px 0; padding: 0;
    background: linear-gradient(90deg, #7DD3FC 0%, #FDE68A 50%, #FCA5A5 100%);
    -webkit-background-clip: text; background-clip: text;
    color: transparent; width: fit-content;
}
.hero .desc { color: var(--muted); line-height: 1.75; font-size: 0.98rem; max-width: 640px; }
@keyframes rise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- 섹션 제목 ---------- */
.sec-title { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; margin: 36px 0 4px 0; }
.sec-desc { color: var(--muted); font-size: 0.92rem; margin-bottom: 18px; }
.panel-title { font-weight: 700; font-size: 1rem; margin: 24px 0 12px 0; letter-spacing: -0.01em; }

/* ---------- 필터 (selectbox) ---------- */
div[data-testid="stSelectbox"] label p { color: var(--muted); font-size: 0.85rem; font-weight: 500; }
div[data-baseweb="select"] > div {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 14px;
    min-height: 48px;
    transition: background .2s var(--ease), border-color .2s var(--ease);
}
div[data-baseweb="select"] > div:hover { background: var(--glass-strong); }

/* ---------- KPI ---------- */
.kpi {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 22px 26px; height: 100%;
    transition: background .25s var(--ease);
}
.kpi:hover { background: var(--glass-strong); }
.kpi .label { color: var(--muted); font-size: 0.88rem; margin-bottom: 12px; }
.kpi .value { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
.kpi .unit { font-size: 1rem; font-weight: 600; color: var(--muted); margin-left: 5px; }
.kpi.alert {
    background: linear-gradient(160deg, rgba(248,113,113,0.20), rgba(248,113,113,0.05));
    border-color: rgba(248,113,113,0.35);
}
.kpi.alert .value { color: #FCA5A5; }

/* ---------- 등급별 지역 수 ---------- */
.dist {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 20px;
}
.dist .bar { display: flex; gap: 3px; height: 14px; margin-bottom: 18px; }
.dist .seg { background: var(--c); min-width: 4px; border-radius: 4px; }
.dist .seg:first-child { border-radius: 8px 4px 4px 8px; }
.dist .seg:last-child  { border-radius: 4px 8px 8px 4px; }
.dist .seg:only-child  { border-radius: 8px; }
.dist .item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0 8px 12px; border-left: 3px solid var(--c); margin-bottom: 6px;
}
.dist .item:last-child { margin-bottom: 0; }
.dist .name { font-weight: 600; font-size: 0.92rem; }
.dist .share { color: var(--muted); font-size: 0.78rem; margin-top: 1px; }
.dist .count { font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; }
.dist .count span { font-size: 0.8rem; font-weight: 600; color: var(--muted); margin-left: 3px; }

/* ---------- 상위 5개 ---------- */
.rank { background: var(--glass); border: 1px solid var(--line); border-radius: 22px; padding: 8px; }
.rank-row {
    display: grid;
    grid-template-columns: 32px 1fr auto auto;
    align-items: center; gap: 12px;
    padding: 11px 12px; border-radius: 14px;
    transition: background .2s var(--ease);
}
.rank-row:hover { background: var(--glass-strong); }
.rank-row .no {
    width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
    border-radius: 9px; background: rgba(255,255,255,0.06);
    color: var(--muted); font-weight: 700; font-size: 0.8rem;
}
.rank-row.top .no { background: var(--c); color: #0A0E16; }
.rank-row .area { font-weight: 600; font-size: 0.92rem; white-space: nowrap; }
.rank-row .num { font-weight: 700; font-size: 0.9rem; font-variant-numeric: tabular-nums; }
.rank-row .chip {
    padding: 3px 10px; border-radius: 999px; font-size: 0.74rem; font-weight: 600;
    color: var(--c); background: color-mix(in srgb, var(--c) 15%, transparent);
}

/* ---------- 지도 ---------- */
div[data-testid="stPlotlyChart"] {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 22px;
    overflow: hidden;
}

@media (max-width: 720px) {
    .hero h1 { font-size: 1.9rem; }
}
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
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
<div class="pill"><i></i>전국 229개 시군구</div>
<h1>지역별 기후복지 취약지역 분석</h1>
<div class="desc">기후 위험과 복지 취약성을 분석해 지역별 지원 우선순위를 지도에서 확인할 수 있습니다.</div>
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
        marker_line_width=0.5,
        marker_line_color="#0A0E16"
    )

    fig.update_layout(
        height=640,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="#161B26",
            bordercolor="rgba(255,255,255,0.15)",
            font=dict(color="#F1F4F9", size=13),
        ),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=0.97,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=13, color="#F1F4F9"),
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

    segs = ""
    items = ""
    for grade in reversed(GRADE_ORDER):
        n = int(counts[grade])
        share = n / total * 100 if total else 0
        color = GRADE_COLORS[grade]
        if n > 0:
            segs += f'<div class="seg" style="--c:{color}; flex:{n}"></div>'
        items += (
            f'<div class="item" style="--c:{color}">'
            f'<div><div class="name">{grade}</div>'
            f'<div class="share">{share:.1f}%</div></div>'
            f'<div class="count">{n:,}<span>개</span></div></div>'
        )
    st.markdown(
        f'<div class="dist"><div class="bar">{segs}</div>{items}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-title">점수 상위 5개 지역</div>', unsafe_allow_html=True)

    top5 = (
        filtered_df.sort_values("지원_우선순위_점수", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    rows = ""
    for i, r in top5.iterrows():
        color = GRADE_COLORS.get(r["지원_우선순위_등급"], "#8F9AAB")
        top_cls = " top" if i < 3 else ""
        rows += (
            f'<div class="rank-row{top_cls}" style="--c:{color}">'
            f'<div class="no">{i + 1}</div>'
            f'<div class="area">{r["시군구"]}</div>'
            f'<div class="num">{r["지원_우선순위_점수"]:.2f}</div>'
            f'<div class="chip">{r["지원_우선순위_등급"]}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="rank">{rows}</div>', unsafe_allow_html=True)