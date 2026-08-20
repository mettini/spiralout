#!/usr/bin/env python3
"""Las dos capas que le faltaban a thermal_mass: grano y aire, desde la lluvia.

Las cuatro capas de `render.py` cubren de 20 Hz a 1,5 kHz y ahi se terminan. Medido
sobre `mix_v2_arco.wav`: **0,0% de energia arriba de 1,5 kHz**, el 99,9% cae antes de
1237 Hz. O sea que las capas 4 (grano) y 5 (aire) de `docs/38` directamente no
existian.

Estas salen de los clips de lluvia del 2026-08-08. La eleccion de fuente no es de
gusto, es aritmetica: de los cuatro clips el 4739 es el unico con agudo real (26% en
1,5-6k y 28% en 6k+, y llega limpio hasta 19 kHz). El 4740 es el unico con
transitorios (15 saltos de mas de 9 dB) y de ahi sale la capa de eventos de lluvia,
que se rinde aparte para poder compararla contra `flywheel` antes de meterla.

    python3.10 lab/thermal_mass/rain.py

Determinista: misma semilla que `render.py` (24, el hexagrama del proyecto).

OJO: la capa de grano vive en 1,5-6 kHz, que es la banda exacta que `task qa:spectral`
marca como fritura. La regla del proyecto (memory/pattern_noise_fritura.md) es no
pasar de ~800 Hz **en ruido sintetizado**, porque no tiene estructura interna. La
lluvia real si la tiene, y `docs/38` define la capa 4 justamente ahi. Pero el margen
es fino: correr qa:spectral sobre mix_v3 antes de dar esto por bueno.
"""
import os
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, welch

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)

from render import (SEMILLA, SR, barrido, camara, del_medio, estirar_estereo,  # noqa: E402
                    expansor, fades, hp, lp, medir, mono_graves, notch_parcial,
                    percusivo, resonancias, respiracion, transient_shaper)

DUR = 120.0                 # el concepto. El master va a 671 (11:11), ver docs/39
BASE = "mix_v2_arco.wav"    # los 2 minutos ya armados, a los que les falta el techo

# Los clips de lluvia. El video vive fuera del repo (pesa), el WAV se cachea.
CLIPS = os.path.expanduser("~/Downloads/Videos-Aem")
FUENTES = {
    # 26% grano + 28% aire, techo a 19 kHz. La unica con agudo de verdad.
    "lluvia_alta": ("IMG_4739.MOV", "lluvia_4739_22k.wav"),
    # 15 saltos de mas de 9 dB. La unica con transitorios.
    "lluvia_golpes": ("IMG_4740.MOV", "lluvia_4740_22k.wav"),
}

# La fundamental de la base, medida con check_source.py. El grave del 4739 esta a
# 70,3 Hz, o sea a 25 cents de esto: batiria. Por eso el pasa-altos no es gusto.
FUNDAMENTAL_BASE = 71.3


def cargar(clave):
    """Saca el audio del clip a mono SR del proyecto. Cachea el WAV."""
    mov, wav = FUENTES[clave]
    origen, destino = os.path.join(CLIPS, mov), os.path.join(AQUI, "source", wav)
    if not os.path.exists(destino):
        assert os.path.exists(origen), f"falta el clip: {origen}"
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", origen,
                        "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le",
                        destino, "-y"], check=True)
    sr, x = wavfile.read(destino)
    assert sr == SR, f"{destino} esta a {sr} Hz, se esperaba {SR}"
    x = x.astype(np.float64)
    x /= np.abs(x).max()
    return sosfilt(butter(2, 30 / (SR / 2), "high", output="sos"), x)


