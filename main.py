import streamlit as st
import pandas as pd
import plotly.express as px

# ── 페이지 기본 설정 ───────────────────────────────────────────
st.set_page_config(page_title="어쩌구", page_icon="🎬", layout="wide")
st.title("🎬 어쩌구 – 일별 박스오피스 분석")

# ── 데이터 불러오기 ────────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url, dtype=str)

    # 열 이름 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜 변환 (YYYYMMDD → datetime)
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

    # 숫자 열 변환 (쉼표 제거 후 float형)
    num_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in num_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .str.replace(",", "", regex=False)
                .str.strip()
                .astype(float)
            )

    return df

df = load_data(DATA_URL)

# ── 데이터 미리보기 ────────────────────────────────────────────
with st.expander("📋 원본 데이터 미리보기", expanded=False):
    st.dataframe(df.head(30), use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 그래프 1 – 관객 수 × 스크린수 / 상영횟수 상관관계
# ══════════════════════════════════════════════════════════════
st.subheader("📊 그래프 1 : 관객 수와 상영 규모의 상관관계")
st.caption(
    "ℹ️ 원본 CSV에 장르 정보가 없어 **스크린수·상영횟수**를 상관관계 축으로 사용했습니다. "
    "장르 데이터가 추가되면 쉽게 교체할 수 있습니다."
)

# 영화별 평균 집계
agg = (
    df.groupby("영화명")[["스크린수", "상영횟수", "일관객", "누적관객"]]
    .mean()
    .reset_index()
    .rename(columns={
        "스크린수": "평균스크린수",
        "상영횟수": "평균상영횟수",
        "일관객":  "평균일관객",
        "누적관객": "평균누적관객",
    })
)

col1, col2 = st.columns(2)

# ── 서브그래프 1-A : 스크린수 vs 일관객 ───────────────────────
with col1:
    st.markdown("#### 스크린수 vs 일관객")

    fig1a = px.scatter(
        agg,
        x="평균스크린수",
        y="평균일관객",
        hover_name="영화명",
        size="평균누적관객",
        size_max=40,
        color="평균일관객",
        color_continuous_scale="Blues",
        trendline="lowess",        # ← ols → lowess 로 변경 (statsmodels 불필요)
        labels={
            "평균스크린수": "평균 스크린수 (개)",
            "평균일관객":  "평균 일관객 (명)",
        },
        title="스크린수와 일관객 수 상관관계",
    )
    fig1a.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig1a, use_container_width=True)

# ── 서브그래프 1-B : 상영횟수 vs 일관객 ──────────────────────
with col2:
    st.markdown("#### 상영횟수 vs 일관객")

    fig1b = px.scatter(
        agg,
        x="평균상영횟수",
        y="평균일관객",
        hover_name="영화명",
        size="평균누적관객",
        size_max=40,
        color="평균일관객",
        color_continuous_scale="Oranges",
        trendline="lowess",        # ← ols → lowess 로 변경 (statsmodels 불필요)
        labels={
            "평균상영횟수": "평균 상영횟수 (회)",
            "평균일관객":  "평균 일관객 (명)",
        },
        title="상영횟수와 일관객 수 상관관계",
    )
    fig1b.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig1b, use_container_width=True)

# ── 상관계수 표 ────────────────────────────────────────────────
st.markdown("#### 📌 주요 변수 간 상관계수")
corr_df = (
    df[["일관객", "누적관객", "스크린수", "상영횟수"]]
    .corr()
    .round(3)
)
st.dataframe(corr_df, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 그래프 2 – 날짜별 총 일관객 추이
# ══════════════════════════════════════════════════════════════
st.subheader("📈 그래프 2 : 날짜별 전체 일관객 추이")

daily_total = (
    df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .rename(columns={"일관객": "총일관객"})
)

fig2 = px.line(
    daily_total,
    x="날짜",
    y="총일관객",
    labels={"날짜": "날짜", "총일관객": "총 일관객 (명)"},
    title="날짜별 전체 일관객 합계",
)
fig2.update_traces(line_color="#4C72B0")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 그래프 3 – 영화별 누적관객 TOP 20
# ══════════════════════════════════════════════════════════════
st.subheader("🏆 그래프 3 : 영화별 최대 누적관객 TOP 20")

top20 = (
    df.groupby("영화명")["누적관객"]
    .max()
    .reset_index()
    .sort_values("누적관객", ascending=False)
    .head(20)
)

fig3 = px.bar(
    top20,
    x="누적관객",
    y="영화명",
    orientation="h",
    color="누적관객",
    color_continuous_scale="Viridis",
    labels={"누적관객": "최대 누적관객 (명)", "영화명": "영화"},
    title="누적관객 TOP 20",
)
fig3.update_layout(
    yaxis={"categoryorder": "total ascending"},
    coloraxis_showscale=False,
    height=600,
)
st.plotly_chart(fig3, use_container_width=True)
