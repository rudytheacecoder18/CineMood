# 🎬 CineMood

> **Find movies that match your mood. Because every movie has a mood.**

A mood-based cinematic discovery platform. Search any movie and CineMood builds
four recommendation categories based on emotional tone, director, cast, and
critical acclaim — all powered by the live TMDB API.

---

## Features

- **Similar Vibe & Mood** — films with the same emotional atmosphere and tone
- **Same Director** — the director's complete filmography, ranked by rating
- **Shared Cast** — movies starring the same actors, ranked by overlap count
- **Critically Acclaimed** — classics at the same quality tier (vote-count verified)
- **Genre Wheel** — spin to explore top films in any genre
- **Movie Cards** — poster, year, IMDb score, hover overview, and "Why Recommended" tags
- **Zero local dataset** — all data is live from TMDB, so nothing goes stale

---

## Tech Stack

| Layer       | Tool                          |
|-------------|-------------------------------|
| Language    | Python 3.10+                  |
| UI          | Streamlit                     |
| Data        | TMDB API (live)               |
| HTTP        | Requests                      |
| Caching     | Streamlit `@st.cache_data`    |
| Deployment  | Streamlit Cloud (free)        |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/CineMood.git
cd CineMood
pip install -r requirements.txt
```

### 2. Get your free TMDB API key

Go to: https://www.themoviedb.org/settings/api  
Register for a free account → request an API key (takes ~1 minute).

### 3. Set your API key

Create a `.env` file in the project root:

```
TMDB_API_KEY=your_api_key_here
```

### 4. Run

```bash
streamlit run app.py
```

---

## Deployment (Streamlit Cloud)

1. Push the repo to GitHub (do NOT commit your `.env` file — add it to `.gitignore`)
2. Go to https://share.streamlit.io → New app → select your repo
3. In **Advanced settings → Secrets**, add:
   ```toml
   TMDB_API_KEY = "your_api_key_here"
   ```
4. Deploy — your app goes live in ~2 minutes for free.

---

## Project Structure

```
CineMood/
├── app.py              # Streamlit UI — all pages, layout, CSS
├── recommender.py      # 4 recommendation engines + genre wheel
├── tmdb_client.py      # Clean TMDB API wrapper
├── requirements.txt
├── .env.example        # Copy to .env and add your key
├── .gitignore
└── README.md
```

---

## How It Works

### Mood Recommendations
Combines TMDB's own recommendation engine, similar-movie results, keyword-based
discovery, and genre-based discovery. Scores candidates by genre overlap (50%),
vote average (30%), and popularity breadth (20%). The "Why Recommended" tags
show shared genres — computed with no extra API calls.

### Director Recommendations
Fetches the director's full filmography via the TMDB person credits endpoint,
filters out low-vote films, and sorts by rating.

### Actor Recommendations
Checks the movie credits of the top 4 billed cast members, counts how many
share a film, and ranks by overlap count then by rating.

### Acclaimed Recommendations
Discovers films with a high vote average *and* a high vote count (≥5000).
The vote count filter is critical — it ensures only genuine classics appear,
not obscure films with inflated scores from a small audience.

---

## ML Concepts Used

- Content-based filtering
- Multi-source candidate generation
- Weighted scoring / ranking
- Cosine similarity (via TMDB's own engine)
- Genre overlap as a proxy for mood/tone similarity

---

## Add to `.gitignore`

```
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
```

---

*This product uses the TMDB API but is not endorsed or certified by TMDB.*