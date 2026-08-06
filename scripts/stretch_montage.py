#!/usr/bin/env python3
"""Montaje de secciones estiradas: una variacion cada N segundos.

El problema: Paulstretch con un window fijo da una textura fija. Si estiras 15
segundos a 30 minutos, son 30 minutos de lo mismo.

La solucion no es automatizar un filtro (eso es maquillaje): es cortar el
material en pedazos distintos y estirar cada uno con un window distinto. Cada
seccion trae material nuevo Y otra textura. Es lo mismo que automatizar Grain
Size en Ableton, pero por secciones en vez de continuo.

La cadena de acabado se aplica al final, sobre la pieza armada, no por seccion:
high-pass, mono en los graves y saturacion paralela (ver `paulstretch.py`).

Uso:
    python3 scripts/stretch_montage.py fuente.wav salida.wav --seccion 18 --cross 3
"""
import argparse
import os
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, oaconvolve, sosfilt, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paulstretch import make_ir, paulstretch  # noqa: E402

# (inicio en la fuente, largo, window). Windows distintos = texturas distintas.
# El orden va de mas fundido a mas granular y vuelve: da forma, no solo cambio.
# Pedazos SOLAPADOS de 6s: un window grande necesita fuente larga (el algoritmo
# pide al menos dos ventanas por pedazo), y el window grande es el que funde.
SECCIONES = [
    (0.0, 6.0, 2.5),
    (3.0, 6.0, 1.0),
    (6.0, 6.0, 2.0),
    (9.0, 6.0, 0.6),
]


def seccion(data, sr, ini, largo, window, stretch, octaves, dur_out):
    """Estira un pedazo de la fuente y devuelve `dur_out` segundos."""
    a, b = int(ini * sr), int((ini + largo) * sr)
    chunk = data[a:b]
    if len(chunk) < int(window * sr) * 2:
        raise SystemExit(f"la seccion en {ini}s es mas corta que su window de {window}s")

    # dos pasadas: mismo espectro, fase distinta = estereo real
    l, r = paulstretch(chunk, sr, stretch, window), paulstretch(chunk, sr, stretch, window)
    n = min(len(l), len(r))
    out = np.stack([l[:n], r[:n]], axis=1)

    if octaves > 0:                              # cinta lenta: pitchea y alarga
        f = 2.0 ** octaves
        idx = np.arange(0, len(out) - 1, 1.0 / f)
        src = np.arange(len(out))
        out = np.stack([np.interp(idx, src, out[:, c]) for c in range(2)], axis=1)

    need = int(dur_out * sr)
    if len(out) < need:
        raise SystemExit(f"la seccion en {ini}s salio de {len(out)/sr:.1f}s, se pidieron {dur_out}s")
    # del medio, no del arranque: el principio de un stretch siempre es el mas pobre
    off = (len(out) - need) // 2
    return out[off:off + need]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--seccion", type=float, default=18.0, help="segundos por seccion")
    p.add_argument("--cross", type=float, default=3.0, help="segundos de cruce entre secciones")
    p.add_argument("--stretch", type=float, default=45.0)
    p.add_argument("--octaves-down", type=float, default=2.0)
    p.add_argument("--space", type=float, default=30.0)
    p.add_argument("--space-lowpass", type=float, default=800.0)
    p.add_argument("--wet", type=float, default=0.95)
    p.add_argument("--lowpass", type=float, default=220.0)
    p.add_argument("--hp", type=float, default=28.0)
    p.add_argument("--mono-below", type=float, default=120.0)
    p.add_argument("--drive", type=float, default=0.35)
    p.add_argument("--peak-db", type=float, default=-6.0)
    a = p.parse_args()

    sr, data = wavfile.read(a.entrada)
    data = data.astype(np.float64)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if np.abs(data).max() > 0:
        data /= np.abs(data).max()

    partes = []
    for ini, largo, window in SECCIONES:
        s = seccion(data, sr, ini, largo, window, a.stretch, a.octaves_down, a.seccion)
        s /= np.abs(s).max() or 1.0
        partes.append(s)
        print(f"   seccion {ini:4.1f}s  window {window:4.1f}s  ->  {a.seccion:.0f}s")

    # armado con crossfade
    x = int(a.cross * sr)
    total = sum(len(s) for s in partes) - x * (len(partes) - 1)
    out = np.zeros((total, 2))
    fade_in = np.linspace(0, 1, x)[:, None]
    pos = 0
    for i, s in enumerate(partes):
        s = s.copy()
        if i > 0:
            s[:x] *= fade_in
            out[pos:pos + x] *= (1 - fade_in)
        out[pos:pos + len(s)] += s
        pos += len(s) - x

    # cadena de acabado, sobre la pieza entera
    out = out.astype(np.float32)
    if a.space > 0:
        wet = np.zeros_like(out)
        for c in range(2):
            ir = make_ir(sr, a.space, a.space_lowpass, seed=1000 + c).astype(np.float32)
            w = oaconvolve(out[:, c], ir)[:len(out)]
            wet[:, c] = w / (np.abs(w).max() or 1.0)
        out = (1 - a.wet) * out / (np.abs(out).max() or 1.0) + a.wet * wet

    if a.lowpass > 0:
        sos = butter(4, a.lowpass / (sr / 2), btype="low", output="sos")
        out = np.stack([sosfilt(sos, out[:, c]) for c in range(2)], axis=1)

    out = out - out.mean(axis=0, keepdims=True)
    if a.hp > 0:
        sos = butter(2, a.hp / (sr / 2), btype="high", output="sos")
        out = np.stack([sosfilt(sos, out[:, c]) for c in range(2)], axis=1)


    if a.drive > 0:
        norm = np.abs(out).max() or 1.0
        out = (1 - a.drive) * out + a.drive * (np.tanh(out / norm * 3.0) * norm)

    if a.mono_below > 0 and out.shape[1] == 2:
        # sosfiltfilt (fase cero) a proposito: con un IIR causal, "senal - lowpass"
        # NO es un complemento porque el lowpass sale desfasado, y deja residuo
        # decorrelacionado en los graves. Con fase cero la resta es exacta.
        # Y va DESPUES del drive: saturar decorrelaciona, asi que la imagen se
        # arregla al final.
        sos = butter(4, a.mono_below / (sr / 2), btype="low", output="sos")
        low = np.stack([sosfiltfilt(sos, out[:, c]) for c in range(2)], axis=1)
        out = (out - low) + low.mean(axis=1, keepdims=True)

    # fade de entrada y salida, para que no arranque ni corte en seco
    f = int(2.0 * sr)
    out[:f] *= np.linspace(0, 1, f)[:, None]
    out[-f:] *= np.linspace(1, 0, f)[:, None]

    peak = np.abs(out).max()
    if peak > 0:
        out = out / peak * (10 ** (a.peak_db / 20))
    wavfile.write(a.salida, sr, (out * 32767).astype(np.int16))
    print(f"-> {a.salida}  {len(out)/sr:.0f}s  {len(SECCIONES)} secciones, "
          f"cruce {a.cross:g}s, pico {a.peak_db:g} dBFS")


if __name__ == "__main__":
    sys.exit(main())
