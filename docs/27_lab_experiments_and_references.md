# 27 — Lab: experimentos futuros + referentes sónicos

> **Qué es esto.** El lugar único para volver a los experimentos/próximos tracks
> que el user quiere explorar, con research corroborado. Si en el futuro
> preguntás "¿qué querías experimentar?", empezá acá. Fecha: 2026-07.

## Índice de material ya existente (no re-authorear — levantar de acá)

- **Referentes de composición** (Eno, Roach, Stars of the Lid, Zimmer,
  **Lustmord**, Tim Hecker, Basinski, vocal drone) → `docs/11_research_composition.md`.
- **Diseño sonoro por track** (opciones A–D con texturas industriales/glitch/
  tectónicas) → `docs/06_diseno_sonoro.md`.
- **Game of Life + síntesis modular** (autómatas celulares → sonido, tesis
  Ernesto Romeo, Lenia, plan de experimento VCV Rack) → `docs/22_game_of_life_sintes_modulares.md`.
- **Próximas transmissions** (backlog dashboard): **TX02 'Em+H'** (sobre el
  amor), **TX03 'Rescue 100'** (rescate en planeta con flores), trabajo de
  framework `aem`.

Los dos hilos nuevos de abajo (A y B) son los que faltaba documentar.

---

## A · Experimento: síntesis desde las tripas de la máquina ("Silicon")

