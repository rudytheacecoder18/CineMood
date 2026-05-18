"""
app.py
------
CineMood — Find movies that match your mood. Because every movie has a mood.

Run locally:  streamlit run app.py
Deploy:       Streamlit Cloud — add TMDB_API_KEY to app secrets
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

# ─── API Key — checks Streamlit secrets first, then .env ─────────────────────
def _get_api_key() -> str:
    # 1. Streamlit Cloud secrets panel
    try:
        key = st.secrets.get("TMDB_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    # 2. Local .env / system environment
    return os.getenv("TMDB_API_KEY", "")

API_KEY = _get_api_key()

# Inject into tmdb_client so it uses the correct key on Cloud
import tmdb_client as _tc
_tc.API_KEY = API_KEY

if not API_KEY:
    st.markdown("""
    <div style="max-width:500px;margin:80px auto;text-align:center;font-family:Inter,sans-serif;">
        <div style="font-size:3rem;margin-bottom:16px;">🎬</div>
        <div style="font-size:1.3rem;font-weight:700;color:#f0f0f0;margin-bottom:12px;">TMDB API Key Missing</div>
        <div style="font-size:0.85rem;color:#777;line-height:1.7;">
            Locally: create a <code style="background:#111;padding:2px 6px;border-radius:4px;color:#f5c518">.env</code> file with
            <code style="color:#f5c518">TMDB_API_KEY=your_key</code><br><br>
            On Streamlit Cloud: add <code style="color:#f5c518">TMDB_API_KEY = "your_key"</code>
            in your app Secrets panel.<br><br>
            Get a free key at <a href="https://www.themoviedb.org/settings/api" target="_blank"
            style="color:#f5c518">themoviedb.org</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Base ── */
