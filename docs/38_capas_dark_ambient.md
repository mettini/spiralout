# 38 — Anatomía de un track dark ambient: capas y qué fuente grabar

> Para qué existe este doc: saber **qué salir a grabar** y **cómo se apilan las
> capas**, sin improvisar. Sale de la primera vuelta completa del experimento de
> deformación (`lab/thermal_mass/`), donde quedó claro que una fuente equivocada
> no se arregla con procesamiento.
>
> Técnica y referentes → `docs/27` hilo B. Cadenas concretas y qué salió mal →
> `lab/thermal_mass/README.md`.

## El principio: un edificio de bandas

Un track de este palo no es "un sonido con reverb". Es un **edificio donde cada
capa es dueña de un rango de frecuencias**, y casi no se pisan. Cuando dos capas
comparten banda, se pelean, y el resultado es el problema "tapado" que ya nos
comimos varias veces (`memory/feedback_muffled_sound_diagnosis.md`).

La prueba está en las dos piezas que ya existen: Thermal Mass tiene el 96% de su
energía debajo de 250 Hz y Cloud Chamber el 97% arriba. Se suman sin ensuciarse.
Eso no fue suerte, fue filtrado deliberado.

**La regla operativa**: antes de sumar una capa nueva, mirá qué banda ocupa. Si ya
hay alguien ahí, o le hacés lugar con un filtro, o no entra.

## Las seis capas

| # | Capa | Banda | Nivel relativo | Qué hace |
|---|---|---|---|---|
| 1 | **Sub / cama** | 20-120 Hz | referencia (0 dB) | El piso. Da tamaño. Es lo único que se siente en el cuerpo |
| 2 | **Cuerpo** | 120-400 Hz | −3 a −6 dB | Lo "pastoso", el petróleo. Da peso sin dar volumen |
| 3 | **Nube / medio** | 250-1500 Hz | −6 a −10 dB | Donde vive la sensación de espacio y de acorde |
| 4 | **Detalle / grano** | 1-6 kHz | −12 a −18 dB | **La capa que da escala.** Sin esto suena a subwoofer roto |
| 5 | **Aire** | 6 kHz+ | −18 a −24 dB | Que la grabación tenga "arriba". Casi inaudible sola |
| 6 | **Eventos** | ancho | picos a −10 dB | Lo único que marca el tiempo. Sin esto no hay track, hay drone |

Hoy tenemos la 1, algo de la 2 y la 3. **Faltan la 4, la 5 y sobre todo la 6.**

### 1 · Sub / cama (20-120 Hz)

Fuentes que sirven: **motores y bombas** (la losa radiante ya está hecha), el
compresor de la heladera, el motor del ascensor, la bomba de agua del edificio, un
aire acondicionado grande, el subte pasando por abajo, un transformador zumbando,
truenos lejanos.

Proceso: Paulstretch con window largo (3-5 s), bajar 1 o 2 octavas, notch en la
resonancia, mono debajo de 120 Hz, **sin saturar**.

Ojo: es la capa donde más fácil se acopla. Un motor a RPM fijas es un tono, y un
tono sostenido resuena. Buscar motores con **carga variable** (que suban y bajen de
vueltas) o grabar el arranque y la parada.

### 2 · Cuerpo (120-400 Hz)

Fuentes: **metal grande golpeado** y dejado sonar — un tanque, una reja, una
puerta de garaje, una escalera de hierro, un tubo de cañería, una chapa. También
cuerdas graves de un piano con el pedal apretado.

Proceso: stretch con window medio (1-2 s), poco o nada de pitch down, y filtrar
arriba de 400 para que no invada la nube.

Esta capa es la que más le falta a lo que tenemos. Es la diferencia entre "grave"
y "pesado".

### 3 · Nube / medio (250-1500 Hz)

Fuentes: cualquier cosa con **armónicos y sostenido** — voz sosteniendo una nota,
un gong, un vaso frotado, un arco sobre metal, cuerdas, un cuenco.

Proceso: el de Cloud Chamber. Stretch con window chico, apilar copias transpuestas
(quinta, octava, octava y quinta, dos octavas), desafinar cada una unos cents y
desfasarlas en el tiempo. High-pass para dejar el sótano libre.

### 4 · Detalle / grano (1-6 kHz) — la que falta y la que más importa

Es la capa que convierte una masa en un **lugar**. Sin ella el track suena
sumergido; con ella el oído entiende la escala del espacio.

