#!/usr/bin/env python3
"""QA de empalmes: busca artefactos PERIODICOS de nivel en un WAV.

    python3.10 scripts/qa_scan_empalmes.py master.wav [--desde 0] [--hasta 671]

POR QUE EXISTE

Una capa que repite un motivo (el moog de `bj3 n pt` lo hace cada 39 s) deja un
empalme en cada repeticion. Si la envolvente no cierra bien, ahi queda un corte seco.
El user lo escucho cinco veces (8:09, 8:48, 9:27, 10:06, 10:46) y lo marco dos veces
en sesiones distintas antes de que lo encontraramos.

Lo que lo delata no es el tamano del salto, es que este ESPACIADO REGULAR. Un evento
musical cae donde cae; un artefacto de empalme cae cada N segundos exactos.

El metodo: se miden los saltos de nivel entre ventanas consecutivas, se toman los mas
grandes, y se busca si sus posiciones tienen una separacion repetida. Si aparece una
periodicidad, es un artefacto y no una decision.
"""
import argparse
import sys

import numpy as np
from scipy.io import wavfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav')
    ap.add_argument('--desde', type=float, default=0.0)
    ap.add_argument('--hasta', type=float, default=1e9)
    ap.add_argument('--ventana', type=float, default=0.25, help='resolucion en segundos')
    a = ap.parse_args()

    sr, x = wavfile.read(a.wav)
    x = x.astype(np.float64) / 32768.0
    if x.ndim == 2:
        x = x.mean(axis=1)
    ini, fin = int(a.desde * sr), min(len(x), int(a.hasta * sr))
    x = x[ini:fin]

    w = int(a.ventana * sr)
    n = len(x) // w
    e = np.abs(x[:n * w]).reshape(n, w).mean(axis=1)
    d = np.abs(np.diff(e))
    if not len(d):
        print('  audio muy corto')
        return 1

    # los saltos que se salen de la distribucion normal
    umbral = np.percentile(d, 99.0)
    picos = np.flatnonzero(d > umbral)
    print(f'=== QA empalmes: {a.wav.split("/")[-1]} ===')
    print(f'  ventana {a.ventana}s · {len(picos)} saltos por encima del percentil 99')

    if len(picos) < 4:
        print('  OK — muy pocos saltos para que haya periodicidad')
        return 0

    # buscar separaciones repetidas entre saltos
    seps = np.diff(picos) * a.ventana
    vals, cuentas = np.unique(np.round(seps, 1), return_counts=True)
    sospechosas = [(v, c) for v, c in zip(vals, cuentas) if c >= 3 and v >= 2.0]

    if not sospechosas:
        print('  OK — los saltos no estan espaciados regularmente')
        return 0

    print('  PERIODICIDAD DETECTADA (probable empalme de una capa que repite):')
    for v, c in sorted(sospechosas, key=lambda t: -t[1]):
        print(f'    cada {v:.1f}s, {c} veces')
    print('  momentos a escuchar:')
    for p in picos[:12]:
        t = a.desde + p * a.ventana
        print(f'    {int(t)//60}:{int(t)%60:02d}   salto {20*np.log10(1+d[p]/(e[p]+1e-9)):.1f} dB')
    return 1


if __name__ == '__main__':
    sys.exit(main())
