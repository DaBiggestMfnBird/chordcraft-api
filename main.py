"""
ChordCraft API - Chord Progression Generator
Built for RapidAPI marketplace.
"""

import os

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from music_theory import (
    generate_progression,
    get_scale,
    get_all_chords_in_key,
    get_chord_notes,
    get_chord_midi_notes,
    get_inversion_label,
    format_chord_name,
    uses_flats,
    NOTES,
    SCALE_INTERVALS,
    GENRE_PROGRESSIONS,
    GENRE_SUGGESTIONS,
    MOOD_MAP,
    CHORD_TYPES,
)
from midi_gen import progression_to_midi, MIDI_INSTRUMENTS

import random

app = FastAPI(
    title="ChordCraft API",
    description="Generate chord progressions, scales, and MIDI files for music production. "
    "Supports multiple genres, moods, inversions, and music theory operations.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for RapidAPI and general use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RapidAPI proxy secret — set via environment variable
RAPIDAPI_PROXY_SECRET = os.environ.get("RAPIDAPI_PROXY_SECRET")


@app.middleware("http")
async def verify_rapidapi(request: Request, call_next):
    """Verify requests come through RapidAPI when proxy secret is configured."""
    # Skip verification for health/docs endpoints and when secret isn't set
    path = request.url.path
    if path in ("/", "/health", "/docs", "/redoc", "/openapi.json"):
        return await call_next(request)

    if RAPIDAPI_PROXY_SECRET:
        proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret")
        if proxy_secret != RAPIDAPI_PROXY_SECRET:
            return Response(
                content='{"detail": "Unauthorized. Access this API through RapidAPI."}',
                status_code=403,
                media_type="application/json",
            )

    return await call_next(request)


# ─── Health ───
@app.get("/", tags=["Health"])
def root():
    return {
        "name": "ChordCraft API",
        "version": "1.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


# ─── Progression Generation ───
@app.get("/progression", tags=["Progressions"])
def get_progression(
    key: str = Query("C", description="Root note (e.g., C, F#, Bb)"),
    scale: Optional[str] = Query(None, description="Scale type (e.g., major, minor, dorian)"),
    genre: Optional[str] = Query(None, description="Genre (e.g., trap, lofi, jazz, pop, rnb, hiphop)"),
    mood: Optional[str] = Query(None, description="Mood (e.g., dark, chill, happy, sad, dreamy)"),
    chords: int = Query(4, ge=2, le=16, description="Number of chords (2-16)"),
    sevenths: bool = Query(False, description="Use 7th chords for richer harmony"),
    inversion: int = Query(0, ge=0, le=3, description="Chord inversion (0=root, 1=1st, 2=2nd, 3=3rd)"),
    seed: Optional[int] = Query(None, description="Random seed for reproducible results"),
):
    """
    Generate a chord progression based on key, scale, genre, and mood.

    Returns chord names, notes, MIDI values, and roman numeral analysis.
    Supports inversions for more realistic voicings.
    """
    try:
        result = generate_progression(
            key=key,
            scale_type=scale,
            genre=genre,
            mood=mood,
            num_chords=chords,
            use_7ths=sevenths,
            seed=seed,
        )

        # Apply inversions to chord data
        if inversion > 0:
            flats = uses_flats(key)
            for chord in result["chords"]:
                chord["midi_notes"] = get_chord_midi_notes(
                    chord["root"], chord["quality"], inversion=inversion
                )
                chord["inversion"] = get_inversion_label(inversion)
            result["inversion"] = get_inversion_label(inversion)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/progression/batch", tags=["Progressions"])
def get_progression_batch(
    key: str = Query("C", description="Root note (e.g., C, F#, Bb)"),
    scale: Optional[str] = Query(None, description="Scale type"),
    genre: Optional[str] = Query(None, description="Genre"),
    mood: Optional[str] = Query(None, description="Mood"),
    chords: int = Query(4, ge=2, le=16, description="Number of chords"),
    sevenths: bool = Query(False, description="Use 7th chords"),
    count: int = Query(5, ge=1, le=10, description="Number of progressions to generate (1-10)"),
):
    """
    Generate multiple chord progressions at once.

    Returns up to 10 unique progressions, saving API calls for apps that want to
    offer users a selection.
    """
    try:
        seen = set()
        progressions = []
        attempts = 0
        max_attempts = count * 5  # avoid infinite loop if not enough unique patterns

        while len(progressions) < count and attempts < max_attempts:
            attempts += 1
            result = generate_progression(
                key=key,
                scale_type=scale,
                genre=genre,
                mood=mood,
                num_chords=chords,
                use_7ths=sevenths,
            )
            label = result["progression_label"]
            if label not in seen:
                seen.add(label)
                progressions.append(result)

        return {
            "key": key,
            "count": len(progressions),
            "progressions": progressions,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/progression/midi", tags=["Progressions"])
def get_progression_midi(
    key: str = Query("C", description="Root note (e.g., C, F#, Bb)"),
    scale: Optional[str] = Query(None, description="Scale type"),
    genre: Optional[str] = Query(None, description="Genre"),
    mood: Optional[str] = Query(None, description="Mood"),
    chords: int = Query(4, ge=2, le=16, description="Number of chords"),
    sevenths: bool = Query(False, description="Use 7th chords"),
    bpm: int = Query(120, ge=40, le=300, description="Tempo in BPM"),
    beats_per_chord: int = Query(4, ge=1, le=16, description="Beats per chord"),
    instrument: str = Query("piano", description="MIDI instrument (e.g., piano, electric_piano, guitar, strings, synth_pad)"),
    inversion: int = Query(0, ge=0, le=3, description="Chord inversion (0=root, 1=1st, 2=2nd, 3=3rd)"),
    seed: Optional[int] = Query(None, description="Random seed"),
):
    """
    Generate a chord progression and return as a downloadable MIDI file.

    Supports instrument selection and chord inversions.
    """
    try:
        if instrument not in MIDI_INSTRUMENTS:
            raise ValueError(
                f"Unknown instrument: {instrument}. Available: {list(MIDI_INSTRUMENTS.keys())}"
            )

        result = generate_progression(
            key=key,
            scale_type=scale,
            genre=genre,
            mood=mood,
            num_chords=chords,
            use_7ths=sevenths,
            seed=seed,
        )
        midi_bytes = progression_to_midi(
            result["chords"],
            bpm=bpm,
            beats_per_chord=beats_per_chord,
            instrument=instrument,
            inversion=inversion,
        )
        safe_key = key.replace("#", "sharp").replace("b", "flat") if len(key) > 1 else key
        filename = f"progression_{safe_key}_{result['scale']}_{result['genre']}.mid"
        return Response(
            content=midi_bytes,
            media_type="audio/midi",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Random / Surprise Me ───
@app.get("/random", tags=["Progressions"])
def random_progression(
    sevenths: bool = Query(False, description="Use 7th chords"),
    inversion: int = Query(0, ge=0, le=3, description="Chord inversion"),
):
    """
    Generate a completely random chord progression.

    Picks a random key, genre, mood, and scale — perfect for beating writer's block.
    """
    rng = random.Random()
    key = rng.choice(NOTES)
    genre = rng.choice(list(GENRE_PROGRESSIONS.keys()))
    mood = rng.choice(list(MOOD_MAP.keys()))

    result = generate_progression(
        key=key,
        genre=genre,
        mood=mood,
        use_7ths=sevenths,
    )

    if inversion > 0:
        for chord in result["chords"]:
            chord["midi_notes"] = get_chord_midi_notes(
                chord["root"], chord["quality"], inversion=inversion
            )
            chord["inversion"] = get_inversion_label(inversion)
        result["inversion"] = get_inversion_label(inversion)

    return result


# ─── Suggest ───
@app.get("/suggest", tags=["Suggestions"])
def suggest_for_genre(
    genre: str = Query(..., description="Genre to get suggestions for"),
):
    """
    Get production suggestions for a genre.

    Returns typical BPM range, common keys, recommended scales, and a producer tip.
    Perfect for figuring out where to start a new track.
    """
    genre_lower = genre.lower()
    if genre_lower not in GENRE_SUGGESTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown genre: {genre}. Available: {list(GENRE_SUGGESTIONS.keys())}",
        )

    suggestions = GENRE_SUGGESTIONS[genre_lower]
    return {
        "genre": genre_lower,
        "bpm_range": suggestions["bpm_range"],
        "suggested_bpm": sum(suggestions["bpm_range"]) // 2,
        "common_keys": suggestions["common_keys"],
        "recommended_scales": suggestions["recommended_scales"],
        "tip": suggestions["tip"],
    }


@app.get("/suggest/all", tags=["Suggestions"])
def suggest_all():
    """Get production suggestions for all genres at once."""
    return {
        "genres": {
            genre: {
                **info,
                "suggested_bpm": sum(info["bpm_range"]) // 2,
            }
            for genre, info in GENRE_SUGGESTIONS.items()
        },
        "count": len(GENRE_SUGGESTIONS),
    }


# ─── Scales ───
@app.get("/scale", tags=["Scales"])
def get_scale_notes(
    root: str = Query("C", description="Root note"),
    type: str = Query("major", description="Scale type"),
):
    """Get all notes in a scale."""
    try:
        flats = uses_flats(root)
        notes = get_scale(root, type, use_flats=flats)
        return {
            "root": root,
            "scale_type": type,
            "notes": notes,
            "num_notes": len(notes),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/scales", tags=["Scales"])
def list_scales():
    """List all available scale types."""
    return {
        "scales": list(SCALE_INTERVALS.keys()),
        "count": len(SCALE_INTERVALS),
    }


# ─── Chords ───
@app.get("/chords", tags=["Chords"])
def get_chords_in_key(
    key: str = Query("C", description="Root note"),
    scale: str = Query("major", description="Scale type"),
    sevenths: bool = Query(False, description="Use 7th chords"),
    inversion: int = Query(0, ge=0, le=3, description="Chord inversion"),
):
    """Get all diatonic chords in a key, with optional inversions."""
    try:
        chords = get_all_chords_in_key(key, scale, use_7ths=sevenths)

        if inversion > 0:
            for chord in chords:
                chord["midi_notes"] = get_chord_midi_notes(
                    chord["root"], chord["quality"], inversion=inversion
                )
                chord["inversion"] = get_inversion_label(inversion)

        return {
            "key": key,
            "scale": scale,
            "use_7ths": sevenths,
            "inversion": get_inversion_label(inversion) if inversion > 0 else "root position",
            "chords": chords,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/chord", tags=["Chords"])
def get_single_chord(
    root: str = Query("C", description="Root note"),
    type: str = Query("maj", description="Chord type (e.g., maj, min, dom7, min7, dim, sus2)"),
    octave: int = Query(4, ge=1, le=7, description="Octave for MIDI notes"),
    inversion: int = Query(0, ge=0, le=3, description="Chord inversion"),
):
    """Get the notes and MIDI values for a specific chord, with optional inversion."""
    try:
        flats = uses_flats(root)
        notes = get_chord_notes(root, type, use_flats=flats)
        midi = get_chord_midi_notes(root, type, octave, inversion=inversion)
        result = {
            "root": root,
            "type": type,
            "name": format_chord_name(root, type),
            "notes": notes,
            "midi_notes": midi,
        }
        if inversion > 0:
            result["inversion"] = get_inversion_label(inversion)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/chord-types", tags=["Chords"])
def list_chord_types():
    """List all available chord types."""
    return {
        "chord_types": list(CHORD_TYPES.keys()),
        "count": len(CHORD_TYPES),
    }


# ─── Reference ───
@app.get("/genres", tags=["Reference"])
def list_genres():
    """List all supported genres."""
    return {
        "genres": list(GENRE_PROGRESSIONS.keys()),
        "count": len(GENRE_PROGRESSIONS),
    }


@app.get("/moods", tags=["Reference"])
def list_moods():
    """List all supported moods with their associated scales and genres."""
    return {
        "moods": {
            mood: info for mood, info in MOOD_MAP.items()
        },
        "count": len(MOOD_MAP),
    }


@app.get("/instruments", tags=["Reference"])
def list_instruments():
    """List all available MIDI instruments."""
    return {
        "instruments": list(MIDI_INSTRUMENTS.keys()),
        "count": len(MIDI_INSTRUMENTS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
