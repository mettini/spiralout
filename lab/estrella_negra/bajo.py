#!/usr/bin/env python3
"""EL PULSO DE ABAJO: la nota que no se mueve nunca.

Mitad Blackstar. En el tema de Bowie el fondo es un pedal grave que se repite y
NO acompana la melodia: esta ahi para que todo lo de arriba se lea como tension
contra algo fijo. Sin ese pedal, el frigio dominante suena a escala; con el
pedal, suena a amenaza.

Aca es Mi1 (41,2 Hz), una octava debajo del riff. Un golpe por compas, y a partir
del ciclo 3 se agrega el contragolpe del pulso 3,5, que es lo que empieza a
apurar el tema sin tocar el tempo.

POR QUE SENO Y NO SIERRA

A 41 Hz una sierra mete armonicos en toda la banda del riff y se pelean. El seno
deja la banda libre. El poco cuerpo que necesita para escucharse en un parlante
chico sale de un pulso a la octava, MUY abajo en nivel: es el mismo truco que un
amplificador de bajo con el canal de distorsion en paralelo.
"""
import numpy as np

from aem import Track
from aem.core import SR
from aem.effects import amp_envelope, hpf, lfo_amp
from aem.synth import sine
from aem.synths import adsr, pulso

from humano import Mano, wow_flutter
from musica import COMPAS, DUR, PULSO, SEMILLA, colocar, compases_de, db, hz, lienzo

LARGO_S = COMPAS * 0.85       # la nota casi llena el compas y deja respirar


def golpe(mano, freq=None, dur=LARGO_S, cuerpo=0.22, nivel=1.0):
    """Un golpe del pedal: seno con ataque suave y un pulso a la octava arriba.

    Igual que en el riff, nada se repite exacto: afinacion, largo, ancho de pulso y
    ataque se sortean por golpe. En una nota grave y larga la variacion de
    afinacion tiene que ser CHICA (2 cents): mas que eso, sobre un pedal que suena
    todo el tema, se escucha como que el tema desafina.
    """
    freq = (freq if freq is not None else hz('1', -1)) * mano.cents(2)
    dur = mano.pct(dur, 0.08)
    n = int(dur * SR)
    x = sine(freq, dur)[:n]
    # el cuerpo: octava arriba con el ancho de pulso movido por golpe, dosificado
    # por nivel y no por EQ (a este nivel sus armonicos quedan debajo del riff)
    x = x + pulso(np.full(n, freq * 2), mano.pct(0.35, 0.25))[:n] * mano.pct(cuerpo, 0.3)
    env = adsr(n, mano.pct(0.012, 0.4), mano.pct(0.35, 0.2), mano.pct(0.45, 0.15),
               dur * 0.55, curva=1.3)
    return x * env * nivel


def pista(comp):
    """El pedal, compas por compas."""
    mano = Mano(SEMILLA + 1)
    fuera = lienzo(DUR)

    for seccion in ('ciclo_1', 'ciclo_2', 'ciclo_3', 'explosion', 'derrumbe'):
        contragolpe = seccion in ('ciclo_3', 'explosion')
        for t in compases_de(seccion):
            colocar(fuera, t + mano.ms(8), golpe(mano, nivel=mano.entre(0.85, 1.0)))
            if contragolpe:
                colocar(fuera, t + 3.5 * PULSO + mano.ms(12),
                        golpe(mano, dur=PULSO * 0.9, nivel=mano.entre(0.55, 0.78)))

    # en la explosion el pedal baja al b7 cada dos compases: es la unica vez en
    # todo el tema que la nota de abajo se mueve, y por eso se siente
    for i, t in enumerate(compases_de('explosion')):
        if i % 2 == 1:
            colocar(fuera, t + mano.ms(8),
                    golpe(mano, hz('b7', -2), dur=COMPAS * 0.6, nivel=0.8))

    # 0,32 y no 0,55: a 41 Hz un seno tiene muchisima ENERGIA y poca sonoridad, asi
    # que un nivel que "se escucha bien" solo se come el headroom de todo lo demas.
    tr = Track('bajo', gain=0.40, pan=0.0, color='#4E8FA6')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 28))                    # saca el subsonico inaudible
    # wow bajito: en el pedal grave 1 ms ya son 2 cents, y de mas suena mareado
    tr.fx(lambda a: wow_flutter(a, wow_ms=0.7, flutter_ms=0.0, semilla=SEMILLA + 2))
    tr.fx(lambda a: lfo_amp(a, rate_hz=0.07, depth=0.10))   # respiracion lenta
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -80), (19.9, -80),
        (20, -6), (98, -6),           # ciclo 1 y 2: sostiene
        (100, -3), (138, -3),         # ciclo 3
        (140, 0), (170, 0),           # explosion
        (172, -8), (200, -20),        # derrumbe: se va antes que el riff
        (200, -80),
    ])))
    return comp.add_track(tr)
