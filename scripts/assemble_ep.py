"""Concatena los 3 masters del EP en un master continuo de 24:00 con
crossfades entre temas. La pieza queda como "una sola transmision continua"
(concept del EP en docs/02_ep.md).

Workflow:
  outbound (8:00) | crossfade 8s | crossing (13:00) | crossfade 8s | recursion (3:00)

  Resultado: 8:00 + 12:52 + 2:52 = 23:44 (con los crossfades superpuestos)

  Si el EP se reproduce en repeat, los ultimos segundos de recursion ya
  encajan con el sub_42hz inicial del outbound (concept "loop" del EP).

Uso:
  python3 scripts/assemble_ep.py [--tx 01] [--crossfade 8.0]

Salida:
  transmissions/<tx>/release/masters/00_heliopause_continuous.wav (24-bit, 44.1)
"""

import argparse
import os
import sys

import numpy as np
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def crossfade(a, b, fade_samples):
    """Crossfade entre dos arrays estereo. fade_samples=0 = concat directo."""
    if fade_samples == 0:
        return np.concatenate([a, b])
    if fade_samples > len(a):
        fade_samples = len(a)
    if fade_samples > len(b):
        fade_samples = len(b)

    fade_out = np.linspace(1.0, 0.0, fade_samples).reshape(-1, 1)
    fade_in = np.linspace(0.0, 1.0, fade_samples).reshape(-1, 1)

    a_tail = a[-fade_samples:] * fade_out
    b_head = b[:fade_samples] * fade_in
    overlap = a_tail + b_head

    return np.concatenate([
        a[:-fade_samples],
        overlap,
        b[fade_samples:],
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tx', default='01')
    ap.add_argument('--crossfade', type=float, default=0.0,
                    help='duracion del crossfade entre temas (segundos). Default 0 — '
                         'los tracks tienen fade in/out propios, asi el total cuadra '
                         'a 24:00 exactos (480+780+180=1440s).')
    args = ap.parse_args()

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    masters_dir = os.path.join(tx_dir, 'release', 'masters')

    inputs = [
        os.path.join(masters_dir, '01_outbound_master.wav'),
        os.path.join(masters_dir, '02_crossing_master.wav'),
        os.path.join(masters_dir, '03_recursion_master.wav'),
    ]
    output = os.path.join(masters_dir, '00_heliopause_continuous.wav')

    for f in inputs:
        if not os.path.exists(f):
            print(f'ERROR: no existe {f} — corré task master:bounce:all primero',
                  file=sys.stderr)
            sys.exit(1)

    print(f'\n=== ep:assemble (crossfade {args.crossfade}s) ===')
    audios = []
    sr = None
    for f in inputs:
        a, file_sr = sf.read(f)
        if sr is None:
            sr = file_sr
        elif sr != file_sr:
            print(f'ERROR: SR distinto entre archivos ({sr} vs {file_sr})',
                  file=sys.stderr)
            sys.exit(1)
        if a.ndim == 1:
            a = np.stack([a, a], axis=-1)
        audios.append(a)
        print(f'  read  {os.path.basename(f)} · {len(a) / sr:.2f}s')

    fade_samples = int(args.crossfade * sr)

    # Concatenar con crossfades acumulativos
    out = audios[0]
    for next_audio in audios[1:]:
        out = crossfade(out, next_audio, fade_samples)
        print(f'  + crossfade {args.crossfade}s · acumulado {len(out) / sr:.2f}s')

    # Write 24-bit
    sf.write(output, out, sr, subtype='PCM_24')
    print(f'\n  write {output}')
    print(f'        duracion total: {len(out) / sr:.2f}s '
          f'({int(len(out) / sr // 60)}:{int(len(out) / sr % 60):02d})')


if __name__ == '__main__':
    main()
