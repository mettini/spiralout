"""Outbound v1 — prototipo 60s, variante TEXTURE (sin pulse, todo voces y drones).

Climax es un peak textural, no ritmico. Mas Steve Roach / Stars of the Lid.
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
from aem.instruments import detuned_drone, voice_pad, melody, riser
from aem.effects import fade, lpf, reverb
from aem.master import dirty_intro

DURATION = 60
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'outbound')
NAME = 'outbound_v1'

comp = Composition(DURATION, name='Outbound v1 - texture')

SACRED_NOTES = [
    (587.33, 2.5), (698.46, 2.0), (880.00, 2.5), (698.46, 2.0),
    (587.33, 3.0), (440.00, 3.0),
]

sub = comp.add_track(Track('sub_42hz', gain=0.50, color='#3a4a5c'))
sub.add(0, sine(42, DURATION, 1.0))
sub.fx(lambda a: fade(a, fi=8, fo=8))

cosmos = comp.add_track(Track('cosmos', gain=0.30, color='#5a5a5a'))
cosmos.add(2, lpf(noise(58, 1.0), 600))
cosmos.fx(lambda a: fade(a, fi=6, fo=8))

drone = comp.add_track(Track('drone_d_minor', gain=0.45, color='#7a5cb8'))
drone.add(12, detuned_drone([146.83, 174.61, 220.00], 48))
drone.fx(lambda a: fade(a, fi=5, fo=6))
drone.fx(lambda a: reverb(a, decay=4.5, mix=0.55))

voyager = comp.add_track(Track('voyager_sacred', gain=0.45, pan=+0.3, color='#e6c34d'))
voyager.add(20, melody(SACRED_NOTES, amp=0.4))
voyager.fx(lambda a: reverb(a, decay=5.5, mix=0.6))

sub_drone = comp.add_track(Track('sub_drone', gain=0.45, color='#2c3a4c'))
sub_drone.add(28, detuned_drone([73.42, 87.31, 110.00], 32))
sub_drone.fx(lambda a: fade(a, fi=6, fo=4))

voices_l = comp.add_track(Track('voices_l_d4', gain=0.40, pan=-0.5, color='#c87a8c'))
voices_l.add(30, voice_pad(293.66, 30, vibrato_rate=4.0, amp=0.45))
voices_l.fx(lambda a: fade(a, fi=8, fo=4))
voices_l.fx(lambda a: reverb(a, decay=5.0, mix=0.6))

voices_r = comp.add_track(Track('voices_r_a4', gain=0.40, pan=+0.5, color='#c87a8c'))
voices_r.add(30, voice_pad(440.00, 30, vibrato_rate=4.5, amp=0.45))
voices_r.fx(lambda a: fade(a, fi=8, fo=4))
voices_r.fx(lambda a: reverb(a, decay=5.0, mix=0.6))

voices_c = comp.add_track(Track('voices_c_d5', gain=0.32, color='#d8a0b0'))
voices_c.add(42, voice_pad(587.33, 18, vibrato_rate=5.0, amp=0.4))
voices_c.fx(lambda a: fade(a, fi=8, fo=4))
voices_c.fx(lambda a: reverb(a, decay=5.0, mix=0.6))

risers_track = comp.add_track(Track('risers', gain=0.20, color='#909090'))
risers_track.add(10, riser())
risers_track.add(28, riser())
risers_track.add(40, riser())
risers_track.fx(lambda a: lpf(a, 2000))
risers_track.fx(lambda a: reverb(a, decay=3.5, mix=0.45))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    master_fx = lambda a: dirty_intro(a, dirty_until=8, transition_dur=4)
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'), master_fx=master_fx)
    comp.export_stems(os.path.join(OUT, 'stems', NAME), master_fx=master_fx)
