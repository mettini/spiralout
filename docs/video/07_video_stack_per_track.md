# Capa video — stack final por track (Transmission 01)

> **Para qué es este doc:** dejar registrado **qué herramienta** rinde cada
> track del álbum, **qué modelo/sistema** usa, **cómo lo configuramos** y
> **qué técnicas** aplica — de manera que la próxima transmisión pueda partir
> de acá sin "vibe coding". Última actualización: 2026-05-23.

---

## Resumen ejecutivo

| Track | Duración | Herramienta | Archivo fuente | Salida |
|-------|----------|-------------|----------------|--------|
| **1 · Outbound** | 8:00 | Python + shader GLSL (preset `outbound`) | `transmissions/01/video/render.py` + `shaders/accumulate.frag` + `shaders/post.frag` | `out/1-outbound.mp4` |
| **2 · Crossing** | 13:00 | Hydra (live-coding) headless | `transmissions/01/video/hydra/crossing_delirio.js` | `out/2-crossing.mp4` |
| **3 · Recursion** | 3:00 | AI local (SDXL-Turbo / MPS) + post-process | `transmissions/01/video/ai/local_render_diffusers.py` → `recursion_ai_v2_full.mp4` → ffmpeg vignette+fade | `out/3-recursion.mp4` |

Decisión: **3 videos separados** (no master continuo de 24 min). Cada track se
publica en su clip; el seam Hexagrama 24 (Recursion → Outbound) es decisión de
player, no de render.

---

## Contrato común: el control track (NumPy)

**Todos los pipelines leen el mismo `control track`** generado por
`analyze.py`. Esto es lo que hace que el audio "comande" la imagen y no que la
imagen "ilustre" el audio.

```
master.wav --analyze.py--> control/<track>.npz {rms, rms_sub, rms_low,
                                                 rms_air, centroid, flux,
                                                 onset, fps}
```

| Canal | Rango Hz | Significado en imagen |
|-------|----------|------------------------|
| `rms` | full band | energía global → contraste, brillo base |
| `rms_sub` | 30–55 | latido → iris/pupila, fuga del túnel |
| `rms_low` | 55–250 | masa → densidad de humo/nébula |
| `rms_air` | 4 000–10 000 | polvo, grano, partículas |
| `centroid` | — | deriva de tinte (hue) |
| `flux` | — | turbulencia, glitch |
| `onset` | 0/1 | disparos puntuales (relámpagos, bells) |

Los tres stacks consumen el mismo `.npz`. En Hydra se traduce a JSON
(`hydra/_headless/control_*.json`) y se inyecta como `a.fft[0..3]` mockeado.

**Reglas de mapeo:**
- Siempre vía **envelope follower** (ataque rápido, release lento) para que el
  movimiento sea musical, no nervioso.
- Las bandas mapean a SUB / LOW / MID / HIGH (4 bins en Hydra) para mantener
  la convención del proyecto (`docs/video/02 §4`).

---

## Track 1 · Outbound — Python + shader (GLSL)

### Por qué este stack

- **Reproducible al 100%**: el render es determinista (mismo `compose` + mismo
  `control.npz` ⇒ mismo `.mp4`).
- **8 minutos de delirio + túnel + mandala**: necesitábamos algo que
  respondiera al audio frame a frame, sin frágilidad de modelo AI.
- **Tunable**: cada parámetro está expuesto como uniform → se itera en
  minutos, no en horas (vs AI).

### Modelos / sistemas

Ninguno externo. Stack 100% código local:

| Pieza | Versión | Rol |
|-------|---------|-----|
| Python | 3.10+ | orquestador |
| moderngl | 5.x | OpenGL 4.1 headless (Apple M3 ok) |
| numpy / scipy | 2.x / 1.x | análisis del WAV + envelope follow |
| soundfile | 0.12+ | carga WAV |
| ffmpeg | 7.1+ | encode H.264 + mux WAV |

No usa librosa (es numpy/scipy puro — `docs/video/00_PLAN_status §4`).
No usa compute shaders (macOS topa en GL 4.1 — usa ping-pong de texturas).

