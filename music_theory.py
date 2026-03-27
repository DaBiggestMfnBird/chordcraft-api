"""
Music theory engine for chord progression generation.
Handles scales, chords, and progression patterns across genres.
"""

import random
from typing import Optional

# All 12 notes
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Enharmonic mappings for flat keys
FLAT_TO_SHARP = {
    "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#",
    "Ab": "G#", "Bb": "A#", "Cb": "B",
}

SHARP_TO_FLAT = {v: k for k, v in FLAT_TO_SHARP.items()}

# Notes displayed with flats instead of sharps
NOTES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def uses_flats(key: str) -> bool:
    """Determine if a key should display notes as flats."""
    clean = key.strip()
    # If the user typed a flat (e.g., Bb, Eb), use flats
    if "b" in clean[1:]:  # skip first char to avoid matching B natural
        return True
    # F major conventionally uses flats
    if clean in ("F", "f"):
        return True
    return False

# Scale intervals (semitones from root)
SCALE_INTERVALS = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "minor":            [0, 2, 3, 5, 7, 8, 10],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "locrian":          [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
}

# Chord quality definitions (intervals from root in semitones)
CHORD_TYPES = {
    "maj":      [0, 4, 7],
    "min":      [0, 3, 7],
    "dim":      [0, 3, 6],
    "aug":      [0, 4, 8],
    "maj7":     [0, 4, 7, 11],
    "min7":     [0, 3, 7, 10],
    "dom7":     [0, 4, 7, 10],
    "dim7":     [0, 3, 6, 9],
    "half_dim7": [0, 3, 6, 10],
    "min_maj7": [0, 3, 7, 11],
    "add9":     [0, 4, 7, 14],
    "sus2":     [0, 2, 7],
    "sus4":     [0, 5, 7],
    "6":        [0, 4, 7, 9],
    "min6":     [0, 3, 7, 9],
    "9":        [0, 4, 7, 10, 14],
    "min9":     [0, 3, 7, 10, 14],
    "maj9":     [0, 4, 7, 11, 14],
    "11":       [0, 4, 7, 10, 14, 17],
    "13":       [0, 4, 7, 10, 14, 21],
}

# Chord qualities for each scale degree (7-note diatonic scales)
DIATONIC_CHORDS = {
    "major":          ["maj", "min", "min", "maj", "maj", "min", "dim"],
    "minor":          ["min", "dim", "maj", "min", "min", "maj", "maj"],
    "dorian":         ["min", "min", "maj", "maj", "min", "dim", "maj"],
    "mixolydian":     ["maj", "min", "dim", "maj", "min", "min", "maj"],
    "phrygian":       ["min", "maj", "maj", "min", "dim", "maj", "min"],
    "lydian":         ["maj", "maj", "min", "dim", "maj", "min", "min"],
    "harmonic_minor": ["min", "dim", "aug", "min", "maj", "maj", "dim"],
}

DIATONIC_7TH_CHORDS = {
    "major":          ["maj7", "min7", "min7", "maj7", "dom7", "min7", "half_dim7"],
    "minor":          ["min7", "half_dim7", "maj7", "min7", "min7", "maj7", "dom7"],
    "dorian":         ["min7", "min7", "maj7", "dom7", "min7", "half_dim7", "maj7"],
    "mixolydian":     ["dom7", "min7", "half_dim7", "maj7", "min7", "min7", "maj7"],
    "phrygian":       ["min7", "maj7", "dom7", "min7", "half_dim7", "maj7", "min7"],
    "lydian":         ["maj7", "maj7", "min7", "half_dim7", "dom7", "min7", "min7"],
    "harmonic_minor": ["min_maj7", "half_dim7", "aug", "min7", "dom7", "maj7", "dim7"],
}

