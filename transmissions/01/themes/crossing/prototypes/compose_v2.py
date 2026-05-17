"""Crossing v2 — VOID DRIFT (90s prototype).

Foco: sensacion de DERIVAR en el espacio interestelar. Heart beat MUY
suave (40 BPM, respiracion no cardiaco). Passing objects: 4-5 whooshes
paneados de L->R o R->L que "pasan cerca". Magia ocasional con granular
pulses agudos (algo brillante muy lejos).

Sub-bass moderado, drone Dm sostenido muy quieto. Sin chant protagonista.
Reverb medio (5s).
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
    detuned_drone, voice_pad, kick, granular_pulse, sub_rumble, whoosh, bell,
)
from aem.effects import fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'crossing')
NAME = 'crossing_v2'

comp = Composition(DURATION, name='Crossing v2 - VOID DRIFT')

rng = np.random.default_rng(13)


def drone_event(notes, dur, fi=8, fo=8, amp=0.4, n_voices=3, detune_cents=10):
    return fade(detuned_drone(notes, dur, amp=amp,
                              n_voices=n_voices, detune_cents=detune_cents),
                fi=fi, fo=fo)


# ============================================================================
# SUB-BASS suave (32 Hz) — base muy quieta
# ============================================================================

# 01. SUB RUMBLE 32Hz
sub = comp.add_track(Track('sub_rumble_32', gain=0.30, color='#1a1a2c'))
sub.add(0, sub_rumble(freq=32, dur=DURATION, mod_rate=0.08, mod_depth=0.5))
sub.fx(lambda a: fade(a, fi=10, fo=15))


# ============================================================================
# DRONE Dm muy quieto — bed
# ============================================================================

# 02. DRONE Dm bed
drone = comp.add_track(Track('drone_dm_quiet', gain=0.28, color='#3a2a4c'))
drone.add(2, drone_event([146.83, 174.61, 220.00], 85, fi=15, fo=15))
drone.fx(lambda a: lpf(a, 1200))
drone.fx(lambda a: reverb(a, decay=5.5, mix=0.55))


# ============================================================================
# HEART BEAT MUY SUAVE — 40 BPM (respiracion, no cardiaco)
# 1 kick cada 1.5s. Amp baja (0.4). LPF heavy.
# ============================================================================

# 03. HEART BEAT SUAVE
heart = comp.add_track(Track('heart_soft_40bpm', gain=0.40, color='#7c4040'))
# 40 BPM = 1 kick cada 1.5 segundos. Desde 15s a 75s = 40 kicks aprox
for i in range(40):
    t = 15 + i * 1.5
    if t > 75:
        break
    amp = 0.5 + (i / 40) * 0.2  # crece muy levemente
    heart.add(t, kick(amp=amp, dur=1.0, f0=65, fe=32))
heart.fx(lambda a: lpf(a, 180))
heart.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# PASSING OBJECTS — whooshes paneados que "pasan cerca"
# Se hace con dos tracks (L y R) con eventos del mismo whoosh desfasado:
# arrancan en L con amp full, terminan en R con amp full = parece que cruza.
# ============================================================================

# 04. PASSING OBJECTS - LEFT side (entrada del whoosh por la izquierda) — gain 0.45→0.34 por R8
pass_l = comp.add_track(Track('passing_objects_L', gain=0.34, pan=-0.6, color='#90a0b0'))
# 5 objects pasando en distintos momentos
pass_times = [12, 28, 42, 58, 72]
for t in pass_times:
    # whoosh de 2.5s — empieza fuerte en L con fade out
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=2500, direction='up')
    pass_l.add(t, fade(w, fi=0, fo=2.0))  # fade out — el sonido "se aleja" del L
pass_l.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 05. PASSING OBJECTS - RIGHT side (salida del whoosh por la derecha) — gain 0.45→0.34 por R8
pass_r = comp.add_track(Track('passing_objects_R', gain=0.34, pan=+0.6, color='#90a0b0'))
for t in pass_times:
    # mismo whoosh pero con fade in — el sonido "llega" al R
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=2500, direction='up')
    pass_r.add(t + 0.4, fade(w, fi=2.0, fo=0))  # fade in — desfasado 0.4s = movimiento L→R
pass_r.fx(lambda a: reverb(a, decay=4.0, mix=0.5))


# ============================================================================
# MAGIA — granular pulses agudos ocasionales (algo brillante muy lejos)
# ============================================================================

# 06. MAGIC PINGS
magic = comp.add_track(Track('magic_pings', gain=0.40, pan=+0.3, color='#c0e0d0'))
# Bells altos esparcidos
magic.add(20, bell(1320.00, dur=4, amp=0.45, decay_rate=2.5))   # E6 — alto y brillante
magic.add(38, bell(1760.00, dur=4, amp=0.40, decay_rate=2.8))   # A6
magic.add(55, bell(1320.00, dur=5, amp=0.45, decay_rate=2.3))
magic.add(72, bell(2093.00, dur=4, amp=0.40, decay_rate=3.0))   # C7 — muy alto
magic.fx(lambda a: reverb(a, decay=6.0, mix=0.7))


# ============================================================================
# COSMIC BED — noise filtrado, deriva
# ============================================================================

# 07. COSMIC BED
cosmic = comp.add_track(Track('cosmic_bed', gain=0.10, color='#3a3a4a'))
cosmic.add(0, lpf(noise(DURATION, 1.0), 500))
cosmic.fx(lambda a: lfo_amp(a, rate_hz=0.06, depth=0.5, offset=0.7))
cosmic.fx(lambda a: fade(a, fi=10, fo=15))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