Fuentes: **fricción y materia chica.** Papel arrugado, hielo crujiendo, hojas
secas, arena, un cepillo sobre cartón, una cremallera, pasos sobre grava, agua
goteando, insectos, el crujido de una silla de madera, el roce de la ropa.

**Cuidado, acá vive nuestra trampa histórica.** Material ruidoso con contenido
arriba de 1 kHz suena a **fritura** si se filtra mal
(`memory/pattern_noise_fritura.md`). La regla: si la capa es ruido, el corte alto
va a 800 Hz o menos. Si la capa tiene **estructura** (una fricción con textura, un
crujido con transitorio), puede vivir arriba de 1 kHz sin freír, pero hay que
mirar la banda HOT de 1,5-4 kHz con `task qa:spectral` y no confiar en el oído
después de dos horas de mezcla.

Y no usar `np.abs()` para excitar armónicos: genera cientos de intermodulaciones.
`tanh` (`memory/abs_rectifier_exciter_antipattern.md`).

### 5 · Aire (6 kHz+)

Fuentes: el **hiss del cuarto** grabado en silencio, viento lejano, una
respiración, el ruido propio de un preamp con la ganancia alta.

Nivel muy bajo, −18 a −24 dB. Se nota solo cuando se saca.

Ojo con el atajo: **un shelf de aire sobre material que no tiene contenido arriba
no agrega aire, agrega ruido.** Es una de las cuatro causas del "tapado" en
`memory/feedback_muffled_sound_diagnosis.md`. El aire hay que grabarlo, no
ecualizarlo.

### 6 · Eventos / transitorios — sin esto no hay track

Todo lo anterior es sostenido. Un track de 8 minutos hecho solo de sostenido es un
drone, y un drone no tiene tiempo: no se puede recordar ni contar.

Fuentes: **un golpe muy espaciado** (cada 30-60 segundos), un portazo con cola, una
gota, un click, una tapa que cae, un cable que se enchufa, el encendido de una
caldera, un interruptor.

Proceso: casi nada. Un evento es valioso justamente por ser el único elemento **no
deformado**. Reverb largo y nada más.

**Y si la fuente trae los golpes mezclados con zumbido** (un lavarropas, un motor
con carga), hay tres técnicas que salieron del primer experimento y sirven siempre
(implementadas en `lab/thermal_mass/render.py`):

1. **Separar golpe de zumbido con filtro de mediana** sobre el espectrograma
   (HPSS): mediana en el **tiempo** aísla lo estacionario, mediana en **frecuencia**
   aísla lo percusivo. En el caso real, el 18% que golpea contra el 82% que zumba.
   Esa es la limpieza, y es quirúrgica.
2. **Nunca Paulstretch en esta capa.** Randomiza la fase, o sea que destruye el
   ataque. Para bajar y alargar un golpe va **velocidad** (cinta lenta), que deja el
   transitorio intacto.
3. **Separar el ritmo del tono.** Si querés los golpes más espaciados, no
   enlentezcas más: se hunden abajo de 60 Hz y pierden definición. Cortá cada
   impacto y **re-espacialos** en una línea de tiempo más lenta, con nivel y
   separación irregulares (una máquina no es un metrónomo).

Y para que el golpe **pise** con reverb enorme en vez de ahogarse en él, tres
cosas: **pre-delay** de 200-300 ms (es la señal de tamaño más fuerte que tiene el
oído), **ducking** de la cola con la envolvente del golpe, y **transient shaper**
(envolvente rápida contra lenta). Sin eso, una cola de 32 s hace desaparecer los
impactos: medido, pasaron de 12 dB sobre el piso a cero detectables.

**Cuántas colas se enciman**: golpes cada 6 s con cola de 32 s son cinco sonando a
la vez. No acopla, pero se junta. Regla gruesa: la cola no debería pasar de 2 o 3
veces el intervalo entre golpes.

Cuántos: 3 a 6 en un track de 8 minutos. Menos de 3 y no hay tiempo; más de 8 y se
vuelve rítmico, que es otro género.

## Cómo saber si una fuente sirve, antes de procesarla

Esta es la lección más caras del primer experimento: **la fuente manda.** La bomba
de la losa tenía el 92% de su energía en una banda, y ningún procesamiento la
convirtió en textura.

Los cuatro criterios:

1. **Banda ancha.** Que tenga contenido repartido, no una nota. Si más del 80% de
   la energía está en una sola octava, es un tono: sirve para la capa 1 y para nada
   más.