# Genre production suggestions (BPM ranges, common keys, recommended scales)
GENRE_SUGGESTIONS = {
    "pop": {
        "bpm_range": [100, 130],
        "common_keys": ["C", "G", "D", "A", "F"],
        "recommended_scales": ["major", "mixolydian"],
        "tip": "Pop thrives on simple, catchy progressions. The I-V-vi-IV is the most used progression in modern pop.",
    },
    "rnb": {
        "bpm_range": [60, 100],
        "common_keys": ["Eb", "Ab", "Bb", "F", "Db"],
        "recommended_scales": ["major", "dorian", "mixolydian"],
        "tip": "Use 7th and 9th chords for that smooth R&B feel. Flat keys sound warmer on keys/pads.",
    },
    "trap": {
        "bpm_range": [130, 170],
        "common_keys": ["C", "F", "G", "D", "A"],
        "recommended_scales": ["minor", "phrygian", "harmonic_minor"],
        "tip": "Trap almost always uses minor keys. Half-time feel at 140+ BPM is standard. Phrygian adds a dark, exotic flavor.",
    },
    "hiphop": {
        "bpm_range": [75, 115],
        "common_keys": ["C", "G", "D", "F", "Bb"],
        "recommended_scales": ["minor", "dorian", "pentatonic_minor"],
        "tip": "Boom bap sits around 85-95 BPM. Minor keys dominate. Dorian gives that jazzy old-school feel.",
    },
    "jazz": {
        "bpm_range": [60, 200],
        "common_keys": ["F", "Bb", "Eb", "Ab", "C"],
        "recommended_scales": ["major", "dorian", "mixolydian", "lydian"],
        "tip": "Jazz lives in flat keys. Always use 7th chords minimum. The ii-V-I is the foundation of jazz harmony.",
    },
    "lofi": {
        "bpm_range": [70, 90],
        "common_keys": ["F", "C", "G", "Eb", "Bb"],
        "recommended_scales": ["major", "dorian", "lydian"],
        "tip": "Keep it between 75-85 BPM for that classic lofi feel. 7th and 9th chords are essential. Lydian adds dreaminess.",
    },
    "rock": {
        "bpm_range": [100, 160],
        "common_keys": ["E", "A", "D", "G", "C"],
        "recommended_scales": ["major", "minor", "pentatonic_minor", "blues"],
        "tip": "Guitar-friendly keys (E, A, D, G) work best. Power chords and pentatonic riffs define the genre.",
    },
    "edm": {
        "bpm_range": [120, 150],
        "common_keys": ["C", "A", "F", "G", "D"],
        "recommended_scales": ["minor", "major", "harmonic_minor"],
        "tip": "House is 120-128 BPM, dubstep 140-150, drum & bass 170-180. Minor keys hit harder on drops.",
    },
    "gospel": {
        "bpm_range": [70, 130],
        "common_keys": ["C", "Db", "Eb", "F", "Ab"],
        "recommended_scales": ["major", "dorian", "mixolydian"],
        "tip": "Gospel loves flat keys and rich extended chords. The IV-I movement is sacred. Always try 7ths and 9ths.",
    },
    "latin": {
        "bpm_range": [80, 130],
        "common_keys": ["C", "G", "D", "A", "F"],
        "recommended_scales": ["major", "minor", "phrygian", "harmonic_minor"],
        "tip": "Phrygian mode gives that flamenco sound. Harmonic minor works for salsa. Keep rhythms syncopated.",
    },
}

# Roman numeral labels
ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII"]

