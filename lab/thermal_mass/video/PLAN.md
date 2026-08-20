# PLAN · video de `bj3 n pt` (TX02 track 1)

> **RONDA 2 pendiente de ejecutar. Ver la sección al final.** La ronda 1 ya está
> hecha: `montaje.sh` produce `bj3_n_pt_1080.mp4`, 671 s exactos, 184 planos.

> Estado: **listo para ejecutar, no ejecutado**. Escrito el 2026-08-11 con el veredicto
> del user sobre el material que ya existe.
> Concepto narrativo y arreglo musical → `docs/39`.

## El audio contra el que se sincroniza

`lab/thermal_mass/tema_1111_master.wav`, 11:11 (671 s), masterizado, LUFS −16.

Los tiempos del arreglo salen de `tema.py` y son los que manda el montaje:

| Desde | Qué pasa en el audio | Qué se ve |
|---|---|---|
| 0:00 | la base sola | el planeta: lluvia |
| 1:30 | entra el cuerpo | " |
| 3:05 | el lavarropas | " |
| 3:25 | la lluvia, se va a 4:45 | " |
| **5:00** | **entran las voces** | **las criaturas hablando** |
| 6:00 | se pudre todo | " |
| **7:50** | **entra el moog** | **el cielo, el fogonazo, algo bajando** |
| 10:15 | queda base + moog | " |
| 11:11 | fin | negro |

## Veredicto del user sobre el material (2026-08-11)

### Los clips de lluvia: SÍ van, pero hay que deformarlos MUCHO más

**Se reconoce que es Buenos Aires con lluvia y se nota que hay una casa.** El
tratamiento actual (`concepto.sh`) no alcanza. Es el problema número uno.

Lo que delata, y qué lo rompe:

| Qué delata | Por qué | Cómo se rompe |
|---|---|---|
| Geometría de edificio | Bordes rectos y ventanas rectangulares se leen como arquitectura | Recortes MUCHO más chicos, ampliados mucho más: sin contexto no hay edificio |
| Perspectiva correcta | El cerebro reconstruye la calle | Rotaciones a ángulos no cardinales, espejado, `perspective` |
| Escala de grises intermedia | Deja leer superficies | Aplastar casi a dos tonos: solo masas |
| Movimiento coherente | La lluvia cayendo derecho se lee como lluvia | `tblend` para arrastre, `displace`, y velocidad alterada |

Herramienta que ya existe y hay que reusar: **`transmissions/01/video/blender/grim_post.py`**,
la función `grim(img, scale, bright, grain_amt, gamma, desat)`. Es el pase de grade
GRIM del proyecto. No escribir otro.

### Los clips generados: cuáles quedan

Generados con `generar.py` en `generado/`, 768×512 a 24 fps, 2,7 s cada uno.

| Clip | Veredicto |
|---|---|
| `bicho_02` hojas gigantes a contraluz | **SÍ** |
| `bicho_03` dos formas en pasto alto | **SÍ** |
| `bicho_05` criatura entre hojas | **SÍ** |
| `cielo_02` relámpago detrás de nubes | **SÍ** |
| `cielo_03` haz de luz atravesando nubes | **SÍ** |
| `cielo_04` objeto ardiendo con estela | **SÍ** |
| `cielo_05` bola de fuego cruzando | **SÍ** |
| `bicho_01` dos siluetas enfrentadas | descartado |
| `bicho_04` plantas contra niebla | descartado |
| `cielo_01` rayos en nubes negras | descartado |

Nota del user sobre los `bicho`: **le gustan aunque no se vean bichos.** O sea que la
lectura literal de "dos criaturas" no es un requisito; alcanza con que haya masas
oscuras que se muevan distinto. No forzar figuras.

### Los tres problemas abiertos

**1. Falta animación.** Los clips generados casi no se mueven. Es limitación de LTX a
65 cuadros y 25 pasos, y se ve en el peso de los archivos: los que quedaron en 74-76 KB
son casi estáticos.

Tres caminos, de más barato a más caro:

- **Fabricar el movimiento en post.** Es lo que el proyecto ya hizo en el build de
  Crossing: zoom lento, boomerang, desplazamiento. Se le puede sumar algo que ningún
  otro tiene: manejar el desplazamiento con los **control tracks** del propio tema
  (ver abajo). Recomendado: es gratis y queda sincronizado.
- **Regenerar con más cuadros y más pasos.** 121 cuadros y 40 pasos. Cuesta ~15 min por
  clip en vez de 4:27.
- **Image-to-video con SVD** desde un frame elegido, que es lo que `docs/video/09`
  recomienda para "animar nuestros picks aprobados sin romper la identidad".

**2. "Veo algo cayendo medio verga".** El objeto de `cielo_04` no convence como caída.
Opciones: usarlo solo en fragmento apretado (que es la regla general igual), o generar
variantes del prompt con el objeto más chico y más lejos, o resolverlo por post con un
desplazamiento vertical lento sobre un fragmento del fuego.

**3. Cómo se concatena la historia.** Es lo que falta decidir y es lo más importante.
El arreglo ya da los tiempos (tabla de arriba); falta el orden de planos adentro de
cada tramo y qué transición va en cada juntura. Los cortes entre clips son **secos**,
sin fade, por decisión ya tomada.

## Lo que hay que hacer, en orden

### 1. Endurecer el tratamiento de la lluvia

Trabajar sobre `concepto.sh`. Objetivo medible: **que no se pueda decir qué se está
mirando.** El test es mostrar un frame sin contexto y no poder nombrar el objeto.

Cambios concretos a probar, de mayor a menor efecto:

```
crop mucho más chico (~400×150 de un 2160×3840) y escalado a 1920×1080
rotate a ángulos no cardinales (7°, 23°, 41°)
hflip / vflip alternados por plano
curves con solo tres puntos: aplastar a masas
tblend=all_mode=average para arrastre temporal
setpts para alterar la velocidad (0.4x y 2.5x)
```

