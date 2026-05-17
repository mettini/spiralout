"""Voyager LAB — render comparativo de 6 versiones.

TODAS comparten la formula TOOL que probo ser amable al timpano:
  - voyager (instrumento principal) panneado center, gain moderado
  - bass: voyager octava abajo, sine pura, sostiene la fundamental
  - drone: D2 sine + reverb 5s — anclaje grave continuo
  - reverb del voyager: decay 3.5 mix 0.40 (corto, no sostiene armonicos altos)

Lo que VARIA entre las 6: el INSTRUMENTO PRINCIPAL.

  v1 — flute_warm           (flute_traversa warm + 4 notches_voyager)
  v2 — flute_warm_NO_BREATH (igual que v1 pero sin breath_noise — menos fantasmal)
  v3 — triangle_voyager     (triangle + 4 notches + LPF 2200 = voyager_safe)
  v4 — triangle_octava_abajo (triangle pero 1 octava abajo = registro D4-A4 — mas calido)
  v5 — flute_warm + delay_TOOL (flauta + delays 250/500/750ms tipo TOOL — mas
       espacial. Si las notas se pisan, va el v1 sin delays)
  v6 — flute_DRY            (flute_warm + drone, SIN bass, SIN delays — minimal,
       solo flauta y drone)

Output: transmissions/01/release/lab/voyager_LAB_v[1-6].wav
"""

import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.instruments import flute_traversa, flute_motif, detuned_drone, melody
from aem.motifs import (VOYAGER_NOTES, voyager_motif, voyager_safe,
                          voyager_safe_fx)
from aem.effects import reverb, fade

OUT_DIR = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'release', 'lab')
os.makedirs(OUT_DIR, exist_ok=True)

LEAD = 1.0
TRAIL = 8.0


def add_bass_and_drone(comp, motif_audio_octave_down):
    """Agrega bass (voyager octava abajo) + drone D2 al comp.
    Formula TOOL: anclaje grave que evita que los agudos floten expuestos."""
    # Bass: el voyager 1 octava abajo en sine pura
    bass = comp.add_track(Track('bass_octave_down', gain=0.45, pan=0.0))
    bass.add(LEAD, fade(motif_audio_octave_down, fi=0.3, fo=0.5))
    bass.fx(lambda a: reverb(a, decay=2.5, mix=0.25))

    # Drone D2 sine continuo
    drone = comp.add_track(Track('drone_D2', gain=0.10))
    drone.add(0.5, detuned_drone([73.42], comp.duration - 1.0, amp=0.4,
                                   n_voices=1, detune_cents=0))
    drone.fx(lambda a: reverb(a, decay=5.0, mix=0.4))


def render(version, name, label):
    """version: function que recibe `comp` y agrega los tracks especificos."""
    motif_dur = sum(d for _, d in VOYAGER_NOTES)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name=f'Voyager LAB v{version} — {label}')
    name_func = name  # callable que toma comp
    name_func(comp, duration)
    audio = comp.render_stereo()
    out_path = os.path.join(OUT_DIR, f'voyager_LAB_v{version}_{label}.wav')
    sf.write(out_path, audio, SR, subtype='PCM_24')
    print(f'  v{version} {label:30s} -> {out_path}')


