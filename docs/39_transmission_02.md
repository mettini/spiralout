# 39 — Transmission 02: la caída al planeta

> Estado: **concepto + labs**. La forma se define experimentando, no planificando.
> Bajado por el user el 2026-07-31.
>
> Este doc reemplaza y fusiona dos entradas viejas del Lab: `tx-02-em-h`
> ("Em+H, sobre el amor") y `tx-03-rescue-100`. Eran dos transmisiones separadas y
> ahora son **dos tracks de la misma**.

## La narrativa

**TX02 pasa en el planeta que se vislumbra en Heliopause**, ese que aparece con los
anillos trastocados en Transmission 01. TX02 es **la caída a ese planeta**.

### El punto de vista: la entidad (decidido 2026-08-08)

**TX02 no se narra desde la sonda. Se narra desde el planeta.**

El narrador es **una entidad de esa civilización**, y es **la misma voz en los tres
tracks**. No hay salto de punto de vista a mitad del disco.

| # | Qué ve la entidad |
|---|---|
| 1 | Algo cae por su atmósfera. No sabe qué es |
| 2 | Se acerca y lo recorre. Al mostrarle su mundo, nos muestra la flora y la fauna |
| 3 | Se funde con lo que cayó |

La versión descartada era que el track 2 pasara al punto de vista de la nave
recorriendo el planeta. Se descarta porque rompe lo único que sostiene el misterio:
**que quien narra no es humano y nunca explica**. Si la nave turistea, el disco pasa
a ser una crónica. Que sea la entidad la que enseña su mundo es más opaco y más
inquietante con el mismo material.

### Esto ya estaba plantado en el cuento de Heliopause

No es un giro nuevo. La ficha de cierre de `docs/10_cuento.md` termina enumerando
hipótesis sobre la firma que volvió, y la segunda dice:

> **2.** captura de una señal de retorno emitida por **un agente externo**

Ese agente externo es la entidad. Ya estaba escrita como hipótesis, sin desarrollar.

Y la misma ficha registra la evidencia física de la fusión:

> **ALTERACIÓN DE FIRMA:** presencia de un carácter no autorizado en los metadatos
> de origen; consiste en una ligadura cerrada por arriba, montada sobre la vocal
> abierta de la firma original

Eso es la **Æ**: A y E fundidas en un solo glifo. Heliopause cierra con la prueba de
que la firma que volvió tiene algo adentro que antes no estaba. **El track 3 es la
explicación de esa Æ.** El final de TX02 ya está escrito al final de TX01.

### Referencia de método: Lem, *Solaris*

No por prestigio: el mecanismo sirve entero. El planeta es la inteligencia, el
contacto nunca se traduce en comunicación, y la forma en que la entidad responde es
fabricar algo desde la memoria del otro. Eso es el track 3.

Ya está en el repo como referencia visual (`docs/video/05` §1.12, la membrana-océano
que ondula).

**La regla dura que se toma de ahí: la entidad no explica nunca, y el contacto
transforma en vez de comunicar.**

Sobre el registro de las oraciones no hay que inventar nada: el de `docs/10_cuento.md`
ya es impersonal y sin nombres ("lo lanzado carecía de nombre y de memoria"), que es
justo lo que necesita una entidad narrando. Lo único que se mueve es la posición: en
TX01 el narrador observa desde afuera, en TX02 narra desde adentro.

### Los tres tracks

| # | Track | Qué pasa | Referencia sonora |
|---|---|---|---|
| 1 | **bj3 n pt** | **El pasaje por la atmósfera**, visto desde abajo. Algo entra | Lustmord. Ya en marcha → `transmissions/02/bj3_n_pt/` |
| 2 | **Rescue 101** | **La vida en el planeta**: flora y fauna local, flores, plantas, pájaros | Steve Roach / **KMRU**. Lab → `lab/rescue_101/` |
| 3 | **+H** | **El amor.** La fusión. La Æ | Synth modular |

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

## Track 1 · bj3 n pt

**Nombre decidido por el user el 2026-08-10.**