Y pasar todo por `grim()` de `grim_post.py` al final, para que quede en la paleta del
proyecto y no en una mía.

### 2. Preparar los siete clips elegidos

Mismo tratamiento duro que la lluvia. Ojo: vienen en 768×512, o sea que soportan mucho
menos ampliación que los 4K del teléfono. Recortes proporcionalmente más grandes.

### 3. Fabricar el movimiento con los control tracks

Esto es lo que hace que el video sea del tema y no un montaje encima. El pipeline de
TX01 genera un `.npz` por track (ver `transmissions/01/video/control/`) con las lanes
`rms`, `rms_sub`, `rms_air`, `centroid`, `flux`, `onset` a 30 fps.

**Falta generarlo para este tema**: hay que correr el mismo análisis sobre
`tema_1111_master.wav` y guardar `lab/thermal_mass/video/control/bj3_n_pt.npz`.

Con eso: el zoom sigue a `rms_sub`, el brillo a `centroid`, y los cortes o destellos
caen en `onset`. Los 36 golpes de sílaba del coro son eventos identificables y ahí
tiene que pasar algo visual.

### 4. Armar el montaje de 11:11

Extender `concepto.sh` de 120 a 671 s con la estructura de tres tramos. Se mantiene:
cortes secos, planos largos en los bordes y cortos en el centro, guarda que aborta si
un plano pide más allá del final de su clip.

### 5. Salida final

**4K (3840×2160) y 60 fps**, sin excepción (`memory/feedback_video_must_be_4k.md` y
`memory/feedback_render_60fps_for_youtube.md`: el 24 da judder por pulldown 3:2). Los
clips fuente son 768×512, así que el upscale es grande: hay que verificar que el grano
tape el escalado en vez de delatarlo.

## Comandos

```bash
# regenerar clips (opcional, ya están los diez)
python3.10 lab/thermal_mass/video/generar.py               # todos los que falten
python3.10 lab/thermal_mass/video/generar.py cielo_04 --rehacer
python3.10 lab/thermal_mass/video/generar.py cielo_04 --rapido   # sin offload, más RAM

# el concepto de 2 min con la lluvia
bash lab/thermal_mass/video/concepto.sh

# el audio
python3.10 lab/thermal_mass/tema.py              # usa el cache de capas
python3.10 lab/thermal_mass/tema.py --rehacer    # rinde todo de nuevo (~3 min)
python3.10 scripts/qa_scan_spectral.py lab/thermal_mass/tema_1111_master.wav

# escuchar
python3.10 player/serve.py --port 8765 --no-open
# http://localhost:8765/lab/thermal_mass/escuchar.html
```

## Notas de generación que ya costaron tiempo

- **float16, no bfloat16.** En Metal el bf16 cae en caminos lentos: con bf16, 40 pasos
  y 97 cuadros un clip tardaba **30 minutos**. Con fp16, 25 pasos y 65 cuadros tarda
  **4:27**.
- **`enable_tiling()` en el VAE** es lo que evita que el proceso se coma 33 GB de 36.
  El pico no es el modelo, es decodificar todos los cuadros de una vez.
- **Guidance 6.0 y prompts de menos de 50 tokens.** Con los defaults (3.0 y prompts
  largos) sale puré (`memory/ltx_video_poc_learnings.md`).
- **Lo que sobrevive al blanco y negro duro es cosa brillante sobre fondo oscuro.** Un
  gris difuso sobre gris se va entero a negro. El primer prompt de cielo pedía "chaotic
  storm clouds" y dio un atardecer tranquilo que tratado quedó en negro.

## Pendiente de audio, que sigue abierto

En la ventana del moog, la **cama está +7,7 dB por encima de él** en su misma banda. Si
al escucharlo sigue tapado, la solución es que la cama se aparte bajo el moog, igual
que ya hacen el lavarropas y la nube bajo las voces: agregar `"cama"` a `DUCKING` en
`tema.py` con una envolvente derivada de `ARREGLO["moog"]`. Son dos líneas.



---

# RONDA 2 · pendiente de ejecutar

Feedback del user sobre `bj3_n_pt_1080.mp4` (2026-08-11), y el error de fondo que hubo
que reconocer: **se le hizo zoom a imágenes fijas**, que es exactamente el antipatrón
de "animar cartón" que el propio proyecto tiene documentado
(`memory/feedback_stills_before_animation.md`).

## 0. La regla que sale de esto: medir el movimiento ANTES de usar un clip

Movimiento medio entre cuadros consecutivos, medido sobre 150 cuadros a 160×160 en
gris (0 = imagen fija):

| Material | Movimiento |
|---|---|
| Lluvia del user, IMG_4740 | **9,64** |
| Lluvia del user, IMG_4741 | 6,98 |
| `bicho_02` generado | 4,73 |
| `bicho_03` generado | 4,50 |
| NASA SDO, fulguración solar | 3,95 |
| `cielo_04` generado | **0,61** |
| `bicho_05` generado | **0,46** |
| `cielo_02` generado | **0,37** |
| `cielo_05` generado | **0,28** |
| `cielo_03` generado | **0,11** |

Los clips del acto 3 tienen entre **15 y 90 veces menos movimiento que la lluvia**. Son
imágenes fijas, y montarlas junto a material dinámico es el golpe que se escucha y se
ve. El zoom de cámara no lo compensa: lo delata.

**Umbral que se adopta: ningún clip entra al montaje con movimiento medido por debajo
de 3,0.** Hay que agregar esa medición como guarda en `montaje.sh`, igual que ya está
la que aborta si un plano pide más allá del final de su clip.

Nota: el user eligió `bicho_02` y `bicho_03` mirándolos, y son justo los dos generados
que superan el umbral. Su ojo coincidió con la medición.