# ---- v1: flute_warm + bass + drone ----
def v1_flute_warm(comp, dur):
    motif = flute_motif(VOYAGER_NOTES, amp=0.40, vibrato=True,
                          breath_amount=0.015, chiff_amount=0.04)
    voy = comp.add_track(Track('voyager_flute_warm', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(motif, fi=0.3, fo=0.5))
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Bass = mismo motif pero octava abajo (notas / 2)
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.35, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v2: flute_warm SIN breath ----
def v2_flute_warm_no_breath(comp, dur):
    motif = flute_motif(VOYAGER_NOTES, amp=0.40, vibrato=True,
                          breath_amount=0.0, chiff_amount=0.0)
    voy = comp.add_track(Track('voyager_flute_pure', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(motif, fi=0.3, fo=0.5))
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.35, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v3: triangle voyager_safe + bass + drone ----
def v3_triangle_voyager_safe(comp, dur):
    voy = comp.add_track(Track('voyager_triangle_safe', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_safe(amp=0.40, variation='main'))
    voyager_safe_fx(voy)
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.35, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v4: triangle 1 octava ABAJO (registro D4-A4 — mas calido) ----
def v4_triangle_octave_down(comp, dur):
    voy = comp.add_track(Track('voyager_triangle_low', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_safe(amp=0.45, variation='main', octave_shift=-1))
    voyager_safe_fx(voy)
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 4, d) for f, d in VOYAGER_NOTES]   # 2 octavas abajo
    bass_motif = melody(bass_notes, amp=0.30, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v5: flute_warm + delays 250/500/750 ms (estilo TOOL) ----
def v5_flute_warm_tool_delays(comp, dur):
    motif = flute_motif(VOYAGER_NOTES, amp=0.40, vibrato=True,
                          breath_amount=0.015, chiff_amount=0.04)
    voy = comp.add_track(Track('voyager_flute_main', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(motif, fi=0.3, fo=0.5))
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Delay L 250ms
    dl = comp.add_track(Track('flute_delay_L_250', gain=0.30, pan=-0.6))
    dl.add(LEAD + 0.250, fade(motif, fi=0.3, fo=0.5))
    dl.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Delay R 500ms
    dr = comp.add_track(Track('flute_delay_R_500', gain=0.20, pan=+0.6))
    dr.add(LEAD + 0.500, fade(motif, fi=0.3, fo=0.5))
    dr.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    # Delay L 750ms
    dl2 = comp.add_track(Track('flute_delay_L_750', gain=0.13, pan=-0.4))
    dl2.add(LEAD + 0.750, fade(motif, fi=0.3, fo=0.5))
    dl2.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.35, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v6: flute_warm SOLO con drone (sin bass) — minimal ----
def v6_flute_minimal(comp, dur):
    motif = flute_motif(VOYAGER_NOTES, amp=0.40, vibrato=True,
                          breath_amount=0.015, chiff_amount=0.04)
    voy = comp.add_track(Track('voyager_flute_solo', gain=0.55, pan=0.0))
    voy.add(LEAD, fade(motif, fi=0.3, fo=0.5))
    voy.fx(lambda a: reverb(a, decay=4.5, mix=0.45))   # un poco mas de aire al estar solo
    # Solo drone, sin bass
    drone = comp.add_track(Track('drone_D2', gain=0.12))
    drone.add(0.5, detuned_drone([73.42], dur - 1.0, amp=0.4,
                                   n_voices=1, detune_cents=0))
    drone.fx(lambda a: reverb(a, decay=5.0, mix=0.4))


# ---- v7: LAYERED — triangle octava abajo (cuerpo) + capa octava normal (brillo sutil) ----
def v7_layered_octave_warm_bright(comp, dur):
    # Cuerpo: octava abajo (igual a v4) — esto es lo que NO aturde
    voy_low = comp.add_track(Track('voyager_body_low', gain=0.55, pan=0.0))
    voy_low.add(LEAD, voyager_safe(amp=0.45, variation='main', octave_shift=-1))
    voyager_safe_fx(voy_low)
    voy_low.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

    # Capa de brillo: octava normal (D5-A5) pero MUY sutil + lejano
    voy_high = comp.add_track(Track('voyager_brightness_high', gain=0.18, pan=0.0))
    voy_high.add(LEAD, voyager_safe(amp=0.35, variation='main'))   # octave normal
    voyager_safe_fx(voy_high)
    voy_high.fx(lambda a: reverb(a, decay=6.0, mix=0.65))   # mas reverb = mas lejos

    # Bass + drone (anclaje grave)
    bass_notes = [(f / 4, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.30, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


# ---- v8: triangle ORIGINAL pero LPF mas agresivo (1500 en vez de 2200) ----
def v8_triangle_original_lpf1500(comp, dur):
    from aem.effects import lpf, notch_eq
    voy = comp.add_track(Track('voyager_triangle_attenuated', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_safe(amp=0.40, variation='main'))
    # Aplicamos los notches manualmente + LPF 1500 (mas bajo que el 2200 default)
    for f, _ in [(880,'A5'),(1046,'C6'),(1760,'D5_3rd'),(2093,'F5_3rd')]:
        voy.fx(lambda a, freq=f: notch_eq(a, freq_hz=freq, q=10, gain_db=-12))
    voy.fx(lambda a: lpf(a, 1500))   # mas agresivo = corta hasta el 2do armonico de A5
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    bass_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    bass_motif = melody(bass_notes, amp=0.35, vibrato=False, waveform='sine',
                          release=0.8)
    add_bass_and_drone(comp, bass_motif)


def main():
    print('=== Voyager LAB ===')
    render(1, v1_flute_warm,                'flute_warm')
    render(2, v2_flute_warm_no_breath,      'flute_pure_no_breath')
    render(3, v3_triangle_voyager_safe,     'triangle_voyager_safe')
    render(4, v4_triangle_octave_down,      'triangle_octave_down')
    render(5, v5_flute_warm_tool_delays,    'flute_warm_TOOL_delays')
    render(6, v6_flute_minimal,             'flute_minimal_drone_only')
    render(7, v7_layered_octave_warm_bright,'triangle_layered_OCTAVE_LOW_plus_high')
    render(8, v8_triangle_original_lpf1500, 'triangle_original_LPF1500_attenuated')
    print()
    print('Escuchá los 6 en lab/. La fórmula común: bass+drone+reverb corto.')
    print('Lo único que cambia es el INSTRUMENTO/REGISTRO.')


if __name__ == '__main__':
    main()
