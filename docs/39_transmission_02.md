# 39 — Transmission 02: la caída al planeta

> Estado: **concepto + labs**. La forma se define experimentando, no planificando.
> Bajado por el user el 2026-07-31.
>
> Este doc reemplaza y fusiona dos entradas viejas del Lab: `tx-02-em-h`
> ("Em+H, sobre el amor") y `tx-03-rescue-100`. Eran dos transmisiones separadas y
> ahora son **dos tracks de la misma**.

## La narrativa

**TX02 pasa en el planeta que se vislumbra en Heliopause** — ese que aparece con los
anillos trastocados en Transmission 01. TX02 es **la caída a ese planeta**.

Tres tracks, tres momentos:

| # | Track | Qué pasa | Referencia sonora |
|---|---|---|---|
| 1 | *(nombre a definir)* | **El pasaje por la atmósfera.** La entrada | Lustmord. Ya en marcha → `lab/thermal_mass/` |
| 2 | **Rescue 101** | **La vida en el planeta**: flora y fauna local, flores, plantas, pájaros | Steve Roach / **KMRU**. Lab → `lab/rescue_101/` |
| 3 | **+H** | **El amor.** La conexión con el planeta, un portal que se abre, una fuerza superior que lo invade | Synth modular |

### Un motor distinto por track

No es capricho. Cada herramienta produce un tipo de material distinto, y eso separa
los tres tracks sin que haya que forzarlo.

| Track | Motor | Qué produce |
|---|---|---|
| 1 | **Python + numpy** (`framework/`, `scripts/paulstretch.py`) | Deformación de grabaciones. Offline, determinista, mineral |
| 2 | **Pure Data** → `docs/40_pure_data_lab.md` | Generación por reglas. Vivo, nunca igual dos veces, orgánico |
| 3 | **VCV Rack 2** | Modulación de voltaje. Se autoorganiza, no se toca |

El arco es descendente y después ascendente: caés, encontrás que hay vida, y te
conectás con algo más grande que vos.

## Track 1 · el pasaje por la atmósfera

Ya existe como cuatro capas en `lab/thermal_mass/`. Falta el nombre.

**Candidatos** (el registro del proyecto: término técnico real, doble sentido, sin
explicar):

| Nombre | Por qué |
|---|---|
| **Ablation** | El escudo térmico sobrevive **perdiendo parte de sí mismo**: se consume por diseño. La nave llega porque se deja quemar. Para una caída, es exacto |
| **Blackout** | Durante la reentrada el plasma **bloquea la radio**: la transmisión se corta. Un proyecto que se llama "transmisiones" con un track donde la transmisión muere |
| **Peak Heating** | El instante de carga térmica máxima |
| **Aerobraking** | Frenar usando la atmósfera. Técnico y poco conocido |
| **Terminal** | Velocidad terminal, y terminal como final y como estación |
| **Shock Layer** | La capa de gas comprimido delante del vehículo |

Los dos primeros son los fuertes. **Ablation** dice lo que le pasa al cuerpo,
**Blackout** dice lo que le pasa a la señal.

## Track 2 · Rescue 101

**Referencia**: KMRU — *By Absence* (del álbum *Kin*, 2026, **20:22**). Field
recording más drone, largo, paciente, **no oscuro**. Y Steve Roach del lado del
sostenido cálido.

Es el track más luminoso de los tres: hay vida. Contra el track 1, que es
mineral y violento, este es orgánico.

**Qué hay que experimentar** (sin decidir todavía):

- **Pianito MIDI o guitarra por la Volt 276.** Es el primer track del proyecto que
  admitiría material tocado. Ojo con la afinación si se cruza con material del
  track 1 (ver abajo).
- **Ableton Live Lite** grabando cosas propias.
- **Field recording de verdad**: pájaros, hojas, agua, insectos. Para este track las
  fuentes orgánicas no son una capa de grano, son **el tema**.
- Lo que hace KMRU y no hacemos todavía: dejar que la grabación de campo se
  escuche **como grabación**, sin deformarla del todo.

**Y acá entra la capa que falta en todo el proyecto**: la de grano (1-6 kHz, ver
`docs/38`). Track 2 es donde vive naturalmente.

## Track 3 · +H

### De dónde sale el nombre

**Em+H es la fusión.** Em más H. El track se llama **+H** por la suma: el momento en
que eso se agrega y ya no se puede restar.

Eso es material del **cuento**, no del tracklist, y va a desarrollarse cuando se
escriba. Importa registrarlo porque define el método del proyecto: en Heliopause el
cuento (`docs/10_cuento.md`) es la fuente de **todos** los textos públicos — los 13
fragmentos cifrados de `textos.md` salen de ahí, y de ahí salen los posts, los
captions y las bios. TX02 va a necesitar su propio cuento antes de tener voz
pública.

> **Ojo con una confusión heredada**: la entrada vieja del Lab decía "Em+H —
> colaboración con Helen". Son dos cosas distintas. Em+H es narrativa. Si hay
> colaboración con Helen, es una decisión aparte y hay que confirmarla.

