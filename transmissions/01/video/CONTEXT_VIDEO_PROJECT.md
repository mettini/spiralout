# Contexto videos Heliopause — estado y direcciones

Doc para preservar contexto si se pierde la conversación. Actualizar
cuando algo cambie.

---

## Crossing v3 — evolución

Carpeta: `transmissions/01/video/experiments/python_v3/crossing_turrell_v3/`

| Versión | Estado | Cambio principal | Backup |
|---|---|---|---|
| v3.2 | rejected | sombra ovalada simple | `final_4k_v3.2_backup.mp4` |
| v3.3 | rejected | smoothie sin phases | `final_4k_v3.3_backup.mp4` |
| v3.4 | rejected | TODO muy oscuro, fractales no visibles | (sobrescrito) |
| v3.5 | rejected | nebula visible sin julia | `final_4k_v3.5_backup.mp4` |
| v3.6 | rejected | FBM ruido (no fractales) | `final_4k_v3.6_backup.mp4` |
| v3.7 | rejected | Voronoi dots (bokeh, no fractales) | `final_4k_v3.7_backup.mp4` |
| v3.8 | rejected | Julia set + bug NaN → medialunas | `final_4k_v3.8_backup.mp4` |
| v3.9 | rejected | Julia OK pero smoothstep inflections "layers" | `final_4k_v3.9_backup.mp4` |
| v3.10 | rejected | Gaussian falloff pero aún 8-bit banding "ondas" | `final_4k_v3.10_backup.mp4` |
| v3.11 | rejected | dither TPDF 1/255 insuficiente | `final_4k_v3.11_backup.mp4` |
| v3.12 | rejected | 16-bit pipeline pero gaussianas overlapping aún "ondas" | `final_4k_v3.12_backup.mp4` |
| **v3.13** | **EN RENDER** | Dither subido a ±4/255 para enmascarar gradientes | — |

### Elementos del crossing v3 (estado actual)

- **Paleta**: verde anegrado intermedio (R: 0.04-0.07, G: 0.08-0.15, B: 0.05-0.08)
- **Background phases**:
  - 0:00-2:00 liso
  - 2:30-4:00 nebula (humo FBM 4.5x advectado rápido)
  - 4:30-6:30 fractales (Julia set evolutivo, c se mueve por círculo)
  - 6:30-8:30 vuelta a liso
  - 8:30-13:00 liso fijo (sin texturas, no se vuelve loco con la luz)