# Genre-specific progression patterns (using 0-indexed scale degrees)
GENRE_PROGRESSIONS = {
    "pop": [
        [0, 4, 5, 3],      # I-V-vi-IV
        [0, 3, 4, 4],      # I-IV-V-V
        [0, 5, 3, 4],      # I-vi-IV-V
        [0, 3, 0, 4],      # I-IV-I-V
        [0, 5, 4, 3],      # I-vi-V-IV
    ],
    "rnb": [
        [0, 3, 4, 0],      # I-IV-V-I (with 7ths)
        [1, 4, 0, 0],      # ii-V-I-I
        [0, 5, 1, 4],      # I-vi-ii-V
        [2, 5, 1, 4],      # iii-vi-ii-V
        [0, 3, 1, 4],      # I-IV-ii-V
    ],
    "trap": [
        [0, 5, 3, 4],      # i-VI-iv-v (minor)
        [0, 2, 5, 4],      # i-III-VI-v
        [0, 6, 5, 4],      # i-VII-VI-v
        [0, 5, 6, 4],      # i-VI-VII-v
        [0, 2, 3, 6],      # i-III-iv-VII
    ],
    "hiphop": [
        [0, 3, 4, 0],      # i-iv-v-i (minor)
        [0, 5, 3, 6],      # i-VI-iv-VII
        [0, 6, 5, 4],      # i-VII-VI-v
        [0, 2, 5, 4],      # i-III-VI-v
        [0, 3, 6, 5],      # i-iv-VII-VI
    ],
    "jazz": [
        [1, 4, 0, 0],      # ii-V-I-I
        [0, 5, 1, 4],      # I-vi-ii-V
        [2, 5, 1, 4],      # iii-vi-ii-V
        [0, 3, 1, 4],      # I-IV-ii-V
        [0, 1, 2, 3],      # I-ii-iii-IV
    ],
    "lofi": [
        [1, 4, 0, 5],      # ii-V-I-vi
        [0, 5, 1, 4],      # I-vi-ii-V
        [2, 5, 1, 4],      # iii-vi-ii-V
        [0, 3, 1, 4],      # I-IV-ii-V
        [0, 2, 5, 3],      # I-iii-vi-IV
    ],
    "rock": [
        [0, 3, 4, 3],      # I-IV-V-IV
        [0, 4, 5, 3],      # I-V-vi-IV
        [0, 3, 5, 4],      # I-IV-vi-V
        [0, 5, 3, 4],      # I-vi-IV-V
        [0, 2, 3, 4],      # I-iii-IV-V
    ],
    "edm": [
        [0, 4, 5, 3],      # I-V-vi-IV
        [5, 3, 0, 4],      # vi-IV-I-V
        [0, 5, 3, 4],      # I-vi-IV-V
        [0, 3, 5, 4],      # I-IV-vi-V
    ],
    "gospel": [
        [0, 3, 1, 4],      # I-IV-ii-V
        [0, 5, 1, 4],      # I-vi-ii-V
        [3, 0, 1, 4],      # IV-I-ii-V
        [0, 3, 4, 0],      # I-IV-V-I
        [2, 5, 1, 4],      # iii-vi-ii-V
    ],
    "latin": [
        [0, 3, 4, 0],      # I-IV-V-I
        [0, 3, 1, 4],      # I-IV-ii-V
        [0, 5, 1, 4],      # I-vi-ii-V
        [1, 4, 0, 0],      # ii-V-I-I
    ],
}

# Mood to scale/genre mapping
MOOD_MAP = {
    "happy":      {"scales": ["major", "lydian", "mixolydian"], "genres": ["pop", "edm"]},
    "sad":        {"scales": ["minor", "phrygian"], "genres": ["lofi", "rnb"]},
    "dark":       {"scales": ["minor", "phrygian", "harmonic_minor"], "genres": ["trap", "hiphop"]},
    "chill":      {"scales": ["dorian", "major", "pentatonic_major"], "genres": ["lofi", "rnb"]},
    "aggressive":  {"scales": ["minor", "phrygian", "locrian"], "genres": ["trap", "rock"]},
    "dreamy":     {"scales": ["lydian", "major", "pentatonic_major"], "genres": ["lofi", "edm"]},
    "soulful":    {"scales": ["dorian", "mixolydian", "minor"], "genres": ["rnb", "gospel"]},
    "energetic":  {"scales": ["major", "mixolydian"], "genres": ["edm", "pop", "rock"]},
    "melancholy": {"scales": ["minor", "harmonic_minor", "dorian"], "genres": ["lofi", "jazz"]},
    "uplifting":  {"scales": ["major", "lydian"], "genres": ["gospel", "pop", "edm"]},
}


def normalize_note(note: str) -> str:
    """Convert a note name to its sharp equivalent (e.g., Bb -> A#)."""
    note = note.strip().capitalize()
    if len(note) > 1:
        note = note[0].upper() + note[1:]
    return FLAT_TO_SHARP.get(note, note)


def get_note_index(note: str) -> int:
    """Get the index of a note in the chromatic scale."""
    if not note or not note.strip():
        raise ValueError("Key is required. Use a note like C, F#, Bb, etc.")
    n = normalize_note(note)
    if n not in NOTES:
        raise ValueError(f"Unknown note: {note}. Valid notes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B (or flats: Db, Eb, Gb, Ab, Bb)")
    return NOTES.index(n)


