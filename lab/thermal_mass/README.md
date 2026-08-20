# Thermal Mass — cuatro capas desde dos electrodomésticos

Experimento de **deformación digital línea Lustmord** (`docs/27` hilo B). Anatomía
de capas y criterios → `docs/38_capas_dark_ambient.md`.

Cuatro capas de 30 segundos, todas sacadas de dos grabaciones de celular hechas en
la misma casa. Cada una es dueña de una banda distinta y están pensadas para sonar
juntas.

```bash
python3.10 lab/thermal_mass/render.py
```

Rinde las cuatro capas más la mezcla. **Determinista**: la semilla está fijada en
24 (el hexagrama del proyecto). Sin semilla cada corrida suena distinto, porque
Paulstretch randomiza la fase.

## Las fuentes

| archivo | qué es | veredicto de `scripts/check_source.py` |
|---|---|---|
| `source/ortiz_de_ocampo.m4a` | 15 s de la **bomba de la losa radiante** del subsuelo | **tono estático.** 92% de la energía en una banda, un solo bin se come la mitad del total. Sirve de cama y tiende a acoplar |
| `source/ortiz_de_ocampo_3.m4a` | 11 s del **lavarropas sarandeándose** | **textura.** Octava más cargada 59%, el nivel varía 10 dB y el timbre 35%. Y tiene **golpes** |

Las dos están a ~70 kbps mono, que es agresivo: el stretch extremo **amplifica los
artefactos del codec**, porque cada cuadro espectral queda sostenido un segundo
entero en vez de pasar en 20 ms. Para la próxima, WAV con la Volt 276, cerca **y**
a distancia.

### Fuentes de lluvia (2026-08-08)

Cuatro clips de lluvia grabados por el user en video 4K, en `~/Downloads/Videos-Aem/`.
El audio sale con `ffmpeg -vn -acodec pcm_s24le -ar 48000`. Son AAC 48 kHz estéreo,
bastante mejores que los m4a de arriba, aunque siguen siendo codec con pérdida.

**Cierran el agujero que tenía el track**: la mezcla de 2 minutos (`mix_v2_arco.wav`)
mide **0.0% de energía arriba de 1.5 kHz** y se termina en 1237 Hz. O sea que las
capas 4 (grano) y 5 (aire) de `docs/38` no existían.

| archivo | dur | reparto | movimiento | transitorios | techo | altura | capa |
|---|---|---|---|---|---|---|---|
| `IMG_4739` | 9,7 s | **26% grano + 28% aire** | no | no | 19,2 kHz | C#2 +25 | **4 · grano, 5 · aire** |
| `IMG_4740` | 10,3 s | 57% en 60-120 | sí (4,9 dB) | **sí, 15 saltos >9 dB** | 8,8 kHz | G2 +28 | **6 · eventos** |
| `IMG_4741` | 3,4 s | 46% en 60-120 | sí (6,2 dB) | no | 10,2 kHz | D#2 −3 | 1 · cama (redundante) |
| `IMG_4742` | 7,8 s | 40% en 60-120 | sí (3,5 dB) | no | 18,8 kHz | G#2 −22 | 1 · cama (redundante) |

**Las dos que sirven son 4739 y 4740, y son complementarias:**

- **4739 es la única con agudo real.** Tiene el 53,5% de su energía arriba de 1.5 kHz
  y llega limpia hasta 19 kHz. Es el complemento exacto de la mezcla actual. Va
  filtrada en pasa-altos: su grave está a 70,3 Hz y la base está a 71,3 Hz, o sea a
  **25 cents**, que batiría feo. Filtrarla no es gusto, es evitar el choque.
- **4740 es la única con transitorios**, 15 saltos de más de 9 dB. Es la capa 6, la
  de eventos. Su grave no se usa: la base ya tiene 52% en 60-120 Hz.
- 4741 y 4742 duplican lo que la mezcla ya tiene de sobra. Quedan de reserva.

