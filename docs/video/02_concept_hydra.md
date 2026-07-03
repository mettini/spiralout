# Dirección creativa — videoclips Heliopause / Transmission 01 (approach HYDRA)

> **Qué es esto.** El plan de dirección creativa + bajada técnica para la
> capa audiovisual del EP *Heliopause*, ejecutada con **Hydra** (video synth
> de live coding, open-source, corre en el browser). Cubre concepto, stack
> técnico, tratamiento por movimiento, pipeline y prototipo.
>
> **Qué NO es.** No es infra montada. Los snippets de Hydra son ilustrativos
> y se commitearán como fuente (igual que los `compose_*.py`) cuando se
> apruebe arrancar. Esto es planificación.
>
> **Estado en el dashboard.** Sirve las tasks `canvas-video` (Spotify Canvas)
> y `yt-visualizer` (YouTube full-album visualizer) de `dashboard/data.json`.
> Visuales = prioridad 3 (después de difusión/cuentas y SEO/GEO).

---

## 0 — TL;DR para el que no lee 24 páginas

- **La variable única es `RETORNO` (Hexagrama 24 / Fù).** No "espacio", no
  "nébulas": el retorno. Hydra es la herramienta del retorno porque su
  primitiva nativa es el **feedback loop** (`src(o0)`): el frame anterior
  vuelve a entrar como insumo del siguiente. La forma de la herramienta *es*
  la forma del concepto. Igual que el loop/recursión/generator de Python ya
  son la firma del audio (`docs/07_vision.md`).
- **Materia prima compartida, no ilustración.** No dibujamos planetas. La FFT
  del propio track maneja los parámetros del patch. El visual no existe sin
  el audio — la onda *es* el material, no el referente.
- **Stack 100% gratis.** Hydra (browser) + BlackHole (routear el audio del
  track a la "entrada de micrófono" que Hydra escucha) + OBS / CCapture para
  capturar a video a alta resolución. Cero costo, cero suscripción.
- **Honestidad sobre el límite.** Hydra es imbatible para textura/feedback y
  débil para storytelling estructurado de 24 min. Lo resolvemos tratándolo
  como **synth de escenas**: un patch por movimiento, transiciones por
  crossfade entre buffers, ensamblado del master continuo en NLE/ffmpeg.
- **Prototipo recomendado: Recursion (3:00).** Es el candidato natural — el
  track *es* feedback y vinilo gastado, y dura poco, así que el MVP es
  demostrable en una sesión. Detalle en §6.

---

## 1 — Dirección creativa abstracta

### 1.1 La variable única (Patrón 1)

> *Si la artista no puede nombrar la variable en una sola palabra, aún no
> está clara.* — creative-direction, Patrón 1.

**La variable es RETORNO.** El Hexagrama 24 (復, *Fù*) no es decoración del
lore: es la carta que cae primero y la música obedece (`docs/02_cosmologia.md`,
§I). Cinco trazos yin, una línea yang entrando por abajo. Lo que vuelve a
empezar, en el mismo tono, pero a otra distancia. La espiral, no el círculo.

Todo output visual se mide contra esa ley: **¿esto vuelve sobre sí mismo?**
Si una decisión no encarna retorno/recursión/feedback, se descarta. La
variable funciona como constraint contra el ornamento.

Distinción importante con las imágenes del artista (espacio, nacimiento,
nébulas, polvo de Saturno, tropezones, vinilo gastado): esas son **estados
de la variable**, no la variable. El retorno se manifiesta como nacimiento
(Outbound), como tránsito que se curva (Crossing), como vuelta literal
(Recursion). Una sola ley, tres caras.

### 1.2 Materia prima compartida, no ilustración (Patrón 2)

> *La prueba es: ¿podría existir el visual sin escuchar el disco? Si sí, está
> ilustrando.* — creative-direction, Patrón 2.

La regla dura del proyecto: **no se ilustra el sonido, se comparte su materia
prima.** El audio del EP es síntesis NumPy/SciPy — las mismas librerías del
LHC (`docs/07_vision.md`). El visual de Hydra **toma la FFT de ese mismo
audio** y la usa como señal de control. No "dibujamos cómo suena un drone":
el espectro del drone *deforma* la geometría en tiempo real.

Si apagás el audio, el patch colapsa a su estado de reposo (un drone visual
mínimo). No hay video "sin el disco". Eso es materia prima compartida.

Esto también honra la regla anti-iconografía del lore (`docs/03_lore.md`):
**cero galaxias dibujadas, cero astronautas, cero espirales decorativas.** La
espiral aparece como *operación* (feedback que rota y escala), no como dibujo.