### Configuración

Comando exacto del render final:

```bash
python3.10 transmissions/01/video/render.py \
  --control transmissions/01/video/control/outbound.npz \
  --wav     transmissions/01/release/masters/01_outbound_master.wav \
  --out     transmissions/01/video/out/1-outbound.mp4 \
  --preset  outbound \
  --w 1280 --h 720 --seconds 480 --crf 20
```

Flags clave:
- `--preset outbound` → mapper específico (`map_outbound` en `render.py`)
  que define cómo el audio modula cada uniform.
- `--w 1280 --h 720` → master en 720p (el grano full-frame infla H.264; 4K
  no aporta perceptiblemente en esta estética).
- `--crf 20` → calidad alta.

### Técnicas (shader)

El shader vive en dos pases (`shaders/accumulate.frag` + `shaders/post.frag`).
Lo que hace cada pase:

**Pase 1 — `accumulate.frag` (feedback buffer + contenido nuevo):**

```
frame_N = warp(frame_{N-1}) * decay + contenido_nuevo
```

El **warp** (zoom + rotación) es la espiral/recursión. Los uniforms que
manejamos:

| Uniform | Origen audio | Qué hace |
|---------|--------------|----------|
| `u_decay` | `rms` + storyboard | cuánto sobrevive el frame anterior (0–0.94) |
| `u_spiralZoom` | `rms_sub` + storyboard | zoom radial = fuga al infinito |
| `u_spiralRot` | `rms_low` + storyboard | rotación = espiral |
| `u_pulse` | `rms_sub` | glow central |
| `u_retina` | `rms` + iris dilation | pupila + fibras radiales |
| `u_smoke` | `rms_low` | fbm con domain warping |
| `u_tunnel` | `rms` | anillos polares fugando |
| `u_dust` | `rms_air` | specks que derivan |
| `u_kaleidN` | storyboard | número de segmentos del mandala (entero) |
| `u_glitch` | `flux` + storyboard | desplazamiento horizontal por línea |
| `u_dropout` | `onset` | banda oscura tipo salto de púa |
| `u_collapse` | tail-window | cierre al centro (reabsorción) |
| `u_inject` / `u_palette` | storyboard `color` | blend monocromo ↔ color sucio |

**Director (storyboard) — `SCENES_OUTBOUND`:**

Para que un tema de 8 min no sea siempre la misma diana, definimos un
storyboard de macro-parámetros que varía con `t ∈ [0,1]` (posición en el
tema). Cada parámetro es una lista de keyframes `[(t0, v0), (t1, v1), ...]`
que se interpola linealmente. Fases del outbound:

```
nacer 0-0.12  →  despegue/túnel 0.12-0.30
→  mandala+color 0.30-0.70 (la "lava" amarilla/verde)
→  seguir hacia afuera 0.70-1.0
```

**Pase 2 — `post.frag` (grade):**

Aplica grain, scanlines, vignette, chroma aberration y mezcla
`u_palette` (verde fósforo ↔ color sucio HSV). El hue **no usa `ang`
directo** (ese saltaba en ±π creando una franja rosa visible — bug
detectado y corregido el 2026-05-23). Se usa `cos(ang)` que es continuo.

**Lecciones del bug 2026-05-23:**

1. Cualquier uso de `atan(c.y, c.x)` para color debe ser **continuo en ±π**
   (usar `cos(ang)` o `sin(ang/2)`, no `ang*k`).
2. El kaleidoscopio (`u_kaleidN`) debe usar **valores enteros** —
   interpolación lineal entre 5 y 9 produce N=6.7 cuyo fold no tila y deja
   costura visible. Se cuantiza con `floor(N + 0.5)`.
3. Rotar la fase del kaleidoscopio con `u_time * 0.13` para que las
   costuras restantes deriven y se promedien en el feedback.

---

## Track 2 · Crossing — Hydra (live-coding) headless

### Por qué este stack

