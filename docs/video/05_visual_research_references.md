# Visual research & references — el "delirio" que transiciona entre conceptos

> **Qué es esto.** Research online profundo de cómo representar de forma
> **abstracta / mística / misteriosa** los conceptos del EP *Heliopause*, y su
> destilación en un material accionable para construir un **video que transiciona
> entre conceptos** — un viaje, un delirio, no algo estático ni un loop plano.
>
> **No es** un concepto cerrado ni reemplaza a `01`–`04`. Es la **caja de
> herramientas estéticas**: de dónde robar, qué lenguaje visual usar por
> concepto, y un storyboard del delirio para *Recursion* (3:00) atado a eventos
> de audio.
>
> Hereda y respeta: `13_visual_style_guide.md` (paleta fósforo, anti-iconografía),
> `02_cosmologia.md` / `03_lore.md` / `10_cuento.md` (concepto), y la tesis de
> `01_concept_python_shader.md` (el audio no se ilustra: comparte materia prima).
>
> **Regla dura heredada (anti-iconografía):** sin caras, sin planetas/Hubble,
> sin astronautas, sin barras de EQ, **sin espiral dibujada literal**. La espiral
> vive en la *trayectoria* y en el *warp del feedback*, nunca como trazo. Color
> phosphor monocromo de base; `signal_red`/`warm_amber` 2-3 veces en TODO el video.
> Para el Concepto B (stargate), el color "sucio mineral" desaturado es la firma,
> nunca neón cyan/magenta.
>
> Estado: research. v1 — 2026-05-21.

---

## 0 — TL;DR (los 30 segundos)

El delirio no inventa un look nuevo: **roba de la genealogía del "visual music"
cósmico** (Belson, los Whitney, Fischinger, Wilfred), del cine experimental
material (Brakhage, Trumbull), de la estética de datos (Ikeda, Semiconductor,
Anadol) y de la geometría sagrada/mística (Hilma af Klint), y lo filtra por la
disciplina fósforo del proyecto. La columna técnica ya está decidida
(Python+shader spine + Hydra textura + AI restyle opcional, ver `00_PLAN_status.md`).
Acá va el **qué** robar y el **cómo encadenarlo** en un viaje de 3:00 que muta de
escena en escena: nacer → humo/nébula → túnel → espiral/mandala → polvo/rocas →
vinilo/colapso → renacer (loop).

---

## 1 — Catálogo de referencias (qué es · link · QUÉ ROBAR)

Ordenado de "más robable para este proyecto" hacia abajo. El "QUÉ ROBAR" es la
técnica/look exacto aplicable, no la admiración genérica.

### 1.1 Jordan Belson — *Allures* (1961), *Samadhi* (1967), *Phenomena*, *Re-entry*
- **Qué es.** "Cosmic cinema" / visual music abstracto: mandalas que flamean y
  giran, espacios-luz que respiran, hechos por **manipulación en vivo de luz
  pura** sobre un banco óptico (no animación cuadro a cuadro). Pretende
  representar estados de conciencia (yoga, budismo) sin explicarlos.
- **Link.** https://www.centerforvisualmusic.org/BelsonFilmNotes.html ·
  https://lightcone.org/en/filmmaker-19-jordan-belson ·
  https://en.wikipedia.org/wiki/Jordan_Belson
- **QUÉ ROBAR.** El **núcleo radial que respira** y muta lentamente (no late
  nervioso) — exactamente el "latido que llama" de Outbound y el colapso de
  Recursion. Robar la *cualidad*: formas que emergen del centro, se abren en
  capas concéntricas y se reabsorben, **sin contorno duro** (todo es densidad de
  luz). Es la prueba histórica de que el núcleo-mandala monocromo funciona sin
  caer en ícono. Es nuestra referencia #1 para "místico sin dibujar la espiral".

### 1.2 John & James Whitney — *Catalog* (1961), *Lapis* (1966)
- **Qué es.** Cine cibernético hecho con una **"cam machine"**: computadora
  analógica de guerra (controladores de cañón antiaéreo) reusada para mover
  motores con precisión. *Catalog* termina con curvas de Lissajous multiplicadas
  decenas de veces, retorciéndose como una flor abriéndose. *Lapis* multiplica
  cientos de puntos dibujados a mano en miles → **mandalas que respiran y se
  desestabilizan**, forma emergente desde puntos.
- **Link.** https://www.imdb.com/title/tt0380493/ (Lapis) ·
  https://canyoncinema.com/2023/03/14/new-artist-members-john-and-james-whitney/ ·
  https://en.wikipedia.org/wiki/John_Whitney_(animator)
