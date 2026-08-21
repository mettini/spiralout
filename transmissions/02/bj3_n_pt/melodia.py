#!/usr/bin/env python3
"""La melodia del moog, armada con estructura de melodia y no como paseo al azar.

    python3.10 transmissions/02/bj3_n_pt/melodia.py

QUE ESTABA MAL, Y NO ERA EL SONIDO
--------------------------------------------------------------------------------
Las tres versiones anteriores fallaban por lo mismo: no habia una melodia, habia una
secuencia de alturas. Cuatro cosas concretas, cada una contra lo que dice la teoria de
composicion melodica:

1. **Ningun motivo se repetia.** En `PLAN_RONDA6.md` la regla escrita era "nunca se
   repite un par de notas consecutivas en toda la ventana". Eso es exactamente lo
   contrario: una melodia se reconoce porque un motivo VUELVE. Sin retorno no hay de
   que agarrarse, y suena a paseo al azar porque es un paseo al azar.
2. **Cero movimiento por grado conjunto.** Con solo Mi, Sol, Si y Re todo intervalo es
   una 3ra, 4ta o 5ta. La proporcion sana es ~80% de segundas y ~20% de saltos. Una
   linea hecha solo de saltos el oido la lee como arpegio del acorde, o sea armonia, no
   como melodia.
3. **Sin arco y sin pico.** No habia un punto alto: la linea deambulaba. El contorno de
   arco (sube al pico, el pico suena UNA sola vez, despues baja) es lo que da sensacion
   de recorrido y de cierre.
4. **Todas las notas con el mismo peso.** Faltaba el par antecedente / consecuente: una
   frase que pregunta y queda abierta, otra que responde y resuelve.

    Fuentes:
    Open Music Theory, "16th-Century Contrapuntal Style" (grados conjuntos, gap-fill:
      un salto grande se compensa con movimiento en direccion contraria)
      https://viva.pressbooks.pub/openmusictheory/chapter/16th-century-contrapuntal-style/
    Ableton, "Creating Melodies 1: Contour" (el arco, "lo que sube tiene que bajar")
      https://makingmusic.ableton.com/creating-melodies-1-contour
    EarMaster 2.3, "Melody" (motivo, frase, repeticion y variacion)
      https://www.earmaster.com/music-theory-online/ch02/chapter-2-3.html
    Attack Magazine, "Legato Synths: Glide, Slide & Portamento" (la articulacion mono:
      el glide solo actua entre notas que se solapan, y son ~80 ms, no segundos)
      https://www.attackmagazine.com/technique/passing-notes/legato-synths-glide-slide-portamento/

EL REGISTRO
--------------------------------------------------------------------------------
Abajo de ~150 Hz el oido no percibe melodia, percibe BAJO: sigue la funcion armonica y
no el contorno. La melodia vive donde se rastrean alturas, mas o menos de 200 a 800 Hz.
Las versiones anteriores estaban en 80 a 120 Hz, o sea territorio de fundamento.

LA ESTRUCTURA QUE SE USA ACA
--------------------------------------------------------------------------------
Nueve ENUNCIADOS agrupados en cuatro frases (A A' B A'') sobre los 200 s de la ventana.
Un enunciado es una pasada del motivo. El detalle esta en la tabla de `ENUNCIADOS`, y el
render imprime el mapa completo.

EL MOTIVO es `mi sol la sol fa# si`: contorno sube, sube, baja, baja, sube, con ritmo
largo · corto · corto · corto · corto · mas largo. Ese ritmo es lo que se reconoce cuando
vuelve, aunque cambien las alturas.

DOS ENUNCIADOS SEGUIDOS NUNCA COMPARTEN CONTORNO. Repetir la misma figura transpuesta es
una secuencia: valida una vez, pero encadenada dos veces se escucha como copia y no como
desarrollo. `verificar_contornos()` aborta el render si pasa.

EL RESPIRO ENTRE ENUNCIADOS NO ES FIJO. Va de 1,8 a 7,0 s segun donde este: corto adentro
de una frase, largo cruzando de frase a frase, el mas corto de todos justo despues del
pico (el gap-fill es un impulso, si se espera se pierde). Un respiro constante es lo que
suena mecanico.

EL PICO (Mi alto, 640 Hz) aparece UNA sola vez, al 51% de la ventana. Es la unica nota de
todo el moog que llega ahi arriba.

LA SEGUNDA VOZ no entra al principio: la linea principal tiene que quedar sola para poder
reconocerse. Se engancha a un enunciado por indice, no a un segundo fijo.

LA COLA. Los ultimos 9,5 s no tienen notas nuevas: son el aire donde la estela de la
ultima nota se disuelve. Sin eso el delay queda truncado por el largo del buffer y el
final se escucha como un corte, por mas que la nota siga sonando.
"""
import os
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "framework"))

