#!/usr/bin/env python3
"""EL PAD: el acorde mareado. La otra mitad Blackstar.

Es el acorde entero del modo apilado de una vez: mi sol# si re fa. En cifrado es
un Mi7 con novena bemol, y es EL acorde del frigio dominante. Bowie no lo toca
como acorde de piano: lo deja como una nube que respira y se desafina sola, asi
que el oido lo escucha como color y no como armonia.

TRES COSAS LO HACEN SONAR MAREADO, EN ORDEN DE IMPORTANCIA

1. Cada voz tiene su PROPIA deriva de afinacion (`aem/synths.deriva`), con
   periodos que no son multiplos entre si. Sin eso las voces mantienen su
   relacion de fase para siempre y el oido las funde en un organo digital.
2. El fa esta arriba de todo, a un semitono y medio del sol#. Ese choque puesto
   en el registro agudo es la firma del tema, y puesto abajo seria barro.
3. El techo del filtro se abre y se cierra cada 23 segundos, que es un periodo
   PRIMO respecto de los 5 segundos del riff: nunca caen juntos, asi que el pad
   nunca marca el compas.

EL FILTRO, HONESTAMENTE

No es un barrido de verdad: es un cruce entre dos pasa-bajos fijos (900 y 3000
Hz) manejado por un LFO. Suena a barrido y cuesta cien veces menos que correr la
escalera Moog sobre dos minutos de audio. Para un pad de fondo la diferencia no
se escucha; para el riff si, y por eso ahi si va la escalera.
"""
import numpy as np

from aem import Track
from aem.core import SR
from aem.effects import amp_envelope, hpf, lfo_amp, lpf, reverb
from aem.synths import deriva, sierra

from humano import wow_flutter
from musica import DUR, SEMILLA, colocar, db, hz, lienzo, tramo

# (grado, octava, nivel). El fa (b2) va arriba y bajo en nivel: es picante.
VOCES = [
    ('1',  1, 1.00),
    ('3',  1, 0.80),
    ('5',  1, 0.72),
    ('b7', 1, 0.60),
    ('b2', 2, 0.34),
]

ARMONICOS = 24        # de sobra para un pad: el resto lo come el filtro igual
DERIVA_CENTS = 7.0    # medido de oido: en 4 el pad queda quieto, en 12 desafina


def nube(dur):
    """El acorde entero, con una deriva y una respiracion distintas por voz."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    fuera = np.zeros(n)
    for i, (grado, octava, nivel) in enumerate(VOCES):
        f = hz(grado, octava) * deriva(n, DERIVA_CENTS, periodo_s=9.0 + 2.7 * i,
                                       semilla=SEMILLA + i)
        # cada voz sube y baja por su cuenta, con periodos que no son multiplos
        # entre si: si respiran juntas se escucha un acorde con tremolo, y si
        # respiran cada una por su lado se escucha un coro
        respira = 1.0 + 0.22 * np.sin(2 * np.pi * t / (13.0 + 4.3 * i) + i * 1.7)
        fuera += sierra(f, armonicos=ARMONICOS) * nivel * respira
    fuera /= np.abs(fuera).max() or 1.0

    # el techo que se abre y se cierra: cruce entre dos pasa-bajos fijos
    t = np.arange(n) / SR
    m = 0.5 + 0.5 * np.sin(2 * np.pi * t / 23.0)
    return lpf(fuera, 900) * (1 - m) + lpf(fuera, 4200) * m


def pista(comp):
    """El pad entra en el ciclo 2 y no se va hasta el derrumbe."""
    ini, _ = tramo('ciclo_2')
    _, fin = tramo('derrumbe')

    fuera = lienzo(DUR)
    colocar(fuera, ini, nube(fin - ini))

    tr = Track('pad', gain=0.50, pan=0.0, color='#7A5CB8')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 150))                   # el pad no toca el grave
    # el wow es mas profundo que en el resto: en una capa sostenida es donde mas
    # se nota que nada esta clavado, y es barato
    tr.fx(lambda a: wow_flutter(a, wow_ms=2.2, flutter_ms=0.0, semilla=SEMILLA + 4))
    tr.fx(lambda a: lfo_amp(a, rate_hz=0.055, depth=0.16))
    tr.fx(lambda a: reverb(a, decay=0.9, mix=0.34, pre_delay_ms=45))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -80), (59.9, -80),
        (60, -12), (98, -8),          # ciclo 2: aparece por abajo
        (100, -5), (138, -3),         # ciclo 3: gana lugar
        (140, -1), (170, -1),         # explosion
        (172, -6), (198, -24),        # derrumbe: es lo primero que se disuelve
        (200, -80),
    ])))
    return comp.add_track(tr)
