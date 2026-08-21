#!/usr/bin/env python3
"""Altura sacada del propio material: el brillo y el chelo.

Dos capas nuevas, y ninguna trae un instrumento. Las dos salen de filtrar la lluvia
con resonadores afinados a la serie armonica de la base (71,3 Hz), que es la jugada
Lustmord: no hay synths, hay grabaciones deformadas.

    python3.10 transmissions/02/bj3_n_pt/cuerdas.py

POR QUE RESONADORES Y NO UN SYNTH

Un resonador de Q alto excitado por ruido de banda ancha suena a cuerda frotada, y no
por casualidad: eso ES una cuerda frotada. El arco mete ruido de friccion, el cuerpo
resuena en una serie armonica y filtra todo lo demas. La lluvia ya es el ruido de
banda ancha. Solo falta el cuerpo.

Y como los parciales se derivan de 71,3 Hz, todo lo que salga de aca esta afinado con
el tema por construccion, no por suerte.

    brillo   parciales 12 16 20 24 32   ->   856 a 2281 Hz
    chelo    fundamental en el parcial 3 (213,9 Hz = un Sol#3 bajo) con sus armonicos

OJO: el brillo vive en 1,5-2,3 kHz, o sea adentro de la banda que marca qa:spectral.
Va con Q alto a proposito: un resonador angosto pone energia en frecuencias
DISCRETAS, que el oido lee como altura. Ruido ancho en la misma banda es fritura. La
diferencia entre las dos cosas es exactamente el ancho de banda.
"""
import os
import sys

import numpy as np

from rain import repetir_suave  # noqa: E402  (el mismo cruce de junturas)
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import iirpeak, sosfilt, tf2sos

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)

from rain import cargar as cargar_lluvia, seguir_arco  # noqa: E402
from render import (SEMILLA, SR, camara, envolvente, fades, hp, lp,  # noqa: E402
                    medir, mono_graves, respiracion)

DUR = 120.0
FUND = 71.3

# parciales del brillo. Todos multiplos enteros: consonantes por definicion.
BRILLO = (12, 16, 20, 24, 32)
# el chelo canta en el parcial 3. Sus propios armonicos son 3, 6, 9, 12, 15, 18.
CHELO = (3, 6, 9, 12, 15, 18)
GANANCIA_CHELO = (1.0, 0.62, 0.38, 0.26, 0.15, 0.10)   # caida natural de una cuerda


def resonar(x, hz, q):
    """Un resonador. Q alto = timbra mas tiempo y mas angosto."""
    b, a = iirpeak(hz / (SR / 2), q)
    return sosfilt(tf2sos(b, a), x)


def banco(exc, parciales, q, ganancias=None):
    """Suma de resonadores sobre la serie armonica de FUND."""
    ganancias = ganancias or [1.0] * len(parciales)
    y = np.zeros(len(exc))
    for p, g in zip(parciales, ganancias):
        hz = FUND * p
        if hz > SR / 2 * 0.9:
            continue
        y += resonar(exc, hz, q) * g
    return y / (np.abs(y).max() or 1.0)


