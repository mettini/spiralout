#!/usr/bin/env python3
"""Thermal Mass / Cloud Chamber — render reproducible desde la fuente.

Dos piezas de 30 s sacadas de la MISMA grabacion: la bomba de una losa radiante
en el subsuelo de una casa de la calle Ortiz de Ocampo, 15 segundos grabados con
el celular. Thermal Mass es el sotano, Cloud Chamber es lo que flota arriba.
Estan pensadas para sonar juntas: sus bandas casi no se cruzan.

    python3.10 lab/thermal_mass/render.py

Requiere ffmpeg (para el m4a) + numpy, scipy, pyloudnorm.
El porque de cada paso esta en README.md.
"""
import os
import subprocess
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.ndimage import median_filter
from scipy.signal import (butter, find_peaks, iirnotch, istft, oaconvolve,
                          resample_poly, sosfilt, sosfiltfilt, stft, tf2sos, welch)

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from paulstretch import make_ir, paulstretch  # noqa: E402

FUENTES = {
    # el hum de la bomba: un tono. Sirve de cama y de nube
    "bomba": ("ortiz_de_ocampo.m4a", "ortiz_de_ocampo_22k.wav"),
    # el lavarropas sarandeandose: tiene GOLPES. De aca sale el cuerpo y los eventos
    "lavarropas": ("ortiz_de_ocampo_3.m4a", "ortiz_de_ocampo_3_22k.wav"),
}
SR = 22050          # el SR del proyecto, y de sobra: la fuente no pasa de 500 Hz
DUR = 30.0
# Paulstretch randomiza la fase, asi que sin semilla cada corrida suena distinto.
# 24 por el hexagrama 24, la marca del proyecto.
SEMILLA = 24

# La frecuencia culpable del acople, medida sobre la fuente estirada y bajada
# dos octavas. Si cambias el pitch, hay que volver a medirla.
RESONANCIA_TM = 71.3


# ---------------------------------------------------------------- utilidades
def lp(x, hz, sr=SR, orden=4):
    return np.stack([sosfilt(butter(orden, hz / (sr / 2), "low", output="sos"), x[:, c])
                     for c in range(x.shape[1])], axis=1)


def hp(x, hz, sr=SR, orden=2):
    return np.stack([sosfilt(butter(orden, hz / (sr / 2), "high", output="sos"), x[:, c])
                     for c in range(x.shape[1])], axis=1)


def notch_parcial(x, f0, q, mezcla, sr=SR):
    """Notch en paralelo: `mezcla` controla la profundidad sin matar la banda."""
    bq = tf2sos(*iirnotch(f0 / (sr / 2), Q=q))
    filtrado = np.stack([sosfilt(bq, x[:, c]) for c in range(x.shape[1])], axis=1)
    return (1 - mezcla) * x + mezcla * filtrado


def barrido(x, hz_a, hz_b, periodo, sr=SR):
    """Cruce lento entre dos low-pass: movimiento sin filtro variable en el tiempo."""
    t = np.arange(len(x)) / sr
    l = (0.5 + 0.5 * np.sin(2 * np.pi * t / periodo))[:, None]
    return lp(x, hz_a) * (1 - l) + lp(x, hz_b) * l


def respiracion(x, prof, periodo, sr=SR):
    t = np.arange(len(x)) / sr
    return x * (1 + prof * np.sin(2 * np.pi * t / periodo))[:, None]


def camara(x, segundos, ir_lowpass, wet, sr=SR, semilla=1000, pre_ms=0):
    """Convolucion con IR sintetica. Una IR distinta por canal = mas ancho.
    `pre_ms` es el pre-delay: la senal de tamano mas fuerte que tiene el oido.
    Con wet=1.0 devuelve solo la cola, para mezclarla aparte."""
    x = x.astype(np.float32)
    mojado = np.zeros_like(x)
    pre = int(pre_ms / 1000 * sr)
    for c in range(x.shape[1]):
        ir = make_ir(sr, segundos, ir_lowpass, seed=semilla + c).astype(np.float32)
        y = oaconvolve(x[:, c], ir)[:len(x)]
        if pre:
            y = np.concatenate([np.zeros(pre, np.float32), y])[:len(x)]
        mojado[:, c] = y / (np.abs(y).max() or 1.0)
    if wet >= 1.0:
        return mojado
    return (1 - wet) * x / (np.abs(x).max() or 1.0) + wet * mojado