.stApp { background: #080808 !important; font-family: 'Inter', sans-serif; }
.block-container { padding-top: 0 !important; padding-bottom: 80px !important; max-width: 1420px !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Header ── */
.cm-header {
    text-align: center;
    padding: 60px 24px 30px;
    background: radial-gradient(ellipse 90% 60% at 50% 0%, #1c1100 0%, #080808 65%);
}
.cm-logo {
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #f5c518 0%, #c8940a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 12px;
}
/* ── TAGLINE — visible but subtle ── */
.cm-tagline {
    font-size: 0.72rem;
    color: #777;
    font-weight: 400;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: #0d0d0d !important;
    border: 1.5px solid #1e1e1e !important;
    border-radius: 10px !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.18s !important;
    caret-color: #f5c518 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f5c518 !important;
    box-shadow: 0 0 0 3px rgba(245,197,24,0.06) !important;
}
.stTextInput > div > div > input::placeholder { color: #383838 !important; }
.stTextInput label {
    color: #666 !important;
    font-size: 0.68rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #f5c518 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 13px 20px !important;
    transition: all 0.16s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #d4a000 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(245,197,24,0.25) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Radio (movie selector) ── */
div[role="radiogroup"] { display: flex; flex-direction: column; gap: 5px; }
div[role="radiogroup"] label {
    background: #0d0d0d !important;
    border: 1px solid #1c1c1c !important;
    border-radius: 9px !important;
    padding: 11px 15px !important;
    cursor: pointer !important;
    color: #aaa !important;
    font-size: 0.88rem !important;
    transition: border-color 0.16s, color 0.16s !important;
}
div[role="radiogroup"] label:hover {
    border-color: #f5c518 !important;
    color: #e0e0e0 !important;
}
div[role="radiogroup"] > label { display: none !important; }

/* Spinner */
.stSpinner > div { border-top-color: #f5c518 !important; }

/* ── Section header ── */
.cm-section {
    display: flex; align-items: center; gap: 10px;
    margin: 46px 0 10px;
    padding-bottom: 12px;
    border-bottom: 1px solid #141414;
}
.cm-section-icon { font-size: 1rem; }
.cm-section-title { font-size: 1rem; font-weight: 700; color: #f5c518; }
/* ── Section sub count — visible ── */
.cm-section-sub { font-size: 0.7rem; color: #555; margin-left: auto; }

/* ── Mood theme tags ── */
.cm-themes { display: flex; flex-wrap: wrap; gap: 7px; margin: 0 0 14px; }
.cm-theme-tag {
    background: rgba(245,197,24,0.07);
    border: 1px solid rgba(245,197,24,0.2);
    color: rgba(245,197,24,0.8);
    border-radius: 20px;
    padding: 4px 13px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* ── Hero card (selected movie) ── */
.cm-hero {
    background: #0c0c0c;
    border: 1px solid #191919;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    margin: 20px 0 0;
}
.cm-hero-poster { flex: 0 0 190px; background: #0a0a0a; }
.cm-hero-poster img { width: 190px; height: 285px; object-fit: cover; display: block; }
.cm-hero-noposter {
    width: 190px; height: 285px;
    display: flex; align-items: center; justify-content: center;
    font-size: 5rem; background: #0f0f0f; color: #1e1e1e;
}
.cm-hero-info {
    padding: 28px 34px; flex: 1; min-width: 0;
    display: flex; flex-direction: column; justify-content: center;
}
.cm-hero-title {
    font-size: 2rem; font-weight: 800;
    color: #f0f0f0; line-height: 1.15;
    margin-bottom: 8px; letter-spacing: -0.5px;
}
.cm-hero-meta {
    font-size: 0.8rem; color: #555;
    display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
}
.cm-hero-rating { color: #f5c518; font-weight: 700; font-size: 0.85rem; }
.cm-hero-tagline {
    font-size: 0.82rem; color: #555;
    font-style: italic; margin-bottom: 14px;
    border-left: 2px solid #222; padding-left: 12px;
}
.cm-hero-overview {
    font-size: 0.83rem; color: #999;
    line-height: 1.75; margin-bottom: 22px; max-width: 640px;
}
.cm-meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px,1fr));
    gap: 14px;
}
/* ── Meta labels — now visible ── */
.cm-meta-label {
    font-size: 0.6rem; color: #555;
    text-transform: uppercase; letter-spacing: 1.8px;
    margin-bottom: 4px; font-weight: 700;
}
.cm-meta-value { font-size: 0.8rem; color: #c0c0c0; font-weight: 500; line-height: 1.5; }

/* ── Card rows ── */
.cards-scroll {
    display: flex; gap: 12px; overflow-x: auto;
    padding: 4px 2px 20px;
    scrollbar-width: thin; scrollbar-color: #1a1a1a transparent;
}
.cards-scroll::-webkit-scrollbar { height: 3px; }
.cards-scroll::-webkit-scrollbar-thumb { background: #1a1a1a; border-radius: 2px; }

/* ── Movie card ── */
.mcard {
    flex: 0 0 156px;
    background: #0d0d0d;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #181818;
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    position: relative;
    cursor: pointer;
}
.mcard:hover {
    transform: translateY(-8px);
    border-color: rgba(245,197,24,0.5);
    box-shadow: 0 16px 40px rgba(0,0,0,0.75), 0 0 0 1px rgba(245,197,24,0.12);
}
.mcard-img { width: 100%; height: 234px; object-fit: cover; display: block; }
.mcard-empty {
    width: 100%; height: 234px;
    background: linear-gradient(135deg, #0f0f0f, #151515);
    display: flex; align-items: center; justify-content: center; font-size: 2.8rem;
}
.mcard-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(8,8,8,0) 25%, rgba(8,8,8,0.97) 75%);
    opacity: 0; transition: opacity 0.22s ease;
    padding: 12px; display: flex; flex-direction: column; justify-content: flex-end;
}
.mcard:hover .mcard-overlay { opacity: 1; }
.mcard-overview-text {
    font-size: 0.65rem; color: #ccc;
    line-height: 1.55;
    display: -webkit-box; -webkit-line-clamp: 7; -webkit-box-orient: vertical; overflow: hidden;
}
.mcard-body { padding: 9px 11px 11px; }
.mcard-title {
    font-size: 0.79rem; font-weight: 600; color: #ddd;
    margin-bottom: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.mcard-meta { font-size: 0.69rem; color: #555; display: flex; gap: 5px; align-items: center; }
.mcard-star { color: #f5c518; font-weight: 700; }

/* ── Genre wheel ── */
/* ── Divider — now visible ── */
.cm-divider {
    text-align: center; color: #444;
    font-size: 0.68rem; letter-spacing: 3px;
    text-transform: uppercase; margin: 40px 0 24px;
}
/* ── Wheel label — now visible ── */
.wheel-label {
    text-align: center;
    font-size: 0.68rem; color: #555;
    letter-spacing: 2.5px; text-transform: uppercase;
    margin-bottom: 18px;
}

/* ── Labels above inputs ── */
.cm-label {
    font-size: 0.66rem; color: #555;
    text-transform: uppercase; letter-spacing: 2px;
    margin: 18px 0 7px; font-weight: 600;
}

/* ── Footer ── */
.cm-attr {
    text-align: center; margin-top: 52px;
    font-size: 0.64rem; color: #333;
}
.cm-attr a { color: #444; text-decoration: none; }
.cm-attr a:hover { color: #666; }
</style>
""", unsafe_allow_html=True)


# ─── Cached API Calls ─────────────────────────────────────────────────────────

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
    title    = (m.get("title") or "").replace('"', "&quot;")
    year     = m.get("year", "")
    rating   = m.get("vote_average", 0)
    overview = (m.get("overview") or "")[:260].replace("<", "&lt;").replace(">", "&gt;")
    p        = _poster(m.get("poster_path") or "")

    img  = (f'<img class="mcard-img" src="{p}" loading="lazy" alt="{title}" />'
            if p else '<div class="mcard-empty">🎬</div>')
    star = f'<span class="mcard-star">⭐ {rating:.1f}</span>' if rating else ""
    dot  = "<span>·</span>" if (year and star) else ""

    return f"""<div class="mcard">
        {img}
        <div class="mcard-overlay"><p class="mcard-overview-text">{overview}</p></div>
        <div class="mcard-body">
            <div class="mcard-title" title="{title}">{title}</div>
            <div class="mcard-meta">{year}{dot}{star}</div>
        </div>
    </div>"""


def _section_hdr(title: str, icon: str, count: int) -> str:
    return (f'<div class="cm-section">'
            f'<span class="cm-section-icon">{icon}</span>'
            f'<span class="cm-section-title">{title}</span>'
            f'<span class="cm-section-sub">{count} films</span>'
            f'</div>')


def render_section(title: str, icon: str, films: list):
    if not films:
        return
    cards = "".join(_card_html(m) for m in films)
    st.markdown(_section_hdr(title, icon, len(films)) +
                f'<div class="cards-scroll">{cards}</div>',
                unsafe_allow_html=True)


def render_hero(movie: dict):
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
    p        = _poster(movie.get("poster_path") or "", "w500")

    poster_html = (
        f'<img src="{p}" style="width:190px;height:285px;object-fit:cover;display:block;" />'
        if p else '<div class="cm-hero-noposter">🎬</div>'
    )

    meta_parts = []
    if year:    meta_parts.append(f"<span>{year}</span>")
    if runtime: meta_parts.append(f"<span>{runtime} min</span>")
    if rating:  meta_parts.append(f'<span class="cm-hero-rating">⭐ {rating:.1f} / 10</span>')
    meta_html = '<span style="color:#222">·</span>'.join(meta_parts)

    tl  = f'<div class="cm-hero-tagline">{tagline}</div>' if tagline else ""
    ov  = f'<div class="cm-hero-overview">{overview[:460]}{"…" if len(overview)>460 else ""}</div>'

    def row(label, val):
        return (f'<div><div class="cm-meta-label">{label}</div>'
                f'<div class="cm-meta-value">{val}</div></div>') if val else ""

    grid = "".join([
        row("Director", director),
        row("Cast",     ", ".join(cast)),
        row("Genres",   " · ".join(genres)),
        row("Themes",   " · ".join(keywords)),
    ])

    st.markdown(
        '<div class="cm-label">You selected</div>'
        f'<div class="cm-hero">'
        f'<div class="cm-hero-poster">{poster_html}</div>'
        f'<div class="cm-hero-info">'
        f'<div class="cm-hero-title">{title}</div>'
        f'<div class="cm-hero-meta">{meta_html}</div>'
        f'{tl}{ov}<div class="cm-meta-grid">{grid}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )


# ─── Genre Wheel ─────────────────────────────────────────────────────────────

FEATURED_GENRES = {
    28: "Action",    12: "Adventure",  16: "Animation",
    35: "Comedy",    80: "Crime",      18: "Drama",
    14: "Fantasy",   36: "History",    27: "Horror",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    53: "Thriller",  10752: "War",     37: "Western",
}


def render_genre_wheel():
    genres_raw = cached_genres()
    genres = sorted(
        [g for g in genres_raw if g["id"] in FEATURED_GENRES],
        key=lambda g: g["name"]
    )

    st.markdown('<div class="cm-divider">— or discover by genre —</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="wheel-label">pick a genre · or spin for a surprise</div>',
                unsafe_allow_html=True)

    _, spin_col, _ = st.columns([2, 2, 2])
    with spin_col:
        if st.button("🎲  Spin the Wheel", use_container_width=True):
            if genres:                                   # ← FIX: guard against empty list
                st.session_state.sel_genre  = random.choice(genres)
                st.session_state.genre_films = None
            else:
                st.warning("Genre data is loading — please try again in a moment.")

    if not genres:
        st.info("Genre list is unavailable right now. Please refresh the page.")
        return

    cols = st.columns(5)
    for i, g in enumerate(genres):
        with cols[i % 5]:
            sel    = st.session_state.get("sel_genre") or {}
            active = sel.get("id") == g["id"]
            label  = f"✓  {g['name']}" if active else g["name"]
            if st.button(label, key=f"genre_{g['id']}", use_container_width=True):
                st.session_state.sel_genre   = g
                st.session_state.genre_films = None

    sel = st.session_state.get("sel_genre")
    if sel:
        if not st.session_state.get("genre_films"):
            with st.spinner(f"Loading top {sel['name']} films…"):
                st.session_state.genre_films = cached_genre_movies(sel["id"])
        films = st.session_state.genre_films or []
        if films:
            render_section(f"Top {sel['name']} Films", "🎡", films)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    for k, v in {
        "search_results": [],
        "recs":           None,
        "sel_movie_id":   None,
        "sel_genre":      None,
        "genre_films":    None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Header
    st.markdown(
        '<div class="cm-header">'
        '<div class="cm-logo">🎬 CineMood</div>'
        '<div class="cm-tagline">Find movies that match your mood.'
        ' &nbsp;·&nbsp; Because every movie has a mood.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # Search bar
    _, col, _ = st.columns([1, 3.2, 1])
    with col:
        query = st.text_input(
            "Search a movie",
            placeholder="Fight Club, Shutter Island, Interstellar, The Godfather…",
            label_visibility="visible",
        )
        btn_col, clear_col = st.columns([5, 1])
        with btn_col:
            search_btn = st.button("🔍  Search", use_container_width=True)
        with clear_col:
            if st.button("✕", use_container_width=True, help="Clear"):
                for k in ["search_results", "recs", "sel_movie_id",
                          "sel_genre", "genre_films"]:
                    st.session_state[k] = [] if k == "search_results" else None
                st.rerun()

    if search_btn and query.strip():
        with st.spinner("Searching…"):
            results = cached_search(query.strip())
            st.session_state.search_results = results[:8]
            st.session_state.recs           = None
            st.session_state.sel_movie_id   = None

    # Movie picker
    if st.session_state.search_results:
        _, col, _ = st.columns([1, 3.2, 1])
        with col:
            options = {}
            for r in st.session_state.search_results:
                yr    = (r.get("release_date") or "")[:4]
                score = r.get("vote_average", 0)
                label = f"{r.get('title', '')}  ({yr})"
                if score:
                    label += f"  ·  ⭐ {score:.1f}"
                options[label] = r["id"]

            st.markdown('<div class="cm-label">Select the movie</div>',
                        unsafe_allow_html=True)
            sel_label = st.radio(
                "Select movie", list(options.keys()),
                label_visibility="collapsed", key="movie_radio"
            )
            if st.button("🎬  Get Recommendations", use_container_width=True):
                st.session_state.sel_movie_id = options[sel_label]
                st.session_state.recs        = None
                st.session_state.sel_genre   = None
                st.session_state.genre_films = None

    # Load recommendations
    if st.session_state.sel_movie_id and st.session_state.recs is None:
        with st.spinner("🎬  Building your CineMood recommendations…"):
            st.session_state.recs = cached_all_recs(st.session_state.sel_movie_id)

    # Display recommendations
    if st.session_state.recs:
        data  = st.session_state.recs
        movie = data["movie"]

        render_hero(movie)

        # 1 — Mood
        mood_data  = data.get("mood", {})
        themes     = mood_data.get("themes", [])
        mood_films = mood_data.get("films", [])

        if mood_films:
            tags_html = "".join(
                f'<span class="cm-theme-tag">{t}</span>' for t in themes
            )
            st.markdown(
                _section_hdr("Similar Vibe & Mood", "🔮", len(mood_films)) +
                (f'<div class="cm-themes">{tags_html}</div>' if themes else "") +
                f'<div class="cards-scroll">{"".join(_card_html(m) for m in mood_films)}</div>',
                unsafe_allow_html=True
            )

        # 2 — Director
        dir_films = data.get("director", [])
        if dir_films:
            render_section(
                f"More from {movie.get('director') or 'Same Director'}",
                "🎬", dir_films
            )

        # 3 — Actors
        act_films = data.get("actors", [])
        if act_films:
            names = [c["name"] for c in movie.get("cast", [])[:3]]
            render_section(
                f"Featuring {', '.join(names)}" if names else "Shared Cast",
                "👥", act_films
            )

        # 4 — Acclaimed
        acc_films = data.get("acclaimed", [])
        if acc_films:
            render_section("Critically Acclaimed Cinema", "⭐", acc_films)

    else:
        render_genre_wheel()

    # Footer
    st.markdown(
        '<div class="cm-attr">Powered by '
        '<a href="https://www.themoviedb.org" target="_blank">TMDB</a> &nbsp;·&nbsp; '
        'Not endorsed or certified by TMDB.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
