#!/usr/bin/env python3
"""La grilla del lab: tempo, escala, estructura. Todo lo demas se cuelga de aca.

DOS PRESTAMOS, UNO DE CADA LADO

1. LA ESTRUCTURA es la de "No Pussy Blues" (Grinderman, 2007): un solo riff, un
   solo acorde, y la pieza no MODULA sino que se CARGA. Cada vuelta suma una capa
   y sube el ruido, la armonia no se mueve nunca, y lo que cambia es la presion.
   Al final revienta y despues queda el riff pelado. Es lo contrario de una
   cancion con puente: aca no hay a donde ir, y esa es la idea.

2. LA ARMONIA es la de "Blackstar" (Bowie, 2016): pedal fijo abajo y arriba una
   escala con la segunda bemol y la tercera mayor. Esa combinacion (frigio
   dominante) es la que da el color medio-oriental del tema. Bowie la sostiene
   sobre un bajo que no se mueve, que es justo lo que necesita un tema de un solo
   acorde para no aburrir: el movimiento pasa en el timbre, no en los acordes.

Traducido: mi frigio dominante = mi fa sol# la si do re. El choque esta entre el
fa (b2) y el sol# (3): un semitono y medio, el intervalo que hace que suene a
Blackstar y no a rock en mi menor.

TEMPO

96 negras por minuto. Es el punto donde el mismo patron se puede leer como stomp
lento o como base rapida si se subdivide en semicorcheas, y el tema usa las dos
lecturas: la bateria arranca en negras y termina en 16avos sin cambiar el tempo.
"""
import numpy as np

from aem.core import SR

# ------------------------------------------------------------------- la grilla
BPM = 96.0
PULSO = 60.0 / BPM          # 0,625 s la negra
COMPAS = 4 * PULSO          # 2,5 s el compas de 4/4
CICLO = 2 * COMPAS          # 5,0 s el riff, que dura dos compases
COMPASES = 84
DUR = COMPASES * COMPAS     # 210 s = 3:30

SEMILLA = 24                # el hexagrama del proyecto, como en thermal_mass

# ------------------------------------------------------------------- la escala
# Mi2. Registro de bajo electrico: es donde vive el riff de Grinderman.
RAIZ_HZ = 82.407

# Frigio dominante. El b2 y la 3 mayor a la vez son el sonido.
GRADOS = {'1': 0, 'b2': 1, '3': 4, '4': 5, '5': 7, 'b6': 8, 'b7': 10}


def hz(grado, octava=0):
    """Frecuencia de un grado de la escala. `octava` 0 es Mi2 (82,4 Hz)."""
    return RAIZ_HZ * 2.0 ** (octava + GRADOS[grado] / 12.0)


# --------------------------------------------------------------- la estructura
# En compases. La carga es lineal: cada ciclo dura 16 compases y suma una capa.
SECCIONES = {
    'intro':     (0, 8),     # 0:00  el riff solo, sin bateria
    'ciclo_1':   (8, 24),    # 0:20  entra el pulso de abajo y el golpe
    'ciclo_2':   (24, 40),   # 0:60  entra el pad y la voz que hace de saxo
    'ciclo_3':   (40, 56),   # 1:40  el ruido empieza a comerse el aire
    'explosion': (56, 68),   # 2:20  revienta
    'derrumbe':  (68, 80),   # 2:50  se cae todo menos el riff
    'cola':      (80, 84),   # 3:20  el ultimo acople
}


def seg(compas, pulso=0.0):
    """Compas (base 0) y pulso dentro del compas, a segundos."""
    return compas * COMPAS + pulso * PULSO


def tramo(nombre):
    """(inicio, fin) de una seccion, en segundos."""
    ini, fin = SECCIONES[nombre]
    return seg(ini), seg(fin)


def compases_de(nombre):
    """Los tiempos de arranque de cada compas de una seccion, en segundos."""
    ini, fin = SECCIONES[nombre]
    return [seg(c) for c in range(ini, fin)]


def ciclos_de(*nombres):
    """Los arranques de cada vuelta del riff (2 compases) en varias secciones."""
    fuera = []
    for nombre in nombres:
        ini, fin = SECCIONES[nombre]
        fuera += [seg(c) for c in range(ini, fin, 2)]
    return fuera


# ----------------------------------------------------------------- utilidades
def lienzo(dur=DUR):
    """Un buffer mono vacio del largo del tema."""
    return np.zeros(int(dur * SR))


def colocar(destino, t_s, audio):
    """Suma `audio` en el segundo `t_s` del buffer. Recorta si se pasa del final."""
    i = int(t_s * SR)
    if i >= len(destino) or i + len(audio) <= 0:
        return destino
    j = min(i + len(audio), len(destino))
    destino[i:j] += audio[:j - i]
    return destino


def db(puntos):
    """Convierte [(segundo, dB), ...] a los pares lineales que espera
    `effects.amp_envelope`. Se escriben en dB porque la automatizacion se piensa
    en dB: -6 es la mitad de fuerte, y en lineal ese numero no dice nada.

    -80 dB se toma como silencio exacto para poder abrir y cerrar sin cola.
    """
    return [(t, 0.0 if v <= -80 else 10.0 ** (v / 20.0)) for t, v in puntos]
