# Capa Video — PLAN MAESTRO + ESTADO (resiliente a corte de contexto)

> **Para retomar si se cortó el contexto: LEÉ ESTE ARCHIVO PRIMERO.**
> Resume el objetivo, las decisiones tomadas, qué está construido, qué falta,
> y cómo seguir. Los detalles creativos/técnicos viven en los docs hermanos
> (`01`–`04`). Última actualización: 2026-05-21.

---

## 0 — Objetivo

Armar los videoclips de **Heliopause / Transmission 01** (3 temas, ~24 min:
Outbound 8:00 · Crossing 13:00 · Recursion 3:00). Arte generativo a partir de
las ondas sonoras: el audio maneja la imagen. Formato objetivo: **master
continuo + cortes por tema + loops cortos** (Spotify Canvas / IG).

Restricciones DURAS (del usuario):
- Nivel **PRO**, nada improvisado.
- **Solo herramientas GRATIS / open-source**. Cero suscripciones pagas
  (NO Kaiber, NO Neural Frames, NO Runway/Pika/Sora).
- Reproducible como el audio: scripts/shaders/patches se commitean, el
  `.mp4`/frames/control se gitignoran (regenerables).

---

## 1 — Flujo de trabajo acordado (ORDEN IMPORTANTE)

El usuario fue explícito sobre el orden (2026-05-21):

1. **FASE A — Explorar las HERRAMIENTAS** (estamos acá). Probar cada approach
   *con el concepto fósforo/telemetría* (concepto A) y ver cuál(es) sirve(n).
   No finalizar concepto todavía — validar la herramienta.
2. **FASE B — Elegir la/las herramienta(s) correcta(s).**
3. **FASE C — Explorar CONCEPTOS** con la herramienta elegida. Hay al menos
   **dos** conceptos sobre la mesa (ver §3): A (fósforo/telemetría) y
   **B (2001 Star Gate — flashero/sucio/críptico)**, que al usuario le llama
   mucho. Pueden convivir o elegirse uno.

> Regla operativa: no saltar a producción final hasta cerrar A→B→C. El
> prototipo actual es para **evaluar herramienta**, no es el clip final.

---

## 2 — Las 3 herramientas en evaluación

Research completo y dirección creativa por herramienta en docs separados:

| Approach | Doc | Quién lo corre | Estado exploración (Fase A — CERRADA 2026-05-21) |
|---|---|---|---|
| **Python + shader (GLSL)** — control track | `01_concept_python_shader.md` | Claude lo corre acá (Mac M3) | ✅ **ELEGIDA como columna vertebral.** Pipeline funcionando; `recursion_phosphor_v2.mp4` (3:00, 720p) con latido-retina + túnel + humo + colapso/loop. El usuario aprobó el look fósforo. |
| **Hydra** (video synth, browser) | `02_concept_hydra.md` | Usuario en browser | ✅ Patch runnable en `video/hydra/` (`recursion.js` + `stargate.js` + README). Ideal para textura/feedback de Recursion; NO para 24 min ni tipografía. Companion, no spine. |
| **AI open-source** (Deforum/ComfyUI/AnimateDiff, local) | `03_concept_ai_opensource.md` | Usuario con GPU/Colab | ✅ Receta runnable en `video/ai/` (`audio_to_keyframes.py` reusa el control track + settings Deforum + workflow ComfyUI). Veredicto: viable pero cara/frágil → usar como **restyle/acabado** sobre el init-video de shader (vid2vid), no como generador standalone. |

**Recomendación de herramienta (Fase B):** **Python+shader = columna vertebral**
(barata, controlable, produce mp4 terminado, encaja con el repo, y el
feedback-buffer ES el Hexagrama 24). **Hydra** = exploración/textura de Recursion.
**AI** = capa de acabado/restyle opcional sobre el shader. No son excluyentes.

**Convergencia de los 3 planes** (lo encontraron independientemente):
- Ancla conceptual: **Hexagrama 24 / Fù = El Retorno** (el último frame de
  Recursion re-inyecta el primero de Outbound → loop sin costura = Fù ejecutado).
- Disciplina anti-iconografía: sin Hubble/planetas/astronautas, sin espiral
  literal dibujada, sin barras de ecualizador.
- Tesis: el audio **no se ilustra**, comparte materia prima (se releen los
  mismos arrays NumPy que sintetizaron el track).

**Por qué Python+shader es la primera que probamos en vivo:** es la única que
Claude puede correr y entregar como `.mp4` terminado acá mismo, gratis, y
además sirve de *init video* para la ruta AI y comparte el feedback-loop con
Hydra. Es la columna vertebral; las otras dos se montan encima.

