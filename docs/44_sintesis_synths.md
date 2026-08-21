# 44 · Síntesis: cómo armamos synths y qué usamos

> Estado: **en uso**. Módulo en `framework/aem/synths.py`.
> Doc general del proyecto, no de una transmisión. El primer uso concreto es la voz
> del track 1 de TX02 (`transmissions/02/bj3_n_pt/moog.py`), pero esto sirve para cualquiera.

## Qué hay

| Función | Qué es |
|---|---|
| `sierra` `cuadrada` `pulso` | Osciladores band-limited exactos, por suma de armónicos |
| `sync_duro` | Hard sync, resuelto por sobremuestreo a 16x |
| `deriva` | Deriva de afinación tipo oscilador analógico |
| `cluster_microtonal` | El racimo de 0,75 de semitono del score de Dune |
| `ladder_moog` | El filtro escalera del Moog, modelo Huovilainen |
| `adsr` `glide` | Envolventes y portamento |
| `voz_moog` | La voz completa, al modo del Subsequent 25 |

## El filtro escalera

No está hecho de oído. Es el modelo publicado del circuito real.

**Huovilainen (DAFx-04, 2004)** mete la no linealidad **adentro de cada una de las
cuatro celdas de un polo**, que es donde están los transistores. Eso es lo que
distingue una escalera de un pasa-bajos con un pico encima: al saturarla no
distorsiona como un fuzz, se comprime y la resonancia se dobla sola.

**Stilson y Smith (ICMC 1996)** aportan el análisis del lazo: con realimentación
inversora, la ganancia en el corte tiende a infinito cuando `k` tiende a 4.

Las constantes son las de los papers, no elegidas a gusto:

```python
THERMAL = 0.000025                                    # tensión térmica del transistor
fcr = 1.8730*f**3 + 0.4955*f**2 - 0.6490*f + 0.9988   # corrección de afinación
acr = -3.9364*f**2 + 1.8409*f + 0.9968                # corrección de resonancia
tune = (1 - exp(-2*pi*f*fcr)) / THERMAL
res_quad = 4.0 * resonancia * acr
```

### Verificado con medición, no de oído

| Qué | Esperado | Medido |
|---|---|---|
| Pendiente (4 polos) | −24 dB/octava | **−23,2 dB/octava** |
| Pico de resonancia en el corte (res 0,9) | varios dB | **+16 dB** |
| Auto-oscilación | cuando el lazo pasa de 4 | **arriba de resonancia 1,03** |
| PWM en ancho 0,5 | armónicos pares nulos | **0,0000** |
| PWM en ancho 0,15 | 2º armónico presente | **0,73 del fundamental** |

Con `resonancia = 1` el lazo queda justo abajo del umbral, o sea marginalmente
estable. Es correcto: `4 * 1 * acr` da 3,99 y hace falta pasar de 4.

## Qué hace que un Moog suene a Moog

En orden de cuánto aporta:

1. **Cuatro polos con realimentación negativa.** La realimentación es la resonancia.
2. **La no linealidad adentro de cada celda**, no a la salida.
3. **Pérdida de ganancia en la banda pasante al subir resonancia.** No es un defecto:
   al abrir la resonancia el Moog se adelgaza. Compensamos a medias, como el gain
   makeup de los equipos reales.
4. **Envolvente de filtro separada de la de amplitud.** El brillo entra después del
   ataque, no junto.
5. **Deriva de afinación por oscilador.** Es lo que más delata a un digital: dos
   osciladores desafinados con valores fijos mantienen su relación de fase para
   siempre y el oído los funde. Uno analógico deriva y el batido nunca se repite.
6. Sub-oscilador con ancho de pulso modulado, y glide entre notas.

## Sobre los osciladores: por qué acá son mejores que en un plugin

Los generamos por **suma de armónicos hasta Nyquist**. Eso es band-limited exacto:
aliasing cero, no aproximado.

Las técnicas tipo **polyBLEP** existen porque en tiempo real no se puede pagar una
suma de sesenta senos por muestra: son una aproximación **por presupuesto de CPU**,
no por calidad. Nosotros rendimos offline, así que usamos la versión exacta.

Lo mismo con el hard sync: genera un salto de tensión, o sea contenido infinito en
frecuencia. En tiempo real hace falta BLEP; acá se genera a 16x y se decima.

## ¿Python pierde calidad?

**No. El lenguaje afecta la velocidad, no la calidad.**

Una muestra es un número. Con el mismo algoritmo y la misma precisión, el resultado
es bit por bit idéntico salga de C++ o de Python.

- **Precisión**: numpy trabaja en **float64**. La mayoría de los plugins comerciales
  corren en float32 porque necesitan rendir en tiempo real. Estamos arriba, no abajo.
- **numpy y scipy son C y Fortran compilado.** Todo lo vectorizado corre a velocidad
  de C. La excepción es la escalera: tiene realimentación, cada muestra depende de la
  anterior, y ese bucle sí corre en el intérprete. Da **1 millón de muestras por
  segundo**, o sea 5 s para 2 minutos y 29 s para los 11:11. Es tiempo, no calidad.

