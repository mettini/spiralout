# 46 · Microsonido

Referencia de trabajo. Qué es el microsonido, por qué es una escala de TIEMPO y no de
altura, y qué se puede hacer con él en este repo.

Primo directo de lo que ya se usa en [`transmissions/02/bj3_n_pt/`](../transmissions/02/bj3_n_pt/README.md)
(Paulstretch) y de la línea de datos como origen de
[`41_data_como_origen.md`](41_data_como_origen.md).

---

## La idea en una línea

**Microsonido es todo lo que pasa entre 1 y 100 milisegundos: más largo que una muestra,
más corto que una nota.**

Es una franja que la música clásica y el rock nunca tocaron, porque no tenían cómo. La
partitura empieza en la nota. El microsonido empieza abajo de la nota, y ahí el material
no tiene altura ni ritmo todavía: tiene *grano*.

## Aclaración, porque se confunde

**Micro es tiempo, no afinación.** El `cluster_microtonal` del framework
(`aem/synths.py`, [doc 44](44_sintesis_synths.md)) es MICROTONAL: divide el semitono.
El microsonido divide el segundo. No tienen nada que ver más allá del prefijo.

## Las escalas de tiempo

Curtis Roads las ordenó así en *Microsound* (MIT Press, 2001), que es el libro que le
puso nombre al asunto:

| escala | duración | qué es |
|---|---|---|
| macro | minutos | la forma del tema, la estructura |
| meso | segundos | la frase, la sección |
| objeto sonoro | 100 ms a segundos | **la nota**. Donde vive toda la música escrita |
| **micro** | **1 a 100 ms** | **el grano. Acá** |
| muestra | 22 µs | un número del WAV |

## Por qué 100 ms y por qué 20

Los dos límites de la franja no son arbitrarios, son perceptuales:

- **Arriba de ~50 a 100 ms** el oído reconoce el sonido como un evento con altura y
  timbre. Es una nota.
- **Abajo de ~20 ms** deja de haber altura y queda un click de banda ancha.
- **En el medio**, el material es ambiguo: se escucha algo, pero no se puede decir qué
  nota es. Ahí está todo el juego.

Y el límite que ordena todo lo demás: **una repetición se vuelve tono a los 20 Hz**. Un
golpe cada segundo es ritmo. Cada 100 ms, ritmo rápido. Cada 20 ms, el oído deja de
contar y empieza a escuchar una nota grave de 50 Hz. **Es el mismo evento, y lo único
que cambió es la velocidad.** El microsonido trabaja justo sobre esa frontera: acelerar
un ritmo hasta que se vuelva timbre es una operación que solo existe en esta escala.

## El grano

La unidad. Un grano es un pedacito de sonido de 1 a 100 ms **con una envolvente**, casi
siempre una campana suave. La envolvente no es un detalle: sin ella, cortar en el medio
de una onda produce un click en cada punta, y una nube de granos sin envolvente es
fritura garantizada.

Historia corta, porque explica el vocabulario:

- **Dennis Gabor (1947)**, físico, propuso que todo sonido se puede describir como una
  suma de "cuantos acústicos": un grano corto con envolvente y una frecuencia. Es la
  transformada de Gabor, prima de la FFT con ventana.
- **Iannis Xenakis (1959)** lo pasó a música en *Analogique A et B*, componiendo con
  nubes de granos y decidiendo su distribución con estadística en vez de con notas.
- **Curtis Roads (1974 en adelante)** lo implementó digital y después escribió el libro.
- La escena que se llamó a sí misma *microsound* es de fines de los 90: los sellos
  **12k** y **LINE**, la lista de correo del mismo nombre, y gente como **Ryoji Ikeda**,
  **Alva Noto**, **Oval**, **Fennesz**, **Mika Vainio / Pan Sonic**, **Taylor Deupree**,
  **Richard Chartier**. Autechre y Tim Hecker desde otro lado.

## Qué se hace con granos

### Síntesis granular

Se generan granos sintéticos (un seno con envolvente) y se tiran a una nube. Los
parámetros que mandan, en orden de importancia:

1. **Densidad**: granos por segundo. Abajo de 20 se escuchan sueltos, como gotas. Arriba
   de 100 se funden en textura continua. Cruzar ese umbral EN VIVO es el gesto más fuerte
   que tiene la técnica.