*bj3 n pt*, se lee **bia-en-pet**, es el nombre que los egipcios le daban al metal
meteórico: **hierro del cielo**. No era una figura retórica, era una descripción de
origen: la daga de Tutankamón está hecha de un meteorito, confirmado por análisis de
composición en 2016. Tenían la palabra porque tenían el objeto.

Encaja en tres niveles:

| | |
|---|---|
| **Literal** | Es lo que la entidad ve: algo de metal cayendo del cielo |
| **Narrativo** | Algo que cayó terminó siendo parte de una persona. Eso es el track 3 |
| **De registro** | Término real, doble sentido, y nadie lo va a descifrar de entrada |

### Por qué no rompe con el protoindoeuropeo

Son dos voces distintas y la diferencia sostiene el marco:

- La **entidad recita** en PIE (`docs/42`). Es su lengua.
- El **archivo cataloga** en egipcio. Es la lengua de quien recibe y nombra.

El cuento de Heliopause ya es un expediente que rotula cosas que no entiende. Que le
ponga a lo que cayó el nombre que una civilización humana usaba para el metal del
cielo es exactamente lo que haría ese archivo. **La entidad no sabe que se llama así.**

### Cómo se escribe, y por qué con 3

**Se escribe `bj3 n pt`. Cerrado.**

La primera consonante es el **alef egiptológico**, cuyo carácter propio es `ꜣ`
(U+A723, LATIN SMALL LETTER EGYPTOLOGICAL ALEF). En ASCII se sustituye de dos formas
y **las dos son legítimas y están en uso**, no hay una vieja y una nueva:

| Forma | De dónde viene |
|---|---|
| `bjꜣ n pt` | El carácter Unicode correcto |
| `bjA n pt` | **Manuel de Codage**, el estándar egiptológico de codificación en ASCII, donde `A` es alef y `a` es ain. Sigue en uso activo |
| `bj3 n pt` | La otra tradición ASCII: sustituye **por forma**, porque el glifo `ꜣ` tiene forma de 3 |

Se elige el `3` por dos razones, una del proyecto y una técnica.

**La del proyecto.** El carácter que significa alef tiene forma de tres, y el disco
está construido sobre el tres: los Ramanes hacen todo por triplicado, son tres tracks,
son 33:33. Escribirlo con `3` mete el tres adentro del título sin decirlo, que es el
registro del proyecto.

**La técnica.** `ꜣ` vive en Latin Extended-D y no se renderiza en todos lados: no se
ve ni en la consola del user. Si ya se rompe ahí, en el formulario de un distribuidor
y en la metadata de un reproductor de auto va a ser peor, y el riesgo de que termine
como `bj? n pt` no lo controla nadie del lado nuestro. `bj3 n pt` es ASCII puro.

El título se propaga al distribuidor, Bandcamp, la metadata embebida, MusicBrainz y el
press kit, y una vez cargado corregirlo es carísimo (criterio de fuente única de
`metadata.md`). Por eso se cierra ahora y no en el momento del upload.

Los jeroglíficos, en cambio, son material de **artwork**, donde no hay encoding que
valga. Los dos signos de *n pt* ("del cielo"), verificados:

| Signo | Unicode | Gardiner | Qué es |
|---|---|---|---|
| **𓈖** | U+13216 | N035 | la onda de agua, vale `n` |
| **𓇯** | U+131EF | N001 | el cielo, `pt` |

### Alternativas evaluadas y descartadas

Antes de esta quedaron en el camino, en orden de cuánto se acercaron: **Aerolite**
(griego "piedra de aire", pero es una acuñación moderna de 1800, no antigua),
**Bolide** (griego *bolís*, "lo arrojado", que rima con la primera línea del cuento de
TX01: *"lo lanzado carecía de nombre"*), **Dark Flight** (la fase en que el objeto deja
de brillar y sigue cayendo a oscuras), **Entry Interface**, **Ablation** y
**Blackout**. Las dos últimas eran las que este doc recomendaba antes.

Mesopotamia y Tíbet tenían el mismo concepto: sumerio **AN.BAR** (𒀭𒁇, glosado como
"fuego del cielo"), que los hititas adoptaron para escribir su propia palabra, y en un
texto ritual hitita aparece *"trajeron hierro negro del cielo"*, que describe la costra
de ablación sin tener la palabra. En tibetano, **gnam lcags** (གནམ་ལྕགས), "hierro del
cielo".

