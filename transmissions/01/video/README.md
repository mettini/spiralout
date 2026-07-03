# transmissions/01/video — capa video (Python + shader)

Pipeline generativo audio-reactivo para los videoclips de Heliopause.
El audio maneja la imagen: se releen los mismos features (NumPy) que generaron
el track. **No ilustra el sonido — comparte su materia prima.**

> Plan creativo + estado: `docs/video/00_PLAN_status.md` (LEER PRIMERO).
> Conceptos: `docs/video/01_concept_python_shader.md` (A, fósforo) y
> `docs/video/04_concept_2001_stargate.md` (B, star gate).

## Arquitectura (3 capas)

```
master.wav ─► analyze.py ─► control/<track>.npz   (Capa A: numpy/scipy/soundfile)
control.npz ─► render.py ─► frames RGB ─► ffmpeg + master.wav ─► out/<...>.mp4
                          (Capa B: moderngl headless, ping-pong feedback)
                                                    (Capa C: mux)
```

- `analyze.py` no sabe de GLSL. `render.py` no sabe de análisis (solo lee el
  control track). El shading vive en `shaders/*.{vert,frag}`. El control track
  (`.npz`) es el contrato entre capas.
- **Un solo motor, presets.** `accumulate.frag` (feedback + contenido nuevo) +
  `post.frag` (grade). El `--preset` cambia el mapeo audio→uniforms y la paleta:
  - `phosphor_recursion` — Concepto A: fósforo verde `#a6d65f`, monocromo, CRT.
  - `stargate` — Concepto B: túnel sucio, color desaturado, aberración cromática,
    solarización (2001 star gate). *Sketch inicial — afinar en Fase C.*

## Dependencias

```bash
python3.10 -m pip install moderngl     # numpy, scipy, soundfile, ffmpeg ya en el repo
```
macOS topa en OpenGL 4.1 (sin compute shaders) → feedback vía ping-pong de
texturas. Validado en Apple M3 Max (headless OK).

## Uso

```bash
# 1. WAV → control track
python3.10 transmissions/01/video/analyze.py \
  --wav transmissions/01/release/masters/03_recursion_master.wav \
  --out transmissions/01/video/control/recursion.npz --fps 30

# 2. Render (preset, resolución, ventana temporal opcional)
python3.10 transmissions/01/video/render.py \
  --control transmissions/01/video/control/recursion.npz \
  --wav transmissions/01/release/masters/03_recursion_master.wav \
  --out transmissions/01/video/out/recursion_phosphor_test.mp4 \
  --preset phosphor_recursion --w 1280 --h 720 --start-sec 50 --seconds 22

# Concepto B (mismo comando, otro preset)
python3.10 transmissions/01/video/render.py ... --preset stargate ...
```

Flags de `render.py`: `--w --h` (resolución), `--start-sec` (offset),
`--seconds` (0 = hasta el final), `--preset {phosphor_recursion,stargate}`.

## Canales del control track

`rms` (energía global) · `rms_sub` (30-55 Hz, latido) · `rms_low` (55-250 Hz) ·
`rms_air` (4-10 kHz, polvo/grano) · `centroid` (color/hue) · `flux` (turbulencia/
glitch) · `onset` (0/1, disparos). Todos 0..1 salvo `onset`. El mapeo a uniforms
usa **envelope followers** (suavizado) → movimiento musical, no nervioso (no es
un visualizer de barras de EQ).

## Git

`control/` y `out/` están gitignorados (regenerables). Se commitean
`analyze.py`, `render.py`, `shaders/*`, este README.

## Pendiente

- Afinar preset `stargate` → túnel slit-scan que fuga al centro (no franjas
  horizontales VHS). Ver `docs/video/04_concept_2001_stargate.md`.
- Cierre/loop seam de Recursion ↔ apertura de Outbound (Hexagrama 24).
- Presets para Outbound y Crossing. Master continuo 24:00.
- Encode más eficiente (el grano full-frame infla el H.264; bajar grain o
  tune=grain / CRF más alto para entregables).
- Sumar tasks `video:*` al `Taskfile.yml`.
