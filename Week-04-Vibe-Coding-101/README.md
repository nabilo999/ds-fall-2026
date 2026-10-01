# MovieLens Streamlit Dashboard

Interactive dashboard for the MovieLens course assignment. It answers the four
required questions about genre distribution, genre satisfaction, ratings across
movie release years, and best-rated movies at two rating-count floors.

## Run locally

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If your virtual environment uses a `bin` folder instead of `Scripts`, activate
it with the matching path. Streamlit will print a local URL, normally
`http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Sign in to GitHub and create a **new public repository**. A name such as
   `movielens-dashboard` is fine. Do not add a README or `.gitignore` through
   GitHub, because this project already has both.
2. In PowerShell, open this project folder and run:

   ```powershell
   git init
   git add app.py requirements.txt .gitignore BUILD_LOG.md README.md data/movie_ratings.csv
   git commit -m "Build MovieLens dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with the values from GitHub.
   GitHub may open a browser or request a personal access token to authenticate.
3. Go to [Streamlit Community Cloud](https://share.streamlit.io/), sign in with
   GitHub, then choose **Create app**.
4. Choose your new public repository and its `main` branch. Set the main file
   path to `app.py`, then select **Deploy**.
5. Wait for the app to finish building. Open its generated `streamlit.app` URL
   in an Incognito/InPrivate browser window. Confirm all four charts load and
   the sidebar widgets work before submitting that public URL.

## Project files

- `app.py` — Streamlit dashboard.
- `data/movie_ratings.csv` — course data packaged with the app for deployment.
- `requirements.txt` — deployment dependencies.
- `BUILD_LOG.md` — retained process notes for the following week's work.
