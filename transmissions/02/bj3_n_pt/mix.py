#!/usr/bin/env python3
"""Mezcla con arco: las cuatro capas entrando y saliendo a lo largo de 2 minutos.

El problema de sumar las cuatro capas a nivel fijo es que suena a paisaje, no a
pieza: todo empieza y termina junto, y en el medio no pasa nada. Aca cada capa
tiene su propia automatizacion de nivel, y el orden de entrada sigue el criterio
de `docs/38`: la cama define la nota, los EVENTOS definen la estructura temporal,
y el relleno se acomoda alrededor.

    python3.10 transmissions/02/bj3_n_pt/mix.py

Estructura (2:00):

    0:00  la cama sola, apareciendo desde el silencio
    0:20  entra el cuerpo, muy abajo
    0:28  primer golpe: la maquina se despierta
    0:45  entra la nube
    1:00  las cuatro, es el peso maximo
    1:25  se retiran la nube y el cuerpo
    1:40  ultimo golpe, y queda la cama con la cola
    2:00  silencio
"""
import os
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, welch

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import render as R  # noqa: E402

DUR = 120.0
SR = R.SR

# (capa, [(segundo, dB)]) — la automatizacion de cada una. -80 dB = silencio.
AUTOMATIZACION = {
    # la cama se queda en -2 hasta pasado el minuto: si sube a 0 en el 0:30,
    # justo cuando entra el cuerpo, el 0:40 se apelotona
    "thermal_mass": [(0, -80), (14, -8), (32, -2), (75, 0), (95, 0), (110, -4), (118, -30), (120, -80)],
    # el cuerpo entra mas abajo y sube mas lento, en tres tramos
    "manifold":     [(0, -80), (20, -80), (34, -14), (52, -8), (72, -5), (88, -5), (100, -14), (110, -80)],
    "cloud_chamber":[(0, -80), (45, -80), (58, -14), (72, -8), (88, -8), (98, -18), (108, -80)],
    # los golpes adelante: +3 en vez de -2
    "flywheel":     [(0, -80), (26, -80), (28, 3), (100, 3), (105, -5), (112, -80)],
}


def rampa(puntos, n, sr=SR):
    """Automatizacion en dB interpolada linealmente y convertida a ganancia."""
    t = np.arange(n) / sr
    xs = np.array([p[0] for p in puntos], float)
    ys = np.array([p[1] for p in puntos], float)
    return (10 ** (np.interp(t, xs, ys) / 20))[:, None]


def main():
    np.random.seed(R.SEMILLA)
    bomba = R.cargar("bomba")
    lavarropas = R.cargar("lavarropas")

    print("  rindiendo capas a 120 s...")
    tm = R.thermal_mass(bomba, dur=DUR)
    lufs = pyln.Meter(SR).integrated_loudness(tm)
    cc = R.cloud_chamber(bomba, lufs, dur=DUR)
    mf = R.manifold(lavarropas, lufs, dur=DUR)
    fw = R.flywheel(lavarropas, dur=DUR)

    n = min(len(tm), len(cc), len(mf), len(fw))
    capas = {"thermal_mass": tm, "manifold": mf, "cloud_chamber": cc, "flywheel": fw}
    mezcla = np.zeros((n, 2))
    for nombre, x in capas.items():
        mezcla += x[:n] * rampa(AUTOMATIZACION[nombre], n)

    # el bus: nada de compresion. Solo saca lo inaudible y centra los graves
    mezcla = mezcla - mezcla.mean(axis=0, keepdims=True)
    mezcla = np.stack([sosfilt(butter(2, 26 / (SR / 2), "high", output="sos"), mezcla[:, c])
                       for c in range(2)], axis=1)
    mezcla = R.mono_graves(mezcla, 110)
    mezcla = R.fades(mezcla, 3.0)
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-3.0 / 20)

    ruta = os.path.join(AQUI, "mix_v2_arco.wav")
    wavfile.write(ruta, SR, (mezcla * 32767).astype(np.int16))
    print(f"-> {ruta}  {len(mezcla)/SR:.0f}s")

    medidor = pyln.Meter(SR)
    print(f"\n  LUFS integrado {medidor.integrated_loudness(mezcla):.1f} · "
          f"pico {20*np.log10(np.abs(mezcla).max()):.1f} dBFS · "
          f"corr {np.corrcoef(mezcla[:,0],mezcla[:,1])[0,1]:+.2f}")

    print(f"\n  COMO EVOLUCIONA (cada 15 s)")
    print(f"    {'tramo':>9} {'LUFS':>7} {'20-60':>6} {'60-120':>7} {'120-250':>8} {'250-1k':>7} {'1k+':>6}")
    for i in range(0, int(len(mezcla) / SR), 15):
        seg = mezcla[int(i * SR):int((i + 15) * SR)]
        if len(seg) < SR:
            continue
        fr, ps = welch(seg.mean(axis=1), SR, nperseg=8192)
        tot = ps.sum() + 1e-20
        b = lambda p, q: 100 * ps[(fr >= p) & (fr < q)].sum() / tot
        print(f"    {i:3d}-{i+15:3d}s {medidor.integrated_loudness(seg):6.1f} "
              f"{b(20,60):5.1f}% {b(60,120):6.1f}% {b(120,250):7.1f}% {b(250,1000):6.1f}% {b(1000,11025):5.1f}%")


if __name__ == "__main__":
    sys.exit(main())