def mono_graves(x, hz, sr=SR):
    """Graves al centro, ancho arriba. Con fase cero: con un IIR causal la resta
    'senal - lowpass' no es un complemento y deja residuo decorrelacionado."""
    sos = butter(4, hz / (sr / 2), "low", output="sos")
    bajo = np.stack([sosfiltfilt(sos, x[:, c]) for c in range(x.shape[1])], axis=1)
    return (x - bajo) + bajo.mean(axis=1, keepdims=True)


def estirar_estereo(mono, stretch, window, sr=SR):
    """Dos pasadas: Paulstretch randomiza la fase, asi que dos corridas dan el
    mismo espectro con fase distinta. Estereo real, sin widener."""
    a, b = paulstretch(mono, sr, stretch, window), paulstretch(mono, sr, stretch, window)
    n = min(len(a), len(b))
    return np.stack([a[:n], b[:n]], axis=1)


def bajar_octavas(x, octavas):
    """Por velocidad, como una cinta lenta: pitchea Y alarga."""
    f = 2.0 ** octavas
    idx = np.arange(0, len(x) - 1, 1.0 / f)
    src = np.arange(len(x))
    return np.stack([np.interp(idx, src, x[:, c]) for c in range(x.shape[1])], axis=1)


def del_medio(x, segundos, sr=SR):
    """El arranque de un stretch siempre es lo mas pobre."""
    n = int(segundos * sr)
    off = max(0, (len(x) - n) // 2)
    return x[off:off + n]


def fades(x, segundos=2.0, sr=SR):
    f = int(segundos * sr)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x


def envolvente(x, ms, sr=SR):
    w = max(int(ms / 1000 * sr), 1)
    return np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "same")) + 1e-9


def percusivo(mono, sr=SR):
    """Separa lo que GOLPEA de lo que zumba, por filtro de mediana sobre el
    espectrograma (HPSS): mediana en el tiempo aisla lo estacionario (motor,
    ruido), mediana en frecuencia aisla lo percusivo. Devuelve lo segundo."""
    f, t, Z = stft(mono, sr, nperseg=2048, noverlap=1536)
    M = np.abs(Z)
    perc = median_filter(M, size=(31, 1))
    sost = median_filter(M, size=(1, 31))
    mascara = (perc ** 2) / (perc ** 2 + sost ** 2 + 1e-12)
    _, y = istft(Z * mascara, sr, nperseg=2048, noverlap=1536)
    return y


def transient_shaper(x, rapida_ms=40, lenta_ms=900, fuerza=0.8):
    """Realza el ataque respecto de su propia cola. Es lo que hace que un golpe
    sobresalga de su reverb en vez de ahogarse."""
    m = x.mean(axis=1)
    g = np.clip((envolvente(m, rapida_ms) / envolvente(m, lenta_ms)) ** fuerza, 0.4, 3.5)
    return x * g[:, None]


def expansor(x, umbral_db=-26, ratio=2.0, suavizado_ms=50, sr=SR):
    """Lo contrario de un compresor: hunde lo que esta bajo. Limpia el ruido
    residual entre golpes sin tocar el ataque."""
    e = envolvente(x, 25)
    g = np.clip((e / (e.max() * 10 ** (umbral_db / 20))) ** ratio, 0, 1)
    w = int(suavizado_ms / 1000 * sr)
    return x * np.convolve(g, np.ones(w) / w, "same")


