"""Granulacion: cortar sonido en granos de 1 a 100 ms y volver a armarlo.

Es la escala de tiempo que esta abajo de la nota y arriba de la muestra. Toda la
teoria y el vocabulario estan en `docs/46_microsonido.md`; aca esta la maquina.

QUE HACE UN GRANULADOR Y QUE NO

Toma una fuente, le recorta pedacitos cortos, les pone una envolvente y los tira a
una nube. Como cada grano se lee de una posicion que uno elige, el TIEMPO y la
ALTURA quedan separados: se puede congelar un sonido en un punto sin bajarlo de
tono, o transponerlo sin alargarlo. Ningun reproductor a velocidad variable puede
hacer eso, y es la unica razon seria para usar esta tecnica.

No es un reverb ni un chorus. Si lo que se busca es cola, va reverb: sale mas
barato y suena mejor.

LOS CUATRO PARAMETROS, EN ORDEN DE IMPORTANCIA

1. `densidad` (granos por segundo). Abajo de 20 se escuchan sueltos, como gotas.
   Arriba de 100 se funden en textura continua. Cruzar ese umbral MIENTRAS SUENA
   es el gesto mas fuerte que tiene la tecnica, y por eso `densidad` acepta una
   curva y no solo un numero.
2. `grano_ms`. Corto (10-30) es percusivo y brillante; largo (80-200) es tonal y
   se parece a un pad. En el medio esta la zona ambigua, que es la interesante.
3. `dispersion_ms`. Cuanto se dispersa al azar la posicion de lectura. Sin
   dispersion los granos caen periodicos y aparece un zumbido en la frecuencia de
   repeticion (100 granos por segundo = un tono de 100 Hz que nadie pidio). Se
   arregla dispersando, no bajando la densidad.
4. `alturas`. Las transposiciones entre las que se sortea cada grano. Con (1.0,)
   la nube conserva la afinacion de la fuente; con (1.0, 2.0) se le suma una
   octava arriba sin cambiar el tempo.

EL ANTIPATRON

Randomizar todo a la vez da ruido: si altura, posicion y duracion de cada grano
son independientes, el resultado tiene espectro de ruido y ninguna estructura, o
sea la fritura de `memory/pattern_noise_fritura.md` por otra puerta. Lo que la
vuelve musica es la correlacion: dejar algo quieto mientras el resto se dispersa.
Un solo parametro al azar por vez.
"""
import numpy as np

from .core import SR


def _curva(valor, t_s, dur):
    """Un parametro puede ser un numero fijo o una curva [(segundo, valor), ...].

    Es el mismo idioma que `effects.amp_envelope`: se escribe en puntos y se
    interpola. Sirve para que la densidad crezca a lo largo de una seccion, que es
    donde la tecnica se escucha de verdad.
    """
    if np.isscalar(valor):
        return float(valor)
    puntos = list(valor)
    tiempos = [p[0] for p in puntos]
    valores = [p[1] for p in puntos]
    return float(np.interp(t_s, tiempos, valores))


def _ventana(n):
    """Hann. La envolvente NO es un detalle: cortar en el medio de una onda deja un
    click en cada punta, y una nube de granos sin envolvente es fritura garantizada."""
    return np.hanning(max(n, 2))


def nube(fuente, dur, densidad=40.0, grano_ms=60.0, var_grano=0.35,
         posicion=0.0, avance=0.0, dispersion_ms=30.0,
         alturas=(1.0,), dispersion_cents=0.0, semilla=24, sr=SR):
    """Una nube de granos leidos de `fuente`.

    Args:
        fuente:      senal mono de la que se recortan los granos. Si la lectura se
                     pasa del final, se envuelve (la fuente se lee en loop)
        dur:         duracion de la nube, en segundos
        densidad:    granos por segundo. Numero o curva [(seg, valor), ...]
        grano_ms:    duracion media del grano. Numero o curva
        var_grano:   cuanto varia esa duracion, 0 a 1
        posicion:    desde que segundo de la fuente se empieza a leer
        avance:      velocidad de lectura. 0 congela el sonido en `posicion`,
                     1 lo lee a tiempo real, 0,1 lo estira diez veces
        dispersion_ms: dispersion al azar de la posicion de lectura
        alturas:     transposiciones entre las que se sortea cada grano
        dispersion_cents: desafinacion al azar por grano, encima de `alturas`
        semilla:     fija el azar. Sin esto no hay dos corridas iguales

    Devuelve un mono de `dur` segundos normalizado a +-1.
    """
    rng = np.random.RandomState(semilla)
    fuente = np.asarray(fuente, dtype=np.float64)
    if len(fuente) < 4:
        return np.zeros(int(dur * sr))

    n = int(dur * sr)
    salida = np.zeros(n + int(0.5 * sr))       # cola: el ultimo grano entra entero
    largo_fuente = len(fuente)
    indice_fuente = np.arange(largo_fuente)

    t = 0.0
    while t < dur:
        d = max(_curva(densidad, t, dur), 0.5)
        # el intervalo entre granos se sortea alrededor de 1/densidad: si fuera
        # exacto, la nube tendria un pulso audible en esa frecuencia
        t += rng.uniform(0.55, 1.45) / d

        ms = max(_curva(grano_ms, t, dur), 1.0)
        ms *= 1.0 + var_grano * rng.uniform(-1.0, 1.0)
        largo = max(int(ms / 1000.0 * sr), 8)

        altura = alturas[rng.randint(len(alturas))]
        if dispersion_cents:
            altura *= 2.0 ** (rng.uniform(-dispersion_cents, dispersion_cents) / 1200.0)

        # de donde se lee: la cabeza avanza a `avance` y se dispersa alrededor
        centro = (posicion + avance * t) * sr
        centro += rng.uniform(-dispersion_ms, dispersion_ms) / 1000.0 * sr

        # el grano se lee a `altura` muestras por muestra de salida: transponer
        # sin cambiar el largo del grano es todo el truco
        lectura = (centro + np.arange(largo) * altura) % largo_fuente
        grano = np.interp(lectura, indice_fuente, fuente) * _ventana(largo)

        i = int(t * sr)
        if i >= n:
            break
        j = min(i + largo, len(salida))
        salida[i:j] += grano[:j - i]

    salida = salida[:n]
    pico = np.abs(salida).max()
    return salida / pico if pico > 0 else salida
