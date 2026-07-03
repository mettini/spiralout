# HANDOFF — Video Crossing (para el próximo contexto / Opus 4.8)

> Punto de entrada único. Leé esto primero, en este orden, antes de tocar nada.
> Fecha del handoff: 2026-05-28.

## ⭐ ESTADO v3 — STILL (ploteo) — 2026-05-28
Rework de la gráfica Blender aplicando FEEDBACK ROUND 1. **Es un STILL, todavía
no animado** (workflow del artista: clavar la imagen fija primero).
- Script: `transmissions/01/video/blender/experiments/crossing_abstract/crossing_still.py`
- Entrega 4K: `…/crossing_abstract/crossing_still_v3_4k.png` (3840×2160, con grano)
- Render: `blender --background --python crossing_still.py -- --out out/still_4k --w 3840 --h 2160 --taa 48 --vol-samples 64` (~13 s) + grano ffmpeg.
- Qué cambió vs v2 (los 5 puntos del feedback):
  1. Bolas → blobs fuzzy con silueta AMBIGUA (Displace noise) + menisco fresnel
     + falloff Facing invertido (centro encendido, borde se apaga). No esferas limpias.
  2. Stripes → FILOTES orgánicos: curvas en Geometry Nodes onduladas (noise) +
     afinadas en puntas (perfil fino), distribuidas en una HÉLICE que converge.
  3. Oclusión → bolas sólidas escriben profundidad; glare domado (no pisa).
  4. Fondo → estrellas fantasma (Voronoi world) + niebla volumétrica tenue.
  5. Aura grim → AgX + negros crushed + contraste alto + viñeta + grano CRT.
- v2 (lo criticado) backup: `crossing_abstract_v2_backup.py` / `crossing_blender_v2.mp4`.

### MANTO "black metal noruego" — `grim_post.py` (POST compartido, REUSABLE)
El render Blender limpio se veía "fake/demasiado nítido" (feedback del artista).
`…/crossing_abstract/grim_post.py` mete el manto sucio y va a TODO el video/abstracts:
warp (inestabilidad) + aberración cromática (signal breakup) + grade sucio
(contraste/saturación/crush verde) + halación + scanlines CRT + dropouts glitch
+ grano analógico + viñeta. Escala por resolución (look consistente a cualquier res).
- Uso: `python3.10 grim_post.py IN.png OUT.png --preset crossing [--scale 1.0] [--seed N]`
- Entregas grim 4K: `crossing_still_v3_grim_4k.png` (espiral) + `planet_still_grim_4k.png` (planeta).

### Segundo abstract — PLANETA ANILLADO (escena 1) — `planet_still.py`
Planeta grande off-center (~55%, inmensidad) + terminador/sombra + superficie
abstracta moteada + rim fantasma; anillas = toros finos concéntricos (líneas
gruesas) rotos/arrastrados (fantasmagóricos), accent amber en el borde. Misma
paleta + mismo `grim_post`. Render: `blender --background --python planet_still.py -- --out out/planet_4k --w 3840 --h 2160 --taa 48 --vol-samples 64`.

### grim v2 + 4 ESCENAS (ronda 2 feedback, 2026-05-28)
Feedback artista sobre ronda 1: estaba muy nítido/fake; NO le gustan las rayas
horizontales de interferencia; quiere más saturación/contraste pero colores más
OPACOS; filotes se veían cuadrados; bolas con bordes más difusos; anillas del
planeta = DISCOS fantasmales (no "chorizos"); más fantasmagórico (humo/nebula),
terror/nórdico. Aplicado en `grim_post.py` v2 (sin scanlines/dropouts, + veil de
nebula, menos aberración, grade más opaco) + en los stills.