> **Ojo con la capa de grano.** 1.5-6 kHz es la banda exacta que marca
> `task qa:spectral` como fritura. La regla del proyecto (`memory/pattern_noise_fritura.md`)
> es no pasar de ~800 Hz **en ruido sintetizado**, porque no tiene estructura. La
> lluvia real sí la tiene, y `docs/38` define la capa 4 justamente ahí. Pero el
> margen es fino: correr `qa:spectral` sobre la mezcla nueva antes de dar nada por
> bueno.

## Las cuatro capas

| capa | rol (docs/38) | banda propia | LUFS | crest |
|---|---|---|---|---|
| **thermal_mass** | 1 · cama | 64% en 60-120 Hz | −20,9 | 12,8 dB |
| **manifold** | 2 · cuerpo | 74% en 120-250 Hz | −20,9 | 14,0 dB |
| **cloud_chamber** | 3 · nube | 45% en 250-500, 39% en 500-1k | −20,9 | 15,1 dB |
| **flywheel** | 6 · eventos | ancha, con picos | −24,2 | **19,4 dB** |
| `mix_v1` | las cuatro juntas | continua de 20 Hz a 1,5 kHz | −19,1 | 14,3 dB |

Las tres primeras están igualadas por **sonoridad (LUFS), no por pico**: con el
mismo pico, Cloud Chamber sonaría bastante más fuerte, porque el oído es mucho más
sensible en 250-1000 Hz que en 60. Flywheel va más abajo a propósito: es la capa
que asoma, no la que sostiene.

Y fijate el **crest factor**: 13-15 dB en las capas de fondo contra **19,4** en
Flywheel. Esa es la diferencia numérica entre algo que acompaña y algo que pisa.

### Los nombres

- **Thermal Mass** — la masa térmica es la capacidad de un material de acumular
  calor y soltarlo despacio. Es literalmente lo que hace una losa radiante y lo
  que hace el sonido.
- **Manifold** — el colector donde converge cada circuito de la losa. Y
  "manifold" también significa múltiple, y en matemática es un espacio.
- **Cloud Chamber** — la cámara de niebla, el detector donde se ven las
  partículas invisibles al pasar.
- **Flywheel** — el volante de inercia: la pieza pesada que acumula energía
  rotacional y hace que una máquina grande se mueva lento y no se pueda frenar.
  Misma familia conceptual que Thermal Mass, con energía en vez de calor.

## El algoritmo de base: Paulstretch

En `scripts/paulstretch.py`. Toma cada ventana FFT, se queda con la **magnitud** y
le **randomiza la fase**. El espectro se sostiene, el tiempo se disuelve. Por eso
no suena metálico como un stretch clásico, que repite granos.

Dos parámetros mandan:

- **stretch** — cuánto estira. 15 s × 45 son 11 minutos, antes de bajar el pitch.
- **window** — el tamaño de la ventana FFT en segundos. **Define el carácter.**
  Chica (0,1-0,5) deja el grano y algo del ritmo; grande (2-5) lo funde en un pad
  sin ataque. No hay valor correcto, son dos sonidos distintos.

De ahí sale el reparto: Thermal Mass usa window **5,0** (máximo fundido), Manifold
**2,0** y Cloud Chamber **1,5** (más detalle).

**Y en Flywheel no se usa.** Randomizar la fase destruye el transitorio, y ahí el
transitorio es todo.

## Cadena · thermal_mass (la cama)

