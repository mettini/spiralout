#!/usr/bin/env python3
"""
Test bench para el detector de banding.

Genera imágenes sintéticas con casos conocidos:
  A. Smooth gradient PERFECTO (16-bit) → debe scorear 0 (no banding)
  B. Smooth gradient con dither leve (8-bit con dither) → debe scorear ~0
  C. Smooth gradient cuantizado SIN dither (banding obvio) → debe scorear ALTO
  D. Gaussian halo (design feature, no banding) → debe scorear 0
  E. Smooth gradient cuantizado SUTIL (1-step bands) → debe scorear MEDIO
  F. High-frequency texture (humo/fractales) → debe scorear 0

Si el detector pasa A,B,D,F como clean y detecta C,E como banded, está calibrado.
"""
import numpy as np
from PIL import Image
from pathlib import Path

OUT = Path("/tmp/banding_synthetic")
OUT.mkdir(exist_ok=True)


def case_a_perfect_gradient(w=1920, h=1080, seed=1):
    """Gradient verde con dither pleno (ground truth de "smooth gradient").
    Equivalente a case B pero con dither más alto para no dejar dudas."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0.05, 0.20, w).astype(np.float32)
    grad = np.tile(x, (h, 1))
    rgb = np.stack([grad * 0.4, grad, grad * 0.5], axis=-1)
    dither = (rng.random(rgb.shape).astype(np.float32) - 0.5) * 8.0 / 255.0
    img = (np.clip(rgb + dither, 0, 1) * 255).astype(np.uint8)
    return img


def case_b_dithered_gradient(w=1920, h=1080, seed=42):
    """Smooth gradient PLUS dither 4/255 (lo que nuestro shader produce)."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0.05, 0.20, w).astype(np.float32)
    grad = np.tile(x, (h, 1))
    rgb = np.stack([grad * 0.4, grad, grad * 0.5], axis=-1)
    dither = (rng.random(rgb.shape).astype(np.float32) - 0.5) * 4.0 / 255.0
    img = (np.clip(rgb + dither, 0, 1) * 255).astype(np.uint8)
    return img


def case_c_quantized_NO_dither(w=1920, h=1080, levels=8):
    """Smooth gradient cuantizado en N niveles, SIN dither. Banding obvio."""
    x = np.linspace(0.05, 0.20, w).astype(np.float32)
    grad = np.tile(x, (h, 1))
    # Quantizar a `levels` niveles fuertes
    grad_q = np.round(grad * (levels - 1) / 0.15) * 0.15 / (levels - 1)
    rgb = np.stack([grad_q * 0.4, grad_q, grad_q * 0.5], axis=-1)
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return img


def case_d_gaussian_halo(w=1920, h=1080, seed=7):
    """Halo Gaussiano CON dither (como el shader real) — design feature, NO banding."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:h, :w].astype(np.float32)
    cx, cy = w / 2, h / 2
    sigma = h / 3
    halo = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma ** 2))
    rgb_v = 0.05 + 0.18 * halo
    rgb = np.stack([rgb_v * 0.4, rgb_v, rgb_v * 0.5], axis=-1)
    # Dither como el shader (4/255 isotrópico)
    dither = (rng.random(rgb.shape).astype(np.float32) - 0.5) * 4.0 / 255.0
    img = (np.clip(rgb + dither, 0, 1) * 255).astype(np.uint8)
    return img


def case_e_subtle_banding(w=1920, h=1080):
    """Gradient cuantizado a 1-step (8-bit floor sin dither) — banding subtle real."""
    x = np.linspace(0.05, 0.20, w).astype(np.float32)
    grad = np.tile(x, (h, 1))
    # Quantizar a 8-bit (256 niveles totales) sin dither — banding sutil
    grad_q = np.floor(grad * 255.0) / 255.0
    rgb = np.stack([grad_q * 0.4, grad_q, grad_q * 0.5], axis=-1)
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return img


def case_f_texture(w=1920, h=1080, seed=42):
    """High-frequency texture (humo style) — sin banding."""
    rng = np.random.default_rng(seed)
    noise = rng.random((h, w), dtype=np.float32)
    # Low-pass filter para hacerla más realista
    from scipy.ndimage import gaussian_filter
    texture = gaussian_filter(noise, sigma=8)
    texture = 0.05 + 0.15 * (texture - texture.min()) / (texture.max() - texture.min())
    rgb = np.stack([texture * 0.4, texture, texture * 0.5], axis=-1)
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return img


def main():
    cases = [
        ("A_perfect_gradient",       case_a_perfect_gradient,    "CLEAN"),
        ("B_dithered_gradient",      case_b_dithered_gradient,   "CLEAN"),
        ("C_quantized_NO_dither",    case_c_quantized_NO_dither, "BANDED (severe)"),
        ("D_gaussian_halo",          case_d_gaussian_halo,       "CLEAN (design)"),
        ("E_subtle_banding_8bit",    case_e_subtle_banding,      "BANDED (subtle)"),
        ("F_texture",                case_f_texture,             "CLEAN"),
    ]

    for name, fn, expected in cases:
        img = fn()
        path = OUT / f"{name}.png"
        Image.fromarray(img).save(path)
        print(f"  generated: {path} ({expected})")

    print(f"\nDone. Images at {OUT}/")
    print("Now run the detector on each and verify scores match expected.")


if __name__ == "__main__":
    main()
