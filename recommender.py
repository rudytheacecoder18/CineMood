"""
recommender.py
--------------
CineMood's four recommendation engines.

1. mood()      — same emotional tone & atmosphere
2. director()  — other films by the same director
3. actors()    — films sharing top cast members
4. acclaimed() — critically rated classics at the same tier

For curated films (~45 iconic titles), the mood engine uses hand-picked
mood profiles from moods.py for precise emotional matching.
For all other films, it falls back to TMDB recs + similar movies + genre
scoring, and uses the film's own TMDB keywords as mood tags.

Designed to be fast on Streamlit Cloud: minimal API calls per section.
"""

from tmdb_client import (
    get_movie,
    get_credits,
    get_keywords,
    get_tmdb_recs,
    get_similar,
    get_person_credits,
    discover,
)
from moods import get_mood
from collections import defaultdict


# ── Build the input movie profile ─────────────────────────────────────────────

def build_profile(movie_id: int) -> dict | None:
    details = get_movie(movie_id)
    if not details or not details.get("title"):
        return None

    credits_data = get_credits(movie_id)
    keywords_raw = get_keywords(movie_id)

    director_name = None
    director_id   = None
    for person in credits_data.get("crew", []):
        if person.get("job") == "Director":
            director_name = person["name"]
            director_id   = person["id"]
            break

    cast     = []
    cast_ids = []
    for actor in credits_data.get("cast", [])[:6]:
        cast.append({
            "name":      actor["name"],
            "id":        actor["id"],
            "character": actor.get("character", ""),
        })
        cast_ids.append(actor["id"])

    genres        = details.get("genres", [])
    genre_ids     = [g["id"]   for g in genres]
    genre_names   = [g["name"] for g in genres]
    keyword_names = [k["name"] for k in keywords_raw]

    return {
        "id":           movie_id,
        "title":        details.get("title", ""),
        "year":         (details.get("release_date") or "")[:4],
        "overview":     details.get("overview", ""),
        "tagline":      details.get("tagline", ""),
        "vote_average": round(details.get("vote_average", 0), 1),
        "vote_count":   details.get("vote_count", 0),
        "runtime":      details.get("runtime"),
        "poster_path":  details.get("poster_path"),
        "genres":       genre_names,
        "genre_ids":    genre_ids,
        "director":     director_name,
        "director_id":  director_id,
        "cast":         cast,
        "cast_ids":     cast_ids,
        "keywords":     keyword_names,
        "mood_data":    get_mood(details.get("title", "")),
    }


# ── Shared helpers ────────────────────────────────────────────────────────────

def _dedupe(movies: list, exclude_ids: set, min_votes: int = 200) -> list:
    seen   = set(exclude_ids)
    result = []
    for m in movies:
        mid = m.get("id")
        if not mid or mid in seen:
            continue
        if m.get("vote_count", 0) < min_votes:
            continue
        seen.add(mid)
        result.append(m)
    return result


def _format(m: dict, why: list = None) -> dict:
    return {
        "id":           m.get("id"),
        "title":        m.get("title", ""),
        "year":         (m.get("release_date") or "")[:4],
        "vote_average": round(m.get("vote_average", 0), 1),
        "vote_count":   m.get("vote_count", 0),
        "poster_path":  m.get("poster_path"),
        "overview":     m.get("overview", ""),
        "genre_ids":    m.get("genre_ids", []),
        "why":          why or [],
    }


def _keywords_to_themes(keywords: list) -> list:
    """
    Convert raw TMDB keyword strings into clean, Title Case theme tags.
    Used as a fallback for films not in the curated CURATED list.
    e.g. 'psychological-thriller' → 'Psychological Thriller'
    """
    seen   = set()
    result = []
    for kw in keywords[:8]:
        tag = kw.replace("-", " ").replace("_", " ").title()
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
        if len(result) == 5:
            break
    return result


# ── Engine 1 — Mood / Vibe ────────────────────────────────────────────────────

