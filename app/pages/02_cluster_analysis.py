import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "지역별_군집분석.csv"
)

CLUSTER_NAMES = {
    0: "한파 취약형",
    1: "폭염 취약형",
    2: "쉼터 공급 부족형"
}

CLUSTER_COLORS = {
    0: "#38BDF8",
    1: "#F87171",
    2: "#FBBF24"
}

NAME_COLORS = {CLUSTER_NAMES[k]: CLUSTER_COLORS[k] for k in CLUSTER_NAMES}
NAME_ORDER = [CLUSTER_NAMES[k] for k in sorted(CLUSTER_NAMES)]

METRIC_LABELS = {
    "노인_1인가구_비율": "노인 1인 가구 비율",
    "폭염일수": "폭염일수",
    "한파일수": "한파일수",
    "무더위쉼터_비율": "무더위쉼터 비율",
    "한파쉼터_비율": "한파쉼터 비율",
}


# ==========================================
# 2. 스타일 (메인 화면과 동일한 톤)
# ==========================================

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
    margin: 34px 0 4px 0;
}
.sec-desc {
    color: #9AA4B2;
    font-size: 0.9rem;
    margin-bottom: 16px;
}
.panel-title {
    font-weight: 700;
    font-size: 1rem;
    margin: 6px 0 4px 0;
}

