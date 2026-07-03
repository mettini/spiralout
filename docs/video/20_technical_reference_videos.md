# Bajada técnica de los videos — Transmission 01

Reference técnico de los 3 videos producidos. Codifica las técnicas,
patrones, lessons learned, y consideraciones para mantener / iterar / promover.

> Pareja con `transmissions/01/video/CONTEXT_VIDEO_PROJECT.md` (estado y
> evolución por versión). Este doc es la **teoría**; el otro es la **bitácora**.

---

## 0. Mapa de los videos

| Track | Versión actual | Folder lab | Estilo / pipeline |
|---|---|---|---|
| **Outbound** | `outbound_3d_rerender` (v6 en render) | `transmissions/01/video/experiments/outbound_3d_rerender/` | 3D raymarched, escenas distintas por momento del track |
| **Crossing** | `crossing_turrell_v3` (v3.16 en render) | `transmissions/01/video/experiments/python_v3/crossing_turrell_v3/` | Campo Turrell-ish, sombra+silueta+julia, single shader |
| **Recursion** | Original AI (Veo 3 / Hydra mix) | `transmissions/01/video/out/3-recursion.mp4` | Generado por modelo AI generativo de video |

Los **masters de audio** son intocables:

```
transmissions/01/release/masters/01_outbound_master.wav  (8:00)
transmissions/01/release/masters/02_crossing_master.wav (13:00)
transmissions/01/release/masters/03_recursion_master.wav (3:00)
```

Los **control tracks** (features audio @ 30 fps):

```
transmissions/01/video/control/{outbound,crossing,recursion}.npz
```

Generados con `analyze.py`. Bandas:
- `rms`         energía global
- `rms_sub`     30-55 Hz (heartbeat / kick)
- `rms_low`     55-250 Hz (bass / voice fundamentals)
- `rms_air`     4-10 kHz (bells / tilín / aire)
- `centroid`    centro espectral
- `flux`        cambio espectral (movimiento / morphing)
- `onset`       1.0 en transientes

---

## 1. Outbound — `outbound_3d_rerender`

### 1.1 Concepto

8 minutos de despegue / journey al espacio. Estructura de 6-7 momentos
distintos (nacer → tunel → humo → mandala → portal/chamber → partida →
afuera). Cada momento es una **escena 3D raymarched distinta**,
encadenadas por transiciones cuidadas.

