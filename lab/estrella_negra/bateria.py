#!/usr/bin/env python3
"""LA BATERIA. Veredicto del user sobre la version anterior: "suena de juguete".

POR QUE SONABA DE JUGUETE, Y NO ERA EL PATRON

Cada tambor era **una sola capa y nada mas**: el bombo un seno con barrido de
tono, la caja dos senos con ruido encima. Eso no es un tambor, es un tono con
envolvente, y el oido lo escucha como lo que es. Un tambor de verdad son tres
cosas sonando juntas, en tres escalas de tiempo distintas:

1. **El golpe** (5 a 15 ms): el palo o el pie contra el parche. Ruido de banda,
   cortisimo. Es el que dice DE QUE esta hecho el tambor y con que se lo pego.
2. **El cuerpo** (50 a 200 ms): el parche vibrando. Tono con barrido.
3. **La cola** (200 ms a 1 s): la caja de resonancia y las bordonas.

Sin la capa 1 todo suena a sintetizador. Sin la capa 3 suena a muestra recortada.

Y LO OTRO QUE FALTABA: EL CUARTO

No habia una sola reflexion en toda la pista. Una bateria grabada NUNCA esta
seca: hay un cuarto alrededor y la mitad de lo que se escucha es eso. Va camara
corta con pre-delay de 18 ms, que a 343 m/s son unos 3 metros de pared.

Y saturacion de bus, que es lo que pega las tres capas y las hace sonar como un
solo golpe en vez de tres cosas apiladas.

TODO OSCURO A PROPOSITO

El golpe del bombo va en 300 a 900 Hz y el de la caja en 400 a 1400, no en 3
kHz. En un tema que arriba de 2 kHz no tiene nada (no hay platillos), un click
brillante seria lo unico que asoma y sonaria pegado.

NO HAY PLATILLOS

El user bajo la pista entera. El kit no tiene un solo metal, y por lo tanto no
hay nada marcando la subdivision: eso lo tienen que hacer las cajas fantasma.
"""
import numpy as np

from aem import Track
from aem.core import SR
from aem.effects import amp_envelope, distort, hpf, lpf, reverb
from aem.synth import sine

from humano import Mano, wow_flutter
from musica import PULSO, DUR, SEMILLA, colocar, compases_de, db, lienzo

PATRONES = {
    'ciclo_1':   dict(bombo=[0.0, 2.5], caja=[2.0], piso=[], fantasma=0.22),
    'ciclo_2':   dict(bombo=[0.0, 2.5, 3.75], caja=[2.0], piso=[], fantasma=0.34),
    'ciclo_3':   dict(bombo=[0.0, 1.75, 2.5], caja=[2.0], piso=[3.5], fantasma=0.42),
    'explosion': dict(bombo=[0.0, 1.0, 2.0, 3.0], caja=[1.0, 3.0], piso=[3.5],
                      fantasma=0.34),
    'derrumbe':  dict(bombo=[0.0], caja=[], piso=[], fantasma=0.0),
}


def _ruido(mano, dur, lo, hi, caida):
    """Ruido de banda con decaimiento exponencial. La materia prima del golpe y
    de las bordonas: lo mismo con distinto largo."""
    n = max(int(dur * SR), 8)
    x = lpf(hpf(mano.rng.standard_normal(n), lo), hi)
    return x * np.exp(-np.arange(n) / SR * caida)


def bombo(mano, nivel=0.9):
    """Tres capas: sub, cuerpo y pie contra el parche."""
    dur = mano.pct(0.85, 0.12)
    n = int(dur * SR)
    t = np.arange(n) / SR

    # sub: el peso. Barrido lento y cola larga
    f_sub = mano.pct(38, 0.05) + mano.pct(26, 0.15) * np.exp(-t * 26)
    sub = np.sin(2 * np.pi * np.cumsum(f_sub) / SR) * np.exp(-t * mano.pct(3.6, 0.2))

    # cuerpo: el parche. Barrido rapido, decaimiento rapido
    f_cpo = mano.pct(84, 0.06) + mano.pct(60, 0.2) * np.exp(-t * 90)
    cuerpo = np.sin(2 * np.pi * np.cumsum(f_cpo) / SR) * np.exp(-t * mano.pct(13, 0.2))

    y = sub * 0.85 + cuerpo * 0.45
    y[:int(0.014 * SR)] += _ruido(mano, 0.014, 300, 900, 260)[:int(0.014 * SR)] * 0.35
    y[:24] *= np.linspace(0, 1, 24)          # que arranque en cero, siempre
    return nivel * np.tanh(y * 1.8) / 1.2


