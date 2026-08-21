# 45 · Cómo se arma una melodía

Referencia de trabajo para las líneas melódicas del proyecto. Escrito después de tres
intentos fallidos con el moog de TX02, donde el sonido estaba bien y la melodía no
existía.

Implementación: `transmissions/02/bj3_n_pt/melodia.py`. El instrumento está en
[`44_sintesis_synths.md`](44_sintesis_synths.md), el material armónico en
[`43_motivo_em_mas_h.md`](43_motivo_em_mas_h.md).

---

## Los cuatro requisitos

Una secuencia de alturas no es una melodía. Faltan cuatro cosas, y las cuatro son
verificables sobre el código antes de escuchar nada.

### 1. Un motivo que vuelve

Un motivo son 4 o 5 notas con un **ritmo propio**. La melodía se reconoce porque ese
motivo reaparece, variado. Sin retorno no hay identidad y suena a paseo al azar.

El ritmo pesa más que las alturas: un motivo se reconoce cuando vuelve con las mismas
proporciones de duración aunque las notas cambien.

**El motivo necesita un giro, no una rampa.** Cuatro notas subiendo derecho es el
contorno más predecible que existe: el oído adivina la siguiente y se desengancha. La
figura que funciona es **sube, sube, baja, baja, sube**. El retroceso hace además que la
nota de llegada pese más, porque se hizo esperar.

**El retroceso tiene que ser de dos grados, no de uno.** Bajar un solo grado se escucha
como un adorno, no como un giro: el contorno sigue leyéndose como ascendente. Bajando
dos, la llegada se hace por salto (una 4ta) y ahí sí la nota final llega a algún lado.

**Variar por inversión.** Cuando el motivo vuelve, darlo vuelta es material reconocible
en vez de material nuevo. Se espeja el contorno por **grado de la escala**, no por
intervalo exacto: la inversión intervállica literal se sale de la escala.

El salto de llegada también se espeja. Si el motivo sube una 4ta para llegar, la
inversión baja una 4ta.

**Antipatrón:** prohibir la repetición. `PLAN_RONDA6.md §A2` fijaba la regla "nunca se
repite un par de notas consecutivas en toda la ventana" para evitar el bucle. Eliminó el
bucle y también la melodía. Lo que no se puede repetir es la **pasada entera**; el motivo
tiene que repetirse.

### 1b. Dos enunciados seguidos nunca comparten contorno

El requisito que balancea al anterior, y el que es más fácil de romper sin darse cuenta.

Un **enunciado** es una pasada del motivo. El motivo tiene que volver, pero **cada
enunciado tiene que variar por lo menos una cosa**: el contorno, el largo, o de qué parte
del motivo sale.

El error concreto: repetir la misma figura transpuesta. Sube, sube, baja, baja, sube desde
Mi, y después sube, sube, baja, baja, sube desde Sol. Eso es una **secuencia**, que es una
técnica válida usada una vez, pero encadenada dos veces se escucha como copia y no como
desarrollo. Sobre el código no se ve: son notas distintas. Lo que se repite es la forma.

Las variaciones disponibles, de menos a más lejos del original:

| Técnica | Qué cambia |
|---|---|
| **secuencia** | misma figura, otra altura. Usar **una** vez, nunca dos seguidas |
| **cambio de contorno** | mismo material, otra forma. Si el motivo hace ↑↑↓↓↑, este hace ↑↓↑↑ |
| **inversión** | el contorno espejado. Ver arriba |
| **fragmento** | solo un pedazo del motivo, y por eso más corto |
| **aumentación / disminución** | mismo contorno, duraciones al doble o a la mitad |
| **extensión** | se le agregan notas a la cola |

**Cómo se verifica:** escribir el contorno de cada enunciado como flechas y comparar
consecutivos. `melodia.py` tiene `verificar_contornos()`, que **aborta el render** si dos
seguidos coinciden. Sin la guarda esto se vuelve a romper: el contorno repetido no se ve
leyendo la lista de notas.

### 2. ~80% de movimiento por grado conjunto

Proporción de referencia: 80% segundas, 20% saltos mayores a una segunda.

Una línea hecha solo de saltos el oído la lee como **arpegio del acorde**, o sea armonía,
no como melodía. Es lo que pasa si el material se limita a las notas del acorde: con Mi,
Sol y Si todo intervalo es una 3ra o más.

Por eso hacen falta las **notas de paso** de la escala. En Mi menor natural: Fa#, La y Do.
Son las que permiten que exista una segunda.

