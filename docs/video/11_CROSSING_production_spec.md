# CROSSING — SPEC DE PRODUCCIÓN (video 13:00)

> Bajado del download del artista 2026-05-28. Esta es la fuente de verdad
> para producir el video de Crossing. Si se reinicia el contexto, retomar
> desde acá. Outbound y Recursion están OK — **solo Crossing se trabaja**.
> Complementa: `10_BRIEF_VISION_crossing.md` (impronta) + `hydra/SCENES.md`
> (realización técnica Hydra existente).

---

## QUÉ SIGNIFICA CROSSING (el norte emocional)

La **etapa más dura**. La transición. La parte del camino **que duele**.
- Desorientada
- Sucia
- Abstracta — **sin conceptos claros, nada literal**
- Oscura

---

## ESTÉTICA (refinada en este download)

- **Black metal noruego** en estética
- **Blanco y negro CON saturación** (no plano) — jugar con **verdes apagados**
- **Luces super difuminadas**: neblina, **luces vistas detrás de un vidrio
  empañado**. Este es el textura clave nueva: nada nítido, todo fugado/velado.
- Puntos de luz / estrellas con **luz fantasmal**
- Mantiene base: fósforo verde CRT + glitch + abstracto no-figurativo
- Luminosidad permitida SOLO hacia el final (mandala/caleidoscopio)

> **NO un saturno literal.** El planeta anillado se SUGIERE difuso, como
> "pistas", nunca como render fotorrealista.

---

## EL CUENTITO (dinámica narrativa, NO se muestra literal)

1. **Apertura**: de cerca, la inmensidad de un planeta con anillas. El planeta
   ocupa **~40% de la pantalla en un rincón**. Las anillas dan la SENSACIÓN
   de ser anillas — algo raro, difuminado, "pistas". Estrellas de fondo /
   puntos de luz con luz fantasmal. Algún movimiento.
2. **Acercamiento lento** a esas anillas.
3. **La cámara da de lleno contra las anillas** → eso se convierte en:
   fondo de radiación / piedras pegando a la cámara / humo / lava. Que dé
   vueltas, que se pegue con todo, que sea **difícil** (acá la música raspa).
4. **Hacia el final del tema**: se ven luces de fondo, nos vamos acercando.
5. **Un caleidoscopio / mandala aparece**, cambia de forma o luces (acá SÍ
   cierto grado de luminosidad), pero es un **murallón al que nos acercamos**.
6. Ese mandala / túnel caleidoscópico **gira, nos atrapa**, nos vamos por un
   **tubo oscuro** y termina.

---

## ESCENAS — desglose 13:00 (780s) con necesidades por escena

Mapeado contra la estructura Hydra existente (`SCENES.md`) + refinado con el
download. Cada escena: narrativa · necesidad gráfica · animación · herramienta
candidata · banda FFT.

### Escena 1 — APERTURA / PLANETA ANILLADO DIFUSO · 0:00–1:30
- **Narrativa**: planeta anillado ocupa ~40% pantalla en un rincón. Anillas
  como "pistas" difusas. Estrellas fantasma de fondo. Movimiento sutil.
- **Necesidad gráfica**: masa oscura off-center con halo/rim apenas insinuado;
  banda de anillas difuminada (no aros nítidos); campo de puntos de luz velados.
- **Animación**: deriva lentísima + parallax sutil estrellas vs planeta.
- **Herramienta**: Hydra (feedback `src(o0)` + `shape` central difuso) o
  shader raymarch con volumetric fog. Post: bloom fuerte + blur "vidrio empañado".
- **FFT**: SUB (masa) + LOW (densidad).

### Escena 2 — ACERCAMIENTO A LAS ANILLAS · 1:30–3:20
- **Narrativa**: acercamiento lento. Las anillas crecen, se vuelven río de
  partículas / polvo arrastrado.
- **Necesidad gráfica**: campo de partículas/polvo en banda; sensación de
  entrar en el plano de las anillas.
- **Animación**: dolly forward lento + scroll del polvo + parallax.
- **Herramienta**: Hydra `noise().thresh().scrollY/X` (ya existe en patch) +
  partículas. Post: diffuse/bloom.