from aem.effects import eco  # noqa: E402
from aem.synths import ladder_moog, pulso, sierra  # noqa: E402
from render import SR, camara, fades, hp, lp, mono_graves  # noqa: E402

FUND = 71.3               # el Re de la base del tema
OCTAVA = 4.0              # dos octavas arriba: la melodia va de 285 a 640 Hz
OCTAVA_2 = 2.0            # la segunda voz, respecto de la principal
GLIDE = 0.08              # 80 ms, el valor del Minimoog
ATAQUE_S = 1.9            # el ataque de cada frase SUBE, no golpea
VENTANA = 200.0           # lo que dura la ventana del moog en el tema
COLA = 9.5                # aire despues de la ultima nota, para que la estela respire

# La ESTELA. Delay realimentado con filtro en el lazo (`aem.effects.eco`): cada
# repeticion vuelve a pasar por el pasabajos y se va oscureciendo. Es lo que sigue
# sonando cuando el tono crudo ya se apago, y es lo que reemplaza al oscilador
# sostenido: una nota que RESUENA en vez de una nota que esta siendo mantenida.
ESTELA = dict(tiempo_s=2.9, realim=0.44, mezcla=0.45, lp_hz=1900)

# La escala completa de Mi menor natural sobre la base. Mi, Sol y Si son el motivo del
# disco (`docs/43`); Fa#, La y Do son las NOTAS DE PASO, y son las que permiten que
# exista movimiento por grado conjunto. El Do es ademas la nota que se sale del encierro
# de tres alturas, y es la que arma la tension del pico.
SEMI = {"re": 0, "mi": 2, "fa#": 4, "sol": 5, "la": 7, "si": 9, "do": 10,
        "re_a": 12, "mi_a": 14}
N = {k: FUND * 2 ** (s / 12) for k, s in SEMI.items()}