- **QUÉ ROBAR.** Dos cosas: (1) **mandala desde campo de puntos/partículas** —
  miles de partículas cuya posición (no su dibujo) genera un patrón concéntrico
  que rota y se reorganiza; encaja 1:1 con el particle system GPGPU del shader.
  (2) **Movimiento armónico** = la posición de cada punto sale de osciladores
  acoplados (Lissajous), no de ruido aleatorio → da el "orden que aparece solo"
  del hexagrama 24. Mapear las frecuencias de esos osciladores al `centroid` /
  `chroma_root` del audio. Esto es el antídoto contra "partículas que se ven
  random".

### 1.3 Douglas Trumbull — Star Gate de *2001* (1968), slit-scan
- **Qué es.** El corredor de luz infinito de "Jupiter and Beyond the Infinite".
  Técnica **slit-scan**: cámara que avanza filmando a través de una **ranura
  móvil** sobre patrones (dibujos de circuitos, micrografías de cristales,
  pinturas y químicos en tanque filmados macro en cámara lenta) → todo se estira
  en corredores que fugan al infinito desde un punto. Color **invertido,
  solarizado, enfermizo/mineral**, no neón.
- **Link.** https://airandspace.si.edu/stories/editorial/making-2001s-star-gate-sequence ·
  https://neiloseman.com/slit-scan-and-the-legacy-of-douglas-trumbull/ ·
  https://www.redsharknews.com/douglas-trumbull-and-how-slit-scan-changed-sfx
- **QUÉ ROBAR.** El **túnel/fuga** (Concepto B, preset `stargate`). En shader no
  hace falta el rig mecánico: se simula con **feedback buffer + zoom fuerte hacia
  el centro en coordenadas polares** (todo se estira radialmente = streaks
  slit-scan). Lo *clave* a robar no es el túnel — es la **paleta sucia
  solarizada**: invertir parcialmente la curva de luminancia + saturación baja +
  sesgo a verde-enfermo/ámbar-terroso. Y el **origen del material**: filmar
  texturas "científicas feas" (no nébulas bonitas) — micrografías, circuitos,
  químicos — para alimentar la fuga. Es exactamente "el cruce de umbral
  (heliopausa)".

### 1.4 Ryoji Ikeda — *test pattern* (2006–), *data.scan*, *the transfinite*
- **Qué es.** **Datos → patrones binarios monocromos** generados en tiempo real:
  barcodes que flickerean y glitchean en bloques blanco/negro, ultra-rápidos
  (cientos de fps en momentos). "Sonificación pura del dato" y su inverso visual.
  Estética del dato: lo bello y lo sublime desde la frialdad del binario.
- **Link.** https://www.ryojiikeda.com/project/testpattern/ ·
  https://forma.org.uk/projects/test-pattern
- **QUÉ ROBAR.** El **glitch/flicker como evento puntual sincronizado al audio** —
  no decorativo, disparado por `onset_flag`/`flux`. Robar la **telemetría
  monocroma**: barcodes/líneas de scan/dropouts que aparecen 1-3 frames en los
  transientes (los "tropezones con rocas", el "vinilo que chicharrea"). Es el
  puente perfecto entre el lore (FICHA / telemetría VT323) y lo audio-reactivo, y
  refuerza la inversión del tropo "visualizer de EQ": **dato como contenido, no
  como gráfico de barras**. Disciplina: monocromo y *ráfagas cortas*, nunca
  continuo (epiléptico).

### 1.5 Semiconductor — *Brilliant Noise* (2006)
- **Qué es.** 10 min de **miles de imágenes solares crudas de la NASA** (las que
  la NASA normalmente *limpia*) montadas en time-lapse, dejando el **ruido**: la
  lluvia de partículas energéticas y viento solar como nieve de grano blanco
  sobre B/N. El sonido es radio solar real; el brillo de la imagen se traduce a
  frecuencia.
- **Link.** https://semiconductorfilms.com/art/brilliant-noise/ ·
  https://lux.org.uk/work/brilliant-noise/
- **QUÉ ROBAR.** La tesis central del proyecto hecha imagen: **el ruido/grano no
  se limpia, es el contenido**. Robar el "**rain of white noise**" como textura de
  polvo (los anillos de Saturno, el polvo de Crossing): grano que NO es post-fx
  sino materia, modulado por `rms_air`. Y la idea de **brillo↔frecuencia**: el
  grado de exposición de la imagen mapeado al audio. Es la justificación estética
  de que el grano CRT del style guide es firma, no defecto (Patrón 3).