def arco(n, ataque_s, sostenido_s, caida_s):
    """La envolvente de un arco: entra lento, se sostiene, muere lento. Es lo que
    separa una cuerda frotada de una campana."""
    a, s, c = (int(v * SR) for v in (ataque_s, sostenido_s, caida_s))
    e = np.concatenate([np.linspace(0, 1, a) ** 1.7,
                        np.ones(max(s, 0)),
                        np.linspace(1, 0, c) ** 2.2])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def brillo(fuente, lufs_objetivo, dur=DUR):
    """La capa que hace que algo destelle. Discreta, no continua.

    Se abre y se cierra: si estuviera siempre, seria otra capa de nube y volveria a
    empastar. Lo que da aire no es agregar agudo, es que el agudo APAREZCA.
    """
    n = int(dur * SR)
    reps = int(np.ceil(n / len(fuente)))
    exc = repetir_suave(fuente, n)

    y = banco(exc, BRILLO, q=90)

    # destellos: el banco solo suena cuando se lo abre
    env = np.zeros(n)
    rng = np.random.RandomState(SEMILLA)
    pos = int(9.0 * SR)
    while pos < n - int(18.0 * SR):   # que no arranque un destello sobre el final
        largo = int(rng.uniform(5.0, 11.0) * SR)
        e = arco(largo, ataque_s=1.8, sostenido_s=largo / SR - 5.0, caida_s=3.2)
        env[pos:pos + len(e)] += e[:max(0, n - pos)] * rng.uniform(0.55, 1.0)
        pos += largo + int(rng.uniform(7.0, 16.0) * SR)
    y = y * np.clip(env, 0, 1)

    x = np.stack([y, np.roll(y, int(0.017 * SR))], axis=1)   # ancho por retardo corto
    x = hp(x, 700)
    x = respiracion(x, 0.14, periodo=43.0)                   # primo libre
    x = camara(x, 7, ir_lowpass=4000, wet=0.5, semilla=13000)
    x = hp(x, 650)
    x = fades(x, 3.0)
    x /= np.abs(x).max()
    m = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, m.integrated_loudness(x), lufs_objetivo)
    return x * (0.98 / np.abs(x).max()) if np.abs(x).max() > 0.98 else x


def vibrato(x, hz=5.4, cents=22.0, arranque_s=0.35):
    """El vibrato, por velocidad de lectura variable.

    Es LO que hace que una cuerda suene a cuerda. Sin esto, un banco de resonadores
    con envolvente suena a organo o a pad, por bien afinado que este.

    Dos detalles que importan: empieza DESPUES del ataque (nadie vibra mientras
    engancha la cuerda) y crece, no arranca a fondo.
    """
    n = len(x)
    t = np.arange(n) / SR
    entrada = np.clip((t - arranque_s) / 0.7, 0, 1)
    tasa = 2.0 ** (cents * entrada * np.sin(2 * np.pi * hz * t) / 1200.0)
    idx = np.cumsum(tasa)
    idx = idx[idx < n - 1]
    return np.interp(idx, np.arange(n), x)


def nota(exc, f0, largo_s, rng):
    """Una nota de chelo: resonadores sobre SU fundamental, arco y vibrato."""
    n = int(largo_s * SR)
    seg = exc[:n] if len(exc) >= n else np.pad(exc, (0, n - len(exc)))

    y = np.zeros(n)
    for k, g in zip((1, 2, 3, 4, 5, 6), GANANCIA_CHELO):
        hz = f0 * k
        if hz > SR / 2 * 0.9:
            continue
        y += resonar(seg, hz, q=160) * g
    y /= np.abs(y).max() or 1.0

    # el ataque del arco: corto. Es la diferencia entre frotar y aparecer
    e = arco(n, ataque_s=rng.uniform(0.18, 0.38),
             sostenido_s=largo_s * 0.55, caida_s=largo_s * 0.35)
    y *= e

    # la mordida: un chispazo de ruido sin filtrar al enganchar la cuerda
    mordida = int(0.05 * SR)
    y[:mordida] += seg[:mordida] * 0.10 * np.linspace(1, 0, mordida)

    return vibrato(y, hz=rng.uniform(4.8, 6.1), cents=rng.uniform(16, 28))


# EL MOTIVO DEL DISCO. Em = Mi Sol Si, y H (notacion alemana) ES el Si: la nota que
# el tercer track "agrega" ya estaba adentro del acorde, es su quinta.
#
# Track 1 lo dice DESCENDENTE y termina en Mi: algo cae, y la entidad sigue siendo
# ella. En el track 3 va al reves y termina en Si: las mismas tres notas, movido el
# centro. No se suma nada y sin embargo cambia todo, que es la Æ.
#
# Afinado contra la base (71,3 Hz = un Re bajo), asi que Em suena sobre su propia
# septima: Em7 con la septima abajo, un acorde que flota y no resuelve.
SEMITONOS = {"mi": 2, "sol": 5, "si": 9}
OCTAVA_CHELO = 2                       # registro de chelo: 160 a 240 Hz
MOTIVO = (("si", 5.0), ("sol", 4.2), ("mi", 6.5))