### 1.3 Inversión de tropos (Patrón 5)

Tropos del visualizer de space-ambient / dark-ambient en YouTube/Bandcamp:

1. Render 3D de nébulas fotorrealistas (Blender / stock NASA). → **Lo
   ignoramos.** Choca con la identidad "diagrama, no ilustración".
2. Waveform/espectro circular bonito girando (el "audio visualizer" genérico
   de After Effects). → **Lo citamos al revés.** Sí usamos FFT, pero no como
   adorno legible: la FFT *deforma* la imagen, no se dibuja como barritas.
3. Glow neón synthwave cyan/magenta. → **Prohibido por el design system.**
   Trabajamos en phosphor verde `#a6d65f` sobre negro CRT — el visualizer se
   ve como un *osciloscopio viejo en un rack de tierra*, no como un screensaver.
4. Hipersaturación / motion frenético. → **Invertido.** Paciencia roach-iana,
   movimiento lento, mucho negro (Patrón 5 + filosofía aem-composer: progresión
   > densidad).

La firma autoral es ese cruce: **un video synth de live-coding tratado con
disciplina de telemetría NASA**. Live-coding glitchy normalmente se ve caótico
y multicolor; nosotros lo encerramos en la paleta de un monitor de phosphor de
30 años en el rack.

### 1.4 Lectura antes que Pinterest (Patrón 7)

El proyecto ya cumple este patrón sin Pinterest: el sistema de pensamiento
está escrito. Los textos que alimentan el visual no son un mood board, son:
`docs/02_cosmologia.md` (el I Ching, el cuerpo, el cruce, la vuelta),
`docs/10_cuento.md` (el expediente HP-01, la inversión de fase, las fichas
técnicas), `docs/07_vision.md` (loop/recursión/generator como gramática del
viaje). De ahí emerge la imagen. Pinterest, si entra, es confirmador.

### 1.5 Mapeo de la variable a los tres movimientos

| Movimiento | Estado de la variable RETORNO | Imagen del artista (verbatim) | Operación visual Hydra |
|---|---|---|---|
| **Outbound** 8:00 | El primer cruce / nacimiento. El feedback todavía no existe — algo se desprende y empieza a alejarse. | "un nacimiento, oscuridad, los latidos llaman, se despega" | Punto/semilla que late con el heartbeat (60 BPM); apenas feedback, todo todavía coherente. La espiral aún no empezó. |
| **Crossing** 13:00 | El tránsito denso. La trayectoria se curva en el centro exacto (inversión de fase, ficha 02). | "nébulas, polvo de los anillos de Saturno, tropezones con rocas, dificultad en el andar" | Campo de ruido/voronoi (polvo), modulación creciente; en el minuto medio el feedback *invierte sentido de rotación* — la órbita se parte. |
| **Recursion** 3:00 | La vuelta literal. Feedback total, vinilo gastado, eco del motivo de Outbound deformado. | "una recursión, un retorno, un vinilo gastado que chicharrea, volver a nacer, spiral out" | `src(o0)` realimentado al máximo: la imagen se traga a sí misma en espiral (Droste). Glitch/crackle = el chicharreo. El final engancha con el frame inicial de Outbound. |

El hilo conductor visual: **el grado de feedback es la trayectoria de la
sonda.** Outbound ≈ feedback 0 (ida limpia). Crossing ≈ feedback que crece y
se invierte (el cruce). Recursion ≈ feedback que se cierra sobre sí (la
vuelta). Si el EP loopea infinito, el último frame de Recursion debe poder ser
el primero de Outbound — igual que el audio engancha armónicamente
(`docs/02_cosmologia.md`, §V). **El loop es la obra.**

### 1.6 Chequeo creative-direction (los 7 patrones)

