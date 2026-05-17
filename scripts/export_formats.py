"""Convierte los WAV masters (44.1 / 24-bit) a los formatos de release:
  - FLAC (lossless, para Bandcamp HQ + preservacion)
  - MP3 320 kbps CBR (preview / SoundCloud)
  - WAV 16-bit / 44.1 (para CD Baby si lo pide)

Uso:
  python3 scripts/export_formats.py [--tx 01]

Salida:
  transmissions/<tx>/release/distribution/flac/
  transmissions/<tx>/release/distribution/mp3/
  transmissions/<tx>/release/distribution/wav_16/
"""

import argparse
import os
import sys
import subprocess

import soundfile as sf
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def export_flac(input_wav, output_flac):
    """FLAC lossless preservando 24-bit."""
    audio, sr = sf.read(input_wav)
    sf.write(output_flac, audio, sr, format='FLAC', subtype='PCM_24')
    print(f'  flac  → {os.path.basename(output_flac)} (24-bit, {sr} Hz)')


def export_wav_16(input_wav, output_wav):
    """WAV 16-bit (estandar CD)."""
    audio, sr = sf.read(input_wav)
    sf.write(output_wav, audio, sr, subtype='PCM_16')
    print(f'  wav16 → {os.path.basename(output_wav)} (16-bit, {sr} Hz)')


def export_mp3_320(input_wav, output_mp3):
    """MP3 320 kbps CBR via ffmpeg."""
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'error',
        '-i', input_wav,
        '-codec:a', 'libmp3lame', '-b:a', '320k',
        output_mp3,
    ]
    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(output_mp3) / (1024 * 1024)
    print(f'  mp3   → {os.path.basename(output_mp3)} (320 kbps, {size_mb:.1f} MB)')


# Mapping de filename del master a nombre clean para distribucion
TRACK_NAMES = {
    '01_outbound_master.wav': 'Outbound',
    '02_crossing_master.wav': 'Crossing',
    '03_recursion_master.wav': 'Recursion',
    '00_heliopause_continuous.wav': 'Heliopause (continuous)',
}


def clean_name(master_filename):
    """01_outbound_master.wav → '01 - Outbound'"""
    base = master_filename.replace('_master.wav', '').replace('.wav', '')
    parts = base.split('_', 1)
    if len(parts) == 2 and parts[0].isdigit():
        num, name = parts
        return f'{num} - {name.replace("_", " ").title()}'
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tx', default='01')
    ap.add_argument('--skip-mp3', action='store_true', help='no exportar MP3 (mas rapido)')
    ap.add_argument('--skip-wav16', action='store_true', help='no exportar WAV 16-bit')
    ap.add_argument('--continuous', action='store_true',
                    help='incluir el heliopause_continuous (sino solo los 3 tracks)')
    args = ap.parse_args()

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    masters_dir = os.path.join(tx_dir, 'release', 'masters')
    dist_dir = os.path.join(tx_dir, 'release', 'distribution')

    flac_dir = os.path.join(dist_dir, 'flac')
    mp3_dir = os.path.join(dist_dir, 'mp3')
    wav16_dir = os.path.join(dist_dir, 'wav_16')
    os.makedirs(flac_dir, exist_ok=True)
    os.makedirs(mp3_dir, exist_ok=True)
    os.makedirs(wav16_dir, exist_ok=True)

    # Listar masters de los tracks individuales (01_, 02_, 03_)
    master_files = sorted([
        f for f in os.listdir(masters_dir)
        if f.startswith(('01_', '02_', '03_')) and f.endswith('.wav')
    ])

    if args.continuous:
        cont = '00_heliopause_continuous.wav'
        if os.path.exists(os.path.join(masters_dir, cont)):
            master_files = [cont] + master_files

    print(f'\n=== export:formats ({len(master_files)} archivos) ===')

    for f in master_files:
        input_wav = os.path.join(masters_dir, f)
        clean = clean_name(f)
        print(f'\n* {clean}')
        export_flac(input_wav, os.path.join(flac_dir, f'{clean}.flac'))
        if not args.skip_mp3:
            export_mp3_320(input_wav, os.path.join(mp3_dir, f'{clean}.mp3'))
        if not args.skip_wav16:
            export_wav_16(input_wav, os.path.join(wav16_dir, f'{clean}.wav'))

    print(f'\nDistribucion lista en: {dist_dir}')


if __name__ == '__main__':
    main()
