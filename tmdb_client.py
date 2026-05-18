"""
tmdb_client.py
--------------
All TMDB API communication lives here.
Uses urllib (Python built-in) — no requests library needed.
Handles retries automatically so one network hiccup doesn't kill the app.
"""

import os
import json
import ssl
import time
import urllib.request
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Unverified SSL context fixes the WinError 10054 issue on Windows
_ssl = ssl._create_unverified_context()

# In-memory caches to eliminate sequential network bottlenecks on Streamlit Cloud
_movie_cache = {}
_credits_cache = {}
_keywords_cache = {}
_person_cache = {}


# ── Core fetch ────────────────────────────────────────────────────────────────

def _fetch(endpoint: str, params: dict = None, retries: int = 4) -> dict:
    """
    GET one TMDB endpoint. Retries up to `retries` times on failure.
    Returns empty dict if all attempts fail — app keeps running.
    """
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    url = f"{BASE_URL}{endpoint}?{urlencode(params)}"

    # Add a proper User-Agent header to stop Cloudflare/TMDB blocking requests from Cloud datacenters
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=_ssl, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception:
            if attempt < retries - 1:
                time.sleep(1.5)
    return {}


def _paginate(endpoint: str, params: dict = None, pages: int = 2) -> list:
    """Fetch multiple pages and flatten into one list."""
    if params is None:
        params = {}
    results = []
    for page in range(1, pages + 1):
        data = _fetch(endpoint, {**params, "page": page})
        results.extend(data.get("results", []))
    return results


# ── Search ────────────────────────────────────────────────────────────────────

def search_movie(query: str) -> list:
    """Search TMDB by title. Returns list of matching movies."""
    data = _fetch("/search/movie", {"query": query, "include_adult": "false"})
    return data.get("results", [])


# ── Single movie data ─────────────────────────────────────────────────────────

def get_movie(movie_id: int) -> dict:
    """Full detail for one movie (genres, runtime, tagline, etc.) with caching."""
    if movie_id in _movie_cache:
        return _movie_cache[movie_id]
    data = _fetch(f"/movie/{movie_id}")
    if data and data.get("title"):
        _movie_cache[movie_id] = data
    return data


def get_credits(movie_id: int) -> dict:
    """Cast and crew for one movie with caching."""
    if movie_id in _credits_cache:
        return _credits_cache[movie_id]
    data = _fetch(f"/movie/{movie_id}/credits")
    if data:
        _credits_cache[movie_id] = data
    return data


def get_keywords(movie_id: int) -> list:
    """Editorial keyword tags (e.g. 'psychological-thriller') with caching."""
    if movie_id in _keywords_cache:
        return _keywords_cache[movie_id]
    data = _fetch(f"/movie/{movie_id}/keywords")
    kw = data.get("keywords", [])
    if data:
        _keywords_cache[movie_id] = kw
    return kw


# ── Recommendation sources ────────────────────────────────────────────────────

def get_tmdb_recs(movie_id: int, pages: int = 2) -> list:
    """TMDB's own recommendation engine."""
    return _paginate(f"/movie/{movie_id}/recommendations", pages=pages)


def get_similar(movie_id: int, pages: int = 2) -> list:
    """TMDB similar movies (metadata-based)."""
    return _paginate(f"/movie/{movie_id}/similar", pages=pages)


def get_person_credits(person_id: int) -> dict:
    """All movies a person (actor/director) has worked on with caching."""
    if person_id in _person_cache:
        return _person_cache[person_id]
    data = _fetch(f"/person/{person_id}/movie_credits")
    res = data if data else {"cast": [], "crew": []}
    if data:
        _person_cache[person_id] = res
    return res


def discover(params: dict, pages: int = 2) -> list:
    """Generic discover endpoint — used for acclaimed and genre wheel."""
    return _paginate("/discover/movie", params, pages=pages)


# ── Genre list ────────────────────────────────────────────────────────────────

def get_genre_list() -> list:
    """All TMDB genre IDs and names."""
    data = _fetch("/genre/movie/list")
    return data.get("genres", [])


# ── Poster URLs ───────────────────────────────────────────────────────────────

def poster(path: str, size: str = "w342") -> str:
    """Build a full TMDB image URL from a poster_path."""
    return f"https://image.tmdb.org/t/p/{size}{path}" if path else ""