"""Voyager STEVE ROACH — pad ambient, capas detuneadas, espacio enorme.

Receta:
  1. Voyager motif central (triangle, notch, fade-in MUY largo, sin attack)
  2. Capa octava arriba con detune subtle (10 cents)
  3. Capa octava abajo con detune opuesto (-10 cents)
  4. Drone D2 sostenido por debajo, casi imperceptible
  5. Reverb GIGANTE (decay 12s, mix 75%) — espacio cavernoso
  6. Tremolo MUY lento (0.15 Hz, depth 0.15) sobre el conjunto = respiracion

A diferencia de Tool: el motif no es "melodia con eco", es "pad que respira".
Las notas individuales se difuminan en el aire, no marcan un beat.
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
from aem.motifs import voyager_motif, voyager_duration, VOYAGER_NOTES, VOYAGER_ASCENDING
from aem.effects import reverb, notch_eq, lfo_amp
from aem.instruments import melody, detuned_drone
from aem.master import master_chain

LEAD_SILENCE = 2.0
TRAIL_SILENCE = 12.0   # cola gigante para que el reverb respire
DURATION = LEAD_SILENCE + voyager_duration('ascending') + TRAIL_SILENCE
OUT_DIR = os.path.join(TRANSMISSION_ROOT, 'out', 'voyager_roach')
LAB_DIR = os.path.join(TRANSMISSION_ROOT, 'release', 'lab')
NAME = 'voyager_roach'

comp = Composition(DURATION, name='Voyager ROACH — pad ambient layered')


def voyager_detuned(amp, octave_shift, detune_cents):
    """Genera motif ASCENDING con detune microscopico. Release 0.6s lineal."""
    factor = (2 ** octave_shift) * (2 ** (detune_cents / 1200))
    notes = [(f * factor, d) for f, d in VOYAGER_ASCENDING]
    return melody(notes, amp=amp, vibrato=True, waveform='triangle',
                  attack=0.2, release=0.6, release_curve=1.0)


# ---- 1. Voz central ----
voy_main = comp.add_track(Track('voyager_main', gain=0.45, pan=0.0, color='#e6c34d'))
voy_main.add(LEAD_SILENCE, voyager_detuned(amp=0.35, octave_shift=0, detune_cents=0))
voy_main.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_main.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))

# ---- 2. Capa octava arriba con detune +10 cents (fattness) ----
voy_up = comp.add_track(Track('voyager_up_+10c', gain=0.18, pan=-0.3, color='#f0d8a0'))
voy_up.add(LEAD_SILENCE, voyager_detuned(amp=0.30, octave_shift=1, detune_cents=10))
voy_up.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voy_up.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voy_up.fx(lambda a: notch_eq(a, freq_hz=1046.50, q=10, gain_db=-12))
voy_up.fx(lambda a: notch_eq(a, freq_hz=2093.00, q=10, gain_db=-12))
voy_up.fx(lambda a: notch_eq(a, freq_hz=3520.00, q=10, gain_db=-9))   # 4to harm de A5

# ---- 3. Capa octava abajo con detune -10 cents ----
voy_dn = comp.add_track(Track('voyager_down_-10c', gain=0.30, pan=+0.3, color='#c89058'))
voy_dn.add(LEAD_SILENCE, voyager_detuned(amp=0.35, octave_shift=-1, detune_cents=-10))

# ---- 4. Drone D2 sostenido por debajo ----
drone = comp.add_track(Track('drone_d2', gain=0.20, color='#5c4a8a'))
drone.add(0.5, detuned_drone([73.42], DURATION - 1.0, amp=0.35,
                              n_voices=3, detune_cents=8))

# ---- 5. Reverb conservador con pre-delay (espacio sin wash sucio) ----
# Decay 7s mix 0.5 (no 12s/0.75 que pisaba todo) + pre-delay 100ms = "sala grande"
big_reverb = lambda a: reverb(a, decay=7.0, mix=0.50, pre_delay_ms=100)
voy_main.fx(big_reverb)
voy_up.fx(big_reverb)
voy_dn.fx(big_reverb)
drone.fx(lambda a: reverb(a, decay=6.0, mix=0.4, pre_delay_ms=100))

# ---- 6. Tremolo lentisimo sobre cada voz (respiracion ambient) ----
slow_tremolo = lambda a: lfo_amp(a, rate_hz=0.15, depth=0.15)
voy_main.fx(slow_tremolo)
voy_up.fx(slow_tremolo)
voy_dn.fx(slow_tremolo)


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
        'name': '★ MASTER · Voyager ROACH · pad ambient + reverb gigante',
        'duration': len(audio) / sr,
        'sample_rate': sr,
        'norm_factor': 1.0,
        'tracks': [{'name': 'master', 'file': 'master.wav',
                    'gain': 1.0, 'pan': 0.0, 'color': '#a08bc8',
                    'peak': final_peak, 'rms': rms}],
    }
    with open(os.path.join(expose_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'  expose: {expose_dir}')