/* 군집 카드 */
.cl {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--c);
    border-radius: 14px;
    padding: 18px 22px;
    height: 100%;
}
.cl .name { color: var(--c); font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; }
.cl .value { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; }
.cl .unit { font-size: 1rem; font-weight: 600; color: #9AA4B2; margin-left: 4px; }
.cl .share { color: #9AA4B2; font-size: 0.85rem; margin-top: 6px; }

/* 구성비 막대 */
.stack {
    display: flex;
    height: 34px;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 16px;
}
.stack div {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 700;
    color: #0E1117;
    white-space: nowrap;
}

/* 일반 KPI */
.kpi {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 22px;
}
.kpi .label { color: #9AA4B2; font-size: 0.85rem; margin-bottom: 8px; }
.kpi .value { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; }
.kpi .note { color: #9AA4B2; font-size: 0.82rem; margin-top: 8px; }

/* 평균 특성 표 */
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
    font-size: 0.8rem;
    font-weight: 600;
    padding: 11px 14px;
    background: rgba(255,255,255,0.03);
    white-space: nowrap;
}
.rank-table td {
    padding: 12px 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.92rem;
    white-space: nowrap;
    vertical-align: middle;
}
.rank-table .dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 8px;
    background: var(--c);
}
.rank-table .nm { font-weight: 700; }
.rank-table .score { display: flex; align-items: center; gap: 10px; min-width: 120px; }
.rank-table .track {
    flex: 1;
    height: 6px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
}
.rank-table .fill { height: 100%; border-radius: 999px; background: var(--c); }
.rank-table .num { font-weight: 700; min-width: 42px; text-align: right; }

/* 군집 프로필 카드 */
.profile {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-top: 4px solid var(--c);
    border-radius: 14px;
    padding: 18px 20px 10px 20px;
}
.profile .name { color: var(--c); font-weight: 800; font-size: 1.1rem; }
.profile .cnt { color: #9AA4B2; font-size: 0.85rem; margin: 4px 0 12px 0; }
.profile .row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.9rem;
}
.profile .row span:first-child { color: #9AA4B2; }
.profile .row span:last-child { font-weight: 700; }

.footer {
    text-align: center;
    color: #6B7482;
    font-size: 0.8rem;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.08);
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


st.markdown(
    """
<div class="hero">
<h1>📊 기후복지 취약지역 군집 분석</h1>
<div class="desc">K-Means 알고리즘으로 전국 시군구를 기후재난 취약 특성에 따라 3개 군집으로 나눴습니다. 군집별 인구 특성, 기후 위험, 쉼터 현황을 비교해 보세요.</div>
</div>
""",
    unsafe_allow_html=True,
)

if not DATA_PATH.exists():
    st.error(f"군집 분석 데이터 파일을 찾을 수 없습니다.\n\n{DATA_PATH}")
    st.stop()

load_data.clear()
df = load_data()

df["군집_K3"] = df["군집_K3"].astype(int)
df["군집명"] = df["군집_K3"].map(CLUSTER_NAMES)

total = len(df)

cluster_counts = (
    df["군집_K3"]
    .value_counts()
    .sort_index()
)

cluster_mean = (
    df.groupby("군집_K3")[list(METRIC_LABELS.keys())]
    .mean()
    .reset_index()
)
cluster_mean["군집명"] = cluster_mean["군집_K3"].map(CLUSTER_NAMES)


# ==========================================
# 4. 군집별 지역 분포
# ==========================================

st.markdown('<div class="sec-title">군집별 지역 분포</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sec-desc">분석 대상 {total:,}개 시군구가 어느 군집에 속하는지 보여줍니다.</div>',
    unsafe_allow_html=True,
)

cols = st.columns(3, gap="medium")
for col, cid in zip(cols, sorted(CLUSTER_NAMES)):
    n = int(cluster_counts.get(cid, 0))
    col.markdown(
        f'<div class="cl" style="--c:{CLUSTER_COLORS[cid]}">'
        f'<div class="name">{CLUSTER_NAMES[cid]}</div>'
        f'<div class="value">{n:,}<span class="unit">개 지역</span></div>'
        f'<div class="share">전체의 {n / total * 100:.1f}%</div></div>',
        unsafe_allow_html=True,
    )

segments = ""
for cid in sorted(CLUSTER_NAMES):
    n = int(cluster_counts.get(cid, 0))
    pct = n / total * 100
    label = f"{pct:.0f}%" if pct >= 8 else ""
    segments += f'<div style="width:{pct:.2f}%;background:{CLUSTER_COLORS[cid]}">{label}</div>'

st.markdown(f'<div class="stack">{segments}</div>', unsafe_allow_html=True)


# ==========================================
# 5. 군집별 취약 특성 비교
# ==========================================

st.markdown('<div class="sec-title">군집별 취약 특성 비교</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">군집별 평균값을 항목별로 비교합니다.</div>',
    unsafe_allow_html=True,
)


def make_bar(column, label):
    fig = px.bar(
        cluster_mean,
        x="군집명",
        y=column,
        color="군집명",
        color_discrete_map=NAME_COLORS,
        category_orders={"군집명": NAME_ORDER},
    )

    fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
        textfont=dict(size=14, color="#E5E9F0"),
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="%{x}<br>" + label + ": %{y:.2f}<extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        height=320,
        bargap=0.5,
        showlegend=False,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(size=13)),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showticklabels=False,
            range=[0, max(cluster_mean[column].max(), 1e-9) * 1.25],
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def show_chart(column, label):
    st.markdown(f'<div class="panel-title">군집별 {label}</div>', unsafe_allow_html=True)
    st.plotly_chart(
        make_bar(column, label),
        use_container_width=True,
        config={"displayModeBar": False},
    )


tabs = st.tabs(["인구 취약성", "기후 위험", "쉼터 공급 현황"])

with tabs[0]:
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        show_chart("노인_1인가구_비율", "노인 1인 가구 비율")
    with c2:
        st.write("")
        st.write("")
        overall = df["노인_1인가구_비율"].mean()
        st.markdown(
            f'<div class="kpi"><div class="label">전국 평균 노인 1인 가구 비율</div>'
            f'<div class="value">{overall:.2f}</div>'
            f'<div class="note">전체 {total:,}개 시군구 평균</div></div>',
            unsafe_allow_html=True,
        )

with tabs[1]:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        show_chart("폭염일수", "평균 폭염일수")
    with c2:
        show_chart("한파일수", "평균 한파일수")

with tabs[2]:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        show_chart("무더위쉼터_비율", "무더위쉼터 비율")
    with c2:
        show_chart("한파쉼터_비율", "한파쉼터 비율")


# ==========================================
# 6. 군집별 평균 특성표
# ==========================================

st.markdown('<div class="sec-title">군집별 평균 특성</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">막대는 항목마다 가장 높은 군집을 100%로 둔 상대 비교입니다.</div>',
    unsafe_allow_html=True,
)

col_max = cluster_mean[list(METRIC_LABELS.keys())].max()

head = "<th>군집 유형</th>" + "".join(f"<th>{v}</th>" for v in METRIC_LABELS.values())

body = ""
for _, r in cluster_mean.iterrows():
    cid = int(r["군집_K3"])
    color = CLUSTER_COLORS[cid]
    cells = (
        f'<td class="nm"><span class="dot"></span>{CLUSTER_NAMES[cid]}</td>'
    )
    for key in METRIC_LABELS:
        width = r[key] / col_max[key] * 100 if col_max[key] else 0
        cells += (
            f'<td><div class="score"><div class="track">'
            f'<div class="fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="num">{r[key]:.2f}</div></div></td>'
        )
    body += f'<tr style="--c:{color}">{cells}</tr>'

st.markdown(
    f'<div class="rank-wrap"><table class="rank-table">'
    f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
    unsafe_allow_html=True,
)


# ==========================================
# 7. 군집별 지역 조회
# ==========================================

st.markdown('<div class="sec-title">군집별 지역 조회</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">군집을 고르면 속한 지역과 군집의 평균 특성을 함께 볼 수 있습니다.</div>',
    unsafe_allow_html=True,
)

selected_cluster = st.radio(
    "확인할 군집",
    options=sorted(CLUSTER_NAMES),
    format_func=lambda x: CLUSTER_NAMES[x],
    horizontal=True,
    label_visibility="collapsed",
)

region_df = df[df["군집_K3"] == selected_cluster][
    ["시도", "시군구", "노인_1인가구_비율", "폭염일수", "한파일수"]
].copy()

region_df.columns = ["시도", "시군구", "노인 1인 가구 비율", "폭염일수", "한파일수"]

table_col, profile_col = st.columns([1.8, 1], gap="large")

with table_col:
    st.dataframe(
        region_df.round(2),
        hide_index=True,
        use_container_width=True,
        height=440,
        column_config={
            "시도": st.column_config.TextColumn("시도", width="medium"),
            "시군구": st.column_config.TextColumn("시군구", width="small"),
            "노인 1인 가구 비율": st.column_config.NumberColumn(
                "노인 1인 가구 비율", format="%.2f"
            ),
            "폭염일수": st.column_config.NumberColumn("폭염일수", format="%.1f"),
            "한파일수": st.column_config.NumberColumn("한파일수", format="%.1f"),
        },
    )

with profile_col:
    prof = cluster_mean[cluster_mean["군집_K3"] == selected_cluster].iloc[0]
    rows = "".join(
        f'<div class="row"><span>{label}</span><span>{prof[key]:.2f}</span></div>'
        for key, label in METRIC_LABELS.items()
    )
    st.markdown(
        f'<div class="profile" style="--c:{CLUSTER_COLORS[selected_cluster]}">'
        f'<div class="name">{CLUSTER_NAMES[selected_cluster]}</div>'
        f'<div class="cnt">총 {len(region_df):,}개 지역 · 군집 평균</div>'
        f'{rows}</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer">SafeWeather-AI | K-Means 기반 기후복지 취약지역 군집 분석</div>',
    unsafe_allow_html=True,
)