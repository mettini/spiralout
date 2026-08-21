#!/usr/bin/env python3
"""El tema completo: 11:11 con el arreglo de `docs/39`.

    python3.10 transmissions/02/bj3_n_pt/tema.py

11:11 son 671 segundos. Nada se estira: cada capa se REN DERIZA a 671, que es como
esta pensado el codigo (todas toman `dur`). Time-stretchear el archivo final embarra
todo.

EL ARREGLO (bajado por el user, `docs/39`)

    0:00  la base sola
    1:30  entra el cuerpo, despues el lavarropas
    3:00  asoma la lluvia y se va
    4:30  entran las voces
    6:00  se pudre todo
    8:00  descarga y entra el moog
    9:30  afloja y cierra

La respuesta a "las lluvias ensucian" es esta: en 2 minutos todas las capas entraban
con segundos de diferencia y sonaban siempre juntas. Aca la lluvia tiene su ventana,
se va, y vuelve solo para el climax.

EL PROBLEMA DE MEMORIA, Y COMO SE RESUELVE

Las capas de `render.py` usan stretch = max(45, dur/N). A 671 eso da factores de 160
a 335, y sobre una fuente de 15 s generaria casi una hora de audio para tirar el 90%,
con picos de gigabytes.

La solucion NO es bajar el stretch, porque el stretch ES el timbre: mas stretch es
mas congelado. Lo que se hace es alimentar una REBANADA mas corta de la fuente con el
mismo factor. Mismo timbre exacto, y se genera solo lo que hace falta.
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

import cuerdas  # noqa: E402
import melodia as melodia_mod  # noqa: E402
import rain  # noqa: E402
import render  # noqa: E402
import voces  # noqa: E402
from aem.master import master_chain  # noqa: E402
from render import SEMILLA, SR, fades, medir  # noqa: E402

DUR = 671.0          # 11:11
MARGEN = 1.12        # cuanto de mas se genera antes de recortar


def rebanada(fuente, segundos):
    """Recorta la fuente al centro. El arranque y el final de una grabacion son lo
    mas pobre, asi que se toma del medio.

    Se usa solo en la cama: su stretch tiene piso 45 y ademas se le cuadruplica el
    largo al bajar dos octavas, o sea que con la fuente entera genera 45 minutos de
    audio intermedio para quedarse con 11. Con 7 segundos de fuente (la ventana de
    paulstretch es de 5, asi que menos no se puede) genera 21 minutos.
    """
    n = int(segundos * SR)
    if n >= len(fuente):
        return fuente
    off = (len(fuente) - n) // 2
    return fuente[off:off + n]


CACHE = os.path.join(AQUI, ".capas")


def cachear(nombre, hacer):
    """Rinde una capa o la levanta del cache.

    Las capas tardan minutos y casi no cambian; el arreglo cambia todo el tiempo.
    Con esto iterar el arreglo cuesta segundos. `--rehacer` fuerza el render.
    """
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, f"{nombre}_{int(DUR)}.npy")
    if "--rehacer" not in sys.argv and os.path.exists(ruta):
        print(f"    {nombre} (cache)")
        return np.load(ruta)
    print(f"    {nombre}...")
    x = hacer()
    np.save(ruta, x)
    return x


def sobre(puntos, dur=DUR):
    """Envolvente de presencia, de (segundo, ganancia) interpolados.

    Es el arreglo hecho numeros: cada capa dice cuando esta y cuando no.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    return np.interp(t, xs, ys)[:, None]


