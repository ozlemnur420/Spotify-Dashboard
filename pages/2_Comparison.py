import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="User Comparison",
    page_icon="⚔️",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("data/spotify.csv")
    df["ts"] = pd.to_datetime(df["ts"])
    df["hours_played"] = df["ms_played"] / (1000 * 60 * 60)
    return df

spotify = load_data()

# =====================================================
# USER SELECTION
# =====================================================

users = sorted(spotify["user"].dropna().unique())

selected_user = st.selectbox(
    "👤 Select User",
    users
)

other_users = [u for u in users if u != selected_user]

if len(other_users) == 0:
    st.error("At least two users are required.")
    st.stop()

other_user = other_users[0]

df1 = spotify[spotify["user"] == selected_user]
df2 = spotify[spotify["user"] == other_user]

# =====================================================
# METRICS
# =====================================================

tracks1 = df1["master_metadata_track_name"].nunique()
tracks2 = df2["master_metadata_track_name"].nunique()

artists1 = df1["master_metadata_album_artist_name"].nunique()
artists2 = df2["master_metadata_album_artist_name"].nunique()

albums1 = df1["master_metadata_album_album_name"].nunique()
albums2 = df2["master_metadata_album_album_name"].nunique()

hours1 = round(df1["hours_played"].sum(), 1)
hours2 = round(df2["hours_played"].sum(), 1)

winner = selected_user if hours1 >= hours2 else other_user
difference = abs(hours1 - hours2)

# =====================================================
# HEADER
# =====================================================

st.title("⚔️ User Comparison")

st.markdown(
    f"""
# **{selected_user} 🆚 {other_user}**
"""
)

st.success(
    f"🏆 **{winner}** listened **{difference:,.1f}** more hours."
)

st.divider()

# =====================================================
# KPI CARDS
# =====================================================

left, right = st.columns(2)

with left:

    st.subheader(selected_user)

    a, b = st.columns(2)

    a.metric("🎵 Tracks", tracks1)
    b.metric("🎤 Artists", artists1)

    c, d = st.columns(2)

    c.metric("💿 Albums", albums1)
    d.metric("⏱ Hours", hours1)

with right:

    st.subheader(other_user)

    a, b = st.columns(2)

    a.metric("🎵 Tracks", tracks2)
    b.metric("🎤 Artists", artists2)

    c, d = st.columns(2)

    c.metric("💿 Albums", albums2)
    d.metric("⏱ Hours", hours2)

st.divider()

# =====================================================
# LISTENING HOURS
# =====================================================

st.subheader("⏱ Listening Hours")

hours_df = pd.DataFrame({
    "User": [selected_user, other_user],
    "Hours": [hours1, hours2]
})

fig = px.bar(
    hours_df,
    x="User",
    y="Hours",
    color="User",
    text_auto=".1f"
)

fig.update_layout(
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TRACKS
# =====================================================

st.subheader("🎵 Unique Tracks")

tracks_df = pd.DataFrame({
    "User": [selected_user, other_user],
    "Tracks": [tracks1, tracks2]
})

fig = px.bar(
    tracks_df,
    x="User",
    y="Tracks",
    color="User",
    text_auto=True
)

fig.update_layout(
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ARTISTS
# =====================================================

st.subheader("🎤 Unique Artists")

artists_df = pd.DataFrame({
    "User": [selected_user, other_user],
    "Artists": [artists1, artists2]
})

fig = px.bar(
    artists_df,
    x="User",
    y="Artists",
    color="User",
    text_auto=True
)

fig.update_layout(
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ALBUMS
# =====================================================

st.subheader("💿 Unique Albums")

albums_df = pd.DataFrame({
    "User": [selected_user, other_user],
    "Albums": [albums1, albums2]
})

fig = px.bar(
    albums_df,
    x="User",
    y="Albums",
    color="User",
    text_auto=True
)

fig.update_layout(
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =====================================================
# COMMON ARTISTS
# =====================================================

st.subheader("🤝 Common Artists")

artists_user1 = set(
    df1["master_metadata_album_artist_name"]
    .dropna()
    .unique()
)

artists_user2 = set(
    df2["master_metadata_album_artist_name"]
    .dropna()
    .unique()
)

common_artists = sorted(
    artists_user1.intersection(artists_user2)
)

if len(common_artists) == 0:

    st.info("No common artists found.")

else:

    common_df = pd.DataFrame({

        "Artist": common_artists

    })

    st.dataframe(

        common_df,

        use_container_width=True,

        hide_index=True

    )

st.divider()

# =====================================================
# COMMON TRACKS
# =====================================================

st.subheader("🎵 Common Tracks")

tracks_user1 = set(
    df1["master_metadata_track_name"]
    .dropna()
    .unique()
)

tracks_user2 = set(
    df2["master_metadata_track_name"]
    .dropna()
    .unique()
)

common_tracks = sorted(
    tracks_user1.intersection(tracks_user2)
)

if len(common_tracks) == 0:

    st.info("No common tracks found.")

else:

    track_df = pd.DataFrame({

        "Track": common_tracks

    })

    st.dataframe(

        track_df,

        use_container_width=True,

        hide_index=True

    )

st.divider()

# =====================================================
# MUSIC SIMILARITY
# =====================================================

st.subheader("❤️ Music Similarity")

union = len(
    artists_user1.union(artists_user2)
)

intersection = len(
    artists_user1.intersection(artists_user2)
)

if union == 0:

    similarity = 0

else:

    similarity = round(
        (intersection / union) * 100,
        1
    )

st.metric(
    "Similarity",
    f"{similarity}%"
)

st.progress(similarity / 100)

st.divider()

# =====================================================
# SUMMARY
# =====================================================

st.subheader("🏁 Summary")

if hours1 > hours2:

    st.success(
        f"🏆 {selected_user} listened more than {other_user}."
    )

elif hours2 > hours1:

    st.success(
        f"🏆 {other_user} listened more than {selected_user}."
    )

else:

    st.info(
        "Both users listened exactly the same amount."
    )