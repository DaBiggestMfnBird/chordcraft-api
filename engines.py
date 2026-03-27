"""
Advanced music engines — Voice Leading, Song Structure, and Melody Generation.
These are the features that make ChordCraft stand out.
"""

import random
from typing import Optional

from music_theory import (
    NOTES,
    SCALE_INTERVALS,
    GENRE_SUGGESTIONS,
    GENRE_PROGRESSIONS,
    MOOD_MAP,
    CHORD_TYPES,
    get_scale,
    get_chord_midi_notes,
    get_chord_notes,
    generate_progression,
    uses_flats,
    format_chord_name,
)


# ═══════════════════════════════════════════════════════════════
#  VOICE LEADING ENGINE
#  Optimizes how chords connect — minimizes note movement
#  between consecutive chords for smooth, professional voicings
# ═══════════════════════════════════════════════════════════════

def _note_to_midi(note: str, octave: int = 4) -> int:
    """Convert a note name to MIDI number."""
    sharp_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    }
    return 12 * (octave + 1) + sharp_map.get(note, 0)


def _midi_to_note(midi: int, use_flats: bool = False) -> str:
    """Convert MIDI number back to note name."""
    sharps = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    flats = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    names = flats if use_flats else sharps
    return names[midi % 12]


def _voice_lead_pair(prev_voicing: list[int], next_chord_notes: list[int]) -> list[int]:
    """
    Given the previous chord voicing (MIDI notes) and the pitch classes
    of the next chord, find the voicing of the next chord that minimizes
    total voice movement (sum of semitone distances).
    """
    # Generate candidate voicings by placing each note in nearby octaves
    candidates = []
    for note in next_chord_notes:
        pitch_class = note % 12
        options = []
        for octave_midi in range(36, 84):  # C2 to B5
            if octave_midi % 12 == pitch_class:
                options.append(octave_midi)
        candidates.append(options)

    # Find the voicing with minimum total movement
    best_voicing = None
    best_cost = float("inf")

    def _search(depth, current_voicing):
        nonlocal best_voicing, best_cost

        if depth == len(candidates):
            # Calculate cost: sum of absolute distances to nearest prev note
            cost = 0
            for i, note in enumerate(current_voicing):
                if i < len(prev_voicing):
                    cost += abs(note - prev_voicing[i])
                else:
                    # Extra voice: penalize distance from center
                    cost += abs(note - 60)
            if cost < best_cost:
                best_cost = cost
                best_voicing = list(current_voicing)
            return

        for option in candidates[depth]:
            current_voicing.append(option)
            _search(depth + 1, current_voicing)
            current_voicing.pop()

    _search(0, [])
    return sorted(best_voicing) if best_voicing else next_chord_notes


def apply_voice_leading(chords: list[dict], use_flats: bool = False) -> list[dict]:
    """
    Apply voice leading optimization to a chord progression.
    Returns the chords with optimized MIDI voicings and voice movement analysis.
    """
    if not chords:
        return []

    result = []
    prev_voicing = None

    for i, chord in enumerate(chords):
        raw_midi = chord["midi_notes"]

        if prev_voicing is None:
            # First chord: use as-is, centered around middle C
            optimized = sorted(raw_midi)
        else:
            optimized = _voice_lead_pair(prev_voicing, raw_midi)

        # Calculate movement from previous chord
        movement = 0
        voice_motion = []
        if prev_voicing and i > 0:
            for j in range(min(len(prev_voicing), len(optimized))):
                diff = optimized[j] - prev_voicing[j]
                movement += abs(diff)
                direction = "up" if diff > 0 else "down" if diff < 0 else "held"
                voice_motion.append({
                    "voice": j + 1,
                    "from": prev_voicing[j],
                    "to": optimized[j],
                    "semitones": abs(diff),
                    "direction": direction,
                })

        chord_result = {
            "root": chord["root"],
            "quality": chord["quality"],
            "name": chord["name"],
            "roman_numeral": chord["roman_numeral"],
            "original_midi": raw_midi,
            "voiced_midi": optimized,
            "voiced_notes": [_midi_to_note(n, use_flats) for n in optimized],
            "total_movement": movement,
        }

        if voice_motion:
            chord_result["voice_motion"] = voice_motion

        result.append(chord_result)
        prev_voicing = optimized

    # Summary stats
    total_movement = sum(c["total_movement"] for c in result)
    avg_movement = total_movement / max(len(result) - 1, 1)

    if avg_movement <= 3:
        smoothness = "ultra smooth"
    elif avg_movement <= 6:
        smoothness = "smooth"
    elif avg_movement <= 10:
        smoothness = "moderate"
    else:
        smoothness = "jumpy"

    return {
        "chords": result,
        "total_movement_semitones": total_movement,
        "avg_movement_per_change": round(avg_movement, 1),
        "smoothness_rating": smoothness,
    }


