"""QA espectral — analiza un WAV buscando energia en banda 1.5-4 kHz
(zona Fletcher-Munson sensible) que se perciba como "fritura/estatica aguda".

Esto COMPLEMENTA qa_scan_code.py (que es estatico). Aca medimos el WAV real:
- ventaneamos el audio en frames de 50 ms con hop 25 ms
- por frame: FFT, energia en banda 1500-4000 Hz / energia total
- si ratio supera threshold (default 0.18) durante varios frames consecutivos,
  marcamos timestamp(s) sospechosos

Usage:
  python3.10 scripts/qa_scan_spectral.py <wav> [--start S] [--end S] [--diagnose]
  task qa:spectral

  --diagnose: ademas analiza cada stem del mismo directorio para identificar
    cual track contribuye mas energia en la zona caliente.
"""

import argparse
import os
import sys
import numpy as np
from scipy.io import wavfile

# Bandas analizadas:
# - HOT (1.5-4 kHz): zona Fletcher-Munson sensible — fritura aguda perceptual
# - BRIGHT (4-8 kHz): brillo punzante — armonicos altos triangle/voice_pad,
#   transientes/clicks broadband. El user reporto que "aturde" sin que la
#   banda HOT diera flag — los armonicos altos del voyager (5to+ del triangle)
#   caen aca.
HOT_LO = 1500.0
HOT_HI = 4000.0
BRIGHT_LO = 4000.0
BRIGHT_HI = 8000.0
FRAME_MS = 50.0
HOP_MS = 25.0
RATIO_THRESHOLD = 0.18    # >18% de energia en banda HOT = sospechoso
BRIGHT_RATIO_THRESHOLD = 0.10  # banda BRIGHT mas sensible (armonicos altos aturden)
MIN_CONSEC_FRAMES = 4     # minimo 4 frames consecutivos sospechosos = hit (~125 ms)


def load_wav_mono(path):
    sr, x = wavfile.read(path)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if x.dtype.kind == 'i':
        x = x.astype(np.float32) / np.iinfo(x.dtype).max
    else:
        x = x.astype(np.float32)
    return sr, x


def energy_ratio_per_frame(x, sr, t_start=0.0, t_end=None):
    """Devuelve (times, ratios_hot, ratios_bright)
    - ratios_hot: energia banda 1.5-4 kHz / total por frame
    - ratios_bright: energia banda 4-8 kHz / total por frame
    """
    if t_end is None:
        t_end = len(x) / sr
    n_start = int(t_start * sr)
    n_end = min(int(t_end * sr), len(x))
    x = x[n_start:n_end]

    frame_n = int(FRAME_MS / 1000 * sr)
    hop_n = int(HOP_MS / 1000 * sr)
    if len(x) < frame_n:
        return np.array([]), np.array([]), np.array([])
    n_frames = (len(x) - frame_n) // hop_n + 1

    freqs = np.fft.rfftfreq(frame_n, d=1.0 / sr)
    hot_mask = (freqs >= HOT_LO) & (freqs <= HOT_HI)
    bright_mask = (freqs >= BRIGHT_LO) & (freqs <= BRIGHT_HI)
    total_mask = freqs >= 50  # ignora DC y subgrave

    times = np.zeros(n_frames)
    ratios_hot = np.zeros(n_frames)
    ratios_bright = np.zeros(n_frames)
    window = np.hanning(frame_n)

    for i in range(n_frames):
        s = i * hop_n
        frame = x[s:s + frame_n] * window
        spec = np.abs(np.fft.rfft(frame)) ** 2
        total = spec[total_mask].sum() + 1e-12
        ratios_hot[i] = spec[hot_mask].sum() / total
        ratios_bright[i] = spec[bright_mask].sum() / total
        times[i] = t_start + (s + frame_n / 2) / sr

    return times, ratios_hot, ratios_bright


def find_hits(times, ratios, threshold=RATIO_THRESHOLD):
    """Devuelve lista de (t_start, t_end, peak_ratio) de runs >= threshold."""
    hits = []
    in_run = False
    run_start_idx = 0
    for i, r in enumerate(ratios):
        if r >= threshold:
            if not in_run:
                in_run = True
                run_start_idx = i
        else:
            if in_run:
                in_run = False
                run_len = i - run_start_idx
                if run_len >= MIN_CONSEC_FRAMES:
                    seg = ratios[run_start_idx:i]
                    hits.append((times[run_start_idx], times[i - 1], float(seg.max())))
    if in_run:
        run_len = len(ratios) - run_start_idx
        if run_len >= MIN_CONSEC_FRAMES:
            seg = ratios[run_start_idx:]
            hits.append((times[run_start_idx], times[-1], float(seg.max())))
    return hits


