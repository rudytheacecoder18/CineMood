"""
recommender.py
--------------
CineMood's four recommendation engines.

1. mood()     — same emotional tone & atmosphere
2. director() — other films by the same director
3. actors()   — films sharing top cast members
4. acclaimed() — critically rated classics at the same tier

All use tmdb_client (urllib-based) and moods (curated intelligence).
"""

from tmdb_client import (
    get_movie,
    get_credits,
    get_keywords,
    get_tmdb_recs,
    get_similar,
    get_person_credits,
    discover,
    poster,
)
from moods import get_mood
from collections import defaultdict


# ── Build the input movie profile ─────────────────────────────────────────────

def build_profile(movie_id: int) -> dict | None:
    """
    Fetch everything we need about the selected movie.
    Returns a clean profile dict, or None if the movie_id is invalid.
    """
    details = get_movie(movie_id)
    if not details or not details.get("title"):
        return None

    credits_data = get_credits(movie_id)
    keywords_raw = get_keywords(movie_id)

    # Director
    director_name = None
    director_id   = None
    for person in credits_data.get("crew", []):
        if person.get("job") == "Director":
            director_name = person["name"]
            director_id   = person["id"]
            break

    # Top 8 cast
    cast     = []
    cast_ids = []
    for actor in credits_data.get("cast", [])[:8]:
        cast.append({
            "name":      actor["name"],
            "id":        actor["id"],
            "character": actor.get("character", ""),
        })
        cast_ids.append(actor["id"])

    # Genres
    genres      = details.get("genres", [])
    genre_ids   = [g["id"]   for g in genres]
    genre_names = [g["name"] for g in genres]

    # Keywords
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
        # Curated mood data from moods.py
        "mood_data":    get_mood(details.get("title", "")),
    }


# ── Shared helpers ────────────────────────────────────────────────────────────

def _dedupe(movies: list, exclude_ids: set, min_votes: int = 200) -> list:
    """Remove duplicates, excluded IDs, and low-vote films."""
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
    """Trim a raw TMDB movie dict down to what the UI needs."""
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


# ── Engine 1 — Mood / Vibe ────────────────────────────────────────────────────

def mood(profile: dict, limit: int = 16) -> dict:
    """
    Films with the same emotional tone and atmosphere.

    Sources (in priority order):
      1. Curated hand-picked films from moods.py   ← the special sauce
      2. TMDB's own recommendation engine
      3. TMDB similar movies

    Returns:
      {"films": [...], "themes": [...]}
    """
    mid         = profile["id"]
    mood_data   = profile.get("mood_data", {})
    themes      = mood_data.get("themes", [])
    curated_ids = mood_data.get("mood_ids", [])

    raw = []

    # Fetch curated films by ID (direct — no search calls)
    for cid in curated_ids:
        if cid == mid:
            continue
        movie_data = get_movie(cid)
        if movie_data and movie_data.get("title"):
            raw.append(movie_data)

    # TMDB's own recs and similar
    raw.extend(get_tmdb_recs(mid, pages=2))
    raw.extend(get_similar(mid, pages=2))

    candidates = _dedupe(raw, {mid}, min_votes=300)

    # Score: vote quality weighted + popularity breadth
    input_gids = set(profile["genre_ids"])
    scored = []
    for m in candidates:
        cand_gids   = set(m.get("genre_ids", []))
        genre_score = len(input_gids & cand_gids) / max(len(input_gids), 1)
        vote_score  = min(m.get("vote_average", 0) / 10, 1.0)
        pop_score   = min(m.get("vote_count", 0) / 50_000, 1.0)
        final       = (0.5 * genre_score) + (0.3 * vote_score) + (0.2 * pop_score)
        scored.append({**_format(m, why=themes[:3]), "score": final})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"films": scored[:limit], "themes": themes}


# ── Engine 2 — Director ───────────────────────────────────────────────────────

def director(profile: dict, limit: int = 12) -> list:
    """Other films directed by the same director, sorted by rating."""
    if not profile["director_id"]:
        return []

    creds    = get_person_credits(profile["director_id"])
    directed = [m for m in creds.get("crew", []) if m.get("job") == "Director"]
    directed.sort(key=lambda x: x.get("vote_average", 0), reverse=True)

    candidates = _dedupe(directed, {profile["id"]}, min_votes=200)
    return [_format(m) for m in candidates[:limit]]


# ── Engine 3 — Actors ─────────────────────────────────────────────────────────

def actors(profile: dict, limit: int = 15) -> list:
    """
    Films sharing the same cast.
    Films featuring more of the input movie's actors rank higher.
    """
    if not profile["cast_ids"]:
        return []

    shared_count = defaultdict(int)
    movie_store  = {}

    # Top 4 billed cast members
    for actor_id in profile["cast_ids"][:4]:
        creds = get_person_credits(actor_id)
        for m in creds.get("cast", []):
            mid = m.get("id")
            if not mid or mid == profile["id"]:
                continue
            if m.get("vote_count", 0) < 300:
                continue
            shared_count[mid] += 1
            movie_store[mid] = m

    all_movies = list(movie_store.values())
    all_movies.sort(
        key=lambda m: (shared_count[m["id"]], m.get("vote_average", 0)),
        reverse=True
    )

    candidates = _dedupe(all_movies, {profile["id"]}, min_votes=300)

    result = []
    for m in candidates[:limit]:
        fmt = _format(m)
        fmt["shared_actors"] = shared_count[m["id"]]
        result.append(fmt)
    return result


# ── Engine 4 — Critically Acclaimed ──────────────────────────────────────────

def acclaimed(profile: dict, limit: int = 15) -> list:
    """
    Critically acclaimed films at the same quality tier.
    vote_count ≥ 5000 ensures only genuine classics appear.
    """
    avg = profile["vote_average"]

    if avg >= 8.5:
        min_rating = 8.5
    elif avg >= 8.0:
        min_rating = 8.0
    elif avg >= 7.5:
        min_rating = 7.5
    else:
        min_rating = 7.0

    raw = discover({
        "sort_by":          "vote_average.desc",
        "vote_count.gte":   5000,
        "vote_average.gte": min_rating,
    }, pages=4)

    candidates = _dedupe(raw, {profile["id"]}, min_votes=5000)
    return [_format(m) for m in candidates[:limit]]


# ── Genre Wheel ───────────────────────────────────────────────────────────────

def genre_wheel(genre_id: int, limit: int = 20) -> list:
    """Top-rated films in a specific genre for the genre wheel feature."""
    raw = discover({
        "with_genres":    genre_id,
        "sort_by":        "vote_average.desc",
        "vote_count.gte": 3000,
    }, pages=3)

    candidates = _dedupe(raw, set(), min_votes=3000)
    return [_format(m) for m in candidates[:limit]]


# ── Main entry point ──────────────────────────────────────────────────────────

def get_all(movie_id: int) -> dict | None:
    """
    Build the full CineMood result for a selected movie.
    Returns None if the movie_id can't be fetched.
    """
    profile = build_profile(movie_id)
    if not profile:
        return None

    return {
        "movie":    profile,
        "mood":     mood(profile),
        "director": director(profile),
        "actors":   actors(profile),
        "acclaimed":acclaimed(profile),
    }