**La idea del user.** En vez de partir de lo analógico (VCO, tensión),
partir de lo **físico/digital de la propia máquina**: páginas leídas de
memoria, señales al CPU, actividad de buses, etc. — y que ESO sea el *input*
y los *moduladores* de una voz de synth "de silicio". Nombre propuesto para
el instrumento: **Silicon** (o "síntesis in-silico" / "machine-native
synthesis"). Pregunta del user: ¿existe? ¿qué hay?

**Qué existe (corroborado).** El espacio existe pero fragmentado; nadie
tiene exactamente "el estado de la máquina como CV de un synth-instrumento".
Piezas del rompecabezas:

1. **Bytebeat** (Viznut, ~2011). Música generada por una expresión aritmética
   corta en C evaluada sobre un contador `t` (ej. `t*(t>>5|t>>8)`). Es
   literalmente "hacer música con aritmética de la CPU". El más cercano a "el
   silicio suena". Fácil de prototipar en el navegador.
2. **Sonificación de actividad del sistema.** De lo accidental (ingenieros
   sintonizaban una radio AM al lado del mainframe para "oír" el estado del
   programa; se colgaban parlantes a registros índice) a lo intencional
   (paper May-2026: sonificación en tiempo real de un supercomputador con
   música estilo EDM, tratando miles de cores como "orquesta mecanizada").
3. **Emanaciones electromagnéticas / coil whine.** Las bobinas (inductores)
   vibran con la corriente alterna y emiten sonido audible; con un pickup de
   bobina (tipo el trabajo de **Christina Kubisch**, "electromagnetic walks")
   se escucha directamente el EMF de CPU/GPU/fuentes. Input físico real de la
   máquina.
4. **Leer memoria/dispositivos como audio.** Truco clásico Unix: pipear
   `/dev/mem`, `/dev/urandom`, `/proc/*` o buffers crudos a la salida de audio
   (`/dev/dsp`) → ruido estructurado por el estado real del sistema.

**Veredicto honesto.** Los ladrillos existen (bytebeat, sonificación, EMF,
`/dev/*`→audio). Lo que NO está muy explorado —y sería lo nuestro— es tratar
**el estado interno de la máquina (páginas de memoria, contadores, IRQs,
temperatura, carga por core) como fuentes de modulación (CV) de una voz de
synth tocable**, con mapeos musicales (no solo "ruido de datos"). Ahí hay
hueco real para un instrumento propio, muy alineado con el linaje del proyecto
(Python/NumPy, "el foco es la data" — ver `docs/07_vision.md`).

**Primer experimento mínimo (en tu Mac, sin comprar nada):**
1. Bytebeat en el navegador (greggman/wurlitzer o similar) → 20 min jugando
   con expresiones → grabar las que peguen.
2. Script Python que lea métricas del sistema (`psutil`: CPU% por core, RAM,
   I/O, temperatura) a ~30 Hz → normalizar → usarlas como envolventes/LFOs que
   modulen una voz del framework `aem` (filtro, pitch, amplitud). Es el "hello
   world" de **Silicon**, reusando el framework que ya tenemos.
3. (Avanzado) Pickup de bobina barato → grabar el EMF del Mac bajo distinta
   carga → tratarlo como field recording (ver hilo B).

---

## B · Experimento: dark ambient por deformación digital (línea Lustmord)

**Corroboración pedida por el user: SÍ, es así.** Lustmord (Brian Williams)
**no usa synths modulares** — todo es manipulación digital de grabaciones.
Citas de las fuentes:

- *"Lustmord wasn't interested in messing around with synths… instead of
  battling with modular synths, which he was never comfortable with, Williams
  could sit in front of the computer screen and manipulate samples with a
  mouse."* No hay synths en vivo en sus discos solistas desde hace años.
- Trabaja desde una **biblioteca enorme de sonidos**: field recordings
  (criptas, cuevas, mataderos — elegidos por su **acústica**, no por lo
  siniestro), library music, y fuentes insólitas: **NASA Jet Propulsion Lab**,
  archivos del **Manhattan Project / Los Álamos**.
- Desde *Heresy* (1989) el core es sampling + manipulación digital (arrancó
  usando un **Atari** como DAW) + reverb/efectos para "cosmic horror".
- Método: prepara material y lo **mezcla/combina al vuelo** ("más
  interesante"). "Diseñar sonidos y después diseñar atmósferas y paisajes".

**La técnica, desglosada (lo que hace ese ambient retorcido):**
- **Time-stretch extremo** (estirar un sonido corto a minutos) → el truco
  central. Herramienta canónica gratis: **PaulStretch / PaulXStretch**.
- **Pitch down** 1–2 octavas → sub-bass cavernoso desde voz/objeto cotidiano.
- **Convolution reverb con IRs de espacios reales** (criptas, tanques) → el
  "lugar". En Ableton: Hybrid Reverb / Convolution Reverb (Max for Live).
- **Granular / spectral freeze** → congelar y difuminar texturas.
- **Layering** de muchas capas graves + no-musicales (roces, ruido, EMF).
- **Saturación/tape** sutil para pegar y ensuciar.

**Tu rig actual (Volt 276 + LUNA + Ableton Live Lite) alcanza y sobra.**
- **Volt 276**: interfaz con compresor 1176-style onboard + bundle de plugins
  (amps/delays). Sirve para grabar (voz sostenida, objetos, cuarto).
- **Ableton**: modo **Warp** (Texture/Complex Pro) para time-stretch extremo +
  granular; efectos nativos.
- **LUNA**: DAW de UA, buena para tape/summing.
- **Gratis para bajar (Mac):** **PaulXStretch** (stretch infinito),
  **Valhalla Supermassive** (reverb/delay enorme), **Valhalla Freq Echo**,
  **SoundHack** / **GRM Tools** (spectral, históricos de esta escuela),
  IRs gratis de espacios reales para convolution.

**Otros referentes de la misma familia (para robar técnica):**
- **Thomas Köner** (gongs pitcheados abajo, glaciar), **Deathprod**,
  **Biosphere**, **Tim Hecker** y **William Basinski** (degradación de tape —
  ya en `docs/11`), **Ben Frost**, **Roly Porter**, **The Caretaker**
  (deformación de discos de 78rpm), **Kevin Richard Martin**.

**Receta de primer track (mejor que el prompt que te pasó la otra IA, y en
la voz del proyecto):**
1. Grabar 1 fuente humilde con la Volt 276: voz sosteniendo una nota, o el
   motor de la heladera, o el cuarto en silencio.
2. En Ableton: Warp Complex Pro → estirar ×20–×100. Duplicar, una capa −12 y
   −24 semitonos (sub).
3. Convolution reverb con IR de un espacio grande, Mix alto (60–90%).
4. Valhalla Supermassive en un return, feedback largo → cola infinita.
5. Capa de EMF/coil del Mac (hilo A) como textura de fondo.
6. Automatizar lento (todo en minutos, no en segundos — es ambient).

> **Nota sobre el prompt que te pasaron.** Está bien como punto de partida
> (PaulXStretch, Supermassive, Warp, Mix alto son correctos). Lo guardamos
> como referencia externa, pero esta receta ya está adaptada a tu rig y a la
> estética ÆM (Heliopause: sonda, data, cruce — no "hacer temblar los vidrios").

---

## Cómo retomar

- Para **Silicon** (hilo A): arrancar por bytebeat + script `psutil`→`aem`.
- Para **Lustmord/deformación** (hilo B): bajar PaulXStretch + Supermassive y
  hacer el track de 6 pasos. Puede alimentar **TX02/TX03** o un EP de estudio.
- Ambos conviven con el framework `aem` (código puro) — no lo reemplazan, lo
  extienden con material grabado/deformado y con fuentes de la máquina.

## Fuentes (corroboración)

- Lustmord — Red Bull Music Academy Daily: https://daily.redbullmusicacademy.com/2015/10/lustmord-feature/
- Lustmord — Equipboard (gear): https://equipboard.com/pros/lustmord
- Lustmord — Wikipedia: https://en.wikipedia.org/wiki/Lustmord
- Where to Begin With Lustmord (Bandcamp Daily): https://daily.bandcamp.com/lists/lustmord-albums-list
- Sonificación de supercomputador (arXiv, 2026): https://arxiv.org/html/2605.21874
- Coil whine / EMF (Corsair explainer): https://www.corsair.com/us/en/explorer/diy-builder/power-supply-units/what-is-coil-whine/
