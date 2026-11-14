
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
    0: "#38bdf8",
    1: "#f87171",
    2: "#fbbf24"
}


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


st.title("📊 기후복지 취약지역 군집 분석")

st.markdown("""
K-Means 알고리즘을 활용하여 전국 시군구를
기후재난 취약 특성에 따라 3개 군집으로 분류했습니다.

각 군집의 인구 특성, 기후 위험 및 쉼터 현황을 비교할 수 있습니다.
""")

st.divider()


if not DATA_PATH.exists():
    st.error(f"군집 분석 데이터 파일을 찾을 수 없습니다.\n\n{DATA_PATH}")
    st.stop()

load_data.clear()
df = load_data()

df["군집_K3"] = df["군집_K3"].astype(int)
df["군집명"] = df["군집_K3"].map(CLUSTER_NAMES)

# ==========================================
# 3. 군집별 주요 현황
# ==========================================

st.header("📌 군집별 지역 분포")

cluster_counts = (
    df["군집_K3"]
    .value_counts()
    .sort_index()
)

col1, col2, col3 = st.columns(3)

for col, cluster_id in zip([col1, col2, col3], [0, 1, 2]):
    count = int(cluster_counts.get(cluster_id, 0))

    col.metric(
        CLUSTER_NAMES[cluster_id],
        f"{count}개 지역",
        f"{count / len(df) * 100:.1f}%"
    )


# ==========================================
# 4. 군집별 지역 분포 차트
# ==========================================

st.subheader("군집별 지역 수")

count_df = cluster_counts.reset_index()
count_df.columns = ["군집_K3", "지역 수"]

count_df["군집명"] = count_df["군집_K3"].map(CLUSTER_NAMES)

fig = px.bar(
    count_df,
    x="군집명",
    y="지역 수",
    text="지역 수",
    color="군집명",
    color_discrete_map={
        CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
        for k in CLUSTER_NAMES
    }
)

fig.update_layout(
    showlegend=False,
    margin=dict(t=30, b=10, l=10, r=10),
    xaxis_title="군집 유형",
    yaxis_title="지역 수"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


# ==========================================
# 5. 군집별 특성 비교
# ==========================================

st.header("📈 군집별 취약 특성 비교")

cluster_mean = (
    df.groupby("군집_K3")[
        [
            "노인_1인가구_비율",
            "폭염일수",
            "한파일수",
            "무더위쉼터_비율",
            "한파쉼터_비율"
        ]
    ]
    .mean()
    .reset_index()
)

cluster_mean["군집명"] = cluster_mean["군집_K3"].map(CLUSTER_NAMES)

tabs = st.tabs([
    "인구 취약성",
    "기후 위험",
    "쉼터 공급 현황"
])

# 인구 취약성
with tabs[0]:
    fig = px.bar(
        cluster_mean,
        x="군집명",
        y="노인_1인가구_비율",
        text_auto=".2f",
        color="군집명",
        color_discrete_map={
            CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
            for k in CLUSTER_NAMES
        },
        title="군집별 노인 1인 가구 비율"
    )

    fig.update_layout(showlegend=False, xaxis_title="군집 유형",
                      yaxis_title="노인 1인 가구 비율")

    st.plotly_chart(fig, use_container_width=True)

# 기후 위험
with tabs[1]:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            cluster_mean,
            x="군집명",
            y="폭염일수",
            text_auto=".2f",
            color="군집명",
            color_discrete_map={
                CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
                for k in CLUSTER_NAMES
            },
            title="군집별 평균 폭염일수"
        )
        fig.update_layout(showlegend=False, xaxis_title="군집 유형",
                          yaxis_title="평균 폭염일수")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            cluster_mean,
            x="군집명",
            y="한파일수",
            text_auto=".2f",
            color="군집명",
            color_discrete_map={
                CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
                for k in CLUSTER_NAMES
            },
            title="군집별 평균 한파일수"
        )
        fig.update_layout(showlegend=False, xaxis_title="군집 유형",
                          yaxis_title="평균 한파일수")
        st.plotly_chart(fig, use_container_width=True)

# 쉼터 공급 현황
with tabs[2]:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            cluster_mean,
            x="군집명",
            y="무더위쉼터_비율",
            text_auto=".2f",
            color="군집명",
            color_discrete_map={
                CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
                for k in CLUSTER_NAMES
            },
            title="군집별 무더위쉼터 비율"
        )
        fig.update_layout(showlegend=False, xaxis_title="군집 유형",
                          yaxis_title="무더위쉼터 비율")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            cluster_mean,
            x="군집명",
            y="한파쉼터_비율",
            text_auto=".2f",
            color="군집명",
            color_discrete_map={
                CLUSTER_NAMES[k]: CLUSTER_COLORS[k]
                for k in CLUSTER_NAMES
            },
            title="군집별 한파쉼터 비율"
        )
        fig.update_layout(showlegend=False, xaxis_title="군집 유형",
                          yaxis_title="한파쉼터 비율")
        st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 6. 군집별 평균 특성표
# ==========================================

st.divider()

st.header("📋 군집별 평균 특성")

display_df = cluster_mean[
    [
        "군집명",
        "노인_1인가구_비율",
        "폭염일수",
        "한파일수",
        "무더위쉼터_비율",
        "한파쉼터_비율"
    ]
].copy()

display_df.columns = [
    "군집 유형",
    "노인 1인 가구 비율",
    "폭염일수",
    "한파일수",
    "무더위쉼터 비율",
    "한파쉼터 비율"
]

st.dataframe(
    display_df.round(2),
    hide_index=True,
    use_container_width=True
)


# ==========================================
# 7. 군집별 지역 조회
# ==========================================

st.divider()

st.header("🔎 군집별 지역 조회")

selected_cluster = st.selectbox(
    "확인할 군집을 선택하세요.",
    options=[0, 1, 2],
    format_func=lambda x: f"군집 {x} - {CLUSTER_NAMES[x]}"
)

region_df = df[df["군집_K3"] == selected_cluster][
    [
        "시도",
        "시군구",
        "노인_1인가구_비율",
        "폭염일수",
        "한파일수",
        "군집명"
    ]
].copy()

region_df.columns = [
    "시도",
    "시군구",
    "노인 1인 가구 비율",
    "폭염일수",
    "한파일수",
    "군집 유형"
]

st.caption(f"총 {len(region_df)}개 지역")

st.dataframe(
    region_df.round(2),
    hide_index=True,
    use_container_width=True
)

st.divider()

st.caption(
    "SafeWeather-AI | K-Means 기반 기후복지 취약지역 군집 분석"
)