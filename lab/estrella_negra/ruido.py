#!/usr/bin/env python3
"""EL RUIDO: la capa que crece. Es la que cuenta la historia.

En "No Pussy Blues" la armonia no se mueve nunca y sin embargo el tema avanza.
Lo que avanza es esto: el ruido de fondo, el acople del amplificador, la basura
alrededor de las notas. Empieza como el cuarto donde estan tocando y termina
tapando a la banda.

Por eso esta pista es un stem aparte y no un efecto adentro de las otras: la
cantidad de ruido es una decision de arreglo, no de mezcla, y hay que poder
subirla y bajarla sola.

CUATRO MATERIALES

1. La sala: crujido continuo, bajisimo, de punta a punta. Es lo que hace que los
   silencios no suenen a archivo digital.
2. El acople: notas altas sostenidas afinadas en armonicos del mi (mi5, sol#5,
   si5). Afinadas a proposito: un acople desafinado suena a error, uno afinado
   suena a que el amplificador esta cantando la misma nota que el bajo.
3. Los cortes: rafagas cortas de banda angosta, cada vez mas seguidas.
4. El muro: en la explosion, drones desafinados y saturados a lo Sunn O))).

SOBRE LA REGLA DE FRITURA

El crujido de sala es ruido SOSTENIDO, o sea el caso exacto que la regla del
proyecto prohibe arriba de 800 Hz. Va filtrado en 800. El acople no es ruido: son
senos, y por eso puede vivir en 660 a 990 Hz sin ensuciar. Los cortes son
transitorios de 120 ms centrados en 700.
"""
import numpy as np

from aem import Track
from aem.effects import amp_envelope, hpf, lpf, reverb
from aem.instruments import feedback_squeal, glitch_burst, vinyl_crackle, wall_of_sound

from musica import COMPAS, DUR, SEMILLA, colocar, db, hz, lienzo, seg, tramo

# (compas de entrada, grado, octava, largo en compases, nivel)
# Cada acople entra al final de una vuelta y se solapa con la siguiente: es lo
# que hace que las secciones se pisen en vez de cortarse.
ACOPLES = [
    (22, '1',  3, 2.5, 0.20),
    (38, '5',  3, 3.0, 0.30),
    (46, '3',  3, 2.5, 0.34),
    (54, '1',  3, 3.5, 0.44),
    (57, '5',  3, 8.0, 0.50),      # el de la explosion, largo
    (62, 'b2', 3, 6.0, 0.44),      # el fa: el mas feo de todos, y va arriba
    (69, '1',  3, 9.0, 0.40),      # el derrumbe: queda el amplificador solo
    (80, '5',  2, 4.0, 0.26),      # la cola
]


def pista(comp):
    """Las cuatro capas de basura, cada una con su calendario."""
    rng = np.random.RandomState(SEMILLA)
    fuera = lienzo(DUR)

    # 1 · la sala, de punta a punta
    sala = lpf(vinyl_crackle(DUR, density=0.22, amp=0.16, base_hiss=0.035,
                             seed=SEMILLA), 800)
    fuera += sala

    # 2 · los acoples
    for compas, grado, octava, largo, nivel in ACOPLES:
        colocar(fuera, seg(compas),
                feedback_squeal(hz(grado, octava), largo * COMPAS,
                                sweep_depth=0.012, sweep_rate=0.23,
                                amp=nivel, decay_rate=0.28))

    # 3 · los cortes, cada vez mas seguidos
    for seccion, cada in (('ciclo_2', 2.0), ('ciclo_3', 1.0), ('explosion', 0.4)):
        ini, fin = tramo(seccion)
        t = ini
        while t < fin:
            colocar(fuera, t + rng.uniform(0, 0.25),
                    glitch_burst(dur=rng.uniform(0.07, 0.16), freq_center=700,
                                 bandwidth=0.5, amp=rng.uniform(0.15, 0.35)))
            t += cada * rng.uniform(0.7, 1.3)

    # 4 · el muro, solo en la explosion
    ini, fin = tramo('explosion')
    colocar(fuera, ini, wall_of_sound([hz('1', 0), hz('5', 0)], fin - ini,
                                      distortion=4.0, n_layers=4, amp=0.34))

    tr = Track('ruido', gain=0.34, pan=0.0, color='#7C7972')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 70))         # el muro no puede pisar el pedal grave
    tr.fx(lambda a: reverb(a, decay=1.0, mix=0.26, pre_delay_ms=30))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -20), (20, -18),          # la sala sola
        (60, -12),                    # ciclo 2
        (100, -7),                    # ciclo 3
        (140, 0), (170, 0),           # explosion
        (172, -4), (198, -10),        # derrumbe: el ruido dura mas que la banda
        (205, -14), (210, -26),
    ])))
    return comp.add_track(tr)