## El estado técnico del track

Vive en `transmissions/02/bj3_n_pt/` (nombre de carpeta heredado de la fuente original, la bomba
de la losa radiante: **no es el título**).

Ya existe como cuatro capas rendidas más las nuevas (lluvia, coro, brillo, moog).
El arreglo completo de 11:11 se arma con `transmissions/02/bj3_n_pt/tema.py`.

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

## Duración: 11:11 cada uno (DECIDIDO 2026-08-08)

**Resuelto por el user: 11:11 por track. Total 33:33.** Es la opción que este doc
recomendaba y queda cerrada. 11:11 son **671 segundos**, que es el número que va a
`DUR` en los scripts de render.

Lo que sigue abajo es el razonamiento que llevó ahí, y se conserva como contexto.

### Cómo se llega a 671 segundos sin estirar nada

**No se time-stretchea el archivo final.** Eso embarra todo. Las capas ya son
paramétricas: `transmissions/02/bj3_n_pt/render.py` tiene `DUR` como constante de módulo y
cada capa recibe `dur=DUR`. El concepto de 2 minutos y el master de 11:11 son **el
mismo código con otro DUR**.

Adentro hay una decisión real, y hay que respetarla al escalar:

| Familia | Ejemplos | Qué hacer |
|---|---|---|
| **Absolutos** | Los períodos de `barrido()` y `respiracion()`: 17, 13, 23, 19, 11 s | **No escalan.** Son físicos. A 671 s simplemente respira más veces |
| **Proporcionales** | El arco, las entradas y salidas de cada capa, los fades, la estructura | **Escalan con DUR** |

Los períodos son todos **primos**, y eso no es decorativo: al ser coprimos las capas
nunca vuelven a alinearse, así que la textura no se siente en loop por más que dure
once minutos. Si se tocan esos números hay que mantener la primalidad.

Detalle: `manifold` ya respira con período 11.0.

### El razonamiento original: 3:33 los tres es demasiado corto

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

## La voz de la entidad: coro en lengua arcana

Idea del user (2026-08-08): grabar su propia voz en registro grave recitando en una
lengua arcana, distorsionarla hasta que sean coros o voces muy graves tipo *Dune*, y
sumarla como track de una capa.

Esa sería **la lengua de la civilización del planeta**, o sea la voz literal del
narrador definido arriba.

### La lengua: protoindoeuropeo

Elegido porque hace exactamente lo que hace el cuento.

