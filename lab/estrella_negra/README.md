# Estrella Negra: estructura de Grinderman, armonía de Blackstar

Experimento de lab. **No es una transmisión**: es una muestra de sonido para escuchar
qué pasa cuando se le pone a un tema de rock de un solo acorde la armonía de Bowie.

```bash
python3.10 lab/estrella_negra/render.py     # ~1:45, determinista (semilla 24)
task serve                                   # y abrir /lab/estrella_negra/escuchar.html
```

Salen **ocho stems** en `stems/` más `mezcla_referencia.wav`. Los ocho están
normalizados con el mismo factor, así que sumarlos da la mezcla: la página de escucha
los toca sincronizados con mute y solo por pista.

Tarda casi dos minutos porque **nada se copia**: las 43 vueltas del riff se generan una
por una, nota por nota, y cada nota pasa por la escalera Moog. Ese es exactamente el
costo de que no suene a plástico.

## Los dos préstamos

**La estructura es de "No Pussy Blues" (Grinderman, 2007).** Un riff, un acorde, y el
tema no modula: se carga. Cada vuelta suma una capa y sube el ruido, la armonía no se
mueve nunca, y lo que cambia es la presión. Al final revienta y queda el riff pelado.
Es lo contrario de una canción con puente: no hay a dónde ir, y esa es la idea.

**La armonía es de "Blackstar" (Bowie, 2016).** Sí tiene sintetizadores, y bastante:
pads y bajos de sintetizador debajo de todo, aunque la línea que se recuerda la lleva
un saxo. Lo que se roba acá no es el timbre sino dos decisiones:

1. **Pedal grave fijo.** El bajo no acompaña la melodía: se queda quieto para que todo
   lo de arriba se lea como tensión contra algo que no cede.
2. **Frigio dominante.** Mi fa sol# la si do re: segunda bemol y tercera mayor a la vez.
   El choque entre el fa y el sol# (un semitono y medio) es el color medio-oriental del
   tema. Es exactamente lo que le falta a un riff de rock en mi menor para no sonar a
   rock en mi menor.

Las dos mitades encajan por un motivo concreto: **un tema de un solo acorde necesita que
el movimiento pase por otro lado**. Grinderman lo resuelve con ruido, Bowie con color
armónico. Acá van los dos a la vez.

## La estructura

96 BPM, 84 compases, 3:30. El compás dura 2,5 s y el riff dos compases, o sea 5 s.

| | compases | qué entra |
|---|---|---|
| 0:00 · intro | 8 | el riff solo, sordo, sin batería |
| 0:20 · ciclo 1 | 16 | el pedal grave y el golpe |
| 1:00 · ciclo 2 | 16 | el pad y la voz que hace de saxo. El charles pasa a semicorcheas |
| 1:40 · ciclo 3 | 16 | el ruido empieza a comerse el aire |
| 2:20 · explosión | 12 | el muro. Bombo en las cuatro negras, riff rabioso, dos gritos |
| 2:50 · derrumbe | 12 | se cae todo menos el riff. La batería pierde compases |
| 3:20 · cola | 4 | el último acople |

El tempo **no cambia nunca**. Lo que acelera es la subdivisión: negras, corcheas,
semicorcheas. Es más barato y funciona mejor que subir el BPM.

## Los siete stems

| stem | rol | de dónde sale |
|---|---|---|
| `riff` | el motor, barroso | escalera Moog con drive 34 a 70, dos sierras + sub gordo |
| `bajo` | el pedal de Mi1 (41,2 Hz) | seno + pulso a la octava, un golpe por compás |
| `bateria` | bombo, caja y toms | `aem/instruments.kick` + caja de dos capas propia |
| `pad` | el acorde entero, mareado | cinco sierras con deriva propia, mi sol# si re fa |
| `lead` | el lugar del saxo | `voz_moog` con scoop y vibrato que entra después |
| `ruido` | la capa que crece | crujido de sala + acoples afinados + cortes + muro |
| `grano` | el polvo | `aem/granular.nube` al unísono sobre el propio riff, techo en 900 Hz |

**El riff toca una sola nota en todo el tema**: el mi. La única excepción es un re grave
al final de cada cuarta vuelta, y está para marcar el giro, no para hacer melodía. Ninguna
vuelta es igual a otra igual (nivel, filtro, fase, afinación y tiempo se sortean por nota),
pero la altura no se mueve.

**No hay platillos.** El kit no tiene un solo metal y la mezcla no tiene prácticamente
nada arriba de 6 kHz. Es una decisión, no un olvido.

**El lead toca siete veces en tres minutos y medio.** Entre frase y frase pasan cuatro
compases de riff solo. Un saxo que toca todo el tiempo deja de ser un evento.

## Medición

Por pista, antes de la normalización del mix:

