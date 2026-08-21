#!/usr/bin/env python3
"""Candidatas de melodia para el moog. Una WAV por cada una, para elegir.

    python3.10 transmissions/02/bj3_n_pt/melodias.py

Idea del user: pensarlo como un tema. Si la melodia no cambia, el que escucha queda
atrapado ahi. Asi que en vez de una melodia que se repite 190 s, se arman VARIAS y
despues se hace el collage con las que sirvan.

Todas salen del mismo material armonico (`docs/43`), o sea que se pueden encadenar sin
que choquen:

    Mi   80,03 Hz     Sol  95,17 Hz     Si  119,91 Hz
    Re   71,30 Hz     la fundamental de la base, la septima del acorde
    Re'  73,42 Hz     el Re del VOYAGER de Heliopause, 51 cents mas arriba

Todas con el mismo largo, mismo nivel y el mismo instrumento, para que la comparacion
sea de melodia y no de mezcla.
"""
import os
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "framework"))

from aem.synths import voz_moog  # noqa: E402
from render import SR, camara, fades, hp, lp, mono_graves, respiracion  # noqa: E402

FUND = 71.3
MI, SOL, SI = FUND * 2 ** (2 / 12), FUND * 2 ** (5 / 12), FUND * 2 ** (9 / 12)
RE = FUND                      # la septima: la nota de la propia base
RE_VOY = 73.42                 # el Re del Voyager. Mismo nombre, 51 cents arriba

# (nombre, notas [(Hz, segundos)], glide, que es)
MELODIAS = [
    ("01_descendente", [(SI, 9), (SOL, 8), (MI, 13)], 2.4,
     "El motivo del disco tal cual. Cae y se queda en Mi"),

    ("02_ascendente", [(MI, 9), (SOL, 8), (SI, 13)], 2.4,
     "El mismo dado vuelta, el de +H. Abre en vez de cerrar"),

    ("03_septima", [(SI, 7), (RE, 9), (SOL, 7), (MI, 11)], 2.8,
     "Pasa por el Re, que es la nota de la base. Suena a que no termina"),

    ("04_saltos", [(MI, 6), (SI, 7), (SOL, 6), (RE, 8), (SI, 10)], 2.0,
     "Intervalos grandes, mas dramatico. Menos drone, mas gesto"),

    ("05_suspendida", [(SOL, 8), (SI, 7), (SOL, 7), (SI, 8), (SOL, 12)], 3.2,
     "Dos notas oscilando. Hipnotico, no resuelve nunca"),

    ("06_voyager", [(SI, 8), (SOL, 8), (MI, 9), (RE_VOY / 2, 16)], 4.0,
     "Abandona el motivo y cae en el Re del VOYAGER, una octava abajo (36,71 Hz). "
     "Contra la base late a 1,06 Hz: no es acorde ni melodia, es interferencia"),

    ("07_grave", [(SI / 2, 9), (SOL / 2, 8), (MI / 2, 14)], 3.0,
     "El motivo una octava entera abajo. Aplastando, para el final"),

    ("08_larga", [(MI, 7), (SOL, 6), (SI, 7), (RE, 6), (SOL, 7), (MI, 8), (SI, 12)], 2.6,
     "Siete notas sin repetir un par consecutivo. Es la que mas se acerca a una linea "
     "que no se cicla"),
]


def rendir(notas, glide, dur_extra=6.0):
    """La misma voz del tema, para que la comparacion sea justa."""
    x = voz_moog(notas, glide_s=glide, detune_cents=2.5, sub=0.62,
                 corte_base=90.0, corte_barrido=2100.0, resonancia=0.78,
                 drive=16.0, sr=SR, env_filtro=(3.2, 4.0, 0.55, 6.0),
                 env_amp=(2.2, 3.0, 0.82, 7.5))

    # el mismo aplanado de latido que lleva en el tema
    env = np.convolve(np.abs(x), np.ones(int(0.35 * SR)) / int(0.35 * SR), "same")
    lento = np.convolve(env, np.ones(int(3.0 * SR)) / int(3.0 * SR), "same")
    x = x * np.clip((lento / (env + 1e-6)) ** 0.7, 0.0, 2.0)
    x /= np.abs(x).max() or 1.0

    x = lp(np.stack([x, x], axis=1), 3500)
    x = np.stack([x[:, 0], np.roll(x[:, 1], int(0.019 * SR))], axis=1)
    x = hp(x, 34)
    x = mono_graves(x, 150)
    x = respiracion(x, 0.08, periodo=47.0)
    cola = camara(x, 4, ir_lowpass=2600, wet=0.25, semilla=17000, pre_ms=60)
    x = 0.96 * x + 0.24 * cola[:len(x)]
    x = hp(x, 30)
    x = fades(x, 1.5)
    return x / (np.abs(x).max() or 1.0)


def main():
    salida = os.path.join(AQUI, "melodias")
    os.makedirs(salida, exist_ok=True)
    medidor = pyln.Meter(SR)
    print("  notas disponibles:")
    for n, f in (("Mi", MI), ("Sol", SOL), ("Si", SI), ("Re base", RE), ("Re Voyager", RE_VOY)):
        print(f"    {n:12} {f:7.2f} Hz")
    print()

    for nombre, notas, glide, que in MELODIAS:
        x = rendir(notas, glide)
        # todas al mismo nivel, para que se comparen melodias y no volumenes
        x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), -20.0)
        if np.abs(x).max() > 0.98:
            x *= 0.98 / np.abs(x).max()
        ruta = os.path.join(salida, f"{nombre}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        alturas = " ".join(f"{f:.0f}" for f, _ in notas)
        print(f"  {nombre:16} {len(x)/SR:5.1f}s   {alturas} Hz")
        print(f"                   {que}")
    print(f"\n  -> {os.path.relpath(salida, RAIZ)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
