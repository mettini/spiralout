"""Crossing v0 — DARK MASS (90s prototype, estilo Lustmord — Heresy).

Foco en TEXTURAS de masa cosmica. Sub-bass profundo (28 Hz), drones D minor
con clusters disonantes, field recording style noise denso. Sin melodia,
sin ritmo. Inmersion total — como estar dentro de una catacumba.

Reverbs muy largos (8s decay). Distortion sutil en los drones graves
para "saturacion cosmica". Granular noise denso simulando field recording.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.synth import sine, noise
from aem.instruments import (
    detuned_drone, voice_pad, granular_pulse, sub_rumble, chant_drone,
)
from aem.effects import fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'crossing')
NAME = 'crossing_v0'

comp = Composition(DURATION, name='Crossing v0 - DARK MASS')

rng = np.random.default_rng(13)


def drone_event(notes, dur, fi=8, fo=8, amp=0.4, n_voices=3, detune_cents=10):
    return fade(detuned_drone(notes, dur, amp=amp,
                              n_voices=n_voices, detune_cents=detune_cents),
                fi=fi, fo=fo)


# ============================================================================
# SUB-BASS profundo (28 Hz) — la presencia grave casi inaudible
# ============================================================================

# 01. SUB RUMBLE 28Hz
sub = comp.add_track(Track('sub_rumble_28', gain=0.45, color='#1a1a2c'))
sub.add(0, sub_rumble(freq=28, dur=DURATION, mod_rate=0.1, mod_depth=0.5))
sub.fx(lambda a: fade(a, fi=8, fo=12))

# 02. SUB RUMBLE 35Hz (capa adicional, ligera disonancia con 28)
sub2 = comp.add_track(Track('sub_rumble_35', gain=0.30, color='#2a2a3c'))
sub2.add(5, sub_rumble(freq=35, dur=80, mod_rate=0.12, mod_depth=0.4))
sub2.fx(lambda a: fade(a, fi=10, fo=15))


# ============================================================================
# DRONES D MINOR con clusters disonantes
# ============================================================================

# 03. DRONE Dm grave
drone_low = comp.add_track(Track('drone_dm_low', gain=0.42, color='#3a2a4c'))
drone_low.add(2, drone_event([73.42, 87.31, 110.00], 85, fi=12, fo=15))  # D2-F2-A2
drone_low.fx(lambda a: distort(a, amount=1.4))  # saturacion cosmica
drone_low.fx(lambda a: reverb(a, decay=8.0, mix=0.6))

# 04. DRONE Dm medio + cluster (Bb agrega disonancia)
drone_mid = comp.add_track(Track('drone_dm_cluster', gain=0.32, color='#4a3a5c'))
drone_mid.add(15, drone_event([146.83, 174.61, 220.00, 233.08], 65, fi=15, fo=15))
drone_mid.fx(lambda a: lpf(a, 1500))
drone_mid.fx(lambda a: reverb(a, decay=8.0, mix=0.6))


# ============================================================================
# FIELD-RECORDING STYLE NOISE — granular denso (textura de cripta)
# ============================================================================

# 05. FIELD ATMOSPHERE — granular noise filtrado lento (gain bajado a 0.13 por R8/AP2)
field = comp.add_track(Track('field_atmosphere', gain=0.13, color='#3a3a3a'))
field.add(0, lpf(np.random.randn(DURATION * SR), 400))
field.fx(lambda a: lfo_amp(a, rate_hz=0.06, depth=0.6, offset=0.6))
field.fx(lambda a: fade(a, fi=10, fo=20))

# 06. GRANULAR DENSO — pulses cortos pasa-banda en frecuencias bajas (gain subido a 0.55)
granular = comp.add_track(Track('granular_dark', gain=0.55, color='#5a4a4a'))
gr_freqs = [80, 120, 200, 280, 380]
t = 8
while t < 80:
    freq = rng.choice(gr_freqs)
    granular.add(t, granular_pulse(freq=freq, dur=0.5 + rng.random() * 0.5, amp=0.5))
    t += 1.5 + rng.random() * 2  # muy denso
granular.fx(lambda a: lpf(a, 800))
granular.fx(lambda a: reverb(a, decay=6.0, mix=0.6))


# ============================================================================
# CHANT — leve, secundario en este v0 (en v1 sera protagonista)
# ============================================================================

# 07. CHANT secundario (apenas audible)
chant = comp.add_track(Track('chant_secondary', gain=0.22, pan=-0.2, color='#5a3a4a'))
chant.add(30, chant_drone(freq=87.31, dur=40, vibrato_rate=1.5, amp=0.45))  # F2
chant.fx(lambda a: fade(a, fi=15, fo=15))
chant.fx(lambda a: lpf(a, 1200))
chant.fx(lambda a: reverb(a, decay=8.0, mix=0.7))


# ============================================================================
# COSMIC SWELLS — peaks puntuales de noise filtrado (el espacio respira)
# ============================================================================

# 08. COSMIC SWELLS
def cosmic_swell(dur=8, peak_amp=0.55, cutoff=600):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    raw = lpf(np.random.randn(n), cutoff)
    env = np.sin(np.pi * ta / dur) ** 2
    return raw * env * peak_amp

swells = comp.add_track(Track('cosmic_swells', gain=0.45, color='#6a5a6a'))
swells.add(20, cosmic_swell(dur=8))
swells.add(45, cosmic_swell(dur=10))
swells.add(70, cosmic_swell(dur=8))
swells.fx(lambda a: reverb(a, decay=7.0, mix=0.7))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
