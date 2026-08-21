#!/usr/bin/env python3
"""Lo que separa una maqueta de algo tocado. Todo lo de este archivo es variacion.

El diagnostico del user sobre la primera version fue "los sonidos son de plastico,
cada tecla suena igual que la anterior, el oscilador no oscila". Tenia razon y la
causa era estructural, no de timbre: **el riff se generaba UNA vez y se repetia
copiado 42 veces**. Era literalmente el mismo array de muestras. Ningun filtro
arregla eso.

QUE HACE QUE ALGO SUENE TOCADO, EN ORDEN DE CUANTO SE NOTA

1. **Nivel distinto por nota**, y el filtro atado al nivel. Un golpe mas fuerte no
   es solo mas fuerte: es mas brillante. Esa correlacion es la senal mas fuerte
   de que hay una mano y no una grilla.
2. **Fase distinta por nota.** Dos notas de la misma altura generadas desde fase
   cero dan EXACTAMENTE las mismas muestras. El ataque es lo que mas delata: son
   los primeros 20 ms los que el oido compara.
3. **Tiempo.** Nadie cae en la grilla. 5 a 15 ms de corrimiento alcanzan, y tienen
   que ser al azar por golpe, no un swing fijo (un swing fijo tambien es una
   grilla, solo que otra).
4. **Afinacion.** Unos pocos cents por nota, mas deriva DENTRO de la nota.
5. **Wow y flutter.** La modulacion lenta de todo el bus, la de la cinta. Es lo que
   hace que nada quede clavado, y es la unica de las cinco que se aplica al final
   y de una vez.
6. **Aire.** El ruido del ataque: el dedo, la pua, el trasteo. Sin eso el ataque
   arranca de la nada y ahi es donde suena sintetico.
"""
import numpy as np

from aem.core import SR


# ---------------------------------------------------------------- azar por nota
class Mano:
    """Un generador de azar con memoria corta, uno por pista.

    Es una clase y no funciones sueltas porque el azar tiene que ser
    REPRODUCIBLE: misma semilla, mismo tema. Sin eso no se puede comparar dos
    renders y no se puede volver atras.
    """

    def __init__(self, semilla=24):
        self.rng = np.random.RandomState(semilla)

    def pct(self, base, cuanto):
        """`base` variado en +-`cuanto` por ciento."""
        return base * (1.0 + cuanto * self.rng.uniform(-1.0, 1.0))

    def entre(self, a, b):
        return self.rng.uniform(a, b)

    def cents(self, cuantos):
        """Factor de frecuencia para una desafinacion al azar de +-`cuantos`."""
        return 2.0 ** (self.rng.uniform(-cuantos, cuantos) / 1200.0)

    def ms(self, cuantos):
        """Corrimiento de tiempo al azar, en segundos."""
        return self.rng.uniform(-cuantos, cuantos) / 1000.0

    def dado(self, probabilidad):
        return self.rng.uniform() < probabilidad

    def elegir(self, opciones):
        return opciones[self.rng.randint(len(opciones))]


# ------------------------------------------------------------- retardo variable
def _retardar(x, d_muestras):
    """Retardo fraccionario por interpolacion. La base de wow, flutter y vibrato:
    modular el retardo ES modular la altura, porque estirar el tiempo de lectura y
    bajar el tono son la misma operacion."""
    n = len(x)
    i = np.arange(n)
    return np.interp(i - d_muestras, i, x)


def _incoherente(n, periodos, semilla, sr=SR):
    """Suma de senos lentos con periodos que no son multiplos entre si, normalizada
    a +-1. Un solo LFO se escucha COMO un LFO; tres incoherentes se escuchan como
    inestabilidad."""
    rng = np.random.RandomState(semilla)
    t = np.arange(n) / sr
    y = sum(rng.uniform(0.5, 1.0) * np.sin(2 * np.pi * t / p + rng.uniform(0, 6.28))
            for p in periodos)
    return y / (np.abs(y).max() or 1.0)


def wow_flutter(x, wow_ms=1.1, wow_periodos=(1.4, 2.3, 3.7),
                flutter_ms=0.09, flutter_hz=6.3, semilla=24, sr=SR):
    """Wow (lento, de la mecanica) y flutter (rapido, del rozamiento).

    Es el efecto con mejor relacion entre lo que cuesta y lo que cambia. Nada
    analogico esta afinado quieto, y en cuanto una senal deja de estar clavada el
    oido la lee como grabada en vez de calculada.

    Valores bajos a proposito: 1 ms de wow sobre un bajo son ~2 cents. Arriba de 3
    ya no es cinta, es un cassette arruinado.
    """
    n = len(x)
    d = _incoherente(n, wow_periodos, semilla, sr) * (wow_ms / 1000.0 * sr)
    if flutter_ms:
        t = np.arange(n) / sr
        d += np.sin(2 * np.pi * flutter_hz * t) * (flutter_ms / 1000.0 * sr)
    return _retardar(x, d)


def vibrato(x, hz=5.4, cents=18.0, desde=0.4, sr=SR):
    """Vibrato que ENTRA DESPUES del ataque, no desde el principio.

    Ningun instrumentista arranca la nota vibrando: primero afina y despues le
    mete el vibrato. El vibrato desde la muestra cero es el tell mas comun de un
    sintetizador con la perilla puesta.

    `desde` es la fraccion de la nota en la que ya llego a profundidad completa.
    """
    n = len(x)
    if n < 16:
        return x
    # profundidad de retardo que da esa desviacion en cents a esa frecuencia
    amp = (2.0 ** (cents / 1200.0) - 1.0) / (2 * np.pi * hz) * sr
    t = np.arange(n) / sr
    crecer = np.clip(np.linspace(0, 1, n) / max(desde, 1e-3), 0, 1) ** 1.6
    return _retardar(x, np.sin(2 * np.pi * hz * t) * amp * crecer)


# ------------------------------------------------------------------------ aire
def aire(dur=0.03, centro=1400.0, amp=0.06, semilla=None, sr=SR):
    """El ruido del ataque: la pua, el dedo, el trasteo, la lengua.

    Banda angosta alrededor de `centro` y 30 ms de vida. La regla anti fritura del
    proyecto es sobre ruido SOSTENIDO; esto dura menos que un parpadeo y es lo que
    le da borde al ataque.
    """
    from aem.effects import hpf, lpf

    n = max(int(dur * sr), 8)
    rng = np.random.RandomState(semilla) if semilla is not None else np.random
    x = rng.standard_normal(n) if hasattr(rng, 'standard_normal') else rng.randn(n)
    x = lpf(hpf(x, centro * 0.6), centro * 2.2)
    ta = np.arange(n) / sr
    env = np.exp(-ta * 90) * (1 - np.exp(-ta * 900))
    pico = np.abs(x * env).max() or 1.0
    return amp * x * env / pico


def fase_azar(freq, mano, sr=SR):
    """Cuantas muestras de mas hay que generar antes de la nota para que arranque
    en otro punto del ciclo. Es una linea de codigo y es la diferencia entre diez
    notas identicas y diez notas parecidas."""
    return int(mano.entre(0, 1) * sr / max(freq, 20.0))