4 escenas-still (cada una: `<name>_still.py` → render 4K → `grim_post.py` → `<name>_grim_4k.png`):
- `crossing_still.py` → `crossing_still_v3_grim_4k.png` (ESPIRAL de filotes + bolas fuzzy)
- `planet_still.py` → `planet_still_grim_4k.png` (PLANETA anillado, escena 1)
- `lightning_still.py` → `lightning_still_grim_4k.png` (RELÁMPAGOS entrando a los discos)
- `mandala_still.py` → `mandala_still_grim_4k.png` (CALEIDOSCOPIO/MANDALA saliendo del planeta)
Render 4K (todas): `blender --background --python <s>.py -- --out out/<x>_4k --w 3840 --h 2160 --taa 48 --vol-samples 64` (~13s) + `python3.10 grim_post.py IN OUT --preset crossing`.

### ronda 3 (2026-05-28): manto v4 APROBADO + 6 escenas
El artista CONFIRMÓ la dirección ("sí, ahora sí"): DURO/OSCURO/POCO VERDE
(blanquecino)/DIFUSO/distorsionado. Memoria: [[crossing-abstracts-grim-aesthetic]].
`grim_post.py` v4: saturación baja (~0.42 gris-verde), sin verde-tinte, crush/negro,
warp BAJO (7 — no deforma las formas grandes), soften moderado + grano fuerte
(bordes definidos pero SUCIOS, no mushy). Ref color = relámpagos (aprobado).
Mandala rehecho con `kaleido_mandala.py` (pliega un frame del Hydra checkpoint en
simetría radial → tercer ojo Tool, en SU textura).

6 escenas-still (→ render 4K → `grim_post.py` → `<name>_grim_4k.png`):
`crossing_still.py` (espiral) · `planet_still.py` (planeta) · `lightning_still.py`
(relámpagos, APROBADO) · `rocks_still.py` (rocas/impacto) · `tunel_still.py` (túnel
salida, espiral converge) · mandala vía `kaleido_mandala.py /tmp/cx_frames/src_*.png`.

Lección clave: **forma LIMPIA/delineada + textura/borde SUCIO** (no forma deformada
ni borde mushy). Render BRILLANTE pre-grim (el crush oscurece mucho; lo oscuro se
come las formas). Geometría suave + shade_smooth (sin facetas/polígonos).

### ronda 4 (2026-05-28, nocturna): ESPIRAL FRACTAL + ANIMACIONES
- Planeta: polígonos del borde RESUELTOS con **Subdivision Surface** (Catmull-Clark)
  en planeta + anillas (era el limbo facetado a 4K). Aprobado ("sí, liso").
- **Espiral fractal** (`fractal_spiral_still.py`): filamentos que RAMIFICAN recursivo
  (dendrita/raíz), sembrados en espiral → vórtice fractal. Aprobado, lo quiere DENSO.
- **Pipeline de animación** (validado): `<scene>_still.py --frames N` keyframea
  giro/fly-through/deriva y renderiza secuencia → `anim_grim.sh <seq> <mp4>`
  (grim por-frame, seed fijo = movimiento suave) → mp4. Batch: `anim_all.sh`.
  Mandala girando vía `anim_mandala.py` (kaleido, sin Blender).
- Animaciones hechas: `anim_mandala_spin.mp4`, `anim_tunel_flythrough.mp4`,
  `anim_spiral_spin.mp4`, `anim_planet_drift.mp4` (720p, 4s, para pulir → luego 4K).
- Índice para el artista: `REVIEW.md` en la carpeta del experimento.

- ABIERTO: **Nébula densa** (volumétrico EEVEE quedó disco uniforme — rehacer
  plegando textura Hydra). **Inversión** (escena 5, giro que se invierte:
  `crossing_still.py --invert --frames N` ya listo, falta renderizar). **Rocas**
  otro pase (quedó oscura). Animar el FRACTAL + subir animaciones aprobadas a 4K.

## LEER EN ESTE ORDEN (no saltearse)
1. `docs/video/10_BRIEF_VISION_crossing.md` — la impronta/estética (fósforo verde CRT, Hydra, abstracto). **NO inventar otra estética.**
2. `docs/video/11_CROSSING_production_spec.md` — spec de producción 9 escenas + assessment de herramientas + investigación + **FEEDBACK ROUND 1** (al final, crítico).
3. `transmissions/01/video/hydra/SCENES.md` — estructura técnica Hydra existente.
4. Memorias: `crossing_video_vision_phosphor_hydra.md`, `feedback_no_rabbit_holes_use_my_vision.md`, `feedback_video_must_be_4k.md`.

