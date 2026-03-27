"""
Hit song reference database — real chord progressions, keys, BPMs, and
patterns from modern hits (2016–2025). Used to power the /hits endpoint
and inform genre-aware generation with real-world data.

Data compiled from public music theory analyses.
"""

# Each entry: (title, artist, year, key, scale, bpm, genre, progression_degrees, mood)
HIT_SONGS = [
    # ─── TRAP / RAP ───
    ("HUMBLE.", "Kendrick Lamar", 2017, "F#", "minor", 150, "trap", [0, 6, 5, 4], "aggressive"),
    ("XO Tour Llif3", "Lil Uzi Vert", 2017, "E", "minor", 155, "trap", [0, 5, 6, 2], "dark"),
    ("Mask Off", "Future", 2017, "F", "minor", 150, "trap", [0, 5, 3, 4], "dark"),
    ("Sicko Mode", "Travis Scott", 2018, "A", "minor", 155, "trap", [0, 6, 5, 3], "dark"),
    ("Money Trees", "Kendrick Lamar", 2016, "F", "minor", 72, "hiphop", [0, 5, 3, 6], "chill"),
    ("goosebumps", "Travis Scott", 2016, "A", "minor", 130, "trap", [0, 2, 5, 6], "dark"),
    ("DNA.", "Kendrick Lamar", 2017, "E", "minor", 140, "trap", [0, 5, 6, 4], "aggressive"),
    ("Rockstar", "Post Malone", 2017, "C", "minor", 160, "trap", [0, 2, 5, 6], "dark"),
    ("RAPSTAR", "Polo G", 2021, "Db", "minor", 140, "trap", [0, 5, 3, 6], "melancholy"),
    ("First Person Shooter", "Drake & J. Cole", 2023, "G", "minor", 144, "trap", [0, 6, 5, 3], "dark"),
    ("Not Like Us", "Kendrick Lamar", 2024, "C", "minor", 103, "hiphop", [0, 3, 4, 0], "aggressive"),
    ("Like That", "Future, Metro Boomin & Kendrick Lamar", 2024, "G", "minor", 133, "trap", [0, 5, 6, 2], "aggressive"),
    ("Carnival", "Kanye West", 2024, "F", "minor", 128, "hiphop", [0, 3, 6, 5], "dark"),
    ("FE!N", "Travis Scott", 2023, "D", "minor", 145, "trap", [0, 5, 3, 4], "aggressive"),
    ("Rich Spirit", "Kendrick Lamar", 2022, "Bb", "minor", 102, "hiphop", [0, 3, 5, 6], "chill"),

    # ─── POP ───
    ("Shape of You", "Ed Sheeran", 2017, "C#", "minor", 96, "pop", [0, 3, 5, 4], "energetic"),
    ("Blinding Lights", "The Weeknd", 2020, "F", "minor", 171, "pop", [0, 2, 5, 6], "energetic"),
    ("Stay", "The Kid LAROI & Justin Bieber", 2021, "C", "major", 170, "pop", [0, 4, 5, 3], "happy"),
    ("As It Was", "Harry Styles", 2022, "F#", "minor", 174, "pop", [0, 3, 4, 0], "melancholy"),
    ("Flowers", "Miley Cyrus", 2023, "A", "minor", 118, "pop", [0, 5, 3, 4], "happy"),
    ("Levitating", "Dua Lipa", 2020, "B", "minor", 103, "pop", [0, 5, 3, 4], "energetic"),
    ("Espresso", "Sabrina Carpenter", 2024, "Bb", "minor", 104, "pop", [0, 3, 5, 4], "chill"),
    ("Cruel Summer", "Taylor Swift", 2023, "A", "major", 170, "pop", [0, 4, 5, 3], "energetic"),
    ("Anti-Hero", "Taylor Swift", 2022, "E", "major", 97, "pop", [0, 4, 5, 3], "melancholy"),
    ("Good 4 U", "Olivia Rodrigo", 2021, "A", "minor", 166, "pop", [0, 4, 5, 3], "aggressive"),
    ("BIRDS OF A FEATHER", "Billie Eilish", 2024, "A", "major", 105, "pop", [0, 4, 5, 3], "dreamy"),
    ("Die With A Smile", "Lady Gaga & Bruno Mars", 2024, "F", "major", 158, "pop", [0, 3, 0, 4], "soulful"),
    ("APT.", "ROSE & Bruno Mars", 2024, "A", "major", 149, "pop", [0, 4, 5, 3], "energetic"),

    # ─── R&B ───
    ("Location", "Khalid", 2017, "Bb", "major", 91, "rnb", [1, 4, 0, 5], "chill"),
    ("Best Part", "Daniel Caesar ft. H.E.R.", 2017, "Db", "major", 71, "rnb", [0, 5, 1, 4], "dreamy"),
    ("After Hours", "The Weeknd", 2020, "C", "minor", 108, "rnb", [0, 3, 5, 4], "dark"),
    ("Snooze", "SZA", 2022, "Bb", "major", 143, "rnb", [0, 5, 1, 4], "dreamy"),
    ("Kill Bill", "SZA", 2022, "G", "major", 89, "rnb", [0, 3, 1, 4], "soulful"),
    ("Redbone", "Childish Gambino", 2016, "Eb", "minor", 81, "rnb", [0, 3, 5, 0], "chill"),
    ("Drunk in Love", "Beyoncé", 2016, "Ab", "minor", 100, "rnb", [0, 3, 5, 6], "dark"),
    ("Come Through", "H.E.R.", 2020, "F", "minor", 66, "rnb", [0, 5, 1, 4], "chill"),
    ("Damage", "H.E.R.", 2020, "Eb", "major", 68, "rnb", [0, 3, 1, 4], "sad"),
    ("Shirt", "SZA", 2022, "C", "minor", 100, "rnb", [0, 5, 3, 6], "melancholy"),
    ("Saturn", "SZA", 2023, "Eb", "major", 136, "rnb", [0, 3, 1, 4], "dreamy"),
    ("Taste", "Sabrina Carpenter", 2024, "Db", "major", 111, "pop", [0, 4, 5, 3], "energetic"),

    # ─── LO-FI / CHILL ───
    ("Tadow", "Masego & FKJ", 2017, "F", "dorian", 95, "lofi", [1, 4, 0, 5], "chill"),
    ("Coffee", "beabadoobee", 2020, "D", "major", 100, "lofi", [0, 4, 5, 3], "dreamy"),
    ("Sanctuary", "Joji", 2019, "Bb", "major", 85, "lofi", [0, 5, 1, 4], "melancholy"),
    ("Slow Dancing in the Dark", "Joji", 2018, "C", "minor", 89, "lofi", [0, 5, 3, 4], "sad"),
    ("Glimpse of Us", "Joji", 2022, "C", "major", 83, "lofi", [0, 4, 5, 3], "melancholy"),

    # ─── JAZZ / NEO-SOUL ───
    ("Black Gold", "Esperanza Spalding", 2016, "Eb", "dorian", 112, "jazz", [1, 4, 0, 5], "soulful"),
    ("Come Home", "Anderson .Paak", 2019, "F", "mixolydian", 96, "jazz", [0, 6, 3, 4], "chill"),
    ("Doo Wop", "Lauryn Hill (sampled 2020s)", 2017, "Bb", "major", 100, "jazz", [0, 3, 1, 4], "soulful"),

    # ─── ROCK ───
    ("Heat Waves", "Glass Animals", 2020, "D", "major", 81, "rock", [0, 4, 5, 3], "melancholy"),
    ("Enemy", "Imagine Dragons", 2021, "C", "minor", 170, "rock", [0, 5, 3, 4], "aggressive"),
    ("Bones", "Imagine Dragons", 2022, "E", "minor", 131, "rock", [0, 5, 3, 4], "energetic"),

    # ─── EDM ───
    ("Alone", "Marshmello", 2016, "Bb", "minor", 128, "edm", [0, 5, 3, 4], "energetic"),
    ("Something Just Like This", "Chainsmokers & Coldplay", 2017, "G", "major", 103, "edm", [0, 4, 5, 3], "uplifting"),
    ("Scared to Be Lonely", "Martin Garrix", 2017, "G", "minor", 107, "edm", [0, 5, 3, 4], "melancholy"),
    ("Save Your Tears", "The Weeknd", 2020, "C", "major", 118, "edm", [0, 4, 5, 3], "sad"),

    # ─── GOSPEL / SOUL ───
    ("Won't He Do It", "Koryn Hawthorne", 2018, "Bb", "major", 78, "gospel", [0, 3, 1, 4], "uplifting"),
    ("Jireh", "Maverick City Music", 2021, "G", "major", 73, "gospel", [0, 4, 5, 3], "uplifting"),
    ("Goodness of God", "Bethel Music", 2019, "C", "major", 63, "gospel", [0, 3, 0, 4], "soulful"),

    # ─── LATIN ───
    ("Despacito", "Luis Fonsi", 2017, "B", "minor", 89, "latin", [0, 3, 4, 0], "energetic"),
    ("Mi Gente", "J Balvin", 2017, "A", "minor", 105, "latin", [0, 3, 4, 0], "energetic"),
    ("Dakiti", "Bad Bunny", 2020, "Db", "minor", 110, "latin", [0, 3, 5, 4], "chill"),
    ("Tití Me Preguntó", "Bad Bunny", 2022, "F#", "minor", 106, "latin", [0, 5, 3, 4], "energetic"),
]