> El user explícitamente rechazó:
> - Post-procesamiento del Hydra original (se ve filtrado, no nuevo)
> - Efectos sutiles que no se ven (homeopáticos)
> - Estrellitas fake / partículas dust como "decoración"
> - Fades a negro entre escenas con luz ("estás en un viaje dimensional y
>   hacés fades?!?")

### 1.2 Pipeline técnico

```
moderngl GLSL fragment shader (uno por escena)
    ↓ render a float32 framebuffer
    ↓ convert a uint16 (16-bit por canal)
    ↓ stream rgb48le a ffmpeg stdin
    ↓ ffmpeg libx264 high10 yuv420p10le CRF 17 preset fast
    ↓ AAC 192k mux desde 01_outbound_master.wav
    ↓ final_4k.mp4
```

**4K 3840×2160 @ 30 fps = 14400 frames.** Render time típico ~50 min.

### 1.3 Escenas y técnicas por escena

#### Scene NACER (0:00 → 1:15)
- **Técnica**: esfera raymarched ("ovulo / planeta") con iris pattern + halo
- **Material**: textura procedural fibrosa + FBM displacement
- **Audio-reactivo**:
  - Heart pulses (eventos discretos en `rms_sub`) → radius scale ±2%
  - Bell sparkles (eventos discretos en `rms_air`) → star burst con
    diffraction spikes thin rays, 2 tipos (A fast/small + B slow/halo)
- **Lesson learned**: la sincronización debe ser por **eventos discretos
  hardcodeados** (lista de timestamps específicos), no por smoothed
  continuous values. Smoothed values dan respuesta promediada que no
  matchea el momento musical exacto.
- **Antipattern**: sparkle dispersos (sin gate temporal) producen "diagonal
  sweep artifacts" porque cualquier centroid spike los activa.

#### Scene DIVE (1:15 → 1:20)
- **Técnica**: cámara Z se mueve hacia adentro de la pupila del ovulo.
  El centro oscuro de la pupila → tunnel entry.
- **Implementación**: en lugar de fade, **animación de cámara Z** continua,
  el ovulo grows on screen, dark center fills the frame → eres dentro del
  tunnel. NO fade plano.

#### Scene TUNEL (1:15 → 3:28)
- **Técnica**: corredor cilíndrico raymarched
  - SDF `length(p.xy) - radius + displacement`
  - Wall texture: FBM 3D con `pTex.z += u_camera_z` (cámara moviéndose en Z)
  - Core light al vanishing point con halo Gaussiano
- **Camera Z velocity**: ~2.85 unidades/seg (después de slowdown -37% v5)
- **Audio-reactivo**: core intensity = `0.45 + 0.55 * rms_sub + 0.30 * onset`
- **Lesson learned**: el core no debe ser una "pelota" separada — debe
  integrarse con los rings del tunnel mediante un smoothstep ancho.
  Antipattern: `pow(vanish, 1.4) * 0.30` que crea un punto negro
  imperceptible pero feo.

#### Scene HUMO (3:28 → 4:23)
- **Técnica**: volumetric ray-marching de fog con multi-octave noise advectado
  por flow field lento. Densidad varía orgánicamente.
- **Color**: verde anegrado claro con bleed de luz del tunnel previo
- **Transición desde tunnel**: xfade asimétrico `tunel(0.8) → humo(0.2)`
  de duración 8s + 2s

#### Scene MANDALA BLOOM (4:23 → 5:12)
- **Técnica**: 2D radial pattern con simetría 8-fold, abre como flor en
  bloom phase, cierra en close_phase
- **NO 3D rods/bastones**: el agente intentó "petals como bastones 3D" y
  fue rechazado (lookea como 3 palitos en cruz)
- **Timing**: bloom open 0-0.57, close 0.57-0.90, dive into close 0.90-1.0
- **Audio-reactivo**: `u_breath` modula radial scale ±8%, `u_lumin` modula
  ember intensity en focos
- **Close_phase trigger**: at scene_t=0.57 (t=291s = 4:51) ← user lo pidió
  específicamente coincidiendo con un cambio musical

#### Scene PORTAL/CHAMBER (5:12 → 6:00)
- **Técnica**: kaleidoscopic IFS (KIFS) o Mandelbox, fractal folding
- **Walls dinámicos**: fold offsets oscilando con `sin(u_time * 0.20)`,
  camera roll continuo `t * 0.25`
- **Antipattern**: paredes static = "cartón pintado". REQUIERE movimiento
  real (camera roll + fold rotation evolving)
- **Visual event at 5:49**: roll acceleration + fold morph speed double
  para acompañar "enrollamiento" rítmico de la música

#### Scene PARTIDA (6:00 → 7:00)
- **Técnica**: 3D spiral magnetar (logarithmic spiral arm raymarched)
- **Camera**: drift forward + slow rotation

#### Scene AFUERA (7:00 → 8:00)
- **Técnica**: volumetric yellow smoke con beams crossing
- **Cierre**: smoke invades todo, fade out natural por densidad

### 1.4 Transiciones — patrones validados

| Tipo | Cuándo usar | Implementación |
|---|---|---|
| **Dive-into** | Cuando hay una luz/forma central que el viewer puede "entrar" | Camera Z animation, target shape grows on screen, dark center → next scene |
| **Light flash** | Entre escenas que ambas tienen luz | Brief whiteout (~2s alrededor del boundary), next scene already in motion when light fades |
| **Asymmetric xfade** | Entre escenas con texturas similares (tunel→humo) | 8s old scene fade out / 2s new scene fade in, the longer tail lets old wash into new |
| **Eye-close** | Cambio dimensional grande (sleeping/awakening metaphor) | Slow fade-to-black (1.5s) + brief black hold (0.3s) + slow fade-from-black (1.5s) |
| **Fade plano** | **NUNCA entre escenas con luz**. Solo OK al inicio (negro → ovulo) | smoothstep multiplica final color |

> Regla: **el next scene tiene que arrancar YA EN MOVIMIENTO** en el frame
> post-transición. No frozen first frames.

### 1.5 Audio reactivity — patrones

**Para eventos discretos** (heart pulses, bell sparkles):
```python
EVENTS = [0.27, 0.917, 1.998, ...]  # timestamps en minutos
amp = 0.0
for ev_t in EVENTS:
    dt = t_min - ev_t
    if 0 <= dt <= 0.4/60:
        amp += np.exp(-(dt - 0.08/60)**2 / (2 * (0.08/60)**2))
```

**Para continuous response** (mandala breath):
```python
breath = 1.0 + 0.08 * rms_sub_smooth_at(t)
lumin  = 0.95 + 0.55 * onset_smooth_at(t)
```

### 1.6 Antipatterns detectados (Outbound)

1. ❌ Post-procesar el original Hydra (look filtrado, no nuevo)
2. ❌ Fades planos entre escenas con luz
3. ❌ Estrellitas fake / particles dust como decoración
4. ❌ Sparkle continuous-driven sin gate (cualquier centroid spike lo activa
   en momentos random)
5. ❌ Smoothstep "casi C∞" en escenas oscuras → inflexiones visibles como
   "ondas" / "capas"
6. ❌ Paredes static en chamber dimensional ("cartón pintado")
7. ❌ Tunnel core "pelota en el fondo" — debe integrarse con rings
8. ❌ Multi-pass particles fake — sin feedback buffer, los "trails" son hash
   noise pretending to be motion
9. ❌ Transiciones fijas en tiempos no-musicales (1:10 cuando el cambio
   musical está en 1:15)

---

## 2. Crossing — `crossing_turrell_v3`

### 2.1 Concepto

13 minutos de tránsito a través de la heliopausa. Campo Turrell-ish:
verde anegrado contemplativo + silueta humana (body + head) que cruza
el frame + phases de background (liso → nebula → fractales julia → vuelta
liso) + bells light al min ~11 (voyager echo).

**NO es Turrell puro** — tiene sombra, silueta, eventos. El nombre v3 es
histórico. Mejor descrito como "dark ambient field con silueta reactiva
y phases de textura".

### 2.2 Pipeline técnico

```
moderngl GLSL fragment shader (single shader, todo en uno)
    ↓ render a float32 framebuffer  ← CRÍTICO para evitar 8-bit banding
    ↓ convert a uint16 (rgb48le)
    ↓ stream a ffmpeg
    ↓ ffmpeg libx264 high10 yuv420p10le CRF 17 preset slow
    ↓ AAC 192k mux desde 02_crossing_master.wav
```

**4K 3840×2160 @ 24 fps = 18720 frames.** Render time típico ~50-60 min.

### 2.3 Elementos del shader

```glsl
// 1. Base verde anegrado (paleta Catmull-Rom temporal)
// 2. Phases del background (FBM-nebula × julia-fractales × liso)
// 3. Silueta s1 = body (ellipse) ∪ head (smaller ellipse, soft-OR)
// 4. Silueta s2 = atmospheric secondary (más grande, opacidad baja)
// 5. Bells light (Gaussian glow upper-left, 10:30-12:10)
// 6. Voyager lights (Gaussian glows upper-right en momentos específicos)
// 7. Vignette suave
// 8. Grain de "película"
// 9. Dither TPDF isotrópico
// 10. Fade in/out global
```

### 2.4 Paleta — Catmull-Rom verde anegrado

```python
PALETTE_STATIONS = [
    (0.00,  R, G, B),   # verde anegrado abierto
    (1.50,  ...),       # respira
    (3.00,  ...),       # peludo entrada: se cierra
    (4.30,  ...),       # peludo peak
    (5.30,  ...),       # respira fuerte
    (6.30,  ...),       # cruce heliopausa: se cierra
    (7.30,  ...),       # post-cruce: el más abierto
    (9.30,  ...),       # plateau verde sereno
    (10.50, ...),       # entrada bells
    (12.00, ...),       # bells
    (13.00, ...),       # asentamiento final
]
```

Catmull-Rom uniforme garantiza C¹ smoothness. Valores RGB en sRGB
normalized 0..1 lineales. El user iteró por ~5 versiones hasta encontrar
balance "no smoothie / no apagón".

### 2.5 Phases del background

```
0:00 - 2:00   LISO (solo campo)
2:00 - 2:30   cross-fade LISO → NEBULA
2:30 - 4:00   NEBULA (FBM 4.5x advectado, humo en movimiento)
4:00 - 4:30   cross-fade NEBULA → FRACTALES
4:30 - 6:30   FRACTALES (Julia set evolutivo, c se mueve por círculo)
6:30 - 8:30   cross-fade FRACTALES → LISO
8:30 - 13:00  LISO (estable para no chocar con bells light)
```

**Julia set**: la `c` se mueve por círculo en plano complejo
`c = 0.7885 * (cos(t*1.3), sin(t*1.7))` → estructura cambia continuamente.
**Auto-similaridad real, no FBM ni Voronoi**. El user rechazó esos pretenders.

### 2.6 Silueta — body + head (figura humana abstracta)

```
body  = ellipse (radius 0.20, falloff Gaussian, ecc 0.70 vertical)
head  = ellipse (radius 0.085, offset (0, -0.22) above body)
silhouette = 1 - (1-body) * (1-head)   # soft-OR
```

**Falloff Gaussiano** `exp(-(d/σ)²)` — no smoothstep (smoothstep produce
inflexiones visibles en gradientes lentos).

**Opacity schedule** (Catmull-Rom):
```
0:00  0.55
1:50  0.60
3:00  0.65
4:30  0.72   ← peak peludo (devora visible)
5:30  0.52
6:30  0.58
8:00  0.48
10:50 0.38
13:00 0.22
```

**Multiplicadores temporales**:
- Audio: `s1_op *= (1 + 0.30*rms_low + 0.10*flux)`
- **Late fade**: `s1_op *= clip((12-t_min)/1, 0, 1)` — silueta muere
  entre 11:00 y 12:00 (elimina overlap con bells light)
- **End fade**: `s1_op *= clip((13-t_min)/0.5, 0, 1)` — últimos 30s a 0

**Pinchudo border** durante peludo:
```glsl
if (peludo > 0.01) {
    vec2 noise = uv * 14.0 + vec2(t*jitter_freq, t*jitter_freq*0.93);
    uv_distorted = uv + (fbm2(noise) - 0.5) * 0.055 * peludo;
}
```
Distorsión de UV con FBM de alta freq + jitter freq 2 Hz (normal) a 8 Hz
(peludo peak) → bordes pinchudos + tembleque visible.

### 2.7 Bells light + Voyager lights

**Bells** (10:30-12:10):
- Position upper-left (0.13, 0.82)
- Gaussian radius 0.50, falloff 1.6
- Peak intensity 0.18, tint verde-amarillento (`#a6d65f`-ish)

**Voyager** (timestamps específicos en minutos):
```python
VOYAGER_MOMENTS_MIN = [
    0.27,    # 0:16
    0.917,   # 0:55
    1.998,   # 1:59
    2.258,   # 2:15
    3.098,   # 3:05
    4.754,   # 4:45
    7.325,   # 7:19
    7.590,   # 7:35
    8.423,   # 8:25
    9.255,   # 9:15
]
```
Cada uno: Gaussian bump en tiempo (sigma 4s), upper-right (0.87, 0.82),
peak 0.10 (más sutil que bells).

### 2.8 Pipeline 16-bit — CRÍTICO

```python
# Float32 framebuffer (no quantization en GL output)
color_tex = ctx.texture((W, H), 4, dtype='f4')

# Read float
raw = fbo.read(components=3, alignment=1, dtype='f4')
arr = np.frombuffer(raw, dtype=np.float32).reshape(H, W, 3)

# Convert a uint16 little-endian
arr_u16 = np.clip(arr * 65535.0, 0, 65535).astype('<u2')

# Stream a ffmpeg con rgb48le
# Encoder: yuv420p10le (10-bit final)
```

**Por qué**: a 8-bit en zonas oscuras de verde anegrado, cada paso de
1/255 se ve como arco concéntrico. Float32 → uint16 → 10-bit elimina la
cuantización en TODO el pipeline.

**Adicionalmente**: TPDF dither isotrópico (3 sin hashes sumados) amp
4/255 enmascara cualquier residual.

### 2.9 Antipatterns (Crossing)

1. ❌ Smoothstep para falloff de sombra/luz (inflexiones visibles en
   gradientes lentos). Usar Gaussian exp(-r²/σ²).
2. ❌ 8-bit pipeline en gradientes lentos → arcos concéntricos. Usar
   16-bit float framebuffer.
3. ❌ Hash sin-based amplitud > 1/255 → patrón crosshatch visible. Usar
   hash multi-componente sumado (≈ Gaussian).
4. ❌ s2 atmospheric con radius muy grande (0.55) y falloff ancho crea
   gradient overlap visible como ondas. Reducir multiplicador (0.18) y
   matar antes de end fade.
5. ❌ Julia set `pow(negative_fi, fractional)` = NaN, propaga como
   medialunas visibles. Clamp `frac` a [0,1] antes de pow.
6. ❌ FBM ruido / Voronoi bokeh dots llamados "fractales". Fractales =
   auto-similaridad real (Julia / Mandelbrot).
7. ❌ "Casi pasa la rúbrica" no pasa. Caveat = falla.

### 2.10 Reglas operativas

- **Stills first**: 3-6 stills 4K antes de comprometer 50min de render
- **Contact-sheet QA del MP4 final**: 15+ frames distribuidos antes de
  pasar path al user
- **No reducir intensidad de la sombra principal** (user lo pidió). Si hay
  que reducir overlay, reducir s2 (atmospheric) o sus contribuciones
  laterales

---

## 3. Recursion — AI generativo

### 3.1 Concepto

3 minutos de cierre del EP. Estética generada por modelo AI (mezcla Veo 3
generativo + post-process Hydra de referencia para timing y palette).

> Estado: el video original (`out/3-recursion.mp4`) ES la pieza válida.
> No se re-renderizó como Outbound y Crossing porque el approach AI
> generó algo que el user aprobó al primer intento.

### 3.2 Por qué AI funcionó acá y no en otros tracks

- **Track corto** (3 min) → menos costo computacional / iteraciones
- **Estética "delirio recursivo"** matchea bien con la naturaleza
  estocástica de los modelos generativos de video
- **Sin elementos figurativos claros** (no hay "el personaje" o "el túnel"
  específicos a defender) → más libertad para el modelo

### 3.3 Pipeline AI

```
audio master + prompt + reference frames
    ↓ Veo 3 (o LTX-Video / SkyReels — ver doc 09_ai_video_models_2026.md)
    ↓ output frames @ 24-30 fps
    ↓ ffmpeg compose + audio mux
    ↓ final mp4
```

> El doc `transmissions/01/video/experiments/ai_video_gemini/PROMPT_FOR_GEMINI.md`
> tiene el prompt template y las specs de los 3 modelos que estaban en
> exploración (LTX-Video, SkyReels, Mochi 1).

### 3.4 Cuándo usar AI vs raymarched

| Caso | Approach |
|---|---|
| Estética definida con elementos claros (personaje, escena específica) | Raymarched (control absoluto, audio reactive preciso) |
| Estética "delirio / abstract / generativa" | AI generativo (más natural, menos rigidez) |
| Audio reactividad fine-grained | Raymarched (events discretos sincronizados) |
| Coherencia visual a lo largo de varios minutos | AI tiene problemas, raymarched es estable |
| Tiempo de iteración | AI 1-2 hs / iteración, raymarched 30-60 min |

### 3.5 Antipatterns AI

1. ❌ Pedirle al modelo "audio reactive" — los modelos no entienden música
   con la precisión que un sync raymarched permite
2. ❌ Pedirle "13 minutos consistentes" — los modelos drift después de
   ~10 segundos
3. ❌ Pedirle "verde anegrado exacto #1a3a1a" — generan paletas
   aproximadas, no exactas

---

## 4. Cómo promover los experiments a "posta"

Cuando los videos del lab pasen aprobación final:

### 4.1 Promover Outbound

```bash
# Copia el final mp4 del lab a out/
cp transmissions/01/video/experiments/outbound_3d_rerender/final_4k.mp4 \
   transmissions/01/video/out/1-outbound_v2.mp4

# El original queda en out/1-outbound.mp4 como backup
# El nuevo queda como out/1-outbound_v2.mp4 hasta confirmar
```

Después de validar reproducción + integración con el player:
```bash
mv transmissions/01/video/out/1-outbound.mp4 \
   transmissions/01/video/out/1-outbound_hydra_original.mp4
mv transmissions/01/video/out/1-outbound_v2.mp4 \
   transmissions/01/video/out/1-outbound.mp4
```

### 4.2 Promover Crossing

Mismo patrón:
```bash
cp transmissions/01/video/experiments/python_v3/crossing_turrell_v3/final_4k.mp4 \
   transmissions/01/video/out/2-crossing_v2.mp4
```

### 4.3 Final assembly del EP

Una vez los 3 videos individuales están en `out/`, ensamblar con
crossfades vía `ffmpeg xfade` (igual que el audio EP en
`transmissions/01/release/distribution/`).

### 4.4 Promote checklist

- [ ] Mp4 final del lab pasa contact-sheet QA (15+ frames sin issues)
- [ ] Reproduce sin glitches en VLC + QuickTime + browser
- [ ] Audio sync perfecta (offset 0 después del fade in)
- [ ] Fps consistente (no frame drops)
- [ ] Bitrate adecuado (~3-6 Mbps a 4K)
- [ ] Tamaño razonable (<1 GB por track)
- [ ] Backups de versiones previas guardados

---

## 5. Stack técnico común

Todo el pipeline corre en:
- **Python 3.10** (venv compartido en `01_heliopause/.venv`)
- **moderngl 5.12** + **GLSL 330 core**
- **numpy 2.x**, **Pillow 12**, **soundfile**
- **ffmpeg 7.x** con `libx264`, `libfdk_aac` (vía homebrew aac), `yuv420p10le`
- **Apple M3 Max** (Metal-via-OpenGL) — limita a OpenGL 4.1 (sin compute shaders)

### 5.1 Workflow obligatorio

```bash
# 1. Editar render.py
# 2. Pretest (stills + small contact sheet)
.venv/bin/python render.py --pretest

# 3. Si pasa rúbrica visual, launch full
nohup nice -n 10 ./.venv/bin/python render.py > render.log 2>&1 & disown

# 4. Cuando termine, QA contact sheet del MP4 real
ffmpeg -ss <t> -i final_4k.mp4 -frames:v 1 frame.png
# ... 15+ veces a distintos t

# 5. Solo si TODOS pasan, comunicar path al user
```

### 5.2 Reglas de proceso (lessons aprendidas duro)

1. **Stills before motion**: no comprometer 50min de render sin validar
   dirección en stills 4K
2. **Contact-sheet QA del MP4 final**: 15+ frames distribuidos
3. **NO confiar en self-report del sub-agente**: el agente puede decir
   "OK" y entregar algo con bugs. Verificar abriendo el archivo yo mismo.
4. **NaN en GLSL**: `pow(neg, fractional)` = NaN. `0 * NaN = NaN`,
   propaga. Clamp antes de pow.
5. **Pipeline 16-bit obligatorio** para gradientes lentos a baja chroma.
6. **Smoothstep tiene inflexiones perceptibles** en gradientes lentos.
   Para Turrell-style usar Gaussian exp(-r²/σ²).
7. **El user lee con calidad cinematográfica**: lo que parece
   "casi imperceptible" en pretest se ve en su monitor calibrado.
8. **Audio reactivity discrete events > continuous smoothed**: para
   sync preciso a momentos musicales.
9. **Pipeline 16-bit shader-side NO salva al delivery format SDR**:
   YouTube tira 10-bit upload a 8-bit yuv420p re-encode → banding en
   gradientes lentos dark. Para preservar 10-bit, encodear HDR HLG.
10. **Paleta verde anegrado crashea en TVs/mobile**: TV UHD modo "vivid"
    crusha bajo ~10/255. Aplicar `pow(0.82)` gamma lift en finalize del
    shader → preserva carácter dark pero sale del threshold de crush.

### 5.3 Distribution encoding — universal compatibility

Para que el video se vea bien en iPhone HDR / 4K HDR TV / Mac Retina /
SD TV / mobile no-HDR, hay un capítulo separado dedicado:

→ [`21_distribution_encoding.md`](21_distribution_encoding.md)

Cubre:
- Por qué los uploads SDR YouTube tienen banding (zurcos)
- Palette lift `pow(0.82)` para evitar TV crush
- Encoding HDR HLG (HEVC main10 + BT.2020) con comando ffmpeg exacto
- Dual versions (master + YouTube trim 0.75s)
- Checklist obligatorio antes de upload
- Por qué HLG y no PQ / Dolby Vision

**Obligatorio leer** antes de publicar cualquier video nuevo.

---

## 6. Próxima fase — qué sigue

Una vez Outbound + Crossing aprobados y promovidos:

1. **Final EP assembly** con xfades entre tracks (igual que el audio EP)
2. **Distribution prep** (1080p / 4K versions per platform)
3. **Site embed** (`site/spiralout/aem/`)
4. **Thumbnail / banner art** para release pages
5. **Trailer / teaser** de 30-60 seg combinando momentos clave

Después de eso → otras transmissions (`02/`, `03/`, ...).

---

## Apéndice — Referencias relevantes en el repo

| Path | Qué tiene |
|---|---|
| `transmissions/01/video/CONTEXT_VIDEO_PROJECT.md` | Bitácora de versiones |
| `transmissions/01/video/_archive/hydra/SCENES.md` | Storyboard del original Hydra (timing reference) |
| `docs/video/00_PLAN_status.md` | Plan creativo del proyecto video |
| `docs/video/13_crossing_storyboard.md` | Storyboard creativo de Crossing |
| `docs/video/14_transition_techniques.md` | Cataloga técnicas de transición |
| `docs/video/QA_pro_rubric.md` | Rúbrica de calidad PRO |
| `docs/video/PRO_vs_amateur.md` | Anti-patterns vs patterns validados |
| `.claude/skills/qa-turrell/SKILL.md` | Skill para QA de piezas Turrell-ish |
| `framework/aem/` | Framework de composición audio |
