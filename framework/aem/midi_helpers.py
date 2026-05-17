"""Helpers para exportar partes melódicas/armonicas/ritmicas a MIDI.

Filosofia: el framework genera AUDIO desde primitives (sine/noise/distort).
MIDI es PARTITURA — solo capturable para tracks que tengan notas explicitas
(melodias, drones armonicos, kicks). Texturas de noise/glitch/sweep NO
son representables en MIDI.

Usage tipico (en un script standalone):

    from aem.midi_helpers import MidiBuilder
    mb = MidiBuilder(bpm=120, output='song.mid')
    mb.add_melody_track('Voyager', [(120, melody_notes), (180, melody_notes)],
                        program=0)  # 0 = Acoustic Grand Piano (GM)
    mb.add_chord_track('Drone Dm', [(60, [73.42, 87.31, 110.0], 60)],
                       program=49)  # 49 = String Ensemble 1
    mb.add_kick_track('Heart Pulse', kick_times)
    mb.save()
"""

import math
import os
from typing import List, Tuple, Optional


def freq_to_midi(freq: float) -> int:
    """Convierte frecuencia Hz a numero de nota MIDI (0-127).
    A4 = 440 Hz = nota 69."""
    return int(round(69 + 12 * math.log2(freq / 440)))


def midi_to_freq(note: int) -> float:
    """Convierte nota MIDI a frecuencia Hz."""
    return 440.0 * (2 ** ((note - 69) / 12))


# General MIDI program numbers utiles para nuestro proyecto
GM_INSTRUMENTS = {
    'piano':           0,    # Acoustic Grand Piano
    'electric_piano':  4,    # Electric Piano 1
    'organ':           19,   # Church Organ
    'strings':         48,   # String Ensemble 1
    'pad_warm':        89,   # Pad 2 (warm)
    'pad_polysynth':   90,   # Pad 3 (polysynth)
    'pad_choir':       91,   # Pad 4 (choir)
    'pad_bowed':       92,   # Pad 5 (bowed)
    'pad_metallic':    93,   # Pad 6 (metallic)
    'pad_halo':        94,   # Pad 7 (halo)
    'pad_sweep':       95,   # Pad 8 (sweep)
    'voice_aahs':      53,   # Choir Aahs
    'voice_oohs':      54,   # Synth Voice
    'tubular_bells':   14,   # Tubular Bells
    'bell':            14,
    'synth_bass':      38,   # Synth Bass 1
    'fingered_bass':   33,   # Electric Bass (finger)
    'standard_kit':    0,    # Drum Kit (en canal 10)
    'sine_lead':       80,   # Lead 1 (square) — placeholder
}


def make_builder(bpm: int = 120, ticks_per_beat: int = 480):
    """Crea un MidiBuilder. Lazy import de mido para no obligar dep."""
    from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
    return MidiBuilder(bpm=bpm, ticks_per_beat=ticks_per_beat,
                       MidiFile=MidiFile, MidiTrack=MidiTrack,
                       Message=Message, MetaMessage=MetaMessage,
                       bpm2tempo=bpm2tempo)


class MidiBuilder:
    """Wrapper sobre mido. Permite agregar tracks de melody/chord/kick a un
    MIDI file con timing en seconds (que se traduce a ticks segun bpm)."""

    def __init__(self, bpm, ticks_per_beat,
                 MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo):
        self.bpm = bpm
        self.tpb = ticks_per_beat
        self._MidiFile = MidiFile
        self._MidiTrack = MidiTrack
        self._Message = Message
        self._MetaMessage = MetaMessage
        self._tempo = bpm2tempo(bpm)

        self.midi = MidiFile(ticks_per_beat=ticks_per_beat)

        # Track 0: tempo y meta info
        meta = MidiTrack()
        meta.append(MetaMessage('track_name', name='ÆM ', time=0))
        meta.append(MetaMessage('set_tempo', tempo=self._tempo, time=0))
        meta.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        self.midi.tracks.append(meta)

    def _seconds_to_ticks(self, seconds):
        # ticks = seconds * BPM/60 * ticks_per_beat
        return int(round(seconds * self.bpm / 60 * self.tpb))

    def _build_track_with_events(self, events, name, channel, program, velocity_default=80):
        """events: lista de (start_seconds, dur_seconds, midi_note, velocity_or_None)
        Genera Track con program_change + note_on/note_off ordenados por tiempo."""
        track = self._MidiTrack()
        track.append(self._MetaMessage('track_name', name=name, time=0))
        if program is not None:
            track.append(self._Message('program_change', program=program,
                                       channel=channel, time=0))

        # Construir lista de eventos absolutos: (tick, type, note, vel)
        evs = []
        for (start_s, dur_s, note, vel) in events:
            v = vel if vel is not None else velocity_default
            t_on = self._seconds_to_ticks(start_s)
            t_off = self._seconds_to_ticks(start_s + dur_s)
            evs.append((t_on, 'on', note, v))
            evs.append((t_off, 'off', note, v))
        # Ordenar por tick, luego off antes que on para evitar overlap raro
        evs.sort(key=lambda e: (e[0], 0 if e[1] == 'off' else 1))

        # Convertir a deltas relativos
        last_tick = 0
        for tick, kind, note, vel in evs:
            delta = tick - last_tick
            if kind == 'on':
                track.append(self._Message('note_on', note=note, velocity=vel,
                                           channel=channel, time=delta))
            else:
                track.append(self._Message('note_off', note=note, velocity=0,
                                           channel=channel, time=delta))
            last_tick = tick

        return track

    def add_melody_track(self, name, melody_events, program=0, channel=0,
                         velocity=80):
        """melody_events: lista de (start_seconds, [(freq, dur), ...])
        Cada evento es una secuencia de notas que se reproduce en serie
        empezando en start_seconds."""
        events = []
        for start_s, notes in melody_events:
            t = start_s
            for freq, dur in notes:
                note = freq_to_midi(freq)
                events.append((t, dur, note, velocity))
                t += dur
        track = self._build_track_with_events(events, name, channel, program, velocity)
        self.midi.tracks.append(track)

    def add_chord_track(self, name, chord_events, program=48, channel=0,
                        velocity=70):
        """chord_events: lista de (start_seconds, [freq1, freq2, ...], dur_seconds)
        Cada chord son N notas tocadas juntas durante dur_seconds."""
        events = []
        for start_s, freqs, dur_s in chord_events:
            for freq in freqs:
                events.append((start_s, dur_s, freq_to_midi(freq), velocity))
        track = self._build_track_with_events(events, name, channel, program, velocity)
        self.midi.tracks.append(track)

    def add_kick_track(self, name, kick_times, channel=9, note=36, velocity=100):
        """kick_times: lista de start_seconds para cada kick.
        channel=9 (10 humano) es canal de drums en GM.
        note=36 = Bass Drum 1 (kick) en standard drum map."""
        events = [(t, 0.1, note, velocity) for t in kick_times]
        track = self._build_track_with_events(events, name, channel, program=None,
                                              velocity_default=velocity)
        self.midi.tracks.append(track)

    def add_note_events_track(self, name, note_events, program=14, channel=0,
                              velocity=80):
        """note_events: lista de (start_seconds, freq, dur_seconds)
        Para bells, single notes puntuales."""
        events = [(t, dur, freq_to_midi(freq), velocity)
                  for (t, freq, dur) in note_events]
        track = self._build_track_with_events(events, name, channel, program, velocity)
        self.midi.tracks.append(track)

    def save(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.midi.save(path)
