"""Interactive MovieLens dashboard for the course dashboard assignment."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="MovieLens Dashboard",
    page_icon="🎬",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "movie_ratings.csv"
REQUIRED_COLUMNS = {"user_id", "movie_id", "rating", "title", "year", "genres"}
COLOR = "#5B5BD6"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load and lightly normalize the supplied MovieLens ratings data."""
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"The data file is missing required columns: {missing_columns}")

    # Use course-friendly names inside the app while leaving the CSV unchanged.
    data = data.rename(columns={"user_id": "userId", "movie_id": "movieId"}).copy()
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["genres"] = data["genres"].fillna("unknown").astype(str)
    data["title"] = data["title"].fillna("Untitled").astype(str)
    return data.dropna(subset=["movieId", "rating"])


def explode_genres(data: pd.DataFrame) -> pd.DataFrame:
    """Return one row per record-genre combination."""
    return data.assign(genre=data["genres"].str.split("|")).explode("genre")


def show_empty_chart(message: str) -> None:
    st.info(message)


try:
    ratings = load_data(str(DATA_PATH))
except FileNotFoundError:
    st.error("Data file not found. Place movie_ratings.csv in the data folder and reload.")
    st.stop()
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Could not load the MovieLens data: {error}")
    st.stop()

genre_data = explode_genres(ratings)
all_genres = sorted(genre_data["genre"].dropna().unique())
known_years = ratings.loc[ratings["year"] > 0, "year"]
minimum_year = int(known_years.min())
maximum_year = int(known_years.max())

st.title("🎬 MovieLens Ratings Dashboard")
st.caption("Exploring 100,000 MovieLens ratings across movies, genres, and release years.")

with st.sidebar:
    st.header("Explore the data")
    selected_genres = st.multiselect(
        "Genres to show",
        options=all_genres,
        default=all_genres,
        help="This changes the genre charts only. Leave every genre selected for the full-data answer.",
    )
    selected_years = st.slider(
        "Release-year range",
        min_value=minimum_year,
        max_value=maximum_year,
        value=(minimum_year, maximum_year),
        help="This changes the release-year trend only. Year 0 is omitted because it is unknown.",
    )

filters_active = (
    set(selected_genres) != set(all_genres)
    or selected_years != (minimum_year, maximum_year)
)
if filters_active:
    st.info("Filters are active. Reset them to view the full-dataset answers requested in the assignment.")
else:
    st.success("Showing full-dataset answers. Use the sidebar to explore a subset.")

with st.expander("Methodology and interpretation choices", expanded=False):
    st.markdown(
        """
        - **Genre breakdown:** Movies can have multiple genres. I first keep each rated movie once,
          split its pipe-separated genres, and count that movie once in each listed genre.
        - **Genre satisfaction:** I split every rating into its movie's listed genres, then calculate
          the mean of rating records for each genre.
        - **Ratings over time:** The trend groups ratings by the movie's **release year**, not by the
          year a user left a rating. Unknown release year `0` is excluded from this chart only.
        - **Best movies:** A movie must meet the stated minimum number of ratings before its average
          rating can qualify it for the top five.
        """
    )

st.header("1. Genre breakdown")
st.write("How are genres distributed among movies that received at least one rating?")
if selected_genres:
    rated_movies = ratings.drop_duplicates(subset="movieId")
    genre_counts = (
        explode_genres(rated_movies)
        .query("genre in @selected_genres")
        .groupby("genre", as_index=False)
        .size()
        .rename(columns={"size": "Rated movies"})
        .sort_values("Rated movies", ascending=True)
    )
    chart = px.bar(
        genre_counts,
        x="Rated movies",
        y="genre",
        orientation="h",
        color_discrete_sequence=[COLOR],
        labels={"genre": "Genre"},
        text="Rated movies",
    )
    chart.update_layout(showlegend=False, height=520, margin=dict(l=10, r=20, t=30, b=10))
    st.plotly_chart(chart, use_container_width=True)