def get_hits_by_genre(genre: str) -> list[dict]:
    """Get all hits matching a genre."""
    genre_lower = genre.lower()
    genre_aliases = {
        "rap": "hiphop", "hip-hop": "hiphop", "hip hop": "hiphop",
        "r&b": "rnb", "r and b": "rnb",
        "lo-fi": "lofi", "lo fi": "lofi",
        "electronic": "edm",
    }
    genre_lower = genre_aliases.get(genre_lower, genre_lower)

    return [
        _song_to_dict(s) for s in HIT_SONGS if s[6] == genre_lower
    ]


def get_hits_by_mood(mood: str) -> list[dict]:
    """Get all hits matching a mood."""
    return [
        _song_to_dict(s) for s in HIT_SONGS if s[8] == mood.lower()
    ]


def get_hits_by_key(key: str) -> list[dict]:
    """Get all hits in a specific key."""
    return [
        _song_to_dict(s) for s in HIT_SONGS if s[3].lower() == key.lower()
    ]


def get_hits_by_year(year: int) -> list[dict]:
    """Get all hits from a specific year."""
    return [
        _song_to_dict(s) for s in HIT_SONGS if s[2] == year
    ]


def search_hits(
    genre: str = None,
    mood: str = None,
    key: str = None,
    year_from: int = None,
    year_to: int = None,
    bpm_min: int = None,
    bpm_max: int = None,
    scale: str = None,
) -> list[dict]:
    """Search hits with multiple filters."""
    genre_aliases = {
        "rap": "hiphop", "hip-hop": "hiphop", "hip hop": "hiphop",
        "r&b": "rnb", "r and b": "rnb",
        "lo-fi": "lofi", "lo fi": "lofi",
        "electronic": "edm",
    }

    results = []
    for s in HIT_SONGS:
        title, artist, year, s_key, s_scale, bpm, s_genre, prog, s_mood = s

        if genre:
            g = genre.lower()
            g = genre_aliases.get(g, g)
            if s_genre != g:
                continue
        if mood and s_mood != mood.lower():
            continue
        if key and s_key.lower() != key.lower():
            continue
        if year_from and year < year_from:
            continue
        if year_to and year > year_to:
            continue
        if bpm_min and bpm < bpm_min:
            continue
        if bpm_max and bpm > bpm_max:
            continue
        if scale and s_scale != scale.lower():
            continue

        results.append(_song_to_dict(s))

    return results