**El techo real del proyecto no es Python, es `SR = 22050`**: arriba de 11 kHz no
existe nada. Para una línea de bajo casi no importa, pero es un límite duro y mucho
más grave que el lenguaje. Hay una task `production:upgrade` marcada WIP para subir a
44,1 kHz.

### Lo que le falta para ser un producto

Honestamente: **nadie lo calibró de oído contra una unidad real**. El modelo es
correcto y está medido, pero una emulación que convence se ajusta comparando contra
el aparato. No tenemos el aparato.

Tampoco hay polifonía (el Subsequent 25 es monofónico, así que no aplica acá) ni
interfaz.

### Si alguna vez hace falta la emulación comercial

No hay que elegir. Desde Python se pueden **hostear plugins VST/AU** con
[DawDreamer](https://github.com/DBraun/DawDreamer) o
[pedalboard](https://github.com/spotify/pedalboard), y renderizarlos offline. O sea
que se podría correr una emulación paga desde el mismo script y que el pipeline siga
siendo reproducible desde código. Sin evaluar todavía.

## El sonido Dune: qué es realmente

Investigado 2026-08-09. El hallazgo importante: **lo que define ese sonido no es un
efecto.** No es un reverb ni una distorsión que nos falte. Son dos decisiones, una de
afinación y otra de dinámica.

### 1. Racimos microtonales de 0,75 de semitono

Zimmer arma clusters con las voces separadas en incrementos de **tres cuartos de
semitono**. Al no caer en ningún intervalo de la escala temperada, el oído no puede
leerlo como acorde y lo escucha como **textura**. Y como los parciales quedan a pocos
Hz entre sí, aparece un batido lento que es lo que da la amenaza.

Implementado en `cluster_microtonal()`. Verificado: cinco voces reparten 254 cents
medidos sobre 300 teóricos, dentro de la resolución del análisis.

### 2. Las sílabas se despedazan y se golpean una por una

Para el canto Sardaukar: se separa cada sílaba, se estira, se dejan huecos, y después
**se golpea cada una con compresión brutal**. En palabras de Zimmer, un compresor
sobreusado "se siente como golpearte la cabeza contra el marco de la puerta", y eso
es lo que hace que cada sílaba suene peligrosa.

**Esto es directamente aplicable a nuestro coro en protoindoeuropeo** (`docs/42`) y
es lo que hoy no tiene: nuestras voces están estiradas y suavizadas, no despedazadas
y golpeadas.

### Lo demás, que ya teníamos o no aplica

| Elemento | Nosotros |
|---|---|
| Barridos de pasa-bajos con resonancia | Ya, y ahora con escalera de verdad |
| Reverb enorme (el suyo es un Bricasti M7) | `camara()`, convolución con IR sintética |
| Synth principal Zebra2 | No aplica: el nuestro es propio |
| Instrumentos inventados (esculturas de Chas Smith, PVC con duduk) | Nuestro equivalente es deformar grabaciones propias |
| Chelo tocado "como un cuerno de guerra tibetano" | Probado con resonadores y falló: quedó granular |
| Osmose / MPE (Dune 2) | No aplica, no tocamos en vivo |

## Reglas que aplican acá

Las del framework, y no cambian por ser un synth:

- El exciter va con **`tanh`**, nunca con `np.abs()`
  (`memory/abs_rectifier_exciter_antipattern.md`).
- Después de saturar, **LPF** para controlar los armónicos que caen en 1,5-4 kHz
  (`T_VOICE_PAD_HARMONICS`).
- `task qa:spectral` después de cada render, sin excepción.

## Fuentes

- [Huovilainen, "Non-Linear Digital Implementation of the Moog Ladder Filter", DAFx-04, 2004](https://dafx.de/paper-archive/2004/P_061.PDF)
- [Stilson y Smith, "Analyzing the Moog VCF with Considerations for Digital Implementation", ICMC 1996](https://ccrma.stanford.edu/~stilti/papers/moogvcf.pdf)
- [MoogLadders, implementaciones de referencia contrastadas](https://github.com/ddiakopoulos/MoogLadders)
- [Moog VCF en musicdsp.org (variante Stilson/Smith)](https://www.musicdsp.org/en/latest/Filters/24-moog-vcf.html)
- [Sound On Sound, "Dune: Hans Zimmer & Friends"](https://www.soundonsound.com/techniques/dune-hans-zimmer-friends)
- [MusicTech, Zimmer sobre inventar instrumentos para Dune](https://musictech.com/news/music/hans-zimmer-dune-score-invent-instruments-sounds-soundtrack-oscar-2022/)
- [The Conversation, cómo Zimmer construyó el mundo sonoro de Dune](https://theconversation.com/bagpipes-in-space-how-hans-zimmer-created-the-dramatic-sound-world-of-the-new-dune-film-224854)
