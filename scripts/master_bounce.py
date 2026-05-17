"""Aplica master_chain a un tema renderizado y exporta WAV 24-bit.

Workflow:
  1. Lee el WAV scratch (ya tiene dirty_intro y demas master_fx aplicados,
     normalizado a peak 0.85).
  2. Atenua a peak target (default -6 dBFS = 0.5 lineal) para dar headroom
     al master chain.
  3. Aplica master_chain: HPF 25Hz + glue compression + soft limiter -1dBTP
     + LUFS normalize a -16.
  4. Escribe WAV 24-bit en transmissions/<tx>/release/masters/.

Uso:
  python3 scripts/master_bounce.py <theme> [--lufs -16] [--tx 01]
  ej: python3 scripts/master_bounce.py outbound

Salida:
  transmissions/01/release/masters/0X_<theme>_master.wav
"""

import argparse
import os
import sys

import numpy as np
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem.master import master_chain  # noqa: E402

# Orden narrativo del EP — para los prefijos numericos
THEME_ORDER = {'outbound': '01', 'crossing': '02', 'recursion': '03'}


def db_to_linear(db):
    return 10 ** (db / 20)


def bounce(input_wav, output_wav, lufs_target=-16.0, headroom_db=-12.0):
    audio, sr = sf.read(input_wav)
    print(f'  read  {input_wav}')
    print(f'        sr={sr} Hz · shape={audio.shape} · peak={np.max(np.abs(audio)):.3f}')

    # Asegurar estereo
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=-1)

    # Atenuar a headroom (dejar espacio al master chain)
    headroom = db_to_linear(headroom_db)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (headroom / peak)
    print(f'        atenuado a peak {headroom:.3f} ({headroom_db:.1f} dBFS)')

    # Aplicar master chain
    audio = master_chain(audio, lufs_target=lufs_target)
    final_peak = np.max(np.abs(audio))
    print(f'        master chain aplicada · peak final={final_peak:.3f}')

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)

    # Write WAV 24-bit
    sf.write(output_wav, audio, sr, subtype='PCM_24')
    print(f'  write {output_wav} (24-bit, LUFS target={lufs_target})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('theme', help='outbound, crossing, recursion')
    ap.add_argument('--tx', default='01', help='transmission')
    ap.add_argument('--lufs', type=float, default=-16.0, help='LUFS target')
    ap.add_argument('--headroom-db', type=float, default=-12.0,
                    help='Headroom antes del master chain (dB). -12 da mas '
                         'espacio para que peaks no claven el limiter en climax.')
    args = ap.parse_args()

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    input_wav = os.path.join(tx_dir, 'out', args.theme, 'master',
                             f'{args.theme}_FULL.wav')
    prefix = THEME_ORDER.get(args.theme, args.theme)
    output_wav = os.path.join(tx_dir, 'release', 'masters',
                              f'{prefix}_{args.theme}_master.wav')

    if not os.path.exists(input_wav):
        print(f'ERROR: no existe {input_wav}', file=sys.stderr)
        sys.exit(1)

    print(f'\n=== master:bounce {args.theme} (LUFS {args.lufs}) ===')
    bounce(input_wav, output_wav, lufs_target=args.lufs, headroom_db=args.headroom_db)


if __name__ == '__main__':
    main()
