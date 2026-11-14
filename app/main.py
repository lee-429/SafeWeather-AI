import streamlit as st

st.set_page_config(
    page_title="SafeWeather-AI",
    page_icon="🌤️",
    layout="wide"
)

# 페이지 구성
pages = {
    "서비스": [
        st.Page(
            "pages/00_dashboard.py",
            title="메인 대시보드",
            icon="🏠",
            default=True
        )
    ],
    "지역 및 데이터 분석": [
        st.Page(
            "pages/01_regional_analysis.py",
            title="지역별 분석",
            icon="🗺️"
        ),
        st.Page(
            "pages/02_cluster_analysis.py",
            title="취약성 분석",
            icon="📊"
        )
    ]
}

# 사이드바 페이지 이동
pg = st.navigation(pages)

st.sidebar.title("🌤️ SafeWeather-AI")
st.sidebar.caption("기후재난 복지 취약지역 분석")

pg.run()
