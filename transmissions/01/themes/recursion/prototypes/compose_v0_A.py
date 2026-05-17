"""Recursion v0 — A: BLACK MASS RETURN (90s prototype, Sunn O))) drone metal).

Wall of sound 0:00-0:35 → peak 0:35-0:45 → despeje 0:45-1:10 → voyager
limpio 1:10-1:35 → cierre 1:35-1:30.

Distortion masiva, sub-bass agresivo, feedback simulado, tempo extremo lento.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.synth import sine
from aem.instruments import (
    detuned_drone, melody, bell, sub_rumble,
    wall_of_sound, feedback_squeal, downlifter,
)
from aem.effects import fade, lpf, reverb, distort, amp_envelope

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'recursion')
NAME = 'recursion_v0_A'

comp = Composition(DURATION, name='Recursion v0 - A: BLACK MASS RETURN')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

# ============================================================================
# WALL OF SOUND (0:00 - 0:45) — Sunn O))) catedral colapsando
# ============================================================================

# 01. WALL principal — D2 + A1 con distortion masivo
wall = comp.add_track(Track('wall_of_sound', gain=0.55, color='#1a0a14'))
wall.add(0, wall_of_sound(root_freqs=[55.00, 73.42], dur=50,
                          distortion=4.5, n_layers=5, amp=0.5))
wall.fx(lambda a: amp_envelope(a, [(0, 0.0), (5, 1.0), (35, 1.0), (50, 0.0)]))
wall.fx(lambda a: lpf(a, 1500))  # masa baja
wall.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 02. SUB punisher 28Hz — base agresiva
sub = comp.add_track(Track('sub_punisher', gain=0.50, color='#2a0a14'))
sub.add(0, sub_rumble(freq=28, dur=50, mod_rate=0.2, mod_depth=0.5))
sub.fx(lambda a: distort(a, amount=2.0))
sub.fx(lambda a: amp_envelope(a, [(0, 0.0), (3, 1.0), (40, 1.0), (50, 0.0)]))

# 03. FEEDBACK SQUEAL — nota alta inestable arriba del wall
fb = comp.add_track(Track('feedback_squeal', gain=0.30, pan=+0.3, color='#5a3030'))
fb.add(15, feedback_squeal(freq=1480, dur=25, sweep_depth=0.025, sweep_rate=0.4,
                           amp=0.45, decay_rate=0.15))
fb.fx(lambda a: reverb(a, decay=4.0, mix=0.5))


# ============================================================================
# EL DESPEJE (0:45 - 1:10) — la distortion se va, aparece luz
# ============================================================================

# 04. DOWNLIFTER — sweep descendente que "calma" el wall
down = comp.add_track(Track('downlifter_release', gain=0.40, color='#7a5050'))
down.add(45, downlifter(dur=10, f_start=400, f_end=80, amp=0.6))
down.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 05. DRONE Dm limpio que emerge — primer signo de luz
drone_clean = comp.add_track(Track('drone_dm_emerge', gain=0.55, color='#7a5cb8'))
drone_clean.add(48, fade(detuned_drone([146.83, 174.61, 220.00], 35, amp=0.45), fi=12, fo=10))
drone_clean.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# VOYAGER REGRESA (1:10 - 1:30) — la melodía limpia, revelación
# ============================================================================

# 06. VOYAGER limpio — el regreso
voyager = comp.add_track(Track('voyager_return', gain=0.55, pan=+0.2, color='#e6c34d'))
voyager.add(70, melody(VOYAGER_NOTES, amp=0.55))
voyager.fx(lambda a: reverb(a, decay=5.5, mix=0.55))

# 07. BELL D5 — closure marker
bells = comp.add_track(Track('closure_bell', gain=0.45, color='#d8c060'))
bells.add(75, bell(587.33, dur=15, amp=0.55, decay_rate=1.2))  # D5 sostenido
bells.fx(lambda a: reverb(a, decay=7.0, mix=0.65))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
