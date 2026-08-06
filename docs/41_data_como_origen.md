# 41 — Data como origen (línea Ikeda)

> Estado: **research + PoC sin ejecutar**. Nada de esto se codeó todavía.
> Bajado por el user el 2026-08-06. La referencia a Ikeda la trajo Helen.
> Entrada de lab: `ikeda-research` en `dashboard/data.json`.

## 1. Qué es la línea

Ryoji Ikeda arma **sonido y visual a partir de data**, del mismo stream y
sincronizados. No es visualizar datos para hacerlos legibles: la data es el
material. Obras de referencia: *test pattern*, *datamatics*, *supercodex*, la
trilogía *data-verse*. Fue residente en el CERN, de donde salió *supersymmetry*.

Dos ejes, y los dos son el centro de la investigación:

1. **Data como material.** Un solo origen alimentando audio y video.
2. **Nicho y mercado.** Cómo se entra a ese circuito, que no es el de streaming.

Ninguno de los dos arranca de cero acá. Ver §2 y §11.

### Lo que ya estaba escrito en el repo

| Dónde | Qué aporta |
|---|---|
| `docs/07_vision.md` | "el foco es la data" como línea del proyecto |
| `docs/27` hilo A ("Silicon") | Veredicto previo: el hueco real es tratar el estado de la máquina como modulación de una voz tocable, no como ruido de datos |
| `docs/video/05` §1.4 | Ikeda ya catalogado como referencia visual de Crossing: "dato como contenido, no como gráfico de barras" |

La investigación une esos tres hilos. No los reabre.

## 2. Dónde estamos parados (veredicto honesto)

**Cerca en herramientas:**

- Componemos desde código (`framework/aem` es Python puro, no un DAW con plugins).
  Ikeda trabaja algorítmicamente también. Es la parte cara y ya está.
- Tratamos audiovisual como unidad: los control tracks `.npz` atan imagen a sonido
  a nivel frame. La mayoría de los músicos terceriza el video y queda pegado por
  arriba.
- Abstracción no figurativa (Crossing no tiene nada representacional).
- Faceless. Su obra tampoco se apoya en una persona al frente.

Crossing es lo más cerca que estuvimos, y no por casualidad: le robamos explícito.

**Lejos en temperamento, que es donde está la distancia real:**

| Nosotros | Él |
|---|---|
| Románticos: cuento, lore, arco emocional, melodía (el motivo *voyager*), reverb como emoción, calidez | Anti romántico: sin narrativa, sin melodía, sin reverb, formalismo y matemática |
| Drones, sub bass, textura, ruido capado a 800 Hz para que suene cálido | Sinusoides, clicks, frecuencias extremas, silencio, dinámica brutal |
| Discos para streaming y YouTube | Piezas para salas y festivales |

**El veredicto.** Tenemos las herramientas de su nicho y no su temperamento. Un
curador mirando *Heliopause* hoy vería un visualizer excelente, no data art.

**Y la posición que sale de ahí (decisión del user, 2026-08-06):** el romanticismo
no es la carencia, es la diferenciación. Ese nicho es uniformemente frío. Meterle
narrativa y melodía es lo que no hay. **No se imita a Ikeda: se toma su método y se
le mete lo nuestro.**

## 3. La topología

Lo que hay hoy es una cadena:

```
audio → análisis → lanes (.npz) → video
```

Lo que queremos es una bifurcación:

```
data → lanes (.npz) → audio
                    ↘ video
```

El audio no pasa al otro lado del video. **Deja de ser el origen y pasa a ser una
salida más**, hermana del video. Aparece un nodo nuevo arriba de todo. La relación
audio→video no se invierte, se disuelve: los dos cuelgan del mismo padre.

> Corrección registrada: en la primera versión esto se describió como "invertir la
> flecha". Está mal. La única flecha que da vuelta es la de audio↔lanes.

### La consecuencia que esa frase tapaba

| Hoy | Destino |
|---|---|
| Las lanes son **descriptivas**: se miden desde un WAV que ya existe | Las lanes son **generativas**: causan el audio |
| La sincronía es gratis por construcción (no pueden no coincidir) | La sincronía hay que producirla |

Por eso "el tooling no se toca" vale solo para la mitad de video, que efectivamente
solo consume lanes. **El lado de audio es laburo nuevo.**

### El schema de las lanes (ya existe, se mantiene)

`transmissions/01/video/control/*.npz`:

| Lane | Qué es |
|---|---|
| `rms`, `rms_sub`, `rms_low`, `rms_air` | energía por banda |
| `centroid` | brillo |
| `flux`, `onset` | cambio y ataque |
| `fps=30`, `sr=44100` | rejilla temporal |

Mantener el schema idéntico es lo que hace que el tooling de video siga andando sin
tocarlo.

### Límite técnico del framework (verificado 2026-08-06)

`framework/aem/synth.py` tiene primitivas con frecuencia **escalar**:

```python
def sine(freq, dur, amp=1.0):
    return amp * np.sin(2 * np.pi * freq * t_arr(dur))
```

Si se le pasa un array numpy no falla, pero suena mal: para modular bien hay que
**integrar la fase** (`cumsum(freq)/SR`), no multiplicar por `t`. Multiplicar da un
chirp, no la modulación pedida.

**Trabajo requerido:** variantes de las primitivas que acepten parámetros a control
rate. Es la primera tarea concreta del PoC.

## 4. La base: señales reales de las Voyager

