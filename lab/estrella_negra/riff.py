#!/usr/bin/env python3
"""EL RIFF: el motor. Frigio dominante, barroso, y con un solo filtro para todo.

VEREDICTOS, EN ORDEN

- v1: "de plastico, cada tecla igual, conconcon". Se generaba UNA vuelta y se
  copiaba 42 veces.
- v2: "una verga". La variacion estaba arreglada pero la direccion era la
  opuesta a la pedida: mas notas, mas brillo, mas definicion.
- v3: "hace tic tic" y "un riff de mi mi mi, ponele onda". Dos cosas distintas:
  una rotura y una correccion de mas.

EL TIC ERA UN BUG MIO, Y ESTE ES

En la v2 agregue un desplazamiento de fase al azar por nota (para que dos notas
iguales no dieran las mismas muestras) y lo implemente **cortando el principio de
la nota YA con la envolvente aplicada**. O sea que la rampa de ataque quedaba en
el pedazo que se tiraba, y la nota arrancaba de golpe en el 25% de su pico. Eso es
un escalon, y un escalon es un click.

Ahora el desfase se le aplica **al oscilador solo**, y las envolventes se calculan
sobre el largo final. Cada nota arranca en cero, medido.

UN SOLO FILTRO PARA TODO EL TEMA

El cambio grande de esta version. Antes cada nota pasaba por su propia escalera
Moog: 430 llamadas, 70 segundos de render, y ademas es **falso**, porque un Moog
es monofonico y tiene UN filtro para todo lo que toca. Ahora se suman todos los
osciladores en un buffer, se arma el corte muestra por muestra (cada nota levanta
el corte con su envolvente, y si dos se pisan gana la mas nueva) y se hace **una
sola pasada de escalera sobre los tres minutos y medio**.

Sale mas rapido, suena mas parecido a un instrumento real, y las notas que se
pisan comparten filtro, que es justo lo que emborrona.

La envolvente de amplitud va ANTES del filtro y no despues. En un Moog el orden es
oscilador, filtro, amplificador, pero al mezclarlo antes se gana algo que sirve:
una nota floja entra mas despacio a la escalera, la satura menos y sale mas
oscura sola. La velocidad maneja el brillo sin una linea de codigo extra.

QUE ENTRA MAS FILTRADO

La apertura del filtro es una curva sobre todo el tema, no tres escalones. Arranca
en 0,14 (corte maximo ~200 Hz sobre un mi de 82: pasan dos armonicos) y llega a
1,02 en la explosion (~1500 Hz). Ese recorrido es el arco del tema.

LA FRASE

    mi  fa  mi  ·  sol#  mi  ||  mi  fa  mi  ·  re  do  si

La celda es **mi fa mi**: el apoyo en la segunda bemol, que es LA marca del frigio.
El sol# es la tercera mayor, y las dos juntas (b2 y 3) son el modo que usa Bowie.
El segundo compas baja re do si, o sea b7 b6 5, y el si devuelve al mi por
dominante. Seis alturas, una celda que vuelve, y nada de escalas paseando.
"""
import numpy as np

from aem import Track
from aem.core import SR
from aem.effects import amp_envelope, eco, hpf, lpf, tape_warm
from aem.synths import adsr, cuadrada, deriva, ladder_moog, sierra

from humano import Mano, aire, wow_flutter
from musica import CICLO, DUR, PULSO, SEMILLA, ciclos_de, colocar, db, hz, lienzo

# (pulso, grado, octava, largo en pulsos, nivel)
PATRON = [
    (0.00, '1',  0, 1.00, 1.00),   # mi, el acento
    (0.75, 'b2', 0, 0.40, 0.62),   # fa: el apoyo frigio
    (1.00, '1',  0, 0.85, 0.82),
    (2.00, '1',  0, 0.35, 0.28),   # fantasma
    (2.50, '3',  0, 0.90, 0.78),   # sol#: la tercera mayor
    (3.50, '1',  0, 0.55, 0.55),
    (4.00, '1',  0, 1.00, 0.98),
    (4.75, 'b2', 0, 0.40, 0.62),
    (5.00, '1',  0, 0.85, 0.80),
    (6.00, 'b7', -1, 0.70, 0.72),  # re
    (6.75, 'b6', -1, 0.35, 0.55),  # do
    (7.00, '5', -1, 1.30, 0.82),   # si: dominante, devuelve al mi
]

# (segundo, apertura). Multiplica la envolvente de corte. 0,14 es "a traves de
# una pared", 1,0 es el amplificador abierto
APERTURA = [(0, 0.14), (18, 0.15), (22, 0.19), (58, 0.20),
            (62, 0.29), (98, 0.32), (102, 0.44), (138, 0.48),
            (142, 1.02), (170, 1.02), (174, 0.34), (198, 0.26), (210, 0.16)]

# (segundo, empuje). Cuanto se le mete a la escalera. Es el drive, pero por nivel
# de entrada y no por parametro: la escalera tiene UNA perilla para todo el tema
EMPUJE = [(0, 0.55), (58, 0.60), (98, 0.75), (138, 0.85),
          (142, 1.35), (170, 1.35), (174, 0.7), (210, 0.5)]

CORTE_BASE = 60.0    # el piso: entre nota y nota el filtro queda cerrado
CORTE_ENV = 1200.0   # lo que abre una nota a nivel 1,0, antes de la apertura
RESONANCIA = 0.50    # baja a proposito: resonancia es definicion
DRIVE = 40.0
SUB = 0.55           # la cuadrada de abajo
ARMONICOS = 32
FIZZ = 0.045         # ruido dentro de la envolvente: el cono del parlante