### El sonido

**Synth modular**, simulado. El tema es el amor: la conexión con el planeta, el
portal, la fuerza superior que invade.

Herramientas para probar:

- **VCV Rack 2** — gratis, el estándar de los simuladores modulares, biblioteca
  enorme de módulos. Corre standalone y también hay versión plugin para meterlo
  dentro de Live.
- **Cardinal** — fork libre de VCV, viene como plugin.
- **Bitwig Grid** o **Softube Modular** si algún día se paga algo.

Hay research previa del proyecto que aplica directo: `docs/22_game_of_life_sintes_modulares.md`
(autómatas celulares y síntesis modular). Un patch **generativo que se
autoorganiza** es la forma más literal de "una fuerza superior que lo invade": el
tema no se toca, se deja correr.

## Los Ramanes y la obsesión con el tres

En *Cita con Rama* la última línea del libro es que **los Ramanes hacen todo por
triplicado**. Tres tracks es honrar eso, y está bien.

**Corrección honesta sobre el nombre del planeta**: en Rama **no hay ningún
planeta**. Rama es una nave cilíndrica. Lo que hay adentro son ciudades bautizadas
por los exploradores con nombres terrestres (New York, London, Rome, Paris, Peking,
Moscow), el **Mar Cilíndrico**, y las tres escaleras: **Alpha, Beta, Gamma**. En las
secuelas aparece **el Nodo**, una instalación Raman.

Así que hay dos caminos:

1. **Usar las tres escaleras como estructura interna**: Alpha, Beta, Gamma como
   subtítulo o marca de los tres tracks. Es canónico, es tres, y nadie lo va a
   descifrar de entrada.
2. **Nombrar el planeta con la lógica del tres, no con un nombre de Rama.** Mi
   propuesta: **Trine**. Es un término astronómico real — el aspecto de 120° entre
   dos cuerpos, o sea **exactamente un tercio del círculo**. Celeste, técnico, y
   lleva el tres adentro sin decirlo.

## Duración: 3:33 los tres es demasiado corto

Sí, te está acotando, y bastante. Tres razones:

- **El lenguaje del género es la duración.** En dark ambient un tema de 3:33 lee
  como boceto. La escala temporal no es un detalle: es parte del material.
- **Tu propia referencia dura 20:22.** KMRU trabaja en esa escala, y Steve Roach
  también (*Structures from Silence* son tres temas para 45 minutos).
- **Y tu propio catálogo**: Outbound son 8:00 exactos. Un 3:33 después de eso lee
  como recorte, no como decisión.

Pero la obsesión del tres se puede honrar en otra escala. Opciones, de mejor a peor:

| Opción | Total | Comentario |
|---|---|---|
| **11:11 cada uno** | **33:33** | El tres en las dos escalas, dígitos repetidos, y cada track con aire para respirar. **La que recomiendo** |
| Libres, sumando 33:33 | 33:33 | Más flexible: el track 1 puede ser 8:00 y el 3 más largo. Se pierde la simetría |
| 3:33 los tres | 9:59 | Cripplea los tres, sobre todo el de Lustmord |
| 3:33 como interludio | — | Un cuarto elemento corto de exactamente 3:33 entre tracks. Ahí el número entra sin costo |

Y hay continuidad de práctica: **Heliopause ya tiene su firma numérica** (8 + 13 + 3
= 24, el hexagrama 24 復, "el retorno"). Que TX02 tenga la suya —33:33— es seguir la
costumbre, no repetirla.

## Cosas que ya existen y aplican

- **`lab/thermal_mass/`** — track 1 en marcha, cuatro de seis capas.
- **`docs/38_capas_dark_ambient.md`** — anatomía de capas y qué fuente grabar.
- **`docs/22_game_of_life_sintes_modulares.md`** — CA + modular, para el track 3.
- **`docs/16_video_H_helen_collab.md`** — el concepto visual de "CERN legos
  florecidos, lianas, pajaritos", paleta azul/blanco/rojo/negro. **Es el mismo
  mundo que el track 2**: infraestructura reclamada por la naturaleza. Vale releerlo
  como material visual de TX02 y no como un video aparte.
- **El cuento de Heliopause** (`docs/10_cuento.md` / `10_cuento_en.md`) — no por su
  contenido sino por el **método**: cuento primero, fragmentos después, voz pública
  al final. TX02 necesita el suyo, y ahí vive Em+H.

## Lo que falta decidir

1. Nombre del track 1 (Ablation / Blackout / otro).
2. Nombre del planeta (Trine / algo de Rama / otro).
3. Duración: 11:11 × 3, o libre sumando 33:33.
4. **Escribir el cuento de TX02.** Es lo que después da los textos, los fragmentos
   y los posts. Em+H vive ahí.
5. Si hay colaboración con Helen y dónde (es una decisión separada de Em+H).
6. Y lo más urgente, que es material y no concepto: **salir a grabar**. Para el
   track 1 faltan las capas de grano y aire; para el track 2, todo lo orgánico.