def repetir_suave(x, n, cruce_s=0.35):
    """Repite `x` hasta llegar a `n` muestras CRUZANDO las junturas.

    `np.tile` pega el ultimo sample de la grabacion con el primero, y eso es un empalme
    duro: un click. La grabacion de lluvia dura 9,71 s, asi que aparecia un salto cada
    9,71 s durante todo el tema. Medido en el master: discontinuidades de 0,57 en
    5:21.02, 5:30.73, 5:40.43 y 5:50.14, separadas por 9,71 exactos.
    """
    c = int(cruce_s * SR)
    if len(x) <= c * 2:
        return np.tile(x, int(np.ceil(n / len(x))))[:n]
    r = np.linspace(0, 1, c)
    if x.ndim > 1:
        r = r[:, None]
    paso = len(x) - c
    piezas = int(np.ceil(n / paso)) + 1
    y = np.zeros((piezas * paso + c,) + x.shape[1:])
    for i in range(piezas):
        a = i * paso
        if i == 0:
            y[a:a + len(x)] = x
        else:
            y[a:a + c] = y[a:a + c] * (1 - r) + x[:c] * r
            y[a + c:a + len(x)] = x[c:]
    return y[:n]


def grano(fuente, lufs_objetivo, dur=DUR):
    """Capa 4 (docs/38): 1,5-6 kHz. La que da ESCALA.

    Ventana de stretch chica a proposito. Con ventana grande Paulstretch promedia
    los cuadros y la lluvia se vuelve un drone liso: se pierde justo el detalle que
    la hace grano. Con ventana chica sobrevive la granulacion.
    """
    # Ventana mas chica que antes (0,30 -> 0,14): la ventana es lo que define cuanto
    # se promedia el espectro, o sea cuanto se BORRA la granulacion de la lluvia.
    x = estirar_estereo(fuente, stretch=max(22, dur / 6), window=0.14)
    x = del_medio(x, dur)                             # el arranque del stretch es pobre

    # LA VIA CRUDA (pedido de Helen: que aparezca el sonido original).
    # Paulstretch, por mas corta que sea la ventana, randomiza la fase y con eso se
    # pierden las gotas: quedan como una sabana. Esto suma la grabacion SIN estirar,
    # filtrada a la banda de la capa y con el transitorio realzado, para que vuelvan
    # a escucharse gotas discretas encima de la sabana.
    n = len(x)
    crudo = repetir_suave(fuente, n)
    crudo = np.stack([crudo, np.roll(crudo, int(0.013 * SR))], axis=1)
    crudo = transient_shaper(hp(crudo, 1200), rapida_ms=12, lenta_ms=260, fuerza=0.9)
    crudo /= np.abs(crudo).max() or 1.0
    x = x / (np.abs(x).max() or 1.0) + crudo * 0.42

    x = hp(x, 1200)                                   # el sotano es de thermal_mass,
    #                                                   y ademas evita el batido de 25 cents
    for f0 in resonancias(x, 1500, 8000, cuantas=3):  # la lluvia tiene picos de recinto
        x = notch_parcial(x, f0, q=8, mezcla=0.50)

    x = barrido(x, 2600, 6500, periodo=29.0)          # primo libre: 17/13/23/19/11 ya usados
    x = respiracion(x, 0.12, periodo=31.0)
    x = mono_graves(x, 900)                           # ancho arriba, sin nada que centrar abajo
    x = camara(x, 6, ir_lowpass=5000, wet=0.42, semilla=7000)
    x = hp(x, 1100)                                   # la camara devuelve grave
    x = fades(x)
    x /= np.abs(x).max()
    medidor = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), lufs_objetivo)
    if np.abs(x).max() > 0.98:
        x *= 0.98 / np.abs(x).max()
    return x