def altura(nombre, octava=OCTAVA_CHELO):
    return FUND * 2.0 ** (SEMITONOS[nombre] / 12.0) * octava


def chelo(fuente, lufs_objetivo, dur=DUR):
    """La cuerda frotada. Entra tarde, toca una linea y se va.

    El chelo no es una capa, es una APARICION: lo que genera tension es que algo con
    altura definida asome sobre un drone que no la tiene. Pero para que se lea como
    chelo tiene que MOVERSE. Notas de 2 a 5 segundos, no de quince.
    """
    n = int(dur * SR)
    reps = int(np.ceil(n / len(fuente)))
    exc = repetir_suave(fuente, n)
    exc = lp(np.stack([exc, exc], axis=1), 4000)[:, 0]

    y = np.zeros(n)
    rng = np.random.RandomState(SEMILLA + 1)
    pos = int(0.55 * dur * SR)                 # entra en el ultimo tercio
    for nombre, largo_s in MOTIVO:
        v = nota(exc[pos:pos + int(largo_s * SR) + SR], altura(nombre), largo_s, rng)
        fin = min(n, pos + len(v))
        if fin <= pos:
            break
        y[pos:fin] += v[:fin - pos] * rng.uniform(0.82, 1.0)
        # legato flojo: las notas casi se tocan, con algun respiro
        pos += int((largo_s * rng.uniform(0.80, 0.95) + rng.uniform(0.1, 0.9)) * SR)
    y /= np.abs(y).max() or 1.0

    x = np.stack([y, np.roll(y, int(0.023 * SR))], axis=1)
    x = hp(x, 120)
    x = mono_graves(x, 200)
    x = camara(x, 9, ir_lowpass=2600, wet=0.48, semilla=14000, pre_ms=60)
    x = hp(x, 110)
    x = fades(x, 3.0)
    x /= np.abs(x).max()
    m = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, m.integrated_loudness(x), lufs_objetivo)
    return x * (0.98 / np.abs(x).max()) if np.abs(x).max() > 0.98 else x


def main():
    np.random.seed(SEMILLA)
    print(f"  base {FUND} Hz = Re (50 cents bajo)")
    print("  motivo Em + H, descendente:",
          "  ".join(f"{n.capitalize()} {altura(n):.1f}" for n, _ in MOTIVO), "Hz")
    print("    brillo  ", "  ".join(f"{FUND*p:.0f}" for p in BRILLO), "Hz")
    print()

    lluvia = cargar_lluvia("lluvia_alta")
    sr, base = wavfile.read(os.path.join(AQUI, "mix_v3.wav"))
    base = base.astype(np.float64) / 32768.0
    n = min(len(base), int(DUR * SR))
    base = base[:n]
    lufs = pyln.Meter(SR).integrated_loudness(base)

    # las dos siguen el arco de la base: si no, siguen timbrando cuando la base
    # ya murio y el ratio de banda alta se dispara al final (lo marco qa:spectral)
    br = seguir_arco(brillo(lluvia, lufs)[:n], base)
    ch = seguir_arco(chelo(lluvia, lufs)[:n], base)

    mezcla = base + br * 10 ** (-17 / 20) + ch * 10 ** (-13 / 20)
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-6.0 / 20)

    salidas = (("brillo", br), ("chelo", ch), ("mix_v5", mezcla))
    for nombre, x in salidas:
        ruta = os.path.join(AQUI, f"{nombre}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        print(f"  -> {os.path.relpath(ruta, RAIZ)}")

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    for nombre, x in (("mix_v3 (antes)", base),) + salidas:
        medir(nombre, x)


if __name__ == "__main__":
    sys.exit(main())
