#!/usr/bin/env python3
"""El coro de la entidad: de una voz sola a un coro grave tipo Dune.

Fuente: las tomas del user recitando las cuatro formulas en protoindoeuropeo
(`docs/42`). Dos versiones para comparar, una limpia y una medio cantada/gutural.

    python3.10 transmissions/02/bj3_n_pt/voces.py

LA DECISION QUE MANDA: la afinacion.

El tono de referencia que se preparo eran 142,6 Hz (el doble de la fundamental de la
base, 71,3 Hz). Las tomas no vinieron ahi: F0 medida 100,4 Hz la limpia y 97,6 Hz la
gutural, unos 600 cents abajo. Contra 71,3 Hz eso cae casi exacto en un TRITONO, que
es el peor intervalo posible para sostener debajo de un drone.

No se corrige con afinador. Se corrige por VELOCIDAD DE CINTA, que es lo que hay que
hacer igual: bajar por velocidad hunde los formantes junto con el tono, y esa es
exactamente la diferencia entre "voz grave" y "voz de otra cosa". Un pitch shifter
que preserva formantes suena a chipmunk al reves.

Las tres voces del stack se derivan de la fundamental de la base, no de la toma:

    sub     35,65 Hz   una octava abajo de la base
    raiz    71,30 Hz   la fundamental, al unisono
    quinta 106,95 Hz   la quinta justa (3/2)

Asi el coro no se apoya sobre el tema: ES el tema, una octava y una quinta arriba.

OJO (memory/pattern_noise_fritura.md, T_VOICE_PAD_HARMONICS): la saturacion que da el
cuerpo tira armonicos a 1,5-4 kHz, la banda que marca qa:spectral. Por eso hay un LPF
despues de cada tanh, no antes.
"""
import os
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)

from render import (SEMILLA, SR, camara, envolvente, fades, hp, lp,  # noqa: E402
                    medir, mono_graves, respiracion)

DUR = 120.0
FUND_BASE = 71.3     # la fundamental de mix_v2_arco, medida con check_source
CANTANTES = 4        # gargantas por altura y repeticion. 3 alturas x 3 x 4 = 36 voces

# toma -> (archivo, F0 medida por autocorrelacion, etiqueta)
TOMAS = {
    "limpia": ("Ortiz de Ocampo 4.m4a", 100.4, "voz limpia"),
    "gutural": ("Ortiz de Ocampo 5.m4a", 97.6, "voz cantada/gutural"),
}
DESCARGAS = os.path.expanduser("~/Downloads")

# Las tres voces del stack, como razon contra la fundamental de la base.
# Subidas una octava respecto de la primera version: con la raiz en 71,3 el coro
# quedaba en zona de sub-graves y perdia todo caracter de voz. En 142,6 se escucha
# que ES una garganta, que es el punto.
VOCES = (
    ("grave", 1.0, 0.80),     # la fundamental: el peso
    ("raiz", 2.0, 1.00),      # una octava arriba: aca se lee como voz
    ("quinta", 3.0, 0.55),    # la quinta sobre esa: el brillo, mas atras
)


def cargar(clave):
    """Trae la toma a mono al SR del proyecto."""
    m4a, _, _ = TOMAS[clave]
    origen = os.path.join(DESCARGAS, m4a)
    destino = os.path.join(AQUI, "source", f"voz_{clave}_22k.wav")
    if not os.path.exists(destino):
        assert os.path.exists(origen), f"falta la toma: {origen}"
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", origen,
                        "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le",
                        destino, "-y"], check=True)
    sr, x = wavfile.read(destino)
    assert sr == SR
    x = x.astype(np.float64)
    x /= np.abs(x).max()
    return sosfilt(butter(2, 40 / (SR / 2), "high", output="sos"), x)   # rumble de mano


def cinta(x, razon):
    """Cambio de tono POR VELOCIDAD. Pitchea y alarga a la vez, y arrastra los
    formantes con el tono. Es lo contrario de un pitch shifter.

    `razon` es el FACTOR DE FRECUENCIA de salida: 0,5 baja una octava y duplica el
    largo, 2,0 sube una octava y lo parte al medio. El paso de lectura es la razon
    misma, porque leer de a `razon` muestras comprime el tiempo por `razon` y por lo
    tanto multiplica la frecuencia por `razon`.
    """
    idx = np.arange(0, len(x) - 1, razon)
    return np.interp(idx, np.arange(len(x)), x)


