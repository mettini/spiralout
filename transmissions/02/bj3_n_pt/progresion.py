#!/usr/bin/env python3
"""La progresion del moog: un solo track continuo, para escuchar como evoluciona.

    python3.10 transmissions/02/bj3_n_pt/progresion.py

QUE SE CORRIGE DE LA TANDA ANTERIOR

1. Eran ocho versiones del MISMO sonido con las notas en otro orden. Aca cada tramo
   tiene un timbre distinto de verdad: cambia el oscilador, el filtro, el drive, la
   resonancia y el espacio, no solo la melodia.
2. El "augghh" del segundo 24: la envolvente de FILTRO tenia release de 6 s, asi que
   en una nota de 30 empezaba a cerrar en el segundo 24 y el corte se desplomaba de
   1245 Hz a 90. En una escalera con resonancia eso es un barrido que aulla. Aca el
   filtro no cierra: se mueve poco y lento.

EL MAPA. La ventana del moog en el tema va de 7:40 a 11:11, o sea 211 s.

    tramo  minuto        seg   sonido
    1      7:40 a 8:15    35   entrada limpia, casi sin drive
    2      8:15 a 8:50    35   cuerpo: sube el drive y la resonancia
    3      8:50 a 9:25    35   RACIMO microtonal: deja de ser nota, es textura
    4      9:25 a 10:00   35   SYNC duro: metalico, lo mas agresivo del tema
    5      10:00 a 10:35  35   una octava abajo, aplastando
    6      10:35 a 11:11  36   el Re del VOYAGER: interferencia que no resuelve

Los tramos se cruzan entre si, no se cortan: la voz no se apaga nunca. Eso ademas
arregla el corte cada 39 s que tenia la version con bucle.
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

from aem.synths import (adsr, cluster_microtonal, glide, ladder_moog,  # noqa: E402
                        pulso, sierra, sync_duro, voz_moog)
from render import SR, camara, fades, hp, lp, mono_graves, respiracion  # noqa: E402

FUND = 71.3
MI, SOL, SI = FUND * 2 ** (2 / 12), FUND * 2 ** (5 / 12), FUND * 2 ** (9 / 12)
RE, RE_VOY = FUND, 73.42
CRUCE = 4.0          # segundos de cruce entre tramos


def _post(x, sala=4, lp_hz=3500, wet=0.25, ancho=0.019):
    x = lp(np.stack([x, x], axis=1), lp_hz)
    x = np.stack([x[:, 0], np.roll(x[:, 1], int(ancho * SR))], axis=1)
    x = hp(x, 32)
    x = mono_graves(x, 150)
    cola = camara(x, sala, ir_lowpass=2600, wet=wet, semilla=17000, pre_ms=60)
    return hp(0.94 * x + wet * cola[:len(x)], 30)


# ---------------------------------------------------------------- los tramos
def t1_limpia(dur):
    """Entrada. Casi sin drive, filtro quieto y abierto: la nota se escucha desnuda."""
    x = voz_moog([(SI, dur * 0.35), (SOL, dur * 0.28), (MI, dur * 0.37)],
                 glide_s=3.0, detune_cents=2.0, sub=0.5, corte_base=420.0,
                 corte_barrido=500.0, resonancia=0.45, drive=4.0,
                 env_filtro=(6.0, 8.0, 0.9, 2.0), env_amp=(3.0, 4.0, 0.9, 3.0))
    return _post(x, sala=5, wet=0.22)


def t2_cuerpo(dur):
    """Sube el drive y la resonancia. La escalera empieza a comprimir sola."""
    x = voz_moog([(MI, dur * 0.3), (SOL, dur * 0.22), (RE, dur * 0.2), (SI, dur * 0.28)],
                 glide_s=2.2, detune_cents=4.0, sub=0.8, corte_base=180.0,
                 corte_barrido=900.0, resonancia=0.86, drive=42.0, pwm=0.32,
                 env_filtro=(5.0, 7.0, 0.8, 2.5), env_amp=(2.0, 3.0, 0.9, 3.0))
    return _post(x, sala=6, wet=0.3)


def t3_racimo(dur):
    """RACIMO MICROTONAL. Cinco voces a 0,75 de semitono: el oido no lo lee como
    acorde sino como textura, y aparece un batido lento. Es el truco de Dune
    (`docs/44`), y es lo mas distinto que hay en todo el modulo."""
    n = int(dur * SR)
    y = cluster_microtonal(SOL, voces=5, paso_semitonos=0.75, dur=dur,
                           generador=sierra, deriva_cents=6.0)
    corte = 200 + 700 * (0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / SR / 31.0))
    y = ladder_moog(y[:n], corte, resonancia=0.7, drive=18.0)
    return _post(y * adsr(n, 6.0, 6.0, 0.92, 5.0), sala=9, lp_hz=3000, wet=0.4)


def t4_sync(dur):
    """SYNC DURO. El esclavo reinicia su fase con cada ciclo del maestro y eso genera
    un formante metalico que barre. Es lo mas agresivo del tema, y es el unico lugar
    donde tiene sentido usarlo."""
    n = int(dur * SR)
    maestro = np.full(n, MI)
    esclavo = MI * (2.0 + 3.0 * (0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / SR / 19.0)))
    y = sync_duro(maestro, esclavo)[:n]
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    y = y * 0.6 + pulso(np.full(n, MI / 2), 0.35) * 0.5
    y = ladder_moog(y, np.full(n, 900.0), resonancia=0.8, drive=55.0)
    return _post(y * adsr(n, 4.0, 5.0, 0.88, 6.0), sala=7, lp_hz=2600, wet=0.28)


def t5_aplastando(dur):
    """Una octava entera abajo, resonancia alta y drive fuerte. No es melodia, es peso."""
    x = voz_moog([(SI / 2, dur * 0.33), (SOL / 2, dur * 0.27), (MI / 2, dur * 0.4)],
                 glide_s=5.0, detune_cents=3.0, sub=1.0, corte_base=70.0,
                 corte_barrido=260.0, resonancia=0.9, drive=70.0,
                 env_filtro=(7.0, 9.0, 0.85, 3.0), env_amp=(4.0, 5.0, 0.92, 4.0))
    return _post(x, sala=8, lp_hz=1400, wet=0.32)


def t6_voyager(dur):
    """El cierre. Dos graves casi identicos: el Re del planeta (35,65) y el Re del
    VOYAGER (36,71). No forman acorde ni melodia, laten a 1,06 Hz. Es la unica parte
    del tema donde las dos afinaciones suenan juntas."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    a = sierra(np.full(n, FUND / 2)) * 0.5 + pulso(np.full(n, FUND / 4), 0.4) * 0.4
    b = sierra(np.full(n, RE_VOY / 2)) * 0.5 + pulso(np.full(n, RE_VOY / 4), 0.4) * 0.4
    # el Voyager entra despues: primero esta solo el planeta
    entrada = np.clip((t - dur * 0.22) / (dur * 0.3), 0, 1)
    y = a + b * entrada
    y = ladder_moog(y, 60 + 180 * np.exp(-t / (dur * 0.6)), resonancia=0.75, drive=30.0)
    return _post(y * adsr(n, 6.0, 8.0, 0.9, dur * 0.35), sala=10, lp_hz=1200, wet=0.38)