2. **Duración del grano**: corto es brillante y percusivo, largo es tonal.
3. **Dispersión**: cuánto varía al azar la altura, la posición y el paneo de cada grano.
4. **Forma de la envolvente**: gaussiana suave o con ataque, cambia todo el carácter.

### Granulación (lo que más sirve acá)

En vez de generar los granos, se **recortan de una grabación**. Se lee la fuente con una
cabeza que avanza más lento que el tiempo real y se van tirando granos superpuestos: el
sonido se estira **sin cambiar de altura**, o cambia de altura sin cambiar de largo.
Separar tiempo de altura es lo que ningún reproductor a velocidad variable puede hacer.

**Esto ya está en el repo, en su versión FFT.** `scripts/paulstretch.py` es el pariente
espectral: en vez de granos en el tiempo, congela la magnitud de cada ventana FFT y
randomiza la fase. La diferencia práctica es el artefacto: la granulación clásica deja
un ritmo audible si los granos caen periódicos (por eso se dispersan), y Paulstretch no
lo deja nunca porque no repite granos, pero a cambio borra todo transitorio. Por eso en
`thermal_mass` las camas van con Paulstretch y **flywheel no lo usa**: ahí el transitorio
era todo.

### Las variantes con nombre

- **Pulsar**: cada grano es un pulso con dos frecuencias independientes, la del tren
  (ritmo) y la del contenido (formante). Vale la pena porque una sola perilla te lleva de
  ritmo a tono.
- **Glisson**: cada grano tiene su propio glissando adentro.
- **Trainlet**: trenes de impulsos, sonido metálico y filoso.
- **Formante / FOF**: granos afinados en formantes, la técnica con la que se sintetiza
  voz cantada (CHANT, IRCAM).

## El antipatrón, y es el mismo de siempre

**Una nube de granos con todo randomizado suena a estática.** Es literalmente ruido: si
la altura, la posición y la duración de cada grano son independientes entre sí, el
resultado tiene el espectro de un ruido y ninguna estructura, o sea la fritura de
[`memory/pattern_noise_fritura.md`](../memory/pattern_noise_fritura.md) por otra puerta.

Lo que la vuelve música es la **correlación**: hay que dejar algo quieto mientras el resto
se dispersa. Una altura fija con posición dispersa. O una posición fija con las alturas
en una escala. O la densidad subiendo despacio mientras todo lo demás queda igual. La
regla práctica: **un solo parámetro al azar por vez.**

Y el otro clásico: granos periódicos a densidad media meten un zumbido en la frecuencia
de repetición (100 granos por segundo = un tono de 100 Hz que nadie pidió). Se arregla
dispersando la posición unos pocos milisegundos, no bajando la densidad.

## Qué hay hoy en el framework

- **`aem/granular.nube(fuente, dur, densidad, grano_ms, posicion, avance, dispersion_ms,
  alturas, ...)`**: el granulador. Escrito el 2026-08-15, primera vez usado en
  [`lab/estrella_negra/grano.py`](../lab/estrella_negra/grano.py), donde granula el riff
  del propio tema. `densidad` y `grano_ms` aceptan una curva `[(segundo, valor), ...]`,
  que es lo que permite el gesto de cruzar el umbral de fusión mientras suena.
- `scripts/paulstretch.py`: la versión espectral, probada y en uso en `thermal_mass`.
- `aem/instruments.granular_pulse`: un grano suelto, no un granulador.
- `aem/instruments.vinyl_crackle`: eventos micro por densidad, sin control de altura.

Con el granulador, las grabaciones que ya hay (lluvia, lavarropas, losa radiante) se
vuelven material infinito, y es el camino más corto que tiene el proyecto hacia la línea
Ikeda de [`41_data_como_origen.md`](41_data_como_origen.md).

**Lo que todavía falta**: pulsar y glisson (los granos con tren y formante propios), y
granulación con la posición de lectura manejada por una envolvente dibujada en vez de por
`avance` constante.

## Para escuchar, en orden de utilidad

1. **Ryoji Ikeda, *dataplex*** o *test pattern*: el extremo clínico, granos como datos.
2. **Fennesz, *Endless Summer***: granulación sobre guitarra. Demuestra que el grano no
   está peleado con la melodía.
3. **Alva Noto + Ryuichi Sakamoto, *Vrioon***: piano entero contra micro-eventos.
4. **Curtis Roads, *Point Line Cloud***: el libro hecho disco, casi didáctico.
5. **Autechre, *Confield***: microsonido usado como ritmo y no como textura.