# El arreglo, capa por capa. Los tiempos son los de docs/39.
ARREGLO = {
    # la cama esta siempre: es el piso del tema
    "cama":      [(0, 0), (12, 1.0), (610, 1.0), (671, 0)],
    # el cuerpo entra a 1:30
    "cuerpo":    [(0, 0), (90, 0), (125, 1.0), (470, 1.0), (505, 0.55),
                  (600, 0.55), (645, 0)],
    # la nube acompana al cuerpo
    "nube":      [(0, 0), (100, 0), (140, 0.9), (200, 0.55), (280, 0.9),
                  (560, 0.9), (635, 0)],
    # el lavarropas entra despues del cuerpo, se va en la descarga
    # se va con rampa larga: son golpes discretos, y con rampa corta uno queda
    # cortado al medio y se escucha como un corte seco
    "lavarropas":[(0, 0), (150, 0), (190, 0.75), (240, 0.75), (275, 0.45),
                  (330, 0.9), (455, 0.9), (520, 0), (671, 0)],
    # LA LLUVIA: ventana propia, se va, y vuelve solo para el climax
    # la lluvia NO acompana a las voces ni al moog: es lo que los tapaba. Tiene su
    # ventana propia al principio y una sola aparicion corta en el climax
    "grano":     [(0, 0), (185, 0), (210, 0.85), (245, 0.85), (275, 0),
                  (368, 0), (390, 0.9), (445, 0.9), (475, 0), (671, 0)],
    # el aire muere antes que la cama a proposito: si queda agudo sonando sobre
    # graves que ya se fueron, la mezcla se vuelve fina y qa:spectral lo marca
    # el aire era el siseo continuo que molestaba de 8:00 en adelante. Ahora muere
    # antes de que entre el moog y no vuelve
    "aire":      [(0, 0), (185, 0), (210, 0.6), (262, 0.6), (292, 0),
                  (368, 0), (392, 0.75), (440, 0.75), (470, 0), (671, 0)],
    # las voces entran a 4:30 y son el centro del climax
    "voces":     [(0, 0), (270, 0), (300, 0.9), (350, 0.55),
                  (380, 1.0), (480, 1.0), (520, 0), (595, 0.45), (650, 0)],
    # el brillo: destellos, nunca continuo
    "brillo":    [(0, 0), (330, 0), (350, 0.8), (470, 0.8), (500, 0),
                  (565, 0.7), (620, 0)],
    # La tercera lluvia, pedida para el medio del tema: entra justo en la ventana
    # donde las otras dos se retiran, asi no se suma barro sino que se cambia el
    # color. Va adelante y con brillo, no debajo.
    "lluvia_brillo": [(0, 0), (282, 0), (300, 0.75), (352, 0.9), (368, 0.55),
                      (392, 0), (498, 0), (520, 0.7), (566, 0.5), (600, 0)],
    # EL MOOG. Antes era una meseta: subia a 1.0 en 495 y se quedaba plano hasta 620.
    # Pedido: "que tenga un incremento de volumen y luego ir bajando, no te digo fade,
    # pero si que sea progresivo el volumen entrando y saliendo".
    #
    # Ahora es un ARCO, y el maximo cae en 543 s, que es donde la melodia toca su PICO
    # (el Mi de 640 Hz, la nota mas alta de toda la linea). O sea que el nivel y la
    # melodia llegan arriba en el mismo lugar en vez de pelearse.
    "moog":      [(0, 0), (455, 0), (480, 0.35), (505, 0.60), (525, 0.80),
                  (543, 1.0), (575, 0.92), (605, 0.72), (635, 0.40), (658, 0)],
}

# Niveles por capa, en dB. Los de docs/38 mas los nuevos.
#
# El moog bajo de -6 a -13. Medido, a -6 quedaba a -0,3 dB de la mezcla entera, o sea
# tan fuerte como todo lo demas junto. Un elemento solista se sienta entre -8 y -12
# respecto del RMS de la mezcla; si no, deja de ser una voz y pasa a ser el tema.
NIVELES = {"cama": 0, "cuerpo": -4, "nube": -8, "lavarropas": -1,
           "grano": -14, "aire": -20, "voces": -6, "brillo": -17, "moog": -9,
           "lluvia_brillo": -13}

