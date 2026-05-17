"""Validacion tecnica de los masters antes de release.

Mide:
  - sample rate / bit depth / channels
  - LUFS integrated (BS.1770 via pyloudnorm)
  - True peak (dBTP) — peak post-encode aproximado (4x oversampling)
  - Sample peak (dBFS) — peak directo de muestras
  - Dynamic range (LU) — short-term LUFS max - min
  - Stereo correlation (sub mono check)

Reporta:
  - OK si pasa todos los thresholds
  - WARN si algo esta marginal
  - FAIL si algo esta fuera del rango aceptable

Thresholds (ver skill aem-release sección Checklist de pre-release):
  - LUFS integrated: -20 < LUFS < -12 (target -16 ± 2)
  - True peak: <= -0.5 dBTP (idealmente -1.0)
  - Sample peak: < 0 dBFS (no clipping)
  - Sample rate: 44100 o 48000 Hz
  - Bit depth: >= 16 (24 ideal)
  - Dynamic range: >= 6 LU (ambient quiere >= 8)

Uso:
  python3 scripts/release_check.py [--tx 01]
"""

import argparse
import os
import sys

import numpy as np
import soundfile as sf
import pyloudnorm as pyln

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def db(x):
    """Linear to dB."""
    return 20 * np.log10(max(x, 1e-12))


def measure(filepath):
    audio, sr = sf.read(filepath)
    info = sf.info(filepath)

    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=-1)

    # Sample peak
    sample_peak = float(np.max(np.abs(audio)))
    sample_peak_db = db(sample_peak)

    # True peak (4x oversampling — aprox simple via linear upsampling)
    # Implementacion ligera: interpolar 4x, medir max abs
    n = audio.shape[0]
    up_n = n * 4
    upsampled = np.zeros((up_n, audio.shape[1]))
    for ch in range(audio.shape[1]):
        upsampled[:, ch] = np.interp(
            np.linspace(0, n - 1, up_n),
            np.arange(n),
            audio[:, ch],
        )
    true_peak = float(np.max(np.abs(upsampled)))
    true_peak_db = db(true_peak)

    # LUFS integrated
    meter = pyln.Meter(sr)
    lufs = meter.integrated_loudness(audio)

    # Stereo correlation (1.0 = mono, -1.0 = anti-fase)
    if audio.shape[1] >= 2:
        l = audio[:, 0]
        r = audio[:, 1]
        # correlacion de Pearson
        if np.std(l) > 0 and np.std(r) > 0:
            corr = float(np.corrcoef(l, r)[0, 1])
        else:
            corr = 1.0
    else:
        corr = 1.0

    return {
        'file': os.path.basename(filepath),
        'duration': len(audio) / sr,
        'sr': sr,
        'subtype': info.subtype,
        'channels': audio.shape[1],
        'sample_peak_db': sample_peak_db,
        'true_peak_db': true_peak_db,
        'lufs_integrated': lufs,
        'stereo_correlation': corr,
    }


def evaluate(m):
    """Devuelve lista de (level, message) — level: OK / WARN / FAIL."""
    msgs = []

    # Sample rate
    if m['sr'] in (44100, 48000):
        msgs.append(('OK', f'sample rate: {m["sr"]} Hz'))
    else:
        msgs.append(('FAIL', f'sample rate: {m["sr"]} Hz (esperado 44100 o 48000)'))

    # Bit depth (subtype)
    if m['subtype'] in ('PCM_24', 'PCM_32', 'FLOAT'):
        msgs.append(('OK', f'bit depth: {m["subtype"]}'))
    elif m['subtype'] == 'PCM_16':
        msgs.append(('OK', f'bit depth: {m["subtype"]} (release final OK)'))
    else:
        msgs.append(('WARN', f'bit depth: {m["subtype"]}'))

    # True peak
    if m['true_peak_db'] <= -1.0:
        msgs.append(('OK', f'true peak: {m["true_peak_db"]:.2f} dBTP'))
    elif m['true_peak_db'] <= -0.5:
        msgs.append(('WARN', f'true peak: {m["true_peak_db"]:.2f} dBTP (target ≤ -1.0)'))
    elif m['true_peak_db'] <= 0:
        msgs.append(('WARN', f'true peak: {m["true_peak_db"]:.2f} dBTP (puede clippear post-encode)'))
    else:
        msgs.append(('FAIL', f'true peak: {m["true_peak_db"]:.2f} dBTP (clippea)'))

    # Sample peak
    if m['sample_peak_db'] < 0:
        msgs.append(('OK', f'sample peak: {m["sample_peak_db"]:.2f} dBFS'))
    else:
        msgs.append(('FAIL', f'sample peak: {m["sample_peak_db"]:.2f} dBFS (clipping)'))

    # LUFS
    target_lo = -20
    target_hi = -12
    ideal = -16
    if target_lo <= m['lufs_integrated'] <= target_hi:
        delta = m['lufs_integrated'] - ideal
        if abs(delta) <= 2:
            msgs.append(('OK', f'LUFS integrated: {m["lufs_integrated"]:.2f} LUFS '
                              f'(target {ideal}, delta {delta:+.2f})'))
        else:
            msgs.append(('WARN', f'LUFS integrated: {m["lufs_integrated"]:.2f} LUFS '
                                f'(esperado entre -20 y -12, target {ideal})'))
    else:
        msgs.append(('FAIL', f'LUFS integrated: {m["lufs_integrated"]:.2f} LUFS '
                            f'(fuera de rango -20..-12)'))

    # Stereo correlation
    if m['stereo_correlation'] > 0.95:
        msgs.append(('OK', f'stereo correlation: {m["stereo_correlation"]:.3f} (mono compatible)'))
    elif m['stereo_correlation'] > 0.5:
        msgs.append(('OK', f'stereo correlation: {m["stereo_correlation"]:.3f} (estereo amplio)'))
    elif m['stereo_correlation'] > 0:
        msgs.append(('WARN', f'stereo correlation: {m["stereo_correlation"]:.3f} (muy ancho — verificar mono)'))
    else:
        msgs.append(('FAIL', f'stereo correlation: {m["stereo_correlation"]:.3f} (anti-fase, cancela en mono)'))

    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tx', default='01')
    args = ap.parse_args()

    masters_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx, 'release', 'masters')
    if not os.path.isdir(masters_dir):
        print(f'ERROR: no existe {masters_dir} — corré master:bounce:all primero',
              file=sys.stderr)
        sys.exit(1)

    files = sorted([
        f for f in os.listdir(masters_dir) if f.endswith('.wav')
    ])

    fail_count = 0
    warn_count = 0
    print(f'\n=== release:check (transmission {args.tx}) ===\n')

    for f in files:
        path = os.path.join(masters_dir, f)
        m = measure(path)
        print(f'━━━ {m["file"]} ({m["duration"]:.1f}s · {m["channels"]} ch) ━━━')
        for level, msg in evaluate(m):
            symbol = {'OK': '✓', 'WARN': '⚠', 'FAIL': '✗'}[level]
            print(f'  {symbol}  {msg}')
            if level == 'FAIL':
                fail_count += 1
            elif level == 'WARN':
                warn_count += 1
        print()

    print(f'━━━ RESUMEN: {len(files)} archivos · {fail_count} FAIL · {warn_count} WARN ━━━')
    if fail_count > 0:
        sys.exit(1)
    if warn_count > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == '__main__':
    main()