| # | Paso | Valores | Por qué |
|---|---|---|---|
| 1 | Paulstretch, dos pasadas | stretch 45, window 5,0 | Dos corridas dan el **mismo espectro con fase distinta** = estéreo real. La única forma honesta de ensanchar un mono |
| 2 | Bajar 2 octavas | por velocidad | Como una cinta lenta: pitchea **y** alarga |
| 3 | Recorte de 30 s | del medio | El arranque de un stretch siempre es lo más pobre |
| 4 | **Notch en 71,3 Hz** | Q 6, paralelo 75% (≈ −9 dB) | La frecuencia del acople, **medida**. Quirúrgico |
| 5 | Barrido lento | LP 220 ↔ 380 Hz cada 17 s | Un tono quieto suena a acople aunque esté bien ecualizado |
| 6 | Respiración | 14% cada 13 s | Idem, en amplitud |
| 7 | Cámara | IR 14 s a 800 Hz, 65% wet | **Una IR distinta por canal**: las colas tampoco están correlacionadas |
| 8 | DC + high-pass | 28 Hz | Saca el subsónico que se come headroom |
| 9 | **Mono debajo de 120 Hz** | fase cero | Sub decorrelado se cancela al sumar a mono |
| 10 | Pico | −9 dBFS | **Cero saturación.** Lo pastoso sale del window largo y del movimiento, no de apretar |

## Cadena · manifold (el cuerpo)

| # | Paso | Valores | Por qué |
|---|---|---|---|
| 1 | High-pass de limpieza | 30 Hz | El lavarropas trae 1,5% de rumble de manejo |
| 2 | Paulstretch, dos pasadas | stretch 45, window 2,0 | |
| 3 | **Subir 14,14 semitonos** | | Su fundamental cruda está en 63 Hz (B1 +35 cents) y el bed en 71,3: son **214 cents**, casi un tono entero. En la zona grave eso es barro y batido. Subirla la deja **una octava exacta arriba del bed**, consonante, y su contenido aterriza en la banda de cuerpo |
| 4 | High-pass | 120 Hz | Le deja el sótano al bed |
| 5 | Barrido | LP 600 ↔ 1200 Hz cada 19 s | |
| 6 | Respiración | 12% cada 11 s | |
| 7 | Cámara | IR 12 s a 1000 Hz, 55% wet | |
| 8 | Igualar sonoridad | al LUFS del bed | |

## Cadena · cloud_chamber (la nube)

| # | Paso | Valores | Por qué |
|---|---|---|---|
| 1 | Paulstretch, dos pasadas | stretch 45, window 1,5 | Ventana chica: queda detalle |
| 2 | **Nube de 5 copias** | 0, +7, +12, +19, +24 semitonos | Un tono no se vuelve textura con filtros: se vuelve apilando transposiciones. Reparte la energía |
| 3 | Desafinación | +4, −5, +6, −7 cents | Sin esto es un acorde. Con esto tiembla |
| 4 | Desfase | 0 a 10 s | Si todas se mueven al unísono suena a acorde. Desfasadas suena a nube |
| 5 | High-pass | 200 Hz | Deja el sótano libre |
| 6 | **De-resonancia** | los 3 picos, Q 9, paralelo 55% | Las transposiciones generan sus propias resonancias |
| 7 | Barrido | LP 2200 ↔ 5000 Hz cada 23 s | Abre y cierra el techo |
| 8 | Tilt | 70% directo + 30% LP 4000 | Se sienta detrás en vez de competir |
| 9 | Cámara | IR 10 s a 1500 Hz, 55% wet | Más corta y más brillante que la de abajo |

## Cadena · flywheel (los eventos)

La más distinta de las cuatro, y la única con transitorios.