- **FFT**: SUB empuje + MID flujo.

### Escena 3 — IMPACTO: RADIACIÓN / PIEDRAS / HUMO / LAVA · 3:20–5:00
- **Narrativa**: la cámara da de lleno contra las anillas → fondo de radiación
  o piedras pegando a la cámara o humo o lava. Densidad que llena el cuadro.
- **Necesidad gráfica**: membrana densa que ondula; texturas de humo/lava B&W;
  oclusiones; sensación de masa golpeando.
- **Animación**: turbulencia, domain warp, impactos.
- **Herramienta**: Hydra `voronoi().modulate(noise)` (existe) + posible sim de
  humo/fluido (Blender Mantaflow / shader fluido) para la lava/humo.
- **FFT**: LOW masa + MID warp.

### Escena 4 — ROCAS / TROPEZONES (LA PARTE DIFÍCIL) · 5:00–6:30
- **Narrativa**: rocas que ocluyen, impactos puntuales en transients. Que dé
  vueltas, que se pegue con todo, que sea difícil. La música raspa.
- **Necesidad gráfica**: bloques/rocas abstractos que cruzan; flashes en golpes;
  jitter / sacudón de cámara.
- **Animación**: jitter reactivo a onsets, oclusiones, giro.
- **Herramienta**: Hydra `voronoi` grueso `.thresh` + `shape(8)` flash + jitter
  (existe en patch).
- **FFT**: HIGH onsets (rocas).

### Escena 5 — INVERSIÓN ⭐ · 6:30–7:50
- **Narrativa**: la órbita SE PARTE. Todo gira y el sentido se invierte.
- **Necesidad gráfica**: anillo partido; inversión de rotación; solarización
  empieza.
- **Animación**: `spin()` cruza +1 → -1 suave en ~20s. Atado a hexagrama 24/42.
- **Herramienta**: Hydra `src(o0).rotate(*spin())` (existe).
- **FFT**: LOW giro invertido.

### Escena 6 — RELÁMPAGOS · 7:50–9:20
- **Narrativa**: flashes solarizados súbitos en onsets fuertes (descarga sucia).
- **Necesidad gráfica**: bolts/sheet lightning verde fósforo; solarización.
- **Animación**: flash en transients, `invert()` momentáneo.
- **Herramienta**: Hydra `osc().thresh` rayo + `mask` flash + `invert()` (existe).
- **FFT**: HIGH onsets (bolts).

### Escena 7 — RAYAS HORIZONTALES · 9:20–10:50
- **Narrativa**: rayas horizontales picantes (scan CRT roto) + chicharreo +
  dropouts.
- **Necesidad gráfica**: striping horizontal, datamosh, signal breakup.
- **Animación**: `scrollY` + crackle + dropouts reactivos.
- **Herramienta**: Hydra `osc().rotate(PI/2).scrollY` + crackle (existe).
- **FFT**: HIGH scan/crackle.

### Escena 8 — STARGATE / MURALLÓN MANDALA · 10:50–12:10
- **Narrativa**: se ven luces de fondo, nos acercamos. Caleidoscopio/mandala
  aparece como MURALLÓN, cambia de forma/luces. Cierta luminosidad permitida.
- **Necesidad gráfica**: corredor slit-scan; kaleidoscopio; color sucio
  mineral solarizado (2001, no neón); sensación de pared luminosa que se acerca.
- **Animación**: zoom fuerte hacia el murallón + `colorama` + `kaleid(5)`.
- **Herramienta**: Hydra `src(o0).scale(>>1)` + `colorama` + `kaleid` (existe).
- **FFT**: SUB fuga + MID hue.

### Escena 9 — TÚNEL OSCURO / NOS ATRAPA · 12:10–13:00
- **Narrativa**: el mandala/túnel gira, nos atrapa, nos vamos por un tubo
  oscuro y termina.
- **Necesidad gráfica**: túnel que se enrosca en espiral; oscurecimiento
  progresivo; fade.
- **Animación**: `rotate` creciente + `modulateScale(o0,>0)` Droste + fade.
- **Herramienta**: Hydra `src(o0).rotate` + Droste (existe).
- **FFT**: LOW espiral + SUB calma.