def ducking(seco, prof=0.75, ventana_ms=120, release_s=1.2, sr=SR):
    """Ganancia para la cola: se aparta mientras pega el golpe y crece despues.
    Permite una camara enorme sin que se coma el ataque."""
    d = envolvente(seco.mean(axis=1), ventana_ms)
    d /= d.max()
    g = 1 - prof * np.clip(d * 3, 0, 1)
    w = int(release_s * sr)
    return np.convolve(g, np.ones(w) / w, "same")[:, None]


# ---------------------------------------------------------------- las piezas
def thermal_mass(fuente, dur=DUR):
    """El sotano. Pastoso, grave, lento, SIN saturacion."""
    x = estirar_estereo(fuente, stretch=max(45, dur / 4), window=5.0)  # ventana 5 s: maximo fundido
    x = bajar_octavas(x, 2.0)
    x = del_medio(x, dur)
    x = notch_parcial(x, RESONANCIA_TM, q=6, mezcla=0.75)  # ~-9 dB solo en 71 Hz
    x = barrido(x, 220, 380, periodo=17.0)
    x = respiracion(x, 0.14, periodo=13.0)
    x = camara(x, 14, ir_lowpass=800, wet=0.65)
    x = x - x.mean(axis=0, keepdims=True)
    x = hp(x, 28)
    x = mono_graves(x, 120)
    x = fades(x)
    return x / np.abs(x).max() * 10 ** (-9.0 / 20)


def cloud_chamber(fuente, lufs_objetivo, dur=DUR):
    """La capa media. Nube de copias transpuestas, desafinadas y desfasadas."""
    base = estirar_estereo(fuente, stretch=max(45, dur / 3), window=1.5)  # ventana chica: mas detalle
    n = int(dur * SR)
    # (semitonos, ganancia, cents de desafinacion, offset en segundos)
    capas = [(0, 1.00, 0, 0.0), (7, 0.55, 4, 2.5), (12, 0.45, -5, 5.0),
             (19, 0.30, 6, 7.5), (24, 0.22, -7, 10.0)]
    x = np.zeros((n, 2))
    for semis, g, cents, off_s in capas:
        f = 2.0 ** ((semis + cents / 100.0) / 12.0)
        idx = np.arange(0, len(base) - 1, f)
        y = np.stack([np.interp(idx, np.arange(len(base)), base[:, c]) for c in range(2)], axis=1)
        ini = int(off_s * SR) + max(0, (len(y) - n) // 2)
        y = y[ini:ini + n]
        if len(y) < n:
            y = np.pad(y, ((0, n - len(y)), (0, 0)))
        y /= (np.abs(y).max() or 1.0)
        x += y * g * (np.array([1.0, 0.65]) if semis % 24 else np.array([0.65, 1.0]))

    x = hp(x, 200)                                    # deja el sotano libre
    for f0 in resonancias(x, 200, 3000, cuantas=3):   # de-resonancia
        x = notch_parcial(x, f0, q=9, mezcla=0.55)
    x = barrido(x, 2200, 5000, periodo=23.0)
    x = respiracion(x, 0.10, periodo=19.0)
    x = 0.7 * x + 0.3 * lp(x, 4000)                   # tilt: se sienta detras
    x = camara(x, 10, ir_lowpass=1500, wet=0.55, semilla=2000)
    x = x - x.mean(axis=0, keepdims=True)
    x = hp(x, 180)
    x = fades(x)
    x /= np.abs(x).max()
    medidor = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), lufs_objetivo)
    if np.abs(x).max() > 0.98:                        # el match de LUFS puede pasarse
        x *= 0.98 / np.abs(x).max()
    return x