# ═══════════════════════════════════════════════════════════════
#  SONG STRUCTURE ENGINE
#  Generates full song blueprints with sections, keys, energy
#  levels, and chord progressions for each part
# ═══════════════════════════════════════════════════════════════

# Common song structures by genre
SONG_STRUCTURES = {
    "pop": {
        "sections": ["intro", "verse", "prechorus", "chorus", "verse", "prechorus", "chorus", "bridge", "chorus", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "prechorus": 4, "chorus": 8, "bridge": 4, "outro": 4},
    },
    "trap": {
        "sections": ["intro", "verse", "hook", "verse", "hook", "bridge", "hook", "outro"],
        "section_bars": {"intro": 4, "verse": 16, "hook": 8, "bridge": 8, "outro": 4},
    },
    "hiphop": {
        "sections": ["intro", "verse", "hook", "verse", "hook", "verse", "hook", "outro"],
        "section_bars": {"intro": 4, "verse": 16, "hook": 8, "outro": 4},
    },
    "rnb": {
        "sections": ["intro", "verse", "prechorus", "chorus", "verse", "prechorus", "chorus", "bridge", "chorus", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "prechorus": 4, "chorus": 8, "bridge": 8, "outro": 4},
    },
    "jazz": {
        "sections": ["head", "solo_a", "solo_b", "solo_a", "head", "outro"],
        "section_bars": {"head": 8, "solo_a": 8, "solo_b": 8, "outro": 4},
    },
    "lofi": {
        "sections": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "chorus": 8, "bridge": 4, "outro": 4},
    },
    "rock": {
        "sections": ["intro", "verse", "chorus", "verse", "chorus", "solo", "chorus", "chorus", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "chorus": 8, "solo": 8, "outro": 4},
    },
    "edm": {
        "sections": ["intro", "buildup", "drop", "breakdown", "buildup", "drop", "outro"],
        "section_bars": {"intro": 8, "buildup": 8, "drop": 16, "breakdown": 8, "outro": 8},
    },
    "gospel": {
        "sections": ["intro", "verse", "chorus", "verse", "chorus", "bridge", "vamp", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "chorus": 8, "bridge": 4, "vamp": 8, "outro": 4},
    },
    "latin": {
        "sections": ["intro", "verse", "chorus", "verse", "chorus", "montuno", "chorus", "outro"],
        "section_bars": {"intro": 4, "verse": 8, "chorus": 8, "montuno": 8, "outro": 4},
    },
}

# Energy levels for common section types (0-100)
SECTION_ENERGY = {
    "intro": 20,
    "verse": 40,
    "prechorus": 60,
    "chorus": 85,
    "hook": 85,
    "bridge": 50,
    "outro": 25,
    "buildup": 70,
    "drop": 100,
    "breakdown": 30,
    "solo": 75,
    "solo_a": 70,
    "solo_b": 80,
    "head": 60,
    "vamp": 90,
    "montuno": 80,
}

# Production notes per section
SECTION_TIPS = {
    "intro": "Set the mood. Strip it back — just the main instrument or a filtered loop.",
    "verse": "Tell the story. Keep it rhythmic but leave room for vocals.",
    "prechorus": "Build tension. Add layers, risers, or change the rhythm.",
    "chorus": "This is the payoff. Full energy, all elements hitting.",
    "hook": "Make it memorable. The hook should stick in your head after one listen.",
    "bridge": "Contrast. Change the feel — different chords, different rhythm, different energy.",
    "outro": "Wind it down. Strip layers back out or fade.",
    "buildup": "Tension and anticipation. Risers, snare rolls, filter sweeps.",
    "drop": "Maximum impact. Everything hits at once. Make it bounce.",
    "breakdown": "Pull back. Let the track breathe before the next build.",
    "solo": "Let one instrument shine. Keep the backing groove locked in.",
    "solo_a": "First solo round — establish the theme and build.",
    "solo_b": "Second solo — push further, more intensity.",
    "head": "State the main melody/theme. Clean and clear.",
    "vamp": "Repeat and build. Let the energy rise with each pass. Ad libs welcome.",
    "montuno": "Call and response. Lock into the groove and let it ride.",
}