```
> Decisión: dirigir los videoclips de Heliopause con Hydra, variable = RETORNO.

✓ Patrón 1 (variable única): RETORNO / Hexagrama 24 nombrada en una palabra.
                             El feedback de Hydra ES la variable hecha herramienta.
✓ Patrón 2 (materia prima):  la FFT del track maneja el patch. Sin audio el
                             visual no existe → no ilustra, comparte materia.
○ Patrón 3 (decisión material): el "soporte físico" del video es el FORMATO
                             de circulación (loop infinito YT/Bandcamp como
                             performance del concepto, ya previsto en el lore).
                             Pregunta abierta abajo.
✓ Patrón 4 (artista/traductor): el repo separa los roles — el artista da el
                             prompt creativo (las imágenes), el patch + este
                             doc son la función traductora (qué se materializa).
✓ Patrón 5 (inversión tropos): se invierten los 4 tropos del space-ambient
                             visualizer (ver §1.3). Firma = live-coding con
                             disciplina de telemetría, paleta phosphor.
○ Patrón 6 (equipo estable):  Hydra + el repo son el "colaborador estable" —
                             el patch evoluciona entre transmisiones, no se
                             rehace de cero cada vez. Continuidad garantizada
                             por el design system y este doc.
✓ Patrón 7 (lectura > Pinterest): el sistema de pensamiento ya está escrito
                             (cosmología, cuento, visión). La imagen emerge de ahí.

Observación clave: Hydra no es "un look que elegimos", es la elección
conceptualmente correcta. El feedback loop (`src(o0)`) es la traducción
literal del Hexagrama 24 y de la recursión de Python que ya firma el audio.
La herramienta y el concepto son la misma operación girando — igual que el
24 y el 42.

Pregunta abierta (Patrón 3): ¿el formato de entrega define el concepto? Mi
recomendación: SÍ — publicar la versión continua como loop infinito real
(no un MP4 que termina) en YouTube/Bandcamp es la decisión material que
encarna "Heliopause loopea, vos también". ¿Lo asumimos como entregable
canónico o como variante?
```

---

## 2 — Por qué Hydra sirve a esta música/concepto (y dónde NO)

### 2.1 Donde Hydra es la herramienta correcta

- **Feedback loops nativos.** `src(o0)` realimenta el output al input. Es
  *la* primitiva del retorno/recursión. Ninguna otra herramienta gratis lo
  tiene tan a mano y tan barato de iterar.
- **Texturas generativas orgánicas.** `noise()`, `voronoi()`, `osc()`
  encadenados dan polvo, nébula, grano, interferencia — sin assets, sin stock,
  reproducible desde código. Coherente con "el medio importa más que el
  acabado" (`docs/07_vision.md`).
- **Audio-reactividad de primera clase.** El objeto `a` (FFT vía Meyda) está
  pensado exactamente para esto: dirigir parámetros desde bandas de frecuencia.
- **Reproducibilidad = código.** El patch es un `.js` chico que se commitea,
  igual que `compose_*.py`. Quien clone el repo regenera el video. Encaja con
  la política "los WAV son gitignored, la fuente queda".
- **Estética glitch/CRT.** `pixelate()`, scanlines a mano, posterización,
  el feedback con leve color-shift → naturalmente se ve a "monitor viejo".
  Casa con el visual style guide sin pelear.
- **Live-coding como performance.** Para shows en vivo / streams, el patch
  reacciona al audio en tiempo real. La capa audiovisual no es solo render:
  es instrumento.

### 2.2 Donde Hydra NO sirve (honestidad)

- **Storytelling estructurado de 24 min en un solo flujo.** Hydra no tiene
  timeline ni keyframes. No es After Effects. Un set largo se programa con
  funciones de tiempo (`() => time`), `setInterval`, o secuenciando arrays —
  pero "en el minuto 6:30 entra la voz grave y la imagen hace X" es engorroso.
  **Solución:** un patch por movimiento (escena), no un patch monstruo.
- **Tipografía / lockups precisos.** Hydra renderiza texto fatal. El lockup
  ÆM, los labels VT323, las fichas técnicas → se montan como **overlay** (capa
  PNG/SVG con transparencia o HTML/CSS encima del canvas), no dentro de Hydra.
- **Captura frame-perfect en tiempo real.** El `MediaRecorder` del browser usa
  *wall clock*: si un frame tarda, se cae (choppy). Para 24 min en alta resolución
  esto es un riesgo real. **Solución:** OBS para realtime, o CCapture para
  render offline frame-a-frame (ver §3).
- **Determinismo perfecto.** `noise()`/feedback dependen de tiempo y, a veces,
  de orden de eval. Para que el render sea reproducible hay que **fijar el
  seed de tiempo** (arrancar `time` desde 0, no desde `Date.now()`), o capturar
  en una sola pasada y versionar el WebM/MP4 resultante junto al patch.
- **Resolución alta = caro.** A 4K con feedback pesado el frame-rate cae. Para
  el master apuntamos a 1920×1080@30; 4K solo si el patch aguanta.

**Veredicto:** Hydra es perfecta como **synth de texturas + feedback dirigido
por audio**, tratada con arquitectura de escenas. No la forzamos a ser un
editor de video. El ensamblado y la tipografía viven afuera.

---

