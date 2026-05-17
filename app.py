"""
app.py
------
CineMood — Find movies that match your mood. Because every movie has a mood.

Run: streamlit run app.py
"""

import os
import random
import streamlit as st
from dotenv import load_dotenv

import tmdb_client as tmdb
import recommender as rec

load_dotenv()

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMood",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_KEY = os.getenv("TMDB_API_KEY", "")
if not API_KEY:
    st.error(
        "**TMDB API key missing.**\n\n"
        "Create a `.env` file in this folder with:\n```\nTMDB_API_KEY=your_key_here\n```\n\n"
        "Get a free key at: https://www.themoviedb.org/settings/api"
    )
    st.stop()


# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & base ── */
.stApp { background: #080808; font-family: 'Inter', sans-serif; }
.block-container { padding-top: 0 !important; padding-bottom: 60px !important; max-width: 1400px !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Header ── */
.cm-header {
    text-align: center;
    padding: 52px 24px 24px;
    background: radial-gradient(ellipse 80% 50% at 50% 0%, #1a1000 0%, #080808 70%);
    margin-bottom: 0;
}
.cm-logo {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #f5c518 0%, #d4a000 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 10px;
}
.cm-tagline {
    font-size: 0.75rem;
    color: #444;
    font-weight: 400;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #0f0f0f !important;
    border: 1.5px solid #1e1e1e !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 13px 16px !important;
    transition: border-color 0.18s !important;
}
.stTextInput > div > div > input:focus { border-color: #f5c518 !important; }
.stTextInput > div > div > input::placeholder { color: #333 !important; }
.stTextInput label { color: #333 !important; font-size: 0.7rem !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }

/* ── Buttons ── */
.stButton > button {
    background: #f5c518 !important;
    color: #080808 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 12px 20px !important;
    transition: all 0.16s ease !important;
    width: 100% !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    background: #d4a000 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(245,197,24,0.22) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Radio (movie selector) ── */
div[role="radiogroup"] { display: flex; flex-direction: column; gap: 5px; }
div[role="radiogroup"] label {
    background: #0f0f0f !important; border: 1px solid #1a1a1a !important;
    border-radius: 8px !important; padding: 10px 14px !important;
    cursor: pointer !important; color: #aaa !important; font-size: 0.88rem !important;
    transition: border-color 0.16s !important;
}
div[role="radiogroup"] label:hover { border-color: #f5c518 !important; }
div[role="radiogroup"] > label { display: none !important; }

/* ── Section headers ── */
.cm-section {
    display: flex; align-items: center; gap: 10px;
    margin: 42px 0 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #141414;
}
.cm-section-icon { font-size: 1rem; }
.cm-section-title { font-size: 1rem; font-weight: 700; color: #f5c518; }
.cm-section-sub { font-size: 0.72rem; color: #333; margin-left: auto; }

/* ── Theme tags ── */
.cm-themes { display: flex; flex-wrap: wrap; gap: 7px; margin: 0 0 16px; }
.cm-theme-tag {
    background: rgba(245,197,24,0.07);
    border: 1px solid rgba(245,197,24,0.18);
    color: rgba(245,197,24,0.75);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* ── Input movie card ── */
.cm-selected {
    background: #0d0d0d; border: 1px solid #1a1a1a;
    border-radius: 14px; overflow: hidden;
    display: flex; gap: 0; margin: 18px 0 0;
}
.cm-sel-poster { flex: 0 0 185px; background: #0a0a0a; }
.cm-sel-poster img { width: 185px; height: 277px; object-fit: cover; display: block; }
.cm-sel-noposter {
    width: 185px; height: 277px;
    display: flex; align-items: center; justify-content: center;
    font-size: 4rem; background: #111; color: #1e1e1e;
}
.cm-sel-info { padding: 26px 30px; flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
.cm-sel-title { font-size: 1.9rem; font-weight: 800; color: #f0f0f0; line-height: 1.15; margin-bottom: 8px; }
.cm-sel-meta { font-size: 0.8rem; color: #444; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.cm-sel-rating { color: #f5c518; font-weight: 700; }
.cm-sel-tagline { font-size: 0.83rem; color: #444; font-style: italic; margin-bottom: 12px; }
.cm-sel-overview { font-size: 0.83rem; color: #888; line-height: 1.7; margin-bottom: 18px; max-width: 660px; }
.cm-meta-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px,1fr)); gap: 12px; }
.cm-meta-label { font-size: 0.62rem; color: #333; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 3px; font-weight: 600; }
.cm-meta-value { font-size: 0.8rem; color: #bbb; font-weight: 500; line-height: 1.4; }

/* ── Horizontal card rows ── */
.cards-scroll {
    display: flex; gap: 12px; overflow-x: auto;
    padding: 4px 2px 18px;
    scrollbar-width: thin; scrollbar-color: #1e1e1e transparent;
}
.cards-scroll::-webkit-scrollbar { height: 4px; }
.cards-scroll::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }

/* ── Movie card ── */
.mcard {
    flex: 0 0 158px;
    background: #0d0d0d;
    border-radius: 11px;
    overflow: hidden;
    border: 1px solid #171717;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
}
.mcard:hover {
    transform: translateY(-7px);
    border-color: #f5c518;
    box-shadow: 0 14px 36px rgba(0,0,0,0.7), 0 0 0 1px rgba(245,197,24,0.15);
}
.mcard-img { width: 100%; height: 237px; object-fit: cover; display: block; }
.mcard-empty {
    width: 100%; height: 237px;
    background: #111; display: flex;
    align-items: center; justify-content: center;
    font-size: 2.5rem;
}
/* Hover overlay */
.mcard-overlay {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg, rgba(8,8,8,0) 35%, rgba(8,8,8,0.97) 78%);
    opacity: 0; transition: opacity 0.2s ease;
    padding: 12px; display: flex; flex-direction: column; justify-content: flex-end;
}
.mcard:hover .mcard-overlay { opacity: 1; }
.mcard-overview {
    font-size: 0.66rem; color: #aaa; line-height: 1.5;
    display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; overflow: hidden;
}
/* Card body */
.mcard-body { padding: 9px 11px 11px; }
.mcard-title {
    font-size: 0.8rem; font-weight: 600; color: #e0e0e0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    margin-bottom: 3px;
}
.mcard-meta { font-size: 0.7rem; color: #444; display: flex; gap: 5px; align-items: center; }
.mcard-rating { color: #f5c518; font-weight: 600; }

/* ── Genre wheel ── */
.wheel-wrap { text-align: center; padding: 6px 0 10px; }
.wheel-label {
    font-size: 0.68rem; color: #2e2e2e;
    letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 16px;
}

/* ── Divider ── */
.cm-divider {
    text-align: center; color: #1e1e1e;
    font-size: 0.68rem; letter-spacing: 3px;
    text-transform: uppercase; margin: 36px 0 24px;
}

/* ── Attribution ── */
.cm-attr { text-align: center; margin-top: 44px; font-size: 0.66rem; color: #1e1e1e; }
</style>
""", unsafe_allow_html=True)


# ─── Cached API Calls ─────────────────────────────────────────────────────────
# These prevent re-fetching the same data when Streamlit reruns the script.

@st.cache_data(ttl=86_400, show_spinner=False)
def cached_search(query: str) -> list:
    return tmdb.search_movie(query)

@st.cache_data(ttl=86_400, show_spinner=False)
def cached_all_recs(movie_id: int) -> dict | None:
    return rec.get_all(movie_id)

@st.cache_data(ttl=86_400, show_spinner=False)
def cached_genre_movies(genre_id: int) -> list:
    return rec.genre_wheel(genre_id)

@st.cache_data(ttl=86_400 * 7, show_spinner=False)
def cached_genres() -> list:
    return tmdb.get_genre_list()


# ─── HTML helpers ─────────────────────────────────────────────────────────────

def _poster(path: str, size: str = "w342") -> str:
    return tmdb.poster(path, size)


def _card_html(m: dict) -> str:
    title    = m.get("title", "")
    year     = m.get("year", "")
    rating   = m.get("vote_average", 0)
    overview = (m.get("overview") or "")[:240]
    p        = _poster(m.get("poster_path"))

    img = (f'<img class="mcard-img" src="{p}" loading="lazy" alt="{title}" />'
           if p else '<div class="mcard-empty">🎬</div>')

    rating_html = f'<span class="mcard-rating">⭐ {rating:.1f}</span>' if rating else ""

    return f"""
    <div class="mcard">
        {img}
        <div class="mcard-overlay">
            <p class="mcard-overview">{overview}</p>
        </div>
        <div class="mcard-body">
            <div class="mcard-title" title="{title}">{title}</div>
            <div class="mcard-meta">
                <span>{year}</span>
                {"<span>·</span>" + rating_html if rating_html else ""}
            </div>
        </div>
    </div>"""


def render_section(title: str, icon: str, films: list, sub: str = ""):
    if not films:
        return
    cards = "".join(_card_html(m) for m in films)
    sub_html = f'<span class="cm-section-sub">{sub}</span>' if sub else ""
    st.markdown(f"""
    <div class="cm-section">
        <span class="cm-section-icon">{icon}</span>
        <span class="cm-section-title">{title}</span>
        {sub_html}
    </div>
    <div class="cards-scroll">{cards}</div>
    """, unsafe_allow_html=True)


def render_input_movie(movie: dict):
    title    = movie.get("title", "")
    year     = movie.get("year", "")
    rating   = movie.get("vote_average", 0)
    runtime  = movie.get("runtime")
    tagline  = movie.get("tagline", "")
    overview = movie.get("overview", "")
    director = movie.get("director", "")
    cast     = [c["name"] for c in movie.get("cast", [])[:6]]
    genres   = movie.get("genres", [])
    keywords = movie.get("keywords", [])[:5]
    p        = _poster(movie.get("poster_path"), "w500")

    poster_html = (f'<img src="{p}" style="width:185px;height:277px;object-fit:cover;display:block;" />'
                   if p else '<div class="cm-sel-noposter">🎬</div>')

    meta = []
    if year:    meta.append(year)
    if runtime: meta.append(f"{runtime} min")
    if rating:  meta.append(f'<span class="cm-sel-rating">⭐ {rating:.1f} / 10</span>')
    meta_html = '<span style="color:#1e1e1e">·</span>'.join(meta)

    tl = f'<div class="cm-sel-tagline">"{tagline}"</div>' if tagline else ""
    ov = f'<div class="cm-sel-overview">{overview[:440]}{"..." if len(overview)>440 else ""}</div>'

    def row(label, val):
        return (f'<div><div class="cm-meta-label">{label}</div>'
                f'<div class="cm-meta-value">{val}</div></div>') if val else ""

    grid = "".join([
        row("Director", director),
        row("Cast",     ", ".join(cast)),
        row("Genres",   " · ".join(genres)),
        row("Themes",   " · ".join(keywords)),
    ])

    st.markdown(f"""
    <div style="font-size:0.68rem;color:#282828;text-transform:uppercase;letter-spacing:2px;margin:26px 0 6px;">You selected</div>
    <div class="cm-selected">
        <div class="cm-sel-poster">{poster_html}</div>
        <div class="cm-sel-info">
            <div class="cm-sel-title">{title}</div>
            <div class="cm-sel-meta">{meta_html}</div>
            {tl}{ov}
            <div class="cm-meta-grid">{grid}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Genre wheel ─────────────────────────────────────────────────────────────

FEATURED_GENRES = {
    28: "Action", 12: "Adventure", 16: "Animation",
    35: "Comedy", 80: "Crime", 18: "Drama",
    14: "Fantasy", 36: "History", 27: "Horror",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    53: "Thriller", 10752: "War", 37: "Western",
}


def render_genre_wheel():
    genres_raw = cached_genres()
    genres = [g for g in genres_raw if g["id"] in FEATURED_GENRES]
    genres.sort(key=lambda g: g["name"])

    st.markdown('<div class="cm-divider">— or explore by genre —</div>', unsafe_allow_html=True)
    st.markdown('<div class="wheel-wrap"><div class="wheel-label">pick a genre · or spin for a random one</div></div>',
                unsafe_allow_html=True)

    _, col_btn, _ = st.columns([2, 2, 2])
    with col_btn:
        if st.button("🎲  Spin the Wheel", use_container_width=True):
            chosen = random.choice(genres)
            st.session_state.sel_genre  = chosen
            st.session_state.genre_films = None

    cols = st.columns(5)
    for i, g in enumerate(genres):
        with cols[i % 5]:
            active = (st.session_state.get("sel_genre") or {}).get("id") == g["id"]
            label  = f"✓ {g['name']}" if active else g["name"]
            if st.button(label, key=f"g_{g['id']}", use_container_width=True):
                st.session_state.sel_genre  = g
                st.session_state.genre_films = None

    sel = st.session_state.get("sel_genre")
    if sel:
        if not st.session_state.get("genre_films"):
            with st.spinner(f"Loading top {sel['name']} films..."):
                st.session_state.genre_films = cached_genre_movies(sel["id"])
        if st.session_state.genre_films:
            render_section(
                title=f"Top {sel['name']} Films",
                icon="🎡",
                films=st.session_state.genre_films,
                sub=f"{len(st.session_state.genre_films)} films",
            )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Session state defaults
    for k, v in {
        "search_results":  [],
        "recs":            None,
        "sel_movie_id":    None,
        "sel_genre":       None,
        "genre_films":     None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Header ──
    st.markdown("""
    <div class="cm-header">
        <div class="cm-logo">🎬 CineMood</div>
        <div class="cm-tagline">Find movies that match your mood. Because every movie has a mood.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Search ──
    _, col, _ = st.columns([1, 3.5, 1])
    with col:
        query = st.text_input(
            "Search a movie",
            placeholder="Fight Club, Shutter Island, Interstellar, The Godfather...",
            label_visibility="visible",
        )
        c1, c2 = st.columns([5, 1])
        with c1:
            search_btn = st.button("🔍  Search", use_container_width=True)
        with c2:
            if st.button("✕", use_container_width=True, help="Clear"):
                for k in ["search_results", "recs", "sel_movie_id",
                          "sel_genre", "genre_films"]:
                    st.session_state[k] = [] if k == "search_results" else None
                st.rerun()

    if search_btn and query.strip():
        with st.spinner("Searching..."):
            results = cached_search(query.strip())
            st.session_state.search_results = results[:8]
            st.session_state.recs           = None
            st.session_state.sel_movie_id   = None

    # ── Movie selection ──
    if st.session_state.search_results:
        _, col, _ = st.columns([1, 3.5, 1])
        with col:
            options = {}
            for r in st.session_state.search_results:
                yr    = (r.get("release_date") or "")[:4]
                score = r.get("vote_average", 0)
                label = f"{r.get('title','')} ({yr})"
                if score:
                    label += f"  ·  ⭐ {score:.1f}"
                options[label] = r["id"]

            st.markdown(
                '<div style="font-size:0.68rem;color:#333;letter-spacing:1.5px;'
                'text-transform:uppercase;margin:16px 0 8px;">Select the movie</div>',
                unsafe_allow_html=True
            )
            sel_label = st.radio("Select movie", list(options.keys()),
                                 label_visibility="collapsed", key="movie_radio")

            if st.button("🎬  Get Recommendations", use_container_width=True):
                st.session_state.sel_movie_id = options[sel_label]
                st.session_state.recs         = None
                st.session_state.sel_genre    = None
                st.session_state.genre_films  = None

    # ── Load recommendations ──
    if st.session_state.sel_movie_id and st.session_state.recs is None:
        with st.spinner("🎬  Building your CineMood..."):
            st.session_state.recs = cached_all_recs(st.session_state.sel_movie_id)

    # ── Display recommendations ──
    if st.session_state.recs:
        data  = st.session_state.recs
        movie = data["movie"]

        render_input_movie(movie)

        # 1 — Mood / Vibe
        mood_data = data.get("mood", {})
        themes    = mood_data.get("themes", [])
        mood_films = mood_data.get("films", [])

        if mood_films:
            if themes:
                tags = "".join(f'<span class="cm-theme-tag">{t}</span>' for t in themes)
                st.markdown(f'<div class="cm-section"><span class="cm-section-icon">🔮</span>'
                            f'<span class="cm-section-title">Similar Vibe & Mood</span>'
                            f'<span class="cm-section-sub">{len(mood_films)} films</span></div>'
                            f'<div class="cm-themes">{tags}</div>'
                            f'<div class="cards-scroll">{"".join(_card_html(m) for m in mood_films)}</div>',
                            unsafe_allow_html=True)
            else:
                render_section("Similar Vibe & Mood", "🔮", mood_films,
                               sub=f"{len(mood_films)} films")

        # 2 — Director
        director_films = data.get("director", [])
        if director_films:
            director_name = movie.get("director", "Same Director")
            render_section(
                title=f"More from {director_name}",
                icon="🎬",
                films=director_films,
                sub=f"{len(director_films)} films",
            )

        # 3 — Actors
        actor_films = data.get("actors", [])
        if actor_films:
            top_cast = [c["name"] for c in movie.get("cast", [])[:3]]
            cast_line = ", ".join(top_cast) if top_cast else "Shared Cast"
            render_section(
                title=f"Featuring {cast_line}",
                icon="👥",
                films=actor_films,
                sub=f"{len(actor_films)} films",
            )

        # 4 — Acclaimed
        acclaimed_films = data.get("acclaimed", [])
        if acclaimed_films:
            render_section(
                title="Critically Acclaimed Cinema",
                icon="⭐",
                films=acclaimed_films,
                sub=f"{len(acclaimed_films)} classics",
            )

    else:
        # Show genre wheel when no movie is selected
        render_genre_wheel()

    # ── Footer ──
    st.markdown(
        '<div class="cm-attr">Powered by TMDB · '
        'This product uses the TMDB API but is not endorsed or certified by TMDB.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
