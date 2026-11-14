
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

# 프로젝트 최상위 경로
BASE_DIR = Path(__file__).resolve().parents[2]

# 분석 결과 CSV 경로
DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "지역별_지원우선순위.csv"
)


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


# ==========================================
# 3. 메인 화면
# ==========================================

st.title("🌤️ SafeWeather-AI")

st.subheader(
    "AI 기반 기후재난 복지 취약지역 분석 및 지원 우선순위 추천 시스템"
)

st.markdown("""
폭염과 한파 등 기후재난에 취약한 지역을 분석하고,
고령인구 및 노인 1인 가구, 기후 위험, 쉼터 현황을 바탕으로
지역별 지원 우선순위를 제시하는 시스템입니다.
""")

st.divider()


# ==========================================
# 4. 데이터 로딩 및 주요 현황
# ==========================================

if not DATA_PATH.exists():
    st.error(f"분석 데이터 파일을 찾을 수 없습니다.\n\n{DATA_PATH}")

else:
    load_data.clear()
    df = load_data()

    # 지원 우선순위 등급별 지역 수
    grade_order = ["일반", "관심", "주의", "우선지원"]

    grade_counts = (
        df["지원_우선순위_등급"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    priority_count = int(grade_counts["우선지원"])
    avg_score = df["지원_우선순위_점수"].mean()

    # ======================================
    # 5. 주요 분석 지표
    # ======================================

    st.header("📊 전국 기후복지 취약지역 현황")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "분석 대상 지역",
        f"{len(df):,}개"
    )

    col2.metric(
        "우선지원 대상 지역",
        f"{priority_count:,}개"
    )

    col3.metric(
        "평균 지원 우선순위 점수",
        f"{avg_score:.2f}점"
    )

    st.divider()

# ======================================
# 6. 지원 우선순위 등급별 현황
# ======================================

st.header("지원 우선순위 등급별 지역 분포")

chart_col, table_col = st.columns([2, 1])

with chart_col:
    # 1. Plotly용 데이터프레임 변환
    chart_df = grade_counts.reset_index()
    chart_df.columns = ["지원 우선순위", "지역 수"]

    # 2. Plotly 바차트 생성 (색상도 예쁘게 지정 가능)
    fig = px.bar(
        chart_df,
        x="지원 우선순위",
        y="지역 수",
        text="지역 수",
        color="지원 우선순위",
        color_discrete_map={
            "일반": "#4CAF50",
            "관심": "#38bdf8",
            "주의": "#fbbf24",
            "우선지원": "#f87171",
        },
    )

    # 3. 👉 핵심: X축 글씨를 0도(가로)로 회전하고 레이아웃 깔끔하게 정리
    fig.update_xaxes(tickangle=0)
    fig.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10))

    # 4. Streamlit에 출력
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    grade_table = grade_counts.rename_axis("지원 우선순위").reset_index()
    grade_table.columns = ["지원 우선순위", "지역 수"]

    st.dataframe(
        grade_table, hide_index=True, use_container_width=True
    )

    # ======================================
    # 7. 우선지원 상위 10개 지역
    # ======================================

    st.header("🏆 지원 우선순위 상위 10개 지역")

    top10 = (
        df.sort_values(
            "지원_우선순위_점수",
            ascending=False
        )
        .head(10)
        [[
            "시도",
            "시군구",
            "지원_우선순위_점수",
            "지원_우선순위_등급"
        ]]
        .reset_index(drop=True)
    )

    top10.index = top10.index + 1

    st.dataframe(
        top10,
        use_container_width=True
    )

    st.divider()


# ==========================================
# 8. 프로젝트 분석 안내
# ==========================================

st.header("🔎 주요 분석 기능")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📍 지역별 분석")
    st.write("""
    전국 시군구별 기후복지 취약지역을
    지도와 지역별 지표를 통해 확인합니다.
    """)

with col2:
    st.subheader("📊 취약성 분석")
    st.write("""
    K-Means 군집 분석을 통해
    지역별 기후재난 취약 특성을 비교합니다.
    """)

with col3:
    st.subheader("🎯 우선순위 추천")
    st.write("""
    종합 취약성 점수를 바탕으로
    지원이 필요한 지역의 우선순위를 제시합니다.
    """)

st.divider()

st.caption(
    "SafeWeather-AI | 기후재난 복지 취약지역 분석 시스템"
)
