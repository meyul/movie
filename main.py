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
    date_col = df.columns[0]
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

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "선택한 영화가 개봉 이후 날짜에 따라 관객 수가 어떻게 변화했는지(급상승·완만한 하락 등 흥행 패턴)를 한눈에 파악할 수 있습니다."
)

st.divider()


# ──────────────────────────────────────────
# 그래프 2 : 흥행 TOP 5 영화 일관객 비교
# ──────────────────────────────────────────
st.header("📊 그래프 2 — 흥행 TOP 5 영화 일관객 비교")
st.markdown("이 기간 일관객 합계가 가장 많은 **5편**의 날짜별 일관객을 한 화면에서 비교합니다.  \n"
            "오른쪽 범례의 영화 이름을 **클릭**하면 켜고 끌 수 있습니다.")

# 일관객 합계 기준 TOP 5 영화 선정
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="흥행 TOP 5 영화 — 날짜별 일관객 비교",
    labels={"날짜": "날짜", "일관객": "일관객 수 (명)", "영화명": "영화"},
    color_discrete_sequence=px.colors.qualitative.Bold,
)

fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수 (명)",
    title_font_size=18,
    height=500,
    legend=dict(
        title="영화 (클릭으로 켜기/끄기)",
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="lightgrey",
        borderwidth=1,
    ),
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "흥행 상위 5편의 개봉 시점과 관객 집중 기간이 서로 겹치는지, "
    "어떤 영화가 단기 폭발형인지 장기 흥행형인지 한눈에 비교할 수 있습니다."
)

st.divider()


# ──────────────────────────────────────────
# 그래프 3 : 날짜별 10위권 일관객 합계 (영역 그래프)
# ──────────────────────────────────────────
st.header("📊 그래프 3 — 날짜별 박스오피스 10위권 일관객 합계")
st.markdown("매일 10위권 영화의 일관객을 모두 더한 값입니다.  \n"
            "전체 극장가가 가장 뜨거웠던 날이 언제인지 확인해 보세요.")

# 날짜별 일관객 합계
daily_total = (
    df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .rename(columns={"일관객": "일관객합계"})
    .sort_values("날짜")
)

# 합계 TOP 3 날짜
top3_days = daily_total.nlargest(3, "일관객합계")

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객합계",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={"날짜": "날짜", "일관객합계": "일관객 합계 (명)"},
    color_discrete_sequence=["#457B9D"],
)

fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객 합계: %{y:,}명<extra></extra>",
    line=dict(width=1.5),
)

# TOP 3 날짜 수직선 + 날짜 라벨 추가
colors = ["#E63946", "#F4A261", "#2A9D8F"]   # 1위·2위·3위 색상

for i, (_, row) in enumerate(top3_days.iterrows()):
    date_str = row["날짜"].strftime("%Y-%m-%d")
    y_val    = row["일관객합계"]

    # 수직 점선
    fig3.add_vline(
        x=row["날짜"].value / 1e6,   # Plotly 내부 timestamp (ms)
        line_width=2,
        line_dash="dash",
        line_color=colors[i],
    )

    # 날짜 + 순위 라벨
    fig3.add_annotation(
        x=row["날짜"],
        y=y_val,
        text=f"  {i+1}위<br>{date_str}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=colors[i],
        arrowwidth=2,
        ax=30,
        ay=-50,
        font=dict(size=12, color=colors[i], family="Arial Black"),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor=colors[i],
        borderwidth=1.5,
        borderpad=4,
    )

fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 합계 (명)",
    title_font_size=18,
    height=500,
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "💡 이 그래프로 알 수 있는 것: "
    "연휴·주말·대작 개봉일 등 특정 시점에 전체 극장 관객이 급증하는 패턴을 파악하고, "
    "한 해 중 극장가가 가장 붐볐던 날이 언제인지 확인할 수 있습니다."
)

st.divider()


# ──────────────────────────────────────────
# 하단 데이터 미리보기 (접기/펼치기)
# ──────────────────────────────────────────
with st.expander("🗂️ 원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True, height=300)
