#!/usr/bin/env python3
"""Arma el tema y exporta los seis stems por separado.

    python3.10 lab/estrella_negra/render.py

Salida:
    stems/*.wav             las seis pistas, al nivel que tienen en la mezcla
    stems/manifest.json     nivel, paneo y color de cada una
    mezcla_referencia.wav   la suma, SIN masterizar. Es referencia, no entrega

Los seis stems estan normalizados con el MISMO factor (el del mix completo), asi
que se pueden sumar en cualquier reproductor y da practicamente la mezcla: cada
uno viene al volumen que le toca. Escucharlos sueltos sirve para decidir que
sobra y que falta antes de tocar la mezcla.

El orden en que se agregan define el orden en que aparecen en el manifest y en la
pagina de escucha, y esta puesto de abajo hacia arriba: primero lo que sostiene,
al final lo que asoma.
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, 'framework'))

from aem import Composition                                      # noqa: E402
from aem.core import SR                                          # noqa: E402

import bajo, bateria, grano, lead, pad, riff, ruido              # noqa: E402,E401
from musica import BPM, COMPASES, DUR, SECCIONES, seg            # noqa: E402

# de abajo hacia arriba: primero lo que sostiene, al final lo que asoma
CAPAS = (riff, bajo, bateria, pad, lead, ruido, grano)

SALIDA_STEMS = os.path.join(AQUI, 'stems')
SALIDA_MEZCLA = os.path.join(AQUI, 'mezcla_referencia.wav')


def mapa():
    """Imprime la estructura en tiempos reales, para leer mientras se escucha."""
    print(f'\n  {BPM:.0f} BPM · {COMPASES} compases · {DUR:.0f} s\n')
    for nombre, (ini, fin) in SECCIONES.items():
        t = seg(ini)
        print(f'  {int(t // 60)}:{int(t % 60):02d}  {nombre:10s} '
              f'{fin - ini:2d} compases')
    print()


def medir(nombre, mono):
    """LUFS, pico y factor de cresta. El crest es el que dice si algo pega o
    acompana: 12-14 dB es una cama, arriba de 18 es un golpe."""
    pico = np.max(np.abs(mono)) or 1e-9
    rms = np.sqrt(np.mean(mono ** 2)) or 1e-9
    linea = (f'  {nombre:10s} pico {20 * np.log10(pico):6.1f} dB   '
             f'crest {20 * np.log10(pico / rms):5.1f} dB')
    try:
        import pyloudnorm as pyln
        lufs = pyln.Meter(SR).integrated_loudness(mono)
        linea += f'   LUFS {lufs:6.1f}'
    except Exception:
        pass
    print(linea)


def main():
    mapa()

    comp = Composition(DUR, name='estrella_negra')
    for capa in CAPAS:
        print(f'  generando {capa.__name__}…')
        capa.pista(comp)

    print()
    comp.list_tracks()
    print()

    comp.export_stems(SALIDA_STEMS)
    comp.export_wav(SALIDA_MEZCLA)

    print('\n  medicion por pista (pre normalizacion del mix):')
    for tr in comp.tracks:
        medir(tr.name, tr.render_mono(DUR))
    print()


if __name__ == '__main__':
    main()
