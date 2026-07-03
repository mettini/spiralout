# Spiral Out Video Pipeline — biblia

> **El norte de calidad** para todos los videos del proyecto Spiral Out.
> Codifica las técnicas, los parámetros, los antipatterns y el workflow
> validado a través de Heliopause (2026-05/06).
>
> **Cuando empecés un video nuevo: leelo entero antes de tocar nada.**

## 0. Filosofía

### Lo que perseguimos

- **Calidad pro real** en delivery a YouTube — cero banding visible, sin
  stutter, color management correcto, comparable a estudios profesionales.
- **Pipeline code-driven** — todo reproducible desde código, sin GUI
  dependency. Vos no usás Resolve / Premiere / etc.
- **Iteración rápida** — herramientas que detectan problemas localmente
  (sin subir a YouTube para validar).
- **Costo zero** — todas las herramientas son free + open source.

### Lo que NO perseguimos

- Editing/composing visual interactivo (eso es Resolve / Premiere)
- Color grading complejo per-scene (no es nuestro caso de uso)
- Multi-cam (no aplica a visualizers)

---

## 1. Targets de calidad por video

Antes de declarar un video "listo", tiene que pasar:

| Métrica | Target | Validación |
|---|---|---|
| Resolución | 3840×2160 (4K UHD) | ffprobe |
| Frame rate | 24/30 fps (24 para crossing-style ambient, 30 para outbound-style motion) | ffprobe |
| Pixel format | yuv420p10le (10-bit) | ffprobe |
| Color space | BT.709 SDR | ffprobe |
| Bitrate master | 60-80 Mbps CBR HEVC | ffprobe |
| Audio | AAC 320 kbps, 44.1 kHz, stereo | ffprobe |
| Detector banding master | **0% banded en todos los frames** | `banding_detect.py` |
| Detector banding YouTube-emulated | **< 0.5% banded en todos los frames** | `youtube_emulate.sh` + `banding_detect.py` |
| Duración master | Match del audio master exacto | ffprobe |
| Duración YouTube version | `master_duration - 0.75s` (evita rebote a +1) | ffprobe |
| Visual TV (real test) | Sin stutter, sin banding, sin crushed blacks | mirarlo en TV grande |

**Si NO pasa los thresholds, no es entregable. Punto.**

---

## 2. Pipeline architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. SHADER / SOURCE                                                    │
│    Python + moderngl + GLSL fragment shader                          │
│    Output: stream raw RGB48LE (16-bit per channel)                   │
│    Dither pixel-level INSIDE el shader (pre-gamma)                   │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 2. INTERMEDIATE — ProRes 422 HQ                                       │
│    ffmpeg con prores_ks profile:v 3                                  │
│    10-bit 4:2:2, ~200 Mbps, BT.709 tagged                            │
│    Es el "negative" digital de cada video. NO se sube a YouTube.     │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3. GRAIN PLATE OVERLAY                                                │
│    ffmpeg blend overlay con grain plate generado (blue noise filt.)  │
│    Strength variable per-scene (default 0.35-0.50)                   │
│    Loop temporal coherent (8-12s grain plate, loop randomized)       │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 4. MASTER ENCODE — HEVC main10 SDR BT.709                             │
│    libx265 profile main10, yuv420p10le                               │
│    CBR 60-80 Mbps (depende del contenido)                            │
│    psy-rd=2.0 + no-strong-intra-smoothing=1 para preservar grain     │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 5. VALIDATION LOCAL                                                   │
│    banding_detect.py sobre master → 0%                               │
│    youtube_emulate.sh → VP9 20Mbps                                    │
│    banding_detect.py sobre output emulated → < 0.5%                   │
│    Si NO pasa: tuning grain o re-render shader.                      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 6. YT TRIM + UPLOAD                                                   │
│    Master = full duration                                            │
│    YT version = master - 0.75s (evita rebote de duración)            │
│    Upload SDR (NO HDR — YouTube castiga HDR fallback)                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Técnicas detalladas

### 3.1 Shader dither (pre-quantization)

**Por qué**: cuando renderás 16-bit float → 8-bit container, hay quantization
inevitable. Sin dither, los gradientes lentos quedan en plateaus → banding.

**Cómo**: dentro del fragment shader, en el output, sumar noise multi-canal:

```glsl
// CRITICAL: precision-safe seed (NO usar u_seed directo si crece con frames)
float s = fract(u_seed * 0.000312345);

// Per-channel isotropic dither, 12/255 amplitude probado óptimo
float dhR = hash21(rot1 + vec2(s * 113.0, s * 191.0));
float dhG = hash21(rot2 + vec2(s * 167.0, s * 89.0));
float dhB = hash21(rot3 + vec2(s * 53.0, s * 251.0));
col += vec3(dhR - 0.5, dhG - 0.5, dhB - 0.5) * 12.0 / 255.0;
```

**Tuning**:
- Amplitud 12/255 = sweet spot. Menos = banding. Más = ruido visible.
- Crossing-style ambient: 12-14
- Outbound-style detail: 12-16
- Bright high-contrast: 8-10 (menos necesario)

