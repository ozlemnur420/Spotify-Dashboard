import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Artist Analysis",
    page_icon="🎤",
    layout="wide"
)

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("data/spotify.csv")

    df["ts"] = pd.to_datetime(df["ts"])

    df["hours_played"] = df["ms_played"] / (1000 * 60 * 60)

    return df

spotify = load_data()

# ----------------------------------------------------
# TITLE
# ----------------------------------------------------

st.title("🎤 Artist Analysis")

st.caption("Analyze listening statistics for any artist")

st.divider()

# ----------------------------------------------------
# SELECT ARTIST
# ----------------------------------------------------

artists = sorted(
    spotify["master_metadata_album_artist_name"]
    .dropna()
    .unique()
)

artist = st.selectbox(
    "Choose Artist",
    artists
)

df = spotify[
    spotify["master_metadata_album_artist_name"] == artist
]

# ----------------------------------------------------
# KPI
# ----------------------------------------------------

tracks = df["master_metadata_track_name"].nunique()

albums = df["master_metadata_album_album_name"].nunique()

hours = round(df["hours_played"].sum(), 1)

plays = len(df)

c1, c2, c3, c4 = st.columns(4)

c1.metric("🎵 Tracks", tracks)
c2.metric("💿 Albums", albums)
c3.metric("▶ Plays", plays)
c4.metric("⏱ Hours", hours)

st.divider()

# ----------------------------------------------------
# MONTHLY LISTENING TREND
# ----------------------------------------------------

monthly = (
    df
    .groupby(df["ts"].dt.to_period("M").astype(str))
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

monthly.columns = ["Month", "Hours"]

fig = px.line(
    monthly,
    x="Month",
    y="Hours",
    markers=True,
    title="📈 Monthly Listening Trend"
)

fig.update_layout(
    height=450,
    xaxis_title="Month",
    yaxis_title="Listening Hours"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ----------------------------------------------------
# TOP TRACKS & ALBUMS
# ----------------------------------------------------

left, right = st.columns(2)

top_tracks = (
    df
    .groupby("master_metadata_track_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig_tracks = px.bar(
    top_tracks,
    x="Play Count",
    y="master_metadata_track_name",
    orientation="h",
    text_auto=True,
    title="🎵 Top Tracks"
)

fig_tracks.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=500
)

left.plotly_chart(
    fig_tracks,
    use_container_width=True
)

top_albums = (
    df
    .groupby("master_metadata_album_album_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig_albums = px.bar(
    top_albums,
    x="Play Count",
    y="master_metadata_album_album_name",
    orientation="h",
    text_auto=True,
    title="💿 Top Albums"
)

fig_albums.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=500
)

right.plotly_chart(
    fig_albums,
    use_container_width=True
)

st.divider()

# ----------------------------------------------------
# LISTENING BY HOUR
# ----------------------------------------------------

hourly = (
    df
    .groupby(df["ts"].dt.hour)
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

hourly.columns = ["Hour", "Hours"]

fig_hour = px.bar(
    hourly,
    x="Hour",
    y="Hours",
    text_auto=".1f",
    title="🕒 Listening by Hour"
)

fig_hour.update_layout(
    height=450
)

st.plotly_chart(
    fig_hour,
    use_container_width=True
)

st.divider()

# ----------------------------------------------------
# RECENT TRACKS
# ----------------------------------------------------

st.subheader("📝 Recent Tracks")

recent = (
    df[
        [
            "ts",
            "master_metadata_track_name",
            "master_metadata_album_album_name"
        ]
    ]
    .sort_values("ts", ascending=False)
    .head(20)
)

recent.columns = [
    "Date",
    "Track",
    "Album"
]

st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True
)