# Iter results 2026-06-09 — wall hit en ffmpeg post-process

> Verdict de la sesión nocturna: **4 iteraciones de post-process ffmpeg, ninguna
> beat v11 baseline**. Es hora de cambiar de estrategia.

## Tabla de resultados

YT-emulated (VP9 8-bit 20Mbps bt709). Threshold del bible: avg < 0.5%.

| # | Strategy                                  | avg banded | max  |
|---|-------------------------------------------|------------|------|
| 0 | **v11 baseline** (sin post-process)       | **3.79%**  | **32.9%** |
| 1 | grain plate overlay 0.06                  | 3.53%      | 47.5% |
| 2 | grainmerge plate 0.10                     | 4.47%      | 53.9% |
| 3 | `noise=c0s=10:c0f=t+u` (YUV todos)         | 29.4%      | 95.8% |
| 4 | `noise=c0s=6:c0f=t` (Y only)               | 25.6%      | 95.2% |

## Por qué falla el approach ffmpeg

Cada técnica de inyección de ruido (filter `noise=` o overlay plate)
**confunde a VP9**:

1. VP9 8-bit en 20Mbps no puede distinguir ruido decorativo de detalle real.
2. Cuando le metés noise pre-encode, el encoder gasta bitrate en intentar
   preservar ese noise.
3. Los gradientes lentos (bloom de outbound) quedan SIN bits suficientes →
   bandas más prominentes.

El grain plate overlay a opacity baja (iter 1) no daña demasiado pero
tampoco aporta — el ruido es de tan baja amplitud que VP9 lo borra como si
fuera quantization noise.

## Estado real del producto

- **outbound v11**: avg 3.79%, max 32.9% en bloom (t=292)
- Esto **no pasa el threshold "0.5%"** del bible.
- Las únicas zonas que muestran banding visible son el bloom y entornos
  cercanos. El resto del video está limpio.

## Opciones para seguir

### Opción A — subir v11 a YouTube real y validar

El YT emulator local podría estar siendo **más pesimista** que YouTube real:
- YouTube aplica su propio dither/grain a slow gradients antes de re-encode.
- El emulator local es vainilla VP9 sin ese pre-processing.
- Subir el v11 a YouTube **unlisted** y ver el resultado real es la
  validación que falta.

Costo: 0 dinero, 10 min de upload.
Riesgo: si banding persiste en YouTube real, igual sirve para confirmar.

### Opción B — fix a nivel shader

El problema raíz: la escena de bloom (t=4:52) **no tiene detalle espacial**
que VP9 pueda agarrar. Es un gradiente puro.

Fix en `outbound/render.py`:
- Agregar microtextura fractal subaudible (FBM 3D bajo amplitud) **sólo
  durante bloom** (t=4:30 a t=5:30).
- Visualmente invisible (amplitud < 1/255).
- Le da a VP9 algo concreto que preservar.

Costo: 30 min implementación + 1h re-render full.
Riesgo: si la amplitud es muy baja, mismo problema. Si es muy alta, se ve.

### Opción C — Resolve Studio ($299)

Ya rechazado por el user. NO retomar.

### Opción D — aceptar y subir

El "max 32.9%" en t=292 puede no ser visible en pantalla real (el detector
analiza patches 128×128, no perceptual). Validar visualmente en el video
final antes de descartar.

## Recomendación

Hacer **A primero** (subir v11 unlisted a YouTube real). Es gratis y rápido.
Si el resultado en YouTube real es peor que en el emulator → **B** (shader
fix). Si es mejor o tolerable → ship.

## Archivos relevantes

- `transmissions/01/video/out/1-outbound.mp4` (= v11 master)
- `transmissions/01/video/out/1-outbound_yt.mp4` (YT trim 7:59.36)
- `transmissions/01/video/youtube_emulate.sh`
- `transmissions/01/video/banding_detect.py`

## Lecciones para la biblia

1. **NO usar `noise=` filter en master encode** — confunde VP9, empeora
   banding catastróficamente.
2. **NO usar grain plate overlay con blend modes** — marginal regression vs
   baseline en este pipeline.
3. **El cuello de botella está en VP9 8-bit 20Mbps de YouTube**, no en el
   master. Cualquier fix tiene que ser invisible al encoder de YouTube.
4. **El "punto de no progreso" debe ser respetado** — 4 iters sin mejora
   significan cambio de strategy, no más iters.
