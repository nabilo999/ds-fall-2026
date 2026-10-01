# MovieLens Dashboard Build Log

This is a brief record of the actual process used to build the dashboard. It is
intentionally a working log rather than a polished report.

## 1. Prompt / assignment direction

The assignment asked for a public Streamlit dashboard using `movie_ratings.csv`
with four charts: genre distribution among rated movies, average rating by genre,
mean rating by movie release year, and the top five movies at 50-rating and
150-rating minimums. It also required one or two working input widgets.

## 2. Initial implementation approach

The first approach was a four-section Streamlit page with two sidebar controls:
a genre multi-select for the genre charts and a release-year range slider for the
time trend. The top-movie comparison stays fixed at 50 and 150 because those are
the exact assignment thresholds. Plotly horizontal bars were chosen for genre
and movie labels, while a marked line chart was chosen for the release-year
trend.

## 3. Decisions made during implementation

- Genres are pipe-separated and movies can appear in more than one genre. For
  the distribution chart, the app de-duplicates movies before splitting genres,
  so a rated movie is counted once in each of its genres rather than once per
  rating event.
- For average genre ratings, the app instead splits every rating record into its
  listed genres and averages those ratings by genre.
- The data contains release year `0`, which is an unknown year. It is excluded
  from the release-year chart only; it remains available for all unrelated
  calculations.
- The time chart groups by movie release year, not the `timestamp` or
  `rating_year` column, because the question asks about release years.
- The movie ranking calculates rating count and mean rating per movie, applies
  each minimum threshold before ranking, and shows counts in the chart hover and
  companion table.

## 4. What changed and why

The dashboard adds a short methodology section and explicit filter-status text.
Those additions make the multi-genre handling, the unknown-year exclusion, and
the difference between an active filtered view and the assignment's full-data
answer visible to a reviewer.
