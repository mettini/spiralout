"""Voyager TOOL — versión a la Adam Jones / Justin Chancellor.

Receta:
  1. Voyager motif central (triangle, notch -12 dB en A5) — la voz principal
  2. Stereo ping-pong delay manual: dos copias paneadas L y R con offsets
     distintos (250ms y 500ms), feedback simulado bajando amp en cada eco
  3. Bajo "Wal-style": voyager octave_shift=-1 (D4/F4/A4), sine pura, pan=0,
     que sostiene la fundamental por debajo
  4. Drone sostenido de fondo: pad bajo en D2 con detune subtle
  5. Reverb plate medio (decay 3.5, mix 0.4) — espacio sin matar definicion

Output:
  release/lab/voyager_tool_master.wav (mastered)
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
from aem.effects import reverb, notch_eq
from aem.instruments import detuned_drone
from aem.master import master_chain

LEAD_SILENCE = 1.0
TRAIL_SILENCE = 6.0
DURATION = LEAD_SILENCE + voyager_duration('ascending') + TRAIL_SILENCE
OUT_DIR = os.path.join(TRANSMISSION_ROOT, 'out', 'voyager_tool')
LAB_DIR = os.path.join(TRANSMISSION_ROOT, 'release', 'lab')
NAME = 'voyager_tool'

comp = Composition(DURATION, name='Voyager TOOL — Adam Jones / Chancellor vibe')

# ---- 1. Voz central: triangle, notch -12 dB en A5 ----
voy_main = comp.add_track(Track('voyager_main', gain=0.55, pan=0.0, color='#e6c34d'))
voy_main.add(LEAD_SILENCE, voyager_motif(variation='ascending', amp=0.40, waveform='triangle', release=0.6))
voy_main.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
voy_main.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

# ---- 2. Stereo ping-pong delay: 250ms L, 500ms R, 750ms L (feedback simulado) ----
voy_delay_l = comp.add_track(Track('delay_L_250', gain=0.30, pan=-0.6, color='#a8c8d8'))
voy_delay_l.add(LEAD_SILENCE + 0.250, voyager_motif(variation='ascending', amp=0.40, waveform='triangle', release=0.6))
voy_delay_l.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_delay_l.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_delay_l.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_delay_l.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
voy_delay_l.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

voy_delay_r = comp.add_track(Track('delay_R_500', gain=0.20, pan=+0.6, color='#a8c8d8'))
voy_delay_r.add(LEAD_SILENCE + 0.500, voyager_motif(variation='ascending', amp=0.40, waveform='triangle', release=0.6))
voy_delay_r.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_delay_r.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_delay_r.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_delay_r.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
voy_delay_r.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

voy_delay_l2 = comp.add_track(Track('delay_L_750', gain=0.13, pan=-0.4, color='#a8c8d8'))
voy_delay_l2.add(LEAD_SILENCE + 0.750, voyager_motif(variation='ascending', amp=0.40, waveform='triangle', release=0.6))
voy_delay_l2.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_delay_l2.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_delay_l2.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_delay_l2.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
voy_delay_l2.fx(lambda a: reverb(a, decay=3.5, mix=0.40))

# ---- 3. Bajo "Wal-style": voyager 1 octava abajo, sine, sostiene fundamental ----
bass = comp.add_track(Track('bass_wal', gain=0.45, pan=0.0, color='#3c4a5c'))
bass.add(LEAD_SILENCE, voyager_motif(amp=0.40, octave_shift=-1, waveform='sine',
                                       vibrato=False, release=0.8))
bass.fx(lambda a: reverb(a, decay=2.5, mix=0.25))

# ---- 4. Drone sostenido D2 SIN detune (sacar zumbido vibrante) ----
drone = comp.add_track(Track('drone_d2', gain=0.10, color='#5c4a8a'))
drone.add(0.5, detuned_drone([73.42], DURATION - 1.0, amp=0.4,
                              n_voices=1, detune_cents=0))
drone.fx(lambda a: reverb(a, decay=5.0, mix=0.4))


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
        'name': '★ MASTER · Voyager TOOL · stereo delay + bajo + drone',
        'duration': len(audio) / sr,
        'sample_rate': sr,
        'norm_factor': 1.0,
        'tracks': [{'name': 'master', 'file': 'master.wav',
                    'gain': 1.0, 'pan': 0.0, 'color': '#c8a050',
                    'peak': final_peak, 'rms': rms}],
    }
    with open(os.path.join(expose_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'  expose: {expose_dir}')