## 1. Material nuevo para el moog, con movimiento real

Pedido textual: *"cuando entra el moog tienen que ser imágenes totalmente distintas, no
usadas. Lava fluyendo, ríos de lava distorsionados, cielos, quásares explotando, algo
que cambie"*.

Fuentes verificadas, de dominio público y **con movimiento medido**:

| Fuente | Qué hay | Estado |
|---|---|---|
| **NASA SVS** `svs.gsfc.nasa.gov/12737` | Fulguraciones solares del SDO en 4096×4096, plasma retorciéndose en distintas longitudes de onda del ultravioleta extremo. WebM de 12 a 40 MB, MOV de hasta 42 GB | **Descargado y medido: 3,95.** Crédito: NASA Goddard |
| **USGS Kīlauea** `usgs.gov/observatories/hvo/multimedia/videos` | Lava fluyendo y fuentes de lava en 4K, dominio público | Por descargar. Crédito: U.S. Geological Survey |
| **NASA SVS** galería `sdo4k-content` | Más material solar en 4K | Por revisar |

El plasma solar del SDO es lo más cerca de "quásar explotando" que existe siendo real y
libre, y encima es **el mismo linaje que el proyecto ya usa**: `docs/27` documenta que
Lustmord trabaja con archivos del JPL de la NASA como fuente.

## 2. Material nuevo para las voces: bocas y caras deformadas

Pedido: *"cuando habla tiene que haber algo distinto, caras distorsionadas moviéndose,
o una boca media rara hablando"*.

Dos caminos, y conviene probar los dos:

- **Prelinger Archives** en Internet Archive (`archive.org/details/prelinger`): unas
  60.000 películas efímeras, ~65% en dominio público en EE.UU. Hay primeros planos de
  gente hablando de sobra. Deformado como la lluvia, queda una boca rara moviéndose y
  no se reconoce a nadie. **Verificar el estado de dominio público de cada clip
  puntual**, porque no todo el fondo lo es.
- **Regenerar con LTX** pidiendo movimiento explícito. Los prompts actuales piden
  atmósfera ("silhouettes", "fog") y el modelo devuelve una postal. Hay que pedir
  **verbos**: *"mouth opening and closing slowly, extreme close up"*. Y subir a 121
  cuadros y 40 pasos, que cuesta ~15 min por clip en vez de 4:27.

## 3. Más espeso, más lento

> la música apunta a un warp y vos le das mucha velocidad a las escenas

| Qué | Ahora | A dónde |
|---|---|---|
| Duración media de plano, acto 1 | ~5,9 s | **12 a 18 s** |
| Velocidad del material de lluvia | 1.0x | **0.5x** (`setpts=2.0*PTS`) |
| Zoom de los generados | 0.0009 por cuadro | **se elimina**: si el clip se mueve solo, no hace falta |

De 184 planos a unos 70.

## 4. La apertura: hay que armar un acto 0

> no podés arrancar con lluvia directo. Que sea todo negro, que se vea un fogonazo en
> una especie de cielo, una toma lenta con una estela formándose, y luego pum, arranca
> la lluvia

Esto encaja con el arreglo musical sin forzar nada. Los primeros 90 segundos del tema
son **la base sola** y el cuerpo entra exactamente a 1:30:

| Tiempo | Audio | Video |
|---|---|---|
| 0:00 - 0:20 | silencio, la base asomando | **negro puro** |
| 0:20 - 1:30 | la base sola | **el cielo**: toma lenta, muy oscura, la estela formándose |
| **1:30** | **entra el cuerpo** | **PUM, corte seco a la lluvia** |

El "pum" ya está en la música. Solo hay que apoyarlo. Para la estela va el material
solar de la NASA ralentizado, no los clips generados.

El acto 1 pasa a 1:30-5:00, o sea 210 s.

## 5. Los blancos queman

**Causa raíz:** `normalize=whitept=white` fuerza el píxel más brillante de CADA plano a
blanco puro (255), así que todos los planos tienen altas quemadas por construcción. Fue
el arreglo de la ronda 1 (que resolvió el colapso a negro) pasándose para el otro lado.

```
normalize=blackpt=black:whitept=0xB0B0B0             # el tope pasa a ~69%
DURO="curves=all='0/0 0.38/0.05 0.62/0.72 1/0.78'"   # la curva ya no llega a 1
```

**Verificación medible:** hoy hay planos con 44% y 51% de píxeles en 255. Objetivo:
**menos del 2%** en el acto 1.

## Orden de ejecución

1. Bajar el blanco (§5). Dos líneas, se valida con stills en segundos.
2. Bajar el material nuevo: NASA solar y USGS lava, y medirles el movimiento (§1).
3. Conseguir el material de bocas (§2) y medirlo igual.
4. Agregar la guarda de movimiento mínimo 3,0 a `montaje.sh` (§0).
5. Rearmar la lista de planos: más lentos y más largos (§3), con el acto 0 adelante (§4).
6. Render 1080p60 para revisar.
7. Recién con el visto bueno, `--4k`.

## Lo que NO hay que tocar

- Los cortes siguen **secos**, sin fade.
- El grado sigue **separado por acto**: duro para la lluvia (material real de una calle
  reconocible), suave para el resto.
- La guarda que aborta si un plano pide más allá del final de su clip.
- El montaje termina en 671,000 s exactos contra el master.
- **Los créditos**: NASA Goddard Space Flight Center y U.S. Geological Survey van
  nombrados donde corresponda (`docs/25_press_kit.md` y la descripción de YouTube).


---

# RONDA 3 · feedback en curso (el user sigue mandando)

## 1. GRAVE: se ve el título del USGS en el video

Aparece el cartel *"Lava Flow / May 20, 2018 / ~2:30 AM HST / Video from the U.S.
Geological Survey"* en pantalla. Los clips de archivo traen placas quemadas y marca de
agua, y los cortes caían justo ahí.

