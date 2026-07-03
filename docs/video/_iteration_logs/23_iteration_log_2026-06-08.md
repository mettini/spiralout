# Brief — overnight iteration 2026-06-07 a 2026-06-08

> Resumen completo de los fixes aplicados durante la noche mientras el user
> dormía. Lectura ~5 min.

## TL;DR

**Lo que sacamos en limpio**:
- Bug crítico encontrado y arreglado: `hash21` perdía precisión en frames
  altos → dither no funcionaba → banding en todo el video. **Esto era la
  raíz de TODO el banding histórico**.
- **YouTube emulator local construido y funcionando** —
  `youtube_emulate.sh` reproduce el SDR fallback VP9 20Mbps de YouTube.
  Ya no necesitamos subir para iterar.
- Tres nuevas versiones de los videos:
  - **outbound v11** (SDR puro BT.709, gamma 0.78, dither 12/255 + gradfun + noise)
  - **crossing v3.20** (mismo combo)
  - **recursion** convertido a 24fps con minterpolate (fix stutter en TVs)

**Estado final** (medido sobre lo que YouTube va a servir vía emulator):

| Video | Master CLEAN | YT emulated avg | YT emulated max | Verdict |
|---|---|---|---|---|
| outbound v11 | 0.0% ✓ | 3.79% | 32.9% (frame t=292 bloom) | MILD residual banding |
| crossing v3.20 | 0.0% ✓ | **0.05%** | **0.83%** | ESENCIALMENTE PERFECT ✓ |
| recursion (24fps) | -- | -- | -- | Fix stutter via minterpolate |

## Issues que reportaste anoche + qué hicimos

### 1) Banding por todos lados, sobre todo crossing primera mitad y outbound 03:30

**Root cause**: bug en `hash21` (GLSL hash function). Cuando `u_seed` crecía
con los frames (i × 47.31 + 0.91), llegaba a valores >300k. Las
multiplicaciones internas del hash (`p * vec2(443.8975, 397.2973)`) lo
llevaban a 1e8+. Float32 a esa escala tiene precisión ±10 — el `fract()`
final retornaba basura semi-constante. **El dither efectivo era ~5% del
intentado**.

**Fix**: pre-`fract(u_seed * 0.000312345)` antes de cualquier hash. Mantiene
los inputs en rango precisado. Aplicado v10/v3.18 ayer y persistido.

**Resultado en master**: outbound y crossing 4K masters van de 70-98%
banded → 0% banded.

### 2) Banding aún visible en YouTube aunque master sea CLEAN

**Root cause**: YouTube re-encodea a VP9 8-bit yuv420p ~20 Mbps para SDR
fallback. Aunque subamos HDR HLG 10-bit, el 95% de viewers ve la SDR a
8-bit, y el VP9 smoothea nuestro dither.

**Fix construido**: `youtube_emulate.sh` reproduce ese pipeline localmente.