### 1.6 Refik Anadol — *Machine Hallucinations* (2017–), *Unsupervised* (MoMA)
- **Qué es.** **Nébulas de datos**: millones de imágenes (espacio, naturaleza)
  procesadas con ML; la "mente máquina", inactiva, genera **alucinaciones** —
  nubes de color y forma fluyendo en el *latent space*, point clouds que se
  derraman y reconfiguran.
- **Link.** https://refikanadolstudio.com/projects/unsupervised-machine-hallucinations-moma/ ·
  https://refikanadol.com/works/machine-hallucinations-nature-dreams/
- **QUÉ ROBAR.** El **flujo de "nube de datos" que se deshace y se rehace** — la
  cualidad de fluido/point-cloud líquido para la nébula de Crossing y la
  saturación de Recursion. OJO con la trampa: Anadol es **muy color/espectacular**;
  acá se roba el *movimiento* (latent walk, derrame fluido) pero monocromo
  fósforo. Es la referencia natural para la **rama AI** (Deforum/AnimateDiff =
  latent walk casero): el "delirio" literalmente *es* una caminata por el espacio
  latente. Inversión de tropo §1.4 del doc 01: la nébula colorida → densidad
  monocroma.

### 1.7 Cymatics / patrones de Chladni — sonido → forma (CLAVE conceptual)
- **Qué es.** Vibración hecha visible: arena sobre una placa metálica excitada a
  una frecuencia se acomoda en **líneas nodales** (donde no hay movimiento),
  formando patrones geométricos. **Más alta la frecuencia → patrón más
  intrincado.** Hans Jenny (cymatics), Ernst Chladni (placas).
- **Link.** https://en.wikipedia.org/wiki/Cymatics ·
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10969725/ (modos resonantes,
  placas circulares y poligonales) ·
  https://www.sciencefriday.com/articles/seeing-the-patterns-in-sound/