```
              pico    crest    LUFS
  riff        -0.6    17.8    -20.3
  bajo        -4.0    20.8    -27.1
  bateria     -1.7    18.2    -19.6
  pad        -11.4    17.3    -27.3
  lead        -8.8    20.8    -24.8
  ruido      -10.0    19.9    -25.2
  grano       -7.2    24.4    -30.4
```

Y el arco, que es lo único que hay que verificar antes de escuchar:

```
  sección      LUFS    <120 Hz   120-500   0,5-2 kHz   >2 kHz
  intro       -28.1      63%       37%        0,3%      0,0%
  ciclo_1     -23.2      68%       32%        0,3%      0,1%
  ciclo_2     -21.9      62%       34%        3,3%      0,1%
  ciclo_3     -20.2      58%       37%        3,9%      0,2%
  explosion   -16.6      55%       38%        7,1%      0,3%
  derrumbe    -25.7      52%       42%        6,5%      0,1%
  cola        -31.8      61%       38%        0,3%      0,0%
```

**11,5 dB de recorrido** entre la intro y la explosión. Lo que más se mueve no es el
volumen sino la banda: el tema **empieza con el 0,3% de su energía arriba de 500 Hz y
termina la explosión con el 7,4%**. Ese recorrido es el "filtrado al principio y se abre".

Arriba de 2 kHz no hay nada, y arriba de 6 kHz hay literalmente 0,0%. Es lo que se pidió
(barroso, tapado, mugriento) y es el número a revisar si en algún momento parece de más.
`scripts/qa_scan_spectral.py` da OK y ningún stem llega al límite.

## Lo que se ajustó midiendo

**La primera pasada tenía el 85% de la energía debajo de 120 Hz.** Entre el sub del riff
(una cuadrada a 41 Hz) y el pedal del bajo se comían el tema entero, y arriba de 2 kHz no
había nada. La corrección no fue ecualizar: fue bajar el sub del riff de 0,35 a 0,20 y el
nivel del bajo de 0,55 a 0,32. **Un seno a 41 Hz tiene muchísima energía y poca sonoridad**,
así que un nivel que "se escucha bien" solo se está comiendo el headroom de todo lo demás.

## Las tres versiones, y por qué

Vale registrar la secuencia entera porque cada veredicto corrigió el anterior.

**v1.** "Los sonidos son de plástico, cada tecla suena igual que la anterior, el oscilador
no oscila, el hihat suena de fábrica, la melodía es conconcon." La causa no era de timbre,
era estructural: **el riff se generaba una vez y se copiaba 42 veces**, el mismo array de
muestras. Ninguna mezcla arregla eso.

**v2.** Se arregló la variación (cada vuelta generada nota por nota, nivel atado al filtro,
notas fantasma, wow y flutter) pero se corrigió de más para el otro lado: más notas, más
brillo, más definición, platillos metálicos arriba. Veredicto: **"riff y platillos son una
verga, sacalos. El grano es una feria de circo gitana."**

**v3, la actual.** Se conserva toda la máquina de variación de la v2 y se le da vuelta la
dirección:

| queja de la v2 | qué se hizo |
|---|---|
| el riff cambia demasiado de nota | una sola nota, el mi. Un re grave cada cuatro vueltas y nada más |
| falta barro | las notas duran más que el hueco hasta la siguiente: **se pisan**. Eso emborrona, no el ecualizador |
| falta mugre | drive de la escalera de 34 a 70 (satura adentro de las celdas, no es un fuzz) + cinta + una banda de ruido que vive dentro de la envolvente |
| el principio tiene que estar filtrado | corte en 90 Hz + 350 de envolvente en la intro: sobre un mi de 82 Hz pasan cuatro armónicos. Recién en la explosión llega a 1600 |
| los platillos | eliminados, pista y archivo |
| el grano es un circo | la calesita eran **granos cortos y densos transpuestos a la octava y a la docena**. Ahora: unísono, cero transposiciones, granos de 180 a 400 ms, densidad máxima 45 en vez de 220, techo en 900 Hz |

También bajó la resonancia del filtro (0,48 contra 0,74): resonancia es definición, y
definición es lo contrario de barroso.

`aem/instruments.hihat_metalico` queda en el framework aunque este tema no lo use: es un
instrumento válido y no molesta a nadie.

## Qué falta

1. **Escuchar la v3 y decidir si el barro está en el punto** o si se pasó de tapado.
2. **Voz.** No hay, y la estructura la está pidiendo: el modelo es un tema hablado y
   gritado. Si va, va cifrada (`transmissions/01/release/textos.md`), no cantada.
3. **La explosión dura 30 s y es simétrica.** El modelo es más largo y más desprolijo.
4. **Estéreo.** Casi todo centrado; sólo el lead y el grano abren.
5. **El kit sin metal deja un hueco de tiempo**, no de frecuencia: no hay nada que marque
   la subdivisión. Si hace falta, va por el lado de más notas fantasma en la caja, no de
   volver a poner platillos.
