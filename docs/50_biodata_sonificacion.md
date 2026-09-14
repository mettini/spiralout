# 50 — Biodata: sonificar un hongo

> Estado: **EN PAUSA, a criterio del user.** El PoC del mapeo está hecho y sonando
> (`lab/biodata/`); falta hardware y organismo, y el user dejó dicho el 2026-08-29
> que no sabe si lo va a hacer: "está copado como experimento pero no sé si me
> desvío mucho, en todo caso usaremos otra cosa".
>
> **No hay nada esperando ni nada que se pudra si esto no arranca.** El doc queda
> para retomarlo sin volver a pensarlo. Antes de arrancar, leer la sección
> "¿Vale la pena o es un desvío?" al final, que es la que contesta esa duda.
>
> Destino: tracks 2 y/o 3 de **Athanor** (TX02), donde la entidad muestra la flora y
> la fauna de su planeta. Ver `docs/39_transmission_02.md`.

## Qué es esto, sin adornos

**El hongo no hace música ni suena.** Lo que se mide es una variación eléctrica y lo
que la vuelve música es el MAPEO, que es una decisión de composición. Decirlo al
revés es marketing, y encima del berreta.

Hay dos mediciones distintas que se confunden todo el tiempo:

| | Qué mide | Con qué | Escala |
|---|---|---|---|
| **Biodata** (PlantWave, MIDI Sprout) | variación de resistencia entre dos puntos | 2 electrodos, corriente mínima | por debajo de 1 Hz |
| **Spiking** (línea Adamatzky) | potencial eléctrico extracelular | microelectrodos en el micelio | picos de minutos, trenes de horas |

La primera es la fácil y la que hacen los aparatos comerciales. La segunda es la del
paper de "cómo hablan los hongos" y la que da los trenes de picos.

## El hallazgo del PoC: la compresión compone

`lab/biodata/sonificar.py` mapea una señal lenta a eventos de nota. Se corrió sobre
señal **sintética declarada como tal**, que imita la estadística publicada (picos de
minutos agrupados en trenes, dos poblaciones).

| Compresión | Hongo comprimido | Notas/min | Qué sale |
|---|---|---|---|
| 15x | 15 min en 60 s | 3 | drone, casi sin eventos |
| **60x** | **1 h en 60 s** | **8** | **respiración ambient** |
| 360x | 6 h en 60 s | 40 | arpegio, textura |

**Mismo organismo, misma señal, tres géneros distintos.** La compresión de tiempo es
la decisión más fuerte de toda la cadena, y es donde entra el compositor.

El 60x cae justo en el terreno del disco: huecos de 1,4 a 10,8 s con mediana de 4,2,
sonido el 43% del tiempo. Y la irregularidad no es aleatoria, viene de los trenes,
que es lo que a una secuencia programada le cuesta conseguir.

**Conclusión operativa: el mapeo ya funciona.** La compra de hardware no es para
saber si la idea sirve, es para tener **material propio**, que borra la pregunta de
licencia entera y da algo que nadie más tiene.

## La trampa de los electrodos (leer antes de comprar)

**Dos metales distintos en un medio húmedo son una pila.** Vas a medir tus propios
electrodos, no el hongo, y con una deriva que parece señal biológica. Los dos
electrodos tienen que ser **del mismo metal**, idealmente acero inoxidable.

Opciones, de mejor a peor: agujas de acupuntura de acero inoxidable (finas, es lo
que se clava en el micelio), parches de ECG adhesivos (mejor contacto en tejido
blando, se despegan con humedad), pinzas cocodrilo (crudo, lastima el tejido).

## El circuito: dos caminos

**A · el 555.** El hongo ES la resistencia de un oscilador astable: su deriva mueve
el tono. Sale a audio directo, entra por la Volt 276, se graba. Cero drivers, cero
código, sonido la primera tarde. Es **el experimento "Silicon" de `docs/27` con un
hongo como componente**. Limitación: es un instrumento, no una medición.