- **No está atestiguado en ningún texto.** Nadie lo escuchó nunca, no hay hablantes,
  no hay grabación posible. Es una **reconstrucción**, deducida por evidencia
  comparada. Es decir: es una *hipótesis sobre un idioma*, que es la forma exacta de
  la ficha de cierre de TX01 ("hipótesis preliminares, enumeradas por orden de
  proposición, no por verosimilitud").
- **Es la lengua anterior a la separación**, el ancestro del que salieron el
  sánscrito, el griego y el latín. Para un disco cuyo final es una fusión, una
  lengua de antes de la división es el espejo.
- **La pronunciación es discutida entre lingüistas**, así que nadie puede corregirla.
  El misterio queda blindado.
- Suena no humano de por sí: laringales (h₁ h₂ h₃) y grupos consonánticos que no
  existen en ninguna lengua viva.

### Qué recitar

| Fórmula | Significado | Por qué |
|---|---|---|
| **\*ḱléwos ń̥dʰgʷʰitom** | "fama imperecedera" | Es la fórmula poética reconstruida más famosa. Se dedujo porque aparece por separado en Homero (*κλέος ἄφθιτον*) y en el Rigveda (*śrávas ákṣitam*), y es la prueba de que existió poesía en PIE. Es la frase poética más antigua que la humanidad puede reconstruir |
| **\*dyḗws ph₂tḗr** | "padre cielo" | El origen de Zeus, Júpiter y Dyaus |

Cumple la regla de voz del proyecto: el que escarba encuentra algo verdadero, y
nosotros no explicamos nada.

**Alternativas evaluadas**, por si el PIE no cierra:

- **Hurrita**: el Himno a Nikkal (Ugarit, ~1400 a.C.) es la melodía anotada más
  antigua que se conoce. Si se quiere una canción antigua real, es esa.
- **Sumerio**: el idioma atestiguado más antiguo y una lengua aislada, sin parientes
  vivos. Tiene corpus real de conjuros.

**Descartados**: sánscrito (mantra new age) y latín (iglesia). Los dos gastados.

### Cómo grabarla

- **WAV limpio por la Volt 276, cerca.** El README de `transmissions/02/bj3_n_pt/` ya tiene la
  lección: las fuentes anteriores estaban a ~70 kbps y el stretch extremo amplifica
  los artefactos del codec, porque cada cuadro espectral queda sostenido un segundo
  entero en vez de pasar en 20 ms.
- **No forzar el gutural.** La profundidad se fabrica después. Forzando se arruina la
  toma y se mete ruido de garganta.
- **Tres tomas reales de la misma frase, no copias del mismo archivo.** Las
  diferencias entre tomas son lo que hace el coro. Copias pegadas suenan a chorus, no
  a varias gargantas.
- La cadena ya existe en `render.py`: `bajar_octavas()` para el registro, paulstretch
  para el coro sostenido, `camara()` para el espacio.

> **Trampa conocida.** Para que suene *Dune* la tentación es saturar, y la saturación
> tira armónicos a 1.5-4 kHz, que es la banda exacta que marca `task qa:spectral`
> (antipatrón `T_VOICE_PAD_HARMONICS`). Fix ya documentado: **LPF 1500 al track del
> coro después de la distorsión.**

## Video: la lluvia deformada

Material grabado por el user el 2026-08-08: cuatro clips de lluvia en 4K a 30 fps,
verticales (iPhone, 2160×3840 en display), de 9,7 s, 10,3 s, 3,4 s y 7,8 s.

**Criterio de encuadre, validado con stills antes de animar:** fragmento apretado y
estirado, **nunca el plano entero**. El plano entero siempre delata la calle. No hay
que respetar el vertical: se rota, se recorta y se estira lo que haga falta.

Lo que funcionó:

| Fuente | Tratamiento | Resultado |
|---|---|---|
| **IMG_4741** | Franja del agua chorriando, sin la senda peatonal, estirada a 16:9 | Bandas verticales duras de blanco y negro con grietas. Lo más parecido a un barcode de Ikeda que produjo el proyecto, y salió de una senda peatonal |
| **IMG_4740** | Rectángulo del agua picada, estirado | Cortina de textura vertical, densa y granulada. Irreconocible |

Lo que no funcionó: las rotaciones del plano completo. El 4740 entero se lee como una
pared con rejas, demasiado literal. El 4739 estirado queda blando.

**Montaje pedido:** secuencia de los cuatro (loopeando si hace falta) sobre la base,
con **cortes secos entre clips, sin fade ni transición**.

**Apertura:** pendiente de definir. La idea sobre la mesa es abrir con algo que no sea
lluvia y saltar de ahí al primer corte, aprovechando que el track 1 se llamaría
*Blackout* justamente porque durante la reentrada el plasma corta la transmisión.

## Cosas que ya existen y aplican

- **`transmissions/02/bj3_n_pt/`** — track 1 en marcha, cuatro de seis capas.
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

1. ~~Nombre del track 1~~ → **decidido y cerrado: `bj3 n pt`**.
2. Nombre del planeta (Trine / algo de Rama / otro).
3. ~~Duración~~ → **decidido: 11:11 por track, 33:33 el total.**
4. **Escribir el cuento de TX02**, ahora que el punto de vista está definido. Es lo
   que después da los textos, los fragmentos y los posts. La Æ vive ahí.
5. Si hay colaboración con Helen y dónde (es una decisión separada de Em+H).
6. ~~Grabar las capas de grano y aire del track 1~~ → **resuelto con los cuatro
   clips de lluvia del 2026-08-08.** Ver `transmissions/02/bj3_n_pt/README.md`. Para el track
   2 sigue faltando todo lo orgánico.
7. Grabar la voz en PIE y armar el coro.
8. Definir con qué abre el video antes del primer corte seco.