**Dónde van los saltos:** al empezar frase. Adentro de la frase se mueve por grado
conjunto.

**Gap-fill:** un salto grande se compensa con movimiento en dirección contraria. Después
de subir una 6ta el oído espera que se llene el hueco bajando por grados.

### 3. Contorno de arco, con un pico único

La melodía sube a un punto alto y después baja. El pico:

- suena **una sola vez** en toda la línea
- se llega **por grado conjunto** desde abajo, no de un salto
- cae alrededor del 55 al 65% del recorrido, no en el medio exacto ni al final
- conviene un **retroceso justo antes**: subir, bajar un grado, y ahí sí llegar. El pico
  pega más fuerte que llegando derecho

Es la nota más alta que va a existir en esa voz. Si aparece dos veces deja de ser pico.

### 4. Antecedente y consecuente

Dos frases emparejadas:

- **antecedente** (pregunta): cierra en una nota que **no** resuelve, la 5ta o la 2da
- **consecuente** (respuesta): mismo material, cierra en la tónica

Es lo que da la sensación de que la línea dice algo en vez de solo transcurrir.

---

## El registro

Abajo de **~150 Hz** el oído no percibe melodía, percibe **bajo**: sigue la función
armónica y no el contorno. El rastreo de alturas trabaja más o menos entre **200 y 800
Hz**.

Una línea correcta en cuanto a motivo, pasos y arco puesta en 80-120 Hz igual no se va a
escuchar como melodía. Es la causa más común de "no siento melodía" cuando el análisis
sobre el papel da bien.

---

## La articulación, en un monosintetizador

Un mono toca una nota a la vez, y de ahí sale su articulación característica:

| | Cuándo | Qué pasa |
|---|---|---|
| **legato** | la nota siguiente entra antes de soltar la anterior | la envolvente **no** se re-dispara y la altura se desliza (glide) |
| **staccato** | hay silencio entre medio | la envolvente **se re-dispara** y se escucha el ataque |

El glide es de **~80 ms**, no de segundos. Con glide de 2 a 5 s nunca se escucha una nota
llegar: es un deslizamiento continuo, que el oído lee como textura de fondo.

Una línea expresiva mezcla las dos articulaciones. En `melodia.py`: legato adentro de la
frase, ataque al empezar frase.

### Implementación sin clicks

Un solo oscilador continuo para toda la línea, con la frecuencia siguiendo un contorno.
La fase se acumula sin cortes, así que no hay click posible en ninguna juntura.

Renderizar nota por nota y concatenar da "tac tac" en cada empalme, aunque las
envolventes cierren.

El glide se interpola **exponencialmente**, no lineal: el oído escucha proporciones de
frecuencia, no diferencias.

### La nota que llegó no se sostiene: resuena

Distinción que cambia todo. Cuando la línea llega a la nota de destino hay dos maneras
de que esa nota siga presente:

| | Cómo suena |
|---|---|
| **sostener el oscilador** 10 s en la misma altura | la nota está siendo **mantenida**. Es un drone, no una llegada. Se escucha que hay una máquina generando tono |
| dejarla **resonar**: el tono crudo se apaga y lo que queda es la cola | la nota **resonó**. Es lo que hace un instrumento |

Lo segundo se consigue con un **delay realimentado con filtro en el lazo**
(`aem.effects.eco`). Cada repetición vuelve a pasar por el pasabajos, así que la cola se
va oscureciendo y perdiendo definición en vez de repetir lo mismo más bajo. Eso es lo que
la hace leer como estela y no como eco de karaoke.

Consecuencia práctica: **las notas de llegada se acortan**. En `melodia.py` pasaron de
10,7 s de tono sostenido a 7,1 s de tono más la estela. Y el hueco entre frases se alarga
(4,5 s), porque ahí es donde vive la cola.

Valores usados: 2,9 s de tiempo, 0,44 de realimentación, 45% de mezcla, pasabajos a 1900
Hz en el lazo. El tiempo elegido hace que la repetición caiga adentro del hueco.

### El respiro entre enunciados no puede ser fijo

Un silencio constante entre frases suena mecánico por la misma razón que un contorno
repetido: es una regularidad que el oído detecta y a partir de ahí deja de escuchar.

La música respira distinto según dónde esté:

| Dónde | Respiro | Por qué |
|---|---|---|
| entre enunciados de la **misma frase** | corto | la frase sigue, no terminó |
| cruzando de **frase a frase** | largo | es un límite estructural |
| **antes del pico** | largo | la pausa acumula |
| **después del pico** | el más corto de todos | el gap-fill es un impulso: si se espera, se pierde |
| **antes del retorno del motivo** | el más largo | el retorno necesita aire para leerse como retorno |