- **QUÉ ROBAR.** Es **la metáfora literal del proyecto** ("arte de ondas
  sonoras") sin caer en ícono: un campo de partículas que se acomoda en **líneas
  nodales** dictadas por el `centroid`/`chroma_root` del audio. Frecuencia baja
  (sub-42Hz) = patrón simple y abierto; centroide alto = patrón denso e
  intrincado. La fórmula de modos de placa circular (funciones de Bessel /
  J_n(kr)·cos(nθ)) da **mandalas que son literalmente la frecuencia del track**.
  Une Belson/Whitney (mandala) + la tesis "materia prima compartida": el patrón
  NO ilustra el sonido, *es* su modo de vibración. Robar para la escena
  espiral/mandala del delirio.

### 1.8 Thomas Wilfred — *Lumia* / Clavilux (1919–)
- **Qué es.** "El octavo arte": **luz como forma autónoma**, sin sonido. El
  Clavilux es un órgano de proyectores con teclado que controla forma, color y
  movimiento; figuras de luz que se deslizan silenciosas, lentísimas, sin bordes
  duros — auroras, velos, formas que nunca se repiten.
- **Link.** https://americanart.si.edu/exhibitions/lumia ·
  https://en.wikipedia.org/wiki/Lumia_art
- **QUÉ ROBAR.** El **tempo**: Wilfred es la referencia de la *lentitud
  hipnótica sin esfuerzo* (hexagrama 24, Eno/Roach). Robar la cualidad "velo de
  luz que deriva" para las transiciones lentas y para Outbound: capas
  semitransparentes de fósforo que se cruzan, additive blend, **cero contorno**.
  Antídoto contra el "movimiento MTV". También: que un loop **nunca repita exacto**
  (Wilfred diseñaba ciclos de horas que no se repetían) → introducir deriva
  pseudo-aleatoria lenta para que el "delirio" no se sienta loopeado aunque loopee.

### 1.9 Stan Brakhage — *Mothlight* (1963), *The Dante Quartet* (1987), hand-painted
- **Qué es.** Cine sin cámara: pegar alas de polilla / pétalos / pasto entre
  cintas de 16mm (*Mothlight*), o pintar/rayar directo sobre la emulsión. **Flicker**:
  cada fotograma como evento explosivo, "verdad 24 veces por segundo".
- **Link.** https://en.wikipedia.org/wiki/Mothlight ·
  https://www.johncoulthart.com/feuilleton/2015/04/07/mothlight-a-film-by-stan-brakhage/
- **QUÉ ROBAR.** El **flicker frame-a-frame** y la **textura orgánica encima del
  cuadro**: para el "vinilo gastado que chicharrea" y el "renacer", inyectar grano
  que cambia *cada frame* (no animado suave) + manchas/rayas tipo emulsión
  dañada. En shader: `hash(uv + frame)` por frame, dropouts, scratches verticales.
  Es el antídoto contra el digital "demasiado limpio" — Brakhage da lo táctil/sucio
  del Concepto B sin recurrir al stargate.

### 1.10 Oskar Fischinger — *Studie* series, *Radio Dynamics*, *Motion Painting No.1*
- **Qué es.** Pionero del visual music: **paint-on-glass**, formas/colores
  sincronizados a la música nota por nota. Correlaciona shapes-líneas-color con
  notas-ritmos-armonías. También extrajo *sonido a partir de dibujos* (sonido
  sintético óptico).
- **Link.** https://en.wikipedia.org/wiki/Oskar_Fischinger ·
  https://blog.artsper.com/en/a-closer-look/the-father-of-visual-music-oskar-fischingers-experimental-legacy/
- **QUÉ ROBAR.** La **gramática del mapeo audio→visual** (lo que ya plantea el
  doc 01 §4 con envelope followers): forma = nota, ritmo = movimiento. Robar la
  *disciplina* de que cada gesto visual tenga su correlato sonoro exacto — pero
  con su lección de cuándo NO: Fischinger es a veces *demasiado* sincrónico
  (Mickey-Mousing). Para *Heliopause* (ambient), atar a *tendencias* (RMS, drone)
  más que a cada onset, salvo los "tropezones" puntuales.

### 1.11 Hilma af Klint — *The Ten Largest*, *Paintings for the Temple*, *The Swan*, *The Dove*
- **Qué es.** Pionera de la abstracción (predata a Kandinsky), mística teosófica.
  Pintaba "guiada por entidades". Vocabulario: **espirales = crecimiento/evolución**
  (el caracol = el universo), círculos = unidad, líneas entrelazadas =
  interconexión. Color simbólico: azul=femenino/espíritu, amarillo=masculino/
  conocimiento, verde=fusión, blanco=lo más sagrado.
- **Link.** https://www.thecollector.com/hilma-af-klint-work-recurring-symbols/ ·
  https://en.wikipedia.org/wiki/Hilma_af_Klint
- **QUÉ ROBAR.** Es la **lectura que valida el approach** (Patrón 7: lectura
  antes que Pinterest): la espiral como crecimiento que itera, no como ícono
  decorativo — exactamente la cosmología del EP. Cuidado con el color: NO robar su
  paleta literal (rompería el fósforo). Robar la **gramática de símbolos como
  estructura subyacente** (el caracol/espiral logarítmica gobierna la
  composición) y la idea de que la abstracción puede ser un *diagrama de fuerzas
  invisibles* — coherente con "panel de control / telemetría".

### 1.12 Tarkovsky — *Solaris* (1972)
- **Qué es.** Minimalismo cósmico, tempo larguísimo, el océano-mente de Solaris
  como superficie que piensa y se reconfigura, sin explicar.
- **Link.** (referencia de mood, ya citada en `13_visual_style_guide.md`)
- **QUÉ ROBAR.** El **permiso de la lentitud y del no-explicar** (críptico). Y la
  imagen de **superficie/fluido que se reorganiza solo** para el "humo/nébula" y
  el océano de Recursion: una membrana de densidad que ondula sin figura.

### 1.13 Shadertoy / demoscene / Hydra — el cómo técnico (todo gratis)
- **Qué es.** Recursos de raymarching volumétrico, FBM, domain warping, feedback
  buffers y túneles Droste, directamente portables al motor del proyecto.
- **Link.** Domain warping (Íñigo Quílez): https://iquilezles.org/articles/warp/ ·
  Volumetric raymarching (Xor/GM Shaders): https://mini.gmshaders.com/p/volumetric ·
  Cloudscapes (Maxime Heckel): https://blog.maximeheckel.com/posts/real-time-cloudscapes-with-volumetric-raymarching/ ·
  "Nebulous Tunnel" (Shadertoy): https://www.shadertoy.com/view/ltfBzM ·
  Hydra feedback/modulate docs: https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/modulate/
- **QUÉ ROBAR.** Las **recetas exactas**: nébula = FBM + domain warping (`f(p+h(p))`)
  acumulando densidad a lo largo del rayo; túnel = `length(p.xy)` + feedback con
  zoom; espiral = warp del feedback en polares con rotación. Estas son las piezas
  que el `accumulate.frag` / `post.frag` del repo ya tienen o pueden tener.

---

## 2 — Lenguajes visuales por concepto

Para cada concepto del EP, 2-3 formas **abstractas/místicas** de representarlo
(no literal), citando la referencia de §1. Todas respetan la anti-iconografía.

| Concepto | Lenguaje A | Lenguaje B | Lenguaje C |
|---|---|---|---|
| **nacimiento / volver a nacer** | Núcleo radial de luz que **emerge del negro y respira** (Belson §1.1) — densidad sin contorno. | Campo de partículas que **se condensa desde el ruido** hacia un punto (inverso del colapso; Whitney §1.2). | Velo de luz que se desliza y "se enciende" muy lento (Wilfred §1.8). |
| **oscuridad** | Negro casi total con **una sola brasa** tenue de fósforo dim (Belson). | "Ruido bajo" — grano apenas perceptible sobre negro, presencia sin forma (Semiconductor §1.5). | — |
| **"los latidos llaman"** | Pulso radial concéntrico sincronizado al sub-42Hz (`rms_sub42`), tipo onda en agua (cymatics §1.7). | Anillos nodales que aparecen/desaparecen con el latido (Chladni §1.7). | — |
| **despegue** | Deriva lenta de cámara **alejándose** del núcleo, sin destino (Wilfred/Tarkovsky tempo §1.8/§1.12). | Streaks tenues empezando a estirarse hacia afuera (pre-slit-scan; Trumbull §1.3). | — |
| **nébulas** | FBM + domain warping volumétrico, **densidad monocroma** (Shadertoy §1.13), no Hubble. | "Nube de datos" fluida que se deshace/rehace (Anadol §1.6), monocromo. | Membrana-océano que ondula (Solaris §1.12). |
| **polvo de los anillos de Saturno** | Río de partículas en flow field de curl-noise (Whitney movimiento armónico §1.2). | "Rain of white noise" como grano-materia, no post-fx (Semiconductor §1.5), modulado por `rms_air`. | — |
| **tropezones con rocas / dificultad en el andar** | Onset → **remolino puntual** que perturba el flow field + destello breve (Fischinger mapeo §1.10). | Glitch/dropout monocromo de 1-3 frames en el transiente (Ikeda §1.4). | Flicker tipo emulsión dañada (Brakhage §1.9). |
| **recursión / vuelta / retorno** | **Feedback buffer** con zoom+rotación leve = `f(x)=transform(f(x-1))` (Shadertoy §1.13). | Mandala que se reorganiza y vuelve "casi" al mismo estado, nunca idéntico (Whitney/Wilfred §1.2/§1.8). | Líneas nodales que colapsan al centro (cymatics inverso §1.7). |
| **vinilo gastado que chicharrea** | Grano frame-a-frame + scratches verticales + dropouts (Brakhage §1.9). | Barcode/glitch monocromo en ráfagas cortas (Ikeda §1.4). | `signal_red` asomando 1 vez al borde (style guide). |
| **spiral out** | Espiral SOLO en la **trayectoria** de partículas y en el **warp** del feedback (af Klint estructura §1.11), nunca trazada. | Mandala emergente de campo de puntos que rota y se abre (Whitney §1.2). | — |
| **el cruce de umbral (heliopausa)** | Túnel/fuga slit-scan con paleta **sucia solarizada** (Trumbull §1.3, Concepto B). | Inversión de fase: la deriva del flow field y la cámara **invierten sentido sin corte** (lore FICHA 02, 24°). | — |
| **el final flashero de 2001** | Corredor de luz que fuga al infinito, color enfermizo invertido (Trumbull §1.3). | Latent walk monocromo (Anadol §1.6) si se usa rama AI. | — |

---

## 3 — Storyboard del "delirio" para *Recursion* (3:00)

Un **viaje, no un loop estático**: ocho escenas que **transicionan** (morph /
cut duro / disolución) y mutan de un lenguaje visual a otro. La regla del
hexagrama 24 manda: nada "resuelve", todo *vuelve más afuera*. El último frame
debe quedar **idéntico al frame 0 de Outbound** (loop sin costura).

> Timecodes aproximados sobre 180s. Atar a los eventos reales del master cuando
> se tenga el `control.npz` de `03_recursion_master.wav` (ver `00_PLAN_status.md`).
> Audio→canal según `01_concept_python_shader.md` §3.

### Escena 1 — NACER · 0:00–0:18
- **Qué se ve.** Negro total. Una sola brasa de fósforo dim emerge del centro y
  **respira** una vez. Sin contorno. Grano apenas perceptible.
- **Referencia.** Belson *Allures* (núcleo que respira §1.1) + Wilfred (lentitud §1.8).
- **Audio.** Primer swell del drone (`rms` release lento) y el eco del pulso de
  Outbound una octava abajo (`rms_sub42`).
- **→ Transición a 2.** **Disolución lenta**: la brasa no se apaga, se *expande* y
  pierde foco hasta volverse humo (morph de núcleo→volumen).

### Escena 2 — HUMO / NÉBULA · 0:18–0:42
- **Qué se ve.** El núcleo se derrama en una **membrana de densidad** que ondula
  y llena el cuadro, monocroma. Se deshace y se rehace como si pensara.
- **Referencia.** Anadol *Machine Hallucinations* (nube fluida §1.6) + Solaris
  (membrana §1.12) + FBM/domain warping (§1.13).
- **Audio.** Capas del drone entrando (`rms`, `centroid` sube la "altitud" de la
  nébula); `flux` agita el domain warping.
- **→ Transición a 3.** **Morph por zoom**: la cámara empieza a "caer" hacia el
  centro de la nébula; el domain warping se estira radialmente → nace el túnel.

### Escena 3 — TÚNEL (el cruce de umbral) · 0:42–1:08
- **Qué se ve.** Corredor de luz que **fuga al infinito**, todo estirado en
  streaks radiales. Paleta empieza a **ensuciarse/solarizarse** (curva de
  luminancia parcialmente invertida). Aberración cromática leve.
- **Referencia.** Trumbull slit-scan / Star Gate (§1.3, Concepto B preset `stargate`).
- **Audio.** `rms_sub` empuja la velocidad de fuga (`u_spiralZoom`); `centroid`
  deriva el tinte sucio; `onset` = flashes solarizados puntuales.
- **→ Transición a 4.** **La fuga frena y rota**: el zoom hacia adentro baja, la
  rotación sube → el túnel se "enrosca" y se convierte en espiral/mandala.

### Escena 4 — ESPIRAL / MANDALA · 1:08–1:34
- **Qué se ve.** El campo se reorganiza en un **mandala que rota y respira** —
  patrón concéntrico que emerge de partículas/puntos, líneas nodales. La espiral
  está en la **trayectoria**, nunca dibujada.
- **Referencia.** Whitney *Lapis* (mandala desde puntos §1.2) + cymatics/Chladni
  (líneas nodales = la frecuencia del track §1.7) + af Klint (espiral=evolución §1.11).
- **Audio.** `centroid`/`chroma_root` definen el orden `n` del modo de placa
  (Bessel J_n) → patrón más o menos intrincado según el brillo del audio.
- **→ Transición a 5.** **El mandala se "descose"**: las líneas nodales se sueltan
  y el patrón ordenado se vuelve río de polvo turbulento (orden → caos).

### Escena 5 — POLVO / ROCAS (el andar difícil) · 1:34–2:02
- **Qué se ve.** Río de **miles de partículas** arrastradas por curl-noise (polvo
  de los anillos). Los onsets = **remolinos puntuales + destellos** (rocas) y
  **dropouts/glitch** de 1-3 frames (tropezones).
- **Referencia.** Whitney (flujo armónico §1.2) + Semiconductor (grano-materia,
  "rain of white noise" §1.5) + Ikeda (glitch puntual §1.4) + Brakhage (flicker §1.9).
- **Audio.** `flux`→turbulencia; `onset_flag`→remolino+glitch; `rms_air`→densidad
  del polvo brillante.
- **→ Transición a 6.** **Cut casi-duro en un onset fuerte**: un dropout grande
  "traga" el cuadro → arranca el chicharreo del vinilo.

### Escena 6 — VINILO / CHICHARREO · 2:02–2:24
- **Qué se ve.** Grano frame-a-frame intenso, **scratches verticales**, dropouts
  tipo salto de púa, barcodes monocromos en ráfaga. `signal_red` asoma **una
  sola vez** en un borde.
- **Referencia.** Brakhage (emulsión dañada §1.9) + Ikeda (barcode/glitch §1.4).
- **Audio.** `flux`→intensidad del glitch; `onset_flag`→dropout; `rms` sigue
  creciendo por debajo (el drone que ocupa todo).
- **→ Transición a 7.** **Saturación creciente**: el feedback buffer empieza a
  comerse cada frame; el chicharreo se "ahoga" en el feedback que crece.

### Escena 7 — COLAPSO / FEEDBACK (la recursión) · 2:24–2:48
- **Qué se ve.** El **feedback buffer toma protagonismo**: cada frame se come al
  anterior con zoom+rotación espiral; las partículas se **reabsorben al centro**.
  Aparecen ecos deformados de las escenas previas (recall visual).
- **Referencia.** Feedback Droste (§1.13) + Belson (reabsorción al núcleo §1.1) +
  cymatics inverso (colapso de nodos §1.7).
- **Audio.** `rms`→`u_feedbackGain` (release MUY lento, crece y crece);
  `rms_sub42`→`u_spiralZoom`; `centroid`→`u_decay`.
- **→ Transición a 8.** **El colapso "atraviesa" el centro**: cuando el feedback
  llega al máximo, todo se reabsorbe en un punto y **renace** como brasa.

### Escena 8 — RENACER / LOOP · 2:48–3:00
- **Qué se ve.** Del punto saturado **vuelve a emerger la brasa de la Escena 1**,
  pero "ya no es lo mismo" (deriva mínima, leve rotación residual). El cuadro
  queda **idéntico al frame 0 de Outbound**.
- **Referencia.** Belson (núcleo §1.1) + Wilfred ("el loop nunca repite exacto" §1.8)
  + hexagrama 24 / Fù (el retorno).
- **Audio.** El cierre de Recursion engancha armónicamente con la apertura de
  Outbound (`02_cosmologia.md` §V). `u_collapse`→cierre.
- **→ Transición.** **Loop sin costura** → vuelve a Escena 1 / Outbound. *La
  espiral dio otra vuelta, más afuera.*

> **Por qué es delirio y no loop estático:** cada escena habla un lenguaje
> distinto (Belson→Anadol→Trumbull→Whitney→Semiconductor→Brakhage→feedback) y
> **muta** al siguiente por morph/zoom/cut. El loop solo cierra al final; el
> interior es un viaje que no se repite. La deriva pseudo-aleatoria lenta
> (Wilfred §1.8) garantiza que ni siquiera el loop se sienta idéntico vuelta a
> vuelta.

---

## 4 — Hints por rama (cómo lograr cada escena)

Para cada escena: (a) shader GLSL (motor del repo, columna vertebral), (b) Hydra
(textura/exploración), (c) AI Deforum/AnimateDiff (restyle/acabado opcional).

### Escena 1 — NACER
- **(a) GLSL.** `accumulate.frag`: glow radial additive `exp(-d*k)` desde el
  centro, `k` modulado por `u_pulse` (=`rms_sub42`). Sin feedback. Grano dim.
- **(b) Hydra.** `shape(64,0.0,0.8).color(0.65,0.84,0.37).luma(0.1).out()` + un
  `osc` lento muy tenue; mantener brillo bajo.
- **(c) AI.** Init negro + prompt `"single dim green ember emerging from black,
  abstract, no object"`, strength alta (~0.9) para casi no mover.

### Escena 2 — HUMO / NÉBULA
- **(a) GLSL.** Raymarch volumétrico: densidad = FBM(p) con **domain warping**
  `d = fbm(p + fbm(p))`; acumular a lo largo del rayo; mono fósforo. `centroid`→
  altura, `flux`→amplitud del warp. (Receta: iquilezles.org/articles/warp §1.13.)
- **(b) Hydra.** `noise(3,0.1).modulate(noise(2,0.05)).color(...).luma(0.3,0.2).out()` —
  el `modulate(noise)` ES el domain warping.
- **(c) AI.** Prompt `"monochrome green volumetric smoke, flowing data cloud,
  latent space, abstract"`; zoom 1.0; strength ~0.6 para que fluya (Anadol look).

### Escena 3 — TÚNEL
- **(a) GLSL.** Coordenadas polares; feedback buffer con `uv = center +
  (uv-center)*u_zoom` (zoom>1 = volar hacia adentro) + rotación pequeña.
  Solarizar en `post.frag`: `mix(c, 1.0-c, u_solarize)`. `u_chroma` para
  aberración. `u_spiralZoom`=`rms_sub`.
- **(b) Hydra.** `src(o0).scale(1.04).rotate(0.01).modulate(noise(2),0.02)
  .colorama(0.02).out(o0)` — el `scale(1.0X)` sobre `o0` = túnel infinito.
- **(c) AI.** Deforum: `zoom: 1.04` sostenido, prompt `"slit-scan light corridor,
  solarized chemical landscapes, desaturated mineral colors, dirty film grain,
  no horizon"`; strength ~0.5; FILM/RIFE para suavizar (§1.13 / Deforum docs).

### Escena 4 — ESPIRAL / MANDALA
- **(a) GLSL.** Partículas (ping-pong) cuya posición sale de modos de placa
  circular: `r,θ` con amplitud ∝ `J_n(k·r)·cos(n·θ)`, `n`=`f(centroid)`. O Lissajous
  acoplados (Whitney). Rotación global lenta.
- **(b) Hydra.** `osc(20,0.05).kaleid(8).rotate(0,0.05).modulate(o0,0.01).out()` —
  `kaleid` da el mandala; `n` del kaleid mapeado a la FFT (`a.fft[0]`).
- **(c) AI.** Prompt `"symmetric mandala of green dots, kaleidoscopic, harmonic,
  abstract light points"`; bajo movimiento, IPAdapter para no derivar.

### Escena 5 — POLVO / ROCAS
- **(a) GLSL.** Particle sim con **curl-noise** flow field, `flux`→turbulencia.
  `onset_flag`→inyectar un vórtice en `u_impactPos` + flash. Grano-materia
  (`rms_air`) sumado, no post.
- **(b) Hydra.** `noise(8,0.5).thresh(0.6).modulate(noise(4),0.3).add(o0,0.4)
  .out()` + disparos por audio en los picos de `a.fft`.
- **(c) AI.** Prompt `"river of dust particles, Saturn rings debris, monochrome
  grain, turbulent flow"`; AnimateDiff para coherencia temporal del flujo.

### Escena 6 — VINILO / CHICHARREO
- **(a) GLSL.** `post.frag`: `hash(uv + u_frame)` por frame (grano que cambia
  cada cuadro = Brakhage), scratches `step(rand, x)` verticales, dropouts cuando
  `onset_flag`. `signal_red` 1 vez. Barcode: `step(0.5, fract(uv.x*N))`.
- **(b) Hydra.** `src(o0).add(noise(200,2),0.3).modulate(noise(1,0.1),0.05)
  .out()` + `.luma()` duro para dropouts.
- **(c) AI.** Menos útil acá (AI suaviza, queremos lo contrario) — mejor hacer
  esta escena en GLSL/Hydra y, si se usa AI, aplicar el glitch en **post** sobre
  el render AI.

### Escena 7 — COLAPSO / FEEDBACK
- **(a) GLSL.** Feedback buffer protagonista: `frame_N = sample(frame_{N-1},
  warp=zoom·rot espiral) * decay + nuevo`. `u_feedbackGain`=`rms` (release muy
  lento). Partículas con flow field **invertido** (hacia el centro).
- **(b) Hydra.** `src(o0).scale(0.98).rotate(0.02).color(1.01,1.01,1.01)
  .out(o0)` — `scale<1` + acumulación = la imagen se traga a sí misma hacia el centro.
- **(c) AI.** Deforum con `zoom` oscilando + strength alta (~0.8) = el clásico
  "Deforum se come a sí mismo"; útil para el recall deformado de escenas previas.

### Escena 8 — RENACER / LOOP
- **(a) GLSL.** `u_collapse` reabsorbe partículas al centro y baja todo a la
  brasa de Escena 1; **forzar** el último frame == estado inicial (mismo encuadre/
  glow) para loop sin costura. Verificar en QA visual.
- **(b) Hydra.** Volver al patch de Escena 1 con un cross-fade de los últimos N
  frames sobre los primeros.
- **(c) AI.** Cerrar el latent walk en el seed/prompt inicial de Escena 1 para
  que el loop empalme.

---

## 5 — Notas de disciplina (no romper)

- **Anti-iconografía siempre:** la espiral vive en trayectoria y warp, **nunca**
  como trazo. Nada de Hubble/planetas/caras/EQ bars.
- **Color:** base phosphor mono (`#a6d65f`/`#6a9034` sobre `#0d1014`). El "sucio
  solarizado" del túnel (Concepto B) es desaturado mineral, **no** neón. `signal_red`
  y `warm_amber`: 2-3 veces en TODO el video, nunca recurrentes.
- **Tempo:** hexagrama 24 = *movimiento natural, sin esfuerzo*. Lento e hipnótico
  (Belson/Wilfred/Tarkovsky), nunca epiléptico/MTV. El glitch es la única señal
  rápida, y solo en ráfagas cortas (Ikeda).
- **Materia prima compartida:** todo gesto se ata a un canal del `control.npz`
  (no animación a mano). Si una escena se ve igual con o sin el audio, está mal
  (prueba de Romagosa, `01_concept_python_shader.md` §1.2).
- **El loop nunca repite exacto:** deriva pseudo-aleatoria lenta (Wilfred) para
  que el "delirio" no se sienta loopeado aunque loopee.

---

## Versión

v1 — 2026-05-21 — research online profundo de referencias de visual music / cine
experimental / estética de datos / cymatics / abstracción mística, destilado en
catálogo "qué robar", lenguajes por concepto, storyboard del delirio de Recursion
y hints por rama (GLSL/Hydra/AI). Base para construir el video que transiciona
entre conceptos.