---

## PRINCIPIOS TRANSVERSALES (aplican a TODAS las escenas)

- **Dinamismo siempre** — nada estático más de unos segundos. Reactivo al audio.
- **Difuminado / vidrio empañado** — capa de bloom + blur + grain en TODO.
- **Crossfade 16s** entre escenas (no cortes secos).
- **B&W con saturación + verdes apagados** — no monocromo plano.
- **Atrapante, esotérico, abstracto** — sin conceptos literales.
- Sync al master `transmissions/01/release/masters/02_crossing_master.wav`.

---

## ASSESSMENT DE HERRAMIENTAS (qué tenemos vs qué falta)

| Necesidad | Tenemos | Falta / a resolver |
|-----------|---------|--------------------|
| Feedback abstracto + glitch + kaleid + scanlines | ✅ Hydra `crossing_delirio_aire.js` | Render headless a 4K limpio |
| Planeta anillado difuso (escena 1) | parcial (Hydra shape) | Look "anillas difusas" convincente |
| Humo / lava / fluidos (escena 3) | ❌ | Sim de fluido (Blender Mantaflow? shader?) |
| Luces vidrio empañado / volumetric fog | ⚠️ shaders/post.frag | Bloom+blur volumétrico fuerte |
| 4K final | ❌ (Hydra/WebGL capa res) | **El cuello: render 4K del patch** |
| Ensamble + grade + grain + sync | DaVinci (a instalar) | — |

---

## HERRAMIENTAS NUEVAS A INVESTIGAR (pendiente — sección abierta)

El download pide explícitamente buscar herramientas que no exploramos. Candidatas
a evaluar para ESTA estética (difuminado/audio-reactivo/abstracto/4K):
- **TouchDesigner** — audio-reactivo + bloom/feedback PRO (¿free res cap?)
- **Cables.gl** — node WebGL browser, audio-reactivo, export
- **Blender EEVEE volumetrics** — para humo/lava/fog volumétrico abstracto (NO saturno)
- **DaVinci Fusion** — compositing nodal 4K free para diffuse/glow/kaleid/grade
- **GLSL raymarch shaders** — volumetric fog + slit-scan custom a 4K

### RESULTADOS DE LA INVESTIGACIÓN (2026-05-28)

**Conclusión: NO abandonar Hydra. El único cuello (export 4K) se resuelve $0.**

**1. Hydra → 4K limpio + sync perfecto (el camino):**
- Correr el patch OFFLINE frame-by-frame con `hydra-synth` (npm) + **Chromium
  headless** (Puppeteer/Playwright), NO captura en vivo.
- `new Hydra({width:3840, height:2160, autoLoop:false})` → controlás el reloj
  con `synth.tick(dt)` fijo (1000/30 ms) → render **determinista** (cada frame
  perfecto aunque tarde segundos; al ser offline no importa la velocidad).
- FFT **pre-analizada offline con `meyda`** (la misma lib de Hydra) a un array
  `[frame][banda]`, inyectada en cada tick → **sync de audio sample-accurate**
  (imposible en captura realtime).
- Cada frame → PNG → `ffmpeg` arma MP4/ProRes + pega el audio.
- Chromium headless renderiza WebGL a 4K sin drama (límite textura 16384px).
- DESCARTADO: `headless-gl` puro (no soporta todas las extensiones WebGL2 que
  usa Hydra). Chromium headless es el seguro.

**2. Alternativas audio-reactivas — veredicto:**
- ❌ **TouchDesigner free**: cap 1280×1280 + licencia non-commercial PROHÍBE
  release monetizado. Doble bloqueo. Descartar.
- ❌ **cables.gl**: no exporta 4K nativo (mismo cuello que Hydra, sin ventaja).
- ✅ **Plan B real**: Processing / openFrameworks / p5.js con `saveFrame()` —
  render offline 4K, audio-reactivo con FFT pre-analizada. Sin caps ni licencias.
  Distinta curva de código, mismo resultado. Solo si no querés tocar Node.