# LA LINEA, enunciado por enunciado.
#
# Cada nota es (nombre, duracion relativa, ligada_a_la_anterior):
#   ligada=True  -> legato: se solapa, glide de 80 ms, NO re-dispara la envolvente
#   ligada=False -> arranca enunciado, se re-dispara y el ataque SUBE (no golpea)
#
# EL MOTIVO tiene un GIRO: sube, sube, baja, baja, sube. No es una escala derecha para
# arriba. Una rampa es el contorno mas predecible que existe (el oido adivina la nota
# siguiente y se desengancha), y ademas el retroceso hace que la nota de llegada pese
# mas, porque se hizo esperar. Los saltos caen SIEMPRE al empezar enunciado; adentro se
# mueve por grado conjunto.
#
# Un enunciado es una pasada del motivo. La regla dura: **dos enunciados consecutivos
# nunca pueden tener el mismo contorno**. Repetir la misma figura transpuesta es una
# secuencia, que es una tecnica valida una vez, pero encadenada dos veces se escucha como
# copia y no como desarrollo. Cada enunciado varia por lo menos una cosa: el contorno, el
# largo, o de que parte del motivo sale.
#
# El chequeo esta abajo en `verificar_contornos()` y aborta el render si se rompe.
#
# EL RESPIRO NO ES FIJO. Tenerlo constante es lo que suena mecanico: la musica respira
# distinto segun donde este. La regla:
#
#   - entre enunciados de la MISMA frase: corto. La frase sigue, no terminó
#   - cruzando de frase a frase: largo. Es un limite estructural
#   - antes del pico: largo, la pausa acumula
#   - despues del pico: el mas corto de todos. El gap-fill tiene que caer encima, es un
#     impulso, si se espera se pierde
#   - antes del retorno del motivo: el mas largo. El retorno necesita aire para leerse
#     como retorno
#
# (frase, que variacion es, silencio ANTES, notas)
ENUNCIADOS = [
    ("A", "el motivo", 0.0, [
        ("mi",  6.0, False), ("sol", 2.8, True), ("la",  2.8, True),
        ("sol", 2.2, True), ("fa#", 2.2, True), ("si",  5.5, True)]),
    ("A", "contorno cambiado", 2.8, [           # NO es el motivo transpuesto
        ("sol", 5.0, False), ("la",  2.5, True), ("sol", 2.2, True),
        ("la",  2.2, True), ("si",  5.0, True)]),                  # cierra abierto en Si
    ("A'", "inversion", 6.0, [                  # el contorno espejado, y el salto tambien
        ("si",  5.5, False), ("sol", 2.8, True), ("fa#", 2.4, True),
        ("sol", 2.2, True), ("la",  2.2, True), ("mi",  6.0, True)]),   # resuelve en Mi
    ("A'", "fragmento", 2.5, [                  # solo un pedazo del motivo, mas corto
        ("mi",  4.5, False), ("fa#", 2.5, True), ("mi",  2.5, True),
        ("sol", 6.0, True)]),
    ("B", "al pico", 5.5, [                     # el unico Do y el unico Mi alto
        # el Si intercalado es un retroceso de 3ra justo antes del pico: hace que el
        # pico pegue mas fuerte de lo que pegaria llegando derecho
        ("si",  5.0, False), ("do",  3.0, True), ("re_a", 2.5, True),
        ("si",  2.2, True), ("mi_a", 6.5, True)]),
    ("B", "gap-fill", 1.8, [                    # llena el hueco que dejo la caida
        ("la",  4.5, False), ("sol", 2.8, True), ("la",  2.2, True),
        ("fa#", 5.0, True)]),
    ("B", "puente", 4.0, [
        ("si",  4.5, False), ("la",  2.5, True), ("sol", 2.5, True),
        ("la",  5.0, True)]),
    ("A''", "el motivo vuelve", 7.0, [          # igual al primero: es el retorno
        ("mi",  6.0, False), ("sol", 2.8, True), ("la",  2.8, True),
        ("sol", 2.2, True), ("fa#", 2.2, True), ("si",  5.5, True)]),
    ("A''", "bajada pura, cierra", 3.2, [       # la unica bajada sin giro de toda la
        ("la",  5.0, False), ("sol", 2.8, True),   # linea: por eso se lee como final
        ("fa#", 2.5, True), (None, 9.0, True)]),   # None = la nota final, ver CIERRES
]

# LA NOTA FINAL. Dos candidatas, y no es lo mismo:
#
#   mi (320,1 Hz)  tonica del motivo. Pero la cama del tema esta afinada en Re, asi que
#                  contra la base el Mi es una 2da: queda colgado, suspendido
#   re (285,2 Hz)  la fundamental de la base. La bajada pura continua un grado mas y
#                  aterriza en la nota sobre la que esta construido todo el tema. Es lo
#                  mas conclusivo que hay disponible sin salir del Em7
CIERRES = {"mi": "tonica del motivo, colgada contra la base",
           "re": "la fundamental de la base, aterriza"}


def aplanar(cierre):
    """ENUNCIADOS -> lista plana de (nota, dur, ligada, silencio_antes)."""
    plano = []
    for _, _, sil, notas in ENUNCIADOS:
        for j, (n, d, l) in enumerate(notas):
            plano.append((n or cierre, d, l, sil if j == 0 else 0.0))
    return plano


LINEA = [(n or "mi", d, l) for _, _, _, notas in ENUNCIADOS for (n, d, l) in notas]


