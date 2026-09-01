import streamlit as st
import pandas as pd
import plotly.express as px

# ──────────────────────────────────────────
# 페이지 기본 설정
# ──────────────────────────────────────────
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("일별 박스오피스 10위권 데이터를 시간 흐름으로 탐색합니다.")
st.divider()


# ──────────────────────────────────────────
# 데이터 불러오기 & 전처리
# ──────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url, encoding="utf-8")

    # 열 이름 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜 열을 진짜 datetime으로 변환 (여덟 자리 숫자 → YYYY-MM-DD)
    date_col = df.columns[0]          # 첫 번째 열 = 날짜
    df[date_col] = pd.to_datetime(df[date_col].astype(str), format="%Y%m%d")
    df = df.rename(columns={date_col: "날짜"})

    # 숫자 열 정리 (쉼표 포함 가능성 대비)
    for col in ["일관객", "누적관객", "스크린수", "상영횟수"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

    return df


df = load_data(DATA_URL)


# ──────────────────────────────────────────
# 그래프 1 : 영화별 일관객 추이
# ──────────────────────────────────────────
st.header("📈 그래프 1 — 영화별 일관객 추이")
st.markdown("드롭다운에서 영화를 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다.")

# 영화 목록 (누적관객 합계 기준 내림차순 정렬)
movie_order = (
    df.groupby("영화명")["누적관객"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

selected_movie = st.selectbox(
    "🎥 영화를 선택하세요",
    options=movie_order,
    key="movie_selectbox",
)

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"<b>{selected_movie}</b> — 날짜별 일관객",
    labels={"날짜": "날짜", "일관객": "일관객 수 (명)"},
    color_discrete_sequence=["#E63946"],
)

fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수 (명)",
    title_font_size=18,
    height=450,
)

st.plotly_chart(fig1, use_container_width=True)

# ▶ '이 그래프로 알 수 있는 것' 문구 자리
st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "선택한 영화가 개봉 이후 날짜에 따라 관객 수가 어떻게 변화했는지(급상승·완만한 하락 등 흥행 패턴)를 한눈에 파악할 수 있습니다."
)

st.divider()


# ──────────────────────────────────────────
# 그래프 2 : (추후 추가 예정)
# ──────────────────────────────────────────
st.header("📊 그래프 2 — (추후 추가 예정)")
st.markdown("여기에 두 번째 그래프와 설명을 추가하세요.")

# ── 그래프 코드를 아래에 작성하세요 ──


# ▶ '이 그래프로 알 수 있는 것' 문구 자리 (작성 후 주석 해제)
# st.info("💡 이 그래프로 알 수 있는 것: ...")

st.divider()


# ──────────────────────────────────────────
# 그래프 3 : (추후 추가 예정)
# ──────────────────────────────────────────
st.header("📊 그래프 3 — (추후 추가 예정)")
st.markdown("여기에 세 번째 그래프와 설명을 추가하세요.")

# ── 그래프 코드를 아래에 작성하세요 ──


# ▶ '이 그래프로 알 수 있는 것' 문구 자리 (작성 후 주석 해제)
# st.info("💡 이 그래프로 알 수 있는 것: ...")

st.divider()


# ──────────────────────────────────────────
# 하단 데이터 미리보기 (접기/펼치기)
# ──────────────────────────────────────────
with st.expander("🗂️ 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True, height=300)