def caja(mano, nivel=0.7):
    """Tono, bordonas y golpe. La cola de bordonas es la que la saca de juguete."""
    dur = mano.pct(0.34, 0.15)
    n = int(dur * SR)
    t = np.arange(n) / SR

    tono = (sine(mano.pct(178, 0.05), dur)[:n] * np.exp(-t * mano.pct(28, 0.2))
            + sine(mano.pct(236, 0.05), dur)[:n] * np.exp(-t * mano.pct(38, 0.2)) * 0.6)
    bordonas = _ruido(mano, dur, 200, mano.pct(1400, 0.15), mano.pct(9.0, 0.25))
    golpe = _ruido(mano, 0.01, 400, 1400, 320)

    y = tono * 0.5 + bordonas[:n] * 0.75
    y[:len(golpe)] += golpe * 0.5
    y[:16] *= np.linspace(0, 1, 16)
    return nivel * np.tanh(y * 1.6) / (np.abs(np.tanh(y * 1.6)).max() or 1.0)


def piso(mano, nivel=0.75, alto=False):
    """Tambor de piso. Mismo esquema que el bombo, mas arriba y mas largo."""
    dur = mano.pct(0.7, 0.15)
    n = int(dur * SR)
    t = np.arange(n) / SR
    base = mano.pct(150 if alto else 104, 0.05)
    f = base + base * 0.45 * np.exp(-t * 40)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * mano.pct(5.5, 0.2))
    y[:int(0.012 * SR)] += _ruido(mano, 0.012, 300, 1100, 280)[:int(0.012 * SR)] * 0.3
    y[:24] *= np.linspace(0, 1, 24)
    return nivel * np.tanh(y * 1.5) / 1.2


def _relleno(mano, fuera, t0):
    """Bajada de toms en el ultimo compas de cada grupo de ocho."""
    for i, p in enumerate((0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)):
        t = t0 + p * PULSO + mano.ms(8)
        if i < 2:
            colocar(fuera, t, caja(mano, mano.entre(0.55, 0.75)))
        else:
            colocar(fuera, t, piso(mano, mano.entre(0.6, 0.9), alto=i < 5))
    colocar(fuera, t0 + 3.75 * PULSO, bombo(mano, 0.95))


def compas(patron, mano, fuera, t0):
    """Un compas: lo escrito, mas lo que se sortea."""
    for p in patron['bombo']:
        colocar(fuera, t0 + p * PULSO + mano.ms(10), bombo(mano, mano.entre(0.8, 0.98)))
        if mano.dado(0.12):
            colocar(fuera, t0 + (p + mano.entre(0.22, 0.3)) * PULSO,
                    bombo(mano, mano.entre(0.45, 0.62)))
    for p in patron['caja']:
        colocar(fuera, t0 + p * PULSO + mano.ms(12), caja(mano, mano.entre(0.65, 0.85)))
    for p in patron['piso']:
        colocar(fuera, t0 + p * PULSO + mano.ms(10), piso(mano, mano.entre(0.6, 0.85)))

    # las fantasma: sin platillos, son lo unico que marca la subdivision
    ocupado = {round(x, 2) for x in patron['bombo'] + patron['caja'] + patron['piso']}
    p = 0.0
    while p < 4.0:
        if round(p, 2) not in ocupado and mano.dado(patron['fantasma']):
            colocar(fuera, t0 + p * PULSO + mano.ms(14),
                    caja(mano, mano.entre(0.10, 0.22)))
        p += 0.25


def pista(comp):
    """Arma la bateria seccion por seccion, compas por compas."""
    mano = Mano(SEMILLA + 3)
    fuera = lienzo(DUR)

    for seccion, patron in PATRONES.items():
        for i, t0 in enumerate(compases_de(seccion)):
            if seccion == 'derrumbe':
                if i % (2 if i < 6 else 4):
                    continue
                colocar(fuera, t0 + mano.ms(14), bombo(mano, mano.entre(0.5, 0.85)))
                continue
            if i % 8 == 7:
                _relleno(mano, fuera, t0)
            else:
                compas(patron, mano, fuera, t0)

    tr = Track('bateria', gain=0.42, pan=-0.05, color='#DEDAD1')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 35))
    tr.fx(lambda a: distort(a, amount=1.6))     # pega las tres capas de cada golpe
    # el cuarto: 18 ms de pre-delay son unos 3 metros hasta la pared
    tr.fx(lambda a: reverb(a, decay=0.9, mix=0.17, pre_delay_ms=18))
    tr.fx(lambda a: lpf(a, 2600))               # el cuarto tambien va oscuro
    tr.fx(lambda a: wow_flutter(a, wow_ms=0.5, flutter_ms=0.04, semilla=SEMILLA + 5))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -6), (58, -6),
        (60, -3), (138, -2),
        (140, 0), (170, 0),
        (172, -6), (200, -30),
    ])))
    return comp.add_track(tr)
