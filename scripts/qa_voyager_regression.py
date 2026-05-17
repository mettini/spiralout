"""QA de regresion del voyager — diff espectral contra benchmark.

Compara la firma espectral (FFT, banda 0-8 kHz) de un voyager_safe renderizado
ahora vs el benchmark guardado. Si la diferencia supera un umbral, falla.

Esto evita el problema de modificar el voyager_safe (o sus deps) sin darse
cuenta y degradar el sonido. Si fallaste el benchmark, hay 2 opciones:
  1. revertir el cambio
  2. regenerar el benchmark si el cambio fue intencional y aprobado por el user

Uso:
  task qa:voyager
"""

import os
import sys

import numpy as np
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BENCHMARK = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'release', 'lab',
                          'voyager_safe_benchmark.wav')

# Generamos el voyager_safe en memoria (sin master chain) para comparar
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))
from aem import Composition, Track, SR
from aem.motifs import voyager_safe, voyager_safe_fx
from aem.effects import reverb

LEAD = 1.0
TRAIL = 6.0
DURATION = LEAD + 13.0 + TRAIL

# Diferencia maxima permitida en cada banda (relativo)
MAX_BAND_DIFF = 0.15   # 15% de diferencia en energia por banda
BANDS = [(0, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000)]


def render_current():
    comp = Composition(DURATION, name='Voyager SAFE current')
    voy = comp.add_track(Track('voyager_safe_main', gain=0.55, pan=0.0))
    voy.add(LEAD, voyager_safe(amp=0.40, variation='ascending'))
    voyager_safe_fx(voy)
    voy.fx(lambda a: reverb(a, decay=3.5, mix=0.40))
    audio = comp.render_stereo()
    if audio.ndim == 2:
        audio = audio.mean(axis=-1)
    return audio


def band_energies(x, sr):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    freqs = np.fft.rfftfreq(len(x), d=1.0 / sr)
    out = []
    for lo, hi in BANDS:
        mask = (freqs >= lo) & (freqs < hi)
        out.append(spec[mask].sum())
    return np.array(out)


def main():
    if not os.path.exists(BENCHMARK):
        print(f'ERROR: no existe el benchmark en {BENCHMARK}')
        print('  Crea el benchmark con: python3.10 scripts/render_voyager_benchmark.py')
        sys.exit(2)

    bench, sr_b = sf.read(BENCHMARK, always_2d=False)
    if bench.ndim == 2:
        bench = bench.mean(axis=-1)
    cur = render_current()
    if sr_b != SR:
        print(f'WARN: sr benchmark={sr_b} != SR={SR}; comparacion puede ser imprecisa')

    # Igualamos longitudes
    n = min(len(bench), len(cur))
    bench = bench[:n]
    cur = cur[:n]

    e_bench = band_energies(bench, SR)
    e_cur = band_energies(cur, SR)

    print('=== QA Voyager Regression ===')
    print(f'  benchmark: {os.path.basename(BENCHMARK)} ({len(bench)/SR:.1f}s)')
    print(f'  current:   render in-memory ({len(cur)/SR:.1f}s)')
    print()
    print(f'  {"banda Hz":>15s}  {"E_bench":>11s}  {"E_actual":>11s}  {"diff %":>8s}  status')

    fails = []
    for (lo, hi), eb, ec in zip(BANDS, e_bench, e_cur):
        if eb < 1e-12:
            diff = 0.0 if ec < 1e-12 else float('inf')
        else:
            diff = abs(ec - eb) / eb
        status = 'OK' if diff <= MAX_BAND_DIFF else 'FAIL'
        if status == 'FAIL':
            fails.append((lo, hi, diff))
        print(f'  {lo:5d}-{hi:<5d}     {eb:.3e}  {ec:.3e}  {diff*100:7.2f}%  {status}')

    if fails:
        print()
        print(f'BLOQUEANTE — {len(fails)} banda(s) divergen del benchmark > {MAX_BAND_DIFF*100:.0f}%:')
        for lo, hi, d in fails:
            print(f'  banda {lo}-{hi} Hz: diff {d*100:.1f}%')
        print()
        print('Posibles causas:')
        print('  - cambio en voyager_safe()/voyager_safe_fx() en framework/aem/motifs.py')
        print('  - cambio en melody()/voyager_motif() defaults')
        print('  - cambio en notch_eq() o lpf() implementacion')
        print()
        print('Acciones posibles:')
        print('  1. Revertir el cambio que rompio el benchmark.')
        print('  2. Si el cambio es intencional y aprobado por el user,')
        print('     regenerar: python3.10 scripts/render_voyager_benchmark.py')
        sys.exit(1)

    print()
    print('OK — voyager_safe matchea benchmark dentro del umbral')


if __name__ == '__main__':
    main()