- **Silueta**: body (ellipse vertical, R=0.20, falloff=0.50, ecc=0.70) + head (R=0.085, offset -0.22). Gaussian falloff.
- **Sombra opacity**: 0.40 → 0.62 (pico peludo 4:30) → 0.20 fin
- **Pinchudo border**: FBM distortion amp 0.055 * peludo (rms_low > 0.2). Jitter freq 2-8 Hz.
- **Bells light** (10:30-12:10): upper-left, R=0.50, falloff=1.6, peak 0.18, tint verde-amarillento (#a6d65f-ish)
- **Voyager light** (0:16 ±5s Gaussian): upper-right, peak 0.10, sutil
- **End fade**: últimos 30s sombra → 0 (entre 12:30 y 13:00)
- **Fade in**: 0:00-0:03 desde negro absoluto. **Fade out**: 12:45-13:00 a negro absoluto.
- **Pipeline 16-bit**: float32 framebuffer → uint16 rgb48le → ffmpeg h264 high10 yuv420p10le CRF 17

### Issues conocidos

- Las "ondas/rayas" que el user reporta en zonas oscuras (1:30, 8:15, fin) son
  interferencia perceptual de Gaussianas overlapping (silueta + s2 + voyager + vignette).
  Dither al 1/255 no alcanza para enmascarar. v3.13 sube a 4/255.

### Reglas de proceso (lecciones aprendidas)

1. NO bajar intensidad de la sombra (user lo pidió explícito)
2. Verde más oscuro pero leíble (NI smoothie NI apagón)
3. Fractales = AUTO-SIMILARES REALES (Julia/Mandelbrot), no FBM ni Voronoi
4. Contact-sheet QA de 15+ frames del MP4 final ANTES de pasar path
5. Si el agente reporta "OK", abrir el archivo yo mismo y verificar antes de entregar
6. Pipeline 16-bit obligatorio para gradientes lentos a baja chroma

---

## Outbound — evolución

| Camino | Estado | Comentario |
|---|---|---|
| `outbound_v2_rebuild/` | abandonado | shaders flat-shader sin motion real, después con motion pero hatía bugs |
| `outbound_enhance/` | abandonado | post-pro del original, "es el mismo video con filtros" |
| `outbound_3d_rerender/` | **EN ITERACIÓN** | 3D raymarched, 6 escenas, **user aprobó dirección** |

### Outbound 3D — versión iteración actual (en sub-agente)

**User dijo**: "Las búsquedas que estás haciendo son interesantes y puede reemplazar al original"

#### 7 fixes específicos (en render por sub-agente):

1. **Ovulo (0:00-1:10)**:
   - NO late de entrada
   - 0:18 (beeps voyager / rms_air spikes): destello pequeño en core
   - 0:27 (heart pulse / rms_sub peaks): late SUTIL, mitad de amplitud actual

2. **Transición ovulo→tunel (1:08-1:20)**:
   - NO fade plano
   - Cámara se mete DENTRO del ovulo, agrandando agujero negro central
   - Z animation: from t=68s to t=80s, camera approaches iris sphere
   - El "túnel" es entrar al pupilo oscuro

3. **Túnel core (1:20-3:20)**:
   - Core titila MÁS LENTO sincronizado con voyager motif (no random)
   - Usar `flux` o `rms_low` smoothed long-window como proxy del motif
   - Hue shift ±0.05 + intensity ±0.20 con ritmo motif

4. **Túnel→humo (3:20)**:
   - Fade actual OK, MANTENER

5. **Humo timing**:
   - Solo 3:20-4:20 (no hasta 4:50)
   - 4:20-4:50: MANDALA FLOR que se abre con luz + color shift (bridge)

6. **Mandala portal dimensional (4:50-6:20)** — el cambio más grande:
   - Cámara se sumerge DENTRO del mandala (sin fade)
   - 4:50-5:10: aproximación, pétalos crecen
   - 5:10-5:30: túnel de patrones fractales
   - 5:30-6:20: HABITÁCULO INMENSO con paredes 3D raymarched fractales
     (Menger Sponge / Mandelbox / KIFS / Apollonian — distinto a crossing)
   - Ref: shadertoy mandelbox / KIFS, Tool "Parabol/Parabola" vibe pero no copiar concepto
   - Sacred geometry temple feel

7. **Final 6:21+**:
   - Mantener look actual
   - Transición: humo invade desde bordes del chamber, llena la pantalla,
     y por 6:21 estás en el final drift

### Outbound scenes plan (8:00 total, 14400 frames @ 30fps)

| Tramo | Contenido | Notas |
|---|---|---|
| 0:00-1:10 | NACER (ovulo) | no late, destello en beeps, sutil pulse |
| 1:10-1:20 | transición into iris | camera dive into pupil |
| 1:20-3:20 | TÚNEL | core synced voyager motif |
| 3:20-4:20 | HUMO claro (acortado) | con luz, no oscuro |
| 4:20-4:50 | mandala flor abriendo | bridge a portal |
| 4:50-5:10 | dive into mandala | approach + petal growth |
| 5:10-5:30 | tunel fractal | between |
| 5:30-6:20 | CHAMBER fractal | habitáculo inmenso, paredes mandala 3D |
| 6:20-7:30 | AFUERA con humo invade | transición + drift |
| 7:30-8:00 | PARTIDA | espiral final |

### Outbound — render técnico

- 4K @ 30fps (3840×2160)
- moderngl + GLSL raymarched scenes
- Audio reactivity per scene
- h264 high10 yuv420p10le CRF 17, AAC 192k mux
- Source audio: `transmissions/01/release/masters/01_outbound_master.wav`

---

## Skill qa-turrell

Skill creado en `.claude/skills/qa-turrell/SKILL.md`. Rúbrica de 7 preguntas
para validar si una pieza ES Turrell o no. Codifica 9 antipatrones del
proyecto (sombras no-Turrell, eventos forzados, dither IGN, QA con 3 frames,
sub-agente self-report sin verificación, etc).

NOTA: el crossing actual NO es Turrell puro — es "dark ambient field con
silueta cuerpo+cabeza + Julia fractal + bells light". Mantener nombre v3
("crossing_turrell_v3") es histórico, no curatorial.

---

## Paths actuales (último estado)

```
# Crossing v3.13 (en render, dither 4/255)
/Users/emilianomettini/git/spiralout/transmissions/01/video/experiments/python_v3/crossing_turrell_v3/final_4k.mp4

# Outbound 3D iteración (en render por sub-agente)
/Users/emilianomettini/git/spiralout/transmissions/01/video/experiments/outbound_3d_rerender/final_4k.mp4

# Original outbound (intocable, referencia de timing)
/Users/emilianomettini/git/spiralout/transmissions/01/video/out/1-outbound.mp4

# Original crossing (intocable, referencia)
/Users/emilianomettini/git/spiralout/transmissions/01/video/out/2-crossing.mp4
```

## Audio masters

```
/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/01_outbound_master.wav  (8:00)
/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/02_crossing_master.wav  (13:00)
/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/03_recursion_master.wav (3:00)
```

## Audio control tracks (analyze.py output)

```
/Users/emilianomettini/git/spiralout/transmissions/01/video/control/outbound.npz
/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz
/Users/emilianomettini/git/spiralout/transmissions/01/video/control/recursion.npz
```

Cada uno con: rms, rms_sub, rms_low, rms_air, centroid, flux, onset (@ 30fps).

---

## Recursion (pendiente)

NO empezado. 3:00 minutos. Track del cierre del EP. Track #3. Cuando
crossing y outbound estén aceptados, encarar.

---

## Lecciones meta del proceso

- **Stills before motion**: validar dirección con stills 4K antes de comprometer 50+ min de render.
- **Contact-sheet QA del MP4 final**: extraer 15+ frames distribuidos y revisar TODOS antes de pasar path al user.
- **No confiar en self-report del sub-agente**: el agente puede decir "OK" y entregar algo con bugs. Verificar antes de pasar.
- **Sub-agente para refactors/renders aislados**: bueno. Para iteraciones rápidas con user feedback continuo: main thread.
- **NaN en GLSL**: `pow(negative, fractional)` = NaN, `0 * NaN = NaN`, propaga. Clamp valores antes de pow.
- **Banding 8-bit en gradientes lentos**: solo se elimina con pipeline 16-bit (float framebuffer → uint16 → 10-bit encode) + dither de amplitud suficiente (≥4/255).
- **Smoothstep tiene inflexiones perceptibles** en gradientes lentos. Para Turrell-style usar Gaussian (exp(-r²/σ²)) — C∞ smooth.
- **El user lee con calidad cinematográfica**: lo que parece "casi imperceptible" en pretest se ve cuando lo proyecta en su monitor calibrado.
