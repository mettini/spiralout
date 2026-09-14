"""Sonificacion de biodata: convierte una serie lenta en eventos de nota.

PASO 0 DEL EXPERIMENTO DE HONGOS. La pregunta que contesta NO es "que dice el
hongo" sino "¿una señal con esa estadistica, mapeada a notas, suena a algo?". Si
la respuesta es que no, ningun hardware lo arregla y no hay que comprar nada.

QUE ES SONIFICAR, SIN ADORNOS. El hongo no suena ni hace musica: lo que se mide es
una variacion electrica y lo que la vuelve musica es el MAPEO, que es una decision
de composicion, no del hongo. Este archivo es ese mapeo, y esta separado a
proposito de la medicion para poder juzgarlo solo.

LA SEÑAL DE ACA ES SINTETICA Y ESTA DECLARADA COMO TAL. Imita la estadistica que
reporto Adamatzky sobre potencial electrico extracelular en hongos: picos de
duracion larga (minutos, no milisegundos) agrupados en trenes, con dos poblaciones,
una rapida y una lenta, y silencios largos entre trenes. NO es data de un hongo y
no puede presentarse como tal en ningun lado.

    python3.10 sonificar.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "framework"))
from scipy.io import wavfile  # noqa: E402

SR = 44100

# LA COMPRESION DE TIEMPO ES LA DECISION MAS FUERTE DE TODAS.
#
# Los picos del hongo pasan en escala de minutos y horas. Para que haya musica hay
# que comprimir, y cuanto se comprime define el genero: poco y es drone, mucho y es
# un arpegio. Aca 1 hora de hongo entra en 60 s de audio, o sea 60x.
#
# Esto NO es un detalle tecnico: es donde el compositor entra y donde se termina
# cualquier ilusion de que "el hongo compuso".
HORAS = 1.0
DUR_S = 60.0
COMPRESION = (HORAS * 3600) / DUR_S

# la escala del proyecto: menor natural sobre re, que es donde cierra `melodia.py`
RAIZ_HZ = 146.83                      # re3
GRADOS = [0, 2, 3, 5, 7, 8, 10]       # menor natural


def señal_sintetica(horas=HORAS, paso_s=1.0, semilla=7):
    """Serie de potencial electrico IMITANDO la estadistica publicada. No es data real.

    Dos poblaciones de picos, como reporta la literatura: una rapida (del orden de
    2-3 min entre picos) y una lenta (del orden de 10-15 min), agrupadas en trenes
    con silencios largos en el medio.
    """
    rng = np.random.default_rng(semilla)
    n = int(horas * 3600 / paso_s)
    t = np.arange(n) * paso_s
    v = np.zeros(n)

    def tren(periodo_s, ancho_s, amp, cuantos):
        """Un tren de picos: varios picos seguidos y despues silencio."""
        inicio = rng.uniform(0, horas * 3600 * 0.8)
        for k in range(cuantos):
            centro = inicio + k * periodo_s * rng.uniform(0.8, 1.2)
            if centro > horas * 3600:
                break
            # el pico es lento y asimetrico: sube mas rapido de lo que baja
            d = t - centro
            sube = np.exp(-np.clip(-d, 0, None) / (ancho_s * 0.35))
            baja = np.exp(-np.clip(d, 0, None) / (ancho_s * 1.0))
            v[:] += amp * np.where(d < 0, sube, baja)

    for _ in range(6):
        tren(periodo_s=rng.uniform(120, 200), ancho_s=40, amp=0.6,
             cuantos=rng.integers(4, 9))
    for _ in range(3):
        tren(periodo_s=rng.uniform(600, 900), ancho_s=150, amp=1.0,
             cuantos=rng.integers(2, 5))

    # deriva lenta de fondo: el electrodo y el organismo van cambiando de base
    deriva = np.cumsum(rng.standard_normal(n)) * 0.004
    v += deriva - deriva.mean()
    return t, v


def a_eventos(t, v, umbral_sigma=1.2):
    """Cada cruce de umbral hacia arriba es una nota. Devuelve (tiempo_s, altura 0..1)."""
    u = v.mean() + umbral_sigma * v.std()
    arriba = v > u
    cruces = np.flatnonzero(np.diff(arriba.astype(int)) == 1) + 1
    ev = []
    for i in cruces:
        # la altura del pico decide el grado; se mide hasta que vuelve a bajar
        j = i
        while j < len(v) - 1 and v[j + 1] >= v[j]:
            j += 1
        alt = (v[j] - u) / (v.max() - u + 1e-9)
        ev.append((t[i] / COMPRESION, float(np.clip(alt, 0, 1))))
    return ev


def render(ev, dur_s=DUR_S):
    """Una voz por evento. Sierra suave con ataque lento, que es la paleta del disco."""
    n = int(dur_s * SR)
    out = np.zeros(n)
    for t0, alt in ev:
        grado = GRADOS[int(alt * (len(GRADOS) - 1))]
        octava = 1 if alt < 0.66 else 2
        f = RAIZ_HZ * (2 ** (grado / 12.0)) * octava
        largo = int(SR * (3.0 + 5.0 * alt))
        i0 = int(t0 * SR)
        if i0 + largo > n:
            largo = n - i0
        if largo <= 0:
            continue
        tt = np.arange(largo) / SR
        # tres armonicos, nada mas: la idea es juzgar el MAPEO, no el timbre
        voz = (np.sin(2 * np.pi * f * tt)
               + 0.35 * np.sin(2 * np.pi * 2 * f * tt)
               + 0.16 * np.sin(2 * np.pi * 3 * f * tt))
        env = np.minimum(tt / 1.2, 1.0) * np.exp(-tt / (largo / SR / 2.2))
        out[i0:i0 + largo] += voz * env * (0.10 + 0.10 * alt)
    pico = np.abs(out).max()
    return out / pico * 0.7 if pico > 0 else out


if __name__ == "__main__":
    t, v = señal_sintetica()
    ev = a_eventos(t, v)
    print(f"  señal SINTETICA de {HORAS:.0f} h, comprimida {COMPRESION:.0f}x a {DUR_S:.0f} s")
    print(f"  {len(ev)} eventos ({len(ev)/DUR_S*60:.0f} notas por minuto de audio)")
    if ev:
        huecos = np.diff([e[0] for e in ev])
        print(f"  hueco entre notas: min {huecos.min():.1f}s  mediana "
              f"{np.median(huecos):.1f}s  max {huecos.max():.1f}s")
    audio = render(ev)
    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hongo_sintetico.wav")
    wavfile.write(salida, SR, np.int16(audio * 32767))
    print(f"  -> {salida}")
