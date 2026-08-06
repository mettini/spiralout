#!/usr/bin/env python3
"""Chequea si una grabacion sirve como fuente, y para que capa.

La leccion del primer experimento de deformacion: la fuente manda. Una bomba con
el 92% de la energia en una banda no se convierte en textura con ningun
procesamiento. Esto lo dice ANTES de perder una tarde.

Los cuatro criterios estan en `docs/38_capas_dark_ambient.md`: banda ancha,
movimiento interno, algun transitorio, y sin comprimir.

Uso:
    python3.10 scripts/check_source.py grabacion.wav
    python3.10 scripts/check_source.py grabacion.m4a     (convierte con ffmpeg)
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import welch

NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BANDAS = [(20, 60, "20-60 sub"), (60, 120, "60-120 sub"), (120, 400, "120-400 cuerpo"),
          (400, 1500, "400-1.5k nube"), (1500, 6000, "1.5k-6k grano"), (6000, 20000, "6k+ aire")]


def nota_de(f):
    m = 69 + 12 * np.log2(f / 440.0)
    n = int(round(m))
    return f"{NOTAS[n % 12]}{n // 12 - 1}", (m - n) * 100


def cargar(ruta):
    if not ruta.lower().endswith(".wav"):
        tmp = os.path.join(tempfile.gettempdir(), "check_source.wav")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", ruta,
                        "-c:a", "pcm_s16le", tmp, "-y"], check=True)
        ruta = tmp
    sr, d = wavfile.read(ruta)
    d = d.astype(np.float64)
    if d.ndim > 1:
        d = d.mean(axis=1)
    if np.abs(d).max() > 0:
        d /= np.abs(d).max()
    return sr, d


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ruta = sys.argv[1]
    sr, d = cargar(ruta)
    dur = len(d) / sr
    fr, ps = welch(d, sr, nperseg=min(32768, len(d) // 4 * 2 or 1024))
    tot = ps.sum()
    banda = lambda a, b: 100 * ps[(fr >= a) & (fr < b)].sum() / tot

    print(f"\n  {os.path.basename(ruta)} · {dur:.1f}s · {sr} Hz\n")
    print("  REPARTO ESPECTRAL")
    reparto = {}
    for a, b, nombre in BANDAS:
        if a >= sr / 2:
            continue
        v = banda(a, min(b, sr / 2 - 1))
        reparto[nombre] = v
        print(f"    {nombre:16} {v:5.1f}%  {'#' * int(v / 2)}")

    # 1. banda ancha o tono
    pico_bin = 100 * ps.max() / tot
    octava_max = max(banda(f, f * 2) for f in (20, 40, 80, 160, 320, 640, 1280)
                     if f * 2 < sr / 2)
    print(f"\n  CRITERIOS")
    tono = octava_max > 80 or pico_bin > 25
    print(f"    banda ancha       {'NO — es un tono' if tono else 'si'}"
          f"   (octava mas cargada {octava_max:.0f}%, pico en un bin {pico_bin:.1f}%)")

    # 2. movimiento interno: cuanto varia el RMS y el centroide a lo largo del tiempo
    w = max(int(0.25 * sr), 1024)
    rms, cen = [], []
    for i in range(0, len(d) - w, w):
        seg = d[i:i + w]
        rms.append(np.sqrt((seg ** 2).mean()) + 1e-12)
        f2, p2 = welch(seg, sr, nperseg=min(2048, w))
        cen.append((f2 * p2).sum() / (p2.sum() + 1e-20))
    rango_rms = 20 * np.log10(max(rms) / min(rms))
    var_cen = 100 * np.std(cen) / (np.mean(cen) + 1e-9)
    movimiento = rango_rms > 6 or var_cen > 15
    print(f"    movimiento        {'si' if movimiento else 'NO — es estatico'}"
          f"   (nivel varia {rango_rms:.1f} dB, timbre {var_cen:.0f}%)")

    # 3. transitorios: saltos de energia entre ventanas cortas
    w2 = max(int(0.01 * sr), 64)
    env = np.array([np.sqrt((d[i:i + w2] ** 2).mean()) for i in range(0, len(d) - w2, w2)]) + 1e-12
    saltos = int((np.diff(20 * np.log10(env)) > 9).sum())
    print(f"    transitorios      {'si' if saltos else 'NO — todo sostenido'}"
          f"   ({saltos} saltos de mas de 9 dB)")

    # 4. compresion: los codecs cortan seco arriba
    corte = fr[np.where(np.cumsum(ps) / tot > 0.999)[0][0]]
    lossy = not ruta.lower().endswith(".wav") or corte < sr / 2 * 0.75
    print(f"    sin comprimir     {'DUDOSO' if lossy else 'si'}"
          f"   (el 99.9% de la energia termina en {corte:.0f} Hz)")

    pk = fr[np.argmax(ps)]
    nm, ct = nota_de(pk)
    print(f"\n  ALTURA            {pk:.1f} Hz = {nm} {ct:+.0f} cents")
    if abs(ct) > 25:
        print(f"    ojo: esta a {abs(ct):.0f} cents de la nota temperada. Si le vas a poner")
        print(f"    algo tonal encima, afinalo a esta altura o vas a chocar (docs/38).")

    print(f"\n  PARA QUE CAPA SIRVE")
    dominante = max(reparto, key=reparto.get)
    usos = []
    if reparto.get("20-60 sub", 0) + reparto.get("60-120 sub", 0) > 40:
        usos.append("1 · cama de sub")
    if reparto.get("120-400 cuerpo", 0) > 25:
        usos.append("2 · cuerpo")
    if reparto.get("400-1.5k nube", 0) > 20:
        usos.append("3 · nube")
    if reparto.get("1.5k-6k grano", 0) > 12:
        usos.append("4 · grano")
    if reparto.get("6k+ aire", 0) > 5:
        usos.append("5 · aire")
    if saltos >= 3:
        usos.append("6 · eventos")
    print("    " + ("\n    ".join(usos) if usos else "ninguna clara — banda demasiado estrecha"))
    print(f"    (domina {dominante})")

    if tono and not movimiento:
        print(f"\n  VEREDICTO: tono estatico. Sirve de cama y nada mas, y va a tender")
        print(f"  a acoplar. Buscar una fuente con carga variable, o grabar el")
        print(f"  arranque y la parada del motor.")
    elif tono:
        print(f"\n  VEREDICTO: tono, pero con movimiento. Cama utilizable.")
    else:
        print(f"\n  VEREDICTO: textura. Sirve para varias capas.")
    print()


if __name__ == "__main__":
    sys.exit(main())
