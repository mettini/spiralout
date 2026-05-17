"""Crossing v1 — DUNE CHANT (90s prototype, estilo Hans Zimmer Sardaukar).

Foco: el chant_drone vocal grave es el PROTAGONISTA. Notas D2/A2 sostenidas
con vibrato lento y formantes acentuados (armonicos 2,4,7) — suena vocal
ritual sin ser una voz real.

Acompanado de drone Dm sostenido + mellotron-like pad alto sutil.
Sin percusion. Reverb largo (6s) en el chant.

Te tiene que dar sensacion de Sardaukar Chant — coro grave ritual.
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
    detuned_drone, voice_pad, bell, granular_pulse, sub_rumble, chant_drone,
)
from aem.effects import fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp

DURATION = 90
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'crossing')
NAME = 'crossing_v1'

comp = Composition(DURATION, name='Crossing v1 - DUNE CHANT')

rng = np.random.default_rng(13)


def drone_event(notes, dur, fi=8, fo=8, amp=0.4, n_voices=3, detune_cents=10):
    return fade(detuned_drone(notes, dur, amp=amp,
                              n_voices=n_voices, detune_cents=detune_cents),
                fi=fi, fo=fo)


# ============================================================================
# SUB-BASS moderado (35 Hz) — base, no protagonista
# ============================================================================

# 01. SUB RUMBLE 35Hz
sub = comp.add_track(Track('sub_rumble_35', gain=0.35, color='#1a1a2c'))
sub.add(0, sub_rumble(freq=35, dur=DURATION, mod_rate=0.12, mod_depth=0.4))
sub.fx(lambda a: fade(a, fi=10, fo=15))


# ============================================================================
# DRONE Dm sostenido — bed armonico
# ============================================================================

# 02. DRONE Dm
drone = comp.add_track(Track('drone_dm', gain=0.32, color='#3a2a4c'))
drone.add(2, drone_event([146.83, 174.61, 220.00], 85, fi=15, fo=15))
drone.fx(lambda a: reverb(a, decay=6.0, mix=0.55))


# ============================================================================
# CHANT — el protagonista. Notas graves Sardaukar-style.
# Patron: D2 sostenido (largo) -> A2 (largo) -> F2 (largo) -> D2 cierre
# ============================================================================

# 03. CHANT D2 entrada — paneada centro-izq
chant_main = comp.add_track(Track('chant_D2', gain=0.50, pan=-0.15, color='#5a3a4a'))
chant_main.add(8, fade(chant_drone(freq=73.42, dur=30, vibrato_rate=1.6,
                                    vibrato_depth=0.014, amp=0.50,
                                    n_harmonics=8, formant_emphasis=(2, 4, 7)),
                       fi=8, fo=10))
chant_main.fx(lambda a: lpf(a, 1800))
chant_main.fx(lambda a: reverb(a, decay=6.5, mix=0.65))

# 04. CHANT A2 desarrollo — paneada centro-der (responde al D2)
chant_resp = comp.add_track(Track('chant_A2', gain=0.45, pan=+0.20, color='#6a4a5a'))
chant_resp.add(28, fade(chant_drone(freq=110.00, dur=30, vibrato_rate=1.8,
                                     vibrato_depth=0.013, amp=0.50,
                                     n_harmonics=8, formant_emphasis=(2, 5, 7)),
                        fi=8, fo=12))
chant_resp.fx(lambda a: lpf(a, 1800))
chant_resp.fx(lambda a: reverb(a, decay=6.5, mix=0.65))

# 05. CHANT F2 climax — pan centro
chant_climax = comp.add_track(Track('chant_F2', gain=0.45, pan=0, color='#8a5a6a'))
chant_climax.add(50, fade(chant_drone(freq=87.31, dur=30, vibrato_rate=1.5,
                                       vibrato_depth=0.015, amp=0.50,
                                       n_harmonics=8, formant_emphasis=(2, 4, 6)),
                          fi=10, fo=15))
chant_climax.fx(lambda a: lpf(a, 1800))
chant_climax.fx(lambda a: reverb(a, decay=7.0, mix=0.70))


# ============================================================================
# MELLOTRON-LIKE PAD ALTO — luz tenue por encima del chant
# ============================================================================

# 06. MELLOTRON PAD alto (D5+A5) — sutil
mellotron = comp.add_track(Track('mellotron_pad', gain=0.22, pan=+0.3, color='#b0a0d0'))
mellotron.add(20, fade(voice_pad(587.33, 60, vibrato_rate=2.5, amp=0.35), fi=12, fo=15))
mellotron.add(20, fade(voice_pad(880.00, 60, vibrato_rate=2.8, amp=0.30), fi=12, fo=15))
mellotron.fx(lambda a: reverb(a, decay=7.5, mix=0.7))


# ============================================================================
# COSMIC BED — noise filtrado bajo, siempre presente
# ============================================================================

# 07. COSMIC BED
cosmic = comp.add_track(Track('cosmic_bed', gain=0.10, color='#3a3a4a'))
cosmic.add(0, lpf(noise(DURATION, 1.0), 500))
cosmic.fx(lambda a: lfo_amp(a, rate_hz=0.07, depth=0.5, offset=0.7))
cosmic.fx(lambda a: fade(a, fi=10, fo=15))


# ============================================================================
# BELL ritualistic — un solo bell grave en el centro del tema
# ============================================================================

# 08. RITUAL BELL
ritual = comp.add_track(Track('ritual_bell', gain=0.40, color='#d8c060'))
ritual.add(45, bell(220.00, dur=15, amp=0.55, decay_rate=1.0))  # A3 sostenido
ritual.fx(lambda a: reverb(a, decay=8.0, mix=0.7))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