## 3 — Stack técnico PRO y gratis

Todo open-source / gratis. Cero suscripciones.

### 3.1 Componentes

| Capa | Herramienta | Costo | Para qué |
|---|---|---|---|
| Video synth | **Hydra** (`hydra.ojack.xyz` o `hydra-synth` npm/local) | gratis | el patch que genera la imagen |
| Editor del patch | el editor web de Hydra **o** un `index.html` local con `hydra-synth` | gratis | live-coding, reproducible desde el repo |
| Routing de audio | **BlackHole** (macOS, ExistentialAudio) | gratis/open | llevar el audio del track a la "entrada de micrófono" que Hydra lee |
| Captura realtime alta-res | **OBS Studio** (window/display capture) | gratis/open | grabar 1080p/4K con bitrate alto |
| Captura offline frame-perfect | **CCapture.js** + ffmpeg | gratis/open | render determinista frame-a-frame para el master |
| Multiplexado / corte / loops | **ffmpeg** | gratis/open | pegar video+audio, cortar por tema, generar loops, recodificar |
| Overlays (lockup, fichas) | **SVG/PNG** del design system + CSS, o capa en ffmpeg/NLE | gratis | tipografía VT323, ÆM, labels técnicos |
| NLE (opcional, ensamblado) | **Shotcut** o **Kdenlive** | gratis/open | montar el master continuo si no se hace todo en ffmpeg |

### 3.2 El gotcha #1 — Hydra escucha el micrófono, no el desktop

> *"Hydra takes your microphone as an input, not your desktop audio."*
> — docs oficiales de audio reactivity.

Como el EP ya está renderizado (no es audio en vivo), hay que **routear** la
salida del reproductor a la entrada que Hydra analiza:

1. Instalar **BlackHole** (2ch alcanza).
2. En *Audio MIDI Setup* (preinstalado en macOS), crear un **Multi-Output
   Device** = BlackHole + tus auriculares/monitores (para escuchar mientras
   capturás).
3. Reproducir el WAV del track con salida → ese Multi-Output.
4. En Hydra, seleccionar **BlackHole** como input de audio (el `a` de Meyda).
5. Resultado: Hydra "escucha" el track exacto del EP. La FFT que maneja el
   patch es la del master real, no la del micrófono ambiente.

**Alternativa más precisa (offline):** en vez de FFT en vivo, pre-analizar el
WAV con un script (Python `numpy.fft` / `librosa`, o Web Audio
`AnalyserNode`) y exportar un JSON de envolventes por banda y por frame
(`{frame, sub42, low, mid, high, beat}`). El patch lee ese JSON indexado por
`time`. Ventaja: **determinista y reproducible** (mismo audio → mismo video
siempre), y desacopla la captura del routing. Recomendado para el master
final; el routing en vivo es ideal para iterar y para shows.

### 3.3 El gotcha #2 — captura de alta calidad

- **Realtime (rápido, para cortes/loops/Canvas):** OBS, *Window Capture* del
  browser con Hydra a pantalla completa, output a 1920×1080@30, CRF/bitrate
  alto. Cuidado con la barra del navegador (recortar con filtro crop).
- **Offline frame-perfect (para el master de 24 min):** el `MediaRecorder`
  nativo (`vidRecorder.start()`/`stop()`, codec vp9/webm) es real-time y baja
  calidad — **no** para el master. Usar **CCapture.js** enganchado al render
  loop de Hydra: captura cada frame a tiempo de reloj *virtual*, no de pared,
  y exporta PNG sequence o webm sin perder frames aunque el render sea pesado.
  Después `ffmpeg` arma el MP4/ProRes a 30fps exactos y multiplexa el audio.

### 3.4 Resolución / fps objetivo

| Entregable | Resolución | fps | Notas |
|---|---|---|---|
| Master continuo (YouTube) | 1920×1080 (4K solo si aguanta) | 30 | feedback pesado → priorizar 1080p estable sobre 4K choppy |
| Corte por tema (YouTube) | 1920×1080 | 30 | derivado del master, mismo patch |
| Spotify Canvas | 1080×1920 (9:16) | 24-30 | loop 3-8s, < 8s, sin texto, `setResolution(1080,1920)` |
| Loop corto IG/Bluesky | 1080×1080 o 1080×1920 | 30 | 3-6s, perfect loop |

`setResolution(w, h)` en Hydra fija el canvas. Para 9:16 se reescribe el patch
con coordenadas verticales (no recortar el 16:9, recomponer).

---

## 4 — Tratamiento por movimiento