def get_scale(root: str, scale_type: str, use_flats: bool = False) -> list[str]:
    """Get all notes in a scale."""
    if scale_type not in SCALE_INTERVALS:
        raise ValueError(f"Unknown scale: {scale_type}. Available: {list(SCALE_INTERVALS.keys())}")
    root_idx = get_note_index(root)
    intervals = SCALE_INTERVALS[scale_type]
    note_list = NOTES_FLAT if use_flats else NOTES
    return [note_list[(root_idx + i) % 12] for i in intervals]


def get_chord_notes(root: str, chord_type: str, use_flats: bool = False) -> list[str]:
    """Get the notes in a chord."""
    if chord_type not in CHORD_TYPES:
        raise ValueError(f"Unknown chord type: {chord_type}. Available: {list(CHORD_TYPES.keys())}")
    root_idx = get_note_index(root)
    intervals = CHORD_TYPES[chord_type]
    note_list = NOTES_FLAT if use_flats else NOTES
    return [note_list[(root_idx + i) % 12] for i in intervals]


def get_chord_midi_notes(root: str, chord_type: str, octave: int = 4, inversion: int = 0) -> list[int]:
    """Get MIDI note numbers for a chord, with optional inversion."""
    root_idx = get_note_index(root)
    base_midi = 12 * (octave + 1) + root_idx  # C4 = MIDI 60
    intervals = CHORD_TYPES[chord_type]
    notes = [base_midi + i for i in intervals]

    # Apply inversion: move the lowest N notes up an octave
    inv = min(inversion, len(notes) - 1)
    for i in range(inv):
        notes[i] += 12

    return sorted(notes)


def get_inversion_label(inversion: int) -> str:
    """Get a human-readable inversion label."""
    labels = {0: "root position", 1: "1st inversion", 2: "2nd inversion", 3: "3rd inversion"}
    return labels.get(inversion, f"{inversion}th inversion")


def format_chord_name(root: str, quality: str) -> str:
    """Format a chord name the way musicians actually write them."""
    display_map = {
        "maj": "",
        "min": "m",
        "dim": "dim",
        "aug": "aug",
        "maj7": "maj7",
        "min7": "m7",
        "dom7": "7",
        "dim7": "dim7",
        "half_dim7": "m7b5",
        "min_maj7": "mMaj7",
        "add9": "add9",
        "sus2": "sus2",
        "sus4": "sus4",
        "6": "6",
        "min6": "m6",
        "9": "9",
        "min9": "m9",
        "maj9": "maj9",
        "11": "11",
        "13": "13",
    }
    suffix = display_map.get(quality, quality)
    return f"{root}{suffix}"


def get_roman_numeral(degree: int, quality: str) -> str:
    """Get roman numeral notation for a chord."""
    numeral = ROMAN_NUMERALS[degree]
    minor_qualities = {"min", "min7", "min9", "min_maj7", "dim", "dim7", "half_dim7", "min6"}
    if quality in minor_qualities:
        numeral = numeral.lower()
    suffix_map = {
        "maj": "", "min": "", "dim": "°", "aug": "+",
        "maj7": "maj7", "min7": "7", "dom7": "7", "dim7": "°7",
        "half_dim7": "ø7", "min_maj7": "mM7",
        "sus2": "sus2", "sus4": "sus4",
        "add9": "add9", "9": "9", "min9": "9", "maj9": "maj9",
    }
    suffix = suffix_map.get(quality, quality)
    return f"{numeral}{suffix}"