**B · Arduino.** Nano, dos electrodos, una resistencia de 1M. Lee y escupe números
por serie. Te queda el **dato archivado y remapeable** sin volver a medir, que es la
línea de `docs/41_data_como_origen.md`. Es la que sirve para el disco.

**Lo que NO funciona: medir directo por la interfaz de audio.** La Volt 276 está
acoplada en alterna, con pasaaltos entre 5 y 20 Hz. La señal está por debajo de 1 Hz.
La interfaz literalmente no la ve. Por eso la opción A convierte a audio antes.

## Qué comprar

Precios verificados en Mercado Libre Argentina el 2026-08-28. Los de electrónica NO
los verifiqué, son de casa de electrónica común (en CABA, zona Paraná y Perón).

**El organismo** (ver el timing más abajo, NO comprar antes del viaje)

- Kit de autocultivo de gírgolas, **ARS 42.750**, envío gratis, 384 resultados en el
  listado → https://listado.mercadolibre.com.ar/kit-cultivo-girgolas
  La gírgola es *Pleurotus ostreatus*, **exactamente la especie del paper**.
- Micelio líquido en jeringa desde ARS 22.000, si algún día se quiere inocular
  sustrato propio → https://listado.mercadolibre.com.ar/micelio-liquido-girgola

**El circuito** (esto sí, antes del viaje)

- NE555 → https://listado.mercadolibre.com.ar/ne555
- Protoboard → https://listado.mercadolibre.com.ar/protoboard
- Cables dupont → https://listado.mercadolibre.com.ar/cables-dupont
- Kit de resistencias → https://listado.mercadolibre.com.ar/kit-resistencias
- Kit de capacitores cerámicos → https://listado.mercadolibre.com.ar/kit-capacitores-ceramicos
- Pinzas cocodrilo → https://listado.mercadolibre.com.ar/pinzas-cocodrilo
- Arduino Nano (camino B) → https://listado.mercadolibre.com.ar/arduino-nano

**Los electrodos**

- Agujas de acupuntura acero inoxidable → https://listado.mercadolibre.com.ar/agujas-acupuntura-acero-inoxidable
- Electrodos ECG descartables → https://listado.mercadolibre.com.ar/electrodos-ecg-descartables

## Timing (el viaje del user: 4 al 10 de septiembre)

**El kit NO se pide antes del viaje.** Tarda de una a tres semanas en fructificar y
hay que humedecerlo todos los días. Arrancándolo ahora, el momento crítico cae justo
cuando no hay nadie, y se pierde.

| Cuándo | Qué |
|---|---|
| **28/08 al 03/09** | Comprar y armar el circuito. Probarlo en una **planta de interior que ya haya en la casa**: da señal galvánica más fuerte y limpia que un hongo, y valida el rig gratis. Si en una hoja no se ve nada, el problema es el circuito o los electrodos |
| 04 al 10/09 | Viaje. Nada vivo esperando |
| **11/09 en adelante** | Pedir el kit. Mientras coloniza, medir una bandeja de gírgolas de verdulería como **control**: tejido cortado contra micelio vivo |
| ~25/09 | Medir lo bueno |

Esa comparación entre bandeja de verdulería y micelio vivo **es en sí misma la nota
de blog**.

## Ideas de post para el blog

El blog está definido en el dashboard como la voz del label donde se acuñan términos
propios (vibe composing, vibe recording). Esto es material de esa serie, **no de la
voz de ÆM**, que es misterio y no explica nunca.

1. **"El hongo no compone: la compresión compone."** El post principal, y el que
   tiene el ángulo que casi nadie usa. Todo el mundo publica "escuchá lo que dice el
   hongo" y la nota es que eso es mentira: el organismo aporta la irregularidad y el
   humano aporta absolutamente todo lo demás. Se sostiene con la tabla de las tres
   compresiones, que es evidencia y no opinión. Citable y discutible, que es lo que
   se busca para SEO y GEO.