def _curva(puntos, n):
    """[(segundo, valor)] a un valor por muestra."""
    t = np.arange(n) / SR
    return np.interp(t, [p[0] for p in puntos], [p[1] for p in puntos])


def _oscilador(freq, n, mano):
    """Las tres ondas de una nota, con desfase al azar y deriva.

    El desfase se saca ACA, generando de mas y recortando el oscilador crudo. Si
    se recorta despues de la envolvente se pierde el ataque y eso hace el tic.
    """
    salto = int(mano.entre(0, 1) * SR / max(freq, 20.0))
    m = n + salto
    t = (np.arange(m) - salto) / SR
    f = freq * (1.0 + 0.010 * np.exp(-np.maximum(t, 0) * 45)) * deriva(
        m, 3.0, periodo_s=mano.entre(1.3, 2.4), semilla=mano.rng.randint(9999))
    x = (sierra(f * 2 ** (+7 / 1200), armonicos=ARMONICOS) * 0.5
         + sierra(f * 2 ** (-7 / 1200), armonicos=ARMONICOS) * 0.5
         + cuadrada(f / 2, armonicos=24) * SUB)
    return (x / (np.abs(x).max() or 1.0))[salto:]


def _construir(mano, arranques, n_total, empuje):
    """Suma los osciladores de todas las vueltas y arma el corte muestra a muestra.

    Devuelve (osc, corte_relativo). El corte todavia no tiene ni base ni apertura:
    eso se aplica una vez, afuera.
    """
    osc = np.zeros(n_total)
    corte = np.zeros(n_total)

    for t0 in arranques:
        for pulso, grado, octava, largo, nivel in PATRON:
            nivel = min(mano.pct(nivel, 0.16), 1.0)
            dur_s = largo * PULSO
            n = int((dur_s + 0.30) * SR)          # cola larga: es la que emborrona
            i = int(max(t0 + pulso * PULSO + mano.ms(11), 0) * SR)
            if i >= n_total:
                continue
            fantasma = nivel < 0.25

            x = _oscilador(hz(grado, octava), n, mano)
            ataque = mano.pct(0.006, 0.5)
            env_a = adsr(n, ataque * 1.5, mano.pct(0.12, 0.3),
                         0.22 if fantasma else 0.55,
                         dur_s * mano.pct(0.95, 0.2), curva=1.1)
            # el fizz vive DENTRO de la envolvente y entra al filtro con la nota
            x = x * env_a + mano.rng.standard_normal(n) * env_a * FIZZ
            x[:int(0.03 * SR)] += aire(0.03, centro=mano.pct(420, 0.25),
                                       amp=(0.05 if fantasma else 0.03),
                                       semilla=mano.rng.randint(9999))[:n]

            j = min(i + n, n_total)
            # la envolvente pre filtro es lo que hace que una nota floja sature
            # menos y salga mas oscura, sin ninguna linea extra
            osc[i:j] += x[:j - i] * nivel * empuje[i]

            env_f = adsr(n, ataque, mano.pct(0.14, 0.3), 0.14 if fantasma else 0.30,
                         dur_s * mano.pct(0.8, 0.25), curva=1.2)
            # si dos notas se pisan gana la mas nueva, como un mono con retrigger
            np.maximum(corte[i:j], (env_f[:j - i] ** 1.4) * (0.5 + 0.8 * nivel),
                       out=corte[i:j])
    return osc, corte


def _filtrar(osc, corte_rel, apertura):
    """La unica pasada de escalera. `oversample=1` a proposito: con el corte donde
    esta (200 a 1500 Hz) los productos de la no linealidad son de orden bajo y no
    llegan a Nyquist, asi que el sobremuestreo del paper no compra nada y cuesta el
    doble. Verificado con `scripts/qa_scan_spectral.py` sobre la mezcla."""
    return ladder_moog(osc, CORTE_BASE + CORTE_ENV * corte_rel * apertura,
                       resonancia=RESONANCIA, drive=DRIVE, oversample=1)


def vuelta(mano, apertura=0.45):
    """Una vuelta sola, filtrada. La usa `grano.py` como fuente."""
    n = int((CICLO + 1.0) * SR)
    osc, corte = _construir(mano, [0.0], n, np.full(n, 1.0))
    return _filtrar(osc, corte, apertura)


def pista(comp):
    """Todo el tema en un buffer y una sola pasada de filtro."""
    mano = Mano(SEMILLA)
    n = int(DUR * SR)

    osc, corte = _construir(mano, ciclos_de('intro', 'ciclo_1', 'ciclo_2', 'ciclo_3',
                                            'explosion', 'derrumbe', 'cola'),
                            n, _curva(EMPUJE, n))
    fuera = lienzo(DUR)
    colocar(fuera, 0, _filtrar(osc, corte, _curva(APERTURA, n)))

    tr = Track('riff', gain=0.80, pan=0.0, color='#C98A3C')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 42))                      # deja el sotano para el bajo
    tr.fx(lambda a: tape_warm(a, drive=2.2))         # la segunda etapa de mugre
    tr.fx(lambda a: lpf(a, 3000))                    # techo: nada asoma arriba
    tr.fx(lambda a: wow_flutter(a, wow_ms=1.2, flutter_ms=0.08, semilla=SEMILLA))
    tr.fx(lambda a: eco(a, PULSO * 0.75, realim=0.20, mezcla=0.14, lp_hz=900))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -7), (18, -7),            # intro: entra pero sin mandar
        (22, -3), (138, -3),          # los tres ciclos, plano a proposito
        (140, 0), (170, 0),           # explosion: recien aca el riff manda
        (172, -4), (200, -6),         # derrumbe
        (200.5, -9), (210, -30),      # cola
    ])))
    return comp.add_track(tr)