def cantante(x, cents, deriva_cents=7.0, periodo_s=9.0, semilla=0):
    """Una copia con vida propia: entra corrida y se va a la deriva.

    Lo que hace que un unisono suene a CORO y no a chorus no es la desafinacion fija,
    es que cada cantante arranca un poquito distinto y se va yendo. Con desafinacion
    constante las copias mantienen su relacion de fase y el oido las funde en una
    sola voz mas gorda. Con deriva lenta e independiente la relacion cambia todo el
    tiempo y aparecen varias gargantas.

    Se implementa como velocidad de lectura variable: se integra una tasa que oscila
    despacio y se lee el original por ese indice. Al ser velocidad y no shifter, cada
    cantante tiene ademas su propio tamano de cuerpo, porque los formantes se mueven
    con el tono.
    """
    rng = np.random.RandomState(semilla)
    n = len(x)
    # tres osciladores lentos incoherentes: no es un LFO, es deriva
    t = np.arange(n) / SR
    d = sum(rng.uniform(0.5, 1.0) * np.sin(2 * np.pi * t / (periodo_s * f) + rng.uniform(0, 6.28))
            for f in (1.0, 1.7, 2.9)) / 2.4
    tasa = 2.0 ** ((cents + deriva_cents * d) / 1200.0)
    idx = np.cumsum(tasa)
    idx = idx[idx < n - 1]
    return np.interp(idx, np.arange(n), x)


def puerta(x, umbral_db=-38, suavizado_ms=40):
    """Baja lo que hay entre frases. La toma es de celular y el piso de ruido, con
    esto estirado y amplificado, se vuelve una capa de siseo."""
    e = envolvente(x, 30)
    g = np.clip(e / (e.max() * 10 ** (umbral_db / 20)), 0, 1) ** 1.5
    w = max(int(suavizado_ms / 1000 * SR), 1)
    return x * np.convolve(g, np.ones(w) / w, "same")


def silabas(x, umbral_db=-30, minimo_ms=140):
    """Encuentra donde arranca y termina cada silaba, por envolvente.

    Devuelve una lista de (inicio, fin) en muestras.
    """
    e = envolvente(x, 25)
    activo = e > e.max() * 10 ** (umbral_db / 20)
    bordes = np.diff(activo.astype(np.int8))
    inicios = list(np.flatnonzero(bordes == 1) + 1)
    finales = list(np.flatnonzero(bordes == -1) + 1)
    if activo[0]:
        inicios.insert(0, 0)
    if activo[-1]:
        finales.append(len(x))
    minimo = int(minimo_ms / 1000 * SR)
    return [(a, b) for a, b in zip(inicios, finales) if b - a >= minimo]