else:
    show_empty_chart("Select at least one genre to display the genre breakdown.")

st.header("2. Genre satisfaction")
st.write("Which genres have the highest and lowest average rating?")
if selected_genres:
    genre_ratings = (
        genre_data.query("genre in @selected_genres")
        .groupby("genre", as_index=False)["rating"]
        .mean()
        .rename(columns={"rating": "Average rating"})
        .sort_values("Average rating", ascending=True)
    )
    chart = px.bar(
        genre_ratings,
        x="Average rating",
        y="genre",
        orientation="h",
        color="Average rating",
        color_continuous_scale="Blues",
        range_x=[0, 5],
        text=genre_ratings["Average rating"].map("{:.2f}".format),
        labels={"genre": "Genre"},
    )
    chart.update_layout(height=520, coloraxis_showscale=False, margin=dict(l=10, r=20, t=30, b=10))
    st.plotly_chart(chart, use_container_width=True)
    low, high = genre_ratings.iloc[0], genre_ratings.iloc[-1]
    st.caption(
        f"Lowest: {low['genre']} ({low['Average rating']:.2f}) · "
        f"Highest: {high['genre']} ({high['Average rating']:.2f})"
    )
else:
    show_empty_chart("Select at least one genre to display average ratings.")

st.header("3. Ratings over movie release years")
st.write("How has the mean rating changed across movie release years?")
year_ratings = (
    ratings.loc[ratings["year"].between(selected_years[0], selected_years[1])]
    .groupby("year", as_index=False)["rating"]
    .mean()
    .rename(columns={"rating": "Mean rating", "year": "Release year"})
    .sort_values("Release year")
)
if year_ratings.empty:
    show_empty_chart("No ratings are available in this release-year range.")
else:
    chart = px.line(
        year_ratings,
        x="Release year",
        y="Mean rating",
        markers=True,
        range_y=[0, 5],
        color_discrete_sequence=[COLOR],
        hover_data={"Mean rating": ":.2f"},
    )
    chart.update_layout(height=480, margin=dict(l=10, r=20, t=30, b=10))
    st.plotly_chart(chart, use_container_width=True)

st.header("4. Best movies, with a floor")
st.write("Top five average-rated movies after requiring at least 50 ratings, then at least 150 ratings.")
movie_summary = (
    ratings.groupby(["movieId", "title"], as_index=False)
    .agg(average_rating=("rating", "mean"), rating_count=("rating", "size"))
)


def top_movies(minimum_ratings: int) -> pd.DataFrame:
    return (
        movie_summary.loc[movie_summary["rating_count"] >= minimum_ratings]
        .sort_values(["average_rating", "rating_count", "title"], ascending=[False, False, True])
        .head(5)
        .sort_values("average_rating", ascending=True)
    )


left, right = st.columns(2)
for column, threshold in ((left, 50), (right, 150)):
    best = top_movies(threshold)
    with column:
        st.subheader(f"At least {threshold} ratings")
        if best.empty:
            show_empty_chart(f"No movies have at least {threshold} ratings.")
        else:
            chart = px.bar(
                best,
                x="average_rating",
                y="title",
                orientation="h",
                color_discrete_sequence=[COLOR],
                range_x=[0, 5],
                labels={"average_rating": "Average rating", "title": "Movie"},
                hover_data={"rating_count": True, "average_rating": ":.2f"},
                text=best["average_rating"].map("{:.2f}".format),
            )
            chart.update_layout(showlegend=False, height=360, margin=dict(l=10, r=20, t=30, b=10))
            st.plotly_chart(chart, use_container_width=True)
            display = best.sort_values("average_rating", ascending=False).copy()
            display["average_rating"] = display["average_rating"].map("{:.2f}".format)
            st.dataframe(
                display[["title", "average_rating", "rating_count"]].rename(
                    columns={
                        "title": "Movie",
                        "average_rating": "Average rating",
                        "rating_count": "Ratings",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )

st.caption("Built with the GroupLens MovieLens dataset for a course dashboard assignment.")