2. **"Dos metales distintos son una pila."** Post corto y técnico sobre la trampa de
   los electrodos. Es el error que casi ningún tutorial menciona y el que hace que
   midas tu propio cable. Los posts que resuelven un error concreto son los que
   traen búsquedas.
3. **"Tejido cortado contra micelio vivo."** La comparación de la bandeja de
   verdulería contra el bloque colonizado, con las dos señales al lado. Contesta la
   pregunta que cualquiera se hace primero: ¿no alcanza con comprar un hongo?
4. **"Por qué la interfaz de audio no puede ver esto."** El acople en alterna, el
   pasaaltos, y por qué hay que convertir a audio antes de grabar. Explica una
   limitación real de equipamiento que mucha gente tiene.
5. **Serie completa: de la planta al disco.** El arco desde la primera hoja medida
   hasta el track de Athanor, si es que llega al disco. Vale también si NO llega:
   un experimento que se descarta con razones es contenido honesto.

## El timelapse

Idea aparte pero del mismo experimento: un bloque de micelio colonizando da
**material de video propio**. Orgánico, lento, no reconocible, sin licencia de nadie
y sin sorpresas escondidas adentro (ver `docs/video/27_lessons_patterns.md`: una
fuente era una ciudad disfrazada de gotas, otra tenía fronteras y texto, y la de
rayos estaba vetada por un cohete adentro).

**Cámara: lo más barato es un teléfono viejo dedicado.** Cualquier teléfono moderno
hace timelapse en 4K de fábrica, y el proyecto exige 4K (`memory/feedback_video_must_be_4k`).
El problema no es la cámara, es que hay que dejarla parada varios días.

Dos detalles prácticos que arruinan un timelapse de días si no se resuelven:

- **Luz constante.** Si entra luz de ventana, el ciclo día/noche hace parpadear todo
  el clip. Va en caja cerrada con una luz chica siempre prendida.
- **El bloque suele venir en bolsa.** El plástico refleja y deforma. Hay que decidir
  si se filma a través, se abre, o se filma sólo la fructificación.

No es bloqueante para el experimento de sonido. Es un extra que sale gratis si el
kit ya está andando.

## Material con licencia verificada (investigado 2026-08-29)

**Esto cambia el calculo del doc entero: hay hongo REAL, con licencia limpia, sin
comprar nada y sin esperar semanas.** Son DATOS (texto, voltaje contra tiempo), no
audio de otro, que es exactamente lo que come `lab/biodata/sonificar.py`.