def despedazar(x, hueco_s=0.9, estirado=1.08, golpe=0.85):
    """El tratamiento Sardaukar: cada silaba se separa, se estira y SE GOLPEA.

    Es la tecnica del canto Sardaukar de Dune (`docs/44`): se despedaza la frase en
    silabas, se estira cada una, se dejan huecos entre ellas, y despues se golpea
    cada silaba con compresion brutal. En palabras de Zimmer, un compresor sobreusado
    "se siente como golpearte la cabeza contra el marco de la puerta", y eso es lo que
    hace que cada silaba suene peligrosa en vez de bonita.

    Es lo contrario de lo que veniamos haciendo. Estirar y suavizar la frase entera da
    un pad; despedazarla y golpearla da una amenaza. El hueco es la mitad del efecto:
    sin silencio antes, el golpe no se siente como golpe.

    `golpe` es cuanto se aplasta cada silaba contra su propio pico: en 0 no hace nada,
    en 1 la silaba entera queda al nivel de su transitorio.
    """
    trozos = silabas(x)
    if not trozos:
        return x

    salida = []
    for a, b in trozos:
        s = x[a:b].copy()
        # apenas se estira: por velocidad tambien BAJA el tono, y encima de la
        # bajada de cinta del stack se iba a zona de rumble sin caracter de voz
        if estirado != 1.0:
            idx = np.arange(0, len(s) - 1, 1.0 / estirado)
            s = np.interp(idx, np.arange(len(s)), s)

        # EL GOLPE: se divide por la propia envolvente, o sea que todo lo que decae se
        # levanta hasta el nivel del ataque. Es compresion de rango infinito.
        e = envolvente(s, 45)
        s = s * (1.0 - golpe + golpe * (e.max() / (e + 1e-6)) ** 0.85)
        s = np.tanh(s / (np.abs(s).max() or 1.0) * 1.7) / np.tanh(1.7)

        # bordes propios para que el hueco sea silencio de verdad y no un corte
        f = min(int(0.012 * SR), len(s) // 4)
        if f > 1:
            s[:f] *= np.linspace(0, 1, f)
            s[-f:] *= np.linspace(1, 0, f)

        salida.append(s)
        salida.append(np.zeros(int(hueco_s * SR)))

    return np.concatenate(salida)


def coro(fuente, f0_medido, dur=DUR):
    """El stack de tres voces, cada una entrando escalonada.

    Las entradas escalonadas son lo que hace que suene a varias gargantas y no a una
    voz con efectos: en un coro real nadie arranca exactamente junto.
    """
    # El tratamiento Sardaukar va ANTES de armar el stack: se despedaza la frase una
    # vez y de ahi salen las 36 gargantas, no al reves.
    seco = despedazar(puerta(fuente))
    n = int(dur * SR)
    mezcla = np.zeros((n, 2))

    for i, (nombre, factor, ganancia) in enumerate(VOCES):
        objetivo = FUND_BASE * factor
        razon = objetivo / f0_medido          # <1 baja y alarga, >1 sube y acorta
        voz = cinta(seco, razon)
        voz /= np.abs(voz).max() or 1.0

        # cada altura dice la frase tres veces a lo largo del tema...
        for j, frac in enumerate((0.07, 0.38, 0.68)):
            arranque = dur * frac + i * 6.5
            # ...y cada vez son CUATRO cantantes, no una copia. Cada uno con su
            # desafinacion, su deriva, su retardo de entrada y su lugar en el estereo.
            for k in range(CANTANTES):
                sem = 100 * i + 10 * j + k
                rng = np.random.RandomState(sem)
                v = cantante(voz, cents=rng.uniform(-9, 9), deriva_cents=rng.uniform(4, 11),
                             periodo_s=rng.uniform(6.5, 14.0), semilla=sem)
                # nadie ataca junto: hasta 90 ms de diferencia entre gargantas
                retardo = int(rng.uniform(0, 0.09) * SR)
                pos = int(arranque * SR) + retardo
                largo = min(len(v), n - pos)
                if largo <= 0:
                    continue
                # repartidos por el estereo, no dos al centro
                lado = -1.0 + 2.0 * (k + 0.5) / CANTANTES
                pan = np.array([np.sqrt((1 - lado) / 2), np.sqrt((1 + lado) / 2)]) * 1.414
                g = ganancia * rng.uniform(0.75, 1.0) * (0.9 + 0.1 * j) / np.sqrt(CANTANTES)
                mezcla[pos:pos + largo] += v[:largo, None] * pan * g

    mezcla /= np.abs(mezcla).max() or 1.0

    # el cuerpo: saturacion suave. tanh y NO abs()
    # (memory/abs_rectifier_exciter_antipattern.md)
    mezcla = np.tanh(mezcla * 1.8) / np.tanh(1.8)
    mezcla = lp(mezcla, 1500)              # el LPF va DESPUES del tanh, por los armonicos

    mezcla = hp(mezcla, 32)
    mezcla = mono_graves(mezcla, 160)      # el sub al centro, la quinta ancha
    mezcla = respiracion(mezcla, 0.10, periodo=41.0)   # otro primo libre

    # el espacio: la sala enorme es la mitad del sonido Dune
    cola = camara(mezcla, 14, ir_lowpass=900, wet=1.0, semilla=11000, pre_ms=180)
    x = 0.80 * mezcla + 0.85 * cola[:len(mezcla)]

    x = hp(x, 30)
    x = fades(x, 3.0)
    return x / (np.abs(x).max() or 1.0) * 10 ** (-6.0 / 20)


def main():
    np.random.seed(SEMILLA)
    print(f"  fundamental de la base: {FUND_BASE} Hz")
    for nombre, factor, _ in VOCES:
        print(f"    {nombre:8} {FUND_BASE * factor:7.2f} Hz")
    print()

    salidas = []
    for clave in TOMAS:
        _, f0, etiqueta = TOMAS[clave]
        razon = FUND_BASE / f0
        print(f"  {etiqueta:22} F0 {f0:6.1f} Hz -> raiz {FUND_BASE} Hz "
              f"(cinta ×{razon:.3f}, {1200*np.log2(razon):+.0f} cents)")
        x = coro(cargar(clave), f0)
        ruta = os.path.join(AQUI, f"coro_{clave}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        print(f"  -> {os.path.relpath(ruta, RAIZ)}")
        salidas.append((f"coro_{clave}", x))

    # y las dos sobre la mezcla, para escucharlas en contexto
    sr, base = wavfile.read(os.path.join(AQUI, "mix_v3.wav"))
    base = base.astype(np.float64) / 32768.0
    n = min(len(base), int(DUR * SR))
    for nombre, x in list(salidas):
        m = base[:n] + x[:n] * 10 ** (-7 / 20)
        m = m / np.abs(m).max() * 10 ** (-6.0 / 20)
        ruta = os.path.join(AQUI, f"mix_v4_{nombre.split('_')[1]}.wav")
        wavfile.write(ruta, SR, (m * 32767).astype(np.int16))
        print(f"  -> {os.path.relpath(ruta, RAIZ)}")
        salidas.append((f"mix_v4_{nombre.split('_')[1]}", m))

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    for nombre, x in salidas:
        medir(nombre, x)


if __name__ == "__main__":
    sys.exit(main())
