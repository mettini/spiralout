"""QA perceptual — detecta problemas que el QA espectral NO ve.

3 detectores:

  T_TRANSIENT_STACK: peak instantaneo en el master (jump sample-level) que
    supera N veces la mediana local. Detecta "TICs" causados por multiples
    transients coincidiendo (ej. 2-3 layers cambiando de nota juntas).

  T_LAYER_DENSITY: numero de stems con energia significativa en una ventana
    de tiempo. > N stems simultaneos = "esto satura, demasiadas capas".

  T_MELODIC_OVERLAP: correlacion cruzada entre pares de stems en ventanas
    deslizantes. Correlacion alta = las voces estan tocando lo mismo (efecto
    "varias cornetas superpuestas que no van").

Uso:
  python3.10 scripts/qa_scan_perceptual.py <wav> [--start S] [--end S]
  task qa:perceptual
"""

import argparse
import os
import sys

import numpy as np
from scipy.io import wavfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- thresholds ---
TRANSIENT_JUMP_RATIO = 4.0       # jump > N * mediana(local) = transient anomalo
TRANSIENT_MIN_ABS_JUMP = 0.025   # jump < this no se reporta (silencio)
DENSITY_PEAK_THRESH = 0.05       # stem con peak > este es "activo"
DENSITY_MAX_STEMS = 8            # > N stems activos en una ventana = warning
WINDOW_DENSITY_S = 1.0
WINDOW_OVERLAP_S = 1.0
OVERLAP_CORR_THRESH = 0.55       # pearson > este = stems tocando lo mismo
OVERLAP_MIN_RMS = 0.02           # ignorar pares donde uno de los dos es casi silencio


def load_mono(path):
    sr, x = wavfile.read(path)
    if x.ndim == 2:
        x = x.mean(axis=-1)
    if x.dtype.kind == 'i':
        x = x.astype(np.float32) / np.iinfo(x.dtype).max
    else:
        x = x.astype(np.float32)
    return sr, x