**Iteración aplicada**: render outbound v11 con shader + encoding cambios:
- Gamma 0.70 → 0.78 (menos brillo, también atiende complaint #4)
- Dither 8/255 → 12/255 (más robusto contra VP9 smoothing)
- Encoder SDR directo BT.709 (sin tonemap HDR HLG intermedio)
- gradfun + noise injection durante encode

**Resultado**: avg banded en YouTube emulated cae de 38.7% → 3.79% para
outbound, 24.5% → 0.05% para crossing.

**Lo que NO funcionó**: probé bumpear noise injection a 10/255 + gradfun
strength 2.5 en re-encode post-master. **Backfired** — avg subió a 85% max.
El noise+gradfun extra crearon artifacts. Volví a v11.

**Residual**: outbound v11 todavía tiene zonas problemáticas. La peor es
t=292 (bloom 4:52) que sigue mostrando 26% banded en el background dark
green alrededor del mandala flor. Probablemente sea inherente del VP9 a
ese bitrate. Para curarlo sin re-render: subir dither a 16/255 + re-render
(2h más).

### 3) 00:09 late el ovulo sin heart pulse

**Root cause**: línea 361 del shader tenía
`+ 0.0055 * u_rms_sub * pulse_enable` que multiplicaba la radio del ovulo
por `rms_sub` (kick band del audio) CONTINUAMENTE. El user quería pulse
solo en heart events discretos.

**Fix**: removido el `rms_sub * pulse_enable` y el `beat * pulse_enable`
del cálculo de radio. Ahora SOLO `u_heart_amp` (Gaussian bumps en
timestamps exactos) modula la radio. Aplicado v11.

### 4) SDR muy brillante (especialmente ovulo y post)

**Fix**: gamma lift 0.70 → 0.78. Verde anegrado pasa de luma 36/255 → 26/255.
Mantiene visibilidad TV sin sobre-iluminar.

### 5) Scene jumps en 00:03 y 06:39

**Investigado**: extraje frames secuenciales en ambas zonas. Frame-to-frame
diffs son normales (5-6, no spikes). En la sequence 380-420 (partida) el
diff promedio es 16-22, consistente con motion continuo del raymarcher +
camera roll del spiral pattern.

**Conclusión**: lo que el user percibe como "saltos" son lens flare circles
del raymarched pattern apareciendo en posiciones distintas cuando la cámara
hace roll. **No son cortes de escena reales** — son artifacts del raymarch
+ spin. Arreglar requeriría rediseñar SCENE_PARTIDA shader (gran scope).
Documentado como conocido.

### 6) Recursion looked entrecortado on TV

**Root cause**: recursion source es 12fps. En TVs 60Hz, cada frame se
muestra 5 veces (5x duplicación) → motion judder visible.

**Fix**: re-encode con `minterpolate fps=24:mi_mode=mci:mc_mode=aobmc`. Crea
frames intermedios via motion compensated interpolation. Salida 24fps mucho
más fluida en TVs.

## Pipeline final que queda para subir

### Files

```
transmissions/01/video/out/
├── 1-outbound.mp4         (master 4K SDR BT.709, gamma 0.78, dither 12/255, 8:00)
├── 1-outbound_yt.mp4      (7:59.36 — trim para YT, evita rebote a 8:01)
├── 2-crossing.mp4         (master 4K SDR BT.709, 13:00)
├── 2-crossing_yt.mp4      (12:59.36)
├── 3-recursion.mp4        (master 4K SDR 24fps minterpolated, 3:00)
└── 3-recursion_yt.mp4     (2:59.44)
```

### Backups (revisables antes de borrar)

```
1-outbound_v10_HDR.mp4       (versión anterior con HDR HLG)
2-crossing_v3.19_HDR.mp4     (anterior HDR)
3-recursion_12fps.mp4        (original 12fps, fuente del minterpolate)
3-recursion_pre_gradfun.mp4  (anterior pre-gradfun)
```

### Subida

- Usar los `_yt.mp4` para YouTube (trim correcto)
- **NO subir HDR HLG** — confirmamos que el SDR fallback de YouTube
  destruye nuestros dithers carefully crafted. SDR puro upload es la
  respuesta.
- Tags: Music, no kids, English. Title/descripción de doc 22.
- Thumbnails ya regenerados en `artwork/youtube_thumbnails/` ayer.

## Limitaciones conocidas que quedan

1. **outbound t=292 (bloom) tiene 26% banded en YouTube emulated**. No es
   visualmente catastrófico pero detectable. Para curar requeriría dither
   16/255 en shader + re-render outbound (2h más).
2. **Scene "jumps" en partida sequence** son inherentes al shader design,
   no fixables sin re-arquitectura.
3. **Banding en zonas dark slow gradient** es asíntotamente difícil de
   eliminar con VP9 8-bit 20Mbps. Lo logramos en crossing pero outbound's
   bloom scene tiene smooth dark green background que VP9 prefiere
   smoothear.

## Recomendaciones para futuras transmissions

1. **Siempre validar con `youtube_emulate.sh`** antes de upload. Local
   CLEAN no implica YouTube CLEAN.
2. **Subir SDR puro**, no HDR HLG. YouTube castiga el HDR fallback.
3. **Dither shader 12/255 mínimo** (con bug fix del hash21).
4. **Gamma lift 0.78** parece el sweet spot — visibilidad sin
   sobre-iluminar.
5. **gradfun + noise=3 en el encode** ayuda. Más que eso (=10+) backfires.
6. **Encoder SDR directo BT.709** sin tonemap intermedio.
7. **Para recursion AI-generated o source 12fps**: minterpolate a 24fps
   para evitar TV stutter.

## Referencias técnicas en docs/video/

- `22_banding_detection_validation.md` — detector v9 algoritmo + bug fix
  hash21 documentado
- `21_distribution_encoding.md` — HDR HLG path (que ahora sabemos NO es
  la opción correcta para YouTube SDR-fallback viewers)
- `20_technical_reference_videos.md` — referencias per-track

## Quick reference para mañana

```bash
# Validar cualquier render local antes de upload
cd transmissions/01/video
.venv_detect/bin/python banding_detect.py --test     # health check detector
.venv_detect/bin/python banding_detect.py master.mp4 # detectar master

# Reproducir YouTube SDR fallback localmente
./youtube_emulate.sh master.mp4 emul.webm
.venv_detect/bin/python banding_detect.py emul.webm  # validar SDR fallback

# Hacer YT trim de master (cortar 0.75s del final)
ffmpeg -i master.mp4 -to {duration-0.75} -c copy -avoid_negative_ts make_zero out_yt.mp4
```