def contorno_simbolos(frase):
    """El contorno del enunciado como flechas, para poder compararlos de un vistazo."""
    s = ""
    for a, b in zip(frase, frase[1:]):
        d = SEMI[b[0] or "mi"] - SEMI[a[0] or "mi"]
        s += "↑" if d > 0 else ("↓" if d < 0 else "=")
    return s


def verificar_contornos():
    """Aborta si dos enunciados consecutivos tienen el mismo contorno."""
    prev = None
    for frase_, que, _, notas in ENUNCIADOS:
        c = contorno_simbolos(notas)
        if c == prev:
            raise SystemExit(f"  ABORTA: '{que}' repite el contorno {c} del anterior. "
                             f"Dos enunciados seguidos no pueden tener la misma figura.")
        prev = c

# La segunda voz. NO entra al principio: la principal tiene que quedar sola para poder
# reconocerse. Entra en el pico y vuelve como pedal en el cierre.
#   (fraccion de la ventana donde entra, notas, nivel)
# Se enganchan a un ENUNCIADO por indice, no a un segundo fijo: si la linea se reacomoda
# la segunda voz sigue cayendo donde tiene que caer.
SEGUNDA = [
    (4, [("si", 8.0, False, 0.0), ("do", 6.0, True, 0.0), ("si", 14.0, True, 0.0)], 0.34),
    (7, [("si", 26.0, False, 0.0)], 0.26),
]


def ajustar(plano, ventana=VENTANA, cola=COLA):
    """Escala las duraciones de las notas para que la linea entre en la ventana.

    Escala solo las notas, NO los silencios: el respiro de cada enunciado esta elegido a
    mano y tiene que durar lo que dice, sin importar el largo total.

    Y reserva `cola` al final, que es el aire donde vive la estela de la ultima nota. Sin
    eso el delay queda truncado y se escucha como un corte.
    """
    sil = sum(s for _, _, _, s in plano)
    suma = sum(d for _, d, _, _ in plano)
    k = (ventana - cola - sil) / suma
    return [(n, d * k, l, s) for n, d, l, s in plano]


def contorno(plano, glide=GLIDE, cola=COLA):
    """Frecuencia por muestra. Al final el oscilador sigue corriendo en la ultima altura
    durante `cola` segundos, asi la nota final resuena en vez de cortarse."""
    tramos, t = [], 0.0
    prev = None
    for nota, dur, ligada, sil in plano:
        f1 = N[nota]
        if sil > 0 and prev is not None:
            tramos.append((sil, prev, prev))
            t += sil
        if ligada and prev is not None:
            g = min(glide, dur * 0.4)
            tramos.append((g, prev, f1))
            tramos.append((dur - g, f1, f1))
        else:
            tramos.append((dur, f1, f1))
        t += dur
        prev = f1

    n = int((t + cola) * SR)
    f = np.zeros(n)
    pos = 0
    for d, a, b in tramos:
        m = int(d * SR)
        if m <= 0:
            continue
        # el glide es exponencial: el oido escucha proporciones, no diferencias
        f[pos:pos + m] = a * (b / a) ** np.linspace(0, 1, m) if a != b else a
        pos += m
    f[pos:] = prev or FUND
    return f, t


TAU_REL = 1.15    # constante del release, en segundos