| Dataset | Qué trae | Licencia | Tamaño |
|---|---|---|---|
| [Zenodo 5790768](https://zenodo.org/records/5790768) · *Recordings of electrical activity of four species of fungi* (Adamatzky) | Ghost fungi (*Omphalotus nidiformis*), Enoki (*Flammulina velutipes*), Split gill (*Schizophyllum commune*), Caterpillar (*Cordyceps militaris*). Texto en zip | **CC BY 4.0** | 84,6 MB |
| [Zenodo 3997031](https://zenodo.org/records/3997031) · *Electrical activity of fungi: Spikes detection and complexity analysis* (Dehshibi y Adamatzky) | 6 setups, de 5 a 16 canales, entre 60 y 93 **horas** de registro continuo. Incluye la deteccion de picos en MATLAB | **CC BY 4.0** | 91 MB (RAR) |

**CC BY 4.0 permite uso comercial.** La condicion es atribuir: nombrar autores,
enlazar la licencia e indicar si se hicieron cambios. Para un disco eso se resuelve
con una linea en los creditos, y encima **conviene** decirlo: es parte de la
historia.

Los dos son de acceso abierto y verificados en la fuente el 2026-08-29, no
asumidos. Ojo con el segundo: viene en RAR, hace falta descompresor.

### Lo que esto implica para la decision

Sube al primer lugar una opcion que ayer no existia: **hongo real, gratis, hoy, con
60 a 93 horas de registro continuo**, que es mucho mas de lo que se mediria en casa
con un kit en las primeras semanas.

El cultivo propio NO queda muerto, pero cambia de argumento: ya no es "conseguir la
señal" (esta resuelto) sino **material propio + la historia de haberlo cultivado +
el timelapse**. Es una decision de contenido, no tecnica.

## Enganches

- `lab/biodata/sonificar.py` — el mapeo, ya funcionando.
- `docs/41_data_como_origen.md` — la línea de dato real como origen. El hongo entra
  por la misma puerta que el plasma de las Voyager.
- `docs/39_transmission_02.md` — Athanor, tracks 2 y 3.
- `docs/27_lab_experiments_and_references.md` hilo A — "Silicon", que es el mismo
  circuito con otro componente.
- `docs/40_pure_data_lab.md` — Pd como host de sonificación en tiempo real.


---

## ¿Vale la pena o es un desvío? (para leer al retomar)

El user planteó la duda el 2026-08-29. Queda contestada acá para no re-derivarla.

### Qué compra el hongo, exactamente

**Irregularidad que no es aleatoria.** Esa es la única propiedad musical que aporta,
y es una propiedad difícil: una secuencia programada suena a grilla, y un
`random()` suena a ruido sin intención. Los trenes de picos caen en el medio, que es
donde vive el ambient.

Todo lo demás (escala, rango, densidad, timbre, tempo) lo pone el mapeo, que **ya
está escrito y funcionando**. O sea que el hongo no es la parte difícil ni la
insustituible.

### Lo que NO se pierde si esto no se hace

`lab/biodata/sonificar.py` mapea **cualquier** serie lenta. No sabe ni le importa de
dónde viene el número. Si el hongo se cae, el mapeo alimenta a otra fuente sin
cambiar una línea. **La inversión ya hecha no está atada a este experimento.**

### Las alternativas que dan la misma propiedad

Ordenadas de menos a más esfuerzo. Todas producen irregularidad no aleatoria.

| Fuente | Costo | Coartada narrativa | Estado |
|---|---|---|---|
| **Plasma de las Voyager** | cero, es descarga | **la mejor de todas**: el motivo se llama voyager y TX01 se llama Heliopause | falta verificar formato y licencia (`docs/41` §4) |
| **El estado de la máquina** ("Silicon") | cero | media: es la línea de "compuesto con AI" llevada al hardware | hilo A de `docs/27`, abierto |
| **Sismos (USGS)** | cero, público y continuo | ninguna todavía | sin explorar |
| **Field recording orgánico** | tiempo, no plata | fuerte para el track 2: `docs/39` dice que ahí las fuentes orgánicas **son el tema** | ya está en el plan de TX02 |
| **Hongo propio** | ~ARS 43.000 + circuito + semanas | la más fuerte de todas si se cultiva | este doc |

### El argumento honesto a favor del hongo

No es sonoro, es de **propiedad y de historia**. Material medido por nosotros: sin
licencia de nadie, sin sorpresas escondidas adentro (el proyecto ya se comió una
fuente con un cohete de NOAA y otra con fronteras dibujadas), y una nota de blog que
nadie más puede escribir porque nadie más cultivó el bicho.

### El argumento honesto en contra

Es **la fuente más cara y más lenta de la tabla** para conseguir una propiedad que
el plasma de las Voyager da gratis y con mejor coartada narrativa. Y suma dos
dependencias nuevas al proyecto: electrónica y un organismo vivo que hay que regar.

### La recomendación

**Si el objetivo es el disco, empezar por el plasma de las Voyager.** Es gratis,
está en la narrativa desde el minuto cero, y el mapeo ya lo puede consumir. El paso
0 es verificar formato y licencia, que es lo que `docs/41` ya dejó anotado como
pendiente.

**Si el objetivo es el blog y tener algo propio**, el hongo. Ahí el costo se paga
con contenido que nadie más tiene.

Las dos no compiten: el mapeo es el mismo y sirve para las dos.
