"""Render lab para comparar voyager OCTAVA ABAJO en cada timbre + version OCTAVA
ORIGINAL con correcciones maximas anti-fatiga.

Output:
  lab/voyager_OCTLOW_flute.wav    — flute_traversa con motivo octava abajo
  lab/voyager_OCTLOW_tool.wav     — TOOL config (3 delays + bass + drone) octava abajo
  lab/voyager_OCTLOW_quena.wav    — QUENA config (triangle ascending + reverb plate) octava abajo
  lab/voyager_OCTLOW_roach.wav    — ROACH config (triple layer detuned + drone + tremolo) octava abajo
  lab/voyager_OCTHIGH_corrected.wav — OCTAVA ORIGINAL con max anti-fatiga:
                                       LPF 1500 + notches -18 + amp variable +
                                       reverb corto + bass+drone fuerte
"""

import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.instruments import (flute_motif, melody, detuned_drone, voice_pad)
from aem.motifs import (voyager_motif, voyager_safe, voyager_safe_fx,
                          VOYAGER_NOTES, VOYAGER_ASCENDING)
from aem.effects import reverb, fade, lpf, notch_eq, lfo_amp

OUT_DIR = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'release', 'lab')
os.makedirs(OUT_DIR, exist_ok=True)

LEAD = 1.0
TRAIL = 8.0


def write(comp, suffix):
    audio = comp.render_stereo()
    out = os.path.join(OUT_DIR, f'voyager_{suffix}.wav')
    sf.write(out, audio, SR, subtype='PCM_24')
    print(f'  -> {out}')


def add_bass_drone(comp, motif_oct_low):
    """Bass + drone D2 (formula TOOL anti-aturde)."""
    bass = comp.add_track(Track('bass', gain=0.45, pan=0.0))
    bass.add(LEAD, fade(motif_oct_low, fi=0.3, fo=0.5))
    bass.fx(lambda a: reverb(a, decay=2.5, mix=0.25))
    drone = comp.add_track(Track('drone_d2', gain=0.10))
    drone.add(0.5, detuned_drone([73.42], comp.duration - 1.0, amp=0.4,
                                   n_voices=1, detune_cents=0))
    drone.fx(lambda a: reverb(a, decay=5.0, mix=0.4))


