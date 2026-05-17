"""Recursion v2 — C: ETERNAL RECURRENCE (90s prototype, Steve Reich phase music).

Apertura 0:00-0:20 → primer loop sincronizado 0:20-0:35 → desfase
gradual 0:35-1:10 → convergencia 1:10-1:25 → cierre 1:25-1:30.

Loops del fragment voyager (D5-F5-A5) en dos voces L/R, una se desfasa
gradualmente. Aparecen ringing effects y patrones nuevos.
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
    detuned_drone, melody, bell, sub_rumble, phased_loop,
)
from aem.effects import fade, lpf, reverb, lfo_amp

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'recursion')
NAME = 'recursion_v2_C'

comp = Composition(DURATION, name='Recursion v2 - C: ETERNAL RECURRENCE')

# Loop corto del voyager: D5-F5-A5 (3 notas, ~3.5s)
LOOP_NOTES = [
    (587.33, 1.0), (698.46, 1.0), (880.00, 1.5),
]

# ============================================================================
# APERTURA (0:00 - 0:20) — drone Dm sostenido, calma
# ============================================================================

# 01. DRONE Dm bed
drone = comp.add_track(Track('drone_dm_bed', gain=0.32, color='#3a2a4c'))
drone.add(0, fade(detuned_drone([146.83, 174.61, 220.00], 88), fi=8, fo=10))
drone.fx(lambda a: reverb(a, decay=5.5, mix=0.55))

# 02. SUB suave
sub = comp.add_track(Track('sub_soft', gain=0.30, color='#1a1a2c'))
sub.add(0, sub_rumble(freq=42, dur=DURATION, mod_rate=0.08, mod_depth=0.4))
sub.fx(lambda a: fade(a, fi=8, fo=12))

# 03. COSMIC BED
cosmic = comp.add_track(Track('cosmic_bed', gain=0.10, color='#5a5a5a'))
cosmic.add(0, lpf(noise(DURATION, 1.0), 500))
cosmic.fx(lambda a: lfo_amp(a, rate_hz=0.07, depth=0.5, offset=0.7))
cosmic.fx(lambda a: fade(a, fi=10, fo=15))


# ============================================================================
# PHASE LOOPS (0:20 - 1:25) — Steve Reich phasing
# Genera dos voces: una sincronizada (L), otra desfasada (R).
# El loop dura ~3.5s. Phase shift de 8ms por loop = se va separando.
# Tras ~440 loops (= 25 min) volveria a phase 0; en 18 loops (~63s) tenes
# 144ms de offset = casi un beat completo de offset, suena DESFASADO.
# ============================================================================

PHASE_DURATION = 65  # 0:20 - 1:25
synced_audio, phased_audio = phased_loop(
    LOOP_NOTES, dur_total=PHASE_DURATION, loop_dur=3.5,
    phase_shift_ms=8, amp=0.50, vibrato=True,
)

# 04. LOOP SINCRONIZADO (L)
loop_l = comp.add_track(Track('phase_loop_synced_L', gain=0.50, pan=-0.4, color='#e6c34d'))
loop_l.add(20, fade(synced_audio, fi=4, fo=8))
loop_l.fx(lambda a: reverb(a, decay=4.5, mix=0.55))

# 05. LOOP DESFASADO (R)
loop_r = comp.add_track(Track('phase_loop_phased_R', gain=0.50, pan=+0.4, color='#c89b3a'))
loop_r.add(20, fade(phased_audio, fi=4, fo=8))
loop_r.fx(lambda a: reverb(a, decay=4.5, mix=0.55))


# ============================================================================
# CIERRE (1:25 - 1:30) — convergencia + bell final
# ============================================================================

# 06. BELL FINAL — D5 sostenido como cierre
final_bell = comp.add_track(Track('closure_bell', gain=0.50, color='#d8c060'))
final_bell.add(85, bell(587.33, dur=10, amp=0.55, decay_rate=1.0))
final_bell.fx(lambda a: reverb(a, decay=7.0, mix=0.65))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