**3. Look "vidrio empañado / difuminado" → en POST, no en el motor:**
- **DaVinci Resolve FREE exporta 4K UHD 3840×2160 hasta 60fps sin watermark.**
- Nodo **Glow** nativo + plugin gratis **X-Glow** (falloff de lente orgánico) +
  Gaussian Blur leve + Soft Clip = el bleed velado CRT.
- Curva/key para empujar verdes a `#a6d65f`. Scanlines + halation en Fusion.

**4. Humo / lava / fluidos B&W (escena 3):**
- ✅ **Más eficiente $0**: stock B&W free de **Mixkit** (sin atribución, uso
  comercial OK) y **Pexels** 4K, humo/fluido sobre negro → blend Screen/Add en
  Resolve sobre Hydra. Instantáneo, sin render farm.
- Alternativa propia: **Blender EEVEE volumetrics** (Principled Volume + bloom)
  para neblina — rápido, tiempo-real. Mantaflow es viable en M-series pero
  pesado a 4K (bajar densidad de sim).

**STACK FINAL $0:**
```
GENERATIVO   → patch Hydra offline (hydra-synth + Chromium headless, 4K, tick fijo, FFT meyda)
HUMO/LAVA    → stock B&W Mixkit/Pexels + EEVEE volumetrics opcional
LOOK VELADO  → DaVinci Resolve free + X-Glow (glow+blur+verdes+scanlines)
CALEIDOSCOPIO/TÚNEL → Hydra (ya existe) + Fusion para refinar
ENSAMBLE     → ffmpeg/Resolve: frames + audio → MP4/ProRes 4K
```
Costo total: **$0**. Único "costo": montar el pipeline headless de Hydra
(~un par de tardes de código Node).

---

## BÚSQUEDA DISTINTA (2026-05-28) — técnicas NUEVAS, no exploradas antes

El artista pidió explícitamente NO volver con "usá Hydra/upscale". Esto es lo
genuinamente distinto que sirve para SALTAR de "Hydra 720p" a algo más rico:

### ⭐ 1. VID2VID RESTYLE: Draw Things (keyframes) → EbSynth (propagación)
**El salto más grande conservando tu trabajo.** Usás el render Hydra como
ESQUELETO (movimiento + estructura) y una AI le re-pinta textura rica encima:
- **Draw Things** (gratis, nativo Apple/MPS, ~3x más rápido que ComfyUI):
  ControlNet (lineart/HED/depth) toma frames de Hydra como condicionamiento →
  SD/SDXL re-pinta con la estética black-metal/velada/fósforo. Hereda la
  geometría de cada frame Hydra.
- **EbSynth** (gratis, corre en Mac): la pieza que faltaba. Restyleás 1-N
  KEYFRAMES con Draw Things, y EbSynth los **propaga por optical-flow** al
  resto → coherencia temporal real, SIN flicker, preservando el movimiento.
- Flujo: Hydra frames → Draw Things restyle de keyframes → EbSynth propaga →
  ffmpeg. Local, $0.
- ❌ ComfyUI+AnimateDiff en MPS: descartado para 13min (lento, crashea).
- Para PROBAR el look sin armar pipeline: GoEnhance / DomoAI (free tiers chicos,
  sirven para validar, no para los 13min completos).

### ⭐ 2. CAVALRY — ahora 100% GRATIS full-Pro (Canva lo liberó abr 2026)
- Motion design 2D pro, data-driven. Falloffs/Duplicator/Forge Dynamics →
  ideal para **mandalas, caleidoscopios, scanlines, telemetría NASA vintage**.
- **Exporta 4K nativo, $0, SIN restricción de monetización** (a diferencia de
  TouchDesigner). Llena justo ese hueco.
- Esfuerzo medio, salto visual inmediato. Componer capas sobre Hydra.

### ⭐ 3. BLENDER Geometry Nodes + EEVEE volumetrics
- Geometry Nodes **audio-driven** (waveform como driver de parámetros — hay
  charla oficial Blender Conf) → túneles/fractales/mandalas.
- **EEVEE volumetrics** = la neblina / "vidrio empañado / velado" NATIVA.
- 4K real sin upscale. MPS-acelerado. Curva alta pero control total del look.
- NO para saturno literal — para abstracto volumétrico.