2. **Movimiento interno.** Algo que cambie durante la grabación: que suba de
   vueltas, que se enfríe, que gotee irregular. Un tono perfectamente estable
   estirado da un tono perfectamente estable.
3. **Un transitorio en algún lugar.** Aunque sea uno. Es lo que después se usa
   como evento.
4. **Sin comprimir.** WAV, no m4a del celular. El stretch extremo **amplifica los
   artefactos del codec**, porque cada cuadro espectral queda sostenido un segundo
   entero en vez de pasar en 20 ms. Con la Volt 276 y 24 bits.

Y dos distancias de micrófono siempre: **cerca** para el detalle y el grano,
**lejos** para el cuarto. Son dos capas distintas de la misma toma.

Para chequearlo sin adivinar:

```bash
python3.10 scripts/check_source.py grabacion.wav
```

Dice en qué banda vive, si es tono o textura, si tiene transitorios y para qué
capa sirve.

## Lista de caza (fuentes concretas a grabar)

De lo que hay en una casa y un barrio, ordenado por capa:

| Capa | Candidatos |
|---|---|
| Sub | bomba de la losa ✓ · compresor de la heladera · motor del ascensor · bomba de agua del edificio · subte de fondo · aire acondicionado exterior |
| Cuerpo | reja del garaje golpeada · escalera de hierro · tanque de agua · cañería con la llave abierta · puerta de chapa · piano con pedal |
| Nube | voz sosteniendo una nota · vaso o cuenco frotado · arco sobre una reja · gong o cacerola |
| Grano | hielo en un vaso · papel · hojas secas · grava · cremallera · goteo · madera crujiendo |
| Aire | el cuarto en silencio a ganancia alta · viento en una ventana · respiración |
| Eventos | portazo · interruptor · encendido de la caldera · una tapa que cae · un cable enchufándose |

## La melodía: sí, pero con dos reglas

La pregunta era si sumar un motivo de synth arriba de todo esto. **Sí**, y en la
familia hay precedente: Lustmord tiene material melódico, pero mínimo y enterrado.
Dos reglas.

### Regla 1 — La afinación no es libre, ya está definida por el material

Medido sobre las piezas que existen:

```
thermal_mass    fundamental  71.3 Hz  =  D2 −50 cents
cloud_chamber   fundamental 286.7 Hz  =  D4 −42 cents
```

O sea: **todo el material está medio semitono abajo de D**, en el cuarto de tono
entre C#2 y D2. Si le metés un synth afinado a 440 estándar, va a chocar con todo.
Tres salidas:

1. **Subir el material +50 cents** para que caiga en D2 exacto, y tocar en D.
2. **Afinar el synth −50 cents** (o bajar el LA de referencia a ~427 Hz) y tocar
   en D. El material queda intacto.
3. **Asumirlo como atonal** y que el motivo no sea de notas afinadas sino de
   glissandos y ruido con altura. Es la opción más del palo, y la más difícil.

Yo iría por la 2: no toca el sonido que ya te gustó y te deja tocar normal.

### Regla 2 — Entra tarde, dice poco, dura mucho

- **3 a 5 notas**, no una melodía.
- **Entra pasado el primer tercio** del track, nunca al principio.
- Cada nota **dura entre 8 y 20 segundos**.
- Nivel **−12 a −18 dB** respecto de la cama: tiene que estar adentro de la masa,
  no arriba.
- Banda 200-800 Hz, filtrada arriba: si el synth tiene brillo, compite con la capa
  de grano y gana, y ahí se rompe el edificio.

**Y el motivo Voyager no se toca.** Es de Heliopause y está protegido
(`memory/voyager_protegido.md`). Un track nuevo lleva un motivo nuevo.

## Orden de armado

De abajo hacia arriba, una capa por vez, mirando el espectro después de cada una:

1. Cama (1) — define la nota y la duración del track.
2. Eventos (6) — **antes** que el resto del relleno, porque definen la estructura
   temporal y todo lo demás se acomoda alrededor.
3. Cuerpo (2) y nube (3) — el volumen del edificio.
4. Grano (4) y aire (5) — la escala y el lugar.
5. Melodía (7), si va, al final y baja.
6. `task qa:spectral` y mirar bandas + correlación. Después escuchar.

Nunca al revés. Si empezás por la melodía, terminás con una canción con reverb.