def generate_progression(
    key: str,
    scale_type: Optional[str] = None,
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    num_chords: int = 4,
    use_7ths: bool = False,
    seed: Optional[int] = None,
) -> dict:
    """Generate a chord progression based on parameters."""
    # Use a local Random instance so concurrent requests don't interfere
    rng = random.Random(seed) if seed is not None else random.Random()

    # Resolve mood to scale and genre if provided
    if mood:
        mood_lower = mood.lower()
        if mood_lower not in MOOD_MAP:
            raise ValueError(f"Unknown mood: {mood}. Available: {list(MOOD_MAP.keys())}")
        mood_info = MOOD_MAP[mood_lower]
        if not scale_type:
            scale_type = rng.choice(mood_info["scales"])
        if not genre:
            genre = rng.choice(mood_info["genres"])

    # Defaults
    if not scale_type:
        scale_type = "major"
    if not genre:
        genre = "pop"

    scale_type = scale_type.lower()
    genre = genre.lower()

    # Genre aliases so common names all work
    genre_aliases = {
        "rap": "hiphop",
        "hip-hop": "hiphop",
        "hip hop": "hiphop",
        "r&b": "rnb",
        "r and b": "rnb",
        "lo-fi": "lofi",
        "lo fi": "lofi",
        "electronic": "edm",
    }
    genre = genre_aliases.get(genre, genre)

    if genre not in GENRE_PROGRESSIONS:
        raise ValueError(f"Unknown genre: {genre}. Available: {list(GENRE_PROGRESSIONS.keys())}")

    # Determine flat/sharp display based on user's key input
    flats = uses_flats(key)

    # Get scale notes
    scale = get_scale(key, scale_type, use_flats=flats)

    # Pick a progression pattern
    patterns = GENRE_PROGRESSIONS[genre]
    pattern = rng.choice(patterns)

    # If num_chords differs from pattern length, adjust
    if num_chords < len(pattern):
        pattern = pattern[:num_chords]
    elif num_chords > len(pattern):
        # Repeat/extend the pattern
        extended = []
        while len(extended) < num_chords:
            extended.extend(pattern)
        pattern = extended[:num_chords]

    # Determine chord quality lookup
    quality_source = scale_type
    if scale_type in ("pentatonic_major", "pentatonic_minor", "blues", "melodic_minor"):
        # Fall back to parent scale for chord qualities
        quality_source = "major" if scale_type == "pentatonic_major" else "minor"

    if quality_source not in DIATONIC_CHORDS:
        quality_source = "major"

    if use_7ths and quality_source in DIATONIC_7TH_CHORDS:
        chord_qualities = DIATONIC_7TH_CHORDS[quality_source]
    else:
        chord_qualities = DIATONIC_CHORDS[quality_source]

    # Build the full scale for degree lookup (always use 7-note parent)
    parent_scale_type = quality_source
    full_scale = get_scale(key, parent_scale_type, use_flats=flats)

    # Build chords
    chords = []
    for degree in pattern:
        degree = degree % len(full_scale)
        root = full_scale[degree]
        quality = chord_qualities[degree]
        notes = get_chord_notes(root, quality, use_flats=flats)
        midi = get_chord_midi_notes(root, quality)
        roman = get_roman_numeral(degree, quality)
        chords.append({
            "root": root,
            "quality": quality,
            "name": format_chord_name(root, quality),
            "roman_numeral": roman,
            "notes": notes,
            "midi_notes": midi,
            "degree": degree + 1,
        })

    return {
        "key": key,
        "scale": scale_type,
        "genre": genre,
        "mood": mood,
        "use_7ths": use_7ths,
        "scale_notes": scale,
        "chords": chords,
        "progression_label": " - ".join(c["roman_numeral"] for c in chords),
    }


def get_all_chords_in_key(key: str, scale_type: str = "major", use_7ths: bool = False) -> list[dict]:
    """Get all diatonic chords in a given key."""
    quality_source = scale_type
    if scale_type in ("pentatonic_major", "pentatonic_minor", "blues", "melodic_minor"):
        quality_source = "major" if scale_type == "pentatonic_major" else "minor"
    if quality_source not in DIATONIC_CHORDS:
        quality_source = "major"

    if use_7ths and quality_source in DIATONIC_7TH_CHORDS:
        chord_qualities = DIATONIC_7TH_CHORDS[quality_source]
    else:
        chord_qualities = DIATONIC_CHORDS[quality_source]

    flats = uses_flats(key)
    full_scale = get_scale(key, quality_source, use_flats=flats)
    chords = []
    for i, (root, quality) in enumerate(zip(full_scale, chord_qualities)):
        notes = get_chord_notes(root, quality, use_flats=flats)
        midi = get_chord_midi_notes(root, quality)
        roman = get_roman_numeral(i, quality)
        chords.append({
            "root": root,
            "quality": quality,
            "name": format_chord_name(root, quality),
            "roman_numeral": roman,
            "notes": notes,
            "midi_notes": midi,
            "degree": i + 1,
        })
    return chords
