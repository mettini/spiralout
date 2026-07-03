# Videoclips Heliopause / Transmission 01 — Dirección creativa + bajada técnica

> **Approach**: pipeline Python + shader con arquitectura *control track*.
> Python+librosa analiza el WAV → emite un *control track* (parámetros por
> frame) → ese control maneja un renderer de shaders GLSL (moderngl headless)
> → ffmpeg muxea el audio. Análisis (Python) y render (GLSL) quedan separados.
>
> **Estado**: documento de planificación. NO hay código todavía.
> **Alcance del prototipo**: animar los primeros minutos de UN movimiento, no
> los 24:00.

Doc maestro de la capa video del proyecto. Hereda toda la identidad de
`docs/13_visual_style_guide.md` y `docs/14_design_system.md` (phosphor verde,
VT323, hexagrama 24, anti-ilustración). No la reemplaza: la pone en movimiento.

---

## 0 — TL;DR para el que tiene 30 segundos

- **Variable única**: *el retorno como deriva, no como destino* (hexagrama 24
  · Fù). Todo lo visual obedece a una sola ley: nada llega, todo vuelve más
  afuera. Una espiral logarítmica que nunca cierra.
- **Materia prima compartida**, no ilustración: el video se construye con los
  **mismos features matemáticos del WAV** (RMS, onsets, centroide, chroma,
  sub-42Hz) que ya son el ADN del audio sintetizado en NumPy. El video no
  "dibuja" la música: corre sobre su misma data. No puede existir sin el audio.
- **Lenguaje**: campo de partículas GPGPU sobre flow field de curl-noise +
  raymarching volumétrico de nébula + feedback buffer para la recursión.
  Todo en phosphor verde sobre negro, grano CRT, telemetría VT323 encima.
- **Recomendación de prototipo**: **todo *Recursion* (3:00 completo)** — es el
  movimiento más corto, el que mejor demuestra el feedback buffer (el efecto
  más "wow" y más conceptual: la imagen comiéndose a sí misma = la espiral),
  y cierra el loop con *Outbound*. MVP demostrable en una sola corrida.

---

## 1 — Dirección creativa abstracta

### 1.1 La variable única (Patrón 1)

**El retorno como deriva.** No es "el espacio". No es "una sonda". Es **una
sola operación abstracta**: algo se aleja, la trayectoria se curva sola (sin
decisión, sin catástrofe — *el movimiento es natural*, dice el hexagrama 24),
y vuelve a un origen que ya se corrió de lugar. La espiral logarítmica: cada
vuelta más afuera y más adentro, nunca el mismo punto.

Esta variable es la ley que filtra cada decisión visual:

- **¿Una explosión, un climax que "resuelve"?** → descartado. La espiral no
  resuelve, itera. No hay clímax vertical, hay deriva.
- **¿Una imagen que cierra (un círculo, un planeta entero, una figura
  completa)?** → descartado. *Tres es el número mínimo para que haya espiral.
  Cuatro ya es figura cerrada.* Todo queda abierto.
- **¿Algo se mueve en línea recta a un destino?** → descartado. El movimiento
  base siempre es curvo, orbital, en deriva.

Si una decisión visual no sirve a *el retorno como deriva*, se cae.

### 1.2 Materia prima compartida, no ilustración (Patrón 2)

La prueba de Romagosa: *"¿podría existir el visual sin escuchar el disco?"*
Si sí, está ilustrando. Acá la respuesta es **no**, por construcción:

- El audio del EP **ya es matemática NumPy/SciPy** — las mismas librerías que
  en el CERN miden colisiones (`docs/07_vision.md`). Cada nota es una operación.
- El video toma **esa misma señal** y extrae sus features (energía, transientes,
  centroide, chroma, sub-bass). Esos features *son* los parámetros que mueven
  cada partícula y cada uniform del shader.
- No hay un artista interpretando "cómo se vería" la música. Hay una **lectura
  de la misma data** que generó el sonido, proyectada a luz. El cordón
  umbilical código↔ciencia↔música (`07_vision.md`) ahora también es código↔luz.

Esto es lo opuesto a un "visualizer de barras de ecualizador". El mapeo es
**musical, no literal** (ver §4): un onset no enciende una barra — perturba un
flow field; el centroide espectral no dibuja un espectrograma — sube la altitud
de la nébula y enfría/calienta el verde.

### 1.3 Decisión material como decisión conceptual (Patrón 3)

El "soporte físico" del video es su **forma de circular y de generarse**:

- **Master continuo de 24:00 + loop infinito.** El cierre de *Recursion*
  engancha armónicamente con la apertura de *Outbound* (`02_cosmologia.md` §V).
  El video se entrega también como **loop sin corte** — en YouTube/Bandcamp es
  performance del concepto: *Heliopause loopea, vos también*. La decisión de
  publicarlo loopeable ES la variable única hecha soporte.
