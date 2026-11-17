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
.hero .desc { color: var(--muted); line-height: 1.75; font-size: 0.98rem; max-width: 680px; }
@keyframes rise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- 섹션 제목 ---------- */
.sec-title { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; margin: 44px 0 4px 0; }
.sec-desc { color: var(--muted); font-size: 0.92rem; margin-bottom: 18px; }
.panel-title { font-weight: 700; font-size: 1rem; margin: 10px 0 4px 0; letter-spacing: -0.01em; }

/* ---------- 군집 카드 ---------- */
.cl {
    position: relative; overflow: hidden;
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 24px 26px; height: 100%;
    transition: background .25s var(--ease);
}
.cl:hover { background: var(--glass-strong); }
.cl::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: var(--c);
}
.cl .name { color: var(--c); font-weight: 700; font-size: 0.95rem; margin-bottom: 14px; }
.cl .value { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
.cl .unit { font-size: 0.95rem; font-weight: 600; color: var(--muted); margin-left: 5px; }
.cl .share { color: var(--muted); font-size: 0.85rem; margin-top: 10px; }

/* 구성비 막대 */
.stack { display: flex; gap: 4px; height: 44px; margin-top: 18px; }
.stack div {
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; color: #0A0E16;
    white-space: nowrap; min-width: 6px;
    transition: filter .2s var(--ease), transform .2s var(--ease);
}
.stack div:first-child { border-radius: 14px 5px 5px 14px; }
.stack div:last-child  { border-radius: 5px 14px 14px 5px; }
.stack div:hover { filter: brightness(1.12); transform: translateY(-2px); }

/* ---------- 일반 KPI ---------- */
.kpi {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 22px 26px;
}
.kpi .label { color: var(--muted); font-size: 0.88rem; margin-bottom: 12px; }
.kpi .value { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
.kpi .note { color: var(--muted); font-size: 0.82rem; margin-top: 12px; }

/* ---------- 탭 ---------- */
div[data-baseweb="tab-list"] {
    gap: 6px; background: var(--glass); border: 1px solid var(--line);
    border-radius: 14px; padding: 5px; width: fit-content;
}
button[data-baseweb="tab"] {
    height: 38px; padding: 0 18px; border-radius: 10px;
    background: transparent; color: var(--muted); font-weight: 600;
    transition: background .2s var(--ease), color .2s var(--ease);
}
button[data-baseweb="tab"][aria-selected="true"] { background: var(--glass-strong); color: var(--text); }
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none; }

/* ---------- 라디오 (군집 선택) ---------- */
div[role="radiogroup"] { gap: 8px; }
div[role="radiogroup"] > label {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 999px; padding: 8px 18px;
    transition: background .2s var(--ease);
}
div[role="radiogroup"] > label:hover { background: var(--glass-strong); }
div[role="radiogroup"] > label:has(input:checked) {
    background: var(--glass-strong); border-color: rgba(255,255,255,0.28);
}

/* ---------- 평균 특성 표 ---------- */
.rank-wrap {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 8px; overflow-x: auto;
}
.rank-table { width: 100%; border-collapse: collapse; }
.rank-table th {
    text-align: left; color: var(--muted); font-size: 0.8rem; font-weight: 600;
    padding: 12px 14px; white-space: nowrap;
}
.rank-table td {
    padding: 14px; border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.92rem; white-space: nowrap; vertical-align: middle;
}
.rank-table tbody tr { transition: background .2s var(--ease); }
.rank-table tbody tr:hover { background: var(--glass-strong); }
.rank-table .dot {
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 10px; background: var(--c);
}
.rank-table .nm { font-weight: 700; }
.rank-table .score { display: flex; align-items: center; gap: 10px; min-width: 120px; }
.rank-table .track { flex: 1; height: 8px; border-radius: 999px; background: rgba(255,255,255,0.07); }
.rank-table .fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, color-mix(in srgb, var(--c) 55%, transparent), var(--c));
}
.rank-table .num { font-weight: 700; min-width: 42px; text-align: right; font-variant-numeric: tabular-nums; }

/* ---------- 군집 프로필 ---------- */
.profile {
    position: relative; overflow: hidden;
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; padding: 24px 24px 12px 24px;
}
.profile::before {
    content: ""; position: absolute; left: 0; top: 0; right: 0; height: 4px; background: var(--c);
}
.profile .name { color: var(--c); font-weight: 800; font-size: 1.15rem; letter-spacing: -0.01em; }
.profile .cnt { color: var(--muted); font-size: 0.85rem; margin: 6px 0 14px 0; }
.profile .row {
    display: flex; justify-content: space-between;
    padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.9rem;
}
.profile .row span:first-child { color: var(--muted); }
.profile .row span:last-child { font-weight: 700; font-variant-numeric: tabular-nums; }

/* ---------- 차트·표 테두리 ---------- */
div[data-testid="stPlotlyChart"] {
    background: var(--glass); border: 1px solid var(--line);
    border-radius: 22px; overflow: hidden; padding: 6px 6px 0 6px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid var(--line); border-radius: 22px; overflow: hidden;
}

.footer {
    text-align: center; color: #657084; font-size: 0.8rem;
    margin-top: 56px; padding-top: 22px; border-top: 1px solid var(--line);
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


# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


st.markdown(
    """
<div class="hero">
<div class="pill"><i></i>K-Means 군집 분석</div>
<h1>기후복지 취약지역 군집 분석</h1>
<div class="desc">전국 시군구를 기후재난 취약 특성에 따라 3개 군집으로 나눴습니다. 군집별 인구 특성, 기후 위험, 쉼터 현황을 비교해 보세요.</div>
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
    if n == 0:
        continue
    pct = n / total * 100
    label = f"{pct:.0f}%" if pct >= 8 else ""
    segments += f'<div style="flex:{n};background:{CLUSTER_COLORS[cid]}">{label}</div>'

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
        textfont=dict(size=14, color="#F1F4F9"),
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="%{x}<br>" + label + ": %{y:.2f}<extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        height=320,
        bargap=0.5,
        showlegend=False,
        margin=dict(t=30, b=10, l=10, r=10),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(size=13)),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showticklabels=False,
            range=[0, max(cluster_mean[column].max(), 1e-9) * 1.25],
        ),
        hoverlabel=dict(
            bgcolor="#161B26",
            bordercolor="rgba(255,255,255,0.15)",
            font=dict(color="#F1F4F9", size=13),
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

st.write("")

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