Convención de bandas FFT del proyecto (fijar con `a.setBins(4)`):

```
a.setBins(4)
// a.fft[0] = SUB    (~ portadora 42 Hz, heartbeat, columna)
// a.fft[1] = LOW    (drones graves, bajo)
// a.fft[2] = MID    (voces, pads, motivo Voyager)
// a.fft[3] = HIGH   (aire, glitches, crackle, fritura controlada)
a.setSmooth(0.85)   // ambient = lento, sin strobe. Recursion baja a ~0.6.
a.setCutoff(0.1)    // gate de ruido de fondo
a.setScale(8)       // headroom de auto-gain
```

Tabla maestra de mapeo audio → visual:

| Movimiento | Qué se ve | Cadena Hydra (núcleo) | `fft[0]` SUB | `fft[1]` LOW | `fft[2]` MID | `fft[3]` HIGH |
|---|---|---|---|---|---|---|
| **Outbound** | punto/semilla que late en negro, se desprende y se aleja; casi sin feedback | `shape→scale→modulate(noise)→out` | escala/pulso del punto (heartbeat 60 BPM) | brillo del bed, drift lento | aparición del motivo (segunda forma tenue) | grano fino, casi nada |
| **Crossing** | campo de polvo/voronoi, nébula que se densifica; en el medio la rotación se invierte | `voronoi→modulate(noise)→rotate→modulate(o0)→out` | densidad del polvo | masa/contraste de la nébula | warp de las "voces" (sílaba grave) | "tropezones": jitter en HIGH transients |
| **Recursion** | Droste/espiral: la imagen se traga a sí misma; glitch = vinilo chicharreando | `src(o0).scale(1.01).rotate(0.02).modulate(noise).layer(seed)→out` | empuje del zoom de feedback | profundidad de la espiral | eco deformado del motivo Outbound | crackle/glitch (el chicharreo) |

### 4.1 Outbound — el primer cruce (feedback ≈ 0)

La idea: **antes de la espiral.** Una sola forma, latido, oscuridad, mucho
negro. El feedback casi no existe todavía (la sonda va en línea recta). El
heartbeat a 60 BPM (la "primera información que el cuerpo entiende",
`docs/02_cosmologia.md` §III) maneja el pulso del punto vía `fft[0]`.

```javascript
// OUTBOUND — el latido en el vacío. Feedback mínimo, todo coherente.
a.setBins(4); a.setSmooth(0.9); a.setScale(8);

shape(64, 0.02, 0.6)                       // semilla casi-circular, borde suave
  .scale(() => 0.5 + a.fft[0] * 0.6)       // SUB/heartbeat -> late
  .color(0.65, 0.84, 0.37)                 // PHOSPHOR #a6d65f aprox
  .modulate(noise(2, 0.05), 0.15)          // drift lento, orgánico
  .add(
    shape(64, 0.01, 0.9)                    // segunda forma = el motivo Voyager
      .scale(() => 1.5 + a.fft[2] * 1.2)    // MID lo trae cuando aparece
      .luma(0.2, 0.05), 0.3
  )
  .modulate(o0, 0.01)                       // FEEDBACK MÍNIMO — la espiral aún no
  .out();
```

Lo audible que lo justifica: el track abre con dos heartbeats (interno y
externo) desincronizándose. El segundo `shape` puede atarse al segundo
heartbeat — dos pulsos que se separan en pantalla. Cuando "se despega" (la
vibración final, el desprendimiento), subir el `modulate(o0)` un toque: la
espiral *empieza a insinuarse* justo al final, anticipando Crossing.

### 4.2 Crossing — el tránsito que se curva (feedback que crece e invierte)

La idea: **polvo, densidad, dificultad en el andar.** Voronoi + noise = polvo
de los anillos / nébula. "Tropezones con rocas" = jitter cuando hay transients
en HIGH. El momento clave: la **inversión de fase en el centro exacto**
(ficha 02: "inversión de fase en el centro exacto del tramo", "desvío 24°").
A los ~6:30 el signo de la rotación del feedback se invierte. La órbita se
parte. No es corte: es crossfade del sentido.