- **Crossing es 13 min**: necesita textura orgánica que evolucione sin
  costuras, donde **no se vean formas claras** y el espectador esté
  desorientado. Hydra (feedback chain + domain warping con noise) es
  exactamente eso.
- **Sin scroll/scrollY**: rechazado en iteraciones previas porque el wrap de
  textura dejaba **costura horizontal** (2:16 / 5:50 — `crossing_delirio.js`
  línea 410). El movimiento se hace con `modulate(noise)` y
  `modulate(src(o0))`.
- **Headless reproducible**: Hydra normalmente corre en browser. Nuestro
  harness `hydra/_headless/render.mjs` lo corre en Node + `headless-gl` y
  pipea pixels crudos a ffmpeg. Cero browser, cero clicks.

### Modelos / sistemas

| Pieza | Versión | Rol |
|-------|---------|-----|
| Node.js | 20+ | runtime del headless |
| `hydra-synth` (npm) | latest | el motor de Hydra |
| `gl` (npm, headless-gl) | latest | contexto WebGL off-screen |
| ffmpeg | 7.1+ | encode H.264 + mux WAV |

El control track Python (`control/crossing.npz`) se convierte a JSON
(`control_crossing.json`) y se inyecta como `a.fft[0..3]` mockeado dentro del
shim de `render.mjs` (Hydra normalmente toma FFT del micrófono; acá la
"vemos" inyectada del audio del master).

### Configuración

Comando exacto:

```bash
cd transmissions/01/video/hydra/_headless && \
HYDRA_PATCH=../crossing_delirio.js \
HYDRA_WAV=../../release/masters/02_crossing_master.wav \
HYDRA_CONTROL=control_crossing.json \
HYDRA_OUT=../../out/2-crossing.mp4 \
node render.mjs 780
```

`780` = duración en segundos (13:00). El `render.mjs` corre `synth.time` a
1/FPS por frame (no usa wall-clock) — sincronización perfecta con el WAV.

### Técnicas (patch Hydra)

El patch (`crossing_delirio.js`) define **7 escenas** que crossfade-ean con
ventanas `win(t0, t1)` solapadas. Cada escena es una cadena de operadores
Hydra construida por composición.

**Timeline (rebalanceada 2026-05-23):**

| # | Escena | t (s) | Qué se ve | Concepto |
|---|--------|-------|-----------|----------|
| 1 | CAOS | 0–140 | polvo en la cara | noise alta freq + modulate(src(o0)) → estelas radiales |
| 2 | DESORIENTACIÓN | 110–240 | "se pudre la momia" | `modulateRotate(src(o0))` + dos rotate de signo opuesto + `modulateScale` |
| 3 | INVERSIÓN (LAVA) | 200–510 | giro invertido + color | `spin()` cruza HALF (4:50) → órbita se parte. Window ancho (5 min) para cubrir el medio del tema y evitar agujero negro post-lava |
| 4 | RELÁMPAGOS | 480–560 | flash difuso (fogonazo como base) | fogonazo como capa primaria + `src(o0)` add-on — antes el escenario inverso drenaba el buffer |
| 5 | RAYAS | 480–600 | ondulación horizontal | osc rotado 90° + soft amplio (sin filo) — overlap con relámpagos para garantizar contenido fresco no-feedback |
| 6 | STARGATE | 580–720 | túnel slit-scan | `scale(>1)` fuerte + colorama + invert parcial |
| 7 | SALIDA | 700–780 | enrosque a Recursion | espiral semilla + Droste suave |

**Reglas anti-bug aplicadas (lecciones del pasado):**

- **No `scroll`/`scrollY`**: dejaban costura horizontal por wrap.
- **No reusar el mismo nodo**: hydra aliasea → sale negro. Cada `src(o0)`,
  cada `noise()` es un nodo NUEVO.
- **No `voronoi+thresh`** o `shape+thresh`: bordes recortados — rechazados.
- **`soft()` siempre**: helper que aplica domain warp pequeño con noise → los
  bordes "tiemblan" y se difuminan. Es nuestro blur improvisado (Hydra no
  tiene `.blur()` nativo).
