#!/usr/bin/env python3.10
"""Capa B+C del pipeline de video — control track + shaders → frames → mp4.

Render headless con moderngl (OpenGL 4.1, sin compute → ping-pong de texturas
para el feedback buffer). Los frames RGB se pipean directo a ffmpeg, que muxea
el WAV master. Un solo motor con PRESETS: el preset define el mapeo
audio→uniforms y la paleta, demostrando el rango de la herramienta.

  preset phosphor_recursion  → Concepto A (fósforo/telemetría, monocromo verde)
  preset stargate            → Concepto B (2001 star gate: túnel sucio, flashero)

Uso:
  python3.10 render.py --control control/recursion.npz \
      --wav .../03_recursion_master.wav --out out/test.mp4 \
      --preset phosphor_recursion --w 1280 --h 720 --start-sec 30 --seconds 22
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
import moderngl

SHADERS = Path(__file__).parent / "shaders"


def env_follow(state: float, x: float, atk: float, rel: float) -> float:
    """Envelope follower: ataque rápido, release lento (movimiento musical, no nervioso)."""
    coeff = atk if x > state else rel
    return state + (x - state) * coeff


def kf(t: float, keys: list) -> float:
    """Interpola una lista de keyframes [(t0,v0),(t1,v1),...] en t (0..1)."""
    if t <= keys[0][0]:
        return keys[0][1]
    if t >= keys[-1][0]:
        return keys[-1][1]
    for k in range(len(keys) - 1):
        t0, v0 = keys[k]
        t1, v1 = keys[k + 1]
        if t0 <= t <= t1:
            a = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return v0 + (v1 - v0) * a
    return keys[-1][1]


# DIRECTOR / storyboard de Recursion (concepto A). Macro-parámetros que mutan la
# COMPOSICIÓN a lo largo del tema (0..1) — para que el video cambie de forma, no
# sea siempre la misma diana. El audio modula el micro-movimiento ENCIMA de esto.
#   1 nacer (negro+latido) · 2 humo/polvo · 3 túnel · 4 espiral/diana ·
#   5 vinilo gastado (acá SÍ las rayas) · 6 colapso/loop
# Fases (t): nacer 0-0.12 · humo 0.12-0.35 · túnel 0.35-0.58 · mandala 0.58-0.80 ·
# vinilo 0.80-0.92 · colapso 0.92-1.0. CLAVE: "decay" (feedback) y "zoom" (pull
# radial) varían por fase — si están siempre altos, TODO se vuelve la misma diana.
SCENES_PHOSPHOR = {
    # feedback: bajo en humo/mandala (contenido fresco, asimétrico) / alto en túnel/colapso
    "decay":  [(0.0, 0.50), (0.12, 0.48), (0.33, 0.52), (0.42, 0.86), (0.55, 0.91),
               (0.62, 0.72), (0.78, 0.74), (0.85, 0.87), (0.95, 0.93), (1.0, 0.93)],
    # pull radial: ~0 en nacer/humo/mandala / alto solo en túnel y colapso
    "zoom":   [(0.0, 0.0), (0.33, 0.0), (0.42, 0.012), (0.55, 0.022), (0.62, 0.003),
               (0.80, 0.003), (0.90, 0.010), (1.0, 0.018)],
    # rotación: protagonista en mandala (pétalos girando)
    "rot":    [(0.0, 0.0), (0.35, 0.001), (0.55, 0.002), (0.68, 0.013), (0.80, 0.004), (1.0, 0.002)],
    "pulse":  [(0.0, 1.0), (0.12, 0.7), (0.30, 0.2), (1.0, 0.0)],
    "smoke":  [(0.0, 0.05), (0.12, 0.6), (0.30, 1.0), (0.42, 0.5), (0.58, 0.4),
               (0.68, 1.0), (0.80, 0.5), (1.0, 0.1)],
    # túnel SOLO en su fase (si no, hace anillos en todos lados)
    "tunnel": [(0.0, 0.0), (0.40, 0.2), (0.50, 1.0), (0.58, 0.9), (0.66, 0.2), (1.0, 0.0)],
    # retina/ojo: un momento puntual (el ojo que se abre), no permanente
    "retina": [(0.0, 0.0), (0.45, 0.15), (0.55, 0.8), (0.62, 0.45), (0.70, 0.1), (1.0, 0.0)],
    "dust":   [(0.0, 0.0), (0.12, 0.5), (0.35, 1.0), (0.58, 0.6), (0.82, 0.9), (1.0, 0.2)],
    # rayas horizontales: en Recursion van en 0 (se mudaron a Crossing, "lo picante")
    "streak": [(0.0, 0.0), (1.0, 0.0)],
    "kaleidN": [(0.0, 0.0), (0.58, 0.0), (0.63, 8.0), (0.70, 12.0), (0.78, 8.0), (0.84, 0.0), (1.0, 0.0)],
    # color (stargate) florece en el pico del delirio (túnel+mandala); verde en los bordes
    "color":  [(0.0, 0.0), (0.38, 0.0), (0.48, 0.55), (0.60, 0.9), (0.72, 1.0),
               (0.80, 0.55), (0.88, 0.12), (1.0, 0.0)],
}


def map_phosphor(ch: dict, i: int, st: dict, t: float) -> dict:
    """Concepto A — fósforo/recursión. t: 0..1 posición en el TEMA (para el director)."""
    st["rms"] = env_follow(st["rms"], ch["rms"][i], 0.30, 0.04)
    st["sub"] = env_follow(st["sub"], ch["rms_sub"][i], 0.50, 0.06)
    st["low"] = env_follow(st["low"], ch["rms_low"][i], 0.30, 0.08)
    st["air"] = env_follow(st["air"], ch["rms_air"][i], 0.60, 0.12)
    st["flx"] = env_follow(st["flx"], ch["flux"][i], 0.70, 0.20)
    st["cen"] = env_follow(st["cen"], ch["centroid"][i], 0.10, 0.04)

    S = SCENES_PHOSPHOR                                  # macro-storyboard (el director)
    collapse = max(0.0, (t - 0.92) / 0.08)               # último 8% del TEMA → cierre/loop
    streak = kf(t, S["streak"])                          # presencia de las rayas horizontales
    glitch_audio = max(0.0, st["flx"] - 0.40) * 1.5
    color = kf(t, S["color"])                            # 0=fósforo verde · 1=color sucio stargate
    return dict(
        u_decay=min(0.94, kf(t, S["decay"]) + 0.03 * st["rms"]),   # feedback POR FASE
        u_spiralZoom=1.001 + kf(t, S["zoom"]) + 0.008 * st["sub"],
        u_spiralRot=kf(t, S["rot"]) + 0.004 * st["low"],
        u_pulse=kf(t, S["pulse"]) * (0.05 + 0.30 * st["sub"]),
        u_retina=kf(t, S["retina"]) * (0.30 + 0.35 * st["rms"]),
        u_iris=0.12 + 0.20 * st["sub"],                  # pupila dilata con el latido
        u_smoke=kf(t, S["smoke"]) * (0.22 + 0.30 * st["low"]),
        u_tunnel=kf(t, S["tunnel"]) * (0.15 + 0.25 * st["rms"]),
        u_dust=kf(t, S["dust"]) * (0.5 * st["air"]),
        u_kaleidN=kf(t, S["kaleidN"]),                   # fase mandala
        u_lightning=0.0, u_rocks=0.0,                    # (relámpagos/piedras → Outbound)
        # las RAYAS horizontales SOLO aparecen donde el director las pide (fase vinilo)
        u_glitch=streak * (0.3 + glitch_audio),
        u_dropout=float(ch["onset"][i]) * (0.25 + 0.75 * streak),
        u_collapse=collapse,
        # color: el contenido nuevo toma tinte sucio donde el director lo pide
        u_inject=color, u_hueBase=0.55 + 0.25 * st["cen"], u_hueSpread=0.45, u_sat=0.55,
        # post
        u_grain=0.05 + 0.14 * st["air"],
        u_vignette=0.85,
        u_palette=color,                                 # blend fósforo↔color
        u_chroma=color * 0.008, u_solarize=color * 0.5,
    )


def map_stargate(ch: dict, i: int, st: dict, t: float) -> dict:
    """Concepto B — 2001 star gate: túnel de zoom fuerte, sucio, flashero."""
    st["rms"] = env_follow(st["rms"], ch["rms"][i], 0.25, 0.05)
    st["sub"] = env_follow(st["sub"], ch["rms_sub"][i], 0.45, 0.08)
    st["low"] = env_follow(st["low"], ch["rms_low"][i], 0.30, 0.08)
    st["air"] = env_follow(st["air"], ch["rms_air"][i], 0.60, 0.12)
    st["flx"] = env_follow(st["flx"], ch["flux"][i], 0.70, 0.20)
    st["cen"] = env_follow(st["cen"], ch["centroid"][i], 0.10, 0.04)
    return dict(
        u_decay=min(0.88, 0.82 + 0.05 * st["rms"]),      # bajo → no smear horizontal
        u_spiralZoom=1.03 + 0.06 * st["sub"],            # fuga rápida = volar al infinito
        u_spiralRot=0.003 + 0.008 * st["low"],           # algo de espiral (no horizontal)
        u_pulse=0.4 * st["sub"],
        u_retina=0.20 + 0.25 * st["rms"],
        u_iris=0.10 + 0.18 * st["sub"],
        u_smoke=0.30 + 0.50 * st["low"],
        u_tunnel=0.45 + 0.45 * st["rms"],                # túnel protagonista en B
        u_dust=1.1 * st["air"],                          # polvo → streaks radiales (slit-scan)
        u_kaleidN=0.0, u_lightning=0.0, u_rocks=0.0,
        u_glitch=max(0.0, st["flx"] - 0.45) * 1.0,       # rayas SOLO en transientes fuertes
        u_dropout=float(ch["onset"][i]),
        u_collapse=0.0,
        u_inject=1.0,                                    # color ON
        u_hueBase=0.55 + 0.25 * st["cen"],               # deriva del tinte sucio
        u_hueSpread=0.4, u_sat=0.5,                      # saturación baja = sucio, no neón
        # post
        u_grain=0.10 + 0.20 * st["air"],
        u_vignette=0.7, u_palette=1.0,
        u_chroma=0.004 + 0.010 * st["flx"], u_solarize=0.5,
    )


# DIRECTOR de Outbound (8:00): DELIRIO + TÚNEL mezclados (más dinámico).
# nacer → DESPEGUE/TÚNEL → humo → mandala+color → seguir hacia afuera.
# SIN rayas, SIN relámpagos/piedras (esos son de Crossing).
SCENES_OUTBOUND = {
    # 0-2:48 nacer/despegue/túnel · 2:48-5:40 STARGATE (kaleid+color+movimiento) ·
    # el agujero negro (colapso) se aplica por --collapse-tail al renderizar 0-~5:40.
    "decay":  [(0.0, 0.50), (0.12, 0.55), (0.18, 0.88), (0.30, 0.90), (0.5, 0.82), (0.7, 0.86), (1.0, 0.90)],
    "zoom":   [(0.0, 0.0), (0.12, 0.008), (0.18, 0.020), (0.25, 0.016), (0.4, 0.008), (0.6, 0.010), (0.7, 0.014), (1.0, 0.018)],
    # rotación creciente = distorsión/giro del mandala hacia el 5:40
    "rot":    [(0.0, 0.0), (0.25, 0.003), (0.40, 0.008), (0.55, 0.016), (0.68, 0.028), (1.0, 0.010)],
    "pulse":  [(0.0, 1.0), (0.12, 0.8), (0.25, 0.2), (1.0, 0.05)],
    "smoke":  [(0.0, 0.05), (0.15, 0.2), (0.30, 0.4), (0.5, 0.6), (0.7, 0.8), (1.0, 0.5)],
    # TÚNEL: fuerte 0-1:55, después taper suave para no saturar el brillo 2:05-3:05
    # (user feedback 2026-05-24: "brilla muy muy brillante, satura tanta luz").
    # Mantiene peak 1.0 en 0.18 (1:26) y empieza a bajar gradual: 0.85 (1:55)
    # → 0.65 (2:24) → 0.45 (3:02). El brillo en 6:50 NO depende del túnel.
    "tunnel": [(0.0, 0.0), (0.10, 0.6), (0.18, 1.0), (0.24, 0.85), (0.30, 0.65), (0.38, 0.45),
               (0.5, 0.3), (0.7, 0.2), (1.0, 0.1)],
    "retina": [(0.0, 0.0), (0.34, 0.2), (0.45, 0.4), (0.6, 0.3), (0.72, 0.2), (1.0, 0.0)],
    # DUST/RAYOS: más polvo en la locura → bajo zoom se estiran en rayas locas tipo stargate
    "dust":   [(0.0, 0.0), (0.2, 0.3), (0.4, 0.7), (0.55, 1.0), (0.68, 1.1), (0.72, 0.6), (1.0, 0.5)],
    # MANDALA/FRACTAL + COLOR ganando: 3:00 entra fuerte, locura plena 4:30-5:30
    "color":  [(0.0, 0.0), (0.24, 0.05), (0.30, 0.4), (0.40, 0.7), (0.55, 1.0), (0.68, 1.0), (1.0, 0.8)],
    # kaleidN: dos PICOS a N=21 sincronizados con los echos del voyager (4:30-4:41 y
    # 4:55-5:04), después cambio mandala adelantado de 5:17 → 5:10 (step 17→16 cae
    # en t=0.6458). El drop 14→10 en t=0.675→0.74 mantiene el SYNC con los bells del
    # 5:50. (user feedback 2026-05-24.)
    "kaleidN": [(0.0, 0.0), (0.24, 0.0), (0.28, 5.0), (0.38, 9.0), (0.50, 13.0),
                (0.55, 14.0), (0.563, 14.5), (0.572, 21.0), (0.585, 14.0),    # voyager #1
                (0.605, 14.5), (0.615, 15.0), (0.622, 21.0), (0.633, 16.0),   # voyager #2
                (0.640, 17.0), (0.675, 14.0),                                  # cambio 5:10
                (0.74, 10.0),                                                  # bell sync 5:50
                (1.0, 6.0)],
    # horizonte: DESHABILITADO (quedaba como franja berreta) — el latido central respira solo
    "horizon": [(0.0, 0.0), (1.0, 0.0)],
}


def map_outbound(ch: dict, i: int, st: dict, t: float) -> dict:
    """Outbound — delirio + túnel: nacer → despegue/túnel → humo → mandala+color → afuera.

    SYNC bell/heart_pulse → mandala (user feedback 2026-05-24, iter 3):
    El usuario notó que en 2:01 el mandala "tira un simbronazo" con un bell, pero
    los bells siguientes (y los heart_pulses 3:30-4:00) NO reaccionan parejo.
    Causa: el simbronazo venía del SUB band — variable según contenido espectral
    de cada bell. Los bells con menos sub → reacción débil → inconsistente.
    Fix: usar st["bell"] (onset-based) que sí dispara CONSISTENTE por cada bell,
    y agregarlo como kick controlado a pulse/retina/rotation/kaleidN. Cada bell
    produce el mismo kick visual independiente de la energía espectral.

    SUB attack vuelve a 0.40 (entre el original 0.50 y el dampened 0.25) para que
    el heart_pulse 3:30-4:00 también haga latir el centro.
    """
    st["rms"] = env_follow(st["rms"], ch["rms"][i], 0.30, 0.04)
    st["sub"] = env_follow(st["sub"], ch["rms_sub"][i], 0.40, 0.06)            # mid-ground entre 0.50 y 0.25
    st["low"] = env_follow(st["low"], ch["rms_low"][i], 0.30, 0.08)
    st["air"] = env_follow(st["air"], ch["rms_air"][i], 0.60, 0.12)
    st["flx"] = env_follow(st["flx"], ch["flux"][i], 0.70, 0.20)
    st["cen"] = env_follow(st["cen"], ch["centroid"][i], 0.10, 0.04)
    st["bell"] = max(float(ch["onset"][i]), st.get("bell", 0.0) * 0.86)         # cola corta ~1s

    bell = st["bell"]                                                            # kick consistente por onset
    S = SCENES_OUTBOUND
    color = kf(t, S["color"])
    return dict(
        u_horizon=kf(t, S["horizon"]) * (0.25 + 0.75 * bell),
        u_decay=min(0.94, kf(t, S["decay"]) + 0.03 * st["rms"]),
        u_spiralZoom=1.001 + kf(t, S["zoom"]) + 0.008 * st["sub"],
        u_spiralRot=kf(t, S["rot"]) + 0.003 * st["low"] + bell * 0.003,         # ⭐ kick suave (era 0.006)
        u_pulse=kf(t, S["pulse"]) * (0.05 + 0.18 * st["sub"]) + bell * 0.05,    # ⭐ kick atenuado (era 0.15 → flashes)
        u_retina=kf(t, S["retina"]) * (0.25 + 0.20 * st["rms"]) + bell * 0.04,  # ⭐ iris pulsa sutil (era 0.10)
        u_iris=0.12 + 0.20 * st["sub"] + bell * 0.03,                            # pupila (era 0.06)
        u_smoke=kf(t, S["smoke"]) * (0.22 + 0.30 * st["low"]),
        u_tunnel=kf(t, S["tunnel"]) * (0.15 + 0.25 * st["rms"]),
        u_dust=kf(t, S["dust"]) * (0.5 * st["air"]),
        u_kaleidN=kf(t, S["kaleidN"]) + bell * 1.2,                              # ⭐ mandala se "estira" (era 2.5)
        u_lightning=0.0, u_rocks=0.0,
        u_glitch=0.0, u_dropout=0.0,
        u_collapse=0.0,
        u_inject=color, u_hueBase=0.02 + 0.06 * st["cen"], u_hueSpread=0.40, u_sat=0.85,
        u_grain=0.05 + 0.12 * st["air"],
        u_vignette=0.80, u_palette=color, u_chroma=color * 0.005, u_solarize=color * 0.25,
    )


# DIRECTOR de Crossing (13:00): el viaje denso "picante". ACÁ van las rayas
# horizontales, el polvo de Saturno, los tropezones (piedras), los relámpagos y
# el color sucio stargate. INVERSIÓN a mitad (~0.50, la órbita se parte).
SCENES_CROSSING = {
    "decay":  [(0.0, 0.80), (0.10, 0.84), (0.35, 0.82), (0.48, 0.70), (0.52, 0.88), (0.75, 0.85), (1.0, 0.80)],
    "zoom":   [(0.0, 0.006), (0.10, 0.004), (0.35, 0.003), (0.48, 0.020), (0.55, 0.016), (0.75, 0.008), (1.0, 0.004)],
    "rot":    [(0.0, 0.001), (0.48, 0.002), (0.55, 0.006), (0.75, 0.003), (1.0, 0.001)],
    "pulse":  [(0.0, 0.1), (1.0, 0.05)],
    "smoke":  [(0.0, 0.4), (0.10, 0.9), (0.35, 0.7), (0.48, 0.5), (0.55, 0.7), (0.75, 0.6), (1.0, 0.4)],
    "tunnel": [(0.0, 0.3), (0.10, 0.1), (0.48, 0.4), (0.55, 1.0), (0.70, 0.6), (0.85, 0.2), (1.0, 0.1)],
    "retina": [(0.0, 0.0), (0.48, 0.2), (0.52, 0.6), (0.58, 0.1), (1.0, 0.0)],
    "dust":   [(0.0, 0.3), (0.12, 1.0), (0.35, 0.9), (0.55, 0.6), (0.75, 0.9), (1.0, 0.5)],
    "lightning": [(0.0, 0.0), (0.30, 0.0), (0.38, 0.7), (0.48, 0.9), (0.55, 0.3), (0.75, 0.7), (0.88, 0.3), (1.0, 0.0)],
    "rocks":  [(0.0, 0.0), (0.28, 0.0), (0.36, 0.6), (0.48, 0.9), (0.60, 0.3), (0.72, 0.8), (0.88, 0.4), (1.0, 0.0)],
    "streak": [(0.0, 0.0), (0.15, 0.2), (0.30, 0.5), (0.45, 0.8), (0.55, 1.0), (0.75, 0.8), (0.90, 0.4), (1.0, 0.1)],
    "color":  [(0.0, 0.1), (0.20, 0.4), (0.40, 0.7), (0.52, 1.0), (0.70, 0.9), (0.88, 0.5), (1.0, 0.2)],
    "kaleidN": [(0.0, 0.0), (0.50, 0.0), (0.55, 6.0), (0.65, 8.0), (0.72, 0.0), (1.0, 0.0)],
}


def map_crossing(ch: dict, i: int, st: dict, t: float) -> dict:
    """Crossing — viaje picante: polvo, tropezones, rayas, relámpagos, color stargate, inversión."""
    st["rms"] = env_follow(st["rms"], ch["rms"][i], 0.30, 0.04)
    st["sub"] = env_follow(st["sub"], ch["rms_sub"][i], 0.50, 0.06)
    st["low"] = env_follow(st["low"], ch["rms_low"][i], 0.30, 0.08)
    st["air"] = env_follow(st["air"], ch["rms_air"][i], 0.60, 0.12)
    st["flx"] = env_follow(st["flx"], ch["flux"][i], 0.70, 0.20)
    st["cen"] = env_follow(st["cen"], ch["centroid"][i], 0.10, 0.04)
    onset = float(ch["onset"][i])
    strong = onset if st["flx"] > 0.5 else 0.0           # relámpago SOLO en golpes fuertes (no abuso)
    st["light"] = max(strong, st.get("light", 0.0) * 0.80)

    S = SCENES_CROSSING
    streak = kf(t, S["streak"])
    color = kf(t, S["color"])
    glitch_audio = max(0.0, st["flx"] - 0.35) * 1.5
    return dict(
        u_decay=min(0.93, kf(t, S["decay"]) + 0.03 * st["rms"]),
        u_spiralZoom=1.002 + kf(t, S["zoom"]) + 0.008 * st["sub"],
        u_spiralRot=kf(t, S["rot"]) + 0.003 * st["low"],
        u_pulse=kf(t, S["pulse"]) * (0.05 + 0.20 * st["sub"]),
        u_retina=kf(t, S["retina"]) * (0.25 + 0.30 * st["rms"]),
        u_iris=0.12 + 0.20 * st["sub"],
        u_smoke=kf(t, S["smoke"]) * (0.22 + 0.30 * st["low"]),
        u_tunnel=kf(t, S["tunnel"]) * (0.15 + 0.25 * st["rms"]),
        u_dust=kf(t, S["dust"]) * (0.7 * st["air"]),
        u_kaleidN=kf(t, S["kaleidN"]),
        u_lightning=kf(t, S["lightning"]) * st["light"],
        u_rocks=kf(t, S["rocks"]) * (0.4 + 0.5 * st["low"]),
        u_glitch=streak * (0.3 + glitch_audio),          # rayas horizontales = lo picante
        u_dropout=onset * (0.2 + 0.8 * streak),
        u_collapse=0.0,
        u_inject=color, u_hueBase=0.55 + 0.25 * st["cen"], u_hueSpread=0.45, u_sat=0.55,
        u_grain=0.06 + 0.16 * st["air"],
        u_vignette=0.82, u_palette=color, u_chroma=color * 0.010, u_solarize=color * 0.5,
    )


def map_signal(ch: dict, i: int, st: dict, t: float) -> dict:
    """SEÑAL sub-42 — impasse entre temas: negro + onda/interferencia sutil del sub-bass."""
    st["sub"] = env_follow(st["sub"], ch["rms_sub"][i], 0.40, 0.10)
    return dict(
        u_decay=0.40, u_spiralZoom=1.0, u_spiralRot=0.0,
        u_pulse=0.0, u_retina=0.0, u_iris=0.0, u_smoke=0.0, u_tunnel=0.0, u_dust=0.0,
        u_kaleidN=0.0, u_lightning=0.0, u_rocks=0.0, u_glitch=0.0, u_dropout=0.0,
        u_collapse=0.0,
        u_wave=0.20 + 0.80 * st["sub"],                  # la onda sub-42 (sutil)
        u_inject=0.0, u_hueBase=0.0, u_hueSpread=0.0, u_sat=0.0,
        u_grain=0.04, u_vignette=0.92, u_palette=0.0, u_chroma=0.0, u_solarize=0.0,
    )


PRESETS = {
    "phosphor_recursion": map_phosphor,
    "stargate": map_stargate,
    "outbound": map_outbound,
    "crossing": map_crossing,
    "signal": map_signal,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--wav", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preset", default="phosphor_recursion", choices=list(PRESETS))
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--start-sec", type=float, default=0.0)
    ap.add_argument("--seconds", type=float, default=0.0, help="0 = hasta el final")
    ap.add_argument("--crf", type=int, default=20, help="calidad H.264 (menor=mejor/pesado)")
    ap.add_argument("--collapse-tail", type=float, default=0.0,
                    help="segundos finales en que se fuerza el colapso a negro (transición agujero)")
    args = ap.parse_args()

    data = np.load(args.control)
    ch = {k: data[k] for k in data.files}
    fps = int(data["fps"])
    n_total = len(ch["rms"])
    start = int(args.start_sec * fps)
    n = n_total - start if args.seconds <= 0 else min(int(args.seconds * fps), n_total - start)
    W, H = args.w, args.h
    mapper = PRESETS[args.preset]

    ctx = moderngl.create_standalone_context()
    vbo = ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], dtype="f4").tobytes())
    vert = (SHADERS / "quad.vert").read_text()
    acc_prog = ctx.program(vertex_shader=vert,
                           fragment_shader=(SHADERS / "accumulate.frag").read_text())
    post_prog = ctx.program(vertex_shader=vert,
                            fragment_shader=(SHADERS / "post.frag").read_text())
    vao_acc = ctx.vertex_array(acc_prog, [(vbo, "2f", "in_pos")])
    vao_post = ctx.vertex_array(post_prog, [(vbo, "2f", "in_pos")])

    def make_tex(comps, dtype):
        t = ctx.texture((W, H), comps, dtype=dtype)
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        t.repeat_x = t.repeat_y = False
        return t

    texs = [make_tex(4, "f4"), make_tex(4, "f4")]      # ping-pong feedback (HDR)
    fbos = [ctx.framebuffer([texs[0]]), ctx.framebuffer([texs[1]])]
    out_tex = make_tex(3, "f1")
    fbo_out = ctx.framebuffer([out_tex])
    for f in fbos:
        f.use(); ctx.clear(0.0, 0.0, 0.0, 1.0)

    for p in (acc_prog, post_prog):
        if "u_res" in p:
            p["u_res"].value = (float(W), float(H))

    # ffmpeg: frames raw RGB por stdin + WAV (recortado a la ventana del render)
    ss = args.start_sec
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-ss", f"{ss}", "-i", args.wav,
           "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "256k", "-t", f"{n / fps:.3f}",
           "-movflags", "+faststart", args.out]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    st = {k: 0.0 for k in ("rms", "sub", "low", "air", "flx", "cen")}
    read_i, write_i = 1, 0
    print(f"render: preset={args.preset} {W}x{H}@{fps} frames={n} "
          f"({n / fps:.1f}s desde {ss:.1f}s) → {args.out}")
    for j in range(n):
        i = start + j
        u = mapper(ch, i, st, i / max(1, n_total - 1))   # t = posición en el TEMA completo
        u.setdefault("u_wave", 0.0)                      # señal sub-42 (solo preset signal)
        u.setdefault("u_horizon", 0.0)                   # horizonte/campanas (solo Outbound)
        u["u_time"] = i / fps
        if args.collapse_tail > 0:                       # colapso forzado a negro en la cola
            tail = args.collapse_tail * fps
            into = j - (n - tail)
            if into > 0:
                u["u_collapse"] = max(float(u.get("u_collapse", 0.0)), min(1.0, into / tail))
        for k, v in u.items():
            if k in acc_prog:
                acc_prog[k].value = float(v)
            if k in post_prog:
                post_prog[k].value = float(v)

        texs[read_i].use(0)
        if "prevTex" in acc_prog:
            acc_prog["prevTex"].value = 0
        fbos[write_i].use()
        vao_acc.render(moderngl.TRIANGLES)

        texs[write_i].use(0)
        if "srcTex" in post_prog:
            post_prog["srcTex"].value = 0
        fbo_out.use()
        vao_post.render(moderngl.TRIANGLES)

        frame = np.frombuffer(fbo_out.read(components=3), dtype="u1").reshape(H, W, 3)
        ff.stdin.write(np.flipud(frame).tobytes())     # GL origen abajo → flip

        read_i, write_i = write_i, read_i
        if j % max(1, n // 10) == 0:
            print(f"  {100 * j // n:3d}%  frame {j}/{n}")

    ff.stdin.close()
    ff.wait()
    print(f"OK → {args.out}")


if __name__ == "__main__":
    main()