def manifold(fuente, lufs_objetivo, dur=DUR):
    """La capa de cuerpo, desde el lavarropas. Afinada una octava arriba del bed.

    Su fundamental cruda esta en 63 Hz (B1 +35 cents) y el bed en 71,3: son 214
    cents, casi un tono entero, y en la zona grave eso es barro. Subirla 14,14
    semitonos la deja exactamente una octava arriba del bed, consonante, y su
    contenido aterriza en la banda de cuerpo.
    """
    x = estirar_estereo(fuente, stretch=max(45, dur / 2), window=2.0)
    f = 2.0 ** (14.14 / 12.0)
    idx = np.arange(0, len(x) - 1, f)
    x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
    x = del_medio(x, dur)
    x = hp(x, 120)                                    # le deja el sotano al bed
    x = barrido(x, 600, 1200, periodo=19.0)
    x = respiracion(x, 0.12, periodo=11.0)
    x = camara(x, 12, ir_lowpass=1000, wet=0.55, semilla=3000)
    x = x - x.mean(axis=0, keepdims=True)
    x = hp(x, 110)
    x = fades(x)
    x /= np.abs(x).max()
    medidor = pyln.Meter(SR)
    x = pyln.normalize.loudness(x, medidor.integrated_loudness(x), lufs_objetivo)
    if np.abs(x).max() > 0.98:
        x *= 0.98 / np.abs(x).max()
    return x


def flywheel(fuente, dur=DUR):
    """La capa de eventos: el sarandeo del lavarropas como maquinaria pesada.

    Aca NO se usa Paulstretch: randomiza la fase, o sea que destruye el ataque, y
    el ataque es todo. Va enlentecido por velocidad (cinta lenta), que alarga y
    baja el tono dejando el transitorio intacto.

    Y el ritmo se separa del tono: en vez de enlentecer mas (que hundiria los
    golpes abajo de 60 Hz y les sacaria definicion), se corta cada impacto y se
    re-espacia en una linea de tiempo mas lenta. Cada golpe conserva su altura.
    """
    perc = percusivo(fuente)
    lento = np.interp(np.arange(0, len(perc) - 1, 1 / 4.0), np.arange(len(perc)), perc)
    lento /= np.abs(lento).max()

    # aislar cada golpe
    db = 20 * np.log10(envolvente(lento, 60))
    picos, _ = find_peaks(db - median_filter(db, size=int(2.5 * SR)),
                          height=8, distance=int(1.2 * SR))

    n, largo = int(dur * SR), int(4.5 * SR)
    t = np.arange(largo) / SR
    decay = np.exp(-t / 1.6)
    decay[:int(0.02 * SR)] = 1.0                      # ataque intacto, cola que muere
    linea = np.zeros((n + largo, 2))
    pos, i = int(3.0 * SR), 0                         # arranca en 3 s: el fade no debe
    while pos < n - int(1.5 * SR):                    # rampear el primer ataque
        p = picos[i % len(picos)]
        i += 1
        golpe = lento[max(0, p - int(0.05 * SR)):][:largo]
        if len(golpe) < largo:
            golpe = np.pad(golpe, (0, largo - len(golpe)))
        golpe = expansor(golpe) * decay
        g = 0.7 + 0.3 * np.random.rand()              # maquinaria: los golpes no son iguales
        pan = np.array([1.0, 0.8]) if i % 2 else np.array([0.8, 1.0])
        linea[pos:pos + largo] += golpe[:, None] * g * pan
        pos += int((5.5 + 2.0 * np.random.rand()) * SR)   # irregular, no metronomo
    x = linea[:n]

    x = lp(hp(x, 35), 2500)
    x = transient_shaper(x)
    seco = np.tanh(x / (np.abs(x).max() or 1.0) * 2.0)    # basto
    seco /= np.abs(seco).max()

    cola = camara(seco, 16, ir_lowpass=700, wet=1.0, semilla=5000, pre_ms=300)
    # el abismo: la misma cola una octava abajo y mas atras
    abismo = np.stack([np.interp(np.arange(0, len(cola) - 1, 0.5),
                                np.arange(len(cola)), cola[:, c]) for c in range(2)], axis=1)
    abismo = np.concatenate([np.zeros((int(0.6 * SR), 2)), lp(abismo, 250)[:len(cola)]])[:len(cola)]

    g = ducking(seco, release_s=0.8)
    x = hp(0.85 * seco + 0.72 * cola * g + 0.28 * abismo * g, 30)
    x = fades(x, 0.8)
    return x / np.abs(x).max() * 10 ** (-6.0 / 20)


