import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="User Analysis",
    page_icon="👤",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------

spotify = pd.read_csv("data/spotify.csv")

spotify["ts"] = pd.to_datetime(spotify["ts"])
spotify["year"] = spotify["ts"].dt.year
spotify["month"] = spotify["ts"].dt.month_name()
spotify["hour"] = spotify["ts"].dt.hour
spotify["weekday"] = spotify["ts"].dt.day_name()

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("👤 User")

user = st.sidebar.selectbox(
    "Choose User",
    sorted(spotify["user"].dropna().unique())
)

df = spotify[spotify["user"] == user]

# -----------------------------
# Title
# -----------------------------

st.title(f"👤 {user}")

st.caption("Detailed listening statistics")

st.divider()

# -----------------------------
# KPI
# -----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Tracks",
    df["master_metadata_track_name"].nunique()
)

c2.metric(
    "Artists",
    df["master_metadata_album_artist_name"].nunique()
)

c3.metric(
    "Albums",
    df["master_metadata_album_album_name"].nunique()
)

c4.metric(
    "Hours",
    round(df["ms_played"].sum()/1000/60/60)
)

st.divider()

# -----------------------------
# Top Artists
# -----------------------------

left, right = st.columns(2)

artists = (
    df
    .dropna(subset=["master_metadata_album_artist_name"])
    .groupby("master_metadata_album_artist_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig1 = px.bar(
    artists,
    x="Play Count",
    y="master_metadata_album_artist_name",
    orientation="h",
    title="Top Artists"
)

fig1.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

left.plotly_chart(
    fig1,
    use_container_width=True
)

# -----------------------------
# Top Tracks
# -----------------------------

tracks = (
    df
    .dropna(subset=["master_metadata_track_name"])
    .groupby("master_metadata_track_name")
    .size()
    .reset_index(name="Play Count")
    .sort_values("Play Count", ascending=False)
    .head(10)
)

fig2 = px.bar(
    tracks,
    x="Play Count",
    y="master_metadata_track_name",
    orientation="h",
    title="Top Tracks"
)

fig2.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

right.plotly_chart(
    fig2,
    use_container_width=True
)

st.divider()

# -----------------------------
# Monthly Trend
# -----------------------------

monthly = (
    df
    .groupby(df["ts"].dt.to_period("M").astype(str))
    .agg(
        Hours=("ms_played", lambda x: x.sum()/1000/60/60)
    )
    .reset_index()
)

fig3 = px.line(
    monthly,
    x="ts",
    y="Hours",
    markers=True,
    title="Monthly Listening Hours"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)