**Antipattern crítico**:
- `hash21(rot1 + u_seed * vec2(113.0, 191.0))` con `u_seed` creciente sin
  `fract()` previo → pierde precisión float32 a partir del frame ~100.
  Effective dither = 5% del intentado → banding masivo.
- Ver: `_iteration_logs/checkpoint_2026-06-08.md` punto bug hash21.

### 3.2 Gamma lift para visibilidad TV

**Por qué**: TVs y monitores en consumer-grade aplican gamma + crushean
blacks < ~10/255. Verde anegrado nativo (luma 10-15/255) se ve negro plano
en TVs no calibradas.

**Cómo**: aplicar gamma < 1 en el shader pre-dither:

```glsl
col = pow(max(col, vec3(0.0)), vec3(0.78));
```

**Tuning** (sweet spots validados Heliopause):
- 0.82 = mínimo necesario para visibilidad TV
- **0.78 = óptimo** (mantiene carácter dark, suficiente brillo)
- 0.75 = límite máximo (empieza a perder verde anegrado)
- 0.70 = demasiado brillante (rompe estética)

**Validación**: mirar el render en una TV real, NO solo monitor calibrado.

### 3.3 Grain plate overlay (post-shader)

**Por qué**: el dither del shader sobrevive el HEVC master pero VP9 8-bit
20Mbps de YouTube lo smoothea. Necesitamos un grain de **mayor amplitud +
patrón perceptualmente correcto** para sobrevivir el re-encode de YouTube.

**Cómo**: grain plate = video separado de noise con distribución blue noise
(no random), overlay sobre el master en blend mode "overlay" al ~5-10%
opacity:

```bash
ffmpeg -i master.mp4 -i grain_plate.mp4 \
  -filter_complex "[1:v]format=rgb24,colorchannelmixer=aa=0.06[grain];[0:v][grain]overlay=shortest=1" \
  -c:v libx265 ... output.mp4
```

**Tuning**:
- Opacity 0.04-0.06 = sutil pero efectivo
- Opacity 0.08-0.10 = bandas tercas (bloom scene tipo outbound)
- Opacity > 0.12 = grain visible como ruido

**Grain plate generation**: ver `experiments/grain_pipeline/gen_grain_plate.py`.
Blue noise vía white noise + high-pass filter. Loop temporal coherent.

### 3.4 Encoding params

**HEVC master** (sube a YouTube como input):

```bash
-c:v libx265 -profile:v main10 -pix_fmt yuv420p10le
-color_primaries bt709 -color_trc bt709 -colorspace bt709
-x265-params "colorprim=bt709:transfer=bt709:colormatrix=bt709:repeat-headers=1:bitrate=80000:vbv-maxrate=80000:vbv-bufsize=160000:nal-hrd=cbr:strict-cbr=1"
-preset medium
-c:a aac -b:a 320k
```

**Por qué CBR 80M**:
- YouTube recomienda 35-45 Mbps para 4K SDR. CBR 80M le da headroom para
  preservar fine detail.
- nal-hrd=cbr + strict-cbr=1 = forzar bitrate FLOOR uniforme, no caer en
  zonas dark.

**Por qué preset medium (no slow)**:
- Slow es 2-3x más lento. Diferencia visual a este bitrate: imperceptible.
- Medium ya da QP <15 = sustancialmente lossless.

**Antipattern crítico**: NO subir HDR HLG. Ver `21_distribution_encoding.md`
y checkpoint 2026-06-08. YouTube castiga el SDR fallback de uploads HDR.

### 3.5 Color management

**Mínimo viable**:
- Tag input como `-color_primaries bt709 -color_trc bt709 -colorspace rgb`
  cuando viene de shader.
- Output siempre `bt709 / bt709 / bt709` para SDR YouTube.

**Pro-grade (futuro)**: adoptar OpenColorIO para conversiones consistentes.
No es necesario para Heliopause-style ambient. Sí para futuros con HDR
intent.

### 3.6 Frame rate

- **30 fps**: motion graphics, raymarched scenes con cámara (outbound-style)
- **24 fps**: ambient contemplativo, escenas estáticas (crossing-style)
- **12 fps source**: SI es AI-generated (recursion-style) → minterpolate
  a 24fps para evitar stutter en TVs 60Hz

**Minterpolate command** (para 12fps source):
```bash
ffmpeg -i source_12fps.mp4 -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,format=yuv420p10le" ...
```

### 3.7 Duraciones y YT trim

- Master = duración exacta del audio
- YT version = master − 0.75s (evita el rebote: si master dura 480.0s,
  YouTube puede mostrar 8:01 por audio AAC overflow)

```bash
ffmpeg -i master.mp4 -to {duration - 0.75} -c copy -avoid_negative_ts make_zero output_yt.mp4
```

---

## 4. Validation workflow obligatorio

**ANTES de declarar entregable**:

