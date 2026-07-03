#!/usr/bin/env python3.10
"""Capa A del pipeline de video — WAV master → control track (control.npz).

Extrae features por frame de video (a `--fps`) usando SOLO numpy/scipy/soundfile
(sin librosa). Filosofía del proyecto: el video corre sobre la MISMA materia
prima NumPy que generó el audio, no lo "ilustra".

Canales del control track (cada uno normalizado 0..1, salvo onset que es 0/1):
  rms        energía global               → escala/brillo global
  rms_sub    energía 30-55 Hz (sub/latido)→ pulso, zoom del feedback
  rms_low    energía 55-250 Hz            → empuje del flow / streaks
  rms_air    energía 4-10 kHz             → grano, polvo brillante
  centroid   centroide espectral norm.    → temperatura de color / hue
  flux       spectral flux (cambio)       → turbulencia, glitch, chroma
  onset      1.0 en transientes, 0.0 else → disparos puntuales

Uso:
  python3.10 analyze.py --wav master.wav --out control/recursion.npz --fps 30
"""
import argparse
from pathlib import Path

import numpy as np
import soundfile as sf


def band_mask(freqs: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return (freqs >= lo) & (freqs < hi)


def robust_norm(x: np.ndarray, pct: float = 99.0) -> np.ndarray:
    """Normaliza a 0..1 dividiendo por el percentil `pct` (robusto a picos)."""
    ref = np.percentile(x, pct)
    if ref < 1e-9:
        return np.zeros_like(x)
    return np.clip(x / ref, 0.0, 1.0)


def main() -> None:
    ap = argparse.ArgumentParser(description="WAV master → control track (.npz)")
    ap.add_argument("--wav", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--win", type=int, default=2048, help="ventana FFT (samples)")
    args = ap.parse_args()

    audio, sr = sf.read(args.wav)
    if audio.ndim > 1:                       # estéreo → mono para análisis
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float64)

    hop = sr / args.fps                       # 1 frame de análisis = 1 frame de video
    n_frames = int(np.floor((len(audio) - args.win) / hop))
    win = args.win
    window = np.hanning(win)
    freqs = np.fft.rfftfreq(win, 1.0 / sr)

    m_sub = band_mask(freqs, 30, 55)
    m_low = band_mask(freqs, 55, 250)
    m_air = band_mask(freqs, 4000, 10000)

    rms = np.zeros(n_frames, np.float64)
    rms_sub = np.zeros(n_frames, np.float64)
    rms_low = np.zeros(n_frames, np.float64)
    rms_air = np.zeros(n_frames, np.float64)
    centroid = np.zeros(n_frames, np.float64)
    flux = np.zeros(n_frames, np.float64)

    prev_mag = None
    for i in range(n_frames):
        start = int(i * hop)
        seg = audio[start:start + win] * window
        rms[i] = np.sqrt(np.mean(seg ** 2))
        mag = np.abs(np.fft.rfft(seg))
        rms_sub[i] = np.sqrt(np.mean(mag[m_sub] ** 2)) if m_sub.any() else 0.0
        rms_low[i] = np.sqrt(np.mean(mag[m_low] ** 2)) if m_low.any() else 0.0
        rms_air[i] = np.sqrt(np.mean(mag[m_air] ** 2)) if m_air.any() else 0.0
        centroid[i] = np.sum(freqs * mag) / (np.sum(mag) + 1e-9)
        if prev_mag is not None:
            flux[i] = np.sqrt(np.mean(np.maximum(mag - prev_mag, 0.0) ** 2))
        prev_mag = mag

    # Normalización
    rms_n = robust_norm(rms)
    rms_sub_n = robust_norm(rms_sub)
    rms_low_n = robust_norm(rms_low)
    rms_air_n = robust_norm(rms_air)
    centroid_n = np.clip(centroid / (sr / 2.0) * 4.0, 0.0, 1.0)  # *4: el grueso vive abajo
    flux_n = robust_norm(flux, pct=95.0)

    # Onset: pico local de flux por encima de media móvil
    onset = np.zeros(n_frames, np.float64)
    k = max(1, args.fps // 6)                 # ventana ~166 ms
    for i in range(1, n_frames - 1):
        lo, hi = max(0, i - k), min(n_frames, i + k)
        local = flux_n[lo:hi]
        thr = local.mean() + 1.2 * local.std()
        if flux_n[i] > thr and flux_n[i] >= flux_n[i - 1] and flux_n[i] >= flux_n[i + 1]:
            onset[i] = 1.0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        rms=rms_n.astype(np.float32),
        rms_sub=rms_sub_n.astype(np.float32),
        rms_low=rms_low_n.astype(np.float32),
        rms_air=rms_air_n.astype(np.float32),
        centroid=centroid_n.astype(np.float32),
        flux=flux_n.astype(np.float32),
        onset=onset.astype(np.float32),
        fps=np.int32(args.fps),
        sr=np.int32(sr),
    )
    print(f"OK control track → {out}")
    print(f"  frames={n_frames}  fps={args.fps}  dur={n_frames / args.fps:.1f}s  sr={sr}")
    print(f"  onsets detectados: {int(onset.sum())}")
    print(f"  rms[p50]={np.percentile(rms_n, 50):.2f}  flux[p50]={np.percentile(flux_n, 50):.2f}")


if __name__ == "__main__":
    main()