## QUÉ ES ESTO
Video de 13:00 para el track "Crossing" (dark ambient, proyecto Spiral Out / ÆM).
**Outbound y Recursion ya están OK — solo Crossing se trabaja.**

## ESTADO ACTUAL (qué existe, dónde)
- **Base "que estaba bien"**: `transmissions/01/video/out/2-crossing-checkpoint-v7.mp4` (1280×720, render de Hydra `crossing_delirio_aire.js`, 13min completos).
- **Camino Blender (el más fuerte)**: `transmissions/01/video/blender/experiments/crossing_abstract/`
  - `crossing_abstract.py` (escena GN+EEVEE, ya en versión v2), `_v1_backup.py`, `run.sh`
  - `crossing_blender_test.mp4` (v1), `crossing_blender_v2.mp4` (v2: más oscuro, spin, alto contraste)
- **Camino vid2vid SDXL**: `transmissions/01/video/vid2vid/experiments/`
  - `restyle_diffusers.py` (SDXL img2img headless sobre frames del v7), `restyled_vid2vid.mp4`, frames en `frames_src/`
- **Camino Cavalry (sin ejecutar, GUI)**: `transmissions/01/video/cavalry/experiments/` (recipe + script JS)

## EL WORKFLOW QUE EL ARTISTA PIDIÓ (importante)
**Primero PLOTEOS/stills, clavar el look gráfico fijo, DESPUÉS animar.** La
gráfica actual se ve "de cartón". No animar hasta que la imagen fija esté bien.

## PRÓXIMO PASO CONCRETO (Blender — el camino elegido)
Rework de la gráfica Blender según FEEDBACK ROUND 1 (ver doc 11 al final):
1. **Bolas** → como mota/gota sobre vidrio: borde fuzzy/difuso, ambiguo, no esfera limpia. Que se muevan/pulsen.
2. **Stripes** → NO cuadrados/rectángulos. Filotes/hilos orgánicos. Con temblequeo audio-reactivo.
3. **Oclusión** → los stripes NO pueden pasar por encima de las bolas (arreglar profundidad/Z).
4. **Fondo** → el negro es muy negro: agregar capa de estrellas fantasma con glow, pisada por las capas de adelante.
5. **Todo girando en espiral** + "aura death metal noruego" (grim, atmósfera).
6. Trabajar primero un STILL que clave esto, después animar a 4K.

Para vid2vid (secundario): forzar paleta oscura fósforo (sin rojo/marrón) + clips más largos/lentos.

## REGLAS DE TRABAJO (no repetir errores de esta sesión)
- **NO inventar estética** — usar la del artista (fósforo verde, abstracto, Hydra). El asistente inventó "B&W woodcut/saturno fotorrealista" y fue un error grande.
- **Decir "no se puede" honesto** en vez de encadenar PoCs que fallan.
- **NO mostrar recipes sin video** — el artista valida viendo, no leyendo.
- **4K es requisito duro** del entregable final.
- **Stills antes de animar.**
- El tiempo del artista es lo más caro. QA propio antes de mostrar.

## HERRAMIENTAS — veredicto rápido
- **Blender GN+EEVEE**: $0, 4K nativo, controlable → camino principal para estructura 3D (túnel/mandala/neblina).
- **vid2vid SDXL (diffusers)**: $0, da textura sucia, pero deriva de paleta y es sub-4K → secundario, para textura.
- **Cavalry** (gratis full-Pro, 4K, GUI-only): para mandala/scanlines/telemetría → el artista lo ejecuta.
- **Hydra** (su sistema): el alma sucia/glitch, base del v7.
- DESCARTADOS: LTX/Wan/Veo/Kling/Sora, TouchDesigner (cap 1280 + licencia).
- Ensamble final: DaVinci Resolve (free, 4K) + grade velado + grain + sync al master `transmissions/01/release/masters/02_crossing_master.wav`.
