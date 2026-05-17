"""Recursion v1 — B: GHOST IN THE MACHINE (90s prototype, Burial-style glitch).

Perturbacion psicologica 0:00-0:50 → despeje 0:50-1:10 → voyager fragil
1:10-1:35 → cierre 1:35-1:30.

Glitches cortos, vinyl crackle constante, voces invertidas, broken beats
fragmentados. Dark ambient sutil — tension psicologica sin saturar.
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
    detuned_drone, voice_pad, kick, melody, bell, sub_rumble,
    vinyl_crackle, glitch_burst, pitch_jitter_melody,
)
from aem.effects import fade, lpf, hpf, reverb, lfo_amp

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'recursion')
NAME = 'recursion_v1_B'

comp = Composition(DURATION, name='Recursion v1 - B: GHOST IN THE MACHINE')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

rng = np.random.default_rng(11)

# ============================================================================
# PERTURBACION (0:00 - 0:50) — paranoia psicologica
# ============================================================================

# 01. VINYL CRACKLE — capa constante de fondo (bed)
crackle = comp.add_track(Track('vinyl_crackle', gain=0.45, color='#3a3030'))
crackle.add(0, vinyl_crackle(dur=DURATION, density=0.35, amp=0.30, base_hiss=0.04, seed=42))
crackle.fx(lambda a: hpf(a, 800))  # solo highs (clicks)
crackle.fx(lambda a: reverb(a, decay=2.0, mix=0.3))

# 02. GLITCH BURSTS — bursts cortos esparcidos en los primeros 50s
glitches = comp.add_track(Track('glitch_bursts', gain=0.50, pan=-0.2, color='#5a3a4a'))
glitch_times = [3, 7, 11, 14, 18, 22, 27, 30, 34, 38, 42, 46]
glitch_freqs = [400, 1200, 800, 2400, 600, 1800, 350, 1500, 900, 1100, 700, 2000]
for t, f in zip(glitch_times, glitch_freqs):
    glitches.add(t, glitch_burst(dur=0.10 + rng.random() * 0.08,
                                  freq_center=f, bandwidth=0.4, amp=0.5))
glitches.fx(lambda a: reverb(a, decay=2.5, mix=0.4))

# 03. SUB MUTED — drone bajo oscuro
sub = comp.add_track(Track('sub_dark', gain=0.35, color='#1a1a2c'))
sub.add(0, sub_rumble(freq=42, dur=DURATION, mod_rate=0.1, mod_depth=0.4))
sub.fx(lambda a: fade(a, fi=8, fo=10))

# 04. DRONE Dm sostenido — bed armonico
drone = comp.add_track(Track('drone_dm_dark', gain=0.45, color='#3a2a4c'))
drone.add(2, fade(detuned_drone([146.83, 174.61, 220.00], 75, amp=0.45), fi=12, fo=15))
drone.fx(lambda a: lpf(a, 1200))
drone.fx(lambda a: reverb(a, decay=5.0, mix=0.55))

# 05. BROKEN BEAT — kicks fragmentados sin patron (paranoia)
broken_beats = comp.add_track(Track('broken_beat', gain=0.40, color='#5c2a2a'))
beat_times = [5, 13, 16, 24, 31, 39, 41]  # patron irregular
for t in beat_times:
    broken_beats.add(t, kick(amp=0.7, dur=0.6, f0=70, fe=32))
broken_beats.fx(lambda a: lpf(a, 200))
broken_beats.fx(lambda a: reverb(a, decay=3.5, mix=0.45))

# 06. REVERSE-LIKE VOICE (voice_pad con fade reverso) — voz inquietante
def reverse_voice_event(freq, dur, amp=0.35):
    raw = voice_pad(freq, dur, vibrato_rate=3.0, amp=amp, n_harmonics=4)
    return fade(raw[::-1], fi=dur * 0.6, fo=dur * 0.05)  # fade in largo, out abrupto

reverse_voice = comp.add_track(Track('reverse_voice', gain=0.50, pan=+0.3, color='#5a4070'))
reverse_voice.add(8, reverse_voice_event(440.00, 6))
reverse_voice.add(20, reverse_voice_event(587.33, 6))
reverse_voice.add(35, reverse_voice_event(440.00, 5))
reverse_voice.fx(lambda a: lpf(a, 1500))
reverse_voice.fx(lambda a: reverb(a, decay=5.0, mix=0.6))


# ============================================================================
# EL DESPEJE (0:50 - 1:10) — los glitches se van, drone limpio emerge
# ============================================================================

# 07. DRONE LIMPIO emerge — sin LPF heavy
drone_clean = comp.add_track(Track('drone_clean_emerge', gain=0.32, color='#7a5cb8'))
drone_clean.add(50, fade(detuned_drone([146.83, 174.61, 220.00], 35), fi=12, fo=8))
drone_clean.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# VOYAGER FRAGIL (1:10 - 1:30) — melodia con pitch jitter
# ============================================================================

# 08. VOYAGER FRAGIL — pitch shift random ±5 cents por nota
voyager_fragil = comp.add_track(Track('voyager_fragile', gain=0.50, pan=+0.2, color='#c8a050'))
voyager_fragil.add(70, pitch_jitter_melody(VOYAGER_NOTES, amp=0.50, jitter_cents=6, seed=13))
voyager_fragil.fx(lambda a: lpf(a, 2200))
voyager_fragil.fx(lambda a: reverb(a, decay=6.0, mix=0.65))

# 09. ULTIMO CRACKLE — un click final fuerte como "fin de transmision"
final_crackle = comp.add_track(Track('final_crackle', gain=0.70, color='#909090'))
final_crackle.add(85, glitch_burst(dur=0.5, freq_center=800, bandwidth=0.6, amp=0.7))
final_crackle.fx(lambda a: reverb(a, decay=4.0, mix=0.6))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