def aire(fuente, lufs_objetivo, dur=DUR):
    """Capa 5 (docs/38): 6 kHz para arriba. El cuarto en silencio a ganancia alta.

    Al SR del proyecto el techo es 11 kHz, asi que esta capa vive en 6-11k. Es poco
    ancho de banda y es a proposito que sea casi inaudible: se nota cuando se apaga,
    no cuando esta.

    Ventana grande, al reves que el grano: aca NO se quiere detalle sino continuidad.
    """
    x = estirar_estereo(fuente, stretch=max(30, dur / 4), window=1.4)
    x = del_medio(x, dur)

    x = hp(x, 6000)
    x = respiracion(x, 0.18, periodo=37.0)            # otro primo libre
    x = camara(x, 4, ir_lowpass=9000, wet=0.30, semilla=8000)
    x = hp(x, 5800)
    x = fades(x)
    x /= np.abs(x).max()
    medidor = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), lufs_objetivo)
    if np.abs(x).max() > 0.98:
        x *= 0.98 / np.abs(x).max()
    return x


def lluvia_brillo(fuente, lufs_objetivo, dur=DUR):
    """La tercera lluvia, para el medio del tema. Pedido del user:

        "en algun momento, en el medio del video se tendria que escuchar como una
        lluvia, quizas no literal como la tenemos, apenitas realentizada con algun FX,
        que aporte brillo, algo mas granular, no tan tapado"

    Es lo contrario de `grano` y `aire`, que estan estiradas 134 y 168 veces y por eso
    suenan a sabana. Esta va **apenas** ralentizada, asi que conserva las gotas.

    Tres decisiones y las tres son por el pedido:

    BRILLO: la mezcla entera se termina en 5,5 kHz. Aca se abre arriba de 2 kHz y se
    deja pasar todo el techo disponible (11 kHz al SR del proyecto). Nada de LPF.

    GRANULAR: `transient_shaper` agresivo sobre la fuente sin estirar. Lo que hace que
    se escuchen gotas y no ruido es el ATAQUE de cada una, y estirar lo borra.

    NO TAPADA: no lleva `camara`. La reverb es lo que manda una capa al fondo, y esta
    tiene que estar adelante. Solo un retardo corto para que tenga ancho.
    """
    n = int(dur * SR)
    # apenas 4x, contra 134x del grano: las gotas sobreviven
    x = estirar_estereo(fuente, stretch=4.0, window=0.10)
    if len(x) < n:
        x = repetir_suave(x, n)
    x = x[:n]

    # y encima la fuente CRUDA, que es de donde sale la granulacion de verdad
    crudo = repetir_suave(fuente, n)
    crudo = np.stack([crudo, np.roll(crudo, int(0.009 * SR))], axis=1)
    crudo = transient_shaper(crudo, rapida_ms=8, lenta_ms=180, fuerza=1.1)
    crudo /= np.abs(crudo).max() or 1.0

    x = x / (np.abs(x).max() or 1.0) * 0.55 + crudo * 0.75
    x = hp(x, 2000)                                   # el brillo empieza aca
    for f0 in resonancias(x, 2500, 9000, cuantas=2):  # sacar picos de recinto
        x = notch_parcial(x, f0, q=10, mezcla=0.40)
    x = respiracion(x, 0.10, periodo=53.0)            # otro primo libre
    x = mono_graves(x, 1500)
    x = transient_shaper(x, rapida_ms=10, lenta_ms=200, fuerza=0.7)
    x = hp(x, 1900)
    x = fades(x, 2.0)
    x /= np.abs(x).max()
    medidor = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), lufs_objetivo)
    if np.abs(x).max() > 0.98:
        x *= 0.98 / np.abs(x).max()
    return x


def lluvia_eventos(fuente, dur=DUR):
    """Capa 6 alternativa, desde el 4740. NO entra en la mezcla todavia.

    `flywheel` ya ocupa el lugar de los eventos con el sarandeo del lavarropas. Esto
    se rinde aparte para poder escuchar las dos y decidir, en vez de amontonar.

    Mismo criterio que flywheel: nada de Paulstretch, que randomiza la fase y mata el
    ataque. Va enlentecido por velocidad, como cinta lenta.
    """
    perc = percusivo(fuente)
    lento = np.interp(np.arange(0, len(perc) - 1, 1 / 3.0), np.arange(len(perc)), perc)
    lento /= np.abs(lento).max()
    lento = expansor(lento, umbral_db=-30)            # limpia lo que hay entre golpes

    n = int(dur * SR)
    reps = int(np.ceil(n / len(lento)))
    x = repetir_suave(lento, n)
    x = np.stack([x, np.roll(x, int(0.011 * SR))], axis=1)   # estereo por retardo corto

    x = lp(hp(x, 300), 5000)                          # el sub es de la base, no de aca
    x = transient_shaper(x, fuerza=0.6)
    x = camara(x, 9, ir_lowpass=2500, wet=0.5, semilla=9000, pre_ms=120)
    x = hp(x, 280)
    x = fades(x)
    return x / np.abs(x).max() * 10 ** (-6.0 / 20)


