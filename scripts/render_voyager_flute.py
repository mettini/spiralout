"""Renderiza el voyager motif con flute_traversa sintetica.

Output: transmissions/01/release/lab/voyager_flute_*.wav
  - voyager_flute_dry.wav     — sin efectos (para escuchar el timbre puro)
  - voyager_flute_cosmic.wav  — con reverb gigante + delay (luz Galadriel)
"""

import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.instruments import flute_motif
from aem.motifs import VOYAGER_NOTES, VOYAGER_ASCENDING
from aem.effects import reverb, fade

OUT_DIR = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'release', 'lab')
os.makedirs(OUT_DIR, exist_ok=True)

LEAD = 1.0
TRAIL = 8.0


def render_motif(notes, name, cosmic=False):
    motif_dur = sum(d for _, d in notes)
    duration = LEAD + motif_dur + TRAIL
    comp = Composition(duration, name=f'Voyager FLUTE {name}')

    voy = comp.add_track(Track('voyager_flute', gain=0.55, pan=0.0))
    audio = flute_motif(notes, amp=0.45, vibrato=True,
                         attack_ms=80, release_ms=250,
                         breath_amount=0.04, chiff_amount=0.06)
    voy.add(LEAD, fade(audio, fi=0.3, fo=0.5))

    if cosmic:
        # Reverb gigante (espacial / cosmica)
        voy.fx(lambda a: reverb(a, decay=6.0, mix=0.55))
        # Eco distante
        echo = comp.add_track(Track('voyager_flute_echo', gain=0.25, pan=-0.3))
        echo.add(LEAD + 0.350, fade(audio * 0.5, fi=0.4, fo=0.5))   # delay 350ms L
        echo.fx(lambda a: reverb(a, decay=8.0, mix=0.7))
        echo2 = comp.add_track(Track('voyager_flute_echo_r', gain=0.18, pan=+0.4))
        echo2.add(LEAD + 0.700, fade(audio * 0.4, fi=0.4, fo=0.5))  # delay 700ms R
        echo2.fx(lambda a: reverb(a, decay=8.0, mix=0.7))
    else:
        voy.fx(lambda a: reverb(a, decay=2.0, mix=0.20))   # reverb minimo

    audio_out = comp.render_stereo()
    suffix = 'cosmic' if cosmic else 'dry'
    out_path = os.path.join(OUT_DIR, f'voyager_flute_{name}_{suffix}.wav')
    sf.write(out_path, audio_out, SR, subtype='PCM_24')
    print(f'  -> {out_path}  ({duration:.1f}s)')


def main():
    print('=== Render Voyager FLUTE TRAVERSA ===')
    render_motif(VOYAGER_NOTES, 'main', cosmic=False)
    render_motif(VOYAGER_NOTES, 'main', cosmic=True)
    render_motif(VOYAGER_ASCENDING, 'ascending', cosmic=False)
    render_motif(VOYAGER_ASCENDING, 'ascending', cosmic=True)


if __name__ == '__main__':
    main()