Esto además explica por qué la lava medía 0,21 de movimiento: **se estaba midiendo y
montando texto fijo**, no lava.

Ventanas limpias, medidas mirando los cuadros:

| Clip | Placa inicial | Ventana limpia | Placa final | Marca de agua |
|---|---|---|---|---|
| `usgs_lava_01.mp4` | 0 a 5 s | **5,5 a 21,5 s** | desde 22 s | **sí, logo USGS abajo a la izquierda, todo el clip** |
| `usgs_fuente_lava.mp4` | 0 a 6 s | **6,5 a 65 s** | desde 66 s | no |

Reglas que salen de esto:

- Ningún corte fuera de esas ventanas.
- En `usgs_lava_01` **ningún recorte puede tocar la esquina inferior izquierda**, que
  es donde vive el logo.
- **Agregar una guarda**: detectar texto quemado antes de montar. Un chequeo barato es
  medir el porcentaje de píxeles casi blancos en la franja central junto con
  movimiento cero, que es la firma de una placa.
- Y la regla general: **mirar el clip entero antes de usarlo**. Esto se hubiera
  evitado abriendo el archivo una vez.

## 2. El negro del arranque es muy largo, y va con fade

Hoy son 20 s de negro puro. Achicarlo, y **poner un fade in ahí y solo ahí** (el resto
del video sigue con cortes secos).

Propuesta: 8 s de negro y fade de entrada de unos 4 s sobre el primer plano, que
termina de abrir alrededor de 0:12. La base del tema tarda 16 s en asomar, así que el
fade acompaña la entrada del audio en vez de pelearse con ella.

## 3. La lava: más distorsionada, pero no toda

> lo de lava un poco más distorsionado quizás, igual me gusta que haya quizás un
> videito un poco más vívido, tampoco distorsiono mucho

O sea: subir el tratamiento en la mayoría de los planos de lava, **pero dejar alguno
más limpio y vívido como contraste**. No aplicar el mismo grado a todo.

Implementación: un tercer nivel de tratamiento entre `t_arch` (suave) y `t_campo`
(duro), y marcar a mano dos o tres planos de lava para que vayan casi sin tocar.

## 4. Nota técnica sobre por qué la lava medía tan poco

Además de las placas, el clip de la fuente es un **plano aéreo general**: la fuente y
la pluma ocupan una fracción chica del cuadro y el resto es cráter quieto. El recorte
tiene que ir cerrado sobre la fuente (aproximadamente en x 0,55 e y 0,25 del cuadro,
o sea alrededor de 1050,270 en 1920×1080) o la medición y la percepción van a seguir
dando material muerto.

## 5. Material nuevo del user: `IMG_4842.MOV`

Grabado el 2026-08-12. 2160×3840 vertical (rotación −90 en metadata), 11,8 s, 30 fps.
Palmeras oscuras en contraluz que se mueven, con un edificio detrás.

- **Movimiento en la fuente: 3,4 a 6,1.** Supera el umbral.
- Indicación del user: usar la zona **derecha, tirando para arriba**, que es donde
  están las hojas que se mueven.
- Recorte que funcionó: `crop=1500:850:640:300`. Tratado con el grado duro queda en
  láminas oscuras con astillas de luz: irreconocible como palmera y, más importante,
  el edificio desaparece.
- **Destino natural: el acto 2, las criaturas.** Es material propio, con movimiento
  real, y lee como masa orgánica oscura que se mueve, que es exactamente lo que se
  pidió ("no hace falta que se vean bichos").

## 6. Corrección a la guarda de movimiento

Medir el plano YA TRATADO está mal. Con el grado duro, el 80% del cuadro queda en
negro, así que la diferencia media entre cuadros cae aunque lo visible se mueva
perfectamente: las hojas pasan de 6,1 en la fuente a 2,7 tratadas.

**La guarda tiene que medir la fuente recortada y sin gradar.** Eso predice si el
material se mueve; el grado es una decisión aparte y no debe contaminar la medición.

## 7. Repetición: el problema más grave del montaje actual

> del minuto 4 al minuto 7 mostrás exactamente lo mismo. La secuencia está
> espectacular, pero no abuses, no repitas más de dos o tres veces lo mismo,
> intercalá además. Armate otras secuencias.

Causa: el acto 2 es un bucle de 19 pasadas sobre tres clips (`bicho_03`, `boca_01`,
`bicho_02`), siempre con el mismo recorte y en el mismo orden. Son 57 planos y hay tres
imágenes distintas.

Reglas nuevas:

- **Máximo dos o tres repeticiones del mismo material en todo el video.**
- **Intercalar**, no agrupar: no tres bloques de lo mismo seguidos.
- Cada repetición con **recorte distinto**, no el mismo encuadre.

Y lo mismo aplica a otros dos puntos que marcó:

- **7:30**: el volcán y la estela repiten lo del principio. Necesitan otra distorsión
  y otro zoom, no el mismo plano.
- Hay que **armar más secuencias distintas** en vez de estirar las que hay.

## 8. Tres momentos que necesitan material ÚNICO

Esto es lo más importante de esta ronda y no es un ajuste, es material que falta.

| Momento | Qué pidió | Estado |
|---|---|---|
| **7:40, entran las voces** | *"quiero sentir la presencia de un puto alien, tiene que ser una escena única, solo para ese momento"*. Y además mezclarlo con un paneo del mundo, como el de volcanes y landscape | **falta** |
| **Cuando entra el moog** | *"algo único, un estallido"* | **falta** |
| **Minuto 8** | *"de cuarta mostrar esto"* | hay que reemplazarlo |

Nota: lo del alien y el estallido no se resuelven recortando lo que ya hay. Son dos
planos que hay que conseguir o generar a propósito.