# Quien se aparta cuando entran las voces, y cuanto.
#
# Medido en la ventana donde las voces estan plenas, en su banda (110-700 Hz): el
# lavarropas esta +8,9 dB por encima de ellas y la nube +4,6. La lluvia esta -27,9,
# o sea que NO era la que tapaba. Bajar la lluvia no hubiera cambiado nada.
DUCKING = {"lavarropas": 0.55, "nube": 0.40, "cuerpo": 0.22}

# Y lo mismo para el moog: medido, en su ventana la CAMA esta +7,7 dB por encima de el
# en su misma banda. Subir el moog no alcanzaba porque el problema no era su nivel
# sino quien lo tapaba. La cama se aparta cuando el entra.
# Se suman las TRES lluvias. El user marco 8:20: "no se si queda copado que pises la
# lluvia que se escucha mas fuerte con el moog que esta entrando, dale aire al moog".
# Y tenia razon sobre el arreglo: `lluvia_brillo` vuelve a subir justo en 498-520, o sea
# exactamente donde el moog esta entrando. Chocaban por diseno.
#
# Con `DUCK_SUAVIZADO_S` en 25 s el apartarse arranca ~25 s antes de que el moog suene,
# asi que el camino se le abre de a poco y no hay ninguna bajada de golpe.
# Marca textual sobre 8:30: "no podes meter el moog ascendente con lluvia repiqueteante
# que entra de fondo, baja esa lluvia de mierda ahi, entra el puto moog, respeto".
#
# Los valores de lluvia suben fuerte: `lluvia_brillo` de 0.45 a 0.78 y `grano` de 0.35 a
# 0.62. El moog es la voz de ese tramo y el fondo tiene que apartarse de verdad, no un
# poquito. Con los 25 s de suavizado el camino se abre bien antes de que el moog suene,
# asi que no hay ninguna bajada de golpe.
DUCKING_MOOG = {"cama": 0.34, "nube": 0.40, "cuerpo": 0.30,
                "lluvia_brillo": 0.78, "grano": 0.62, "aire": 0.45}

# El sidechain no puede seguir la envolvente de las voces tal cual: esa sube de 0 a
# 0.9 en 30 s, y con tres capas apartandose a la vez se escucha como un fade-out
# corto en el minuto 5. Suavizado a 25 s, el apartarse deja de ser un evento.
DUCK_SUAVIZADO_S = 25.0