def envolvente(n, plano):
    """Amplitud. Ataque solo donde se re-dispara; en las ligadas casi no decae, asi la
    nota SUENA todo lo que dura en vez de pasar.

    EL RELEASE OCUPA EL SILENCIO. Cuando termina una corrida ligada y viene una nota con
    ataque, la envolvente NO cae a cero de golpe: se apaga exponencialmente a lo largo del
    respiro. Es lo que pasa al soltar una tecla, la nota sigue sonando mientras muere. El
    oscilador sigue corriendo en la altura anterior, asi que lo que resuena es esa misma
    nota. Cortar en seco ahi era el "corta de golpe" despues de las primeras notas.
    """
    e = np.zeros(n)
    t = 0.0
    for nota, dur, ligada, sil in plano:
        if sil > 0:
            # el silencio no esta vacio: es la cola de la nota anterior apagandose
            s0, s1 = int(t * SR), min(int((t + sil) * SR), n)
            if s1 > s0:
                nivel = e[s0 - 1] if s0 else 0.0
                e[s0:s1] = nivel * np.exp(-np.arange(s1 - s0) / SR / TAU_REL)
            t += sil
        a, b = int(t * SR), min(int((t + dur) * SR), n)
        if b <= a:
            t += dur
            continue
        if ligada:
            e[a:b] = np.linspace(e[a - 1] if a else 0.95, 0.93, b - a)
        else:
            # el ataque TARDA en llegar al maximo: es un crecimiento, no un golpe. La
            # curva es suave en las dos puntas (smoothstep), asi que no se escucha
            # arrancar ni llegar. Y sale desde donde quedo la estela, no desde cero.
            at = int(min(ATAQUE_S, dur * 0.45) * SR)
            u = np.linspace(0, 1, at)
            resto = e[a - 1] if a else 0.0
            e[a:a + at] = resto + (1.0 - resto) * (u * u * (3 - 2 * u))
            e[a + at:b] = np.linspace(1.0, 0.92, b - a - at)
        t += dur
    # la ultima nota se apaga sola a lo largo de toda la cola, y adentro de esa cola la
    # estela sigue repicando. Es lo que hace que el final se disuelva en vez de cortarse
    c0 = int(t * SR)
    if n > c0:
        e[c0:] = e[c0 - 1] * np.exp(-np.arange(n - c0) / SR / 3.4)
    w = int(0.012 * SR)          # suavizar micro-saltos sin borrar los ataques
    return np.convolve(e, np.ones(w) / w, "same")


def voz(plano, oct=1.0, drive=14.0, corte=2200.0, res=0.72, sub=0.35, cola=COLA):
    f, dur = contorno(plano, cola=cola)
    f = f * oct
    n = len(f)
    # UN SOLO oscilador continuo para toda la linea: la fase se acumula sin cortes, asi
    # que no hay click posible en ninguna juntura de notas.
    x = (sierra(f * 2 ** (2.5 / 1200)) * 0.5
         + sierra(f * 2 ** (-2.5 / 1200)) * 0.5
         + pulso(f / 2, 0.42) * sub)
    x /= np.abs(x).max() or 1.0
    env = envolvente(n, plano)
    x = ladder_moog(x, corte * (0.35 + 0.65 * env), resonancia=res, drive=drive)
    return x * env, dur


def tiempos(plano):
    """Segundo en que arranca cada enunciado, y el segundo de cada nota."""
    arranques, por_nota, t, i = [], [], 0.0, 0
    for _, _, _, notas in ENUNCIADOS:
        t += plano[i][3]                   # el respiro de este enunciado
        arranques.append(t)
        for _, d, _, _ in plano[i:i + len(notas)]:
            por_nota.append(t)
            t += d
        i += len(notas)
    return arranques, por_nota


def construir(cierre):
    """Arma la melodia entera con una nota final dada. Devuelve (audio, plano)."""
    plano = ajustar(aplanar(cierre))
    x, _ = voz(plano, oct=OCTAVA)
    n = len(x)
    arranques, _ = tiempos(plano)

    y = np.zeros(n)
    for idx, frag, niv in SEGUNDA:
        v, _ = voz(frag, oct=OCTAVA * OCTAVA_2, drive=7.0, corte=3200.0,
                   res=0.5, sub=0.12, cola=4.0)
        a = int(arranques[idx] * SR)
        b = min(n, a + len(v))
        if b > a:
            y[a:b] += v[:b - a] * niv

    x = x + y
    x /= np.abs(x).max() or 1.0
    x = lp(np.stack([x, x], axis=1), 3800)
    x = np.stack([x[:, 0], np.roll(x[:, 1], int(0.019 * SR))], axis=1)
    x = eco(x, **ESTELA)         # la estela, antes de la sala
    x = hp(x, 32)
    x = mono_graves(x, 150)
    sala = camara(x, 7, ir_lowpass=2800, wet=0.36, semilla=17000, pre_ms=70)
    x = hp(0.90 * x + 0.38 * sala[:len(x)], 30)
    x = fades(x, 2.0)
    x /= np.abs(x).max()
    m = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, m.integrated_loudness(x), -20.0)
    if np.abs(x).max() > 0.98:
        x *= 0.98 / np.abs(x).max()
    return x, plano


