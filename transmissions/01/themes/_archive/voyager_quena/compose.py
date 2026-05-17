"""Voyager QUENA — el motivo Voyager como una quena espacial.

Receta:
  1. Waveform 'flute': sine + 5% del 2do harmonic + noise filtrado bandpass
     alrededor de la fundamental (simula el soplo de una quena de viento)
  2. Pitch wobble (vibrato 5 Hz) suave
  3. Release LARGO (1.0s) — cada nota se sostiene como pedal de piano,
     las colas se cruzan en el aire
  4. Notch -12 dB en A5 + 1760 Hz (anti-Fletcher-Munson)
  5. Reverb gigante (decay 10s, mix 0.65) — quena escuchada por los
     rincones del universo
  6. Tape warmth subtle — distorsion organica espacial
  7. LPF 6 kHz suave — saca lo mas estridente sin matar cuerpo

Output:
  release/lab/voyager_quena_master.wav
"""

import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.motifs import voyager_motif, voyager_duration
from aem.effects import reverb, notch_eq, lpf, tape_warm
from aem.master import master_chain

LEAD_SILENCE = 1.5
TRAIL_SILENCE = 10.0  # cola larga para que el reverb gigante respire
DURATION = LEAD_SILENCE + voyager_duration('ascending') + TRAIL_SILENCE
OUT_DIR = os.path.join(TRANSMISSION_ROOT, 'out', 'voyager_quena')
LAB_DIR = os.path.join(TRANSMISSION_ROOT, 'release', 'lab')
NAME = 'voyager_quena'

comp = Composition(DURATION, name='Voyager QUENA — flauta espacial por los rincones del universo')

# ---- Voz quena central ----
voy = comp.add_track(Track('quena_main', gain=0.55, pan=0.0, color='#e6c34d'))
voy.add(LEAD_SILENCE, voyager_motif(
    variation='ascending',  # con cumbre C6 (la "cara introspectiva del 42")
    amp=0.40,
    waveform='triangle',
    vibrato=True,
    attack=0.05,
    release=0.6,            # alineado con sonido validado del outbound
    release_curve=1.0,
))
# Anti-Fletcher-Munson: A5 + 2do harm + C6 + 2do harm (notas del ascending)
voy.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
# Reverb medio con pre-delay (sensacion de espacio sin wash)
voy.fx(lambda a: reverb(a, decay=5.0, mix=0.40, pre_delay_ms=80))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION:.1f}s  {len(comp.tracks)} tracks')
    comp.list_tracks()

    raw_wav = os.path.join(OUT_DIR, 'master', f'{NAME}_FULL.wav')
    comp.export_wav(raw_wav)
    comp.export_stems(os.path.join(OUT_DIR, 'stems', NAME))

    print('\n=== master ===')
    audio, sr = sf.read(raw_wav)
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=-1)
    headroom = 10 ** (-6.0 / 20)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (headroom / peak)
    audio = master_chain(audio, lufs_target=-16.0)
    print(f'  peak final={np.max(np.abs(audio)):.3f}')

    os.makedirs(LAB_DIR, exist_ok=True)
    master_wav = os.path.join(LAB_DIR, f'{NAME}_master.wav')
    sf.write(master_wav, audio, sr, subtype='PCM_24')
    print(f'  -> {master_wav}')

    expose_dir = os.path.join(OUT_DIR, 'stems', f'{NAME}_master_view')
    os.makedirs(expose_dir, exist_ok=True)
    wav_link = os.path.join(expose_dir, 'master.wav')
    if os.path.lexists(wav_link):
        os.remove(wav_link)
    os.symlink(master_wav, wav_link)
    final_peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))
    manifest = {
        'name': '★ MASTER · Voyager QUENA · flauta espacial',
        'duration': len(audio) / sr,
        'sample_rate': sr,
        'norm_factor': 1.0,
        'tracks': [{'name': 'master', 'file': 'master.wav',
                    'gain': 1.0, 'pan': 0.0, 'color': '#e6c34d',
                    'peak': final_peak, 'rms': rms}],
    }
    with open(os.path.join(expose_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'  expose: {expose_dir}')
