# Heliopause — videoclips · plan de dirección creativa + bajada técnica (AI generativo open-source / local)

> **Qué es esto.** Plan de dirección para los videoclips de *Heliopause /
> Transmission 01*, usando exclusivamente **AI generativa open-source y
> local** (Stable Diffusion / ComfyUI / Deforum / AnimateDiff / Wan / LTX),
> con audio-reactividad real (las ondas dirigen la imagen). NADA de
> herramientas pagas (Kaiber / Neural Frames / Runway / Pika / Sora quedan
> fuera por definición).
>
> **Qué NO es.** No es un encargo a un proveedor externo, no es "tirar el
> tema en una web y ver qué sale". Es un sistema de dirección donde **el
> artista dirige** y la AI ejecuta dentro de un constraint. La tesis del
> proyecto ("composición humana + AI donde el artista dirige") se mantiene
> en lo visual.
>
> **Estado.** Planificación. No se generó nada todavía.

---

## 0 · TL;DR de la propuesta

Construir los videoclips como **transmisión continua de telemetría visual**:
una sola pieza de ~24 min (tres movimientos) donde **la propia onda sonora
deforma la imagen frame a frame**. La técnica central es `audio → librosa
→ series de keyframes → motion` sobre un pipeline open-source. El estilo se
**ancla** (paleta phosphor + sci-fi 70s ya validadas en `artwork/generated/`)
con ControlNet + IPAdapter + first-frame restyle para que NO derive en "sopa
AI" genérica. La variable conceptual única es **el cruce de un umbral** — y la
imagen literalmente cruza umbrales cuando el audio cruza los suyos.

Prototipo recomendado: **primeros 60s de Outbound** (nacimiento / latido /
despegue), porque es donde el mapeo audio→imagen es más legible y más barato
de computar.

---

## 1 · Dirección creativa abstracta

### 1.1 La variable única (Patrón 1 · creative-direction)

> **Variable: el CRUCE DE UMBRAL.**

No es "el espacio", no es "lo cósmico" (eso es tema/estética, no variable).
Es la **operación** que el lore nombra una y otra vez: *"el viento que
empujaba deja de empujar, y empieza otra cosa"*. Un nacimiento es un cruce.
La inversión de fase a mitad de *Crossing* es un cruce. El loop de *Recursion*
que engancha con *Outbound* es un cruce. **Todo el EP es la misma operación
girando** (24 ↔ 42, la cara que mira adentro y la que mira afuera).

La variable se traduce a lo visual como una regla dura: **cada vez que el
audio cruza un umbral perceptible (un onset, un cambio de energía, la inversión
de fase del minuto ~12 de Crossing, el enganche del loop), la imagen tiene que
cruzar el suyo** — un cambio de prompt, una inversión de color, un salto de
estructura. La imagen no ilustra el cruce: lo *ejecuta* en el mismo instante
en que el sonido lo ejecuta.

Si una decisión visual no sirve al cruce de umbral, se descarta. Eso protege
contra el ornamento (la "sopa AI" decorativa que no significa nada).

### 1.2 Materia prima compartida, no ilustración (Patrón 2)

La prueba de Romagosa: *"¿podría existir el video sin escuchar el disco?"*. Si
sí, está ilustrando. Acá la respuesta es **no**, por construcción: los
keyframes de movimiento, fuerza y color **son funciones de la señal de audio**
(RMS, onset, centroide espectral, croma). La materia prima compartida es
**literal** — los mismos arrays de NumPy que sintetizan el track (`framework/
aem/`, SR=22050) se vuelven a leer con librosa para dirigir el video. El medio
es el mismo. El cordón umbilical código↔sonido↔imagen es real, no metáfora
(coherente con `docs/07_vision.md`, "AIRTE", "el código es el medium").

> No "dibujamos cómo suena el latido". Tomamos el envelope del latido y con él
> empujamos el `zoom`/`strength` del frame. El pulso cardíaco del minuto 0:30
> de Outbound ES el pulso de la imagen.

### 1.3 Hexagrama 24 (復 Fù · El Retorno) como ancla

El hexagrama 24 — cinco trazos yin + una línea yang entrando por abajo — es la
forma del proyecto: *"lo nuevo entrando por abajo"*, *"la luz que entra otra
vez por la grieta donde antes había salido"*. En lo visual eso se vuelve una
**gramática de composición y de montaje**:

- **La línea yang entra por abajo.** Las entradas importantes (despegue de
  Outbound, vestigio del Voyager en Crossing, primer destello de retorno en
  Recursion) **emergen desde el borde inferior del frame** y empujan hacia
  arriba. Movimiento `translation_y` negativo (la cámara sube / el contenido
  asciende) en cada nacimiento.