La NASA publica la telemetría del cruce de la heliopausa. El Plasma Wave Subsystem
es de donde salieron los "sonidos del espacio interestelar"; hay además
magnetómetro y rayos cósmicos, con series largas y públicas.

**Por qué esta data y no otra:** el motivo central del proyecto se llama *voyager*
y el disco se llama *Heliopause*, que es el borde que la sonda cruzó. Serían las
mediciones reales del evento que el disco narra. Ikeda hizo exactamente eso con
data del CERN estando ahí.

Eso además contesta la pregunta que el circuito hace primero: por qué **esta** data.

**Sin verificar:** formato exacto, cadencia, vía de descarga y licencia. Es el paso
0 del PoC, no un dato asumido.

**Respaldo si resulta impracticable:** el estado de la máquina (línea Silicon,
`docs/27` hilo A). Sigue válida, pero es menos específica y no tiene coartada
narrativa.

## 5. Lenguaje: Python, ninguno nuevo

`framework/aem` es Python+numpy, el `.npz` es numpy, la suite de QA es Python,
`paulstretch.py` es Python. Un lenguaje nuevo cuesta toolchain y no compra nada en
esta etapa. Para el video se reusa el spine de shader/Hydra existente, alimentado
por el mismo `.npz`. **Un solo lenguaje en el origen** es parte del punto.

## 6. Técnica de mapeo

El mapeo es el experimento entero. `docs/27` ya lo dice: el hueco son mapeos
musicales, no ruido de datos.

La misma serie se usa de dos formas:

| Uso | Velocidad | Qué produce |
|---|---|---|
| Data como CV | remuestreada a 30 Hz | modula una voz tocable: cutoff, pitch, amplitud |
| Data como onda | a sample rate | la data *es* la muestra (territorio bytebeat/PWS) |

Tres reglas que separan música de sonificación:

1. **Cuantizar a escala** todo lo que tenga altura.
2. **Comprimir el rango dinámico de la serie antes de mapear.** Los datos crudos
   tienen outliers que se traducen en saltos que no son musicales.
3. **Una misma lane maneja un parámetro de audio y uno visual en el mismo frame.**
   Ahí está la firma de sincronía, y es lo que distingue esto de un visualizer.

## 7. El PoC

1. Bajar un tramo de data real y meterlo en un `.npz` con el schema existente.
2. Agregar al framework las primitivas a control rate (§3).
3. Renderizar **60 segundos**: audio desde `aem`, video desde el spine actual, los
   dos leyendo ese `.npz`.
4. Escuchar y mirar.

Alcance cerrado. Nada de disco todavía.

## 8. Prueba de falsación (obligatoria)

Los mismos 60 segundos, una vez con la data real y otra reemplazándola por **ruido
suavizado con la misma estadística**.

Si no se distingue, la data es decoración y el experimento fracasó. Eso se escribe
acá, que es la regla de `docs/`.

## 9. Dónde entra en el disco

**TX03, no TX02.**

TX02 ya tiene sus tres motores asignados (Python deformación / Pure Data / VCV
Rack) y esa asignación es lo que separa los tracks entre sí (`docs/39`). Meter un
cuarto motor rompe justamente eso. Un disco cuyo origen entero es data merece ser
el suyo.

Opción abierta: que la línea de data sea una pata aparte de los discos, con otro
nombre si hace falta. Los discos siguen siendo lo que son.

## 10. Trampas del repo que aplican

Los datos mapeados a ruido o a brillo caen derecho en cicatrices ya documentadas:

- Cutoff de ruido **≤ 800 Hz** (`T_NOISE_FRITURA`, `memory/pattern_noise_fritura.md`).
- **Nunca `abs()` como exciter, va `tanh`**
  (`memory/abs_rectifier_exciter_antipattern.md`).
- `task qa:spectral` después de cada render, antes de reportar.
- Si el mapeo toca el motivo *voyager*: requiere aprobación explícita del user y
  `task qa:voyager` contra el benchmark (`memory/voyager_protegido.md`).

## 11. Eje 2: nicho y mercado (sin resolver)

Circuito distinto al del release en plataformas: museos, bienales, festivales tipo
Ars Electronica / MUTEK / Sónar+D, comisiones, residencias.

**Hipótesis del user:** está menos explorado que el mercado de música.

**A validar con datos, no a asumir:** vías de entrada reales (open calls,
requisitos), si piden trayectoria previa, plata que mueve, y si un artista
**faceless** puede entrar a un circuito que expone y programa personas. Esa última
es pregunta propia nuestra y no la tiene nadie más.

Menos saturado que streaming, probablemente sí. Pero la puerta es curatorial y
suele mirar trayectoria.

## 12. Brief pasado a Helen (2026-08-06)

- Cerca en herramientas: componemos desde código y ya atamos imagen a sonido a
  nivel frame (los visualizers de *Heliopause*).
- Diferencia técnica: lo nuestro es audio → imagen, o sea un visualizer. Lo suyo es
  data → audio + imagen, del mismo origen.
- Diferencia de fondo: somos románticos (cuento, melodía, calidez). Ese nicho es
  todo formalismo frío.
- Ahí está la ventaja: tenemos sus herramientas y no su temperamento. No vamos a
  imitarlo, vamos a meter algo que ahí no hay.
- Próximo paso: PoC de 60 segundos para armar la línea desde la data, como hace él,
  y derivar de ahí el audio y la imagen. Fuente: las señales reales de las Voyager.
