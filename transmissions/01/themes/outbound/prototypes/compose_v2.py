"""Outbound v2 — prototipo 60s, variante RHYTHMIC (pulse temprano, dub-techno).

Heart pulse arranca a 22s sparse, denso a 40s. Voyager se monta sobre el pulse.
Mas Donato Dozzy / Wolfgang Voigt (Gas).
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
from aem.instruments import detuned_drone, voice_pad, kick, hihat, melody, riser
from aem.effects import fade, lpf, hpf, reverb
from aem.master import dirty_intro

DURATION = 60
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'outbound')
NAME = 'outbound_v2'

comp = Composition(DURATION, name='Outbound v2 - rhythmic')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

sub = comp.add_track(Track('sub_42hz', gain=0.50, color='#3a4a5c'))
sub.add(0, sine(42, DURATION, 1.0))
sub.fx(lambda a: fade(a, fi=8, fo=8))

cosmos = comp.add_track(Track('cosmos', gain=0.28, color='#5a5a5a'))
cosmos.add(2, lpf(noise(58, 1.0), 600))
cosmos.fx(lambda a: fade(a, fi=6, fo=8))

drone = comp.add_track(Track('drone_d_minor', gain=0.38, color='#7a5cb8'))
drone.add(12, detuned_drone([146.83, 174.61, 220.00], 48))
drone.fx(lambda a: fade(a, fi=4, fo=6))
drone.fx(lambda a: reverb(a, decay=2.5, mix=0.35))

pulse = comp.add_track(Track('heart_pulse', gain=0.55, color='#d04545'))
for t in [22, 26, 30, 34, 38]:
    pulse.add(t, kick(amp=0.8, dur=0.7, f0=70, fe=30))
for i in range(20):
    t = 40 + i * 1.0
    if t >= DURATION:
        break
    pulse.add(t, kick(amp=1.0, dur=0.7, f0=70, fe=30))
pulse.fx(lambda a: reverb(a, decay=2.0, mix=0.30))

voyager = comp.add_track(Track('voyager_clear', gain=0.42, pan=+0.3, color='#e6c34d'))
voyager.add(28, melody(VOYAGER_NOTES, amp=0.4))
voyager.fx(lambda a: reverb(a, decay=3.5, mix=0.5))

sub_drone = comp.add_track(Track('sub_drone', gain=0.38, color='#2c3a4c'))
sub_drone.add(28, detuned_drone([73.42, 87.31], 32))
sub_drone.fx(lambda a: fade(a, fi=6, fo=4))

voices_l = comp.add_track(Track('voices_l_d4', gain=0.30, pan=-0.5, color='#c87a8c'))
voices_l.add(40, voice_pad(293.66, 20, vibrato_rate=4.0, amp=0.4))
voices_l.fx(lambda a: fade(a, fi=6, fo=4))
voices_l.fx(lambda a: reverb(a, decay=3.5, mix=0.5))

voices_r = comp.add_track(Track('voices_r_a4', gain=0.30, pan=+0.5, color='#c87a8c'))
voices_r.add(40, voice_pad(440.00, 20, vibrato_rate=4.5, amp=0.4))
voices_r.fx(lambda a: fade(a, fi=6, fo=4))
voices_r.fx(lambda a: reverb(a, decay=3.5, mix=0.5))

hihats = comp.add_track(Track('hihats', gain=0.22, color='#b8b8b8'))
for i in range(int((DURATION - 42) * 2)):
    t = 42 + i * 0.5 + 0.5
    if t >= DURATION - 0.1:
        break
    hihats.add(t, hihat(dur=0.05, amp=0.3))
hihats.fx(lambda a: hpf(a, 6000))
hihats.fx(lambda a: reverb(a, decay=1.5, mix=0.25))

risers_track = comp.add_track(Track('risers', gain=0.20, color='#909090'))
risers_track.add(10, riser())
risers_track.add(20, riser())
risers_track.add(38, riser())
risers_track.fx(lambda a: lpf(a, 2000))
risers_track.fx(lambda a: reverb(a, decay=2.5, mix=0.4))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    master_fx = lambda a: dirty_intro(a, dirty_until=8, transition_dur=4)
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'), master_fx=master_fx)
    comp.export_stems(os.path.join(OUT, 'stems', NAME), master_fx=master_fx)
