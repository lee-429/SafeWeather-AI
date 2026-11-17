import streamlit as st
import pandas as pd
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


# ==========================================
# 2. 스타일 (CSS)
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
    --cold: #38BDF8;
    --warm: #FBBF24;
    --hot: #F87171;
    --ease: cubic-bezier(.22,.61,.36,1);
}

/* Streamlit 기본 요소 정리 */
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
.hero {
    padding: 44px 0 36px 0;
    animation: rise .7s var(--ease) both;
}
.hero .pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 999px;
    background: var(--glass);
    border: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.82rem;
    font-weight: 500;
    margin-bottom: 22px;
}
.hero .pill i {
    width: 8px; height: 8px; border-radius: 50%;
    background: linear-gradient(90deg, var(--cold), var(--hot));
}
.hero h1 {
    font-size: 3.1rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin: 0 0 16px 0;
    padding: 0;
    background: linear-gradient(90deg, #7DD3FC 0%, #FDE68A 50%, #FCA5A5 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    width: fit-content;
}
.hero .sub {
    font-size: 1.12rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 10px;
}
.hero .desc {
    color: var(--muted);
    line-height: 1.75;
    font-size: 0.98rem;
    max-width: 640px;
}
@keyframes rise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- 섹션 제목 ---------- */
.sec-title {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 44px 0 4px 0;
}
.sec-desc {
    color: var(--muted);
    font-size: 0.92rem;
    margin-bottom: 18px;
}

/* ---------- KPI ---------- */
.kpi {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 24px 26px;
    height: 100%;
    transition: background .25s var(--ease), border-color .25s var(--ease);
}
.kpi:hover { background: var(--glass-strong); }
.kpi .label { color: var(--muted); font-size: 0.88rem; margin-bottom: 14px; }
.kpi .value {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
}
.kpi .unit {
    font-size: 1rem;
    font-weight: 600;
    color: var(--muted);
    margin-left: 5px;
}
.kpi.alert {
    background: linear-gradient(160deg, rgba(248,113,113,0.20), rgba(248,113,113,0.05));
    border-color: rgba(248,113,113,0.35);
}
.kpi.alert .value { color: #FCA5A5; }

/* ---------- 등급 분포 ---------- */
.dist {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 26px;
}
.dist .bar {
    display: flex;
    gap: 4px;
    height: 54px;
}
.dist .seg {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 6px;
    color: #0A0E16;
    font-weight: 700;
    font-size: 0.9rem;
    background: var(--c);
    transition: filter .2s var(--ease), transform .2s var(--ease);
}
.dist .seg:first-child { border-radius: 14px 5px 5px 14px; }
.dist .seg:last-child  { border-radius: 5px 14px 14px 5px; }
.dist .seg:only-child  { border-radius: 14px; }
.dist .seg:hover { filter: brightness(1.12); transform: translateY(-2px); }
.dist .legend {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 22px;
}
.dist .item { padding-left: 14px; border-left: 3px solid var(--c); }
.dist .item .name { color: var(--muted); font-size: 0.85rem; margin-bottom: 4px; }
.dist .item .count { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; }
.dist .item .count span { font-size: 0.85rem; font-weight: 600; color: var(--muted); margin-left: 3px; }
.dist .item .share { color: var(--muted); font-size: 0.8rem; margin-top: 2px; }

/* ---------- 상위 10개 ---------- */
.rank {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 10px;
}
.rank-row {
    display: grid;
    grid-template-columns: 44px 1.1fr 2fr 84px;
    align-items: center;
    gap: 16px;
    padding: 14px 16px;
    border-radius: 14px;
    transition: background .2s var(--ease);
}
.rank-row:hover { background: var(--glass-strong); }
.rank-row .no {
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px;
    background: rgba(255,255,255,0.06);
    color: var(--muted);
    font-weight: 700;
    font-size: 0.85rem;
}
.rank-row.top .no { background: var(--c); color: #0A0E16; }
.rank-row .area { font-weight: 600; font-size: 0.97rem; white-space: nowrap; }
.rank-row .area small { color: var(--muted); font-weight: 500; margin-right: 6px; }
.rank-row .meter { display: flex; align-items: center; gap: 14px; }
.rank-row .track { flex: 1; height: 8px; border-radius: 999px; background: rgba(255,255,255,0.07); }
.rank-row .fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, color-mix(in srgb, var(--c) 55%, transparent), var(--c));
}
.rank-row .num { font-weight: 700; min-width: 46px; text-align: right; font-variant-numeric: tabular-nums; }
.rank-row .chip {
    justify-self: end;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--c);
    background: color-mix(in srgb, var(--c) 15%, transparent);
}