| # | Paso | Valores | Por qué |
|---|---|---|---|
| 1 | **HPSS por filtro de mediana** | ventanas de 31 | Mediana en **tiempo** aísla lo estacionario (motor, ruido); mediana en **frecuencia** aísla lo percusivo. Nos quedamos con el 18% que golpea y tiramos el 82% que zumba. **Esta es la limpieza** |
| 2 | Enlentecer ×4 | por velocidad | 24 semitonos abajo, y el ataque **queda intacto**. Nada de Paulstretch acá |
| 3 | Aislar cada golpe | picos 8 dB sobre el piso local | |
| 4 | **Re-espaciar** | cada 5,5 a 7,5 s, irregular | Separa el **ritmo** del **tono**. Enlentecer más hundiría los golpes abajo de 60 Hz y les sacaría definición; re-espaciar los separa dejando cada uno con su altura |
| 5 | Nivel por golpe | 70-100% aleatorio | Maquinaria pesada no es un metrónomo |
| 6 | **Expansor descendente** | umbral −26 dB, ratio 2 | Lo contrario de un compresor: hunde lo que está bajo. Limpia el ruido residual **entre** golpes sin tocar el ataque |
| 7 | Decaimiento por golpe | exp, τ 1,6 s, primeros 20 ms intactos | La cola muere de verdad en vez de dejar el piso levantado |
| 8 | **Transient shaper** | envolvente 40 ms vs 900 ms, ^0,8 | Realza el ataque respecto de su propia cola. Es lo que hace que el golpe sobresalga de su reverb |
| 9 | Saturación | tanh ×2,0 | Basto. Acá sí, es un golpe |
| 10 | **Cámara con pre-delay** | IR 32 s a 700 Hz, pre 300 ms | El pre-delay es **la señal de tamaño más fuerte que tiene el oído**. El golpe se escucha limpio antes de que aparezca el cuarto |
| 11 | **Cola del abismo** | la cámara una octava abajo, LP 250, 600 ms más atrás | El abismo está para abajo |
| 12 | **Ducking de las colas** | 75%, release 1,2 s | Las dos colas se apartan mientras pega el golpe y crecen después. Es lo que permite una cámara enorme sin que se coma el ataque |
| 13 | Mezcla interna | 0,85 seco + 0,80 cámara + 0,45 abismo | El seco adelante |

Resultado medido: **5 golpes en 30 s**, cada uno ~12 dB sobre el piso local, con
**19,4 dB de crest** y ~20 dB de rango entre pico y silencio.

## Verificación (lo que hay que medir siempre)

```
                    LUFS   pico  truePk  crest   corr   20-60 60-120 120-250 250-500 500-1k 1k-3k
  thermal_mass     -20.9   -9.0    -9.0   12.8  +0.70   14.9  64.3   17.4    3.2   0.0   0.0
  manifold         -20.9   -9.2    -9.2   14.0  +0.03    0.0   0.4   73.9    6.7  16.2   2.8
  cloud_chamber    -20.9   -8.5    -8.5   15.1  -0.02    0.0   0.0    2.7   45.2  39.1  12.9
  flywheel         -24.2   -6.0    -6.0   19.4  +0.08   20.9  42.2   31.7    4.7   0.4   0.0
  mix_v1           -19.1   -6.0    -6.0   14.3  +0.42   13.7  50.6   25.5    5.6   3.6   0.9
```

- **true peak = pico** en todas: no hay picos entre muestras, no clipea al convertir.
- **crest de 13-15 dB** en las camas: sin comprimir. **19,4 en Flywheel**: pega.
- **corr +0,70 en el bed** (graves centrados) y **≈0 en el resto** (ancho).
- **Bandas complementarias**: cada capa domina una y la mezcla cubre 20 Hz a 1,5 kHz
  de forma continua, con la fundamental en 71,3 Hz.

## La mezcla con arco

```bash
python3.10 lab/thermal_mass/mix.py     # -> mix_v2_arco.wav, 2 minutos
```

Sumar las cuatro capas a nivel fijo suena a paisaje, no a pieza: todo empieza y
termina junto y en el medio no pasa nada. `mix.py` le da a cada capa su propia
automatización de nivel, y el orden de entrada sigue el criterio de `docs/38` — la
cama define la nota, los **eventos** definen la estructura temporal, el relleno se
acomoda alrededor.

```
0:00  la cama sola, apareciendo del silencio
0:20  entra el cuerpo, muy abajo
0:28  primer golpe: la máquina se despierta
0:45  entra la nube
1:00  las cuatro juntas, peso máximo
1:25  se retiran nube y cuerpo
1:40  último golpe, queda la cama con la cola
2:00  silencio
```

La automatización es una tabla de puntos `(segundo, dB)` editable a mano:

