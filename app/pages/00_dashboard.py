import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="SafeWeather-AI",
    page_icon="🌤️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "지역별_지원우선순위.csv"
)

# 등급 순서와 색상 (한 곳에서 관리)
GRADE_ORDER = ["일반", "관심", "주의", "우선지원"]
GRADE_COLORS = {
    "일반": "#34D399",
    "관심": "#38BDF8",
    "주의": "#FBBF24",
    "우선지원": "#F87171",
}

BG = "#0E1117"
CARD = "#161B26"
BORDER = "rgba(255,255,255,0.08)"
MUTED = "#9AA4B2"


# ==========================================
# 2. 스타일 (CSS)
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

/* 헤더 영역: 한파(파랑)에서 폭염(빨강)으로 이어지는 띠 */
.hero {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 34px 36px 30px 36px;
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
}
.hero::before {
    content: "";
    position: absolute;
    left: 0; top: 0; right: 0;
    height: 5px;
    background: linear-gradient(90deg, #38BDF8 0%, #FBBF24 55%, #F87171 100%);
}
.hero h1 {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0 0 6px 0;
    padding: 0;
}
.hero .sub {
    font-size: 1.05rem;
    font-weight: 600;
    color: #E5E9F0;
    margin-bottom: 12px;
}
.hero .desc {
    color: #9AA4B2;
    line-height: 1.7;
    font-size: 0.95rem;
    max-width: 720px;
}

/* 섹션 제목 */
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

/* KPI 카드 */
.kpi {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 22px;
    height: 100%;
}
.kpi .label {
    color: #9AA4B2;
    font-size: 0.85rem;
    margin-bottom: 8px;
}
.kpi .value {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.kpi .unit {
    font-size: 1rem;
    font-weight: 600;
    color: #9AA4B2;
    margin-left: 4px;
}
.kpi.alert {
    border-color: rgba(248,113,113,0.45);
}
.kpi.alert .value {
    color: #F87171;
}

/* 등급 카드 */
.grade {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--c);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.grade .name {
    font-weight: 700;
    color: var(--c);
    font-size: 0.95rem;
}
.grade .share {
    color: #9AA4B2;
    font-size: 0.8rem;
    margin-top: 2px;
}
.grade .count {
    font-size: 1.4rem;
    font-weight: 800;
}
.grade .count span {
    font-size: 0.85rem;
    font-weight: 600;
    color: #9AA4B2;
    margin-left: 3px;
}

/* 기능 안내 카드 */
.feature {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 22px;
    height: 100%;
}
.feature .icon {
    font-size: 1.6rem;
    margin-bottom: 10px;
}
.feature .title {
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 8px;
}
.feature .text {
    color: #9AA4B2;
    font-size: 0.9rem;
    line-height: 1.65;
}

/* 상위 10개 표 (잘림 없이 전체 표시) */
.rank-wrap {
    background: #161B26;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    overflow: hidden;
}
.rank-table {
    width: 100%;
    border-collapse: collapse;
}
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
    padding: 10px 14px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.92rem;
    white-space: nowrap;
    vertical-align: middle;
}
.rank-table .rk {
    font-weight: 700;
    color: #9AA4B2;
    width: 44px;
}
.rank-table .score {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 150px;
}
.rank-table .track {
    flex: 1;
    height: 6px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
}
.rank-table .fill {
    height: 100%;
    border-radius: 999px;
    background: var(--c);
}
.rank-table .num {
    font-weight: 700;
    min-width: 44px;
    text-align: right;
}
.rank-table .chip {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--c);
    background: color-mix(in srgb, var(--c) 16%, transparent);
}

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


# ==========================================
# 4. 헤더
# ==========================================

