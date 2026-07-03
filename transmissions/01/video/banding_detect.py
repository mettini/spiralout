#!/usr/bin/env python3
"""
Banding detection v2 — basado en "flat-plateau-in-gradient-zone" signature.

Diferencia banding de design features:
  - BANDING: gradient local CERO (plateau plano) dentro de zona que globalmente
    sí tiene gradiente. Step jumps entre plateaus.
  - DESIGN FEATURE (halos, curvas): gradient no-cero EN TODOS LADOS por curvatura
    continua.

Algoritmo:
  1. luma = 0.299*R + 0.587*G + 0.114*B
  2. grad_local = |∇luma| (1-pixel gradient magnitude)
  3. luma_blurred = Gauss(luma, sigma=blur_sigma)
     grad_global = |∇luma_blurred| (large-scale gradient direction)
  4. in_gradient_zone = grad_global > zone_threshold
  5. flat_plateau    = grad_local < plateau_threshold
  6. banded_pixel    = in_gradient_zone AND flat_plateau

Score = % de pixels in_gradient_zone que son flat_plateau.

Uso:
  ./banding_detect.py <video.mp4> [--interval 10]
  ./banding_detect.py --test          # corre contra el test bench
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, laplace


def _run_stats_1d(arr_int: np.ndarray) -> tuple:
    """Returns (max_run_length, n_transitions) para arr."""
    if arr_int.size == 0:
        return 0, 0
    diffs = np.diff(arr_int)
    change_idx = np.where(diffs != 0)[0]
    n_transitions = len(change_idx)
    if change_idx.size == 0:
        return arr_int.size, 0
    runs = np.diff(np.concatenate([[-1], change_idx, [arr_int.size - 1]]))
    return int(runs.max()), n_transitions


def detect_wide_bands(luma: np.ndarray,
                      ds: int = 4,
                      min_plateau_px: int = 96,
                      max_step: float = 2.0) -> dict:
    """v12 — bandas ANCHAS (>= ~100 px) que el análisis por patches no ve.

    El patch de 128 px es ciego a bandas más anchas que el patch: con
    pendientes de 268-800 px/nivel (medidas en bloom 4:25-4:45 de outbound
    v11) un patch cae entero ADENTRO de una banda y reporta "flat". Acá
    trabajamos a nivel de línea completa:

      1. Box-downscale ds× (promedia grain/dither → queda la señal base).
      2. Por cada fila y columna: smooth 1D suave + round a niveles 8-bit.
      3. Run-lengths: dos plateaus ADYACENTES, ambos >= min_plateau_px,
         con step entre ellos de 1..max_step niveles = banda ancha.

    Nota semántica: esto es PREDICTIVO. Un gradiente con dither perfecto
    también flaggea si su señal subyacente es demasiado chata, porque
    YouTube (VP9 8-bit ~20Mbps) borra el dither/grain y la banda aparece
    igual. La única defensa real es señal con más rango o estructura de
    baja frecuencia — no más ruido. Ver docs/video/27_fable_review_plan.
    """
    from scipy.ndimage import gaussian_filter1d
    H, W = luma.shape
    Hc, Wc = (H // ds) * ds, (W // ds) * ds
    small = luma[:Hc, :Wc].reshape(Hc // ds, ds, Wc // ds, ds).mean(axis=(1, 3))
    min_run = max(2, min_plateau_px // ds)

    def _line_band_pairs(line):
        sm = gaussian_filter1d(line, sigma=1.5)
        q = np.round(sm).astype(np.int32)
        change = np.where(np.diff(q) != 0)[0]
        if change.size == 0:
            return 0, 0
        starts = np.concatenate([[0], change + 1])
        ends = np.concatenate([change + 1, [q.size]])
        lens = ends - starts
        vals = q[starts]
        pairs = 0
        worst = 0
        for i in range(len(vals) - 1):
            if lens[i] >= min_run and lens[i + 1] >= min_run:
                step = abs(int(vals[i + 1]) - int(vals[i]))
                if 0 < step <= max_step and not (vals[i] <= 2 and vals[i + 1] <= 2):
                    pairs += 1
                    worst = max(worst, int(min(lens[i], lens[i + 1])))
        return pairs, worst

    n_lines = 0
    n_banded_lines = 0
    worst_plateau = 0
    for row in small:
        p, w = _line_band_pairs(row)
        n_lines += 1
        n_banded_lines += (p > 0)
        worst_plateau = max(worst_plateau, w)
    for col in small.T:
        p, w = _line_band_pairs(col)
        n_lines += 1
        n_banded_lines += (p > 0)
        worst_plateau = max(worst_plateau, w)

    return {
        'wide_pct': float(100.0 * n_banded_lines / max(n_lines, 1)),
        'worst_plateau_px': int(worst_plateau * ds),
    }


def detect_banding(img_rgb: np.ndarray,
                   patch_size: int = 128,
                   lap_median_max: float = 0.5,
                   spike_ratio_min: float = 5.0,
                   range_min: float = 0.3,
                   max_run_min: int = 30,
                   max_transitions: int = 12) -> dict:
    """
    Detector v4 — Laplacian-filter + spike-ratio.

    Distingue:
      - banding         (|Laplaciano| ≈ 0 + spike-ratio alto) → BANDED
      - Gaussian halo   (|Laplaciano| moderado en todo el patch) → SKIP
      - texture/noise   (|Laplaciano| alto, alta freq)          → SKIP
      - dithered smooth (|Laplaciano| alto por dither)          → SKIP
      - flat            (range muy bajo)                        → SKIP

    Banded patch =
      (patch_range > range_min: hay variación en luma)
      AND (mean |Laplacian| < lap_max: zona LINEAR sin curvatura ni noise)
      AND (max(grad) / mean(grad) > spike_ratio_min: gradient con plateaus + spikes)
    """
    luma = (0.299 * img_rgb[:, :, 0]
            + 0.587 * img_rgb[:, :, 1]
            + 0.114 * img_rgb[:, :, 2]).astype(np.float32)

    # Raw gradient — preserva spikes en band edges
    gy, gx = np.gradient(luma)
    grad = np.sqrt(gy ** 2 + gx ** 2)
    # SMOOTHED Laplacian para curvature filter — el dither no rompe el filtro
    luma_smooth = gaussian_filter(luma, sigma=3.0)
    lap = np.abs(laplace(luma_smooth))

    H, W = luma.shape
    n_patches_total = 0
    n_patches_linear = 0
    n_patches_banded = 0
    banding_mask = np.zeros_like(luma, dtype=bool)

    for y in range(0, H - patch_size + 1, patch_size):
        for x in range(0, W - patch_size + 1, patch_size):
            patch_luma = luma[y:y + patch_size, x:x + patch_size]
            patch_grad = grad[y:y + patch_size, x:x + patch_size]
            patch_lap = lap[y:y + patch_size, x:x + patch_size]
            n_patches_total += 1

            prange = float(patch_luma.max() - patch_luma.min())
            if prange < range_min:
                continue

            lap_median = float(np.median(patch_lap))
            if lap_median > lap_median_max:
                # Not a linear gradient zone (halo curvature, texture, dither noise)
                continue

            n_patches_linear += 1

            gmean = float(patch_grad.mean())
            gmax = float(np.percentile(patch_grad, 99))
            spike_ratio = gmax / max(gmean, 1e-3)

            row_mid = np.round(patch_luma[patch_size // 2, :]).astype(np.int32)
            col_mid = np.round(patch_luma[:, patch_size // 2]).astype(np.int32)
            row_max_run, row_trans = _run_stats_1d(row_mid)
            col_max_run, col_trans = _run_stats_1d(col_mid)

            # v11: cuantization detector. Banding perceptual = pocos niveles
            # discretos en una zona smooth con rango decente. Si después de
            # filtrar el grain (blur) hay <= 8 unique values en un patch que
            # cubre rango >= 5, es banding visible. Esto agarra los gradientes
            # con escalones anchos (30-50 px) que el run-length missaba porque
            # el grain shader inflaba transitions.
            patch_smooth = gaussian_filter(patch_luma, sigma=3.5)
            smooth_range = float(patch_smooth.max() - patch_smooth.min())
            smooth_round = np.round(patch_smooth).astype(np.int32)
            unique_levels = int(np.unique(smooth_round).size)
            # Plateau check: para cada nivel único, cuál es la run-length total?
            # En banding real hay plateaus anchos (un nivel ocupa muchos pixels).
            # En halo continuo cada nivel ocupa pocos pixels.
            level_counts = np.bincount(smooth_round.ravel() - smooth_round.min())
            max_level_share = float(level_counts.max()) / smooth_round.size
            quant_banded = (
                smooth_range >= 5.0 and
                unique_levels <= max(6, int(smooth_range * 0.4)) and
                max_level_share >= 0.10  # un nivel ocupa ≥10% del patch
            )
            run_banded = (
                (row_max_run >= max_run_min and row_trans <= max_transitions)
                or (col_max_run >= max_run_min and col_trans <= max_transitions)
            )

            # v10: usar SOLO run-length signature. spike_ratio daba falsos
            # positivos en escenas con silueta/halo Gaussianas (curvatura suave
            # con gradient pico en los bordes).
            # v11: agregamos quant_banded (escalones anchos que sobreviven al grain).
            if run_banded or quant_banded:
                n_patches_banded += 1
                banding_mask[y:y + patch_size, x:x + patch_size] = True

    if n_patches_linear > 0:
        score = 100.0 * n_patches_banded / n_patches_linear
    else:
        score = 0.0

    wide = detect_wide_bands(luma)
    return {
        'score': float(score),
        'in_zone_pct': float(100.0 * n_patches_linear / max(n_patches_total, 1)),
        'banded_pct': float(100.0 * n_patches_banded / max(n_patches_total, 1)),
        'wide_pct': wide['wide_pct'],
        'worst_plateau_px': wide['worst_plateau_px'],
        'banding_mask': banding_mask,
    }


def save_heatmap(img_rgb: np.ndarray, det: dict, out_path: Path):
    out = img_rgb.copy()
    out[det['banding_mask']] = [255, 0, 0]
    Image.fromarray(out).save(out_path)


def extract_frame_raw(video_path: Path, t_seconds: float, out_path: Path):
    """Extract frame as raw signal (no tone-map) — coincide con lo que ven la
    mayoría de los players default."""
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-ss", str(t_seconds), "-i", str(video_path),
           "-frames:v", "1", str(out_path)]
    subprocess.run(cmd, check=True)


def analyze_video(video_path: Path, interval: float, out_dir: Path) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]).strip())
    sample_times = np.arange(2.0, duration - 1.0, interval)
    results = []
    print(f"  {video_path.name}: dur={duration:.1f}s, sampling {len(sample_times)} frames")

    for i, t in enumerate(sample_times):
        frame_path = out_dir / f"frame_t{int(t):04d}.png"
        extract_frame_raw(video_path, t, frame_path)
        img = np.array(Image.open(frame_path))
        if img.ndim == 2:
            img = np.stack([img] * 3, axis=-1)
        elif img.shape[2] == 4:
            img = img[:, :, :3]

        det = detect_banding(img)
        result = {
            't': float(t),
            'score': det['score'],
            'in_zone_pct': det['in_zone_pct'],
            'banded_pct': det['banded_pct'],
            'wide_pct': det['wide_pct'],
            'worst_plateau_px': det['worst_plateau_px'],
            'frame_path': str(frame_path),
        }
        results.append(result)

        if det['score'] > 10.0:
            heatmap_path = out_dir / f"BANDING_t{int(t):04d}.png"
            save_heatmap(img, det, heatmap_path)
            result['heatmap_path'] = str(heatmap_path)

        print(f"  [{i+1:3}/{len(sample_times)}] t={t:6.1f}s  "
              f"score={det['score']:6.1f}%  "
              f"in_zone={det['in_zone_pct']:5.1f}%  "
              f"banded={det['banded_pct']:5.1f}%  "
              f"wide={det['wide_pct']:5.1f}% (plateau {det['worst_plateau_px']}px)")
    return results


def run_test_bench():
    """Run detector on synthetic cases — validates calibration."""
    bench_dir = Path("/tmp/banding_synthetic")
    if not bench_dir.exists():
        print(f"ERROR: test bench not found. Run banding_test_bench.py first.")
        sys.exit(1)

    cases = [
        ("A_perfect_gradient",       "CLEAN",            0,   5),
        ("B_dithered_gradient",      "CLEAN",            0,   5),
        ("C_quantized_NO_dither",    "BANDED (severe)", 40, 100),
        ("D_gaussian_halo",          "CLEAN (design)",   0,   5),
        ("E_subtle_banding_8bit",    "BANDED (subtle)", 10, 100),
        ("F_texture",                "CLEAN",            0,   5),
    ]

    print(f"\n{'Case':30} {'Expected':20} {'Score':>8} {'Verdict':>15}")
    print("-" * 75)
    all_pass = True
    for name, label, lo, hi in cases:
        path = bench_dir / f"{name}.png"
        img = np.array(Image.open(path))
        det = detect_banding(img)
        score = det['score']
        verdict = "PASS" if lo <= score <= hi else "FAIL"
        if verdict == "FAIL":
            all_pass = False
        save_heatmap(img, det, bench_dir / f"{name}_heatmap.png")
        print(f"  {name:28} {label:20} {score:7.2f}  [{lo:3}-{hi:3}] {verdict:>10}")

    print()
    if all_pass:
        print("✅ Detector calibrated correctly — ALL test cases pass.")
    else:
        print("❌ Detector miscalibrated — FAILED test cases above.")
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path, nargs="?")
    ap.add_argument("--interval", type=float, default=10.0)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--test", action="store_true",
                    help="Run synthetic test bench and exit")
    args = ap.parse_args()

    if args.test:
        run_test_bench()
        return

    if args.video is None:
        ap.error("Must provide video or --test")

    out_dir = args.out_dir or Path(f"/tmp/banding_{args.video.stem}")
    results = analyze_video(args.video, args.interval, out_dir)
    json.dump(results, open(out_dir / "results.json", "w"), indent=2)

    avg_banded = float(np.mean([r['banded_pct'] for r in results]))
    max_banded = max(r['banded_pct'] for r in results)
    avg_wide = float(np.mean([r['wide_pct'] for r in results]))
    max_wide = max(r['wide_pct'] for r in results)
    print(f"\n=== {args.video.name} ===")
    print(f"avg banded_pct: {avg_banded:.1f}%  max: {max_banded:.1f}%")
    print(f"avg wide_pct (bandas anchas v12): {avg_wide:.1f}%  max: {max_wide:.1f}%")
    if max_wide > 15:
        print("⚠️  WIDE BANDS: hay frames con bandas anchas (>96px) que el "
              "patch-detector no ve. Revisar TOP wide abajo.")
    print(f"  (% del frame total con zurcos detectados)")
    if avg_banded < 2:
        v = "CLEAN ✓"
    elif avg_banded < 10:
        v = "MILD banding (visible en zonas oscuras)"
    elif avg_banded < 25:
        v = "VISIBLE banding"
    else:
        v = "SEVERE banding (zurcos prominentes)"
    print(f"verdict: {v}")

    sorted_worst = sorted(results, key=lambda r: r['banded_pct'], reverse=True)
    print(f"\nTOP 10 WORST (most banded frames):")
    for r in sorted_worst[:10]:
        print(f"  t={r['t']:6.1f}s  banded={r['banded_pct']:5.1f}%  "
              f"(score over qualifying patches={r['score']:5.1f}%, in_zone={r['in_zone_pct']:4.1f}%)")
    sorted_wide = sorted(results, key=lambda r: r['wide_pct'], reverse=True)
    print(f"\nTOP 5 WIDE BANDS (v12):")
    for r in sorted_wide[:5]:
        print(f"  t={r['t']:6.1f}s  wide={r['wide_pct']:5.1f}%  "
              f"worst plateau={r['worst_plateau_px']}px")
    print(f"\nTOP 5 CLEANEST:")
    for r in sorted_worst[-5:]:
        print(f"  t={r['t']:6.1f}s  banded={r['banded_pct']:5.1f}%  "
              f"(score={r['score']:5.1f}%, in_zone={r['in_zone_pct']:4.1f}%)")


if __name__ == "__main__":
    main()
