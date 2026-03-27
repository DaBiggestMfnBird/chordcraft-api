"""
ChordCraft API - Chord Progression Generator
Built for RapidAPI marketplace.
"""

import os

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import Response, HTMLResponse
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
    docs_url=None,
    redoc_url=None,
)

CUSTOM_DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChordCraft API</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: #0a0a0f;
            color: #e0e0e8;
            min-height: 100vh;
        }

        .hero {
            background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 40%, #2d1b69 70%, #1a0a2e 100%);
            padding: 48px 32px 32px;
            text-align: center;
            border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(ellipse at 50% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
        }

        .hero * { position: relative; }

        .logo {
            font-size: 40px;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa, #7c3aed, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }

        .tagline {
            color: #9ca3af;
            font-size: 16px;
            margin-top: 8px;
            font-weight: 400;
        }

        .badges {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .badge {
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.3);
            color: #c4b5fd;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .quick-links {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 24px;
        }

        .quick-link {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.4);
            color: #c4b5fd;
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
        }

        .quick-link:hover {
            background: rgba(139, 92, 246, 0.35);
            border-color: #7c3aed;
            color: #fff;
        }

        .quick-link.primary {
            background: #7c3aed;
            border-color: #7c3aed;
            color: #fff;
        }

        .quick-link.primary:hover {
            background: #6d28d9;
        }

        .content {
            max-width: 960px;
            margin: 0 auto;
            padding: 32px 24px;
        }

        .section {
            margin-bottom: 32px;
        }

        .section-title {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #7c3aed;
            font-weight: 700;
            margin-bottom: 16px;
        }

        .endpoint-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .endpoint {
            background: #111118;
            border: 1px solid #1e1e2e;
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.2s;
        }

        .endpoint:hover {
            border-color: rgba(139, 92, 246, 0.4);
        }

        .endpoint-header {
            display: flex;
            align-items: center;
            padding: 14px 18px;
            cursor: pointer;
            gap: 14px;
            user-select: none;
        }

        .method {
            background: #065f46;
            color: #6ee7b7;
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            min-width: 48px;
            text-align: center;
        }

        .endpoint-path {
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 14px;
            font-weight: 600;
            color: #e5e7eb;
        }

        .endpoint-desc {
            color: #6b7280;
            font-size: 13px;
            margin-left: auto;
        }

        .endpoint-arrow {
            color: #4b5563;
            transition: transform 0.2s;
            font-size: 12px;
        }

        .endpoint.open .endpoint-arrow {
            transform: rotate(90deg);
        }

        .endpoint-body {
            display: none;
            padding: 0 18px 18px;
            border-top: 1px solid #1e1e2e;
        }

        .endpoint.open .endpoint-body {
            display: block;
        }

        .endpoint-body p {
            color: #9ca3af;
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 14px;
            margin-top: 14px;
        }

        .params-table {
            width: 100%;
            border-collapse: collapse;
        }

        .params-table th {
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #6b7280;
            padding: 8px 12px;
            border-bottom: 1px solid #1e1e2e;
        }

        .params-table td {
            padding: 10px 12px;
            font-size: 13px;
            border-bottom: 1px solid #1a1a24;
        }

        .param-name {
            font-family: 'SF Mono', 'Fira Code', monospace;
            color: #c4b5fd;
            font-weight: 500;
        }

        .param-type {
            color: #6b7280;
            font-size: 12px;
        }

        .param-desc { color: #9ca3af; }

        .param-default {
            font-family: 'SF Mono', 'Fira Code', monospace;
            color: #6ee7b7;
            font-size: 12px;
        }

        .try-box {
            background: #0d0d15;
            border: 1px solid #1e1e2e;
            border-radius: 8px;
            padding: 14px;
            margin-top: 14px;
        }

        .try-url {
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 12px;
            color: #a78bfa;
            word-break: break-all;
        }

        .try-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #6b7280;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .footer {
            text-align: center;
            padding: 40px 24px;
            color: #4b5563;
            font-size: 13px;
            border-top: 1px solid #1e1e2e;
        }

        @media (max-width: 640px) {
            .endpoint-desc { display: none; }
            .logo { font-size: 28px; }
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="logo">ChordCraft</div>
        <div class="tagline">Chord progressions, scales & MIDI for music production</div>
        <div class="badges">
            <span class="badge">10 Genres</span>
            <span class="badge">10 Moods</span>
            <span class="badge">12 Scales</span>
            <span class="badge">20+ Chord Types</span>
            <span class="badge">MIDI Export</span>
            <span class="badge">22 Instruments</span>
        </div>
        <div class="quick-links">
            <a href="/openapi.json" class="quick-link">OpenAPI Spec</a>
            <a href="/progression?key=C&scale=minor&genre=trap&mood=dark" class="quick-link primary">Try It</a>
        </div>
    </div>

    <div class="content">
        <div class="section">
            <div class="section-title">Progressions</div>
            <div class="endpoint-group">
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/progression</span>
                        <span class="endpoint-desc">Generate a chord progression</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Generate a chord progression based on key, scale, genre, and mood. Returns chord names, notes, MIDI values, and roman numeral analysis.</p>
                        <table class="params-table">
                            <tr><th>Param</th><th>Type</th><th>Default</th><th>Description</th></tr>
                            <tr><td class="param-name">key</td><td class="param-type">string</td><td class="param-default">C</td><td class="param-desc">Root note (C, F#, Bb, etc.)</td></tr>
                            <tr><td class="param-name">scale</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Scale type (major, minor, dorian, etc.)</td></tr>
                            <tr><td class="param-name">genre</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Genre (trap, lofi, jazz, pop, rnb, etc.)</td></tr>
                            <tr><td class="param-name">mood</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Mood (dark, chill, happy, sad, dreamy)</td></tr>
                            <tr><td class="param-name">chords</td><td class="param-type">int</td><td class="param-default">4</td><td class="param-desc">Number of chords (2-16)</td></tr>
                            <tr><td class="param-name">sevenths</td><td class="param-type">bool</td><td class="param-default">false</td><td class="param-desc">Use 7th chords</td></tr>
                            <tr><td class="param-name">inversion</td><td class="param-type">int</td><td class="param-default">0</td><td class="param-desc">Chord inversion (0-3)</td></tr>
                            <tr><td class="param-name">seed</td><td class="param-type">int</td><td class="param-default">-</td><td class="param-desc">Random seed for reproducibility</td></tr>
                        </table>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/progression?key=C&scale=minor&genre=trap&mood=dark&sevenths=true</div>
                        </div>
                    </div>
                </div>

                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/progression/batch</span>
                        <span class="endpoint-desc">Generate multiple progressions</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Generate multiple unique chord progressions at once. Returns up to 10 options, saving API calls.</p>
                        <table class="params-table">
                            <tr><th>Param</th><th>Type</th><th>Default</th><th>Description</th></tr>
                            <tr><td class="param-name">key</td><td class="param-type">string</td><td class="param-default">C</td><td class="param-desc">Root note</td></tr>
                            <tr><td class="param-name">scale</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Scale type</td></tr>
                            <tr><td class="param-name">genre</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Genre</td></tr>
                            <tr><td class="param-name">mood</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Mood</td></tr>
                            <tr><td class="param-name">count</td><td class="param-type">int</td><td class="param-default">5</td><td class="param-desc">Number of progressions (1-10)</td></tr>
                        </table>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/progression/batch?key=A&scale=minor&genre=rnb&count=5</div>
                        </div>
                    </div>
                </div>

                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/progression/midi</span>
                        <span class="endpoint-desc">Download as MIDI file</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Generate a progression and download it as a MIDI file. Drag it straight into your DAW.</p>
                        <table class="params-table">
                            <tr><th>Param</th><th>Type</th><th>Default</th><th>Description</th></tr>
                            <tr><td class="param-name">key</td><td class="param-type">string</td><td class="param-default">C</td><td class="param-desc">Root note</td></tr>
                            <tr><td class="param-name">genre</td><td class="param-type">string</td><td class="param-default">-</td><td class="param-desc">Genre</td></tr>
                            <tr><td class="param-name">bpm</td><td class="param-type">int</td><td class="param-default">120</td><td class="param-desc">Tempo (40-300)</td></tr>
                            <tr><td class="param-name">beats_per_chord</td><td class="param-type">int</td><td class="param-default">4</td><td class="param-desc">Beats per chord (1-16)</td></tr>
                            <tr><td class="param-name">instrument</td><td class="param-type">string</td><td class="param-default">piano</td><td class="param-desc">MIDI instrument (22 options)</td></tr>
                            <tr><td class="param-name">inversion</td><td class="param-type">int</td><td class="param-default">0</td><td class="param-desc">Chord inversion (0-3)</td></tr>
                        </table>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/progression/midi?key=F&genre=lofi&bpm=85&instrument=electric_piano</div>
                        </div>
                    </div>
                </div>

                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/random</span>
                        <span class="endpoint-desc">Surprise me — random everything</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Picks a random key, genre, mood, and scale. Perfect for beating writer's block.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/random?sevenths=true</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Suggestions</div>
            <div class="endpoint-group">
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/suggest</span>
                        <span class="endpoint-desc">Get production tips for a genre</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Returns typical BPM range, common keys, recommended scales, and a producer tip for any genre.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/suggest?genre=trap</div>
                        </div>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/suggest/all</span>
                        <span class="endpoint-desc">All genre suggestions at once</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Get production suggestions for every supported genre in one call.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/suggest/all</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Scales & Chords</div>
            <div class="endpoint-group">
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/scale</span>
                        <span class="endpoint-desc">Get notes in a scale</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Returns all notes in a given scale.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/scale?root=A&type=dorian</div>
                        </div>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/chords</span>
                        <span class="endpoint-desc">All diatonic chords in a key</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Get every diatonic chord in a key with optional 7ths and inversions.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/chords?key=D&scale=minor&sevenths=true</div>
                        </div>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/chord</span>
                        <span class="endpoint-desc">Look up a single chord</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                    <div class="endpoint-body">
                        <p>Get notes and MIDI values for any chord type with optional inversions.</p>
                        <div class="try-box">
                            <div class="try-label">Example</div>
                            <div class="try-url">/chord?root=E&type=min7&inversion=1</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Reference</div>
            <div class="endpoint-group">
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/scales</span>
                        <span class="endpoint-desc">List all scale types</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/chord-types</span>
                        <span class="endpoint-desc">List all chord types</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/genres</span>
                        <span class="endpoint-desc">List all genres</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/moods</span>
                        <span class="endpoint-desc">List all moods</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                </div>
                <div class="endpoint" onclick="this.classList.toggle('open')">
                    <div class="endpoint-header">
                        <span class="method">GET</span>
                        <span class="endpoint-path">/instruments</span>
                        <span class="endpoint-desc">List all MIDI instruments</span>
                        <span class="endpoint-arrow">&#9654;</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        ChordCraft API v1.1.0 &mdash; Built for producers, by a producer.
    </div>
</body>
</html>"""


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def custom_docs():
    return CUSTOM_DOCS_HTML

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
    genre_aliases = {
        "rap": "hiphop", "hip-hop": "hiphop", "hip hop": "hiphop",
        "r&b": "rnb", "r and b": "rnb",
        "lo-fi": "lofi", "lo fi": "lofi",
        "electronic": "edm",
    }
    genre_lower = genre_aliases.get(genre_lower, genre_lower)
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