st.markdown(
    """
<div class="hero">
<h1>🌤️ SafeWeather-AI</h1>
<div class="sub">AI 기반 기후재난 복지 취약지역 분석 및 지원 우선순위 추천 시스템</div>
<div class="desc">폭염과 한파에 취약한 지역을 찾아냅니다. 고령인구와 노인 1인 가구, 기후 위험, 쉼터 현황을 종합해 지역별 지원 우선순위를 제시합니다.</div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 5. 데이터 로딩
# ==========================================

if not DATA_PATH.exists():
    st.error(f"분석 데이터 파일을 찾을 수 없습니다.\n\n{DATA_PATH}")
    st.stop()

load_data.clear()
df = load_data()

grade_counts = (
    df["지원_우선순위_등급"]
    .value_counts()
    .reindex(GRADE_ORDER, fill_value=0)
)

total = len(df)
priority_count = int(grade_counts["우선지원"])
avg_score = df["지원_우선순위_점수"].mean()


# ==========================================
# 6. 주요 지표
# ==========================================

st.markdown('<div class="sec-title">전국 현황</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">분석 대상 전체 시군구의 핵심 지표입니다.</div>',
    unsafe_allow_html=True,
)

k1, k2, k3 = st.columns(3)

k1.markdown(
    f'<div class="kpi"><div class="label">분석 대상 지역</div>'
    f'<div class="value">{total:,}<span class="unit">개</span></div></div>',
    unsafe_allow_html=True,
)
k2.markdown(
    f'<div class="kpi alert"><div class="label">우선지원 대상 지역</div>'
    f'<div class="value">{priority_count:,}<span class="unit">개</span></div></div>',
    unsafe_allow_html=True,
)
k3.markdown(
    f'<div class="kpi"><div class="label">평균 지원 우선순위 점수</div>'
    f'<div class="value">{avg_score:.2f}<span class="unit">점</span></div></div>',
    unsafe_allow_html=True,
)


# ==========================================
# 7. 등급별 분포
# ==========================================

st.markdown('<div class="sec-title">지원 우선순위 등급별 분포</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">전국 시군구를 4개 등급으로 나눈 결과입니다.</div>',
    unsafe_allow_html=True,
)

chart_col, summary_col = st.columns([2.2, 1], gap="large")

with chart_col:
    chart_df = grade_counts.reset_index()
    chart_df.columns = ["지원 우선순위", "지역 수"]

    fig = px.bar(
        chart_df,
        x="지원 우선순위",
        y="지역 수",
        text="지역 수",
        color="지원 우선순위",
        color_discrete_map=GRADE_COLORS,
        category_orders={"지원 우선순위": GRADE_ORDER},
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14, color="#E5E9F0"),
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y}개 지역<extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        height=340,
        bargap=0.45,
        showlegend=False,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(size=14)),
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showticklabels=False,
            range=[0, max(grade_counts.max(), 1) * 1.2],
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with summary_col:
    cards = ""
    # 우선지원이 가장 위에 오도록 역순 표시
    for grade in reversed(GRADE_ORDER):
        n = int(grade_counts[grade])
        share = n / total * 100 if total else 0
        cards += (
            f'<div class="grade" style="--c:{GRADE_COLORS[grade]}">'
            f'<div><div class="name">{grade}</div>'
            f'<div class="share">전체의 {share:.1f}%</div></div>'
            f'<div class="count">{n:,}<span>개</span></div></div>'
        )
    st.markdown(cards, unsafe_allow_html=True)


# ==========================================
# 8. 상위 10개 지역
# ==========================================

st.markdown('<div class="sec-title">지원 우선순위 상위 10개 지역</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">점수가 높을수록 먼저 지원이 필요한 지역입니다.</div>',
    unsafe_allow_html=True,
)

top10 = (
    df.sort_values("지원_우선순위_점수", ascending=False)
    .head(10)[["시도", "시군구", "지원_우선순위_점수", "지원_우선순위_등급"]]
    .reset_index(drop=True)
)
top10.insert(0, "순위", range(1, len(top10) + 1))
top10["지역"] = top10["시도"] + " " + top10["시군구"]

bar_col, table_col = st.columns([1, 1.15], gap="large")

with bar_col:
    fig2 = px.bar(
        top10,
        x="지원_우선순위_점수",
        y="지역",
        orientation="h",
        text="지원_우선순위_점수",
        color="지원_우선순위_등급",
        color_discrete_map=GRADE_COLORS,
        category_orders={"지원_우선순위_등급": GRADE_ORDER},
    )

    fig2.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        textfont=dict(size=12, color="#E5E9F0"),
        marker_line_width=0,
        cliponaxis=False,
        hovertemplate="%{y}<br>%{x:.2f}점<extra></extra>",
    )

    fig2.update_layout(
        template="plotly_dark",
        height=440,
        bargap=0.35,
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=50),
        xaxis=dict(
            title=None,
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            showticklabels=False,
            range=[0, top10["지원_우선순위_점수"].max() * 1.15],
        ),
        yaxis=dict(title=None, autorange="reversed", tickfont=dict(size=13)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with table_col:
    max_score = top10["지원_우선순위_점수"].max()
    rows = ""
    for _, r in top10.iterrows():
        color = GRADE_COLORS.get(r["지원_우선순위_등급"], "#9AA4B2")
        width = r["지원_우선순위_점수"] / max_score * 100 if max_score else 0
        rows += (
            f'<tr style="--c:{color}">'
            f'<td class="rk">{r["순위"]}위</td>'
            f'<td>{r["시도"]} {r["시군구"]}</td>'
            f'<td><div class="score"><div class="track">'
            f'<div class="fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="num">{r["지원_우선순위_점수"]:.2f}</div></div></td>'
            f'<td><span class="chip">{r["지원_우선순위_등급"]}</span></td>'
            f'</tr>'
        )
    st.markdown(
        '<div class="rank-wrap"><table class="rank-table">'
        '<thead><tr><th>순위</th><th>지역</th><th>점수</th><th>등급</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ==========================================
# 9. 주요 분석 기능
# ==========================================

st.markdown('<div class="sec-title">주요 분석 기능</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sec-desc">왼쪽 메뉴에서 각 분석 페이지로 이동할 수 있습니다.</div>',
    unsafe_allow_html=True,
)

features = [
    ("📍", "지역별 분석", "전국 시군구별 기후복지 취약지역을 지도와 지역별 지표로 확인합니다."),
    ("📊", "취약성 분석", "K-Means 군집 분석으로 지역별 기후재난 취약 특성을 비교합니다."),
    ("🎯", "우선순위 추천", "종합 취약성 점수를 바탕으로 지원이 필요한 지역의 우선순위를 제시합니다."),
]

f_cols = st.columns(3, gap="medium")
for col, (icon, title, text) in zip(f_cols, features):
    col.markdown(
        f'<div class="feature"><div class="icon">{icon}</div>'
        f'<div class="title">{title}</div>'
        f'<div class="text">{text}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer">SafeWeather-AI | 기후재난 복지 취약지역 분석 시스템</div>',
    unsafe_allow_html=True,
)