- **Sin `invert` sobre el feedback**: explota en arcoíris neón. Solo sobre
  capas frescas.
- **Saturación baja (0.6–0.8)**: el smear acumula color → si saturás alto,
  sale neón. Crossing es mineral/sucio.

**Disorientación en Hydra — técnicas catalogadas:**

| Técnica | Efecto |
|---------|--------|
| `modulateRotate(src(o0), k)` | cada píxel rota según el feedback → sin eje estable |
| `modulateScale(src(o0), k)` | fractal Droste descontrolado → no hay escala anclada |
| Dos `rotate` apilados con signos opuestos | conflicto de giro |
| Cadena de `modulate(noise(...))` a 3 escalas distintas | vectores contradictorios |
| `scale(1.05+)` continuo con feedback | sensación de fuga radial |
| `noise(40+, fast)` | partículas de polvo en la cara |

---

## Track 3 · Recursion — AI local (SDXL-Turbo / MPS) + post

### Por qué este stack

- **Recursion es 3 min**: corto, abstracto, "la vuelta" — el AI local
  produce un look pictórico/orgánico difícil de imitar con shader.
- **100% local**: corre en Mac M3 con MPS (`Metal Performance Shaders`).
  Cero Colab, cero cuenta paga, cero API key.
- **Repetible**: seeds versionadas, prompts versionados, settings versionados.

### Modelos / sistemas

| Pieza | Versión | Rol |
|-------|---------|-----|
| Python | 3.10+ | orquestador |
| diffusers (HuggingFace) | latest | pipeline AI |
| torch + MPS backend | 2.x | inferencia en Apple Silicon |
| **modelo principal** | `stabilityai/sdxl-turbo` | text2img + img2img rápido |
| **fallback** | `runwayml/stable-diffusion-v1-5` | si Turbo no carga |
| ffmpeg | 7.1+ | encode + post-process |

Performance observado en M3 Max: **~1.3 s/frame** a 768×432 → 180 s × 12 fps =
2160 frames × 1.3 s ≈ **45 min de render**.

### Configuración

Comando del render base (el que produjo `recursion_ai_v2_full.mp4`):

```bash
python3.10 transmissions/01/video/ai/local_render_diffusers.py \
  --secs 180 --fps 12 --w 768 --h 432 \
  --reinject 24 --reinject-mix 0.35 \
  --strength 0.58 --noise 0.04 --zoom-max 0.02
```

Flags clave (toda la receta vive en `local_render_diffusers.py`):

| Flag | Default | Función |
|------|---------|---------|
| `--secs` | 30 | duración del clip |
| `--fps` | 12 | bajo: el AI dirige el look "pictórico" |
| `--w / --h` | 768×432 | 16:9; default chico para iterar |
| `--strength` | 0.58 | img2img: cuánto se respeta el frame anterior vs el prompt |
| `--reinject` | 24 | cada N frames mezcla un txt2img FRESCO de la escena vigente |
| `--reinject-mix` | 0.35 | alpha del reinject (evita deriva a verde plano) |
| `--noise` | 0.04 | inyección de noise por warp → evita "lavado" del latente |
| `--zoom-max` | 0.02 | tope al zoom acumulado (evita saturación) |
| `--seed` | aleatorio + reseed por escena | semilla nueva por corte de scene-graph |

### Técnicas (AI dirigido por audio)

**Pipeline:**

```
control/recursion.npz  +  scenes_recursion_delirio.json  +  prompts_recursion_delirio.txt
                              │
                              ▼
              audio_to_keyframes.py  (mapea control track + scene-graph
                                       a un schedule de prompt/zoom/rot/strength)
                              │
                              ▼
                 local_render_diffusers.py (img2img frame-a-frame + reinject)
                              │
                              ▼
                     ffmpeg (encode H.264 + mux WAV)
```

**Decisiones de receta (del comentario v2 del script):**

1. **Deriva a verde plano** — img2img con strength bajo + Turbo guidance=0
   colapsa el latente. Soluciones aplicadas: strength más alto (0.58),
   **reseed por escena**, **re-inyección periódica de txt2img fresco**,
   noise injection + AGC suave.