```javascript
// CROSSING — polvo, nébula, y la órbita que se parte en el medio.
a.setBins(4); a.setSmooth(0.8); a.setScale(10);

const half = 13*60/2;                       // 6:30, el centro del tramo
voronoi(() => 4 + a.fft[1] * 8, 0.3, 0.2)   // LOW densifica el polvo
  .color(0.42, 0.56, 0.20)                  // PHOSPHOR_DIM, nébula apagada
  .modulate(noise(3, 0.1), () => 0.1 + a.fft[2] * 0.4) // MID = voces deforman
  .rotate(() => (time < half ? 0.02 : -0.02) * (time % half)) // INVERSIÓN a mitad
  .add(
    noise(8, 0.2).thresh(() => 0.9 - a.fft[3] * 0.3).luma(0.5), // tropezones HIGH
    0.2
  )
  .modulate(o0, () => 0.02 + (time/half) * 0.03)  // feedback CRECE hacia el centro
  .out();
```

Lo audible: 13 min de masa, voces graves sin palabras (gospel sin dios),
y la inversión sin aviso a la mitad. El polvo no debería ser fritura visual
gratuita — paciencia, igual que el sonido evita la fritura sobre 1000 Hz
(`memory/pattern_noise_fritura.md`): movimiento lento, no ruido nervioso.

### 4.3 Recursion — la vuelta (feedback total, Droste, chicharreo)

La idea: **el track ES feedback.** Drone que crece hasta ocupar todo, eco
distorsionado del motivo de Outbound una octava abajo, vinilo gastado que
chicharrea. Acá Hydra hace lo que mejor hace: `src(o0)` realimentado con
zoom + rotación leves = **espiral Droste** (la imagen dentro de sí misma,
infinita). El crackle del vinilo = glitch en HIGH.

```javascript
// RECURSION — la espiral se traga a sí misma. Spiral out.
a.setBins(4); a.setSmooth(0.6); a.setScale(12);  // menos smooth: reacciona al glitch

src(o0)                                     // EL FRAME ANTERIOR vuelve a entrar
  .scale(() => 1.008 + a.fft[0] * 0.02)     // SUB empuja el zoom hacia adentro
  .rotate(() => 0.015 + a.fft[1] * 0.02)    // LOW = profundidad de la espiral
  .modulate(noise(2, 0.02), 0.01)           // jitter orgánico
  .layer(                                    // eco deformado del motivo Outbound
    shape(64, 0.02, 0.7)
      .scale(() => 1 + a.fft[2] * 0.8)
      .color(0.65, 0.84, 0.37)
      .luma(0.4, 0.1)
  )
  .add(
    noise(20, 0.5).thresh(() => 0.95 - a.fft[3] * 0.4).color(0.83,0.63,0.29), // chicharreo (WARM_AMBER, raro)
    () => a.fft[3] * 0.3
  )
  .out();
```

Lo audible y lo conceptual: el último compás de Recursion engancha
armónicamente con el primero de Outbound (`docs/02_cosmologia.md` §V). El
visual debe cerrar igual: el último frame de Recursion = el primer frame de
Outbound (la semilla en negro). **Si loopea, no hay corte.** Eso *es* el
Hexagrama 24. El crackle usa WARM_AMBER (`#d4a04a`) — el accent raro del
design system, "2-3 veces total". Acá tiene sentido: es la única vez que el
verde phosphor se quiebra, justo cuando la firma cambia (Æ que se agrega).

> **Nota anti-fritura (memoria del proyecto):** el ruido visual de alta
> frecuencia es el equivalente al `np.abs()` exciter / noise > 1000 Hz que
> suena a fritura. Usar `thresh()` para que el glitch sea *eventos discretos*
> (chicharreo de vinilo = clicks), no estática continua. Menos es más.

---

## 5 — Pipeline de producción

### 5.1 Arquitectura: synth de escenas, no patch monstruo

```
patches/
├── outbound.js        ← un patch por movimiento (escena), commiteado
├── crossing.js
├── recursion.js
├── _common.js         ← setBins/setSmooth, paleta, helpers (color phosphor, etc.)
└── analysis/          ← (opción offline) JSON de envolventes por banda/frame
    ├── outbound.json
    ├── crossing.json
    └── recursion.json
```

Igual que `themes/<track>/compose_full.py`: **el patch es la fuente, el video
es regenerable.** Se commitea el `.js`; el MP4 NO (gitignored, como los WAV).

### 5.2 Cómo se arma el master continuo (3 movimientos)

Hydra no tiene timeline, así que el master se ensambla **afuera**, en dos
modos posibles:

**Modo A — captura por escena + montaje (recomendado, control total):**
1. Capturar cada movimiento por separado (Outbound 8:00, Crossing 13:00,
   Recursion 3:00) con su patch, sincronizado al WAV del track vía BlackHole
   o al JSON de análisis offline.
2. Diseñar **transiciones de 15-30s** entre escenas (igual que los crossfades
   de audio, regla R2 de aem-composer): los últimos 20s de un patch ya morphean
   hacia el siguiente (subir `modulate(o0)` al final de Outbound; arrancar
   Crossing con el polvo apareciendo desde el centro).