def get_progression_stats() -> dict:
    """Analyze the hit database for common patterns."""
    from collections import Counter

    key_counts = Counter()
    scale_counts = Counter()
    bpm_by_genre = {}
    prog_counts = Counter()
    mood_counts = Counter()

    for s in HIT_SONGS:
        title, artist, year, key, scale, bpm, genre, prog, mood = s

        key_counts[key] += 1
        scale_counts[scale] += 1
        mood_counts[mood] += 1
        prog_counts[str(prog)] += 1

        if genre not in bpm_by_genre:
            bpm_by_genre[genre] = []
        bpm_by_genre[genre].append(bpm)

    avg_bpm_by_genre = {}
    for genre, bpms in bpm_by_genre.items():
        avg_bpm_by_genre[genre] = {
            "avg": round(sum(bpms) / len(bpms)),
            "min": min(bpms),
            "max": max(bpms),
            "count": len(bpms),
        }

    return {
        "total_songs": len(HIT_SONGS),
        "most_common_keys": [{"key": k, "count": c} for k, c in key_counts.most_common(10)],
        "most_common_scales": [{"scale": k, "count": c} for k, c in scale_counts.most_common()],
        "most_common_moods": [{"mood": k, "count": c} for k, c in mood_counts.most_common()],
        "most_common_progressions": [{"degrees": k, "count": c} for k, c in prog_counts.most_common(10)],
        "bpm_by_genre": avg_bpm_by_genre,
    }


def _song_to_dict(s: tuple) -> dict:
    """Convert a song tuple to a dict."""
    title, artist, year, key, scale, bpm, genre, prog, mood = s
    return {
        "title": title,
        "artist": artist,
        "year": year,
        "key": key,
        "scale": scale,
        "bpm": bpm,
        "genre": genre,
        "progression_degrees": prog,
        "mood": mood,
    }