2. **Aparición de persona** (~1:10 en v1) — negative prompt reforzado con
   figuras humanas/criaturas. Abstracto only.
3. **Cuadrado/baja calidad** — ahora 16:9 parametrizable.
4. **Movimiento calmo pero "pasan cosas"** — reseed + reinyección mutan
   escenas; zoom/rot bajos + ruido suave mantienen el flow lento.

### Post-process (fade-túnel)

`recursion_ai_v2_full.mp4` cortaba abrupto al final. Se agregó vignette
animado + fade-out con ffmpeg, sin re-renderizar el AI:

```bash
ffmpeg -y -i recursion_ai_v2_full.mp4 \
  -vf "vignette=angle='if(lt(t,170), PI/4, PI/4 - (PI/8)*(t-170)/10)':eval=frame, fade=t=out:st=176:d=4" \
  -af "afade=t=out:st=176:d=4" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -movflags +faststart \
  out/3-recursion.mp4
```

Efecto: a t=170 empieza a cerrar el vignette (de PI/4 a PI/8 en 10 s) → da
sensación de túnel; a t=176 inicia fade-to-black de 4 s → sugiere entrar al
agujero / volver al Spiral (Hexagrama 24).

---

## Cómo aplicar este stack a la próxima transmisión (TX=02+)

Decisión que hay que tomar **por track**: ¿shader determinista (control
total), Hydra orgánico (textura), o AI (look pictórico)? Criterios:

| Si el track es… | Preferí… |
|-----------------|----------|
| Estructurado, con secciones claras, motivos repetidos | **shader (Python+GLSL)** |
| Largo (8+ min), masa orgánica, sin formas claras | **Hydra** |
| Corto (≤4 min), abstracto, look pictórico/orgánico | **AI local** |
| Necesita anchor visual reproducible al 100% | **shader** |
| Iteración rápida en vivo, sin re-render | **Hydra** |

**Pasos genéricos:**

1. Renderizar master del track → `transmissions/NN/release/masters/<NN_track>.wav`.
2. Generar control track: `python3.10 transmissions/NN/video/analyze.py
   --wav <master.wav> --out control/<track>.npz --fps 30`.
3. Elegir herramienta (tabla arriba).
4. Si shader: crear `map_<track>` y `SCENES_<TRACK>` en `render.py`.
5. Si Hydra: clonar un patch existente (`<track>_delirio.js`), ajustar
   timeline + escenas.
6. Si AI: ajustar `prompts_<track>.txt`, `scenes_<track>.json`, los
   defaults de `local_render_diffusers.py`.
7. **Render corto de prueba primero** (30–60 s en resolución baja). Validar.
8. Render completo. Sample 5–6 frames a lo largo del clip para verificar
   que no hay regresiones (franjas, costuras, deriva a un color).
9. Cleanup `out/` y entrega como `N-<track>.mp4`.

---

## Anti-patrones (memoria del proyecto)

- **No usar `ang` directo en hue** (shader): salto en ±π → franja rosa visible.
- **No interpolar kaleidN** en valores no-enteros: fold no tila → costura.
- **No `scroll`/`scrollY`** en Hydra: wrap de textura → costura horizontal.
- **No reusar nodos** en Hydra: aliasea → sale negro.
- **No `voronoi+thresh`** o `shape+thresh` para "piedras": bordes recortados.
- **No `invert` sobre `src(o0)`** en Hydra: explota en arcoíris neón.
- **No img2img con strength bajo + guidance=0**: deriva a color plano.
- **No escenas de Hydra que dependan SOLO de `src(o0)` + audio onsets**: si la
  ventana es larga y los onsets son raros, el buffer se drena y queda negro.
  Siempre incluí un baseline (no audio-gated) en escenas largas.
- **No olvidar `task qa:spectral`** del audio antes de renderizar video sobre
  un master nuevo (el video se compromete con un máster aprobado, no con uno
  que vamos a remixear).
