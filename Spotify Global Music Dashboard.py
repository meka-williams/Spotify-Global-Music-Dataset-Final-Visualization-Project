"""
The dashboard was built using Streamlit for the dashboard framework,
Pandas for the data manipulation, and Plotly Express for interactive
visualizations. The page layout was set to wide format to prevent clutter
and improve readability.

The dataset is loaded using a robust file path to improve performance and
prevent "file not found" error. Basic data cleaning is performed during loading,
filling in missing artist genres values with "Unknown". 

To support genre-level analysis, the artist_genres column is split and exploded so
that each genre can be treated as its own row. This allows accurate filtering and 
aggregation when users interact with the genre selector. Then, I set a title and divider
to visually separate the header from the interactive content.

The two visualization I created:
- A scatter plot showing the relationship between artist popularity and average
track popularity.
- A bar chart summarizing average track popularity by album type

Both visuals are dynamically linked to the filtered dataset, ensuring consistency across
the dashboard.

--- How the Interactivity Works ---
Interactivity is driven primarily through a genre select box at the top of the dashboard. 
Users can choose from a specific genre or select "All" to view the full dataset. When the genre
is selected, the dataset filtered in real time, and all the visualizations update automatically.

The dashboard also includes:
- Hover tooltip in the scatter plot that display the artist name and related metrics.
- Responsive charts that adjust to the screen width using Streamlit's container layout

--- What the Dashboard Helps the Viewer Understand ---
This dashboard helps viewers understand how artist popularity relates to track popularity, and how this
relationship varies across genres. The scatter plot highlights whether more popular artists consistently
produce popular tracks and reveal outliers. 

The bar chart provides insights into how album types (i.e. singles, albums, or compilations) differ in terms
of average track popularity. Together, these visuals helps users explore questions about music release strategies,
artist performance, and genre-specific trends within Spotify's data.

"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page Layout set to wide to avoid clutering
st.set_page_config(page_title="Spotify Dataset Dashboard", layout="wide")

# Added a robust path to avoid "file not found" error
DATA_PATH = Path(__file__).parent / "spotify_data clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Clean null genres with "Unknown"
    df["artist_genres"] = df["artist_genres"].fillna("Unknown").str.lower()

    return df

df = load_data()

# Expand genres for easy filtering
genre_df = (
    df.assign(artist_genres=df["artist_genres"].str.split(", "))
      .explode("artist_genres")
)

genre_options = sorted(genre_df["artist_genres"].unique())

# Dashboard Title
st.title("Spotify Track Popularity Dashboard")
st.divider()

# Input - Selected a genre using select box
selected_genre = st.selectbox(
    "Filter by Artist Genre",
    ["All"] + genre_options
)

if selected_genre != "All":
    df_filtered = genre_df[genre_df["artist_genres"] == selected_genre]
else:
    df_filtered = df.copy()

# Visualization 1: Scatter Plot
# Average Track Popularity vs. Average Artist Popularity 
artist_summary = (
    df_filtered
    .groupby("artist_name", as_index=False)
    .agg(
        avg_track_popularity=("track_popularity", "mean"),
        artist_popularity=("artist_popularity", "mean"),
        track_count=("track_id", "count")
    )
)

fig_scatter = px.scatter(
    artist_summary,
    x="artist_popularity",
    y="avg_track_popularity",
    size="track_count",
    hover_name="artist_name",
    hover_data = {
        "artist_popularity" : ":.1f",
        "avg_track_popularity" : ":.1f",
        "track_count" : ":d"
    },
    title="Artist Popularity vs Average Track Popularity",
    labels={
        "artist_popularity": "Artist Popularity ",
        "avg_track_popularity": "Average Track Popularity ",
        "track_count": "Number of Tracks "
    },
    color_discrete_sequence=["#1DB954"]
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Visualization 2: Bar Chart
# Average Track Popularity by Album Type
album_summary = (
    df_filtered
    .groupby("album_type", as_index=False)
    .agg(avg_track_popularity=("track_popularity", "mean"))
)

fig_bar = px.bar(
    album_summary,
    x="album_type",
    y="avg_track_popularity",
    hover_data = {
        "avg_track_popularity" : ":.1f"
    },
    title="Average Track Popularity by Album Type",
    labels={
        "album_type": "Album Type ",
        "avg_track_popularity": "Average Track Popularity "
    },
    color_discrete_sequence=["#1DB954"]
)

st.plotly_chart(fig_bar, use_container_width=True)