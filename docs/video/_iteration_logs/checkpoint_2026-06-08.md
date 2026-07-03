# Checkpoint Heliopause — 2026-06-08

> Punto de control del estado actual. Lo que tenemos, lo que está roto, lo
> que es experimento.

## TL;DR

- **Crossing**: prácticamente perfecto (0.05% banded en YT emulated). Subible.
- **Recursion**: convertido a 24fps, stutter de TV resuelto. Subible.
- **Outbound**: 3.79% banded en YT emulated. **No subible bajo estándar de
  "sin banding". Va a Resolve para fix definitivo via film grain.**
- **Pipeline pro nuevo**: Python+Resolve híbrido — ver `24_pro_pipeline.md`.

## Status por video

### crossing
- File: `transmissions/01/video/out/2-crossing.mp4` (master 4K SDR, 7.3 GB)
- File: `transmissions/01/video/out/2-crossing_yt.mp4` (YT trim, 12:59.36)
- Detector master: 0.0% banded ✓
- Detector YT emulated: **0.05% avg, 0.83% max** ✓
- Verdict: **SUBIBLE como está**. Pasa todos los test.

### recursion
- File: `transmissions/01/video/out/3-recursion.mp4` (master 4K SDR 24fps)
- File: `transmissions/01/video/out/3-recursion_yt.mp4` (YT trim, 2:59.36)
- Convertido de 12fps source via minterpolate (mci aobmc) → 24fps
- Verdict: **SUBIBLE como está**. Stutter de TV solucionado por interpolation.
- Caveat: no validé visualmente en una TV — confirmar fluidez antes de
  decidir.

### outbound
- File: `transmissions/01/video/out/1-outbound.mp4` (= v11 master)
- File: `transmissions/01/video/out/1-outbound_yt.mp4` (YT trim, 7:59.36)
- File: `transmissions/01/video/out/1-outbound_v11.mp4` (backup, mismo
  contenido)
- Detector master: 0.0% banded ✓
- Detector YT emulated: **3.79% avg, 32.9% max** (max en t=292 bloom scene)
- Verdict: **NO SUBIBLE bajo estándar perfect**. Banding visible en YouTube
  específicamente en el background del bloom 4:52.
- Decisión: ir a Resolve para film grain → ProRes 4444 + Resolve workflow.

### Versiones backupeadas (para no perder progresión)

```
1-outbound_v10_HDR.mp4              # v10 con HDR HLG (tenía banding en YT)
1-outbound_v11.mp4                  # v11 actual con bug fix hash21 + dither 12/255 + SDR
2-crossing_pre_bugfix.mp4           # antes del bug fix hash21
2-crossing_v3.19_HDR.mp4            # versión HDR previa
3-recursion_12fps.mp4               # 12fps original (pre minterpolate)
3-recursion_pre_gradfun.mp4         # antes de gradfun
```

## Lo que se solucionó esta noche/madrugada

1. **Bug hash21 GLSL**: la función hash perdía precisión float32 con seeds
   altos → dither shader trabajaba al 5% de amplitud intentada. Root cause
   de todo el banding histórico. Fix: pre-fract el seed.
2. **Heart pulse 0:09 ovulo**: removido rms_sub continuo, sólo eventos
   discretos.
3. **Recursion stutter en TV**: minterpolate a 24fps.
4. **Brightness SDR**: gamma 0.70 → 0.78.
5. **Scene jumps 0:03 y 6:39**: confirmado que eran artifacts del bug
   hash21, ya no aparecen.

## Lo que queda pendiente

1. **Outbound bloom scene banding**: 26-32% banded en YT emulator. NO
   resolvible solo con shader iteration. Va a Resolve workflow (ver
   `24_pro_pipeline.md`).
2. **Validación visual en TV**: recursion 24fps necesita validation real.
3. **Migración pipeline pro**: empezamos hoy con outbound como
   experimento. Si funciona, aplicamos a crossing+recursion también para
   consistencia.

## Herramientas que dejé construidas

### YouTube emulator local

`transmissions/01/video/youtube_emulate.sh`

Reproduce el SDR fallback de YouTube (VP9 20Mbps 8-bit BT.709) localmente.
Ya no necesitamos subir un video para saber si va a tener banding.

```bash
./youtube_emulate.sh input.mp4 output.webm
```

### Detector de banding programático

`transmissions/01/video/banding_detect.py`

V10 (current) con test bench sintético validado. Detecta banding via
run-length signature en patches 128×128.

```bash
.venv_detect/bin/python banding_detect.py --test        # validate detector
.venv_detect/bin/python banding_detect.py video.mp4     # analyze
```

## Iteraciones técnicas que NO funcionaron

Para que no las re-probemos:

1. **HDR HLG upload**: pensamos que iba a ayudar. **NO** — YouTube castiga
   el SDR fallback de uploads HDR. Subir SDR directo es mejor.
2. **Dither shader > 16/255**: a partir de ahí, ruido visible.
3. **gradfun + noise=10 post-master**: backfired, creó más bandas (avg
   85% YT emulated). Demasiado processing chain.
4. **SVT-AV1 con film-grain=16**: mejora marginal, no resuelve. HEVC + bug
   fix es mejor camino.
5. **Tonemap mobius vs reinhard vs hable**: cualquiera de los 3 deja
   banding similar en YouTube SDR fallback. La diferencia no es ahí.

## Pipeline propuesto adelante

Ver `24_pro_pipeline.md` — adopción híbrida Python + DaVinci Resolve.

Para Transmission 02: research Blender como render engine (notas en mismo
doc).