# ---- OCTLOW: flute ----
def render_flute_octlow():
    motif_dur = sum(d for _, d in VOYAGER_NOTES)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name='Voyager OCTLOW flute')
    notes_low = [(f / 2, d) for f, d in VOYAGER_NOTES]   # octava abajo
    motif = flute_motif(notes_low, amp=0.45, vibrato=True,
                          breath_amount=0.015, chiff_amount=0.04)
    voy = comp.add_track(Track('voyager_flute_low', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(motif, fi=0.3, fo=0.5))
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 4, d) for f, d in VOYAGER_NOTES]   # 2 octavas abajo
    bass_motif = melody(bass_notes, amp=0.30, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_drone(comp, bass_motif)
    write(comp, 'OCTLOW_flute')


# ---- OCTLOW: tool ----
def render_tool_octlow():
    motif_dur = sum(d for _, d in VOYAGER_ASCENDING)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name='Voyager OCTLOW tool')
    # Voz central — TOOL usa 'ascending' con triangle + 4 notches + reverb 3.5/0.40
    voy_main = comp.add_track(Track('tool_main', gain=0.55, pan=0.0))
    voy_main.add(LEAD, voyager_motif(variation='ascending', amp=0.40,
                                       waveform='triangle', release=0.6,
                                       octave_shift=-1))   # octava abajo
    for f in [880, 1046, 1760, 2093]:
        voy_main.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
    voy_main.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Delays L 250ms, R 500ms, L2 750ms — estilo TOOL
    for offset, gain, pan in [(0.250, 0.30, -0.6), (0.500, 0.20, +0.6), (0.750, 0.13, -0.4)]:
        d = comp.add_track(Track(f'tool_delay_{int(offset*1000)}ms', gain=gain, pan=pan))
        d.add(LEAD + offset, voyager_motif(variation='ascending', amp=0.40,
                                              waveform='triangle', release=0.6,
                                              octave_shift=-1))
        for f in [880, 1046, 1760, 2093]:
            d.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
        d.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Bass octava abajo (osea -2 oct del original) + drone
    bass_notes = [(f / 4, d) for f, d in VOYAGER_ASCENDING]
    bass_motif = melody(bass_notes, amp=0.30, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_drone(comp, bass_motif)
    write(comp, 'OCTLOW_tool')


# ---- OCTLOW: quena ----
def render_quena_octlow():
    motif_dur = sum(d for _, d in VOYAGER_ASCENDING)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name='Voyager OCTLOW quena')
    voy = comp.add_track(Track('quena_main_low', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_motif(variation='ascending', amp=0.40,
                                  waveform='triangle', vibrato=True,
                                  attack=0.05, release=0.6, release_curve=1.0,
                                  octave_shift=-1))
    for f in [880, 1046, 1760, 2093]:
        voy.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
    voy.fx(lambda a: reverb(a, decay=5.0, mix=0.40, pre_delay_ms=80))
    bass_notes = [(f / 4, d) for f, d in VOYAGER_ASCENDING]
    bass_motif = melody(bass_notes, amp=0.30, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_drone(comp, bass_motif)
    write(comp, 'OCTLOW_quena')


# ---- OCTLOW: roach ----
def render_roach_octlow():
    motif_dur = sum(d for _, d in VOYAGER_ASCENDING)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name='Voyager OCTLOW roach')

    def voy_detuned(amp, oct_shift, detune_cents):
        # OCT_SHIFT: -1 para que el "main" del roach quede en octava abajo
        # (roach original: main=0, up=+1, dn=-1 → ahora main=-1, up=0, dn=-2)
        factor = (2 ** oct_shift) * (2 ** (detune_cents / 1200))
        notes = [(f * factor, d) for f, d in VOYAGER_ASCENDING]
        return melody(notes, amp=amp, vibrato=True, waveform='triangle',
                      attack=0.2, release=0.6, release_curve=1.0)

    # Main (era 0, ahora -1)
    voy_main = comp.add_track(Track('roach_main_low', gain=0.45, pan=0.0))
    voy_main.add(LEAD, voy_detuned(amp=0.35, oct_shift=-1, detune_cents=0))
    for f in [880, 1046, 1760, 2093]:
        voy_main.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
    # Up (era +1, ahora 0 — octava original como capa de brillo)
    voy_up = comp.add_track(Track('roach_up_low', gain=0.18, pan=-0.3))
    voy_up.add(LEAD, voy_detuned(amp=0.30, oct_shift=0, detune_cents=10))
    for f in [880, 1046, 1760, 2093]:
        voy_up.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
    voy_up.fx(lambda a: notch_eq(a, freq_hz=3520, q=10, gain_db=-9))
    # Down (era -1, ahora -2)
    voy_dn = comp.add_track(Track('roach_dn_low', gain=0.30, pan=+0.3))
    voy_dn.add(LEAD, voy_detuned(amp=0.35, oct_shift=-2, detune_cents=-10))
    # Drone
    drone = comp.add_track(Track('roach_drone', gain=0.20))
    drone.add(0.5, detuned_drone([73.42], duration - 1.0, amp=0.35,
                                   n_voices=3, detune_cents=8))
    # Reverb + tremolo
    big_reverb = lambda a: reverb(a, decay=7.0, mix=0.50, pre_delay_ms=100)
    for t in [voy_main, voy_up, voy_dn]:
        t.fx(big_reverb)
        t.fx(lambda a: lfo_amp(a, rate_hz=0.15, depth=0.15))
    drone.fx(lambda a: reverb(a, decay=6.0, mix=0.4, pre_delay_ms=100))

    write(comp, 'OCTLOW_roach')


# ---- OCTHIGH: octava ORIGINAL con maximas correcciones anti-fatiga ----
def render_octhigh_corrected():
    motif_dur = sum(d for _, d in VOYAGER_NOTES)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name='Voyager OCTHIGH corregido (anti-fatiga max)')

    # Triangle voyager EN OCTAVA ORIGINAL pero con todo el anti-fatiga aplicado
    # 1. amp variable por nota: A5/C6 con amp -30%
    # 2. notches -18 dB (en lugar de -12)
    # 3. LPF 1500 (corta 2do armonico de A5 directamente)
    # 4. reverb 2.0 mix 0.25 (corto, no sostiene)
    # 5. bass + drone fuertes para masking grave

    # amp variable: notas con freq alta = amp menor
    notes_var_amp = []
    for freq, dur in VOYAGER_NOTES:
        # Las notas D5/F5/A5 son las altas. Bajo A5 mas que el resto.
        if freq >= 800:    # A5
            scale = 0.65
        elif freq >= 600:  # F5
            scale = 0.85
        else:              # D5, A4
            scale = 1.0
        notes_var_amp.append((freq, dur, scale))
    # Generar nota por nota con amp escalado
    chunks = []
    for freq, dur, scale in notes_var_amp:
        chunks.append(melody([(freq, dur)], amp=0.40 * scale, vibrato=True,
                               waveform='triangle', release=0.6, release_curve=1.0))
    voy_audio = np.concatenate(chunks)

    voy = comp.add_track(Track('voyager_corrected', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(voy_audio, fi=0.3, fo=0.5))
    # Notches -18 dB (mas agresivos)
    for f in [880, 1046, 1760, 2093]:
        voy.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-18))
    # LPF 1500 (mas agresivo)
    voy.fx(lambda a: lpf(a, 1500))
    # Reverb corto
    voy.fx(lambda a: reverb(a, decay=2.0, mix=0.25))

    # Bass + drone GRAVE FUERTE (masking)
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]   # 1 octava abajo
    bass_motif = melody(bass_notes, amp=0.45, vibrato=False, waveform='sine',
                          release=0.8)
    bass = comp.add_track(Track('bass_strong', gain=0.55, pan=0.0))
    bass.add(LEAD, fade(bass_motif, fi=0.3, fo=0.5))
    bass.fx(lambda a: reverb(a, decay=2.5, mix=0.25))

    # Drone D2 mas presente
    drone = comp.add_track(Track('drone_d2_strong', gain=0.18))
    drone.add(0.5, detuned_drone([73.42], duration - 1.0, amp=0.45,
                                   n_voices=2, detune_cents=5))
    drone.fx(lambda a: reverb(a, decay=5.0, mix=0.4))

    write(comp, 'OCTHIGH_corrected')


def main():
    print('=== Voyager OCTAVE LAB ===')
    render_flute_octlow()
    render_tool_octlow()
    render_quena_octlow()
    render_roach_octlow()
    render_octhigh_corrected()
    print()
    print('Comparacion:')
    print('  OCTLOW_*  = octava abajo (tipo v4 que NO te molesto)')
    print('  OCTHIGH_corrected = octava ORIGINAL con max anti-fatiga')
    print('   → si OCTHIGH no te molesta, las correcciones funcionan')
    print('   → si te molesta igual, el problema ES la octava (registro fisico)')


if __name__ == '__main__':
    main()