## 9. Las placas del USGS siguen apareciendo

El user las vio en **el minuto 8 y en 8:07** ("mostrás como una marca", "mostrás lo de
Lava Flow en la pantalla"). Es la marca de agua y la placa de título documentadas
arriba. Prioridad alta: son las únicas dos cosas del video que se leen como error y no
como decisión.

## 10. AUDIO: la lluvia del medio

Pedido aparte, de sonido y no de video:

> en algún momento, en el medio del video se tendría que escuchar como una lluvia,
> quizás no literal como la tenemos, apenitas ralentizada con algún FX, que aporte
> brillo, algo más granular, no tan tapado

O sea una **tercera versión de la lluvia**, distinta de las dos capas actuales
(`rain_grano` y `rain_aire`):

- Apenas ralentizada, no estirada al extremo como las otras.
- Con FX que aporte **brillo**, o sea contenido arriba de 2 kHz que hoy no existe: la
  mezcla se termina en 5,5 kHz.
- **Más granular**, o sea que se escuchen gotas discretas y no una sábana.
- **No tapada**: tiene que estar adelante, no debajo.

Va en el medio del tema, o sea en la ventana donde hoy la lluvia se retira (entre
4:45 y 6:00). Se implementa en `rain.py` como una función nueva, no tocando `grano`.

## 11. El video dura menos de 11:11

Confirmado: **604,9 s en vez de 671**, o sea 66 segundos de menos. El audio quedó
cortado por `-shortest`.

Causa: la suma de los planos dio 608 s. Cuando se recortaron los planos que se pasaban
del largo de su clip, la suma quedó corta y no se compensó en ningún lado.

Fix: además de la guarda que aborta si un plano se pasa, **agregar una verificación
final que aborte si la suma de planos es menor que el largo del audio**. Hoy el script
lo imprime pero sigue igual, y ahí se cuela el error.

## 12. AUDIO: el moog suena tapado al entrar

> 8:30 cuando entra el moog, le pusiste mucho efecto arriba? Lo siento medio tapado,
> me gustaría que sea una bocanada de aire fresco (no en volumen, sino en sonido más
> limpio, que traiga eso)

Ya se bajó una vez (drive de 30 a 16, cola de 12 s a 7, LPF de 1500 a 2000) y sigue
tapado. Lo que queda por revisar, en orden de cuánto pesa:

1. **El LPF en 2000 Hz.** Es lo que más lo tapa. Un Moog real no tiene nada cortando
   ahí; el filtro escalera ya define el techo por sí solo. Se puede subir a 3500 o
   sacarlo del todo, y controlar la fritura desde el `drive` en vez de con un pasa-bajos.
2. **La cola de reverb.** 7 s con corte en 1800 Hz sigue siendo bastante barro sobre un
   bajo. Probar 4 s y mezcla 0,25.
3. **Quién lo está tapando en la mezcla**, que es lo medido y no se resolvió: en su
   ventana la **cama está +7,7 dB por encima de él** en su misma banda. Agregar `"cama"`
   al `DUCKING` de `tema.py` con envolvente derivada de `ARREGLO["moog"]` es lo que le
   abre el lugar de verdad.

"Bocanada de aire fresco" apunta a lo mismo que pidió para la lluvia del medio: que
haya contenido arriba. Hoy la mezcla entera se termina en 5,5 kHz.

## 13. INVENTARIO CERRADO · material conseguido y verificado

Todo bajado, medido y revisado con hoja de contacto. Los créditos van en la
descripción de YouTube y en `docs/25_press_kit.md`.

| Material | Origen | Ventana limpia | Ojo con | Destino |
|---|---|---|---|---|
| `IMG_4739/40/41/42` | grabado por el user | todo | es una calle reconocible: grado DURO | acto 1, la lluvia |
| **`IMG_4842`** | grabado por el user | todo | usar zona derecha-arriba, `crop=1500:850:640:300` | acto 2, las criaturas |
| `bicho_02` `bicho_03` `boca_01` | LTX local | todo (2,7 s c/u) | son los únicos tres generados que se mueven | acto 2 |
| **`noaa_medusa_01`** | NOAA Ocean Exploration | **13,5 a 30 s** | rótulos en 4-5 s y 9-13 s, placa final | **el alien, 7:40** |
| **`noaa_sifonoforo`** | NOAA Ocean Exploration | **0 a 5 s · 9,5 a 23 s** | rótulo en 5,8-8,1 s, placas finales | **el alien, 7:40** |
| **`usgs_erupcion_2025`** | USGS Kīlauea | **55 a 84 s · 190 a 205 s** | sin placas visibles | **el estallido del moog** |
| `usgs_lava_01` | USGS Kīlauea | **15 a 27 s** | **logo abajo a la izquierda TODO el clip**: ningún recorte puede tocar esa esquina | acto 3 |
| `usgs_fuente_lava` | USGS Kīlauea | **6,5 a 65 s** | plano aéreo general: recorte cerrado sobre la fuente o queda muerto | acto 3 |
| `SDO_20170910_131` | NASA SVS | **2,4 a 6,6 s** | antes de 2,3 s está quieto | acto 0 y acto 3 |

Nueve fuentes distintas contra las tres de la versión anterior.

### Los dos momentos únicos, resueltos

- **El alien (7:40)**: la medusa de 3.900 m es una campana naranja encendida con
  tentáculos larguísimos sobre agua negra, y el sifonóforo es una cinta luminosa
  azul que se enrosca en ocho. No hay que inventar nada: son alienígenas de verdad.
- **El estallido (moog)**: el respiradero de la erupción de 2025, naranja pleno con
  columna de vapor.

### Créditos obligatorios

NOAA Ocean Exploration · U.S. Geological Survey · NASA Goddard Space Flight Center.

## 14. Estructura final del montaje

| Desde | Audio | Video |
|---|---|---|
| 0:00 | silencio | negro 8 s, **con fade in de 4 s** (el único fade del video) |
| 0:12 | la base sola | el solar, planos largos |
| **1:30** | **entra el cuerpo** | **corte seco a la lluvia** |
| 1:30 a 5:00 | el planeta | lluvia + `IMG_4842`, planos de 12 a 18 s, intercalados |
| **5:00** | **entran las voces** | criaturas: palmeras, bichos, boca, **más paneo del mundo** |
| **7:40** | las voces plenas | **el alien**: medusa y sifonóforo. Escena única |
| **7:50** | **entra el moog** | **el estallido**: la erupción. Escena única |
| 7:50 a 11:11 | el moog | erupción, lava, solar, todo con recortes distintos a los del acto 0 |
| 11:11 | fin | negro |

### Reglas de montaje

- Máximo **dos o tres apariciones** del mismo material en todo el video.
- **Intercalar**, nunca agrupar el mismo clip.
- Cada reaparición con **recorte y tratamiento distintos**.
- Cortes **secos** en todo salvo el fade de apertura.
- La suma de planos tiene que dar **671 s o más**, con guarda que aborte si no.
- Guarda de movimiento medida **sobre la fuente recortada**, no sobre el plano gradado.
- Tres niveles de tratamiento: DURO para la lluvia, MEDIO para archivo, y **dos o tres
  planos casi limpios** como contraste (pedido del user).

## 15. Cambios de audio a aplicar en la misma tanda

1. **Tercera capa de lluvia** para el medio del tema: apenas ralentizada, con brillo
   arriba de 2 kHz, granular, adelante y no tapada. Función nueva en `rain.py`.
2. **Moog más limpio**: subir el LPF de 2000 a 3500 o sacarlo, cola de 7 s a 4 s con
   mezcla 0,25, y agregar `"cama"` al `DUCKING` con envolvente del moog.
3. Re-render y `qa:spectral`.

---

# RONDA 4 · feedback en curso (el user sigue mirando)

## 1. El fade de apertura tarda mucho en entrar

Hoy son 8 s de negro + 4 s de fade. Bajarlo: **fade de 2 s**, y evaluar bajar el negro
a 6 s.

## 2. El primer 1:10 son las mismas dos escenas, y cansa

> si vas a usar las mismas dos escenas, modificales, cambiale la distorsion y hacele
> zoom, cambia el angulo, flipeala, investigá técnicas

Causa: el acto 0 son 12 planos del MISMO clip solar, y ese clip tiene solo 4,2 s
usables (2,4 a 6,6). Cambiar el recorte no alcanza porque el contenido es el mismo:
un disco con una fulguracion.

**Cambiar el recorte NO es variar.** Lo que varia de verdad, en orden de cuanto cambia
la lectura de la imagen:

| Tecnica | Filtro | Qué hace |
|---|---|---|
| **Negativo** | `negate` | Es la mas fuerte de todas: el mismo material en negativo se lee como OTRO material. Blanco sobre negro pasa a negro sobre blanco |
| **Espejado** | `hflip` `vflip` | Rompe la orientacion memorizada |
| **Giro de 90°** | `transpose=1` `transpose=2` | Cambia el eje de la composicion entera |
| **Rotacion libre** | `rotate=0.4` y recortar despues | Ya se usa, pero solo en la lluvia |
| **Reversa** | `reverse` | El movimiento va al reves. Los clips son cortos, entra en memoria |
| **Escala del recorte** | recortes muy cerrados vs muy abiertos | Un detalle ampliado y un plano general del mismo cuadro son dos imagenes |
| **Grado** | alternar `t_campo` `t_difuso` `t_arrastre` `t_vivo` | Ya existen los cuatro, pero el acto 0 usa uno solo |
| **Velocidad** | `setpts` distinto por plano | Ya existe, se usa uniforme |

**Regla nueva: dos planos de la misma fuente nunca comparten receta.** Cada plano
lleva una combinacion distinta de negativo, espejado, giro, grado y velocidad.

Y esto **aplica a todo el video, no solo al acto 0**: el user lo dijo explicito ("esto
mismo para toda otra escena que haya").

## 3. Idea estructural: el acto 0 no puede ser una sola fuente

Con 4,2 s de material no hay variacion posible que sostenga 78 segundos. Hay que
mezclarle otra cosa: la medusa en negativo, o la erupcion muy oscurecida, o material
del acto 3 tratado al reves. Pero **sin gastar el alien ni el estallido**, que tienen
que aparecer por primera vez en su momento.

## 4. La palmera muestra los edificios en 3:45

Verificado: en `IMG_4842` el edificio ocupa la mitad izquierda del cuadro y las hojas
la derecha. **Los recortes con x menor a 900 agarran ventanas.**

El plano de 3:45 usa `crop=1600:900:520:400`, o sea x=520. Los que hay que corregir:

| Recorte en uso | x | Estado |
|---|---|---|
| `1500:850:640:300` | 640 | corregir |
| `1300:730:820:700` | 820 | corregir |
| `1700:960:460:150` | 460 | corregir |
| `1400:790:700:1100` | 700 | corregir |
| `1600:900:520:400` | 520 | **el de 3:45** |
| `1200:675:900:1500` | 900 | ok |
| `1500:850:600:250` | 600 | corregir |

**Regla: ningun recorte de palmera con x < 900.** Lo que delata al edificio son las
formas rectangulares brillantes (ventanas); las hojas son diagonales y curvas.

## 5. Se abuso de la palmera

Aparece 11 veces. Ademas de bajar la cantidad, **cada aparicion tiene que llevar una
modificacion distinta**: negativo, espejado, giro de 90°, otra escala de recorte u
otro grado. Es la misma regla del punto 2, aplicada a esta fuente en particular.

Nota: el user dijo que **todas las tomas anteriores a 3:45 estan bien y le gustan**.
El acto 1 va por buen camino; el problema es la repeticion, no el tratamiento.

## 6. LA REGLA GENERAL, y por qué hay que cambiar cómo se arma la lista

El user lo repitió en 1:10, en 3:45, en el minuto 5 y en el 6. **No son cuatro
observaciones, es una sola regla**: nunca dos planos iguales de la misma fuente.

Los números del montaje actual muestran por qué se siente así, y muestran algo peor:

| Fuente | Apariciones | Movimiento |
|---|---|---|
| Solar | **17** | 16,5 |
| `usgs_fuente_lava` | **14** | **1,06** |
| Palmera | **11** | 5,1 |
| Erupción | 6 | 3,3 |
| **Medusa** | **1** | 4,0 |
| **Sifonóforo** | **1** | 4,2 |

**La distribución está exactamente al revés de lo que debería**: lo que más se repite
es lo más quieto, y lo que más impacto tiene aparece una sola vez.

### El cambio: dejar de escribir los planos a mano

Con 83 planos escritos uno por uno es imposible garantizar que no se repita una
combinación. Hay que **generar la lista**, con una receta por plano compuesta de:

    fuente · recorte · grado · espejado · giro · negativo · velocidad

y una regla de unicidad: **ninguna combinación se repite en todo el video, y dos
planos consecutivos nunca comparten fuente.**

Con seis ejes de variación, incluso una fuente que aparezca diez veces se ve distinta
las diez. Es la única forma de que nueve fuentes sostengan once minutos.

Además hay que **rebalancear**: bajar el solar y la lava aérea, subir la medusa y el
sifonóforo (que hoy aparecen una vez cada uno), sin gastar el momento del alien.

## 7. El alien FUNCIONA (7:34 en adelante)

Confirmado por el user: *"bieeen las escenas de 7:34 en adelante para generar eso de
la voz"*. La decision de usar material de NOAA en vez de generarlo fue la correcta.

Un solo ajuste: **la primera medusa se lee demasiado como medusa**. Causa: es el unico
plano del video con `t_vivo`, el tratamiento casi sin tocar. Hay que subirle el grado
a `t_arch` o `t_campo`: tiene que quedar la presencia, no el bicho identificable.

El sifonoforo, que va con `t_arch`, quedo bien.

## 8. Los textos, cuarta vez. Causa raiz y fix definitivo

Aparecieron en **8:18, 8:25, 9:08, 9:17, 9:55 y 9:57**. Todos del mismo clip.

**Causa: la ventana limpia de `usgs_lava_01` estaba mal anotada.** Este doc decia
"limpio 15 a 27 s" y la placa de cierre arranca en el **segundo 21**. Verificado
cuadro por cuadro: limpio en 19 y 20, cartel desde 21.

La ventana real es **5,5 a 20,5 s**. Corregido en el script y reescritos los cuatro
planos que la usaban (uno arrancaba en el segundo 24, o sea de lleno en la placa).

**El fix de fondo no es corregir la ventana, es dejar de confiar en ellas.** Se agrego
a `revisar.py` un escaneo del VIDEO YA ARMADO:

    python3.10 lab/thermal_mass/video/revisar.py --salida bj3_n_pt_1080.mp4

Recorre la salida buscando texto quemado y lista los tramos. Es lo unico que el
espectador ve, y es el unico chequeo que no depende de que yo haya anotado bien una
ventana. **Pasa a ser obligatorio antes de entregar cualquier corte.**

## 9. El moog: la escena tiene que SOSTENERSE

> 8:30 cuando entra el moog medio pelo lo que mostras, no es tan wooow y tenes que
> mantenerla esa escena mientras toque el moog asi generamos esa tension, te digo
> hasta donde. 8:40/8:43 quizas

Cambio de criterio importante: en la entrada del moog **no hay que cortar**. Un plano
unico y sostenido de 8:30 a 8:43 (unos 13 s), que es lo contrario de lo que hace el
resto del video. El corte permanente diluye la tension justo donde tiene que crecer.

Y a las **9:12 vuelve el moog**: ahi va la misma escena especial pero distorsionada, u
otra distinta. No repetida igual.

## 10. AUDIO: el "pimpumpum" en 9:37

Medido entre 9:30 y 9:50: el **moog** es la capa mas fuerte del tramo (−19,4 dB) y
tiene **23 picos en 20 s**, o sea un pulso cada 0,87 s. Un bajo sostenido no deberia
pulsar.

Hipotesis a verificar: es el **batido entre las dos sierras desafinadas 7 cents**. A
80 Hz, 14 cents de diferencia total dan un batido de ~0,65 Hz, del orden de lo medido.
Fix probable: bajar `detune_cents` de 7 a 3, o desafinar solo una de las dos.

## 11. El final: cerrar con el alien

> quiero que termines con la escena del alien que tenemos, mostrar un poco mas

Hoy el video termina con lava y con el solar, y encima con la placa al aire. El cierre
tiene que ser **la medusa y el sifonoforo**, y con mas metraje del que tienen hoy
(13 s en total, una sola aparicion).

Eso ademas resuelve el desbalance medido: el material de mas impacto aparece una vez y
el mas quieto catorce.

Estructura del cierre, con lo que agrego el user despues:

> que dure esa escena, como generando misterio, hacele fade out cuando termine, fade
> out al negro

- Ultimos ~40 s con el alien, **sin cortar**: uno o dos planos largos y nada mas. Es
  el mismo criterio que la entrada del moog, y por el mismo motivo: cortar diluye.
- **Fade out al negro** al final. Junto con el fade de apertura, son los dos unicos
  fundidos del video; todo lo del medio sigue en corte seco.
- La duracion del plano es lo que genera el misterio: dejarlo respirar, no explicarlo.

## 12. Los seis textos eran UN solo error

8:18, 8:25, 9:08, 9:17, 9:55, 9:57 y 11:03 salian todos de `usgs_lava_01` con la
ventana mal anotada. Corregido de raiz. El escaneo de salida (`--salida`) es lo que
garantiza que no vuelva a pasar sin depender de mi anotacion.

## 13. AUDIO: el pumpumpum, medido

Aparece en 9:37 y en 10:21. Medido sobre la capa `moog` aislada:

| Momento | Pulsos | Frecuencia |
|---|---|---|
| 9:35 | 10 en 16 s | 2,90 Hz |
| 10:21 | 4 en 16 s | **1,27 Hz** |

Batido teorico entre las dos sierras desafinadas ±7 cents:

| Nota | Batido |
|---|---|
| Mi, 80 Hz | 0,65 Hz |
| Si, 119,9 Hz | **0,97 Hz** |

El de 10:21 coincide bastante (1,27 medido contra 0,97 teorico, y la deriva
independiente de cada oscilador ensancha el rango). El de 9:35 a 2,9 Hz es mas rapido:
probablemente el segundo armonico del sub batiendo contra el fundamental de las
sierras, porque el sub tambien lleva deriva propia.

**Fix**: bajar `detune_cents` de 7 a 2,5 y `deriva_cents` de 4,5 a 1,5 en `voz_moog`.
Un bajo sostenido no tiene que latir. La deriva se puso para que no sonara digital,
pero en una nota larga y grave se escucha como un pulso y no como vida.

## Estado

**Esperando el resto del feedback.** No renderizar hasta que el user avise.


---

# RONDA 5 · feedback del 2026-08-12

## AUDIO

### 1. El "sonido raro" cada 39 segundos: RESUELTO, y era mio

Marcado en **8:09, 8:48, 9:27, 10:06 y 10:46**. Las diferencias son 39, 39, 39, 40:
no era casualidad, era el ciclo de repeticion del moog (35 s de melodia + 4 de pausa).

**Causa: el aplanado que se agrego para sacar el latido.** Dividia por la envolvente
lenta, y eso levanta la COLA que estaba decayendo hasta el nivel pleno, o sea que
destruia el fade natural del final de cada pasada y dejaba un corte seco.

Fix: limitar esa ganancia a 2x (asi no puede resucitar una cola que muere) y agregar
un fade propio de 0,35 s en los bordes de cada pasada. Verificado: la discontinuidad
en los empalmes quedo en 0,035 contra 0,062 de una zona tranquila cualquiera.

**Agregado al QA**: `scripts/qa_scan_empalmes.py`. Busca saltos de nivel ESPACIADOS
REGULARMENTE, que es lo que distingue un artefacto de empalme de un evento musical:
un evento cae donde cae, un empalme cae cada N segundos exactos.

    python3.10 scripts/qa_scan_empalmes.py master.wav --desde 455

Honestidad: la herramienta pasa sobre el master actual, pero **no se pudo validar
contra el caso malo** porque la capa ya estaba regenerada cuando se escribio.

### 2. El moog de la ultima tirada tiene que ser OTRA melodia

> 9:39 no me gusta que el moog haga lo mismo. Es repetitivo, siendo la ultima tirada,
> tenemos que idear otra melodia, con el moog, pero algo mas ya de final, no se si
> tan chicharra, medio fantasmagorico, trabajemos en esto antes de meterlo

**No ejecutar todavia.** Hay que disenar la melodia de cierre primero. Direccion:
menos chicharra, mas fantasmagorico, y que se lea como final.

Insumo para esa charla: el motivo del disco es Si → Sol → Mi descendente (`docs/43`),
y el track 3 lo da vuelta terminando en Si. Una version de cierre podria quedarse en
el Mi sin resolver, o bajar una octava entera.

### 3. En 10:19 no va este moog

Va una variacion de la melodia nueva, **o el mismo pero mucho mas grave, aplastando**.

## VIDEO

### 4. Interferencia: gusta, pero esta sobreusada

> la interferencia como si el video estuviera danado me gusta, le pones mucho o todas
> las escenas con mucho de eso. No abuses

Y en dos puntos concretos molesta: **8:20** (un toque menos) y **10:26** (extrema).
Ademas en el primer minuto **la toma mas blanca parpadea con demasiada iluminacion**.

Fix: bajar el `noise` general, y sobre todo **dejar planos sin nada de grano**, para
que la interferencia sea un recurso puntual y no el default.

### 5. Los edificios siguen apareciendo

- **3:05**: se notan un toque.
- **3:40**: se ven los aires acondicionados pese a la transformacion.

Mover el recorte no alcanzo. Hace falta sumar deformacion sobre esos planos:
negativo, giro, o un recorte todavia mas cerrado.

### 6. Minuto 5: el volcan lejano no pega con el sonido de lluvia

Es donde suena la lluvia nueva, la clara y granular. **Ver el aporte pedido abajo.**

Y ademas: la lluvia deja de sonar y el video sigue con volcanes y hojas. Ahi tiene que
entrar otra escena antes de volver al volcan.

### 7. Los tiempos

- Las medusas: de **7:34 a 7:36 o 7:37**, cuando arrancan las voces.
- **8:20**: sostener ese plano un poco mas, antes de la lava invertida.
- **8:58/8:59**: el cambio de imagen y la entrada del moog tienen que caer juntos.

### 8. Lo que SI funciona

> que lindo la lava y el mundo invertido (asi flipeado), me gusta como queda con el moog

El negativo y el espejado son los recursos que hay que usar mas. Tambien: **del minuto
1 al 3 esta muy bien**.

### 9. La medusa del final

Se nota demasiado que es medusa y se muestra poco. Tiene que estar **mas tiempo que en
las apariciones anteriores y con mas zoom**, antes del fade a negro.

## Estado

**Esperando definir la melodia de cierre del moog antes de la proxima tanda.**