---

## 3 — Conceptos visuales (para FASE C)

### Concepto A — Fósforo / Telemetría (el que propuso Claude)
Verde fósforo `#a6d65f` sobre negro, CRT, grano, overlays VT323, monocromo.
Telemetría tipo NASA. Hereda `docs/13_visual_style_guide.md`. Detalle creativo
en `01_concept_python_shader.md` §1 y §4. **Es el concepto con el que se
exploran las herramientas en Fase A.**

### Concepto B — 2001 Star Gate / flashero (lo que pidió el usuario)
> Cita del usuario: *"otro con espacio, polvo y demás, pero medio críptico
> medio sucio, medio flashero, como el final de la peli 2001 odisea del
> espacio, esa exploración flashera o ese viaje en la nave"*.

Espacio, polvo, viaje psicodélico, sucio y críptico. Técnica madre: **slit-scan
/ stargate** (Douglas Trumbull, 1968) + tunnel de feedback con zoom fuerte.
Color sucio/desaturado (no neón limpio), aberración cromática, grano pesado.
Dirección creativa completa en **`04_concept_2001_stargate.md`**.

> Decisión pendiente (Fase C): A y B no son excluyentes — podrían mapear a
> distintos movimientos (p.ej. B = el cruce/viaje de *Crossing*; A = la
> telemetría de *Outbound*/*Recursion*). O elegir uno. **No decidido aún.**

---

## 4 — Estado técnico (qué está construido y validado)

**Entorno validado (2026-05-21):**
- `moderngl` instalado. Headless GL **funciona** en el Mac (OpenGL 4.10, Apple
  M3 Max) — `create_standalone_context()` + render a FBO + readback OK.
  → El riesgo #1 del plan (GL headless en macOS) está **descartado**.
- `ffmpeg 7.1.1` presente. `soundfile`, `numpy 2.2.6`, `scipy` presentes.
- **Sin librosa**: la extracción de features se hace en **numpy/scipy puro**
  (más alineado con la tesis "misma materia prima NumPy"; evita numba).
- macOS topa en OpenGL 4.1 → **sin compute shaders**. Se usa ping-pong de
  texturas / fragment passes (patrón estándar). NO usar `glDispatchCompute`.

**Masters de audio (input):** `transmissions/01/release/masters/`
- `03_recursion_master.wav` — 44100 Hz, estéreo, **180.0 s** (el del prototipo).
- `01_outbound_master.wav`, `02_crossing_master.wav`,
  `00_heliopause_continuous.wav`.

**Pipeline construido en `transmissions/01/video/`:**
```
analyze.py            Capa A — WAV → control.npz (numpy/scipy/soundfile)
render.py             Capa B+C — control + shaders → frames → ffmpeg → mp4
shaders/quad.vert     fullscreen triangle
shaders/accumulate.frag  feedback buffer + contenido nuevo (pulso/nébula/polvo/glitch)
shaders/post.frag     grade: phosphor mono | color sucio, grano, scanlines, vignette, chroma
control/              control.npz (GITIGNORED)
out/                  mp4 de prueba (GITIGNORED)
README.md             cómo correr
```
El engine es **un solo motor con presets**: mismo `accumulate.frag` + `post.frag`,
y `render.py --preset {phosphor_recursion|stargate}` cambia el mapeo
audio→uniforms y la paleta. Esto demuestra el rango de la herramienta (mismo
motor, dos conceptos A y B) — argumento fuerte para elegir Python+shader.

**Arquitectura control track (contrato entre capas):**
```
master.wav → analyze.py → control.npz {rms, rms_sub, rms_low, rms_air,
                                        centroid, flux, onset, fps}
control.npz → render.py (moderngl headless, ping-pong feedback) → frames RGB
frames RGB --stdin--> ffmpeg + master.wav → out/*.mp4
```

---

## 5 — Cómo correr (resumen; detalle en `transmissions/01/video/README.md`)

```bash
# 1. Analizar el WAV → control track
python3.10 transmissions/01/video/analyze.py \
  --wav transmissions/01/release/masters/03_recursion_master.wav \
  --out transmissions/01/video/control/recursion.npz --fps 30

# 2. Render (preset fósforo, prueba corta de 22s desde el seg 30)
python3.10 transmissions/01/video/render.py \
  --control transmissions/01/video/control/recursion.npz \
  --wav transmissions/01/release/masters/03_recursion_master.wav \
  --out transmissions/01/video/out/recursion_phosphor_test.mp4 \
  --preset phosphor_recursion --w 1280 --h 720 --start-sec 30 --seconds 22

# Concepto B (2001 stargate), mismo motor:
python3.10 transmissions/01/video/render.py ... --preset stargate ...
```

Dependencias: `python3.10 -m pip install moderngl` (numpy/scipy/soundfile/ffmpeg ya estaban).

---

## 6 — Próximos pasos (TODO, en orden)

- [x] **Fase A:** render Python+shader, preset fósforo + features (latido-retina, túnel, humo) → `recursion_phosphor_v2.mp4`. Aprobado por el usuario.
- [x] **Fase A:** preset stargate (concepto B) — sketch renderizado (`recursion_stargate_test.mp4`), pendiente afinar túnel.
- [x] **Fase A:** patch Hydra runnable entregado (`video/hydra/`).
- [x] **Fase A:** receta AI open-source runnable entregada (`video/ai/`); corre en el M3.
- [x] **Fase B:** herramienta elegida → **Python+shader spine + Hydra textura + AI restyle opcional.**
- [~] **Fase C EN CURSO** (2026-05-21):
  - Research místico → `docs/video/05_visual_research_references.md` (Belson, Whitney, Trumbull,
    cymatics/Chladni, Ikeda/Semiconductor + storyboard delirio de 8 escenas + hints por rama).
  - **Director/storyboard de 6 fases** implementado en `render.py` (`SCENES_PHOSPHOR`): nacer →
    humo → túnel → mandala (caleidoscopio) → vinilo → colapso. El feedback (`decay`) y el zoom
    radial varían POR FASE → rompe la "diana siempre igual". Rayas horizontales SOLO en fase vinilo.
    → `out/recursion_delirio_v3.mp4` (las fases ya se diferencian; queda anillo residual tenue).
  - **Hydra delirio** → `video/hydra/recursion_delirio.js` (7 escenas, crossfades por ventanas).
  - **AI delirio** → `video/ai/` (`--mode delirio`, 7 escenas atadas a valles de energía del audio).
  - **Color (stargate) en Recursion**: el director sube `color` (blend fósforo↔color sucio) en el
    pico del delirio (túnel+mandala) y vuelve al verde → `recursion_delirio_v4.mp4` (con) /
    `recursion_delirio_v5.mp4` (color + SIN rayas horizontales). v5 es el keeper actual.
  - **Rayas horizontales → Crossing** (decisión usuario): en Recursion `streak`=0. Las rayas son
    "lo picante" de Crossing.
  - **Outbound** (preset `outbound` + `SCENES_OUTBOUND`): nacer → TÚNEL → se pudre → viaje
    complicado con **relámpagos** (`u_lightning`, flash en onsets) y **piedras** (`u_rocks`,
    oclusión chunky). → `outbound_v1.mp4` (960x540). Nuevos elementos de shader: bolt + rockMask.
  - PENDIENTE: **Crossing** (13:00) — el viaje denso/picante, acá van las rayas horizontales +
    polvo de Saturno + tropezones. Aplicar Chladni/Whitney del research; matar anillo residual;
    afinar `stargate` (slit-scan real); master continuo + loop seam.
  - DECIDIR: A vs B vs combo por movimiento (Outbound y Recursion ya empezados).
- [ ] Presets para Outbound y Crossing; master continuo 24:00; loop seam Recursion↔Outbound.
- [ ] Encode más eficiente para entregables (el grano full-frame infla H.264; ~390 MB/3min @720p).
- [ ] Sumar tasks `video:*` al `Taskfile.yml`.
- [ ] (futuro) Bajar una **skill `creative-direction`-aplicada-a-video** o extender la existente.
- [ ] Actualizar `dashboard/data.json` con la capa video.

## 8 — BATCH NOCTURNO en curso (2026-05-21 noche) — para el reporte de mañana

El usuario pidió: reporte completo + en `out/` los mp4 de los 3 tracks con las 3
tecnologías + recomendación sobre mezclarlas o no. Estado de lo lanzado:

- **Python (lo hace Claude):** presets de los 3 tracks listos en `render.py`
  (`outbound` = delirio+túnel SIN rayas/relámpagos; `crossing` = picante: rayas +
  polvo + tropezones + relámpagos + color stargate + inversión a mitad;
  `phosphor_recursion` = v5). Renders en curso → `out/recursion_delirio_v5.mp4`,
  `out/outbound_v2.mp4`, `out/crossing_v1.mp4`. (Crossing 13min = render largo.)
- **Hydra:** agent rindiendo el patch a mp4 HEADLESS (frágil, puede fallar →
  fallback documentado). Otro agent creando `outbound_delirio.js` + `crossing_delirio.js`.
- **AI:** agent creando recetas de outbound + crossing. ⚠️ mp4 de AI probablemente
  NO se puede generar acá (necesita modelos SD + GPU + horas) — reportar como blocker.
- **Decisiones del usuario aplicadas:** rayas horizontales SOLO en Crossing;
  Outbound = túnel + delirio (sin viaje complicado, que es de Crossing); no abusar
  de relámpagos; color stargate florece en mandala.

Pendiente al despertar Claude: verificar frames de los renders, integrar resultados
de los 3 agents, y COMPILAR el reporte (acá + actualizar este doc) con tabla
3 tracks × 3 tecnologías (qué mp4 existe / qué quedó como receta) + recomendación
de mezcla.

## 9 — ESTADO AL 2026-05-22 (mixes por track + AI andando) — LEER

**Decisión de mezcla del usuario (por track):**
- **Outbound**: Python 0:00–5:48 → **transición agujero-negro** (el stargate de Python se lo
  come un agujero, colapsa a negro en 5:48 con el bombo) → **Hydra** emerge desde el negro →
  final a negro. NO corte seco. Implementado con `render.py --collapse-tail` + composite ffmpeg.
- **Crossing**: **Hydra** completo, reescrito ORGÁNICO/DIFUSO (base `noise`+domain-warp, sin
  `thresh/voronoi/shape/scroll`; sin costura ni líneas filosas). Verificado 2:16/5:50/510/760.
- **Recursion**: **Hydra** completo (ablandado). PENDIENTE decidir si queda Hydra puro o mezcla.

**Entregables (todos gitignored, en `transmissions/01/video/`):**
- `out/mix_outbound.mp4` (108M) · `out/mix_crossing.mp4` (225M) · `out/mix_recursion.mp4` (27M)
- `ai/out/recursion_ai_test.mp4` (1.4M) — prueba AI LOCAL que FUNCIONA (SDXL-Turbo/MPS,
  ~1.3s/frame, eclipse verde fósforo). Regenerar/alargar:
  `python3.10 ai/local_render_diffusers.py --secs 20 --fps 12`

**Pipelines/archivos clave (versionados):**
- Python: `transmissions/01/video/{analyze.py,render.py,shaders/}` — presets `phosphor_recursion`,
  `outbound`, `crossing`, `stargate`. Flag `--collapse-tail SEC` (colapso a negro en cola, para
  transiciones). Director por track = dicts `SCENES_*` (storyboard keyframeado).
- Hydra: `hydra/{recursion_delirio.js, outbound_delirio.js, crossing_delirio.js}` + render
  HEADLESS reusable en `hydra/_headless/render.mjs` (env vars `HYDRA_PATCH/WAV/OUT/CONTROL`;
  `a.fft` mockeado desde control track → `control_<track>.json`). `node render.mjs <segundos>`.
- AI: `ai/{audio_to_keyframes.py --track ..., local_render_diffusers.py, prompts_*, scenes_*,
  deforum_settings_*, comfyui_*}` + `README.md`. local_render_diffusers = "poor-man's Deforum"
  con diffusers/MPS, reusa el control track.
- Reporte 3×3 + recomendación de mezcla: `docs/video/06_REPORTE_3x3.md`.

**Cómo armar un mix (recordatorio):**
- Mix Hydra ablandado: `ffmpeg -i hydra/out/<t>_hydra.mp4 -vf gblur=sigma=1.5 ... out/mix_<t>.mp4`
- Transición agujero-negro: render Python `--seconds N --collapse-tail 4` → `fade=out` a negro;
  Hydra con `fade=in` desde negro; `concat` + audio master. (Ver historia: Outbound.)

**PRÓXIMOS PASOS:**
1. Afinar tiempos/curvas de transición; decidir dónde entra color por track.
2. Definir Recursion (Hydra puro vs mezcla con Python/AI).
3. **Master continuo 24:00** (Outbound→Crossing→Recursion) con seams entre temas (Hexagrama 24).
4. Pase de paleta fino si hace falta; afinar stargate (granulado leve en canal central ~650-730s
   de Crossing, línea ~332 de crossing_delirio.js si molesta).

## 7 — Decisiones abiertas (pendientes de confirmación del usuario)

1. ¿Concepto A, B, o ambos repartidos por movimiento?
2. ¿Herramienta única o combo (p.ej. shader para la base + Hydra para texturas)?
3. fps final: 24 (cine) vs 30 (CRT). Resolución master: 1080p (suficiente para
   esta estética de grano) vs 4K (4× costo sin ganancia perceptible).
4. ¿Probar la ruta AI? Depende de hardware/Colab disponible.