```bash
cd transmissions/NN/video

# 1. Health check del detector
.venv_detect/bin/python banding_detect.py --test
# DEBE pasar todos los casos sintéticos

# 2. Detector sobre master
.venv_detect/bin/python banding_detect.py out/N-track.mp4 --interval 15
# DEBE dar avg < 0.5%, max < 2%

# 3. YouTube emulator
./youtube_emulate.sh out/N-track.mp4 /tmp/N_yt.webm
# Toma ~30-45 min

# 4. Detector sobre emulated
.venv_detect/bin/python banding_detect.py /tmp/N_yt.webm --interval 10
# DEBE dar avg < 0.5%, max < 1%

# 5. Visual TV (manual)
# Mandate vos a una TV grande y mirá scenes críticas:
# - Zonas dark con gradient (escena principal del track)
# - Lens flares / spirals (si aplica)
# - Transiciones de scene
```

**Si CUALQUIERA falla → re-render con tuning → repetir.**

---

## 5. Antipatterns conocidos

Esto NO hacer, lo pagamos caro:

1. **Subir HDR HLG a YouTube**: pensamos que el viewer HDR lo iba a ver
   bien. Resultado: el 95% que ve SDR fallback ve banding terrible. SDR
   directo upload es la respuesta.
2. **Dither shader sin precaution de precision (hash21 bug)**: u_seed
   creciendo sin `fract` → float32 garbage en hashes → dither 5% efectivo.
3. **CBR ABR con bitrate floor sin enforce**: `-b:v 100M` sin nal-hrd=cbr
   → encoder baja bitrate cuando contenido "simple" → banding.
4. **Tonemap intermedio**: HDR → tonemap → SDR encode introduce smoothing
   adicional. Encode SDR DIRECTO desde shader.
5. **noise=10 en post-master sin grain plate**: backfire — crea bandas
   adicionales. Necesita grain plate proper.
6. **preset slow en HEVC**: pérdida de tiempo, mismo result.
7. **Iterar visualmente en preview chico**: el detector + emulator es
   más confiable que mirar PNG escalado a 1080p.
8. **Pipe RGB directo a ffmpeg con HDR conversion**: zscale necesita el
   input tagueado correctamente. Sin tag → "no path between colorspaces".

---

## 6. Tuning guide rápido

### Caso 1: detector master CLEAN, emulator dice banding

→ Subir grain plate opacity (0.06 → 0.08 → 0.10)
→ Si nada: subir dither shader (12 → 14 → 16)
→ Si nada: subir bitrate master (80 → 100 Mbps)

### Caso 2: visual "muy oscuro" en TV

→ Bajar gamma 0.82 → 0.80 → 0.78
→ Si igual oscuro: subir floor del palette directly
→ Validar en TV real, no monitor

### Caso 3: visual "muy ruidoso"

→ Bajar grain plate opacity
→ Bajar dither shader

### Caso 4: stutter en TV (especialmente para 12fps AI generated)

→ Minterpolate fps=24
→ Si stutter persiste: minterpolate fps=30

### Caso 5: scene jumps perceptuales (camera roll, fades)

→ Verificar bug hash21 fix aplicado (causa más probable)
→ Si persiste post-fix: extender fade-in (5s → 8s)
→ Si persiste: revisar shader-specific camera/transformation code

---

## 7. Roadmap futuro

### Mejoras que SÍ podemos hacer (rank de impacto)

1. **VapourSynth full pipeline** (en progreso 2026-06-08): bluenoise dither
   real + grain plate temporal coherent + multi-pass encoding
2. **OpenColorIO**: color management profesional
3. **Multi-pass encoding**: encoder ajusta bitrate per-scene complexity
4. **VMAF-driven iteration**: medir calidad perceptual end-to-end

### Para Transmission 02+

- Si tema es visual procedural complejo: **migrar a Blender + Resolve**
  (research en `24_pro_pipeline.md`)
- Si tema mantiene estética minimalista tipo Heliopause: **seguir Python
  shader + VapourSynth + ffmpeg**

---

## 8. Tools del repo

| Tool | Path | Qué hace |
|---|---|---|
| Detector banding | `transmissions/01/video/banding_detect.py` | v10 con run-length signature |
| Test bench detector | `transmissions/01/video/banding_test_bench.py` | 6 casos sintéticos |
| YT emulator | `transmissions/01/video/youtube_emulate.sh` | Reproduce VP9 20M SDR fallback |
| Grain plate gen | `transmissions/01/video/experiments/grain_pipeline/gen_grain_plate.py` | Blue noise 4K |

## 9. Referencias

- `20_technical_reference_videos.md` — Heliopause per-track technical reference
- `21_distribution_encoding.md` — encoding params + duals master/YT
- `22_banding_detection_validation.md` — detector algoritmo + bug hash21
- `23_iteration_log_2026-06-08.md` (en `_iteration_logs/`) — historia tuning Heliopause
- `24_pro_pipeline.md` — research Blender + Resolve para futuros transmissions
- `_iteration_logs/checkpoint_2026-06-08.md` — estado actual files Heliopause
