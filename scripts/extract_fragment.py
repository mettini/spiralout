"""Extrae un fragmento de tiempo de los stems de un tema y crea una nueva
composition con los stems aislados, exponible al player con mute/solo por track.

Uso:
  python3.10 scripts/extract_fragment.py outbound 130 150 \\
    --name fragment_outbound_2_10_2_30
"""

import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('theme', help='outbound | crossing | recursion')
    ap.add_argument('start', type=float, help='inicio del fragmento (segundos)')
    ap.add_argument('end', type=float, help='fin del fragmento (segundos)')
    ap.add_argument('--name', default=None,
                    help='nombre del fragmento (default fragment_<start>_<end>)')
    ap.add_argument('--tx', default='01')
    args = ap.parse_args()

    if args.name is None:
        args.name = f'fragment_{int(args.start)}_{int(args.end)}'

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    stems_dir = os.path.join(tx_dir, 'out', args.theme, 'stems', f'{args.theme}_FULL')
    if not os.path.exists(stems_dir):
        print(f'ERROR: no existe {stems_dir}', file=sys.stderr)
        sys.exit(1)

    with open(os.path.join(stems_dir, 'manifest.json')) as f:
        original_manifest = json.load(f)

    out_dir = os.path.join(tx_dir, 'out', args.theme, 'stems', args.name)
    os.makedirs(out_dir, exist_ok=True)

    duration = args.end - args.start
    new_tracks = []
    sr = None
    skipped = []
    for track in original_manifest['tracks']:
        src = os.path.join(stems_dir, track['file'])
        if not os.path.exists(src):
            continue
        audio, sr = sf.read(src)
        s_start = int(args.start * sr)
        s_end = int(args.end * sr)
        if s_start >= len(audio):
            skipped.append((track['name'], 'fuera de rango'))
            continue
        s_end = min(s_end, len(audio))
        clip = audio[s_start:s_end]
        if np.max(np.abs(clip)) < 1e-6:
            skipped.append((track['name'], 'silencio total'))
            continue
        out_file = os.path.join(out_dir, track['file'])
        sf.write(out_file, clip, sr)
        peak = float(np.max(np.abs(clip)))
        rms = float(np.sqrt(np.mean(clip ** 2)))
        new_tracks.append({**track, 'peak': peak, 'rms': rms})

    new_manifest = {
        'name': args.name,
        'duration': duration,
        'sample_rate': sr,
        'norm_factor': original_manifest.get('norm_factor', 1.0),
        'tracks': new_tracks,
    }
    with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
        json.dump(new_manifest, f, indent=2)

    print(f'\nFragment extraido: {out_dir}')
    print(f'  duracion: {duration}s ({args.start}s - {args.end}s)')
    print(f'  tracks activos: {len(new_tracks)}')
    print(f'  skipped: {len(skipped)}')
    for name, reason in skipped:
        print(f'    - {name}: {reason}')


if __name__ == '__main__':
    main()
