import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎵",
    layout="wide"
)

# ==========================================================
# CSS
# ==========================================================

try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
except:
    pass

# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("data/spotify.csv")

    df["ts"] = pd.to_datetime(df["ts"])

    # Gerekli sütunlar
    df["hours_played"] = df.get(
        "hours_played",
        df["ms_played"] / (1000 * 60 * 60)
    )

    df["year"] = df.get(
        "year",
        df["ts"].dt.year
    )

    df["year_month"] = df["ts"].dt.to_period("M").astype(str)

    df["hour"] = df.get(
        "hour",
        df["ts"].dt.hour
    )

    df["day_name"] = df.get(
        "day_name",
        df["ts"].dt.day_name()
    )

    df["platform_clean"] = df.get(
        "platform_clean",
        df["platform"]
    )

    return df


spotify = load_data()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🎛 Filters")

users = ["All"] + sorted(
    spotify["user"].dropna().unique().tolist()
)

selected_user = st.sidebar.selectbox(
    "User",
    users
)

years = ["All"] + sorted(
    spotify["year"].dropna().unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Year",
    years
)

platforms = ["All"] + sorted(
    spotify["platform_clean"].dropna().unique().tolist()
)

selected_platform = st.sidebar.selectbox(
    "Platform",
    platforms
)

# ==========================================================
# FILTERS
# ==========================================================

filtered = spotify.copy()

if selected_user != "All":
    filtered = filtered[
        filtered["user"] == selected_user
    ]

if selected_year != "All":
    filtered = filtered[
        filtered["year"] == selected_year
    ]

if selected_platform != "All":
    filtered = filtered[
        filtered["platform_clean"] == selected_platform
    ]

# ==========================================================
# TITLE
# ==========================================================

st.title("🎵 Spotify Dashboard")

st.caption(
    "Explore your Spotify Extended Streaming History"
)

st.divider()

# ==========================================================
# KPI
# ==========================================================

tracks = filtered[
    "master_metadata_track_name"
].nunique()

artists = filtered[
    "master_metadata_album_artist_name"
].nunique()

albums = filtered[
    "master_metadata_album_album_name"
].nunique()

hours = filtered[
    "hours_played"
].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🎵 Tracks",
    f"{tracks:,}"
)

c2.metric(
    "🎤 Artists",
    f"{artists:,}"
)

c3.metric(
    "💿 Albums",
    f"{albums:,}"
)

c4.metric(
    "⏱ Listening Hours",
    f"{hours:,.1f}"
)

st.divider()

# ==========================================================
# MONTHLY TREND
# ==========================================================

monthly = (
    filtered
    .groupby("year_month")
    .agg(
        Hours=("hours_played", "sum")
    )
    .reset_index()
)

fig_month = px.line(
    monthly,
    x="year_month",
    y="Hours",
    markers=True,
    title="📈 Monthly Listening Trend"
)

fig_month.update_layout(
    height=500,
    xaxis_title="Month",
    yaxis_title="Listening Hours"
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)

st.divider()

# ==========================================================
# TOP ARTISTS
# ==========================================================

left, right = st.columns(2)

top_artists = (
    filtered
    .dropna(
        subset=[
            "master_metadata_album_artist_name"
        ]
    )
    .groupby(
        "master_metadata_album_artist_name"
    )
    .size()
    .reset_index(name="Play Count")
    .sort_values(
        "Play Count",
        ascending=False
    )
    .head(10)
)

fig_artist = px.bar(
    top_artists,
    x="Play Count",
    y="master_metadata_album_artist_name",
    orientation="h",
    title="🎤 Top 10 Artists"
)

fig_artist.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    ),
    height=450
)

left.plotly_chart(
    fig_artist,
    use_container_width=True
)

# ==========================================================
# TOP TRACKS
# ==========================================================

top_tracks = (
    filtered
    .dropna(subset=["master_metadata_track_name"])
    .groupby("master_metadata_track_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig_track = px.bar(
    top_tracks,
    x="Play Count",
    y="master_metadata_track_name",
    orientation="h",
    title="🎵 Top 10 Tracks"
)

fig_track.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=450
)

right.plotly_chart(
    fig_track,
    use_container_width=True
)

st.divider()

# ==========================================================
# LISTENING BY HOUR
# ==========================================================

col1, col2 = st.columns(2)

