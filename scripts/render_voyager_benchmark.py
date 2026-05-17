"""Renderiza el voyager_safe aislado como benchmark de referencia.

El WAV resultante es la "version validada del voyager" contra la cual
qa_voyager_regression.py compara cualquier render futuro. Si el voyager
suena distinto al benchmark, la regresion lo detecta.

Output: transmissions/01/release/lab/voyager_safe_benchmark.wav

NO MODIFICAR sin confirmacion del user. Si el user dice "ahora me gusta MAS"
algun cambio del voyager, regenerar el benchmark con este script.
"""

import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.motifs import voyager_safe, voyager_safe_fx
from aem.effects import reverb

LEAD = 1.0
TRAIL = 6.0
DURATION = LEAD + 13.0 + TRAIL  # ascending = 13s

OUT_DIR = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'release', 'lab')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, 'voyager_safe_benchmark.wav')


def main():
    comp = Composition(DURATION, name='Voyager SAFE benchmark')

    # Track principal con voyager_safe + voyager_safe_fx (los 4 notches + LPF 2200)
    voy = comp.add_track(Track('voyager_safe_main', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_safe(amp=0.40, variation='ascending'))
    voyager_safe_fx(voy)
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

    # Render solo este track (no master chain — queremos el sonido directo)
    audio = comp.render_stereo()
    sf.write(OUT_PATH, audio, SR, subtype='PCM_24')
    print(f'  benchmark voyager_safe -> {OUT_PATH}')
    print(f'  duration={DURATION:.1f}s  variation=ascending  amp=0.40  gain=0.55')


if __name__ == '__main__':
    main()