/* ---------- 기능 안내 ---------- */
.feature {
    background: var(--glass);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 26px;
    height: 100%;
    transition: background .25s var(--ease), transform .25s var(--ease);
}
.feature:hover { background: var(--glass-strong); transform: translateY(-3px); }
.feature .icon {
    width: 46px; height: 46px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    border-radius: 14px;
    background: rgba(255,255,255,0.07);
    margin-bottom: 16px;
}
.feature .title { font-weight: 700; font-size: 1.08rem; margin-bottom: 8px; letter-spacing: -0.01em; }
.feature .text { color: var(--muted); font-size: 0.9rem; line-height: 1.7; }

.footer {
    text-align: center;
    color: #657084;
    font-size: 0.8rem;
    margin-top: 56px;
    padding-top: 22px;
    border-top: 1px solid var(--line);
}

/* ---------- 모바일 ---------- */
@media (max-width: 720px) {
    .hero h1 { font-size: 2.2rem; }
    .dist .legend { grid-template-columns: repeat(2, 1fr); }
    .rank-row { grid-template-columns: 36px 1fr 70px; }
    .rank-row .meter { display: none; }
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


# ==========================================
# 4. 헤더
# ==========================================

st.markdown(
    """
<div class="hero">
<div class="pill"><i></i>폭염 · 한파 복지 취약지역 분석</div>
<h1>SafeWeather-AI</h1>
<div class="sub">기후재난에 가장 먼저 지원이 필요한 지역을 찾아드립니다</div>
<div class="desc">고령인구와 노인 1인 가구, 기후 위험, 쉼터 현황을 종합해 전국 시군구의 지원 우선순위를 제시합니다.</div>
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

k1, k2, k3 = st.columns(3, gap="medium")

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

segs = ""
legend = ""
for grade in GRADE_ORDER:
    n = int(grade_counts[grade])
    share = n / total * 100 if total else 0
    color = GRADE_COLORS[grade]
    if n > 0:
        label = f"{share:.0f}%" if share >= 7 else ""
        segs += f'<div class="seg" style="--c:{color}; flex:{n}">{label}</div>'
    legend += (
        f'<div class="item" style="--c:{color}">'
        f'<div class="name">{grade}</div>'
        f'<div class="count">{n:,}<span>개</span></div>'
        f'<div class="share">전체의 {share:.1f}%</div></div>'
    )

st.markdown(
    f'<div class="dist"><div class="bar">{segs}</div>'
    f'<div class="legend">{legend}</div></div>',
    unsafe_allow_html=True,
)


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

max_score = top10["지원_우선순위_점수"].max()
rows = ""
for _, r in top10.iterrows():
    color = GRADE_COLORS.get(r["지원_우선순위_등급"], "#8F9AAB")
    width = r["지원_우선순위_점수"] / max_score * 100 if max_score else 0
    top_cls = " top" if r["순위"] <= 3 else ""
    rows += (
        f'<div class="rank-row{top_cls}" style="--c:{color}">'
        f'<div class="no">{r["순위"]}</div>'
        f'<div class="area"><small>{r["시도"]}</small>{r["시군구"]}</div>'
        f'<div class="meter"><div class="track">'
        f'<div class="fill" style="width:{width:.1f}%"></div></div>'
        f'<div class="num">{r["지원_우선순위_점수"]:.2f}</div></div>'
        f'<div class="chip">{r["지원_우선순위_등급"]}</div>'
        f'</div>'
    )

st.markdown(f'<div class="rank">{rows}</div>', unsafe_allow_html=True)


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