hourly = (
    filtered
    .groupby("hour")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

fig_hour = px.bar(
    hourly,
    x="hour",
    y="Hours",
    title="🕒 Listening by Hour",
    text_auto=".1f"
)

fig_hour.update_layout(
    xaxis_title="Hour",
    yaxis_title="Listening Hours",
    height=450
)

col1.plotly_chart(fig_hour, use_container_width=True)

# ==========================================================
# LISTENING BY WEEKDAY
# ==========================================================

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday = (
    filtered
    .groupby("day_name")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

weekday["day_name"] = pd.Categorical(
    weekday["day_name"],
    categories=weekday_order,
    ordered=True
)

weekday = weekday.sort_values("day_name")

fig_week = px.bar(
    weekday,
    x="day_name",
    y="Hours",
    title="📅 Listening by Weekday",
    text_auto=".1f"
)

fig_week.update_layout(
    height=450,
    xaxis_title="Weekday",
    yaxis_title="Listening Hours"
)

col2.plotly_chart(fig_week, use_container_width=True)

st.divider()

# ==========================================================
# YEARLY LISTENING
# ==========================================================

yearly = (
    filtered
    .groupby("year")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

fig_year = px.bar(
    yearly,
    x="year",
    y="Hours",
    title="📈 Listening Hours by Year",
    text_auto=".1f"
)

fig_year.update_layout(
    height=500
)

st.plotly_chart(fig_year, use_container_width=True)

st.divider()

# ==========================================================
# PLATFORM USAGE
# ==========================================================

platform = (
    filtered
    .groupby("platform_clean")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
)

fig_platform = px.pie(
    platform,
    names="platform_clean",
    values="Play Count",
    hole=0.5,
    title="📱 Platform Usage"
)

st.plotly_chart(fig_platform, use_container_width=True)

st.divider()

# ==========================================================
# LISTENING TIME DISTRIBUTION
# ==========================================================

st.divider()

artist_hours = (
    filtered
    .dropna(subset=["master_metadata_album_artist_name"])
    .groupby("master_metadata_album_artist_name")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
    .sort_values("Hours", ascending=False)
)

top5 = artist_hours.head(5).copy()

others = artist_hours.iloc[5:]["Hours"].sum()

if others > 0:
    top5.loc[len(top5)] = {
        "master_metadata_album_artist_name": "Others",
        "Hours": others
    }

fig = px.pie(
    top5,
    names="master_metadata_album_artist_name",
    values="Hours",
    hole=0.60,
    title="🎧 Listening Time Distribution"
)

fig.update_traces(textposition="inside")

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# RECENT LISTENING HISTORY
# ==========================================================

st.subheader("📝 Recent Listening History")

recent = (
    filtered[
        [
            "ts",
            "user",
            "master_metadata_track_name",
            "master_metadata_album_artist_name",
            "master_metadata_album_album_name",
            "hours_played"
        ]
    ]
    .sort_values("ts", ascending=False)
    .head(20)
)

recent.columns = [
    "Date",
    "User",
    "Track",
    "Artist",
    "Album",
    "Hours"
]

st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True
)

st.divider()


# ==========================================================
# LISTENING HEATMAP
# ==========================================================

st.divider()

st.subheader("🔥 Listening Heatmap")

heatmap = (
    filtered
    .groupby(["day_name", "hour"])
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

heatmap["day_name"] = pd.Categorical(
    heatmap["day_name"],
    categories=weekday_order,
    ordered=True
)

heatmap = heatmap.pivot(
    index="day_name",
    columns="hour",
    values="Hours"
).fillna(0)

fig_heat = px.imshow(
    heatmap,
    aspect="auto",
    labels=dict(
        x="Hour",
        y="Weekday",
        color="Hours"
    ),
    color_continuous_scale="Viridis",
    title="Listening Intensity by Day & Hour"
)

fig_heat.update_layout(
    height=500
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)


# ==========================================================
# TOP ALBUMS
# ==========================================================

st.divider()

top_albums = (
    filtered
    .dropna(subset=["master_metadata_album_album_name"])
    .groupby("master_metadata_album_album_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig_album = px.bar(
    top_albums,
    x="Play Count",
    y="master_metadata_album_album_name",
    orientation="h",
    title="💿 Top 10 Albums",
    color="Play Count",
    color_continuous_scale="Greens"
)

fig_album.update_layout(
    height=500,
    yaxis=dict(categoryorder="total ascending"),
    coloraxis_showscale=False
)

st.plotly_chart(fig_album, use_container_width=True)

# ==========================================================
# COUNTRY ANALYSIS
# ==========================================================

st.divider()

st.subheader("🌍 Listening by Country")

country = (
    filtered
    .groupby("conn_country")
    .agg(
        Hours=("hours_played", "sum")
    )
    .reset_index()
    .sort_values("Hours", ascending=False)
)

fig_country = px.bar(
    country,
    x="conn_country",
    y="Hours",
    text_auto=".1f",
    title="Listening Hours by Country"
)

fig_country.update_layout(
    height=450,
    xaxis_title="Country",
    yaxis_title="Hours"
)

st.plotly_chart(
    fig_country,
    use_container_width=True
)

# ==========================================================
# DEVICE USAGE
# ==========================================================

st.divider()

st.subheader("📱 Device Usage")

device = (
    filtered
    .groupby("platform_clean")
    .agg(
        Hours=("hours_played", "sum")
    )
    .reset_index()
    .sort_values("Hours", ascending=False)
)

fig_device = px.bar(
    device,
    x="platform_clean",
    y="Hours",
    text_auto=".1f",
    color="Hours",
    title="Listening Hours by Device"
)

fig_device.update_layout(
    height=450,
    xaxis_title="Platform",
    yaxis_title="Hours",
    coloraxis_showscale=False
)

st.plotly_chart(
    fig_device,
    use_container_width=True
)

# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

st.subheader("📊 Dashboard Summary")

summary = pd.DataFrame({
    "Metric": [
        "Tracks",
        "Artists",
        "Albums",
        "Listening Hours"
    ],
    "Value": [
        tracks,
        artists,
        albums,
        round(hours, 1)
    ]
})

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)
# ==========================================================
# FAVORITE DAY
# ==========================================================

st.divider()

favorite_day = (
    filtered
    .groupby("day_name")
    .agg(Hours=("hours_played", "sum"))
    .sort_values("Hours", ascending=False)
)

st.subheader("🏆 Favorite Listening Day")

st.success(
    f"You listen the most on **{favorite_day.index[0]}** "
    f"({favorite_day.iloc[0,0]:.1f} hours)"
)

# ==========================================================
# FAVORITE HOUR
# ==========================================================

favorite_hour = (
    filtered
    .groupby("hour")
    .agg(Hours=("hours_played", "sum"))
    .sort_values("Hours", ascending=False)
)

st.success(
    f"🕒 Favorite Hour: **{favorite_hour.index[0]}:00** "
    f"({favorite_hour.iloc[0,0]:.1f} hours)"
)

# ==========================================================
# QUICK STATS
# ==========================================================

st.divider()

col1, col2, col3 = st.columns(3)

col1.info(f"🎵 Total Plays: {len(filtered):,}")

col2.info(
    f"⏱ Average Song Length: "
    f"{filtered['ms_played'].mean()/1000/60:.2f} min"
)

col3.info(
    f"🔥 Longest Play: "
    f"{filtered['hours_played'].max():.2f} hours"
)

# ==========================================================
# SPOTIFY INSIGHTS
# ==========================================================

st.divider()

st.subheader("🔥 Spotify Insights")

col1, col2 = st.columns(2)

# Most Played Artist
top_artist = (
    filtered["master_metadata_album_artist_name"]
    .value_counts()
    .reset_index()
)

top_artist.columns = ["Artist", "Play Count"]

col1.metric(
    "🎤 Most Played Artist",
    top_artist.iloc[0]["Artist"]
)

# Most Played Track
top_track = (
    filtered["master_metadata_track_name"]
    .value_counts()
    .reset_index()
)

top_track.columns = ["Track", "Play Count"]

col2.metric(
    "🎵 Most Played Track",
    top_track.iloc[0]["Track"]
)

st.divider()

# Longest Listening Day

daily = (
    filtered
    .groupby("date")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

best_day = daily.sort_values(
    "Hours",
    ascending=False
).iloc[0]

st.metric(
    "📅 Longest Listening Day",
    f"{best_day['date']} ({best_day['Hours']:.1f} h)"
)

st.divider()

# Platform Usage Table

st.subheader("📱 Platform Usage")

platform_table = (
    filtered["platform_clean"]
    .value_counts()
    .reset_index()
)

platform_table.columns = [
    "Platform",
    "Play Count"
]

st.dataframe(
    platform_table,
    use_container_width=True,
    hide_index=True
)

# ==========================================================
# DISCOVERY SCORE
# ==========================================================

st.divider()

st.subheader("🌍 Discovery Score")

artist_count = filtered["master_metadata_album_artist_name"].nunique()
track_count = filtered["master_metadata_track_name"].nunique()

if track_count == 0:
    discovery = 0
else:
    discovery = min(100, round((artist_count / track_count) * 300))

col1, col2 = st.columns([1,3])

col1.metric(
    "Score",
    f"{discovery}/100"
)

col2.progress(discovery/100)

if discovery >= 80:
    st.success("🎧 You explore lots of different artists.")
elif discovery >= 60:
    st.info("🎵 Good balance between new music and favorites.")
else:
    st.warning("🔁 You mostly listen to the same artists.")
    # ==========================================================
# REPEAT SCORE
# ==========================================================

st.divider()

st.subheader("🔁 Repeat Score")

total_plays = len(filtered)
unique_tracks = filtered["master_metadata_track_name"].nunique()

if total_plays == 0:
    repeat_score = 0
else:
    repeat_score = round(
        (1 - unique_tracks / total_plays) * 100
    )

repeat_score = max(0, repeat_score)

col1, col2 = st.columns([1,3])

col1.metric(
    "Score",
    f"{repeat_score}%"
)
col2.progress(repeat_score/100)

if repeat_score > 80:
    st.info("🎵 You love replaying your favorite songs.")
elif repeat_score > 50:
    st.success("🎧 Nice mix of repeats and new songs.")
else:
    st.success("🌍 You rarely replay the same songs.")