### Ranking esfuerzo/resultado (las 3 nuevas)
1. **Draw Things → EbSynth** — el vid2vid local-$0 que da el salto de textura
   conservando tu Hydra. Mejor relación esfuerzo/resultado.
2. **Cavalry (gratis)** — capas mandala/scanlines/telemetría 4K nativas sobre Hydra.
3. **Blender GN + EEVEE** — túneles/neblina audio-driven 4K, máximo control.

Las tres son DISTINTAS a: Hydra solo, LTX/Wan/Veo/Kling/Sora, upscaling, TouchDesigner.

---

## FEEDBACK ROUND 1 del artista (2026-05-28) — CRÍTICO, leer antes de seguir

Tras ver el primer test de Blender (v2) y el vid2vid SDXL. Material visto:
- `transmissions/01/video/blender/experiments/crossing_abstract/crossing_blender_v2.mp4` (4K, túnel fósforo girando)
- `transmissions/01/video/vid2vid/experiments/restyled_vid2vid.mp4` (1024×576, v7 restyleado SDXL)

### WORKFLOW (insight clave del artista)
> "Podemos pasar a un paso anterior, armar unos ploteos y luego animarlos? Es
> de cartón la gráfica."

**NO animar antes de que el STILL esté bien.** Primero armar PLOTEOS / frames
estáticos, clavar el look gráfico, DESPUÉS animar. La gráfica actual se ve "de
cartón" (barata) — hay que resolver la imagen fija primero.

### Feedback sobre el BLENDER v2 (qué está mal y qué quiere)

1. **Las bolas/esferas — muy literales.** Quiere que sean como **una mota/gota
   sobre un vidrio**: borde distinto/diferenciado, O borde **fuzzy/difuso**,
   ambiguo — "que no sabés qué casco es". NO una esfera limpia obvia.
2. **Los stripes/shards son un CUADRADO literal.** "Loco, ¿vos ves eso en el
   espacio?" Demasiado geométrico/duro/rectangular. Tienen que ser **filotes
   (hilos/filamentos)**, orgánicos, no rectángulos.
3. **Los stripes NO pueden pasar POR ENCIMA de las bolas.** Error de
   oclusión/profundidad — las bolas tienen que tapar los stripes, no al revés.
4. **Más dinamismo en cada elemento:**
   - Las bolas que **hagan algo** (se muevan / pulsen).
   - Los stripes/filotes con **temblequeo audio-reactivo** ("temblequeo por las
     frecuencias que maneja") — reaccionan al audio.
   - **Todo girando en espiral** (reforzar el spin).
   - **Falta el "aura de death metal noruego"** — más grim, más atmósfera.
5. **El negro es DEMASIADO negro.** Quiere las **estrellas con glow / visión
   fantasmal de fondo** (las que pidió antes) — una capa de fondo de estrellas
   fantasma, pisada/overlayeada por las capas de adelante. Que el fondo no sea
   negro plano.

### Feedback sobre el VID2VID SDXL

- **Las texturas le gustan.** Ese es el valor de este camino.
- **PERO**: reducir la paleta a la que manejamos (fósforo verde B&W oscuro) —
  el test se contaminó de rojo/marrón, hay que forzar paleta oscura on-brand.
- **El clip pasó "rapidísimo"** — fue solo 2s/48 frames del v7 (que morphea
  rápido). Hacer clips más largos/lentos para poder evaluar.

### Estado de las herramientas tras Round 1
- **Blender**: el camino más fuerte, on-paleta, 4K, controlable — pero la
  gráfica necesita el rework de arriba (filotes no-cuadrados, bolas fuzzy con
  oclusión correcta, fondo de estrellas fantasma, temblequeo audio-reactivo).
- **Vid2vid SDXL**: texturas buenas, falta forzar paleta oscura + clips más largos.
- **Cavalry**: recipe sin ejecutar (GUI-only) — `cavalry/experiments/`.
- **Hydra v7**: la base "que estaba bien" — `out/2-crossing-checkpoint-v7.mp4`.