def fmt_t(t):
    m = int(t // 60)
    s = t - m * 60
    return f'{m}:{s:05.2f}'


# ---------------------------------------------------------------------------
# T_TRANSIENT_STACK
# ---------------------------------------------------------------------------

def scan_transients(x, sr, t_start, t_end):
    """Scan jumps sample-level. Devuelve [(t, jump, ratio_vs_local_median)]."""
    n_start = int(t_start * sr)
    n_end = int(t_end * sr)
    seg = x[n_start:n_end]
    if len(seg) < 100:
        return []
    jumps = np.abs(np.diff(seg))
    # Mediana local en ventanas de 0.5s
    win_n = int(0.5 * sr)
    hits = []
    last_t = -1.0
    for i in range(0, len(jumps), win_n // 4):
        win = jumps[max(0, i - win_n // 2):min(len(jumps), i + win_n // 2)]
        if len(win) < 100:
            continue
        med = float(np.median(win))
        if med < 1e-9:
            continue
        # Pico maximo en la ventana
        local_idx = np.argmax(jumps[i:i + win_n // 4]) if i + win_n // 4 <= len(jumps) else 0
        actual_idx = i + local_idx
        if actual_idx >= len(jumps):
            continue
        peak_jump = float(jumps[actual_idx])
        if peak_jump < TRANSIENT_MIN_ABS_JUMP:
            continue
        ratio = peak_jump / med
        if ratio < TRANSIENT_JUMP_RATIO:
            continue
        t = t_start + actual_idx / sr
        # Deduplicate: si el ultimo hit fue muy reciente (<0.1s), saltar
        if t - last_t < 0.1:
            continue
        hits.append((t, peak_jump, ratio))
        last_t = t
    return hits


# ---------------------------------------------------------------------------
# T_LAYER_DENSITY + T_MELODIC_OVERLAP — usan stems
# ---------------------------------------------------------------------------

def scan_density(stems_dir, t_start, t_end):
    """Cuenta cuantos stems estan 'activos' (peak > thresh) por ventana de 1s."""
    if not os.path.isdir(stems_dir):
        return []
    # Cargar todos los stems
    stems = {}
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith('.wav'):
            continue
        try:
            sr, x = load_mono(os.path.join(stems_dir, f))
        except Exception:
            continue
        stems[f] = (sr, x)
    if not stems:
        return []

    # Ventanas
    sr_ref = next(iter(stems.values()))[0]
    win_n = int(WINDOW_DENSITY_S * sr_ref)
    hits = []
    t = t_start
    while t < t_end:
        active = []
        for name, (sr, x) in stems.items():
            n_s = int(t * sr)
            n_e = n_s + win_n
            if n_s >= len(x):
                continue
            seg = x[n_s:min(n_e, len(x))]
            if len(seg) < 100:
                continue
            peak = float(np.max(np.abs(seg)))
            if peak >= DENSITY_PEAK_THRESH:
                active.append((name, peak))
        if len(active) > DENSITY_MAX_STEMS:
            hits.append((t, len(active), [n for n, _ in active]))
        t += WINDOW_OVERLAP_S
    return hits


def scan_melodic_overlap(stems_dir, t_start, t_end):
    """Cross-correlation pearson entre pares de stems en ventanas. Detecta voces
    tocando lo mismo (corr > thresh)."""
    if not os.path.isdir(stems_dir):
        return []
    stems = {}
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith('.wav'):
            continue
        try:
            sr, x = load_mono(os.path.join(stems_dir, f))
        except Exception:
            continue
        stems[f] = (sr, x)
    if not stems:
        return []

    # Filtrar solo stems "melodicos" (no drones/sub) — heuristica por nombre
    melodic_keywords = ['voyager', 'bell', 'flute', 'voice', 'melody', 'lead',
                          'main', 'chant', 'mellotron', 'shimmer', 'pad']
    filtered = {n: v for n, v in stems.items()
                if any(k in n.lower() for k in melodic_keywords)}
    if len(filtered) < 2:
        return []

    sr_ref = next(iter(filtered.values()))[0]
    win_n = int(2.0 * sr_ref)   # ventana 2s
    hits = []
    t = t_start
    while t < t_end - 2:
        n_s = int(t * sr_ref)
        n_e = n_s + win_n
        # Para cada stem, segmento + verificar RMS minimo
        segs = {}
        for name, (sr, x) in filtered.items():
            if n_s >= len(x):
                continue
            seg = x[n_s:min(n_e, len(x))]
            if len(seg) < 100:
                continue
            rms = float(np.sqrt(np.mean(seg ** 2)))
            if rms < OVERLAP_MIN_RMS:
                continue
            segs[name] = seg
        # Pares
        names = sorted(segs.keys())
        pairs_high = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = segs[names[i]], segs[names[j]]
                m = min(len(a), len(b))
                if m < 100:
                    continue
                # Pearson
                a, b = a[:m], b[:m]
                am, bm = a - a.mean(), b - b.mean()
                denom = np.sqrt((am ** 2).sum() * (bm ** 2).sum()) + 1e-12
                corr = float((am * bm).sum() / denom)
                if abs(corr) >= OVERLAP_CORR_THRESH:
                    pairs_high.append((names[i], names[j], corr))
        if pairs_high:
            hits.append((t, pairs_high))
        t += 2.0
    return hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav', help='path al master WAV')
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--no-transients', action='store_true')
    ap.add_argument('--no-density', action='store_true')
    ap.add_argument('--no-overlap', action='store_true')
    args = ap.parse_args()

    if not os.path.exists(args.wav):
        print(f'ERROR: no existe {args.wav}', file=sys.stderr)
        sys.exit(2)

    sr, x = load_mono(args.wav)
    end = args.end if args.end else len(x) / sr
    print(f'=== QA perceptual: {os.path.basename(args.wav)} ===')
    print(f'  rango: [{fmt_t(args.start)}, {fmt_t(end)}]')

    fail = False
    wav_dir = os.path.dirname(args.wav)
    parent = os.path.dirname(wav_dir)
    wav_basename = os.path.splitext(os.path.basename(args.wav))[0]
    stems_dir = os.path.join(parent, 'stems', wav_basename)

    # 1. T_TRANSIENT_STACK
    if not args.no_transients:
        hits = scan_transients(x, sr, args.start, end)
        if hits:
            fail = True
            print(f'\n[T_TRANSIENT_STACK] {len(hits)} transientes anomalos:')
            for t, jump, ratio in hits[:20]:
                print(f'  {fmt_t(t):>8s}  jump={jump:.4f}  ratio={ratio:.1f}x median')
            if len(hits) > 20:
                print(f'  ... y {len(hits)-20} mas')
        else:
            print(f'\n[T_TRANSIENT_STACK] OK')

    # 2. T_LAYER_DENSITY
    if not args.no_density:
        hits = scan_density(stems_dir, args.start, end)
        if hits:
            fail = True
            print(f'\n[T_LAYER_DENSITY] {len(hits)} ventanas con > {DENSITY_MAX_STEMS} stems activos:')
            for t, n, names in hits[:15]:
                print(f'  {fmt_t(t):>8s}  {n} stems: {", ".join(names[:6])}{"..." if len(names)>6 else ""}')
            if len(hits) > 15:
                print(f'  ... y {len(hits)-15} mas')
        else:
            print(f'\n[T_LAYER_DENSITY] OK')

    # 3. T_MELODIC_OVERLAP
    if not args.no_overlap:
        hits = scan_melodic_overlap(stems_dir, args.start, end)
        if hits:
            fail = True
            print(f'\n[T_MELODIC_OVERLAP] {len(hits)} ventanas con voces tocando lo mismo (corr >= {OVERLAP_CORR_THRESH}):')
            for t, pairs in hits[:15]:
                for a, b, c in pairs[:3]:
                    print(f'  {fmt_t(t):>8s}  corr={c:+.2f}  {a} <-> {b}')
            if len(hits) > 15:
                print(f'  ... y {len(hits)-15} ventanas mas')
        else:
            print(f'\n[T_MELODIC_OVERLAP] OK')

    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