CIERRE_ELEGIDO = "re"    # la nota final. Cambiar a "mi" para la version colgada
DESDE_S = 455.0          # donde arranca en el tema: el arreglo abre el moog en 455


def capa(dur, desde=DESDE_S, cierre=CIERRE_ELEGIDO):
    """La melodia colocada adentro del tema entero, para `tema.py`.

    Devuelve un buffer estereo de `dur` segundos con la linea puesta en `desde`. La
    ventana del arreglo (455 a 655 s) coincide con VENTANA, asi que la linea entra justa
    y su envolvente de arreglo se encarga de la entrada y la salida.
    """
    verificar_contornos()
    x, _ = construir(cierre)
    y = np.zeros((int(dur * SR), 2))
    a = int(desde * SR)
    b = min(len(y), a + len(x))
    if b > a:
        y[a:b] = x[:b - a]
    return y


def main():
    verificar_contornos()
    plano = ajustar(aplanar("mi"))
    arranques, por_nota = tiempos(plano)

    # el mapa de la linea, para poder discutirla sin escucharla entera
    print(f"  {'#':>2} {'frase':5} {'enunciado':22} {'desde':>6} {'respiro':>8} "
          f"{'contorno':10} {'larga':>6}")
    i = 0
    for k, (frase_, que, sil, notas) in enumerate(ENUNCIADOS):
        larga = max(d for _, d, _, _ in plano[i:i + len(notas)])
        d0 = arranques[k]
        print(f"  {k+1:2d} {frase_:5} {que:22} "
              f"{int(d0)//60}:{int(d0)%60:02d}  {sil:6.1f}s  "
              f"{contorno_simbolos(notas):10} {larga:5.1f}s")
        i += len(notas)
    sils = [s for _, _, s, _ in ENUNCIADOS[1:]]
    print(f"     contornos: ninguno repite el del anterior")
    print(f"     respiros:  de {min(sils):.1f} a {max(sils):.1f}s, ocho valores distintos")

    tot = sum(1 for a, b in zip(LINEA, LINEA[1:])
              if abs(SEMI[b[0]] - SEMI[a[0]]) > 0)
    cj = sum(1 for a, b in zip(LINEA, LINEA[1:])
             if 0 < abs(SEMI[b[0]] - SEMI[a[0]]) <= 2)
    print(f"\n  grados conjuntos: {cj}/{tot} = {100*cj/tot:.0f}%  "
          f"(la proporcion sana es ~80%)")
    ipico = [m[0] for m in LINEA].index("mi_a")
    print(f"  el pico (Mi {N['mi_a']*OCTAVA:.0f} Hz) suena 1 vez, en "
          f"{int(por_nota[ipico])//60}:{int(por_nota[ipico])%60:02d} = "
          f"{100*por_nota[ipico]/VENTANA:.0f}% de la ventana")
    ent = ", ".join(f"{int(arranques[i])//60}:{int(arranques[i])%60:02d}"
                    for i, _, _ in SEGUNDA)
    print(f"  segunda voz: entra en {ent} (la principal arranca sola)")
    fin = por_nota[-1] + plano[-1][1]
    print(f"  la ultima nota termina en {int(fin)//60}:{int(fin)%60:02d} y quedan "
          f"{VENTANA-fin:.1f}s de cola para la estela")

    salida = os.path.join(AQUI, "melodias")
    os.makedirs(salida, exist_ok=True)
    print()
    for cierre, que in CIERRES.items():
        x, _ = construir(cierre)
        ruta = os.path.join(salida, f"13_MELODIA_cierre_{cierre.upper()}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        d = np.abs(np.diff(x.mean(axis=1)))
        print(f"  cierre en {cierre.upper()} ({N[cierre]*OCTAVA:5.1f} Hz): {que}")
        print(f"    -> {os.path.relpath(ruta, RAIZ)}   {len(x)/SR:.0f}s   "
              f"discontinuidad max {d.max():.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
