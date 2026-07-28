import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Track Analysis",
    page_icon="🎵",
    layout="wide"
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------

spotify = pd.read_csv("data/spotify.csv")

spotify["ts"] = pd.to_datetime(spotify["ts"])
spotify["hours_played"] = spotify["ms_played"] / (1000 * 60 * 60)
spotify["year"] = spotify["ts"].dt.year

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🎵 Track Analysis")
st.caption("Detailed statistics for each track")

# --------------------------------------------------
# Select Track
# --------------------------------------------------

tracks = sorted(
    spotify["master_metadata_track_name"]
    .dropna()
    .unique()
)

track = st.selectbox(
    "Choose Track",
    tracks
)

df = spotify[
    spotify["master_metadata_track_name"] == track
]

# --------------------------------------------------
# KPI
# --------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Play Count",
    len(df)
)

c2.metric(
    "Listening Hours",
    round(df["hours_played"].sum(), 2)
)

c3.metric(
    "Artist",
    df["master_metadata_album_artist_name"].iloc[0]
)

c4.metric(
    "Album",
    df["master_metadata_album_album_name"].iloc[0]
)

st.divider()

# --------------------------------------------------
# Listening By Year
# --------------------------------------------------

yearly = (
    df
    .groupby("year")
    .agg(Hours=("hours_played", "sum"))
    .reset_index()
)

fig = px.line(
    yearly,
    x="year",
    y="Hours",
    markers=True,
    title="Listening Hours by Year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# Listening History
# --------------------------------------------------

st.subheader("Recent Plays")

history = (
    df[
        [
            "ts",
            "user",
            "platform",
            "hours_played"
        ]
    ]
    .sort_values("ts", ascending=False)
)

history.columns = [
    "Date",
    "User",
    "Platform",
    "Hours"
]

st.dataframe(
    history,
    use_container_width=True,
    hide_index=True
)