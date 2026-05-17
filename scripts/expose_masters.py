"""Expone los masters del release al player web.

Para cada master en release/masters/, crea una composicion de 1 track
en out/<theme>/stems/<theme>_MASTER/ que apunta al WAV via symlink.
Despues de correr esto + index:rebuild, los masters aparecen en el
dropdown del player.

Uso:
  python3 scripts/expose_masters.py [--tx 01]
"""

import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def expose_master(tx_dir, theme, master_path):
    """Expone un master al player creando manifest + symlink al wav."""
    comp_id = f'{theme}_MASTER'
    target_dir = os.path.join(tx_dir, 'out', theme, 'stems', comp_id)
    os.makedirs(target_dir, exist_ok=True)

    # Symlink al wav (rapido, no copia)
    wav_link = os.path.join(target_dir, 'master.wav')
    if os.path.lexists(wav_link):
        os.remove(wav_link)
    os.symlink(master_path, wav_link)

    # Manifest de 1 track
    audio, sr = sf.read(master_path)
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=-1)
    duration = len(audio) / sr
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))

    manifest = {
        'name': f'{theme.title()} (master)',
        'duration': duration,
        'sample_rate': sr,
        'norm_factor': 1.0,
        'tracks': [{
            'name': 'master',
            'file': 'master.wav',
            'gain': 1.0,
            'pan': 0.0,
            'color': '#a6d65f',
            'peak': peak,
            'rms': rms,
        }],
    }
    with open(os.path.join(target_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'  exposed {theme.upper()} master -> out/{theme}/stems/{comp_id}/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tx', default='01')
    args = ap.parse_args()

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    masters_dir = os.path.join(tx_dir, 'release', 'masters')

    if not os.path.isdir(masters_dir):
        print(f'ERROR: no existe {masters_dir} — corre task master:bounce:all primero',
              file=sys.stderr)
        sys.exit(1)

    # Mapping master file -> theme name
    mapping = {
        '01_outbound_master.wav': 'outbound',
        '02_crossing_master.wav': 'crossing',
        '03_recursion_master.wav': 'recursion',
    }

    print(f'\n=== expose:masters (transmission {args.tx}) ===\n')
    for filename, theme in mapping.items():
        master_path = os.path.join(masters_dir, filename)
        if os.path.exists(master_path):
            expose_master(tx_dir, theme, master_path)
        else:
            print(f'  skip {theme}: no existe {filename}')

    # Tambien el continuous como pseudo-tema
    continuous = os.path.join(masters_dir, '00_heliopause_continuous.wav')
    if os.path.exists(continuous):
        # Lo expongo bajo "outbound" como un comp_id especial: heliopause_CONTINUOUS
        comp_id = 'heliopause_CONTINUOUS'
        target_dir = os.path.join(tx_dir, 'out', 'outbound', 'stems', comp_id)
        os.makedirs(target_dir, exist_ok=True)
        wav_link = os.path.join(target_dir, 'master.wav')
        if os.path.lexists(wav_link):
            os.remove(wav_link)
        os.symlink(continuous, wav_link)
        audio, sr = sf.read(continuous)
        if audio.ndim == 1:
            audio = np.stack([audio, audio], axis=-1)
        manifest = {
            'name': 'Heliopause (continuous EP master)',
            'duration': len(audio) / sr,
            'sample_rate': sr,
            'norm_factor': 1.0,
            'tracks': [{
                'name': 'master', 'file': 'master.wav',
                'gain': 1.0, 'pan': 0.0, 'color': '#a6d65f',
                'peak': float(np.max(np.abs(audio))),
                'rms': float(np.sqrt(np.mean(audio ** 2))),
            }],
        }
        with open(os.path.join(target_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f'  exposed CONTINUOUS -> out/outbound/stems/{comp_id}/')


if __name__ == '__main__':
    main()