3. En ffmpeg/NLE: concatenar las 3 escenas con crossfade de video (`xfade`) +
   pegar el audio del master continuo del EP (`00_heliopause_continuous.wav`).
4. Verificar que el último frame de Recursion ≈ primer frame de Outbound
   (loop limpio).

**Modo B — un solo patch con switch por tiempo (más Hydra-puro, menos control):**
Un patch maestro que cambia de escena con `() => time` y condicionales o un
secuenciador (`[...].fast()`/`setInterval`). Honra el "single continuous flow"
pero es frágil para 24 min. Sirve para vivo/streams; para el master canónico,
Modo A.

### 5.3 Cortes derivados por tema

Del master (o re-capturando cada patch aislado): tres MP4 1080p, uno por
track, con su overlay de lockup (`01 OUTBOUND 08:00`, etc.) montado encima en
ffmpeg/NLE. Sirven para subir cada track como single con visualizer
(dashboard task `single-1`).

### 5.4 Loops cortos (Spotify Canvas / IG / Bluesky)

- Reescribir el patch en 9:16 (`setResolution(1080,1920)`), recomponer
  vertical.
- Capturar 6-8s de un segmento que loopee perfecto (Recursion es ideal: el
  feedback ya es cíclico). El truco del loop perfecto: capturar un período
  exacto del ciclo de feedback, o hacer crossfade de los extremos en ffmpeg.
- < 8s, sin texto (regla del Canvas), MP4 H.264, 1080×1920.

### 5.5 Resolución / fps / captura (resumen)

- Master: 1920×1080@30, captura offline (CCapture) → ProRes/MP4 → ffmpeg mux.
- Cortes: 1920×1080@30, derivados.
- Canvas/loops: 1080×1920@30, OBS o CCapture, loop perfecto.
- Overlays (lockup/fichas): SVG/PNG del design system, compuestos encima
  fuera de Hydra.

---

## 6 — Propuesta de prototipo

### 6.1 Recomendación: arrancar por **Recursion**

Por qué Recursion y no Outbound:

1. **Es el track que justifica Hydra.** Recursion *es* feedback, recursión,
   vinilo gastado, spiral out. El `src(o0)` Droste es la demo más fuerte y la
   más conceptualmente cargada. Si el prototipo convence, convence con el
   argumento más fuerte.
2. **Dura 3:00** → MVP demostrable en una sesión, no 13 min de captura.
3. **Cierra el loop conceptual.** Probar que el último frame puede enganchar
   con el primero de Outbound valida la tesis central (el Hexagrama 24) desde
   el primer prototipo.
4. **El brief del usuario lo pide:** "alcanza con animar los primeros minutos
   de UN tema" — y Recursion entero son 3 min.

(El brief también acepta Outbound como alternativa de "primeros minutos". Si
se prefiere validar el heartbeat-reactividad antes que el feedback, Outbound
es plan B. Pero la apuesta es Recursion.)

### 6.2 MVP mínimo demostrable

Un `recursion.js` que:
- Lea la FFT del WAV de Recursion (vía BlackHole en vivo para iterar).
- Implemente la cadena Droste de §4.3.
- Reaccione audiblemente: el zoom empuja con el SUB, el crackle aparece con
  el HIGH, el motivo eco aparece con el MID.
- Se capture a un MP4 1080p de ~30-60s (no hace falta los 3 min completos
  para el MVP) sincronizado al audio.

Criterio de éxito: que al ver el clip **sin que te digan nada**, sientas
"esto vuelve sobre sí mismo / esto chicharrea como un vinilo". Si la variable
RETORNO se lee sin explicación, el prototipo pasa.

### 6.3 Pasos concretos (cuando se apruebe arrancar)

1. **Setup (30 min):** instalar BlackHole, crear Multi-Output Device, instalar
   OBS. Verificar que Hydra "escucha" un WAV reproducido (`a.show()` muestra el
   espectro moviéndose).
2. **Patch base (1 sesión):** escribir `patches/recursion.js` + `_common.js`
   (paleta phosphor, setBins/setSmooth). Iterar contra el WAV de Recursion.
3. **Mapeo audio→visual (1 sesión):** afinar qué banda maneja qué hasta que
   reaccione *audiblemente* (no a ojo). Documentar el mapeo final en el patch
   como comentario (en español, como el resto del repo).
4. **Captura MVP (30 min):** capturar 30-60s con OBS o CCapture, mux con
   ffmpeg, revisar en loop.
