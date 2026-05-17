"""
moods.py
--------
CineMood's curated cinematic intelligence layer.

This is what separates CineMood from a generic recommender.
Instead of relying purely on TMDB metadata, we store hand-picked
"mood profiles" for iconic films — capturing emotional tone, atmosphere,
and thematic similarity that algorithms alone miss.

Structure per film:
  themes   — the emotional/thematic tags shown in the UI ("Why Recommended")
  mood_ids — TMDB movie IDs of hand-picked films with the same cinematic feel

To add a new film: look up its TMDB ID, write its themes, pick 8-12 films
with the same emotional experience, and add an entry below.
"""

# Keys are lowercase movie titles (stripped of punctuation) for fuzzy matching.
# TMDB IDs are used directly — no extra search API calls needed.

CURATED = {

    # ── Existential Male Alienation ───────────────────────────────────────────
    "fight club": {
        "themes": ["Male Alienation", "Identity Crisis", "Anti-Consumerism",
                   "Psychological Chaos", "Dark Satire"],
        "mood_ids": [
            103,     # Taxi Driver
            475557,  # Joker
            242582,  # Nightcrawler
            228150,  # Drive
            1359,    # American Psycho
            544,     # Trainspotting
            641,     # Requiem for a Dream
            44217,   # American History X
            6977,    # No Country for Old Men
            7551,    # There Will Be Blood
            152601,  # Her
            37799,   # The Social Network
        ],
    },

    # ── Psychological Mystery / Paranoia ──────────────────────────────────────
    "shutter island": {
        "themes": ["Psychological Thriller", "Paranoia", "Mind-Bending Mystery",
                   "Dark Atmosphere", "Reality vs Illusion"],
        "mood_ids": [
            807,     # Se7en
            274,     # The Silence of the Lambs
            146233,  # Prisoners
            1599,    # Zodiac
            77,      # Memento
            210577,  # Gone Girl
            1745,    # The Prestige
            45612,   # Black Swan
            1422,    # The Departed
            6045,    # Oldboy
            6977,    # No Country for Old Men
            103,     # Taxi Driver
        ],
    },

    # ── Mafia / Crime Empire ──────────────────────────────────────────────────
    "the godfather": {
        "themes": ["Mafia & Power", "Family Betrayal", "Crime Empire",
                   "Organized Crime", "Masculine Intensity"],
        "mood_ids": [
            769,     # Goodfellas
            503,     # Casino
            111,     # Scarface
            398978,  # The Irishman
            949,     # Heat
            1422,    # The Departed
            6977,    # No Country for Old Men
            680,     # Pulp Fiction
            500,     # Reservoir Dogs
            106646,  # The Wolf of Wall Street
        ],
    },

    "godfather": {
        "themes": ["Mafia & Power", "Family Betrayal", "Crime Empire",
                   "Organized Crime", "Masculine Intensity"],
        "mood_ids": [
            769,     # Goodfellas
            503,     # Casino
            111,     # Scarface
            398978,  # The Irishman
            949,     # Heat
            1422,    # The Departed
            680,     # Pulp Fiction
            500,     # Reservoir Dogs
            106646,  # The Wolf of Wall Street
        ],
    },

    # ── Cosmic / Emotional Sci-Fi ─────────────────────────────────────────────
    "interstellar": {
        "themes": ["Existential Sci-Fi", "Cosmic Awe", "Time & Loss",
                   "Human Survival", "Philosophical Wonder"],
        "mood_ids": [
            329865,  # Arrival
            62,      # 2001: A Space Odyssey
            17431,   # Moon
            686,     # Contact
            419704,  # Ad Astra
            335984,  # Blade Runner 2049
            152601,  # Her
            38365,   # Eternal Sunshine of the Spotless Mind
            27205,   # Inception
            1895,    # Star Wars: A New Hope — removed, wrong vibe
        ],
        "mood_ids": [
            329865,  # Arrival
            62,      # 2001: A Space Odyssey
            17431,   # Moon
            686,     # Contact
            419704,  # Ad Astra
            335984,  # Blade Runner 2049
            152601,  # Her
            38365,   # Eternal Sunshine
            27205,   # Inception
            496243,  # Parasite (for thematic depth)
        ],
    },

    # ── Pulp Crime / Dialogue-Driven ─────────────────────────────────────────
    "pulp fiction": {
        "themes": ["Non-Linear Crime", "Sharp Dialogue", "Dark Humor",
                   "Pulp Aesthetic", "Stylized Violence"],
        "mood_ids": [
            500,     # Reservoir Dogs
            238,     # The Godfather
            769,     # Goodfellas
            111,     # Scarface
            949,     # Heat
            807,     # Se7en
            550,     # Fight Club
            16869,   # Inglourious Basterds
            68718,   # Django Unchained
            273481,  # The Hateful Eight
            503,     # Casino
        ],
    },

    "reservoir dogs": {
        "themes": ["Crime Heist", "Pulp Violence", "Sharp Dialogue",
                   "Male Tension", "Dark Wit"],
        "mood_ids": [
            680,     # Pulp Fiction
            807,     # Se7en
            769,     # Goodfellas
            949,     # Heat
            111,     # Scarface
            550,     # Fight Club
            16869,   # Inglourious Basterds
            68718,   # Django Unchained
            273481,  # The Hateful Eight
            503,     # Casino
        ],
    },

    # ── Psychological Crime Thriller ──────────────────────────────────────────
    "se7en": {
        "themes": ["Dark Crime Investigation", "Psychological Dread",
                   "Serial Killer", "Moral Corruption", "Disturbing Atmosphere"],
        "mood_ids": [
            274,     # Silence of the Lambs
            11324,   # Shutter Island
            1599,    # Zodiac
            146233,  # Prisoners
            210577,  # Gone Girl
            77,      # Memento
            242582,  # Nightcrawler
            103,     # Taxi Driver
            1745,    # The Prestige
            45612,   # Black Swan
        ],
    },

    "seven": {
        "themes": ["Dark Crime Investigation", "Psychological Dread",
                   "Serial Killer", "Moral Corruption"],
        "mood_ids": [
            274,     # Silence of the Lambs
            11324,   # Shutter Island
            1599,    # Zodiac
            146233,  # Prisoners
            210577,  # Gone Girl
            77,      # Memento
            242582,  # Nightcrawler
            103,     # Taxi Driver
            1745,    # The Prestige
        ],
    },

    # ── Mind-Bending / Dream Logic ────────────────────────────────────────────
    "inception": {
        "themes": ["Dream Architecture", "Mind-Bending Reality",
                   "Heist Thriller", "Emotional Core", "Layered Plot"],
        "mood_ids": [
            77,      # Memento
            1745,    # The Prestige
            157336,  # Interstellar
            329865,  # Arrival
            11324,   # Shutter Island
            210577,  # Gone Girl
            335984,  # Blade Runner 2049
            38365,   # Eternal Sunshine
            27205,   # Inception itself — skip in dedup
        ],
    },

    "memento": {
        "themes": ["Non-Linear Narrative", "Memory Loss", "Psychological Noir",
                   "Unreliable Narrator", "Mind-Bending"],
        "mood_ids": [
            27205,   # Inception
            1745,    # The Prestige
            11324,   # Shutter Island
            807,     # Se7en
            210577,  # Gone Girl
            146233,  # Prisoners
            6045,    # Oldboy
            103,     # Taxi Driver
            45612,   # Black Swan
        ],
    },

    # ── Lone Wolf / Dark Character Study ─────────────────────────────────────
    "taxi driver": {
        "themes": ["Urban Alienation", "Lone Wolf", "Psychological Descent",
                   "Dark Character Study", "Vigilante Obsession"],
        "mood_ids": [
            550,     # Fight Club
            475557,  # Joker
            242582,  # Nightcrawler
            228150,  # Drive
            1359,    # American Psycho
            807,     # Se7en
            103,     # Taxi Driver
            103,     # itself — skip in dedup
            6977,    # No Country for Old Men
            281957,  # The Revenant
            244786,  # Whiplash
        ],
    },

    "joker": {
        "themes": ["Psychological Descent", "Urban Alienation", "Anti-Hero",
                   "Mental Illness", "Social Rejection"],
        "mood_ids": [
            103,     # Taxi Driver
            550,     # Fight Club
            242582,  # Nightcrawler
            228150,  # Drive
            1359,    # American Psycho
            641,     # Requiem for a Dream
            44217,   # American History X
            475557,  # itself — skip
            281957,  # The Revenant
            244786,  # Whiplash
        ],
    },

    # ── Goodfellas / Crime Lifestyle ──────────────────────────────────────────
    "goodfellas": {
        "themes": ["Crime Lifestyle", "Rise & Fall", "Mafia Energy",
                   "Dark Glamour", "Kinetic Storytelling"],
        "mood_ids": [
            238,     # The Godfather
            503,     # Casino
            111,     # Scarface
            398978,  # The Irishman
            949,     # Heat
            1422,    # The Departed
            680,     # Pulp Fiction
            106646,  # The Wolf of Wall Street
            500,     # Reservoir Dogs
        ],
    },

    # ── Heist / Cerebral Action ───────────────────────────────────────────────
    "heat": {
        "themes": ["Heist Thriller", "Cops vs Criminals", "Male Intensity",
                   "Professional Code", "Cat and Mouse"],
        "mood_ids": [
            949,     # Heat itself
            769,     # Goodfellas
            238,     # The Godfather
            111,     # Scarface
            680,     # Pulp Fiction
            1422,    # The Departed
            6977,    # No Country for Old Men
            500,     # Reservoir Dogs
            503,     # Casino
        ],
    },

    # ── Psychological Obsession ───────────────────────────────────────────────
    "black swan": {
        "themes": ["Psychological Obsession", "Duality", "Perfectionism",
                   "Descent into Madness", "Dark Feminine"],
        "mood_ids": [
            11324,   # Shutter Island
            807,     # Se7en
            1599,    # Zodiac
            77,      # Memento
            45612,   # itself
            274,     # Silence of the Lambs
            244786,  # Whiplash
            641,     # Requiem for a Dream
            103,     # Taxi Driver
            210577,  # Gone Girl
        ],
    },

    "whiplash": {
        "themes": ["Obsessive Pursuit", "Perfectionism", "Brutal Mentorship",
                   "Psychological Pressure", "Artistic Ambition"],
        "mood_ids": [
            45612,   # Black Swan
            244786,  # itself
            37799,   # The Social Network
            496243,  # Parasite
            7551,    # There Will Be Blood
            103,     # Taxi Driver
            550,     # Fight Club
            244786,  # Whiplash
            281957,  # The Revenant
        ],
    },

    # ── Emotional Isolation / Quiet Sci-Fi ───────────────────────────────────
    "her": {
        "themes": ["Emotional Loneliness", "Futuristic Intimacy",
                   "Urban Isolation", "Melancholic Romance", "Human Connection"],
        "mood_ids": [
            38365,   # Eternal Sunshine
            157,     # Lost in Translation
            335984,  # Blade Runner 2049
            157336,  # Interstellar
            329865,  # Arrival
            152601,  # itself
            17431,   # Moon
            550,     # Fight Club
        ],
    },

    "lost in translation": {
        "themes": ["Quiet Loneliness", "Transient Connection",
                   "Urban Ennui", "Emotional Intimacy"],
        "mood_ids": [
            152601,  # Her
            38365,   # Eternal Sunshine
            157336,  # Interstellar
            329865,  # Arrival
            17431,   # Moon
            335984,  # Blade Runner 2049
        ],
    },

    # ── High-Stakes Crime Thriller ────────────────────────────────────────────
    "no country for old men": {
        "themes": ["Relentless Evil", "Fate vs Free Will", "Bleak Crime",
                   "Existential Dread", "Slow-Burn Tension"],
        "mood_ids": [
            807,     # Se7en
            274,     # Silence of the Lambs
            1599,    # Zodiac
            146233,  # Prisoners
            949,     # Heat
            769,     # Goodfellas
            550,     # Fight Club
            103,     # Taxi Driver
            7551,    # There Will Be Blood
        ],
    },

    # ── Tarantino ─────────────────────────────────────────────────────────────
    "django unchained": {
        "themes": ["Revenge", "Dark Western", "Stylized Violence",
                   "Sharp Wit", "Historical Brutality"],
        "mood_ids": [
            500,     # Reservoir Dogs
            680,     # Pulp Fiction
            16869,   # Inglourious Basterds
            273481,  # The Hateful Eight
            466272,  # Once Upon a Time in Hollywood
            24428,   # Kill Bill Vol 1
            949,     # Heat
            238,     # The Godfather
        ],
    },

    "inglourious basterds": {
        "themes": ["Wartime Revenge", "Stylized History", "Sharp Dialogue",
                   "Dark Wit", "Tension-Filled Scenes"],
        "mood_ids": [
            500,     # Reservoir Dogs
            680,     # Pulp Fiction
            68718,   # Django Unchained
            273481,  # The Hateful Eight
            466272,  # Once Upon a Time in Hollywood
            24428,   # Kill Bill Vol 1
            807,     # Se7en
        ],
    },

    "kill bill": {
        "themes": ["Revenge Thriller", "Stylized Action", "Female Fury",
                   "Genre-Blending", "Vivid Violence"],
        "mood_ids": [
            500,     # Reservoir Dogs
            680,     # Pulp Fiction
            68718,   # Django Unchained
            16869,   # Inglourious Basterds
            273481,  # The Hateful Eight
            6045,    # Oldboy
            949,     # Heat
        ],
    },

    # ── The Dark Knight ───────────────────────────────────────────────────────
    "the dark knight": {
        "themes": ["Chaos vs Order", "Moral Complexity", "Urban Crime",
                   "Iconic Villain", "Grounded Superhero"],
        "mood_ids": [
            807,     # Se7en
            550,     # Fight Club
            1422,    # The Departed
            475557,  # Joker
            949,     # Heat
            103,     # Taxi Driver
            238,     # The Godfather
            769,     # Goodfellas
            281957,  # The Revenant
        ],
    },

    "dark knight": {
        "themes": ["Chaos vs Order", "Moral Complexity", "Urban Crime",
                   "Iconic Villain", "Grounded Superhero"],
        "mood_ids": [
            807,     # Se7en
            550,     # Fight Club
            1422,    # The Departed
            475557,  # Joker
            949,     # Heat
            103,     # Taxi Driver
            238,     # The Godfather
            769,     # Goodfellas
        ],
    },

    # ── Rise and Fall / Excess ────────────────────────────────────────────────
    "the wolf of wall street": {
        "themes": ["Capitalist Excess", "Hedonism", "Rise & Fall",
                   "Dark Comedy", "Male Ego Spiral"],
        "mood_ids": [
            769,     # Goodfellas
            111,     # Scarface
            503,     # Casino
            238,     # The Godfather
            398978,  # The Irishman
            550,     # Fight Club
            37799,   # The Social Network
            106646,  # itself
            7551,    # There Will Be Blood
        ],
    },

    "scarface": {
        "themes": ["Rise & Fall", "Crime Empire", "Immigrant Ambition",
                   "Violence & Power", "Tragic Excess"],
        "mood_ids": [
            238,     # The Godfather
            769,     # Goodfellas
            503,     # Casino
            398978,  # The Irishman
            949,     # Heat
            1422,    # The Departed
            680,     # Pulp Fiction
            106646,  # The Wolf of Wall Street
        ],
    },

    # ── Slow Burn / Atmospheric ───────────────────────────────────────────────
    "drive": {
        "themes": ["Quiet Lone Wolf", "Neon Noir", "Explosive Violence",
                   "Melancholic Atmosphere", "Stylized Silence"],
        "mood_ids": [
            103,     # Taxi Driver
            242582,  # Nightcrawler
            550,     # Fight Club
            228150,  # itself
            1359,    # American Psycho
            281957,  # The Revenant
            475557,  # Joker
            807,     # Se7en
        ],
    },

    "nightcrawler": {
        "themes": ["Predatory Ambition", "Dark Satire", "Urban Predator",
                   "Psychological Manipulation", "American Nightmare"],
        "mood_ids": [
            103,     # Taxi Driver
            550,     # Fight Club
            228150,  # Drive
            475557,  # Joker
            1359,    # American Psycho
            37799,   # The Social Network
            807,     # Se7en
            242582,  # itself
        ],
    },

    # ── Parasite / Class Commentary ───────────────────────────────────────────
    "parasite": {
        "themes": ["Class Struggle", "Dark Comedy Thriller",
                   "Social Commentary", "Twisting Plot", "Korean Cinema"],
        "mood_ids": [
            496243,  # itself
            37799,   # The Social Network
            7551,    # There Will Be Blood
            550,     # Fight Club
            6977,    # No Country for Old Men
            244786,  # Whiplash
            281957,  # The Revenant
        ],
    },

    # ── Arrival / Quiet Sci-Fi ────────────────────────────────────────────────
    "arrival": {
        "themes": ["Linguistic Mystery", "Time & Grief", "First Contact",
                   "Quiet Sci-Fi", "Emotional Depth"],
        "mood_ids": [
            157336,  # Interstellar
            62,      # 2001: A Space Odyssey
            17431,   # Moon
            686,     # Contact
            335984,  # Blade Runner 2049
            152601,  # Her
            38365,   # Eternal Sunshine
            27205,   # Inception
        ],
    },

    # ── Blade Runner ─────────────────────────────────────────────────────────
    "blade runner 2049": {
        "themes": ["Neo-Noir Sci-Fi", "Identity & Humanity", "Dystopian Future",
                   "Existential Longing", "Visual Grandeur"],
        "mood_ids": [
            78,      # Blade Runner (1982)
            157336,  # Interstellar
            329865,  # Arrival
            62,      # 2001: A Space Odyssey
            17431,   # Moon
            152601,  # Her
            419704,  # Ad Astra
            335984,  # itself
        ],
    },

    # ── Social Network ────────────────────────────────────────────────────────
    "the social network": {
        "themes": ["Ambition & Betrayal", "Tech Obsession", "Sharp Dialogue",
                   "Rise & Fall", "Modern Tragedy"],
        "mood_ids": [
            550,     # Fight Club
            37799,   # itself
            7551,    # There Will Be Blood
            244786,  # Whiplash
            242582,  # Nightcrawler
            103,     # Taxi Driver
            106646,  # Wolf of Wall Street
            496243,  # Parasite
        ],
    },

    # ── Prisoners / Moral Thriller ────────────────────────────────────────────
    "prisoners": {
        "themes": ["Moral Dilemma", "Dark Investigation", "Desperate Father",
                   "Slow-Burn Thriller", "Ambiguous Justice"],
        "mood_ids": [
            807,     # Se7en
            11324,   # Shutter Island
            1599,    # Zodiac
            210577,  # Gone Girl
            77,      # Memento
            274,     # Silence of the Lambs
            6977,    # No Country for Old Men
            103,     # Taxi Driver
        ],
    },

    # ── Gone Girl ─────────────────────────────────────────────────────────────
    "gone girl": {
        "themes": ["Psychological Game", "Marriage as Warfare",
                   "Unreliable Narrator", "Dark Satire", "Twisting Mystery"],
        "mood_ids": [
            807,     # Se7en
            11324,   # Shutter Island
            1599,    # Zodiac
            77,      # Memento
            146233,  # Prisoners
            274,     # Silence of the Lambs
            210577,  # itself
            45612,   # Black Swan
        ],
    },

    # ── Shawshank / Emotional Drama ───────────────────────────────────────────
    "the shawshank redemption": {
        "themes": ["Hope & Perseverance", "Friendship in Adversity",
                   "Institutional Life", "Emotional Depth", "Classic Drama"],
        "mood_ids": [
            278,     # itself
            238,     # The Godfather
            769,     # Goodfellas
            424,     # Schindler's List
            389,     # 12 Angry Men
            1366,    # One Flew Over the Cuckoo's Nest
            13,      # Forrest Gump
            244786,  # Whiplash
        ],
    },

    "shawshank redemption": {
        "themes": ["Hope & Perseverance", "Friendship in Adversity",
                   "Classic Drama", "Emotional Depth"],
        "mood_ids": [
            238,     # The Godfather
            769,     # Goodfellas
            424,     # Schindler's List
            389,     # 12 Angry Men
            1366,    # One Flew Over the Cuckoo's Nest
            13,      # Forrest Gump
            244786,  # Whiplash
        ],
    },

}


def get_mood(movie_title: str) -> dict:
    """
    Look up curated mood data for a movie title.
    Returns {"themes": [...], "mood_ids": [...]} or empty dict if not found.

    Matching is case-insensitive and handles 'The X' vs 'X' variation.
    """
    key = movie_title.lower().strip()

    if key in CURATED:
        return CURATED[key]

    # Try without leading 'the '
    if key.startswith("the "):
        short = key[4:]
        if short in CURATED:
            return CURATED[short]

    # Try adding 'the '
    long = "the " + key
    if long in CURATED:
        return CURATED[long]

    return {}
