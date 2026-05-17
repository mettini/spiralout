"""Outbound v0 — prototipo 60s, variante BALANCED (cinematic + dub emergente).

Arquitectura: 10 tracks, dirty intro (capsule -> clean), heart pulse al final.
Renderea master + stems en out/outbound/.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))      # transmissions/01
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))    # repo root
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track
from aem.synth import sine, noise
from aem.instruments import detuned_drone, voice_pad, kick, melody, riser
from aem.effects import fade, lpf, reverb, distort
from aem.master import dirty_intro

DURATION = 60
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'outbound')
NAME = 'outbound_v0'

comp = Composition(DURATION, name='Outbound v0 - balanced')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

sub = comp.add_track(Track('sub_42hz', gain=0.50, color='#3a4a5c'))
sub.add(0, sine(42, DURATION, 1.0))
sub.fx(lambda a: fade(a, fi=8, fo=8))

cosmos = comp.add_track(Track('cosmos', gain=0.30, color='#5a5a5a'))
cosmos.add(2, lpf(noise(58, 1.0), 600))
cosmos.fx(lambda a: fade(a, fi=6, fo=8))

drone = comp.add_track(Track('drone_d_minor', gain=0.40, color='#7a5cb8'))
drone.add(12, detuned_drone([146.83, 174.61, 220.00], 48))
drone.fx(lambda a: fade(a, fi=4, fo=6))
drone.fx(lambda a: reverb(a, decay=3.0, mix=0.4))

voyager_clear = comp.add_track(Track('voyager_clear', gain=0.45, pan=+0.3, color='#e6c34d'))
voyager_clear.add(18, melody(VOYAGER_NOTES, amp=0.4))
voyager_clear.fx(lambda a: reverb(a, decay=4.0, mix=0.5))


def voyager_deg():
    low_notes = [(f / 2, d) for f, d in VOYAGER_NOTES]
    raw = melody(low_notes, amp=0.5)
    return distort(lpf(raw, 1500), amount=2.5)


voyager_alien = comp.add_track(Track('voyager_degraded', gain=0.40, pan=-0.3, color='#a04030'))
voyager_alien.add(35, voyager_deg())
voyager_alien.fx(lambda a: reverb(a, decay=5.0, mix=0.6))

sub_drone = comp.add_track(Track('sub_drone', gain=0.40, color='#2c3a4c'))
sub_drone.add(25, detuned_drone([73.42, 87.31], 35))
sub_drone.fx(lambda a: fade(a, fi=6, fo=4))

voices_l = comp.add_track(Track('voices_l_d4', gain=0.32, pan=-0.5, color='#c87a8c'))
voices_l.add(30, voice_pad(293.66, 30, vibrato_rate=4.0, amp=0.4))
voices_l.fx(lambda a: fade(a, fi=8, fo=4))
voices_l.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

voices_r = comp.add_track(Track('voices_r_a4', gain=0.32, pan=+0.5, color='#c87a8c'))
voices_r.add(30, voice_pad(440.00, 30, vibrato_rate=4.5, amp=0.4))
voices_r.fx(lambda a: fade(a, fi=8, fo=4))
voices_r.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

pulse = comp.add_track(Track('heart_pulse_60bpm', gain=0.55, color='#d04545'))
for i in range(14):
    pulse.add(45 + i * 1.0, kick(amp=1.0, dur=0.7, f0=70, fe=30))
pulse.fx(lambda a: reverb(a, decay=2.5, mix=0.35))

risers_track = comp.add_track(Track('risers', gain=0.20, color='#909090'))
risers_track.add(10, riser())
risers_track.add(28, riser())
risers_track.add(43, riser())
risers_track.fx(lambda a: lpf(a, 2000))
risers_track.fx(lambda a: reverb(a, decay=3.0, mix=0.4))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    master_fx = lambda a: dirty_intro(a, dirty_until=8, transition_dur=4)
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'), master_fx=master_fx)
    comp.export_stems(os.path.join(OUT, 'stems', NAME), master_fx=master_fx)