- **El retorno como estructura, no como dibujo.** No hay una espiral dibujada
  flotando (lo prohíbe el lore: *"la espiral nunca se ilustra de manera
  obvia"*). El retorno está en el **montaje**: el último frame de Recursion
  re-inyecta el primer frame de Outbound como init image (loop cerrado, igual
  que el audio engancha armónicamente). El video, en loop infinito, no tiene
  corte. *Fù* ejecutado, no ilustrado.
- **24 → 42 girando.** Una transición clave: a mitad de Crossing, la imagen
  **se invierte** (rotación 180° lenta / inversión de paleta phosphor↔ámbar) —
  la misma cifra mirada desde el otro lado. Sutil, sin texto que lo explique.

### 1.4 Hilo conductor mapeado a los tres movimientos + imágenes del artista

| Mov. | Imagen del artista (verbatim) | Umbral que se cruza | Traducción visual |
|---|---|---|---|
| **Outbound** (8:00) | "un nacimiento, oscuridad, los latidos llaman, se despega" | nacimiento = primer cruce | Negro absoluto → primer latido empuja la imagen desde abajo (yang entra) → estructura wireframe que se desprende y acelera hacia afuera. La oscuridad es punto de partida, no estética. |
| **Crossing** (13:00) | "nébulas, polvo de los anillos de Saturno, tropezones con rocas, dificultad en el andar" | inversión de fase (min ~12, 24°) | Densidad: polvo/grano que se acumula, oclusiones que tropiezan la cámara (jitter en `translation` cuando hay onsets graves). En el centro exacto: la imagen se da vuelta (24↔42). Vestigio del Voyager = un destello de la paleta/estructura de Outbound que "llega de pedo". |
| **Recursion** (3:00) | "una vuelta, un retorno, un vinilo gastado que chicharrea, volver a nacer, spiral out" | el loop (cierre engancha con apertura) | Lo más denso: el frame se satura, glitch/crackle visual (vinilo gastado), el ECO de Outbound vuelve deformado (mismo init, una octava de degradación visual: LPF de color, disintegration-loop estilo Basinski aplicado a la imagen). Último frame = primer frame de Outbound. |

### 1.5 Inversión de tropos del género (Patrón 5)

Tropos visuales heredados del "space ambient / dark ambient visualizer":
1. Nébulas fotorrealistas tipo fondo de pantalla Hubble. **Se invierte:** nada
   figurativo-realista; telemetría / wireframe / phosphor (la línea A ya
   establecida).
2. Túnel psicodélico fractal infinito (el cliché Deforum por excelencia). **Se
   cita al revés:** usamos Deforum, pero con `strength` alto + ControlNet
   atado a una geometría, para que NO se vuelva el zoom-fractal-mareo genérico.
3. Audio-reactivity tipo "barras de ecualizador / waveform brillante". **Se
   ignora:** la reactividad acá deforma la *materia* de la imagen, no dibuja un
   medidor encima.
4. Astronautas / planetas / naves. **Prohibido por lore** (`03_lore.md`).
5. Glow neón synthwave cyan/magenta. **Prohibido por design system.**

La firma autoral es la **telemetría que respira con el audio** — no el viaje
psicodélico ni el visualizer de barras.

### 1.6 Lectura antes que Pinterest (Patrón 7)

La fase 1 no es generar imágenes. Es releer lo que ya alimenta el proyecto:
`docs/02_cosmologia.md` (la carta, el cuerpo, el cruce, la vuelta),
`docs/10_cuento.md` (el expediente HP-01: "una onda no atraviesa un medio: es
el medio atravesándose" — esa frase ES la tesis audio-reactiva), y los textos
de las directoras en `creative-direction/SOURCES.md`. De ahí emerge el sistema;
las imágenes de referencia (que ya existen en `artwork/generated/`) son
confirmador, no generador.

### 1.7 Chequeo creative-direction (resumen)

- ✓ **P1 Variable única**: *cruce de umbral*, nombrable en dos palabras, opera
  como ley de montaje y de reactividad.
- ✓ **P2 Materia prima compartida**: los keyframes SON funciones del audio
  (NumPy/librosa), no una ilustración.
- ○ **P3 Decisión material como conceptual**: el "soporte" acá es el formato de
  entrega — *un master continuo en loop infinito* (YouTube/Bandcamp) ES la
  decisión conceptual (el lore lo pide: "versiones en loop infinito como
  performance del concepto"). Profundizable: ¿edición física? (no aplica ahora).
- ✓ **P5 Inversión de tropos**: se listan 5, se invierten/ignoran con
  conciencia.
- ○ **P6 Equipo estable**: hoy el "equipo" es artista + este pipeline. Si más
  adelante entra un colaborador de motion, que sea estable entre transmisiones.
- ✓ **P7 Lectura antes que Pinterest**: el sistema sale de cosmología/cuento.
- **Observación clave**: el riesgo número uno de la AI generativa de video es
  que la herramienta imponga *su* estética (drift, sopa, túnel fractal) por
  encima de la del autor. Todo el stack de la sección 3 está elegido para que
  el control autoral gane: ControlNet/IPAdapter como correa, audio como
  director, paleta cerrada como constraint.

---

## 2 · Por qué AI open-source sirve a ESTA música/concepto — y cómo se mantiene el control autoral

### 2.1 Por qué sirve conceptualmente

1. **Coherencia con la tesis del proyecto.** *Heliopause* ya es "composición
   humana + AI dirigida por el artista", sintetizada en Python con las mismas
   libs (NumPy/SciPy) que usa el CERN (`docs/07_vision.md`). Hacer el video con
   AI **local y open-source** — no con una API paga de caja negra — es la misma
   postura ética/estética un nivel más arriba. El medium (código abierto, corre
   en tu máquina, reproducible desde un script) ES el mensaje.
2. **El concepto pide reactividad, no narrativa.** No hay personajes (lo
   prohíbe el lore). No hay que contar una historia con actores. Hay que hacer
   *sentir una operación física* (un cruce, una onda atravesando un medio).
   Para eso la AI generativa audio-reactiva es la herramienta exacta: convierte
   una señal en materia visual mutante. Una productora de video tradicional
   sería cara y *menos* fiel al concepto.
3. **Reproducibilidad = firma del proyecto.** Igual que los WAV se regeneran de
   `compose_*.py`, el video se regenera de un `settings.json` (Deforum) o un
   workflow `.json` (ComfyUI) + el WAV. El video pesado es gitignoreable; la
   *receta* se versiona. Misma política que `transmissions/`.

### 2.2 Anti "sopa AI" — las cinco correas de control autoral

La "sopa AI" (frames inconsistentes, drift de estilo, túnel fractal genérico,
caras que aparecen donde no debe) es el modo de fallo por defecto. Se combate
con cinco mecanismos, todos open-source:

1. **El audio dirige (no el azar).** Los keyframes no son random ni "lo que
   salga": son funciones deterministas de la señal (sección 4). El artista
   elige *qué feature maneja qué parámetro* y *con qué curva*. Eso es dirección,
   no generación ciega.
2. **ControlNet como esqueleto.** Atar cada frame a una geometría de control
   (depth/canny/lineart derivada de un init video — ver 2.3) impide que la
   imagen "se vaya". La estructura la pone el autor; la AI sólo la viste.
3. **IPAdapter como ancla de estilo.** Se le pasa **una imagen de referencia
   del propio proyecto** (un frame de `artwork/generated/01_hero_background_
   painterly/` o de la línea A phosphor) como *style reference*. IPAdapter
   fuerza la paleta y la textura del proyecto en cada frame → no deriva a otra
   estética. (Yvann-Nodes incluso permite que el audio modle el *peso* del
   IPAdapter por frame.)
4. **First-frame restyle / init image.** Tanto Wan 2.2 Restyle como LTX-2
   inyectan un primer frame estilizado y propagan ESE estilo por la secuencia
   (combate el style drift de los métodos prompt-only). El primer frame lo
   generamos nosotros con el pipeline de imagen ya validado (Draw
   Things/Diffusers + FLUX/SDXL) siguiendo `docs/13_visual_style_guide.md`.
5. **Paleta y negative prompt cerrados.** El `negative` base del proyecto
   (`prompt_library.md`: sin neón, sin cyan/magenta, sin caras, sin
   watermarks) viaja en cada frame. La paleta phosphor `#a6d65f`/`#0d1014` es
   constraint, no sugerencia.

> Regla de oro heredada del artwork (`README.md` de los briefs): **el texto va
> después.** Las labels de telemetría (`TRANSMISSION 01`, `42HZ`,
> `01 OUTBOUND 08:00`) se componen encima en VT323 real (CSS/SVG/After
> Effects/DaVinci), nunca se le pide a la AI que escriba texto — lo inventa.

### 2.3 Hibridación: dirigir la AI con una base de shaders/geometría

Opción de máximo control que vale la pena (coherente con el espíritu del repo):
en vez de dejar que Deforum invente la cámara, **generar un init video base por
código** — un render de shaders (GLSL/Shadertoy export, o un script
Python/processing) con la geometría del proyecto: wireframe landscape estilo
Battlezone, la elipse Voyager, el hexagrama latiendo, una espiral logarítmica
fina. Ese init video (aunque sea crudo, en phosphor sobre negro) entra como:
- **init/vid2vid** (Deforum `video_init_path`) con `strength` medio-alto, o
- **ControlNet depth/lineart** en ComfyUI/Wan, o
- **first frame** para LTX/Wan Restyle.

La AI entonces *viste* nuestra geometría con textura cinemática en vez de
inventar una. El audio sigue dirigiendo encima (deforma tanto el shader base
como el `strength` de la AI). Esto es lo más cerca de "el artista dirige" que
se puede llegar — la composición la pone el autor, la AI sólo da el acabado.

---

## 3 · Stack técnico — PRO, gratis y local

Dos rutas. Empezar por la **A** (más simple, más madura para esta estética),
escalar a la **B** cuando se quiera fotorealismo/movimiento más rico. Ambas
100% open-source.

### Ruta A — Deforum (Automatic1111/Forge) · el caballo de batalla audio-reactivo

El camino más probado y mejor documentado para audio-reactividad fina sobre
SD 1.5 / SDXL. Es el que mejor encaja con la estética telemetría/wireframe.

| Pieza | Qué es | Licencia | Rol |
|---|---|---|---|
| **Stable Diffusion WebUI Forge** (o Automatic1111) | host de SD, GUI | open-source | motor de inferencia |
| **Deforum extension** | animación 2D/3D por keyframes (zoom, angle, translation_x/y/z, rotation_3d, strength, cadence) | open-source | el motor de movimiento |
| **ControlNet extension** | condicionamiento por depth/canny/lineart/openpose | open-source | esqueleto (anti-drift) |
| **Audio Keyframe Generator** (`nicolai256/audio_keyframe_deforum`, Colab de `fzantalis`, o `kacia.com` tools) | convierte WAV → series de keyframes Deforum | open-source | el puente audio→parámetros |
| **librosa** | extracción de features (RMS, onset, centroide, croma, beats) | ISC (open) | análisis de audio a medida (sección 4) |
| **SD 1.5 / SDXL + LoRAs** (Pixel Art XL, Retro/1980s Sci-Fi, DreamShaper XL) | checkpoints de estilo | Open RAIL++ | la paleta visual |
| **FLUX.1 schnell / SDXL** (Draw Things o Diffusers, ya en el repo) | generación de imagen estática | Apache 2.0 / RAIL++ | first frames + init images |

Por qué Deforum para esto: la audio-reactividad en Deforum es **directa y
fina** — mapeás un feature de audio a una *math expression* de keyframe (ej.
`zoom: 0:(1.0 + 0.04*sin(...))` o una serie precomputada por frame). Control
total, determinista, reproducible desde el `settings.json`.

### Ruta B — ComfyUI · coherencia temporal + modelos de video 2026

Cuando se quiera menos flicker y movimiento más orgánico que el clásico
zoom-Deforum, ComfyUI es "la interfaz definitiva para video local" y soporta
todos los modelos open de 2026 vía nodos comunitarios.

| Pieza | Qué es | Licencia | Rol |
|---|---|---|---|
| **ComfyUI** | host node-based | open-source | orquestador |
| **AnimateDiff-Evolved** (`Kosinkadink`) | motion module sobre SD, context windows para clips largos | open-source | coherencia temporal |
| **ComfyUI-Advanced-ControlNet** | ControlNet + context options + SparseCtrl | open-source | esqueleto temporalmente coherente |
| **IPAdapter Plus** | style reference por imagen | open-source | ancla de estilo del proyecto |
| **ComfyUI_Yvann-Nodes** *o* **ComfyUI_RyanOnTheInside** | audio reactivity (amplitude/drums/bass weights, peak detection → AnimateDiff scheduling, IPAdapter transitions, prompt schedule) | open-source | reactividad nativa en el grafo |
| **ComfyUI-Frame-Interpolation** (RIFE VFI, recom. rife47/rife49) | interpolación de frames | open-source | sube fps sin re-generar |
| **Modelos de video** según hardware (ver 3.1) | Wan 2.2 / LTX-Video / CogVideoX / HunyuanVideo / Mochi | Apache 2.0 (Wan/CogVideoX/Mochi) | generación/restyle de video |

### 3.1 Modelos de video open-source 2026 (para Ruta B)

| Modelo | Fuerte en | VRAM (cuantizado) | Licencia | Para qué acá |
|---|---|---|---|---|
| **LTX-Video / LTX-2** | velocidad (4s 720p < 30s en RTX 4090), audio+video nativo, 4K, ControlNet por first-frame | 13B FP8: ~14–18 GB; 2B: ~8–12 GB | open | clips rápidos, iteración, restyle por first frame |
| **Wan 2.2** | calidad / consistencia, MoE, Video Restyle (depth+canny+IPAdapter, anti-drift) | 14B GGUF: ~6 GB @480p, más a 720p | Apache 2.0 | restyle de un init video con anclaje fuerte de estilo |
| **CogVideoX-5B** | liviano, 6s 720×480, soporta cuantización | FP8: ~16 GB; 2B aún menos | Apache 2.0 | fallback de bajo VRAM |
| **HunyuanVideo 1.5** | movimiento/física naturales | ~8 GB con GGUF | open | si se quiere movimiento más realista (menos prioritario, estética no figurativa) |
| **Mochi 1** | fidelidad de short video | FP8: ~20 GB | Apache 2.0 | opcional |

Con FP8 + GGUF + tiling, **casi todos corren en GPU de consumo** (8–16 GB).

### 3.2 Requisitos de hardware y alternativas gratis

- **Mac Apple Silicon (la máquina del proyecto).** El pipeline de **imagen** ya
  corre local en MPS (Draw Things / Diffusers, FLUX/SDXL — ver
  `generation_briefs/README.md`). Para **video**: Deforum (Ruta A, SD1.5/SDXL)
  corre en Mac vía ComfyUI/A1111 con MPS, lento pero funcional. Los modelos de
  video pesados de 2026 (Wan/LTX) **todavía no tienen MPS oficial** a enero
  2026 — hay workarounds reportados (LTX 2.3 con parches MPS, ~5 min/clip en
  M3), pero es frágil. **Recomendación realista**: hacer Ruta A (Deforum) local
  en el Mac, y reservar Ruta B (Wan/LTX) para Colab gratis o una GPU prestada.
- **Colab Free (T4 16 GB).** Sirve para Deforum SD1.5/SDXL y para modelos de
  video chicos/cuantizados (LTX 2B, CogVideoX-2B, AnimateDiff). Los modelos
  grandes a veces piden L4 (tier pago). Para el prototipo de 60s alcanza el T4.
  La *herramienta* sigue siendo gratis (es la GPU lo que se "consigue", no se
  paga una suscripción de software de video).
- **GPU NVIDIA de consumo (si se consigue).** RTX 3060 12 GB / 4070 → LTX,
  CogVideoX-2B, AnimateDiff cómodos. RTX 4090 24 GB → todo, rápido.

### 3.3 Cómo se encadena (vista de pájaro)

```
WAV del track (transmissions/01/release/masters/*.wav, SR 22050/44100)
        │
        ▼
[librosa] extrae features por frame de video (fps fijo, p.ej. 12/15 fps)
   RMS, onset_strength, spectral_centroid, chroma, beats
        │  → normalización + suavizado + curvas (sección 4)
        ▼
[series de keyframes]  zoom / translation / rotation / strength / prompt_sched
        │
        ├── Ruta A → Deforum (settings.json)  ── ControlNet(init video) ─┐
        │                                                                 │
        └── Ruta B → ComfyUI (Yvann/Ryan nodes → AnimateDiff/Wan/LTX)    │
                         ── ControlNet + IPAdapter(style ref) ───────────┤
                                                                          ▼
                                              [frames PNG por movimiento]
                                                          │
                                   [RIFE VFI] interpola 12→24/30 fps
                                                          │
                                   [Real-ESRGAN] upscale a 1080p/4K
                                                          │
                                   [DaVinci Resolve (gratis)] ensamble,
                                   grade phosphor, overlays VT323, sync audio,
                                   export master continuo + cortes + loops
```

---

## 4 · Tratamiento por movimiento + mapeo audio→parámetros

Convención: video a **fps fijo** (12 o 15 fps base → interpolar a 24/30 con
RIFE). Cada feature de librosa se calcula con `hop_length = sr / fps` para que
**un valor de feature = un frame de video** (sincronía exacta). Pipeline de
extracción genérico:

```python
import librosa, numpy as np

SR_VIDEO_FPS = 15
y, sr = librosa.load("masters/01_outbound_master.wav", sr=None, mono=True)
hop = int(sr / SR_VIDEO_FPS)                       # 1 frame de feature = 1 frame de video

rms      = librosa.feature.rms(y=y, hop_length=hop)[0]                 # energía → fuerza/zoom
onset    = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)    # ataques → eventos/saltos
centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]  # brillo → color/cutoff
chroma   = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)      # tono → paleta/prompt
beats    = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)[1]      # pulso → cortes/pulsos

def norm(x):                                       # 0..1 robusto
    x = np.asarray(x, float); lo, hi = np.percentile(x, [5, 95])
    return np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)

def smooth(x, w=5):                                # evita jitter de 1 frame
    k = np.ones(w) / w; return np.convolve(x, k, mode="same")

# ejemplo de export a keyframes Deforum (zoom respira con RMS):
zoom = 1.0 + 0.05 * smooth(norm(rms))
kf_zoom = ", ".join(f"{i}:({v:.4f})" for i, v in enumerate(zoom))
```

### Tabla maestra de mapeo audio → parámetro

| Feature librosa | Qué del audio captura | Parámetro destino | Movimiento donde más pesa | Curva |
|---|---|---|---|---|
| **RMS (energía)** | el "cuerpo" / loudness | `zoom` (Deforum) · `strength`/denoise · peso de capa | Outbound (build), Crossing (densidad), Recursion (saturación) | suavizado, lineal |
| **onset_strength** | ataques / golpes / latido | salto de `translation` (jitter), trigger de prompt-switch, peak→transición (Yvann peak detection) | latido de Outbound; "tropezones con rocas" de Crossing | umbralizado (sólo picos) |
| **spectral_centroid** | brillo / agudo vs grave | color/`hue`, `cutoff` de un filtro de imagen, mezcla phosphor↔ámbar | inversión 24↔42 de Crossing | suavizado, mapeo a rampa de color |
| **chroma / croma** | clase de altura (acorde) | selección de prompt en `prompt_schedule`, paleta secundaria | cambios armónicos (R1 del composer: Dm→Bb→F→Am→Dm) | discreto (argmax → estado) |
| **beat_track** | pulso / tempo | cadence de cortes, pulso del hexagrama (scale 1.0→1.05) | latido 60 BPM de Outbound; 40 BPM "respiración" de Crossing | eventos discretos |
| **sub-band 42 Hz** (filtro pasa-banda 38–46 Hz) | la portadora subgrave del EP | `translation_z` lento (deriva hacia adentro/afuera) · vignette pulse | todo el EP (la "columna") | muy suavizado, casi DC |

Regla de cordura (hereda R8 del composer, traducida a video): **bed = poco
movimiento, evento = mucho**. El RMS del bed debe mover el zoom ±5% como
mucho; los onsets protagonistas pueden disparar saltos del 20–30%. Si todo se
mueve siempre, nada se siente — igual que "si todo tiene riser, ninguno cuesta"
(AP8).

---

### 4.1 Outbound (8:00) — *nacimiento · oscuridad · los latidos llaman · se despega*

**Qué se ve.** Negro absoluto (BG_DEEP `#060810`). El **primer latido**
(librosa onset del heart_pulse a 0:30) empuja desde el borde inferior la
primera línea de luz phosphor — la línea yang del hexagrama entrando por abajo
(§1.3). De a poco se arma una estructura wireframe (landscape Battlezone /
elipse Voyager). Cuando el track "se despega" (build de densidad ~3:00–6:00),
la estructura se desprende y la cámara **acelera hacia afuera** (`translation_z`
crece con el RMS). Climax: todas las capas, máxima velocidad. Fade: la
estructura se aleja, queda el punto.

**Técnica AI.** Deforum 3D (Ruta A) + ControlNet lineart sobre un init video de
shader (la geometría wireframe la ponemos nosotros). IPAdapter style ref = un
frame phosphor de `artwork/generated/01_hero_background/`. El latido maneja el
nacimiento de la luz; el RMS maneja la aceleración.

**Prompt scheduling (ejemplo, paleta línea A phosphor):**
```
0:    "absolute black void, single faint phosphor green line emerging from
       below, retro CRT terminal, vintage NASA telemetry, deep space,
       minimal, monochromatic green on black"
0:30: "a heartbeat of light from below pushing upward, wireframe horizon
       forming, Battlezone vector grid, phosphor green on cosmic black"
3:00: "wireframe landscape detaching and accelerating outward into deep
       space, vector grid receding, sense of departure and ascent,
       phosphor green, subtle warm amber highlight, CRT scanlines"
6:00: "everything rushing outward at maximum speed, dense vector field,
       cosmic loneliness, the moment of leaving, monochromatic phosphor"
7:00: "structure receding into a single distant point, fading to black void"
negative: photo, photorealistic, 3d render people, face, character, neon,
       cyan, magenta, synthwave, watermark, text, ornament, deformed
```

**Mapeo audio→param (Outbound):**
| Feature | Param | Efecto buscado |
|---|---|---|
| onset del heart_pulse (0:30–3:00) | `translation_y` (-) + pulso de brillo | el latido "empuja" la luz desde abajo (yang entra) |
| RMS global | `translation_z` + `zoom` | la aceleración del despegue |
| sub-42Hz | vignette pulse muy lento | la columna grave, casi imperceptible |
| centroid | mezcla phosphor→ámbar leve en el climax | el calor de Outbound (warm accent, raro) |

---

### 4.2 Crossing (13:00) — *nébulas · polvo de Saturno · tropezones con rocas · dificultad en el andar*

**Qué se ve.** Densidad creciente: **grano/polvo** que se acumula (textura
granular reactiva al RMS, coherente con la paleta Crossing del composer:
field-recording atmospheres). La cámara "**tropieza**": cada onset grave dispara
un jitter brusco de `translation`/`rotation` (la dificultad en el andar). En el
**centro exacto del tema** (la inversión de fase del lore, "desvío 24°"), la
imagen **se da vuelta** lentamente (rotación 180° + inversión de paleta
phosphor↔ámbar) — el 24↔42 girando, sin texto. Último ~20%: el **vestigio del
Voyager** (T13 radio_interference del composer) llega "de pedo" — un destello
de la estructura/paleta de Outbound emergiendo del ruido.

**Técnica AI.** Ruta B recomendada acá (ComfyUI + AnimateDiff o Wan 2.2 Restyle)
por la duración y por la necesidad de coherencia temporal en el grano. Yvann
peak-detection sobre la banda de bass dispara los "tropezones". ControlNet depth
sobre init video oscuro para mantener la profundidad de "nébula". IPAdapter ref
= frame painterly de `artwork/generated/01_hero_background_painterly/` (línea B,
paleta cósmica rica) — Crossing es el movimiento donde la línea B "vuela".

**Prompt scheduling (ejemplo, mezcla línea A/B):**
```
0:    "drifting through cosmic dust and faint nebula, dark depth, sub-bass
       weight, particles slowly accumulating, deep blacks, contemplative,
       painterly 70s sci-fi space art, Chris Foss, Don Davis NASA"
4:00: "denser dust field, ring particles of Saturn, the path becomes hard
       to traverse, occlusions drifting in, ritualistic cosmos, deep amber
       and phosphor"
6:30: "the image slowly inverting, palette flipping, the same place seen
       from the other side, threshold of phase, 24 degrees turn"   ← inversión
9:00: "deep dark traversal, weight, dust settling"
11:00:"a faint vestige of an earlier signal emerging from static, radio
       interference, a green wireframe ghost from the beginning, almost lost"
negative: [base] + clean, bright, cheerful, neon, face, character, watermark
```

**Mapeo audio→param (Crossing):**
| Feature | Param | Efecto buscado |
|---|---|---|
| RMS | densidad de grano/partículas + `strength` | nébula/polvo acumulándose |
| onset banda grave (Yvann bass weight) | jitter de `translation_x/y` + `rotation` | tropezones con rocas, dificultad |
| inversión de fase (marca de tiempo del compose, ~min 6:30/12) | rotación 180° + flip de paleta | 24↔42, el cruce central |
| vestigio Voyager (último 20%) | switch de IPAdapter ref → frame de Outbound + glitch | el eco que "llega de pedo" |
| heart 40 BPM | vignette/respiración lenta | la respiración del cruce |

---

### 4.3 Recursion (3:00) — *una vuelta · retorno · vinilo gastado que chicharrea · volver a nacer · spiral out*

**Qué se ve.** Lo más corto y lo más **denso/saturado**. El frame se llena
(drone que ocupa todo el espectro → imagen que ocupa todo el cuadro).
**Glitch/crackle visual** = el vinilo gastado (datamosh leve, crackle de grano,
dropouts — análogo visual del T13/T14 del composer, disintegration-loop estilo
Basinski aplicado a la imagen: cada "vuelta" pierde brillo y gana crackle). El
**eco de Outbound vuelve deformado** (mismo init de Outbound, una octava de
degradación visual: LPF de color, desaturación, ruido). Cierre: el **último
frame ES el primer frame de Outbound** → en loop infinito no hay corte (Fù
ejecutado).

**Técnica AI.** Ruta A o B. Lo clave acá no es el modelo sino el
**post**: el datamosh/crackle se hace mejor en DaVinci/glitch tools open-source
(`ffglitch`, datamosh por scripting) que pidiéndoselo a la AI. La AI genera la
base "saturada"; el post le mete el vinilo gastado.

**Mapeo audio→param (Recursion):**
| Feature | Param | Efecto buscado |
|---|---|---|
| RMS (creciente al drone total) | denoise/`strength` máximo + saturación de imagen | el drone que ocupa todo |
| crackle/glitch del audio (onset de alta densidad) | datamosh / crackle visual (post) | el vinilo gastado que chicharrea |
| eco del motivo Outbound (las mismas alturas 1 octava abajo) | re-inyección del init de Outbound + LPF de color | volver a nacer deformado |
| beat final que engancha | crossfade del último frame → primer frame de Outbound | spiral out, loop sin corte |

> **Voyager protegido (paralelo visual).** Igual que el motivo Voyager sonoro
> es intocable sin benchmark (`memory/voyager_protegido.md`), su
> representación visual (el destello que vuelve en Crossing/Recursion) debe ser
> **consistente entre los tres movimientos** — mismo init/IPAdapter ref. No
> reinventarlo por movimiento; es el ancla reconocible.

---

## 5 · Pipeline de producción

### 5.1 Estructura de entregables (Patrón 3 — el loop infinito es la decisión material)

```
docs/video/                         ← este plan + futuros storyboards por mov.
transmissions/01/video/             ← (a crear cuando se ejecute)
├── recipes/                        ← VERSIONADO (la "fuente", liviano)
│   ├── outbound.deforum.json       ← settings.json de Deforum
│   ├── crossing.comfy.json         ← workflow ComfyUI
│   ├── recursion.deforum.json
│   └── keyframes/                  ← series exportadas por librosa (csv/json)
├── init/                           ← init videos de shader (gitignore si pesan)
├── frames/                         ← PNG por movimiento (GITIGNORE, regenerable)
├── out/                            ← MP4 (GITIGNORE, regenerable)
│   ├── heliopause_master_24min.mp4 ← master continuo (3 movimientos)
│   ├── cuts/ 01_outbound.mp4 ...   ← cortes por tema
│   └── loops/ *_5s.mp4             ← loops cortos (Canvas/social)
└── scripts/ extract_keyframes.py   ← librosa → keyframes (VERSIONADO)
```

Misma política que `transmissions/`: **la receta se versiona (chica),
el MP4 se gitignorea (pesado, regenerable del WAV + recipe)**. El **master
continuo en loop infinito** (YouTube/Bandcamp) es la decisión material que
encarna la variable (el lore lo pide explícitamente).

### 5.2 Resolución / fps / upscale / interpolación

- **Generar barato, terminar lindo.** Generar a **512–768px y 12–15 fps**
  (rápido, menos VRAM, menos drift por frame), luego:
  - **RIFE VFI** (`ComfyUI-Frame-Interpolation`, rife47/rife49): interpola
    12→24 o 15→30 fps. Movimiento fluido sin re-generar (barato).
  - **Real-ESRGAN** (open): upscale ×2/×4 a 1080p o 4K.
- **Entregas:** master continuo 1920×1080 @24fps; loops Canvas 1080×1920 @24–30
  fps, < 8 s, < 8 MB (spec Spotify del brief `02_spotify_canvas.md`).

### 5.3 Cómo evitar flicker / drift (resumen operativo)

1. **Seed fijo** por movimiento (consistencia base).
2. **ControlNet** atado a init video → la estructura no flota.
3. **IPAdapter style ref** del proyecto → la paleta no deriva.
4. **AnimateDiff context windows / overlapping segments** (Ruta B) → segmentos
   solapados se mezclan = mejor coherencia temporal en clips largos (y menos
   VRAM por segmento).
5. **Cadence** en Deforum (generar 1 de cada N frames, interpolar el resto) →
   menos chance de flicker por frame.
6. **RIFE al final**, no antes (interpolar suaviza el micro-jitter restante).
7. **Grade unificado en DaVinci** (un solo LUT phosphor sobre todo) → cohesión
   final de color.

### 5.4 Montaje final (DaVinci Resolve, gratis)

Ensamble de los tres movimientos con crossfades (igual que el audio se ensambla
con crossfades — `task ep:assemble`), grade phosphor, **overlays de telemetría
VT323** (`TRANSMISSION 01`, `01 OUTBOUND 08:00`, `42HZ`, `SPIRAL/1`) compuestos
encima (NUNCA generados por AI), sync exacto con el WAV master, export del
master continuo + cortes + loops.

---

## 6 · Propuesta de prototipo (MVP)

### Recomendación: **primeros 60 segundos de Outbound.**

Por qué Outbound y por qué los primeros 60s:
- Es donde el **mapeo audio→imagen es más legible**: negro → primer latido →
  luz que entra por abajo → estructura. La relación causa-efecto (latido ⇒ pulso
  visual) se *ve* sin explicación. Demuestra la tesis en un minuto.
- Es **barato de computar**: 60s × 15 fps = 900 frames base (luego RIFE ×2 →
  1800). Factible en Colab Free T4 o en el Mac (Deforum SD1.5) en una corrida
  de noche.
- Ejercita **todas las piezas** del pipeline (librosa → keyframes → ControlNet
  → IPAdapter → frames → RIFE → grade → sync) en escala chica antes de comprometer
  cómputo en los 24 min.

### MVP mínimo demostrable

Un **MP4 de ~60s, 1080p @24fps**, donde:
1. el primer latido del track dispara visiblemente el nacimiento de la luz desde
   abajo, y
2. la imagen mantiene la paleta phosphor del proyecto sin derivar (prueba de que
   IPAdapter+ControlNet funcionan como correa).

Si esas dos cosas se cumplen, el sistema está validado y escala.

### Pasos concretos

1. **Lectura/storyboard** (sin máquina): escribir `docs/video/04_storyboard_
   outbound.md` — qué pasa por segundo en esos 60s, qué umbral se cruza cuándo.
2. **Extracción**: `scripts/extract_keyframes.py` sobre
   `release/masters/01_outbound_master.wav` → keyframes (RMS→zoom/z,
   heart-onset→translation_y/brillo, sub42→vignette). Validar las curvas en un
   plot antes de generar nada.
3. **Init video base** (hibridación): shader/Python de 60s con la línea de luz +
   wireframe naciente en phosphor sobre negro (crudo, es sólo la geometría).
4. **First frame**: generar con el pipeline ya validado (Draw Things/Diffusers,
   FLUX/SDXL, prompts de `13_visual_style_guide.md`) → el frame 0 phosphor.
5. **Generar**: Deforum (Ruta A) con seed fijo + ControlNet(init) +
   IPAdapter(first frame) + keyframes del paso 2. 512–768px, 12–15 fps.
6. **Terminar**: RIFE ×2 → Real-ESRGAN a 1080p → DaVinci (grade phosphor +
   overlay VT323 `01 OUTBOUND` + sync WAV) → export MP4.
7. **Revisión** contra los dos criterios del MVP + chequeo creative-direction
   (¿se ve el cruce de umbral? ¿derivó el estilo?). Iterar.
8. Si pasa → escalar a Outbound completo, luego Crossing/Recursion, luego master
   continuo + loops.

> **Realismo de cómputo.** No prometer 24 min audio-reactivos 4K en la primera
> tanda. 60s @1080p es el alcance honesto del primer sprint. El master continuo
> es el objetivo de varias corridas (idealmente con una GPU de consumo o Colab
> sostenido), no de una noche.

---

## 7 · Riesgos / gotchas + referencias

### Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| **Sopa AI / drift de estilo** | las 5 correas (§2.2): audio dirige, ControlNet, IPAdapter ref del proyecto, first-frame restyle, paleta+negative cerrados. |
| **Túnel fractal Deforum genérico** | `strength` controlado + ControlNet atado a geometría + init video de shader (no dejar la cámara al azar). |
| **Flicker entre frames** | seed fijo, cadence, AnimateDiff context windows, RIFE al final, grade unificado (§5.3). |
| **Mac sin MPS para Wan/LTX** (enero 2026) | Ruta A (Deforum) local en Mac; Ruta B (Wan/LTX) en Colab Free / GPU prestada (§3.2). |
| **Texto inventado por la AI** | NUNCA pedir texto a la AI; overlays VT323 reales en post (regla heredada del artwork). |
| **Caras donde no debe** (FLUX/SDXL tell) | negative prompt del proyecto + reroll; lore prohíbe caras igual. |
| **Cómputo subestimado** | generar barato (512–768px, 12–15 fps) + upscale/interpolación; prototipo de 60s antes de comprometerse a 24 min. |
| **Reverb/efectos de imagen que "amplifican"** | igual que el bug de reverb decay del audio (`memory/aem_effects_reverb_bug.md`): clampear rangos de los parámetros reactivos (zoom ±5% bed, no dejar `strength` libre). |
| **Voyager visual inconsistente** | mismo init/IPAdapter ref del Voyager en los 3 movimientos; tratarlo como el motivo protegido que es. |

### Referencias (links)

**Audio-reactividad / Deforum**
- Audio Keyframe Generator (Colab, fzantalis): https://colab.research.google.com/github/fzantalis/colab_collection/blob/master/Audio_Keyframe_Generator_For_Deforum_Stable_Diffusion.ipynb
- `nicolai256/audio_keyframe_deforum_DD_0.5`: https://github.com/nicolai256/audio_keyframe_deforum_DD_0.5
- `kessoning/Audio-Offline-Analysis` (beat detection): https://github.com/kessoning/Audio-Offline-Analysis
- Deforum tools (kacia): https://kacia.com/tools-for-deforum-extension-for-automatic1111-stable-diffusion/

**ComfyUI audio-reactivo + coherencia**
- `ryanontheinside/ComfyUI_RyanOnTheInside`: https://github.com/ryanontheinside/ComfyUI_RyanOnTheInside
- `yvann-ba/ComfyUI_Yvann-Nodes`: https://github.com/yvann-ba/ComfyUI_Yvann-Nodes
- `Kosinkadink/ComfyUI-AnimateDiff-Evolved`: https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
- Audioreactive AnimateDiff workflow (Civitai): https://civitai.com/articles/3923/audioreactive-animatediff-animations-in-comfyui-kaciaai-workflow

**Modelos de video open-source 2026**
- Comparativa LTX-2 / Wan 2.2 / HunyuanVideo: https://www.aimagicx.com/blog/open-source-ai-video-models-comparison-2026
- VRAM por modelo (WillItRunAI): https://willitrunai.com/blog/video-generation-gpu-guide-2026
- LTX-Video system requirements: https://docs.ltx.video/open-source-model/getting-started/system-requirements
- Wan 2.2 Video Restyle (first-frame, anti-drift): https://www.runcomfy.com/comfyui-workflows/wan2-2-first-frame-restyle-comfyui-video-generation
- LTX 2.3 vs Wan 2.2 (2026): https://wavespeed.ai/blog/posts/ltx-2-3-vs-wan-2-2-comparison-2026/

**Interpolación / upscale**
- `Fannovel16/ComfyUI-Frame-Interpolation` (RIFE VFI): https://github.com/Fannovel16/ComfyUI-Frame-Interpolation
- Workflow RIFE + upscaling: https://comfyui.org/en/boost-video-creation-with-rife-upsampling

**Audio features**
- librosa feature extraction: https://librosa.org/doc/main/feature.html
- librosa RMS: https://librosa.org/doc/main/generated/librosa.feature.rms.html

**Mac / Colab**
- ComfyUI LTXVideo MPS issue (Mac): https://github.com/Lightricks/ComfyUI-LTXVideo/issues/302
- ComfyUI en M3 MacBook Pro: https://comfyui.org/en/install-comfyui-on-m3-macbook-pro
- LTX-Video en M3/M4 (HF discussion): https://huggingface.co/Lightricks/LTX-Video/discussions/26

---

## Apéndice — coherencia con el resto del repo

- **Estética**: respeta `docs/13_visual_style_guide.md` y `14_design_system.md`
  (paleta phosphor, VT323, líneas A/B). Reusa el pipeline de imagen ya
  implementado (`task gen:artwork`, briefs en `artwork/generation_briefs/`).
- **Lore**: respeta lo prohibido (`03_lore.md`): sin caras, sin
  astronautas/planetas obvios, sin espiral ilustrada literal; el loop infinito
  como performance del concepto.
- **Composición**: las reglas del `aem-composer` se reflejan en el mapeo (bed
  poco movimiento / evento mucho; el Voyager protegido también en lo visual).
- **Política de archivos**: receta versionada, MP4 gitignoreado y regenerable —
  como los WAV.