- **Generativo y reproducible** = el video se regenera del script, igual que los
  WAV se regeneran de `compose_*.py`. El mp4 va gitignored; el `render_*.py` +
  el control track + los `.glsl` se commitean. **El medio es el mensaje**
  (McLuhan, literal — `07_vision.md`): el video se *transmite* desde código,
  no se *edita* a mano en un timeline. Coherente con la filosofía del repo.
- **Imperfección como firma** (`07_vision.md` §"el foco no es la calidad
  sonora"): el grano CRT, el aliasing de pixel, el phosphor que satura no son
  acabado — son el "monitor de phosphor verde que tiene 30 años en el rack"
  (`13_visual_style_guide.md`). Lo táctil del video es ese ruido deliberado.

### 1.4 Inversión de tropos del género (Patrón 5)

Tropos heredados del visual de música espacial / ambient / dark ambient:

1. Galaxias y nébulas fotorrealistas tipo Hubble → **INVERTIDO**: la nébula es
   un campo de densidad raymarcheado en *un solo verde phosphor*, sin color
   astronómico. Ciencia de telemetría, no postal de la NASA.
2. Astronautas, planetas, naves visibles → **IGNORADO** (lo prohíbe el lore,
   `03_lore.md`): cero figurativo, cero personajes.
3. Visualizer de espectro / waveform / barras → **CITADO AL REVÉS**: sí hay
   data de audio en pantalla, pero como **telemetría VT323** (números, labels
   `SIGNAL ACTIVE`, `42HZ`, `SPIRAL / 1`), no como gráfico de EQ. El dato es
   contenido del lore, no decoración (regla de oro del style guide).
4. Synthwave neón cyan/magenta (el default de "música + espacio" en 2026) →
   **PROHIBIDO** explícitamente (`13_visual_style_guide.md`). Solo phosphor.
5. Espiral dibujada literal → **PROHIBIDO** (`03_lore.md`: *la espiral nunca se
   ilustra de manera obvia*). La espiral está en la **trayectoria de las
   partículas y en la deriva de la cámara**, no en un trazo dibujado.

La firma autoral es la inversión 1+4: la cosa más obvia (nébula colorida neón)
se vuelve su opuesto (campo de densidad monocromo de fósforo).

### 1.5 Lectura antes que Pinterest (Patrón 7)

El sistema de pensamiento ya existe y está documentado — **esto no arranca de
un mood board**, arranca de textos:

- **I Ching, hexagrama 24 (復 Fù)** — la carta fundacional (`02_cosmologia.md`
  §I). *El movimiento es natural, surge espontáneamente.* La deriva de cámara
  y de partículas tiene que sentirse **sin esfuerzo**, nunca cinética/agresiva.
- El **expediente HP-01** (`10_cuento.md`) — la estructura narrativa por
  movimiento (ficha de recepción, las tres transmisiones, las anotaciones al
  margen). De acá salen los overlays de texto VT323.
- La **cosmología** (`02_cosmologia.md`) — nacimiento/vida/vuelta, el latido,
  el 24↔42. Subtexto, nunca enunciado.

Pinterest/referencias visuales entran como confirmador (§7), no como generador.

### 1.6 Hilo conductor de los 24:00 — mapeo a los 3 movimientos

Un solo organismo visual que muta. **No** tres videos pegados: una sola escena
GLSL cuyos parámetros derivan de control track, atravesando tres estados.

```
                    OUTBOUND (8:00)        CROSSING (13:00)         RECURSION (3:00)
                    nacimiento/despegue    el viaje/el espesor      la vuelta/el retorno
densidad visual     vacío → primer pulso   máxima, polvo y rocas    colapso → feedback → loop
cámara              deriva lenta saliendo  atraviesa el medio       se pliega sobre sí misma
partículas          pocas, naciendo del    río de polvo en flow     se reabsorben al centro,
                    centro (latido)        field, "tropezones"      ecos de Outbound deformados
nébula (raymarch)   apenas insinuada       densa, domain warping    se satura hasta ocupar todo
color               phosphor naciente,     phosphor pleno + dim,    phosphor degradándose,
                    casi negro             un toque amber raro       glitch, signal_red al borde
feedback buffer     off                    leve (estela)            ON, protagonista
overlay VT323       "FICHA 00 / 21:17:42"  "FICHA 02 / 24°"         "FICHA CIERRE / loop"
hexagrama 24        ausente                aparece tenue al cruce    pleno al cerrar el loop
```

El **minuto 24:00 del EP no existe** (el EP dura 24:00), pero **el cruce — el
centro exacto de *Crossing*, la inversión de fase a 24° (`10_cuento.md` FICHA
02)** — es el punto donde la cámara y el flow field invierten su sentido de
deriva. Es el evento visual más importante de los 24 minutos: no es un climax,
es una *vuelta* (la órbita que se parte). El hexagrama 24 (5 yin + 1 yang
entrando por abajo) puede materializarse exactamente ahí, un solo frame,
"la luz que entra otra vez por la grieta donde antes había salido".

### 1.7 Chequeo creative-direction — resumen

| Patrón | Estado | Nota |
|---|---|---|
| 1 · Variable única | ✓ | *El retorno como deriva*. Nombrable en 3 palabras. |
| 2 · Materia prima compartida | ✓✓ | El video corre sobre los mismos features que generaron el audio. No ilustra. |
| 3 · Decisión material = conceptual | ✓ | Loop infinito + generativo-reproducible + grano CRT como firma. |
| 4 · Doble rol artista/traductor | ○ | El usuario es artista (brief, imágenes); este pipeline es la *traductora* que materializa. Ver §6 — separar sesión de "elegir mood" de sesión de "tunear control track". |
| 5 · Inversión de tropos | ✓ | Nébula monocroma de fósforo (no Hubble), telemetría (no EQ bars), prohibido neón/synthwave. |
| 6 · Equipo estable | ○ | El "colaborador estable" acá es el **pipeline mismo** + la skill creative-direction como segunda lectura recurrente. Si entra un humano (motion designer), comprometerlo a los 3 movimientos, no a uno. |
| 7 · Lectura antes que Pinterest | ✓✓ | Arranca del I Ching + cosmología + cuento, ya documentados. |

Observación clave: el approach Python+shader **es** el Patrón 2 llevado al
extremo — no hay traducción "interpretativa" entre sonido y visual, hay
**identidad de materia prima**. Eso es lo que ningún visualizer comercial puede
copiar, porque el audio de este EP se generó en el mismo lenguaje (NumPy) del
que sale el control track. La firma es estructural, no estética.

---

## 2 — Por qué Python + shader sirve a ESTA música/concepto

1. **Misma materia prima (Patrón 2 estructural).** El audio se sintetizó en
   NumPy/SciPy; el control track se extrae en librosa (que es NumPy por
   debajo). El video literalmente comparte el linaje científico del audio
   (`07_vision.md` §NumPy/SciPy). Un After Effects o un Resolve romperían esa
   coherencia: serían "edición a mano", no transmisión desde código.

2. **Reproducibilidad = filosofía del repo.** `compose_*.py` → WAV;
   `render_*.py` + control track → mp4. El mp4 es pesado y se gitignora; la
   fuente (script + `.glsl` + control `.npz/.json`) es chica y se commitea.
   Encaja 1:1 con la política de `transmissions/CLAUDE.md` (no commitear WAVs;
   regenerar).

3. **Separación de capas (mandato del repo + buena ingeniería).** Análisis de
   audio (Python, lento, una vez) vs render (GLSL, GPU, por frame). Se puede
   re-tunear el look (shaders) sin re-analizar el audio, y viceversa. El control
   track es el contrato entre las dos capas — como `index.json` es el contrato
   entre render y player.

4. **Lo musical, no lo literal.** Mapear features → uniforms con envelope
   followers (suavizado) da movimiento *orgánico* (Eno/Roach: paciencia,
   respiración), no nervioso. Un visualizer de FFT crudo sería exactamente el
   tropo que invertimos (§1.4).

5. **El feedback buffer ES la recursión.** Técnicamente, un ping-pong de
   framebuffers donde el frame N se alimenta del frame N-1 desplazado/rotado
   *es* una recursión visual: `f(x) = transform(f(x-1))`. Es el equivalente
   exacto en GLSL de la recursión de Python que el lore celebra (`07_vision.md`:
   `def transmit(n): return transmit(n+1)`). El concepto se ejecuta en el medio,
   no se ilustra.

6. **Gratis y local.** Todo corre en el Mac del usuario (Apple Silicon, Metal vía
   OpenGL/moderngl), sin nube, sin suscripción, sin cuenta. Coherente con la
   restricción dura del proyecto.

---

## 3 — Stack técnico (PRO y 100% gratis / open-source)

Todo Python 3.10+ (target del repo, `Taskfile.yml`). Capas:

### Capa A — Análisis de audio → control track

| Lib | Versión | Rol | Licencia |
|---|---|---|---|
| **librosa** | ≥ 0.11 | RMS, onset_strength/onset_detect, spectral_centroid, chroma_cqt, bandas | ISC |
| **numpy** | (ya en repo) | base; el control track es un array | BSD |
| **scipy** | (ya en repo) | filtrado de bandas (sub-42Hz, air), suavizado Savitzky-Golay | BSD |
| **soundfile** | (en `install:release`) | leer el WAV master | BSD |

Salida: **control track** = `control.npz` (arrays float32 por frame, a fps de
video) + un `control_meta.json` (fps, nombres de canales, rangos de
normalización). Un array `(n_frames, n_channels)`. Canales propuestos:

```
rms          energía global              → escala global / brillo del bed
rms_sub42    energía banda 30-55 Hz      → "presión", latido, tamaño de partículas
rms_low      energía 55-250 Hz           → empuje del flow field
rms_air      energía 4-10 kHz            → grano/destello fino, polvo
onset_env    fuerza de transiente        → perturbación del flow field
onset_flag   1.0 en el frame del onset   → disparo de eventos puntuales ("rocas")
centroid     centroide espectral norm.   → altitud/temperatura del color, altura nébula
chroma_root  nota dominante (0-11)       → tinte fino del phosphor (sutil, no arcoíris)
flux         spectral flux               → turbulencia del curl-noise
section      id de movimiento (0/1/2)    → preset de escena (Outbound/Crossing/Recursion)
phase_inv    rampa 0→1 alrededor del cruce → inversión de deriva (el evento de §1.6)
```

> Nota anti-fritura (memory): el audio del EP tiene reglas espectrales propias
> (`memory/pattern_noise_fritura.md`), pero **acá librosa solo LEE el WAV
> masterizado** — no genera audio. No hay riesgo de los antipatrones de síntesis.

### Capa B — Render de shaders (GLSL) headless

| Lib | Versión | Rol | Licencia |
|---|---|---|---|
| **moderngl** | ≥ 5.12 | contexto OpenGL **standalone/headless** (`create_standalone_context`), FBOs, ping-pong, render a textura | MIT |
| **moderngl-window** | (opcional) | solo para preview interactivo en dev; no para el render final | MIT |
| **numpy** | — | sube uniforms/arrays de partículas a la GPU | BSD |
| **Pillow** | — | (opcional) volcado de frames PNG para debug | HPND |

- Render **offline/headless**: `moderngl.create_standalone_context()` → no
  necesita ventana ni display server. Cada frame se rinde a un FBO (textura),
  se lee con `fbo.read()` y se pipea a ffmpeg. OpenGL 3.3+ (Apple Silicon lo
  soporta vía su driver GL).
- **GPGPU de partículas** sin compute shaders (macOS GL tope 4.1, sin compute):
  usar **transform-feedback** o el patrón **ping-pong de texturas** — posición
  de cada partícula guardada en los canales RGBA de un pixel de una textura de
  estado; un fragment shader actualiza posiciones leyendo la textura N y
  escribiendo la N+1 (nunca read+write a la misma → evita race conditions).
- **Feedback buffer** (recursión): mismo patrón ping-pong a resolución de
  pantalla — el frame N samplea el N-1 con un leve warp/zoom/rotación + decay.

GLSL como archivos `.glsl` versionados (vertex + fragment + el "sim" de
partículas + el "feedback"), cargados por el runner Python.

### Capa C — Encode / mux

| Lib | Rol | Licencia |
|---|---|---|
| **ffmpeg** (binario, ya implícito en stack release) | recibe frames raw por stdin (`rawvideo`), encodea, **muxea el WAV master** | LGPL/GPL |
| **moviepy** | ≥ 2.x — opcional, wrapper cómodo para mux audio+video y para los cortes | MIT |

- Camino recomendado para el master: **pipe directo a ffmpeg** (más rápido y
  control total de codec) — frames raw RGB por stdin + `-i master.wav`.
- `moviepy` para conveniencia en cortes/loops si se prefiere API en Python.
- Codecs (ver §5).

### Cómo se conectan (contrato entre capas)

```
master.wav ──► [A: analyze.py / librosa] ──► control.npz + control_meta.json
                                                     │
                                                     ▼
                              [B: render.py / moderngl headless]
                              lee control.npz, por cada frame:
                                · setea uniforms desde el control track
                                · corre sim de partículas (ping-pong)
                                · raymarchea nébula
                                · aplica feedback buffer
                                · compone overlay VT323
                                · fbo.read() → bytes RGB
                                     │
                                     ▼ (stdin rawvideo)
                              [C: ffmpeg] + master.wav ──► heliopause.mp4
```

Modular, single-responsibility: `analyze.py` no sabe de GLSL; `render.py` no
sabe de librosa (solo lee el control track); el shading vive en `.glsl`.

### Ubicación propuesta en el repo

```
transmissions/01/video/
├── analyze.py            Capa A — WAV → control.npz (commit)
├── render.py             Capa B — control + glsl → frames (commit)
├── encode.py             Capa C — frames → mp4 (commit)
├── shaders/
│   ├── quad.vert         vertex trivial fullscreen quad (commit)
│   ├── particles_sim.frag  update de partículas ping-pong (commit)
│   ├── scene.frag        raymarch nébula + draw partículas (commit)
│   └── feedback.frag     ping-pong de pantalla, recursión (commit)
├── control/              control.npz + meta (GITIGNORED — regenerable)
├── out/                  mp4 + cortes + loops (GITIGNORED — regenerable)
└── README.md            cómo correr el pipeline (commit)
```

Tasks nuevas a sumar al `Taskfile.yml` (mismo patrón `TX`):
`task video:analyze`, `task video:render`, `task video:encode`,
`task video:all`, `task video:loops`.

---

## 4 — Tratamiento por movimiento (qué se ve · técnica · mapeo audio→visual)

Principio de mapeo (research): **envelope followers + smoothing**, nunca el
feature crudo. Cada uniform es el feature pasado por un low-pass (attack/release
distintos según si es "pulso" o "tendencia"). `onset_flag` es la única señal
binaria (1.0 un solo frame) para disparos sharp. Esto es lo que separa "musical"
de "barras de EQ".

### 4.1 OUTBOUND (8:00) — nacimiento / despegue / oscuridad / los latidos llaman

**Qué se ve.** Negro casi total. Del centro nace un pulso — el latido a 60 BPM
(`02_cosmologia.md` §III): una expansión radial de fósforo tenue, sincronizada
al heartbeat del track. Pocas partículas, naciendo del centro, derivando hacia
afuera muy lento (la cápsula que acelera a un límite no elegido). La cámara se
aleja del centro con deriva sin esfuerzo. Nébula apenas insinuada en los bordes.

**Técnica de shader.** Particle system GPGPU emisor radial desde el origen +
flow field de curl-noise muy suave (laminar, casi sin turbulencia). Glow radial
por el latido (additive blend de fósforo). Sin feedback. Sin nébula densa.

| feature (canal) | uniform | efecto visual | follower |
|---|---|---|---|
| `rms_sub42` | `u_pulse` | radio + brillo del glow central (el latido) | attack rápido, release medio |
| `rms` | `u_globalGain` | brillo general del bed | release lento (respira) |
| `onset_flag` | `u_emit` | emite un burst de partículas nuevas | binario 1-frame |
| `centroid` | `u_colorTemp` | phosphor más frío (dim) cuando es grave | release lento |
| `rms_low` | `u_drift` | velocidad de deriva hacia afuera | medio |

### 4.2 CROSSING (13:00) — el viaje / nébulas / polvo de Saturno / tropezones con rocas

**Qué se ve.** El medio se vuelve denso. Río de polvo: miles de partículas
arrastradas por un flow field turbulento (el polvo de los anillos). Nébula
raymarcheada con domain warping ocupa el cuadro, en capas de fósforo + dim. Los
"tropezones con rocas" = transientes/onsets que **perturban el flow field**
(remolinos puntuales) y disparan destellos breves — la dificultad en el andar.
En el **centro exacto** (cruce, FICHA 02, 24° — §1.6): la deriva del flow field
y de la cámara **se invierte** sin corte; el hexagrama 24 destella un instante.

**Técnica de shader.** Curl-noise flow field con turbulencia modulada por
`flux`. Raymarching volumétrico de la nébula: densidad por FBM + domain warping
(la técnica de Quílez/Heckel del research) — *wisps* y pliegues, no esferas
limpias. Feedback buffer leve (estela de las partículas). Cuidado: monocromo
phosphor, **no** color astronómico (inversión de tropo §1.4).

| feature (canal) | uniform | efecto visual | follower |
|---|---|---|---|
| `flux` | `u_turbulence` | fuerza del curl-noise (cuán revuelto el polvo) | medio |
| `onset_flag` + `onset_env` | `u_impact` / `u_impactPos` | "roca": remolino + destello puntual | binario + envelope |
| `centroid` | `u_nebulaHeight` | altura/altitud de la masa de nébula | release lento |
| `rms_low` | `u_flowSpeed` | velocidad del río de polvo | medio |
| `rms_air` | `u_grain` | densidad del grano fino / polvo brillante | rápido |
| `chroma_root` | `u_tint` | micro-tinte del phosphor (muy sutil) | lento |
| `phase_inv` | `u_invert` | rampa que invierte el sentido de deriva en el cruce | rampa lenta |

### 4.3 RECURSION (3:00) — la vuelta / vinilo gastado que chicharrea / volver a nacer / spiral out

**Qué se ve.** El drone crece hasta ocupar todo el espectro → la imagen se
**satura de sí misma**: el feedback buffer toma protagonismo, cada frame se come
al anterior con un leve zoom+rotación (espiral). Las partículas se **reabsorben
al centro** (retorno al origen). Aparecen ecos deformados de *Outbound* — el
mismo pulso radial, una octava abajo, distorsionado (recall visual del motivo).
El "vinilo que chicharrea" = grano/glitch CRT intenso, `signal_red` asomando al
borde una sola vez. Al final, el frame queda **enganchado armónicamente con la
apertura de Outbound** → loop infinito sin corte. El hexagrama 24 pleno.

**Técnica de shader.** **Feedback buffer** como técnica central: ping-pong a
resolución de pantalla, frame N = sample(frame N-1, warp = zoom·rotación
espiral) · decay + nuevo aporte. Eso es la recursión `f(x)=transform(f(x-1))`
hecha shader. Glitch/grain procedural fuerte (líneas, dropouts tipo vinilo).
Partículas con flow field invertido (hacia el centro).

| feature (canal) | uniform | efecto visual | follower |
|---|---|---|---|
| `rms` | `u_feedbackGain` | cuánto del frame anterior sobrevive (saturación) | release MUY lento (crece y crece) |
| `rms_sub42` | `u_spiralZoom` | zoom+rotación del warp del feedback (la espiral) | lento |
| `flux` | `u_glitch` | intensidad del glitch/chicharreo del vinilo | rápido |
| `onset_flag` | `u_dropout` | dropout puntual tipo salto de púa | binario |
| `centroid` | `u_decay` | qué tan rápido se desvanece la estela | medio |
| `phase_inv`/end-ramp | `u_collapse` | reabsorción de partículas al centro + cierre loop | rampa |

> El cierre de *Recursion* debe quedar **visualmente** idéntico (mismo encuadre,
> mismo glow naciente) que el frame 0 de *Outbound*, para que el loop infinito
> no tenga costura — espejo del enganche armónico del audio.

---

## 5 — Pipeline de producción (master, cortes, loops)

### Resolución / fps / codec

| Entrega | Resolución | fps | Codec / contenedor | Uso |
|---|---|---|---|---|
| **Master continuo** (24:00) | 1920×1080 (16:9) | 30 | H.264 high, CRF 16-18, yuv420p, +faststart / mp4 | YouTube, archivo, loop |
| **Master HQ (archivo)** | 1920×1080 | 30 | ProRes 422 o H.264 CRF 12 / mov-mp4 | backup calidad, regrade |
| **Corte por tema** (3 mp4) | 1920×1080 | 30 | H.264 CRF 18 / mp4 | upload por track, singles |
| **Loop corto** (3-8s) | 1080×1920 (9:16) | 30 | H.264 CRF 18 / mp4, **sin audio o muteable** | Spotify Canvas, IG Reels/Story |
| **Loop cuadrado** (3-6s) | 1080×1080 (1:1) | 30 | H.264 / mp4 | post IG feed, Bandcamp |

- **fps 30** (no 60): la estética es deriva lenta + CRT; 30 refuerza el "monitor
  viejo" y ahorra mitad de render. 24 también válido (cine) — decidir en proto.
- **1080p** alcanza y sobra (la materia es grano + fósforo, no detalle fino);
  4K cuadruplica el costo de render sin ganancia perceptible en este look.
- Aspect ratios respetan el design system (`14_design_system.md`): 16:9 master,
  9:16 Canvas, 1:1 social.

### Cómo se rinde cada cosa

1. **Master continuo.** `task video:analyze` sobre
   `release/masters/00_heliopause_continuous.wav` (el EP encadenado) → un solo
   `control.npz` con el canal `section` marcando los tres movimientos por
   timestamp (Outbound 0-8:00, Crossing 8:00-21:00, Recursion 21:00-24:00).
   `task video:render` corre los 24min × 30fps = 43.200 frames → ffmpeg + WAV.
   Una sola escena GLSL que muta por presets de `section`.

2. **Cortes por tema.** Dos caminos: (a) re-analizar/re-render el WAV por track
   (`01_outbound_master.wav`, etc.) — más limpio; o (b) recortar el master con
   ffmpeg `-ss/-to` sin re-encodear (`-c copy`) — instantáneo. Recomiendo (b)
   para los cortes "single" y (a) solo si se quiere un encuadre distinto.

3. **Loops cortos (3-8s).** Elegir un segmento "rico pero loopeable" (ej. un
   tramo de deriva estable de Crossing, o el colapso espiral de Recursion).
   Render dedicado en 9:16 / 1:1 con la cámara compuesta para vertical
   (elementos clave en mitad superior — regla Canvas del style guide). Loop
   perfecto: rampa de `u_*` que vuelve al estado inicial al final del clip
   (o cross-dissolve de los últimos N frames con los primeros). Spotify Canvas:
   3-8s, sin texto pegado a UI de play (zona inferior libre).

### Reproducibilidad / git

- **Commit**: `analyze.py`, `render.py`, `encode.py`, `shaders/*.glsl`,
  `video/README.md`. Y el `control_meta.json` si es chico.
- **Gitignore**: `control/*.npz`, `out/*.mp4`, frames intermedios. Regenerables.
- Sumar las reglas al `transmissions/.gitignore` y documentar en
  `transmissions/CLAUDE.md` (sección artwork/video).

---

## 6 — Propuesta de prototipo (MVP)

### Recomendación: **Recursion completo (3:00)**

Por qué Recursion y no los primeros 60-90s de Outbound:

- **Demuestra la técnica más conceptual y más vistosa** — el feedback buffer
  (la imagen comiéndose a sí misma = la espiral = `f(x)=transform(f(x-1))`).
  Es el "wow" y a la vez la prueba de que el concepto se *ejecuta*, no se
  ilustra. Outbound (negro + pocas partículas) es bello pero menos demostrable
  como proof-of-pipeline.
- **Es corto (3:00)** → un solo render barato, iteración rápida.
- **Cierra el loop** con Outbound → permite probar el deliverable estrella
  (loop infinito sin costura) ya en el MVP.
- Toca **las tres técnicas núcleo** en un solo tema: partículas (reabsorción),
  algo de nébula (saturación) y feedback (protagonista). Si Recursion sale, el
  pipeline está validado para los otros dos.

> Alternativa más conservadora: **primeros 90s de Outbound** — más simple
> (sin feedback), valida antes la cadena A→B→C con menos riesgo de shader.
> Si el objetivo es "que ande la tubería YA", empezar por Outbound 90s; si es
> "mostrar de qué es capaz esto", Recursion. **Recomiendo Recursion** porque
> el feedback buffer es justamente lo que justifica todo el approach.

### MVP mínimo demostrable

Un mp4 de 3:00 (1920×1080, 30fps, H.264) de *Recursion* donde:

1. El audio del master de Recursion está muxeado y sincronizado.
2. El feedback buffer reacciona a `rms` (la saturación crece con el drone).
3. Las partículas se reabsorben al centro hacia el final.
4. Hay grano/glitch CRT reaccionando a `flux` (el chicharreo del vinilo).
5. Overlay VT323 mínimo: `FICHA DE CIERRE` + `SPIRAL / 1` (del lore/style guide).
6. El último frame ≈ un frame de apertura de Outbound (prueba de loop).

Eso ya prueba A (control track), B (los 3 shaders núcleo), C (mux) y la
identidad visual. Lo demás (afinar curvas, nébula bonita, los otros 2 temas)
es iteración.

### Pasos concretos para ejecutarlo (cuando se dé "go" para codear)

1. **Scaffold** `transmissions/01/video/` + tasks `video:*` en Taskfile +
   reglas .gitignore. Dependencias: `pip install librosa moderngl moviepy`
   (sumar a `install:release` o un `install:video`).
2. **Capa A — `analyze.py`**: leer `recursion_master.wav`, extraer los canales
   de §3 a 30fps, normalizar, escribir `control.npz` + meta. Verificar plots
   rápidos (matplotlib, debug) de que `rms`/`flux`/`onset_flag` tienen sentido.
3. **Capa B — esqueleto `render.py`**: contexto moderngl headless, fullscreen
   quad, leer control.npz, loop de frames seteando uniforms. Primero un shader
   trivial (color = `rms`) para validar la tubería A→B sin GLSL complejo.
4. **Shaders, incrementales**: (a) `feedback.frag` ping-pong con zoom+rot
   espiral; (b) partículas ping-pong reabsorbiéndose; (c) grano/glitch CRT;
   (d) overlay VT323 (textura de texto pre-rendereada o SDF font). Probar cada
   uno aislado antes de componer.
5. **Capa C — `encode.py`**: pipe de frames RGB a ffmpeg + `-i recursion.wav`.
   Primero 10s de prueba, después los 3:00.
6. **QA visual + loop check**: ver el mp4, confirmar sync audio↔visual y que el
   último frame engancha con el inicial. Iterar curvas de los followers (§4)
   hasta que se sienta *musical*, no nervioso.
7. **Mostrar al usuario** → feedback → recién entonces escalar a Outbound,
   Crossing y el master continuo.

> **Patrón 4 (doble rol)**: en el paso 6, el usuario entra como *artista*
> (¿se siente como el retorno? ¿la deriva es sin esfuerzo?) y el pipeline +
> la skill creative-direction como *traductor*. Separar esa sesión de feedback
> de la sesión de tuneo técnico — mínimo un día de distancia (recomendación
> Tourso).

---

## 7 — Riesgos / gotchas + referencias

### Riesgos técnicos

- **macOS sin compute shaders.** El driver GL de Apple topa en OpenGL 4.1 — no
  hay compute shaders. Mitigación: GPGPU vía **transform-feedback o ping-pong de
  texturas** (probado, es el patrón estándar pre-compute). No intentar
  `glDispatchCompute`. Si en algún momento se quiere compute, el camino es
  Metal nativo (fuera de scope) o WebGPU.
- **Headless GL en Mac.** `create_standalone_context()` de moderngl funciona,
  pero validar temprano que rinde a FBO sin ventana en este Mac. Plan B:
  three.js + `headless-gl`/puppeteer (offline, también gratis) si moderngl da
  problema en Apple Silicon. Plan C: moderngl-window con ventana oculta.
- **Costo de render del master.** 24min × 30fps = 43.200 frames. A unos
  segundos/frame con raymarch pesado puede ser horas. Mitigaciones: bajar
  samples del raymarch, cachear el flow field, rendear los 3 temas en paralelo,
  y dejar el master para el final (el proto es 3:00 = 5.400 frames).
- **Sync audio↔video drift.** Asegurar fps de análisis == fps de render ==
  fps de encode, y dejar que ffmpeg use el WAV como reloj maestro (`-i wav`
  + duración del video derivada de `n_frames/fps`). Verificar en el QA del MVP.
- **I/O de frames.** Leer FBO y pipear RGB raw a ffmpeg por stdin (evitar
  escribir 43k PNGs a disco). `moviepy` es cómodo pero más lento que pipe
  directo — para el master, pipe directo.

### Riesgos creativos (chequeo contra el repo)

- **Caer en el visualizer de EQ.** El riesgo permanente. Antídoto: followers
  suavizados (§4), mapeos a *movimiento/densidad* y no a *barras*, y la regla
  "¿podría existir sin el audio?" (Patrón 2). Si en el MVP se ve un espectro,
  está mal.
- **Color que se va a neón.** Vigilar el phosphor: nunca cyan/magenta
  (`13_visual_style_guide.md`). `signal_red` y `warm_amber` son raros (1-3 veces
  en TODO el video), no acentos recurrentes.
- **Sobre-ilustrar la espiral.** Prohibido el trazo de espiral dibujado
  (`03_lore.md`). La espiral vive en la trayectoria de partículas, la deriva de
  cámara y el warp del feedback — nunca como ícono.
- **Movimiento agresivo.** El hexagrama 24 manda *movimiento natural, sin
  esfuerzo*. Si la cámara o las partículas se sienten cinéticas/videoclip-MTV,
  contradice la variable única. Lento, paciente (Eno/Roach, `aem-composer`).

### Referencias del research (todas gratis / open-source)

**Pipeline / render headless**
- ModernGL — repo + docs (headless `create_standalone_context`, FBOs, ping-pong):
  https://github.com/moderngl/moderngl · https://moderngl.readthedocs.io/
- Headless 3D rendering con Python (ejemplo): https://github.com/szabolcsdombi/headless-moderngl-experiment
- MoviePy (mux audio+video, cortes): https://pypi.org/project/moviepy/ · https://zulko.github.io/moviepy/user_guide/rendering.html
- FFmpeg codecs (H.264/ProRes/VP9, CRF): https://ffmpeg.org/ffmpeg-codecs.html

**Análisis de audio → control track**
- librosa spectral_centroid: https://librosa.org/doc/main/generated/librosa.feature.spectral_centroid.html
- librosa rms: https://librosa.org/doc/main/generated/librosa.feature.rms.html
- Audio feature extraction (overview): https://kaavyamaha12.medium.com/extracting-audio-features-using-librosa-3be4ff1fe57f

**Técnicas de shader**
- GPGPU partículas / ping-pong / curl-noise (three.js, transferible a moderngl): https://discourse.threejs.org/t/gpgpu-particles/90558 · https://medium.com/@midnightdemise123/creating-chaotic-flow-fields-with-gpgpu-in-react-three-fiber-f9aad608c534
- Curl noise GPU (OpenGL): https://github.com/kbladin/Curl_Noise
- GPU particle systems (conceptos, ping-pong): https://nvoid.gitbooks.io/introduction-to-touchdesigner/content/GLSL/12-7-GPU-Particle-Systems.html
- Raymarching volumétrico de nébula/clouds + FBM + domain warping: https://blog.maximeheckel.com/posts/real-time-cloudscapes-with-volumetric-raymarching/ · https://blog.42yeah.is/rendering/2023/02/11/clouds.html · http://pegwars.blogspot.com/2018/12/rendering-nebulae.html · https://mini.gmshaders.com/p/volumetric

**Mapeo audio→uniform (musical, no literal)**
- Envelope followers para audio-reactive: https://kferg.dev/posts/2020/audio-reactive-programming-envelope-followers/
- Audio-reactive shaders (mapeo a uniforms, no EQ bars): https://tympanus.net/codrops/2023/02/07/audio-reactive-shaders-with-three-js-and-shader-park/ · https://github.com/sandner-art/Audio-Shader-Studio

---

## Versión

v1 — 2026-05-21 — primer doc de dirección creativa + bajada técnica de la capa
video. Approach Python + shader (control track). Pendiente: aprobación del
usuario para scaffoldear `transmissions/01/video/` y arrancar el prototipo de
*Recursion*.