def generate_song_structure(
    key: str,
    genre: str = "pop",
    mood: Optional[str] = None,
    scale: Optional[str] = None,
    bpm: Optional[int] = None,
    use_7ths: bool = False,
    seed: Optional[int] = None,
) -> dict:
    """Generate a full song structure with sections, progressions, and energy mapping."""
    rng = random.Random(seed) if seed is not None else random.Random()

    genre_lower = genre.lower()
    genre_aliases = {
        "rap": "hiphop", "hip-hop": "hiphop", "hip hop": "hiphop",
        "r&b": "rnb", "r and b": "rnb",
        "lo-fi": "lofi", "lo fi": "lofi",
        "electronic": "edm",
    }
    genre_lower = genre_aliases.get(genre_lower, genre_lower)

    if genre_lower not in SONG_STRUCTURES:
        raise ValueError(f"Unknown genre: {genre}. Available: {list(SONG_STRUCTURES.keys())}")

    structure_template = SONG_STRUCTURES[genre_lower]

    # Resolve scale from mood if needed
    if mood and not scale:
        mood_lower = mood.lower()
        if mood_lower in MOOD_MAP:
            scale = rng.choice(MOOD_MAP[mood_lower]["scales"])
    if not scale:
        # Pick genre-appropriate default
        suggestions = GENRE_SUGGESTIONS.get(genre_lower, {})
        rec_scales = suggestions.get("recommended_scales", ["minor"])
        scale = rng.choice(rec_scales)

    # Resolve BPM
    if not bpm:
        suggestions = GENRE_SUGGESTIONS.get(genre_lower, {})
        bpm_range = suggestions.get("bpm_range", [100, 130])
        bpm = rng.randint(bpm_range[0], bpm_range[1])

    flats = uses_flats(key)

    # Generate a progression for each unique section type
    section_types = list(set(structure_template["sections"]))
    section_progressions = {}

    for section_type in section_types:
        prog = generate_progression(
            key=key,
            scale_type=scale,
            genre=genre_lower,
            mood=mood,
            num_chords=4,
            use_7ths=use_7ths,
        )
        section_progressions[section_type] = prog

    # Build the full song
    sections = []
    total_bars = 0

    for section_name in structure_template["sections"]:
        bars = structure_template["section_bars"].get(section_name, 8)
        energy = SECTION_ENERGY.get(section_name, 50)
        tip = SECTION_TIPS.get(section_name, "")
        prog = section_progressions[section_name]

        sections.append({
            "section": section_name,
            "bars": bars,
            "energy": energy,
            "progression": prog["progression_label"],
            "chords": [
                {"name": c["name"], "roman_numeral": c["roman_numeral"]}
                for c in prog["chords"]
            ],
            "tip": tip,
        })
        total_bars += bars

    # Calculate duration
    beats_per_bar = 4
    total_beats = total_bars * beats_per_bar
    duration_seconds = (total_beats / bpm) * 60
    duration_min = int(duration_seconds // 60)
    duration_sec = int(duration_seconds % 60)

    # Build energy curve data
    energy_curve = []
    bar_position = 0
    for s in sections:
        energy_curve.append({
            "bar": bar_position,
            "section": s["section"],
            "energy": s["energy"],
        })
        bar_position += s["bars"]

    return {
        "key": key,
        "scale": scale,
        "genre": genre_lower,
        "mood": mood,
        "bpm": bpm,
        "time_signature": "4/4",
        "total_bars": total_bars,
        "estimated_duration": f"{duration_min}:{duration_sec:02d}",
        "sections": sections,
        "energy_curve": energy_curve,
        "section_count": len(sections),
        "unique_sections": len(section_types),
    }


# ═══════════════════════════════════════════════════════════════
#  MELODY ENGINE
#  Generates melodies that fit over chord progressions using
#  scale-aware patterns, rhythm generation, and contour shaping
# ═══════════════════════════════════════════════════════════════

# Melodic contour shapes
CONTOUR_SHAPES = {
    "ascending": [0, 1, 2, 3, 4, 5, 6, 7],
    "descending": [7, 6, 5, 4, 3, 2, 1, 0],
    "arch": [0, 2, 4, 6, 7, 5, 3, 1],
    "valley": [7, 5, 3, 1, 0, 2, 4, 6],
    "wave": [0, 3, 1, 4, 2, 5, 3, 6],
    "zigzag": [0, 4, 1, 5, 2, 6, 3, 7],
    "peak": [0, 1, 3, 7, 6, 4, 2, 0],
    "flat": [3, 4, 3, 4, 3, 4, 3, 4],
}

# Rhythm patterns (1 = note on, 0 = rest, 0.5 = shorter note)
RHYTHM_PATTERNS = {
    "simple": [1, 0, 1, 0, 1, 0, 1, 0],
    "syncopated": [1, 0, 0, 1, 0, 1, 0, 0],
    "driving": [1, 1, 1, 1, 1, 1, 1, 1],
    "sparse": [1, 0, 0, 0, 1, 0, 0, 0],
    "dotted": [1, 0, 0, 1, 0, 0, 1, 0],
    "offbeat": [0, 1, 0, 1, 0, 1, 0, 1],
    "trap_hats": [1, 0, 1, 1, 0, 1, 1, 0],
    "bounce": [1, 0, 1, 0, 0, 1, 0, 1],
}

# Genre-appropriate melody styles
GENRE_MELODY_STYLES = {
    "pop": {"contours": ["arch", "wave"], "rhythms": ["simple", "syncopated"], "range_octaves": 1.5, "prefer_chord_tones": 0.6},
    "trap": {"contours": ["flat", "descending"], "rhythms": ["trap_hats", "sparse"], "range_octaves": 1, "prefer_chord_tones": 0.7},
    "hiphop": {"contours": ["wave", "flat"], "rhythms": ["syncopated", "bounce"], "range_octaves": 1, "prefer_chord_tones": 0.5},
    "rnb": {"contours": ["arch", "wave", "valley"], "rhythms": ["syncopated", "dotted"], "range_octaves": 1.5, "prefer_chord_tones": 0.5},
    "jazz": {"contours": ["zigzag", "wave", "ascending"], "rhythms": ["syncopated", "driving"], "range_octaves": 2, "prefer_chord_tones": 0.4},
    "lofi": {"contours": ["arch", "valley", "flat"], "rhythms": ["sparse", "dotted"], "range_octaves": 1, "prefer_chord_tones": 0.6},
    "rock": {"contours": ["ascending", "peak", "arch"], "rhythms": ["driving", "simple"], "range_octaves": 1.5, "prefer_chord_tones": 0.6},
    "edm": {"contours": ["ascending", "arch", "wave"], "rhythms": ["driving", "syncopated"], "range_octaves": 1.5, "prefer_chord_tones": 0.7},
    "gospel": {"contours": ["arch", "ascending", "peak"], "rhythms": ["syncopated", "dotted"], "range_octaves": 2, "prefer_chord_tones": 0.5},
    "latin": {"contours": ["wave", "zigzag", "arch"], "rhythms": ["syncopated", "offbeat"], "range_octaves": 1.5, "prefer_chord_tones": 0.5},
}


def generate_melody(
    key: str,
    scale: str = "minor",
    genre: str = "pop",
    contour: Optional[str] = None,
    rhythm: Optional[str] = None,
    notes_per_chord: int = 8,
    octave: int = 4,
    chord_progression: Optional[list[dict]] = None,
    seed: Optional[int] = None,
) -> dict:
    """
    Generate a melody that fits over a chord progression.
    If no progression is provided, one is generated automatically.
    """
    rng = random.Random(seed) if seed is not None else random.Random()

    genre_lower = genre.lower()
    genre_aliases = {
        "rap": "hiphop", "hip-hop": "hiphop", "hip hop": "hiphop",
        "r&b": "rnb", "r and b": "rnb",
        "lo-fi": "lofi", "lo fi": "lofi",
        "electronic": "edm",
    }
    genre_lower = genre_aliases.get(genre_lower, genre_lower)

    style = GENRE_MELODY_STYLES.get(genre_lower, GENRE_MELODY_STYLES["pop"])
    flats = uses_flats(key)

    # Get scale notes
    scale_notes = get_scale(key, scale, use_flats=flats)

    # Generate or use provided progression
    if chord_progression is None:
        prog = generate_progression(key=key, scale_type=scale, genre=genre_lower, num_chords=4)
        chord_progression = prog["chords"]

    # Choose contour
    if contour and contour in CONTOUR_SHAPES:
        contour_shape = CONTOUR_SHAPES[contour]
        contour_name = contour
    else:
        contour_name = rng.choice(style["contours"])
        contour_shape = CONTOUR_SHAPES[contour_name]

    # Choose rhythm
    if rhythm and rhythm in RHYTHM_PATTERNS:
        rhythm_pattern = RHYTHM_PATTERNS[rhythm]
        rhythm_name = rhythm
    else:
        rhythm_name = rng.choice(style["rhythms"])
        rhythm_pattern = RHYTHM_PATTERNS[rhythm_name]

    # Build the full scale across octaves for melody range
    range_semitones = int(style["range_octaves"] * 12)
    base_midi = _note_to_midi(key, octave)

    # Collect all scale MIDI notes within range
    scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["minor"])
    available_notes = []
    for oct_offset in range(-1, 3):
        for interval in scale_intervals:
            midi_note = base_midi + (oct_offset * 12) + interval
            if base_midi - 6 <= midi_note <= base_midi + range_semitones + 6:
                available_notes.append(midi_note)
    available_notes = sorted(set(available_notes))

    if not available_notes:
        available_notes = [base_midi + i for i in scale_intervals]

    prefer_chord_tones = style["prefer_chord_tones"]

    # Generate melody per chord
    melody_notes = []
    melody_over_chords = []

    for chord_idx, chord in enumerate(chord_progression):
        chord_midi_set = set()
        for n in chord.get("midi_notes", []):
            # Add chord tones across octaves
            pc = n % 12
            for candidate in available_notes:
                if candidate % 12 == pc:
                    chord_midi_set.add(candidate)

        # Interpolate contour shape to fit notes_per_chord
        chord_notes_list = []

        for note_idx in range(notes_per_chord):
            # Check rhythm — is this a rest?
            rhythm_pos = note_idx % len(rhythm_pattern)
            if rhythm_pattern[rhythm_pos] == 0:
                chord_notes_list.append({"midi": None, "is_rest": True, "beat": note_idx / 2})
                continue

            # Determine target scale degree from contour
            contour_pos = note_idx % len(contour_shape)
            contour_val = contour_shape[contour_pos]
            # Map contour (0-7) to available note indices
            note_index = int((contour_val / 7) * (len(available_notes) - 1))

            # Decide: chord tone or scale tone
            if rng.random() < prefer_chord_tones and chord_midi_set:
                # Pick nearest chord tone to our target
                target = available_notes[note_index]
                chosen = min(chord_midi_set, key=lambda x: abs(x - target))
            else:
                # Add a bit of randomness around the contour target
                jitter = rng.randint(-1, 1)
                idx = max(0, min(len(available_notes) - 1, note_index + jitter))
                chosen = available_notes[idx]

            note_name = _midi_to_note(chosen, flats)
            is_chord_tone = (chosen % 12) in {n % 12 for n in chord.get("midi_notes", [])}

            chord_notes_list.append({
                "midi": chosen,
                "note": note_name,
                "octave": chosen // 12 - 1,
                "beat": note_idx / 2,
                "is_rest": False,
                "is_chord_tone": is_chord_tone,
                "velocity": rng.randint(70, 110) if rhythm_pattern[rhythm_pos] == 1 else rng.randint(50, 80),
            })

        # Build MIDI sequence for this chord (non-rests only)
        midi_sequence = [n["midi"] for n in chord_notes_list if not n["is_rest"]]

        melody_over_chords.append({
            "chord": chord.get("name", ""),
            "roman_numeral": chord.get("roman_numeral", ""),
            "notes": chord_notes_list,
            "midi_sequence": midi_sequence,
        })

        melody_notes.extend(chord_notes_list)

    # Calculate melody statistics
    pitched_notes = [n for n in melody_notes if not n["is_rest"]]
    midi_values = [n["midi"] for n in pitched_notes]

    intervals = []
    for i in range(1, len(midi_values)):
        intervals.append(midi_values[i] - midi_values[i - 1])

    if intervals:
        avg_interval = sum(abs(i) for i in intervals) / len(intervals)
        max_leap = max(abs(i) for i in intervals)
        stepwise_pct = sum(1 for i in intervals if abs(i) <= 2) / len(intervals)
    else:
        avg_interval = 0
        max_leap = 0
        stepwise_pct = 0

    chord_tone_pct = sum(1 for n in pitched_notes if n.get("is_chord_tone")) / max(len(pitched_notes), 1)

    return {
        "key": key,
        "scale": scale,
        "genre": genre_lower,
        "contour": contour_name,
        "rhythm": rhythm_name,
        "octave": octave,
        "notes_per_chord": notes_per_chord,
        "melody": melody_over_chords,
        "stats": {
            "total_notes": len(pitched_notes),
            "rest_count": sum(1 for n in melody_notes if n["is_rest"]),
            "chord_tone_percentage": round(chord_tone_pct * 100, 1),
            "avg_interval_semitones": round(avg_interval, 1),
            "max_leap_semitones": max_leap,
            "stepwise_motion_pct": round(stepwise_pct * 100, 1),
        },
        "available_contours": list(CONTOUR_SHAPES.keys()),
        "available_rhythms": list(RHYTHM_PATTERNS.keys()),
    }