def seguir_arco(x, base, suavizado_s=6.0):
    """Multiplica la capa por la envolvente lenta de la base.

    Sin esto las capas de arriba entran a nivel pleno mientras la base todavia esta
    en silencio. `mix_v2_arco` tarda 16 s en entrar y 15 en salir, asi que durante
    esos tramos la mezcla queda siendo lluvia sola y el ratio HOT se dispara: era la
    causa de los 8 hits que marcaba qa:spectral en los bordes, con el medio limpio.

    Con ventana larga la envolvente casi no se mueve en la meseta, asi que en el
    cuerpo del tema no comprime nada: actua en los extremos, que es donde hace falta.
    """
    m = np.abs(base).mean(axis=1)
    w = max(int(suavizado_s * SR), 1)
    env = np.convolve(m, np.ones(w) / w, "same")
    env /= env.max() or 1.0
    # exponente > 1: la meseta casi no se mueve pero las puntas colapsan mucho mas
    # rapido. Sin esto queda cola de lluvia sonando sola sobre una base ya muerta.
    env = env ** 1.8
    return x * env[:len(x), None]


def techo(x, etiqueta):
    """Cuanta energia hay arriba de 1,5 kHz. Es el numero que justifica todo esto."""
    fr, ps = welch(x.mean(axis=1), SR, nperseg=16384)
    tot = ps.sum()
    alto = 100 * ps[fr >= 1500].sum() / tot
    acum = np.cumsum(ps) / tot
    corte = fr[np.searchsorted(acum, 0.999)]
    print(f"  {etiqueta:16} arriba de 1,5 kHz: {alto:5.1f}%   el 99,9% cae en {corte:6.0f} Hz")


def main():
    np.random.seed(SEMILLA)

    sr, base = wavfile.read(os.path.join(AQUI, BASE))
    assert sr == SR, f"{BASE} esta a {sr} Hz"
    base = base.astype(np.float64) / 32768.0
    n = min(len(base), int(DUR * SR))
    base = base[:n]

    lufs_base = pyln.Meter(SR).integrated_loudness(base)

    alta = cargar("lluvia_alta")
    golpes = cargar("lluvia_golpes")

    # igualadas por sonoridad a la base, despues se sientan con los niveles de docs/38
    gr = seguir_arco(grano(alta, lufs_base)[:n], base)
    ai = seguir_arco(aire(alta, lufs_base)[:n], base)
    ev = lluvia_eventos(golpes)[:n]

    # docs/38: el grano se siente pero no se escucha, el aire menos todavia
    mezcla = base + gr * 10 ** (-14 / 20) + ai * 10 ** (-20 / 20)
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-6.0 / 20)

    salidas = (("rain_grano", gr), ("rain_aire", ai),
               ("rain_eventos", ev), ("mix_v3", mezcla))
    for nombre, x in salidas:
        ruta = os.path.join(AQUI, f"{nombre}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        print(f"-> {os.path.relpath(ruta, RAIZ)}")

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    for nombre, x in (("base v2", base),) + salidas:
        medir(nombre, x)

    print("\n  EL AGUJERO QUE SE TAPA")
    techo(base, "base v2")
    techo(mezcla, "mix_v3")


if __name__ == "__main__":
    sys.exit(main())