En `melodia.py` van de **1,8 a 7,0 s**, ocho valores distintos, y son parte de la
definición de cada enunciado.

### La cola: el final necesita aire propio

**Bug fácil de cometer:** si el buffer termina donde termina la última nota, la estela de
esa nota **queda truncada**. Con un delay de 2,9 s y cuatro repeticiones son casi 12 s de
cola que no tienen dónde ir, y eso se escucha como un corte por más que la nota siga
sonando.

Se reservan **9,5 s** después de la última nota. Ahí el oscilador sigue corriendo en la
altura final con la amplitud cayendo, y la estela repica adentro de ese espacio.

Medido: −23 dB al terminar la nota, −37 a los 8 s, y recién ahí entra el fade.

### La nota final

Contra qué resuelve la melodía depende de en qué está afinada **la cama**, no de cuál es
la tónica del motivo.

En TX02 la cama está en **Re 71,3 Hz** y el motivo es Em, o sea Em7 con el Re de séptima.
Las dos candidatas:

| Nota | Hz | Cómo resuelve |
|---|---|---|
| **Mi** | 320,1 | tónica del motivo, pero contra la base es una 2da: queda **colgada**, suspendida |
| **Re** | 285,2 | la fundamental de la base. La bajada pura continúa un grado más y **aterriza** en la nota sobre la que está construido todo el tema |

`melodia.py` rinde **las dos** (`13_MELODIA_cierre_MI.wav` y `..._RE.wav`) porque es una
decisión estética, no técnica: Re cierra, Mi deja abierto.

### El ataque sube, no golpea

Al entrar una frase nueva después del hueco, el ataque **tarda en llegar al máximo**:
1,9 s con curva suave en las dos puntas (smoothstep), no una rampa de 0,35 s.

Y arranca **desde donde quedó la estela**, no desde cero. Así la frase nueva emerge de la
cola de la anterior en vez de aparecer al lado.

Medido: −40 dB al empezar, −23,7 dB a los 1,9 s.

### Que la nota suene

Cuatro cosas, en orden de cuánto pesan:

1. **El release ocupa el silencio.** Cuando termina una corrida ligada y viene una nota
   con ataque, la envolvente no puede caer a cero de golpe. Se apaga exponencialmente a
   lo largo de esos segundos, que es lo que pasa al soltar una tecla: la nota sigue
   sonando mientras muere. El oscilador sigue corriendo en la altura anterior, así que
   lo que resuena es esa misma nota.

   Es el error más audible de todos y el más fácil de pasar por alto, porque el código
   se ve bien: hay una nota, hay un silencio, hay otra nota. Lo que falta es la juntura.

   Medido en `melodia.py`, primer hueco: −22,9 dB al soltar, −38,6 a los 2 s, −41,3 a
   los 3, y a los 4 vuelve a subir apenas porque ahí entra la repetición de la estela.
   Cortada en seco eso era un corte y se escuchaba como tal.
2. **Sostenido plano en las ligadas.** Decaer de 0,95 a 0,93 a lo largo de la nota, no a
   0,85. Una nota que cae rápido se escucha como que pasó, no como que suena.
3. **Sala grande y mojada**, encima de la estela.
4. **Duraciones, sin exagerar.** Cortas de 2,2 a 2,8 s, llegadas de 5 a 6,5 s. Con notas
   de 1 a 3 s contra una cama sostenida no hay melodía audible: no hay tiempo de
   reconocer la altura. Pero pasar de 6,5 s tampoco sirve, porque ahí la nota deja de
   llegar y empieza a ser sostenida. Con la estela puesta, el techo baja.

---

## La segunda voz

Un mono es monofónico, pero nadie graba una sola pasada. La segunda línea:

- **no entra al principio.** La principal tiene que quedar sola para poder reconocerse.
  Si la segunda entra antes de que el motivo se haya enunciado, las dos se cancelan.
- entra en el **pico**, que es donde una segunda voz suma de verdad
- vuelve como **pedal** en el cierre, sosteniendo una nota mientras la principal resuelve

---

## Estructura usada en el moog de TX02

Ventana de 200 s (7:35 a 10:55 del tema). Forma **A A' B A''**.

Nueve enunciados agrupados en cuatro frases. Ninguno repite el contorno del anterior.

