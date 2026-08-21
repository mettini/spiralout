#!/usr/bin/env python3
"""LA VOZ: el lugar del saxo de Blackstar, tocado por un monosintetizador.

En el tema de Bowie la linea principal no la lleva un sintetizador sino un saxo,
y lo que hace que funcione no es el timbre sino DONDE entra: nunca sobre el
golpe, siempre despues, y siempre arrastrando la nota hacia la siguiente. Un
saxo no salta entre alturas, las liga.

Eso se puede copiar sin tener un saxo: alcanza con glide corto (0,28 s) y una
envolvente de amplitud que hincha y afloja a lo largo de toda la frase en vez de
por nota. `voz_moog` hace exactamente eso (una envolvente por frase, no por
nota), asi que la frase entera respira como un soplido.

LA FRASE

si  do  si  sol#  fa  mi

Baja por el modo y se para en el mi. El do es la b6 y el fa la b2: las dos notas
que en una escala menor comun no estarian, y son las que dan el color. La segunda
version corta la caida y se queda en el fa, sin resolver: es la misma frase
"preguntando", y se usa cuando el tema todavia no puede cerrar.

Registro: mi3 a do4. Arriba del riff (mi2) y adentro del pad, que es donde vive
un tenor.
"""
from aem import Track
from aem.effects import amp_envelope, eco, hpf, reverb
from aem.synths import voz_moog

from humano import Mano, aire, vibrato
from musica import DUR, PULSO, SEMILLA, colocar, db, hz, lienzo, seg

# (grado, octava, largo en pulsos). 16 pulsos = 4 compases.
FRASE = [('5', 1, 3.0), ('b6', 1, 1.0), ('5', 1, 2.0),
         ('3', 1, 2.0), ('b2', 1, 1.5), ('1', 1, 6.5)]

# La misma frase sin resolver: se queda colgada del fa.
PREGUNTA = [('5', 1, 3.0), ('b6', 1, 1.5), ('5', 1, 2.5),
            ('3', 1, 3.0), ('b2', 1, 6.0)]

TIMBRE = dict(glide_s=0.28, detune_cents=4.0, sub=0.25,
              corte_base=300.0, corte_barrido=3000.0, resonancia=0.55, drive=12.0,
              env_filtro=(0.35, 1.1, 0.50, 1.4), env_amp=(0.30, 0.9, 0.88, 1.6),
              deriva_cents=2.5, semilla=SEMILLA)


def frase(notas, mano, octava=0, scoop=True, **cambios):
    """Convierte una frase en audio. `octava` +1 la sube para gritar.

    Tres cosas la separan de una linea de sintetizador con la perilla puesta:

    1. **El scoop.** Un saxofonista no ataca la nota afinada: entra desde abajo y
       llega. Se hace agregando una nota fantasma un tono abajo al principio y
       dejando que el glide la resuelva.
    2. **El vibrato entra despues.** Nadie arranca vibrando. `humano.vibrato` lo
       hace crecer a lo largo de la frase.
    3. **El aire del ataque.** El soplido antes del tono.

    Y cada aparicion sortea afinacion, largos y semilla: la misma frase dos veces
    no da las mismas muestras.
    """
    hz_dur = []
    if scoop:
        grado, oct0, _ = notas[0]
        hz_dur.append((hz(grado, oct0 + octava) * 2 ** (-2 / 12), 0.16))
    for grado, oct0, largo in notas:
        hz_dur.append((hz(grado, oct0 + octava) * mano.cents(6),
                       largo * PULSO * mano.pct(1.0, 0.05)))

    timbre = {**TIMBRE, **cambios, 'semilla': mano.rng.randint(9999)}
    y = voz_moog(hz_dur, **timbre)
    y = vibrato(y, hz=mano.pct(5.4, 0.12), cents=mano.pct(22, 0.3), desde=0.30)

    soplo = aire(0.09, centro=mano.pct(2100, 0.2), amp=0.05,
                 semilla=mano.rng.randint(9999))
    y[:len(soplo)] += soplo[:len(y)]
    return y


def pista(comp):
    """Cuatro apariciones y un grito. La voz no toca nunca dos veces seguidas:
    entre frase y frase pasan al menos cuatro compases de riff solo."""
    mano = Mano(SEMILLA + 13)
    fuera = lienzo(DUR)

    # cada aparicion se genera de nuevo: las dos "normal" no son el mismo audio
    apariciones = [
        (26, PREGUNTA, {}),                              # ciclo 2, entra preguntando
        (34, FRASE, {}),                                 # ciclo 2, la frase entera
        (42, PREGUNTA, dict(corte_barrido=3300.0)),      # ciclo 3, mas abierta
        (50, FRASE, dict(resonancia=0.60)),
        (58, FRASE, dict(resonancia=0.68, drive=26.0, corte_barrido=3400.0)),
        (64, FRASE, dict(resonancia=0.70, drive=30.0, corte_barrido=3600.0)),
        (72, PREGUNTA, dict(corte_barrido=1500.0, drive=8.0)),   # apagada, al final
    ]
    for compas, notas, cambios in apariciones:
        octava = 1 if 56 <= compas < 68 else 0           # en la explosion, grita
        colocar(fuera, seg(compas) + mano.ms(35),
                frase(notas, mano, octava=octava, **cambios))

    tr = Track('lead', gain=0.46, pan=-0.12, color='#D6564B')
    tr.add(0, fuera)
    tr.fx(lambda a: hpf(a, 120))
    tr.fx(lambda a: eco(a, PULSO * 1.5, realim=0.30, mezcla=0.22, lp_hz=2400))
    tr.fx(lambda a: reverb(a, decay=1.0, mix=0.30, pre_delay_ms=60))
    tr.fx(lambda a: amp_envelope(a, db([
        (0, -3), (138, -3),
        (140, 0), (170, 0),           # en la explosion el grito va arriba de todo
        (172, -5), (200, -12),
    ])))
    return comp.add_track(tr)
