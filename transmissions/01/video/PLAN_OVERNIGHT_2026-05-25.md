# Overnight 2026-05-25 — Task A (assembly) + Task B (AI render)

Dos videos de 13 min a entregar mañana. Documento lo que voy a ejecutar y dónde
están los outputs para que mires en cuanto te despiertes.

---

## Task A — assembly Crossing 13min con los materiales aprobados

**Pipeline**: extender los `animate_*.py` para timeline largo + crossfades →
encode mp4 + sync con `crossing_master.wav`.

**Storyboard 13:00 (780s)** :

| Inicio | Fin   | Sección                    | Descripción |
|--------|-------|----------------------------|-------------|
| 0:00   | 0:30  | Cold open                  | Negro + stars fading in |
| 0:30   | 3:30  | **SATURN aproximación**    | Saturno distorsionado off-center, scale crece + motion blur. Stars shake en background. |
| 3:30   | 4:00  | TRANSITION → stones        | Anillos se "rompen" en granular → fade a stones field. La magia: los dots eran rocas. |
| 4:00   | 8:30  | **STONES flow**            | Lava B&W fluyendo. Variaciones de scale + density + speed. ~4:30 — antes de que se pudra. |
| 8:30   | 9:15  | TRANSITION → stars         | Stones dissipate, contrast baja, fade a negro con stars subtle |
| 9:15   | 11:30 | **STARS limpias**          | Cielo abierto, chromatic_green ghost + shake en el lugar. ~2:15 |
| 11:30  | 12:00 | TRANSITION → mandala       | Punto de luz crece, se transforma en mandala center |
| 12:00  | 12:40 | **MANDALA breathing**      | Scale + rotación visibles |
| 12:40  | 13:00 | **TUNNEL** + fade to black | Mandala zoom acelera, kaleidoscope-tunnel, fade out |

**Params técnicos**:
- 1280x720 @ 24 fps  ⇒ 18720 frames totales
- Estimado: ~5-6 hs render PIL (CPU) en background
- Audio: `transmissions/01/release/masters/02_crossing_master.wav`

**Output esperado**:
`transmissions/01/video/out/maquetas/picks/crossing_assembly_v1.mp4`

---

## Task B — AI render Crossing 13min B&W trash/nordic

**Engine**: `local_render_diffusers.py` (mismo que recursion). SDXL Turbo
img2img frame-a-frame con control track de `crossing.npz`. Reseed por escena
+ reinject anti-deriva.

**Narrativa esoterica → scene-graph**:

| Inicio | Sección                              | Prompt key elements |
|--------|--------------------------------------|---------------------|
| 0:00   | Aproximación nave → planeta anillado | dark void, distant ringed planet, ship approaching, blacker than black, nordic, woodcut |
| 1:30   | Relampagos / rayos en el planeta     | lightning over the rings, charged void, electric discharge, dread |
| 3:00   | Tragada por cinturón asteroides     | thrown into asteroid belt, rocks rushing past, dust streaks, helpless |
| 4:30   | Trompicones piedras polvo            | violent traversal, debris flying, claustrophobic, vertigo |
| 6:00   | "Donde estamos?" visiones esoteric   | impossible geometry, ghost figures, omens, hexagrams, runes, nordic mythos |
| 7:30   | Incongruencia / esoterismo presente  | non-euclidean space, broken physics, eye sigils, sacred geometry corrupted |
| 9:00   | Disipa polvo / sale a estrellas      | dust falls back, vast starfield emerges, calmer, glacial |
| 10:00  | Luz/Mandala aproxima                 | distant luminous mandala, fractal core, pull |
| 11:00  | Caleidoscopio gigante / velocidad    | giant kaleidoscope, walls distorting from velocity, infinite folds |
| 12:00  | Ojo al fondo del caleidoscopio       | an eye at the center, watching, ancient, all-seeing |
| 12:40  | Fade out to black                    | (final scene tail) |

**Params técnicos**:
- 640x360 @ 8 fps  ⇒ 6240 frames totales (low-fi black-metal feel ayuda)
- Estimado: ~5-7 hs render en MPS
- Audio: `02_crossing_master.wav` muxed
- Negative prompts: anti-figura humana reforzado (ya está en el engine)

**Output esperado**:
`transmissions/01/video/ai/out/crossing_metal_v1.mp4`

---

## Modelo AI alternativo — Tercera opción (si SDXL Turbo no entrega)

**Recomendación si SDXL Turbo derive**: probar **AnimateDiff + SDXL Lightning** en
ComfyUI — temporal consistency dedicada (no parche frame-a-frame). Trade-off:
más setup, requiere ComfyUI + AnimateDiff weights (~5GB), pero el flow temporal
es nativo (no necesita anti-drift hacks).

**Si querés probar otra ruta para black-metal**:
- **CogVideoX-5B** (Q4 quantized): text2video nativo, 6 sec clips concatenables.
  Open source, corre en MPS lento pero entrega temporal consistency real.
- **LTX-Video** (Lightricks): text/img2video, 5 sec clips, license open. Buena
  fidelidad al prompt, fast (5s clip ~30s en buen GPU; en MPS ~3-5 min).

Para esta noche **arranco con SDXL Turbo** (el engine probado) — los alternativos
los planteo como Plan B para iterar mañana si Task B no entrega lo que queremos.

---

## Notas de QA

Para minimizar errores tipo los de hoy:
- Cada sección tendrá un "check frame" en `out/maquetas/picks/animations/_qa/`
  con un sample frame mid de cada sección — los podés ver de un vistazo.
- Si el assembly Task A revela un bug, queda en queue para iterar — NO voy a
  re-encodear todo el 13min sin tu OK.

---

## Estado de iter-2 fixes (lo que hicimos esta tarde)

- **stars chromatic_green shake** ✓ (fixeado el bug de subpixel = 0; ahora ndimage.shift bilineal)
- **stars streak shake** ✓ 
- **mandala overscan 2.5x** ✓ (no más bordes negros)
- **saturn off-center distorsionado** ✓ (gravity_lens source + motion blur creciente)

Pendiente fix menor en saturn iter 2:
- A `scale_min=1.0` no había margen para off-center real. Cambié a `scale_min=1.5`.
- Re-rendereo en el contexto del assembly Task A (no perdés tiempo viendo un test 5-sec ahora).