```python
"flywheel": [(0, -80), (26, -80), (28, 3), (100, 3), (105, -5), (112, -80)],
```

Resultado: **de −36 LUFS en el arranque a −20,7 en el clímax y −28 al final.** Son
15 dB de recorrido, y el espectro también se mueve (el contenido arriba de 250 Hz
va del 1,5% al 11%). Los golpes **asoman 7,5 dB sobre la mezcla** en promedio, con
cero muestras al límite.

En el bus **no hay compresión ni limitador**: solo high-pass en 26 Hz y graves
centrados abajo de 110.

### Dos cosas que se ajustaron escuchando

**El 0:40 se apelotonaba.** La cama subía a 0 dB en el segundo 32, justo cuando
entraba el cuerpo, y las dos crecían encima. Ahora la cama se queda en −2 hasta
pasado el minuto y el cuerpo entra en −14 subiendo en tres tramos. El salto entre
tramos bajó de 3,3 a 2,6 dB.

**Los golpes quedaban atrás.** Estaban en −2 y pasaron a +3. Hay margen porque
Flywheel es la capa más baja en LUFS (−27 contra −21 de las camas), así que subirla
no compromete headroom.

## Duración objetivo

**8 minutos** (rango 7 a 9), si esto va como single.

La duración **no cambia la plata**: un stream cuenta a los 30 segundos y un tema de
20 minutos paga lo mismo por play que uno de 3. Así que la decisión es artística y
de playlists.

- **Género**: en dark ambient los temas viven entre 6 y 15 minutos. Tres minutos
  lee como boceto, la escala temporal es parte del lenguaje.
- **Playlists**: arriba de 10 minutos casi ningún curador toma, salvo sleep y focus.
- **Catálogo propio**: Outbound dura exactamente 8:00. Misma escala arma
  continuidad. (Y los tres de Heliopause suman 24, el hexagrama, si se quiere
  seguir el hilo numérico.)

A 8 minutos el arco da para **90 s de apertura**, **4-5 min de cuerpo** con golpes
cada 8-12 s, y **2 min de disolución**. Los 2 minutos actuales son esa maqueta a
escala 1:4.

Y algo sobre singles en este género: lo que hace que un tema se recuerde no es la
duración sino que **pase algo una vez**. Acá ese algo es el primer golpe.

## Lo que salió mal en el camino

Vale más que el resultado, porque es lo que no hay que repetir.

**Perseguir el acople bajando el pitch fue al revés.** Con dos octavas abajo y un
low-pass en 220 Hz, la fuente queda convertida en un seno de 71 Hz, y un tono
sostenido y solo en esa zona **es** un acople. La reacción intuitiva —subir el
espectro, sacar graves— destruye justo lo que se buscaba. Lo correcto: **medir la
frecuencia culpable, agujerearla, y agregar movimiento.**

**El montaje por secciones** (varios windows cruzados en una misma pieza) sonó
peor: las secciones de window chico son mucho más granulosas y la normalización por
sección mete bombeo en los cruces. Descartado.

**`señal − lowpass` no es un complemento** si el lowpass es un IIR causal: sale
desfasado y la resta deja residuo decorrelacionado justo en los graves. La
correlación bajo 120 Hz daba −0,08 en vez de +1. Se arregla con **fase cero**
(`sosfiltfilt`).

**El orden importa**: saturar decorrelaciona, así que el mono de graves va
**después** del drive. Con el orden invertido la correlación empeoraba de −0,08 a
−0,28.

**El mega reverb se comía los golpes.** Con la cola al 55% y sin pre-delay, los
impactos pasaron de 12 dB sobre el piso a **cero detectables**: la cola rellenaba
los huecos y subía el piso local. Se arregla con pre-delay, ducking y transient
shaper, no bajando el reverb.

**El fade de entrada rampeaba el primer ataque.** El primer golpe caía en el
segundo 1,0 y el fade duraba 1,5. Ahora el primer golpe entra en el segundo 3 y el
fade dura 0,8.

