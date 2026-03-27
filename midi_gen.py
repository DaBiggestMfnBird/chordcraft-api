"""MIDI file generation for chord progressions."""

import io
from midiutil import MIDIFile
from music_theory import get_chord_midi_notes

# General MIDI instrument mappings (program numbers)
MIDI_INSTRUMENTS = {
    "piano": 0,
    "electric_piano": 4,
    "organ": 19,
    "guitar": 25,
    "acoustic_guitar": 25,
    "electric_guitar": 27,
    "bass": 33,
    "strings": 48,
    "synth_pad": 89,
    "synth_lead": 80,
    "brass": 61,
    "flute": 73,
    "vibraphone": 11,
    "Rhodes": 4, # MIDI GM doesn't have exact Rhodes, use electric piano
    "wurlitzer": 4, # Same for wurlitzer, closest is electric piano
    "marimba": 12,
    "choir": 52,
    "clavinet": 7,
    "harpsichord": 6,
    "music_box": 10,
    "pad": 89,
    "lead": 80,
}


def progression_to_midi(
    chords: list[dict],
    bpm: int = 120,
    beats_per_chord: int = 4,
    velocity: int = 100,
    octave: int = 4,
    instrument: str = "piano",
    inversion: int = 0,
) -> bytes:
    """Convert a chord progression to a MIDI file and return as bytes."""
    midi = MIDIFile(1)
    track = 0
    channel = 0
    time = 0

    midi.addTempo(track, 0, bpm)

    program = MIDI_INSTRUMENTS.get(instrument, 0)
    midi.addProgramChange(track, channel, 0, program)

    for chord in chords:
        midi_notes = get_chord_midi_notes(
            chord["root"], chord["quality"], octave, inversion=inversion
        )
        for note in midi_notes:
            midi.addNote(track, channel, note, time, beats_per_chord, velocity)
        time += beats_per_chord

    buffer = io.BytesIO()
    midi.writeFile(buffer)
    buffer.seek(0)
    return buffer.read()