| # | Frase | Enunciado | Desde | Respiro antes | Contorno |
|---|---|---|---|---|---|
| 1 | **A** antecedente | el motivo | 0:00 | — | ↑↑↓↓↑ |
| 2 | A | contorno cambiado | 0:23 | 2,8 s | ↑↓↑↑ |
| 3 | **A'** consecuente | inversión | 0:45 | 6,0 s | ↓↓↑↑↓ |
| 4 | A' | fragmento | 1:08 | 2,5 s | ↑↓↑ |
| 5 | **B** partida | al pico: único Do, único Mi alto | 1:28 | 5,5 s | ↑↑↓↑ |
| 6 | B | gap-fill | 1:49 | 1,8 s | ↓↑↓ |
| 7 | B | puente | 2:07 | 4,0 s | ↓↓↑ |
| 8 | **A''** retorno | el motivo vuelve | 2:28 | 7,0 s | ↑↑↓↓↑ |
| 9 | A'' | bajada pura, cierra | 2:51 | 3,2 s | ↓↓↓ |

Última nota hasta 3:10, y los 9,5 s restantes son cola para la estela.

Motivo: `mi sol la sol fa# si`, ritmo largo · corto · corto · corto · corto · más largo.

El enunciado 2 es el que suele salir mal: la tentación es transponer el motivo una 3ra
arriba, y eso da el mismo contorno dos veces seguidas. Acá cambia la figura (`sol la sol
la si`) usando el mismo material.

El 9 es la única bajada sin giro de toda la línea, y por eso se lee como final.

Duraciones: notas cortas de 2,2 a 2,8 s, llegadas de 5 a 6,5 s, y la última de 9. Ninguna
pasa de 6,5 salvo el cierre: el resto lo hace la estela.

Material, sobre la base de 71,3 Hz y dos octavas arriba:

| | Hz | Función |
|---|---|---|
| Re | 285,2 | la fundamental de la base, séptima del acorde |
| Mi | 320,1 | tónica del motivo |
| Fa# | 359,3 | paso |
| Sol | 380,7 | tercera del motivo |
| La | 427,3 | paso |
| Si | 479,6 | la **H** del motivo, quinta |
| Do | 508,2 | paso, y la nota que se sale del encierro de tres alturas |
| Mi alto | 640,3 | el **pico**, una sola vez |

Medido sobre la línea: **63% de grados conjuntos**, pico una vez al 51% de la ventana.

Queda por debajo del 80% de referencia a propósito. Los saltos son casi todos las
llegadas del motivo (la 4ta que cierra el giro) y los arranques de frase. El único
intervalo grande de verdad es la caída desde el pico, y esa se llena bajando por grados.

---

## Chequeo antes de escuchar

`melodia.py` imprime esto en cada render:

```
 # frase enunciado               desde  respiro contorno    larga
 1 A     el motivo              0:00     0.0s  ↑↑↓↓↑        5.8s
 2 A     contorno cambiado      0:23     2.8s  ↑↓↑↑         4.8s
 3 A'    inversion              0:45     6.0s  ↓↓↑↑↓        5.8s
 4 A'    fragmento              1:08     2.5s  ↑↓↑          5.8s
 5 B     al pico                1:28     5.5s  ↑↑↓↑         6.3s
 6 B     gap-fill               1:49     1.8s  ↓↑↓          4.8s
 7 B     puente                 2:07     4.0s  ↓↓↑          4.8s
 8 A''   el motivo vuelve       2:28     7.0s  ↑↑↓↓↑        5.8s
 9 A''   bajada pura, cierra    2:51     3.2s  ↓↓↓          8.7s
   contornos: ninguno repite el del anterior
   respiros:  de 1.8 a 7.0s, ocho valores distintos

grados conjuntos: 26/41 = 63%
el pico (Mi 640 Hz) suena 1 vez, en 1:41 = 51% de la ventana
segunda voz: entra en 1:28, 2:28
la ultima nota termina en 3:10 y quedan 9.5s de cola para la estela
```

Qué mirar:

- **la columna contorno**: ninguno igual al de arriba. La guarda aborta el render si pasa
- **la columna respiro**: valores distintos, no una constante repetida
- **la cola**: que quede aire después de la última nota, más largo que el delay completo
- **grados conjuntos** arriba del 60%, y que los saltos sean chicos. Muy abajo es
  arpegio, no línea
- **el pico una sola vez**, entre el 55 y el 65%
- **el motivo aparece en 3 de las 4 frases**
- **discontinuidad entre muestras** baja: si sube, hay un empalme y va a haber click
- **el nivel adentro de cada hueco**, que tiene que bajar gradual y no de golpe
- después, `qa_scan_spectral.py` sobre el WAV