**Las colas se apilaban en la segunda mitad.** Golpes cada 6 s con una cola de 32 s
son **cinco colas sonando a la vez**. No acoplaba, pero se juntaba. Se bajó la
cámara a 16 s, el abismo de 0,45 a 0,28 y el release del ducking de 1,2 a 0,8: se
encima 2,5 veces en vez de 5, y el crest de Flywheel **subió** de 19,4 a 22,7 dB.
Menos reverb, más golpe.

**Un error de lectura mío que vale registrar**: encontré una periodicidad de 0,36 s
en el lavarropas y la interpreté como dos motores batiendo entre sí. Era el tambor.
Tenía el dato correcto y le puse la explicación equivocada, y eso me llevó a
tratar la grabación como drone de fondo cuando era la capa de eventos.

**La IR del reverb es ruido**, así que le aplica la regla de fritura del proyecto
(`memory/pattern_noise_fritura.md`): filtrada a 700-1500 Hz según la capa. Con
estas fuentes no se nota porque no tienen contenido ahí arriba, pero con una fuente
de banda ancha una IR sin filtrar da estática, no espacio.

## Cómo replicarlo en Ableton

| Paso del script | En Ableton Live |
|---|---|
| Paulstretch | Warp del clip en modo **Texture**: **Grain Size** es el window y **Flux** la randomización. El botón **÷2** del "Orig. BPM" duplica el largo cada vez: 5 veces son ×32. O el plugin **PaulXStretch** (VST3/AU, gratis) dentro de Live |
| Bajar octavas por velocidad | Transposición del clip con Warp **apagado**, así también alarga |
| HPSS (separar golpe de zumbido) | No hay nativo. Lo más cercano: duplicar la pista, en una un **Gate** agresivo con look-ahead (queda el golpe) y en la otra la invertida (queda el zumbido). Sirve, pero es más sucio que la mediana |
| Notch quirúrgico | **EQ Eight**, banda en modo notch, Q alto |
| Expansor descendente | **Gate** con Floor alto y release largo |
| Transient shaper | No hay nativo en Lite. Con **Compressor** en modo Peak, ataque rápido y ratio bajo en paralelo se aproxima |
| Barrido lento | **Auto Filter** con LFO de período largo, o automatización dibujada |
| Respiración | Automatización de volumen |
| Cámara + pre-delay | **Hybrid Reverb** (tiene pre-delay y IRs) o **Valhalla Supermassive** en un return |
| Cola del abismo | Un segundo return con el mismo reverb, pitcheado −12 y filtrado bajo |
| Ducking de la cola | En el return del reverb, un **Compressor** en modo sidechain escuchando la pista seca |
| Mono debajo de 120 Hz | **Utility** con "Bass Mono" en 120 |
| Igualar por LUFS | El medidor de Live |

El estéreo por dos pasadas **no** se replica con un widener: hay que correr el
stretch dos veces y poner una en cada canal.

## Estado y qué falta

Cuatro capas de las seis de `docs/38`. Falta:

1. **Capa 4 · grano** (1-6 kHz) — la que da escala. Fuentes: hielo, papel, hojas
   secas, grava, una cremallera, madera crujiendo.
2. **Capa 5 · aire** (6 kHz+) — el cuarto en silencio a ganancia alta. **Hay que
   grabarlo, no ecualizarlo**: un shelf de aire sobre material que no tiene
   contenido arriba agrega ruido, no aire.
3. **El arco.** Son 30 segundos en loop, no una pieza. Falta que algo pase a lo
   largo de varios minutos.
4. **Volver a grabar las fuentes en WAV.** Es lo que más va a cambiar el resultado.
5. **Melodía**, si va: el material está en el cuarto de tono entre C#2 y D2, o sea
   50 cents abajo de D. Reglas en `docs/38`.

Referentes de la misma familia para robar técnica, en `docs/27`: Lustmord, Thomas
Köner, Deathprod, Ben Frost, Roly Porter, The Caretaker.