TRAMOS = [
    ("1 · entrada limpia", t1_limpia, 35),
    ("2 · cuerpo, con drive", t2_cuerpo, 35),
    ("3 · racimo microtonal", t3_racimo, 35),
    ("4 · sync duro", t4_sync, 35),
    ("5 · aplastando", t5_aplastando, 35),
    ("6 · el Voyager", t6_voyager, 36),
]


def main():
    medidor = pyln.Meter(SR)
    salida = os.path.join(AQUI, "melodias")
    os.makedirs(salida, exist_ok=True)

    piezas = []
    print("  tramo                    desde     seg")
    t = 460.0
    for nombre, fn, dur in TRAMOS:
        x = fn(dur + CRUCE)
        x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), -20.0)
        if np.abs(x).max() > 0.98:
            x *= 0.98 / np.abs(x).max()
        # cada tramo tambien se guarda suelto, para escucharlo aislado
        ruta = os.path.join(salida, f"tramo_{nombre.split(' ')[0]}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        piezas.append(x)
        print(f"  {nombre:24} {int(t)//60}:{int(t)%60:02d}   {dur:3d}")
        t += dur

    # concatenar con cruce: la voz no se apaga NUNCA entre tramos
    c = int(CRUCE * SR)
    total = sum(len(p) for p in piezas) - c * (len(piezas) - 1)
    y = np.zeros((total, 2))
    pos = 0
    for i, p in enumerate(piezas):
        if i:
            r = np.linspace(0, 1, c)[:, None]
            y[pos:pos + c] = y[pos:pos + c] * (1 - r) + p[:c] * r
            y[pos + c:pos + len(p)] = p[c:]
        else:
            y[:len(p)] = p
        pos += len(p) - c

    y = fades(y, 3.0)
    y = y / np.abs(y).max() * 10 ** (-6.0 / 20)
    ruta = os.path.join(salida, "00_PROGRESION.wav")
    wavfile.write(ruta, SR, (y * 32767).astype(np.int16))
    print(f"\n  -> {os.path.relpath(ruta, RAIZ)}   {len(y)/SR/60:.2f} min")

    # verificar que no haya huecos: el bug de la version con bucle
    n = len(y) // SR * SR
    e = np.abs(y[:n]).mean(axis=1).reshape(-1, SR).mean(axis=1)
    mudos = int((e < e.max() * 0.02).sum())
    print(f"  segundos mudos: {mudos}   (la version con bucle tenia 4 cada 39 s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
