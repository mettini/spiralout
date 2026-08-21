#!/usr/bin/env python3
"""Verifica CADA PLANO tal como va a salir, antes de renderizar el video entero.

    python3.10 transmissions/02/bj3_n_pt/video/planos.py | python3.10 transmissions/02/bj3_n_pt/video/verificar.py

POR QUE ESTE Y NO `ventanas.py`
--------------------------------------------------------------------------------
`ventanas.py` mira el cuadro ENTERO de cada fuente. Pero el video no muestra el cuadro
entero: muestra un recorte, a veces girado, a veces en negativo. Las dos cosas fallan por
lados opuestos:

    falso positivo   `IMG_4842` sale "inservible" porque el detector ve las rectas del
                     edificio, cuando los recortes usados lo esquivan por completo
    falso negativo   un logo chico puede estar fuera del recorte en el segundo que se
                     muestreo y adentro en el que se usa

Asi que aca se renderizan cuadros del plano REAL, con su recorte, su variante y su punto
de entrada, y se los revisa. Es la unica verificacion que corresponde.

QUE BUSCA
--------------------------------------------------------------------------------
    texto      claro, quieto entre cuadros, con bordes duros al lado
    grafico    lineas rectas largas: mapas, marcos, barras. No existen en la naturaleza
    silueta    SOLO en los planos de pelo. Una mancha oscura grande y compacta contra un
               fondo claro es un animal reconocible, que es justo lo que no se quiere.
               Salio en 7:27: se veia el lomo y el anca contra el pasto.
"""
import subprocess
import sys

import numpy as np

A, L = 320, 180
CUADROS = 8


def render(ruta, ss, dur, recorte, variante, vel):
    """Cuadros del plano tal cual va a salir, repartidos a lo largo de su duracion."""
    vf = [f"setpts={vel}*PTS", f"crop={recorte}"]
    if variante:
        vf.append(variante)
    vf += ["format=gray", f"scale={A}:{L}"]
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta,
                        "-t", str(dur), "-vf", ",".join(vf) + f",fps={CUADROS/float(dur):.3f}",
                        "-frames:v", str(CUADROS), "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    n = len(o) // (A * L)
    if n < 2:
        return None
    return np.frombuffer(o[:n * A * L], dtype=np.uint8).reshape(n, L, A).astype(float)


def revisar(m, es_pelo=False):
    fallas = []
    for i in range(len(m) - 1):
        q, s = m[i], m[i + 1]
        quieto = np.abs(s - q) < 3
        gx = np.zeros_like(q); gx[:, :-1] = np.abs(np.diff(q, axis=1))
        gy = np.zeros_like(q); gy[:-1, :] = np.abs(np.diff(q, axis=0))

        if (quieto & (q > 190) & (gx > 60)).mean() > 0.0025:
            fallas.append(f"texto en el cuadro {i}")
        rectas = ((gy > 45).mean(axis=1) > 0.45).sum() + ((gx > 45).mean(axis=0) > 0.45).sum()
        if rectas >= 2:
            fallas.append(f"lineas rectas en el cuadro {i}")

    if es_pelo:
        # SILUETA: una region oscura grande y COMPACTA. Se mide cuanto del cuadro es
        # oscuro y que tan "lleno" esta ese oscuro: el pelo da oscuro disperso y con
        # mucho borde; un lomo da una mancha grande con poco borde para su tamano.
        for i, q in enumerate(m):
            osc = q < np.percentile(q, 45)
            if osc.mean() < 0.25:
                continue
            borde = np.zeros_like(osc, dtype=float)
            borde[:, :-1] = np.abs(np.diff(osc.astype(float), axis=1))
            compacidad = osc.mean() / (borde.mean() + 1e-6)
            if compacidad > 14:
                fallas.append(f"silueta compacta en el cuadro {i} "
                              f"(compacidad {compacidad:.0f}, el pelo da menos de 14)")
                break
    return fallas


def main():
    filas = [l.rstrip("\n").split("|") for l in sys.stdin if l.strip() and not l.startswith("#")]
    print(f"  verificando {len(filas)} planos, cuadro por cuadro, tal como van a salir\n")
    malos = 0
    t = 6.0
    for i, f in enumerate(filas, 1):
        clave, ruta, ss, dur, recorte, variante, trat, vel = f
        m = render(ruta, ss, dur, recorte, variante, vel)
        if m is None:
            print(f"  {i:3d} {clave:8} {int(t)//60}:{int(t)%60:02d}  NO SE PUDO LEER")
            malos += 1
            t += float(dur)
            continue
        fallas = revisar(m, es_pelo=(trat == "pelo"))
        if fallas:
            malos += 1
            print(f"  {i:3d} {clave:8} {int(t)//60}:{int(t)%60:02d}  ss={ss}  "
                  f"{'; '.join(fallas[:2])}")
        t += float(dur)
    print(f"\n  {malos} planos con problemas de {len(filas)}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