5. **Review con el usuario:** ¿se lee el RETORNO? ¿el chicharreo es evento o
   fritura? Ajustar.
6. **Si pasa:** escalar a Recursion completo (3:00) + extender el patrón a
   Crossing y Outbound. Definir overlays y el ensamblado del master (Modo A).

Esto NO monta infra todavía — es el plan de ejecución para cuando visuales
suba de prioridad 3.

---

## 7 — Riesgos / gotchas + referencias

### 7.1 Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Hydra escucha mic, no desktop audio | BlackHole + Multi-Output Device (§3.2), o análisis offline a JSON |
| `MediaRecorder` (vidRecorder) es real-time y baja calidad → frames perdidos en 24 min | CCapture frame-a-frame para el master; OBS para cortes/loops |
| Captura no determinista (noise/feedback dependen de wall-clock) | fijar `time` desde 0; o capturar una sola pasada y versionar el resultado junto al patch |
| 4K con feedback pesado = frame-rate cae | priorizar 1080p@30 estable; 4K solo si el patch aguanta medido |
| Glitch visual de alta frecuencia = "fritura visual" | `thresh()` para eventos discretos (clicks), no estática continua. Menos es más (memoria del proyecto) |
| Hydra renderiza texto pésimo | lockup/fichas/labels como overlay SVG/PNG fuera de Hydra |
| Salirse de paleta (live-coding tiende al multicolor) | constraint duro: `.color()` solo a phosphor/dim; WARM_AMBER 2-3 veces; cero cyan/magenta |
| Romper el lore (iconografía obvia) | cero galaxias/planetas/astronautas dibujados; la espiral es operación, no dibujo |
| 24 min en un solo patch es frágil | arquitectura de escenas (un patch por movimiento) + ensamblado afuera |

### 7.2 Referencias (research)

- Hydra — audio reactivity (objeto `a`, FFT/Meyda, `setBins`, `setSmooth`,
  `setScale`, `setCutoff`, `onBeat`): https://hydra.ojack.xyz/docs/docs/learning/guides/audio/
- Hydra — audio (versión sequencing/interactivity): https://hydra.ojack.xyz/docs/docs/learning/sequencing-and-interactivity/audio/
- Hydra — grabar el output (vidRecorder vp9/webm, OBS recomendado): https://hydra.ojack.xyz/docs/docs/learning/guides/how-to/record-hydra-output/
- Hydra — modulate / combinecoord (warping de geometría): https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/combinecoord/
- Hydra — sources (`src(o0)`, buffers de salida, feedback): https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/src/
- Hydra — repo oficial: https://github.com/hydra-synth/hydra
- Tutorial corto de Hydra (Charlie Roberts): https://gist.github.com/charlieroberts/93d52a5671a43e3f513a3d55652ab6f0
- Visualizar música con FFT (contexto técnico): https://sangarshanan.com/2024/11/05/visualising-music/
- BlackHole — driver de audio loopback macOS (gratis/open): https://github.com/ExistentialAudio/BlackHole
- BlackHole — routear desktop audio en macOS: https://existential.audio/blackhole/
- Limitación de `MediaRecorder` (wall-clock, no frame-by-frame) → necesidad de CCapture: https://github.com/w3c/mediacapture-record/issues/213
- OBS Studio (captura realtime gratis/open): https://obsproject.com/
- ffmpeg (mux / corte / loops / recodificación): https://ffmpeg.org/

### 7.3 Documentos del proyecto que sostienen este plan

- Variable única / RETORNO / Hexagrama 24: `docs/02_cosmologia.md`, `docs/10_cuento.md`
- Recursión/loop/generator como gramática del viaje: `docs/07_vision.md`
- Reglas anti-iconografía: `docs/03_lore.md`
- Paleta, tipografía, tokens, aspect ratios: `docs/13_visual_style_guide.md`, `docs/14_design_system.md`
- Chequeo de patrones de dirección: `.claude/skills/creative-direction/SKILL.md`
- Filosofía sonora (progresión, crossfades, curva de densidad): `.claude/skills/aem-composer/SKILL.md`
- Anti-fritura / paciencia: `memory/pattern_noise_fritura.md`, `memory/abs_rectifier_exciter_antipattern.md`
- Estado/prioridad de la capa visual: `dashboard/data.json` (`canvas-video`, `yt-visualizer`)

---

*v1 — 2026-05-21 — primer plan de dirección creativa audiovisual (Hydra) para
Transmission 01. Planificación; sin infra montada.*