def mood(profile: dict, limit: int = 16) -> dict:
    """
    Mood recommendations using curated intelligence + TMDB data.

    For curated films: uses hand-picked mood IDs as the primary signal,
    boosted in the scoring. Themes come from the curated profile.

    For uncurated films: falls back entirely to TMDB recs + similar movies
    + genre scoring. Themes are derived from the film's own TMDB keywords.

    API calls per section:
      - up to 6 individual movie lookups for curated IDs
      - 1 page of TMDB recs + 1 page of similar  (2 calls)
    Total: under 10 calls.
    """
    mid         = profile["id"]
    mood_data   = profile.get("mood_data", {})
    themes      = mood_data.get("themes", [])
    curated_ids = mood_data.get("mood_ids", [])

    # For uncurated films, derive themes from TMDB keywords
    if not themes:
        themes = _keywords_to_themes(profile.get("keywords", []))

    raw = []

    # Fetch top 6 curated films individually (direct ID lookup — fast)
    fetched = 0
    for cid in curated_ids:
        if cid == mid:
            continue
        if fetched >= 6:
            break
        movie_data = get_movie(cid)
        if movie_data and movie_data.get("title"):
            raw.append(movie_data)
            fetched += 1

    # 1 page of TMDB recs + 1 page of similar (2 API calls)
    raw.extend(get_tmdb_recs(mid, pages=1))
    raw.extend(get_similar(mid, pages=1))

    candidates = _dedupe(raw, {mid}, min_votes=300)

    input_gids  = set(profile["genre_ids"])
    curated_set = set(curated_ids)

    scored = []
    for m in candidates:
        cand_gids     = set(m.get("genre_ids", []))
        genre_score   = len(input_gids & cand_gids) / max(len(input_gids), 1)
        vote_score    = min(m.get("vote_average", 0) / 10, 1.0)
        pop_score     = min(m.get("vote_count", 0) / 50_000, 1.0)
        # Curated films get a strong boost so they surface first
        curated_bonus = 0.4 if m.get("id") in curated_set else 0.0
        final = (0.35 * genre_score) + (0.25 * vote_score) + (0.15 * pop_score) + curated_bonus
        scored.append({**_format(m, why=themes[:3]), "score": final})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"films": scored[:limit], "themes": themes}


# ── Engine 2 — Director ───────────────────────────────────────────────────────

def director(profile: dict, limit: int = 12) -> list:
    """Other films by the same director. Single API call."""
    if not profile.get("director_id"):
        return []

    creds    = get_person_credits(profile["director_id"])
    directed = [m for m in creds.get("crew", []) if m.get("job") == "Director"]
    directed.sort(key=lambda x: x.get("vote_average", 0), reverse=True)

    candidates = _dedupe(directed, {profile["id"]}, min_votes=100)
    return [_format(m) for m in candidates[:limit]]


# ── Engine 3 — Actors ─────────────────────────────────────────────────────────

def actors(profile: dict, limit: int = 15) -> list:
    """
    Films sharing the same cast.
    Checks top 3 billed actors (3 API calls total) to stay fast on Cloud.
    """
    cast_ids = profile.get("cast_ids", [])
    if not cast_ids:
        return []

    shared_count = defaultdict(int)
    movie_store  = {}

    for actor_id in cast_ids[:3]:
        creds = get_person_credits(actor_id)
        for m in creds.get("cast", []):
            mid = m.get("id")
            if not mid or mid == profile["id"]:
                continue
            if m.get("vote_count", 0) < 200:
                continue
            shared_count[mid] += 1
            movie_store[mid] = m

    all_movies = list(movie_store.values())
    all_movies.sort(
        key=lambda m: (shared_count[m["id"]], m.get("vote_average", 0)),
        reverse=True
    )

    candidates = _dedupe(all_movies, {profile["id"]}, min_votes=200)
    result = []
    for m in candidates[:limit]:
        fmt = _format(m)
        fmt["shared_actors"] = shared_count[m["id"]]
        result.append(fmt)
    return result


# ── Engine 4 — Critically Acclaimed ──────────────────────────────────────────

def acclaimed(profile: dict, limit: int = 15) -> list:
    """Classics at the same quality tier. 2 pages of discover."""
    avg = profile["vote_average"]

    if avg >= 8.5:   min_rating = 8.5
    elif avg >= 8.0: min_rating = 8.0
    elif avg >= 7.5: min_rating = 7.5
    else:            min_rating = 7.0

    raw = discover({
        "sort_by":          "vote_average.desc",
        "vote_count.gte":   5000,
        "vote_average.gte": min_rating,
    }, pages=2)

    candidates = _dedupe(raw, {profile["id"]}, min_votes=5000)
    return [_format(m) for m in candidates[:limit]]


# ── Genre Wheel ───────────────────────────────────────────────────────────────

def genre_wheel(genre_id: int, limit: int = 20) -> list:
    raw = discover({
        "with_genres":    genre_id,
        "sort_by":        "vote_average.desc",
        "vote_count.gte": 3000,
    }, pages=2)

    candidates = _dedupe(raw, set(), min_votes=3000)
    return [_format(m) for m in candidates[:limit]]


# ── Main entry point ──────────────────────────────────────────────────────────

def get_all(movie_id: int) -> dict | None:
    profile = build_profile(movie_id)
    if not profile:
        return None

    return {
        "movie":     profile,
        "mood":      mood(profile),
        "director":  director(profile),
        "actors":    actors(profile),
        "acclaimed": acclaimed(profile),
    }