def fmt_t(t):
    m = int(t // 60)
    s = t - m * 60
    return f'{m}:{s:05.2f}'


def diagnose_stems(stems_dir, t_start, t_end, ignore_stems=None):
    """Analiza cada stem en el rango [t_start, t_end] y reporta los top
    contribuyentes de energia en banda caliente.

    ignore_stems: set de nombres de stem (sin .wav) a saltear.
    """
    if ignore_stems is None:
        ignore_stems = set()
    contributions = []
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith('.wav'):
            continue
        stem_name = os.path.splitext(f)[0]
        if stem_name in ignore_stems:
            continue
        path = os.path.join(stems_dir, f)
        try:
            sr, x = load_wav_mono(path)
        except Exception as e:
            print(f'  SKIP {f}: {e}')
            continue
        n_start = int(t_start * sr)
        n_end = min(int(t_end * sr), len(x))
        if n_start >= len(x):
            continue
        seg = x[n_start:n_end]
        # FFT del segmento entero
        if len(seg) < 256:
            continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        freqs = np.fft.rfftfreq(len(seg), d=1.0 / sr)
        hot_mask = (freqs >= HOT_LO) & (freqs <= HOT_HI)
        bright_mask = (freqs >= BRIGHT_LO) & (freqs <= BRIGHT_HI)
        hot_e = spec[hot_mask].sum()
        bright_e = spec[bright_mask].sum()
        # Score combinado (HOT pesa mas que BRIGHT)
        score = hot_e + 0.5 * bright_e
        rms = float(np.sqrt(np.mean(seg ** 2)) + 1e-12)
        contributions.append((f, score, hot_e, bright_e, rms))
    contributions.sort(key=lambda c: -c[1])
    print(f'\n=== Top contribuyentes (score = HOT + 0.5*BRIGHT) en [{fmt_t(t_start)}, {fmt_t(t_end)}] ===')
    for name, score, hot_e, bright_e, rms in contributions[:10]:
        print(f'  {name:35s}  score={score:.2e}  HOT={hot_e:.2e}  BRIGHT={bright_e:.2e}  rms={rms:.4f}')


def load_ignore_config(wav_path):
    """Lee .qa_spectral_ignore.json en el dir hermano del wav (master/../).
    Formato:
      {"ignore_ranges": [[start_s, end_s, "reason"], ...],
       "ignore_stems": ["feedback_squeal", ...]}
    """
    parent = os.path.dirname(os.path.dirname(wav_path))
    cfg_path = os.path.join(parent, '.qa_spectral_ignore.json')
    if not os.path.exists(cfg_path):
        return [], []
    import json
    with open(cfg_path) as f:
        cfg = json.load(f)
    return cfg.get('ignore_ranges', []), cfg.get('ignore_stems', [])


def filter_hits(hits, ignore_ranges):
    """Filtra hits que caen completamente dentro de algun rango ignorado."""
    if not ignore_ranges:
        return hits, []
    kept = []
    skipped = []
    for h in hits:
        t0, t1, peak = h
        ignored = False
        for rng in ignore_ranges:
            r_start, r_end = rng[0], rng[1]
            reason = rng[2] if len(rng) > 2 else 'whitelisted'
            if t0 >= r_start and t1 <= r_end:
                skipped.append((h, reason))
                ignored = True
                break
        if not ignored:
            kept.append(h)
    return kept, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav', help='archivo .wav a analizar')
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--threshold', type=float, default=RATIO_THRESHOLD,
                    help='ratio threshold para banda HOT 1.5-4 kHz')
    ap.add_argument('--bright-threshold', type=float, default=BRIGHT_RATIO_THRESHOLD,
                    help='ratio threshold para banda BRIGHT 4-8 kHz (mas sensible)')
    ap.add_argument('--diagnose', action='store_true',
                    help='analizar stems en el mismo dir buscando contribuyentes')
    ap.add_argument('--ignore-stems', nargs='*', default=[],
                    help='stems a excluir del diagnose')
    ap.add_argument('--no-ignore-config', action='store_true',
                    help='ignorar el archivo .qa_spectral_ignore.json')
    args = ap.parse_args()

    if not os.path.exists(args.wav):
        print(f'ERROR: no existe {args.wav}', file=sys.stderr)
        sys.exit(2)

    sr, x = load_wav_mono(args.wav)
    times, r_hot, r_bright = energy_ratio_per_frame(x, sr, args.start, args.end)
    hits_hot = find_hits(times, r_hot, threshold=args.threshold)
    hits_bright = find_hits(times, r_bright, threshold=args.bright_threshold)

    # Cargar whitelist
    ignore_ranges, ignore_stems_cfg = ([], [])
    if not args.no_ignore_config:
        ignore_ranges, ignore_stems_cfg = load_ignore_config(args.wav)
    hits_hot, skipped_hot = filter_hits(hits_hot, ignore_ranges)
    hits_bright, skipped_bright = filter_hits(hits_bright, ignore_ranges)
    skipped = skipped_hot + skipped_bright
    all_ignore_stems = set(args.ignore_stems) | set(ignore_stems_cfg)

    print(f'=== QA espectral: {os.path.basename(args.wav)} ===')
    print(f'  rango analizado: [{fmt_t(args.start)}, {fmt_t(args.end if args.end else len(x)/sr)}]')
    print(f'  bandas:          HOT {HOT_LO:.0f}-{HOT_HI:.0f} Hz   BRIGHT {BRIGHT_LO:.0f}-{BRIGHT_HI:.0f} Hz')
    print(f'  thresholds:      HOT={args.threshold}   BRIGHT={args.bright_threshold}')
    print(f'  frames analizados: {len(times)}')
    if skipped:
        print(f'  whitelisted ranges: {len(skipped)} hits ignorados')
        for (t0, t1, peak), reason in skipped:
            print(f'    [{fmt_t(t0)} - {fmt_t(t1)}] peak={peak:.3f}  ({reason})')

    if not hits_hot and not hits_bright:
        print('  OK — no se detectaron runs sospechosos (post-whitelist)')
        sys.exit(0)

    if hits_hot:
        print(f'\nHITS HOT 1.5-4 kHz ({len(hits_hot)}):')
        for t0, t1, peak in hits_hot:
            print(f'  [{fmt_t(t0)} - {fmt_t(t1)}]  peak ratio = {peak:.3f}')
    if hits_bright:
        print(f'\nHITS BRIGHT 4-8 kHz ({len(hits_bright)}):')
        for t0, t1, peak in hits_bright:
            print(f'  [{fmt_t(t0)} - {fmt_t(t1)}]  peak ratio = {peak:.3f}')

    # Para el diagnose, usamos el peor hit de cualquier banda
    hits = hits_hot + hits_bright

    if args.diagnose:
        # diagnosticar el peor hit (mayor peak ratio)
        worst = max(hits, key=lambda h: h[2])
        # busco stems en el mismo padre que el wav: master/../stems/<wav_basename>/
        wav_dir = os.path.dirname(args.wav)
        parent = os.path.dirname(wav_dir)
        wav_basename = os.path.splitext(os.path.basename(args.wav))[0]
        # Priorizar el dir que matchea exactamente el WAV
        preferred = os.path.join(parent, 'stems', wav_basename)
        if os.path.isdir(preferred):
            print(f'\n--- diagnose stems en {preferred} ---')
            diagnose_stems(preferred, max(0, worst[0] - 0.5), worst[1] + 0.5,
                           ignore_stems=set(args.ignore_stems))
        else:
            # fallback: cualquier subdir de stems/
            stems_root = os.path.join(parent, 'stems')
            if os.path.isdir(stems_root):
                for d in sorted(os.listdir(stems_root)):
                    full = os.path.join(stems_root, d)
                    if os.path.isdir(full):
                        print(f'\n--- diagnose stems en {full} ---')
                        diagnose_stems(full, max(0, worst[0] - 0.5), worst[1] + 0.5,
                                       ignore_stems=set(args.ignore_stems))
                        break

    sys.exit(1)


if __name__ == '__main__':
    main()
