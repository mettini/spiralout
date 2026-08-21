#!/usr/bin/env python3
"""EL GRANO: polvo, no chispas. Microsonido sobre el material del propio tema.

QUE SALIO MAL EN LA PRIMERA VERSION

El user dijo "estoy en una feria de circo gitana". Tenia razon y la causa es
identificable: **granos cortos, densos y transpuestos a la octava y a la
docena**. Esas tres cosas juntas son la receta de una calesita. La octava y la
quinta arriba, repetidas rapido, las escucha cualquiera como carillon, y no hay
filtro que lo arregle porque el problema es la afinacion de los granos.

QUE CAMBIO

1. **Una sola altura: el unisono.** Cero transposiciones. La nube hereda la
   afinacion del riff y no agrega ninguna nota que no este.
2. **Granos largos** (180 a 400 ms en vez de 28 a 120). Un grano largo es tonal y
   se funde; uno corto es un click con altura, y muchos clicks con altura afinados
   en octavas son, literalmente, una caja de musica.
3. **Densidad mucho mas baja** (5 a 45 granos por segundo en vez de 220). El
   enjambre se fue.
4. **Techo en 900 Hz.** Es polvo, tiene que vivir abajo con el resto.

Lo que queda es la sala del riff sin nadie tocando: mismo material, misma altura,
sin ritmo. La teoria esta en `docs/46_microsonido.md` y la maquina en
`aem/granular.nube`.
"""
from aem import Track
from aem.effects import amp_envelope, hpf, lpf, reverb
from aem.granular import nube

from humano import Mano, wow_flutter
from musica import DUR, SEMILLA, db, lienzo

# (segundo, granos por segundo). Sigue habiendo arco, pero adentro de un rango
# donde la nube nunca se vuelve un enjambre
DENSIDAD = [(0, 5), (20, 6), (60, 12), (100, 20), (140, 45), (170, 45),
            (172, 14), (190, 6), (210, 4)]

# (segundo, duracion del grano en ms). Todos largos: es lo que los funde
GRANO_MS = [(0, 380), (60, 320), (140, 180), (170, 220), (185, 400), (210, 420)]


def _fuente():
    """El material a granular: una vuelta del propio riff, ya embarrada."""
    import riff as riff_mod
    return riff_mod.vuelta(Mano(SEMILLA + 11), apertura=0.45)


def pista(comp):
    """Una sola nube, al unisono y oscura."""
    fuera = lienzo(DUR)
    fuera += nube(_fuente(), DUR, densidad=DENSIDAD, grano_ms=GRANO_MS,
                  var_grano=0.45, posicion=0.4, avance=0.012, dispersion_ms=1200,
                  alturas=(1.0,), dispersion_cents=6, semilla=SEMILLA)

    tr = Track('grano', gain=1.50, pan=0.10, color='#8FA37A')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 100))              # el grano no compite con el pedal
    tr.fx(lambda a: lpf(a, 900))              # y no asoma arriba: es polvo
    tr.fx(lambda a: wow_flutter(a, wow_ms=1.8, flutter_ms=0.0, semilla=SEMILLA + 9))
    tr.fx(lambda a: reverb(a, decay=1.0, mix=0.26, pre_delay_ms=25))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -80), (19, -80),
        (20, -24), (60, -18), (100, -12),
        (140, -6), (170, -6),
        (172, -12), (196, -20), (210, -30),
    ])))
    return comp.add_track(tr)