def main():
    np.random.seed(SEMILLA)
    print(f"  rindiendo {DUR:.0f}s (11:11)\n")

    bomba = render.cargar("bomba")
    lavarropas_src = render.cargar("lavarropas")
    lluvia = rain.cargar("lluvia_alta")

    capas = {}

    capas["cama"] = cachear("cama", lambda: render.thermal_mass(rebanada(bomba, 7.0), dur=DUR))
    lufs = pyln.Meter(SR).integrated_loudness(capas["cama"])
    capas["nube"] = cachear("nube", lambda: render.cloud_chamber(bomba, lufs, dur=DUR))
    capas["cuerpo"] = cachear("cuerpo", lambda: render.manifold(lavarropas_src, lufs, dur=DUR))
    capas["lavarropas"] = cachear("lavarropas", lambda: render.flywheel(lavarropas_src, dur=DUR))
    capas["grano"] = cachear("grano", lambda: rain.grano(lluvia, lufs, dur=DUR))
    capas["aire"] = cachear("aire", lambda: rain.aire(lluvia, lufs, dur=DUR))
    _, f0, _ = voces.TOMAS["gutural"]           # la toma que eligio el user
    capas["voces"] = cachear("voces", lambda: voces.coro(voces.cargar("gutural"), f0, dur=DUR))
    capas["brillo"] = cachear("brillo", lambda: cuerdas.brillo(lluvia, lufs, dur=DUR))
    capas["lluvia_brillo"] = cachear("lluvia_brillo",
                                    lambda: rain.lluvia_brillo(lluvia, lufs, dur=DUR))
    # La melodia: nueve enunciados con estructura A A' B A'' (ver docs/45). Reemplaza
    # a `moog.py`, que repetia una pasada de 35 s con una pausa de 4 y por eso cortaba
    # cada 39 s. Esta es una sola linea continua que ocupa la ventana entera.
    capas["moog"] = cachear("moog", lambda: melodia_mod.capa(DUR))

    # SIDECHAIN: los que tapan a las voces se apartan cuando ellas suenan.
    # Es lo que se hace en una mezcla real: no se sube al que no se escucha, se baja
    # al que lo esta tapando. Subir las voces solo hubiera sumado barro.
    w = int(DUCK_SUAVIZADO_S * SR)

    def media_movil(e, ancho):
        """Promedio movil por suma acumulada: O(n).

        Antes esto era np.convolve con un nucleo de 25 s sobre 14,8 millones de
        muestras. np.convolve hace la convolucion DIRECTA, o sea n por m: unas 8e12
        operaciones, y el render se colgaba veinte minutos en esta sola linea.
        """
        c = np.cumsum(np.concatenate([[0.0], e]))
        mitad = ancho // 2
        idx = np.arange(len(e))
        a = np.clip(idx - mitad, 0, len(e))
        b = np.clip(idx + ancho - mitad, 0, len(e))
        return (c[b] - c[a]) / np.maximum(b - a, 1)

    def envolvente_suave(nombre):
        e = sobre(ARREGLO[nombre])[:, 0]
        e = e / (e.max() or 1.0)
        e = media_movil(e, w)
        return e / (e.max() or 1.0)

    voz_env = envolvente_suave("voces")
    moog_env = envolvente_suave("moog")

    print("\n  mezclando con el arreglo de docs/39...")
    n = int(DUR * SR)
    mezcla = np.zeros((n, 2))
    for nombre, x in capas.items():
        x = x[:n]
        if len(x) < n:
            x = np.pad(x, ((0, n - len(x)), (0, 0)))
        g = sobre(ARREGLO[nombre])[:, 0]
        if nombre in DUCKING:
            g = g * (1.0 - DUCKING[nombre] * voz_env)
        if nombre in DUCKING_MOOG:
            g = g * (1.0 - DUCKING_MOOG[nombre] * moog_env)
        x = x * g[:, None] * 10 ** (NIVELES[nombre] / 20)
        capas[nombre] = x
        mezcla += x

    mezcla = fades(mezcla, 6.0)
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-6.0 / 20)

    ruta = os.path.join(AQUI, "tema_1111.wav")
    wavfile.write(ruta, SR, (mezcla * 32767).astype(np.int16))
    print(f"  -> {os.path.relpath(ruta, RAIZ)}  ({len(mezcla)/SR/60:.2f} min)  scratch")

    # Y la version masterizada, con la cadena v2 del proyecto (framework/aem/master.py).
    # Mismo camino que scripts/master_bounce.py: se atenua a -12 dBFS primero para que
    # los picos del climax no claven el limiter.
    master = master_chain(mezcla * (10 ** (-12 / 20) / np.abs(mezcla).max()),
                          lufs_target=-16.0)
    ruta_m = os.path.join(AQUI, "tema_1111_master.wav")
    wavfile.write(ruta_m, SR, (np.clip(master, -1, 1) * 32767).astype(np.int16))
    print(f"  -> {os.path.relpath(ruta_m, RAIZ)}  masterizado, LUFS -16")

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    medir("tema_1111", mezcla)
    medir("tema_1111_master", master)

    print("\n  QUIEN SUENA CUANDO")
    marcas = [0, 90, 180, 270, 360, 480, 570, 660]
    print("       " + "".join(f"{m//60}:{m%60:02d}".rjust(8) for m in marcas))
    for nombre in ARREGLO:
        env = sobre(ARREGLO[nombre])[:, 0]
        fila = "".join(("#" * int(round(env[min(int(m * SR), n - 1)] * 5))).rjust(8) for m in marcas)
        print(f"  {nombre:11}{fila}")


if __name__ == "__main__":
    sys.exit(main())