def resonancias(x, desde, hasta, cuantas=3):
    """Los picos espectrales mas fuertes, separados entre si al menos un 15%."""
    fr, ps = welch(x.mean(axis=1), SR, nperseg=16384)
    banda = (fr > desde) & (fr < hasta)
    orden = fr[banda][np.argsort(ps[banda])[::-1]]
    picos = []
    for f0 in orden:
        if all(abs(f0 - p) > f0 * 0.15 for p in picos):
            picos.append(f0)
        if len(picos) == cuantas:
            break
    return picos


# ---------------------------------------------------------------- reporte
def medir(nombre, x):
    medidor = pyln.Meter(SR)
    up = np.stack([resample_poly(x[:, c], 4, 1) for c in range(2)], axis=1)
    fr, ps = welch(x.mean(axis=1), SR, nperseg=16384)
    tot = ps.sum()
    b = lambda p, q: 100 * ps[(fr >= p) & (fr < q)].sum() / tot
    rms = np.sqrt((x ** 2).mean())
    print(f"  {nombre:16}{medidor.integrated_loudness(x):6.1f} "
          f"{20*np.log10(np.abs(x).max()):6.1f} {20*np.log10(np.abs(up).max()):7.1f} "
          f"{20*np.log10(np.abs(x).max()/rms):6.1f} {np.corrcoef(x[:,0],x[:,1])[0,1]:+6.2f}  "
          f"{b(20,60):5.1f} {b(60,120):5.1f} {b(120,250):6.1f} {b(250,500):6.1f} "
          f"{b(500,1000):5.1f} {b(1000,3000):5.1f}")


def cargar(clave):
    m4a, wav = (os.path.join(AQUI, "source", n) for n in FUENTES[clave])
    if not os.path.exists(wav):
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", m4a,
                        "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", wav, "-y"], check=True)
    sr, x = wavfile.read(wav)
    assert sr == SR, f"{wav} esta a {sr} Hz, se esperaba {SR}"
    x = x.astype(np.float64)
    x /= np.abs(x).max()
    # el lavarropas trae rumble de manejo abajo de 30 Hz (era el 1,5%)
    return sosfilt(butter(2, 30 / (SR / 2), "high", output="sos"), x)


def main():
    np.random.seed(SEMILLA)          # render determinista, byte por byte
    bomba = cargar("bomba")
    lavarropas = cargar("lavarropas")

    tm = thermal_mass(bomba)
    lufs = pyln.Meter(SR).integrated_loudness(tm)
    cc = cloud_chamber(bomba, lufs)                   # igualado por sonoridad, no por pico
    mf = manifold(lavarropas, lufs)
    fw = flywheel(lavarropas)

    # la mezcla, con los niveles de docs/38 por capa
    n = min(len(tm), len(cc), len(mf), len(fw))
    mezcla = (tm[:n] * 1.0 + mf[:n] * 10 ** (-4 / 20)
              + cc[:n] * 10 ** (-8 / 20) + fw[:n] * 10 ** (-1 / 20))
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-6.0 / 20)

    for nombre, x in (("thermal_mass", tm), ("manifold", mf),
                      ("cloud_chamber", cc), ("flywheel", fw), ("mix_v1", mezcla)):
        ruta = os.path.join(AQUI, f"{nombre}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        print(f"-> {os.path.relpath(ruta, RAIZ)}")

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    for nombre, x in (("thermal_mass", tm), ("manifold", mf),
                      ("cloud_chamber", cc), ("flywheel", fw), ("mix_v1", mezcla)):
        medir(nombre, x)


if __name__ == "__main__":
    sys.exit(main())
