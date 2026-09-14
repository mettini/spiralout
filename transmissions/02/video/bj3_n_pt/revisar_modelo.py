#!/usr/bin/env python3
"""Dice DONDE MIRAR los planos que pasaron por el modelo. No dictamina.

    python3.10 transmissions/02/video/bj3_n_pt/revisar_modelo.py

POR QUE ESTO NO ES UN CRITERIO DEL EXAMEN
--------------------------------------------------------------------------------
El modelo (Real-ESRGAN) inventa estructura donde la fuente no tiene nada. Paso y salio al
aire: en 0:15 aparecio, nitido y abajo a la derecha, algo con forma de renglon de texto, y
el user lo marco como "algo se escapa del blur". Medido en el mismo instante y la misma
region, el crudo es una mancha de bloques de compresion sin ninguna estructura.

SE PROBARON DOS FORMAS DE DETECTARLO AUTOMATICAMENTE Y LAS DOS FALLAN:

  varianza local de la fuente   la region del texto tiene MAS varianza local (mediana
                                0,0110) que el cuadro entero (0,0027), o sea que queda
                                del lado "detallado" y no del lado "plano"
  inestabilidad temporal        mejor, pero no alcanza: puntuando energia relativa por
                                inestabilidad, el caso conocido salio 9,5 y quedo SEXTO
                                de 16 intermedios, debajo de cinco que no hay razon para
                                creer malos. Un umbral que lo atrape reprueba inocentes

Asi que esto NO dice si hay alucinacion. Ordena los intermedios por sospecha y extrae el
cuadro y la region de cada uno para MIRARLOS. La decision es del ojo, y conviene que eso
este escrito y no disimulado detras de un PASA.
"""
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = AQUI
while RAIZ != "/" and not os.path.isdir(os.path.join(RAIZ, ".git")):
    RAIZ = os.path.dirname(RAIZ)
BALDOSA = 24


def puntuar(dst, w, h, cuadros=12):
    """Energia de alta frecuencia por baldosa, contra cuanto va y viene entre cuadros."""
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", dst, "-frames:v", str(cuadros),
                        "-vf", "format=gray", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    k = len(o) // (w * h)
    if k < 4:
        return None
    a = np.frombuffer(o[:k*w*h], dtype=np.uint8).reshape(k, h, w).astype(np.float32)
    g = (np.abs(np.diff(a, axis=2))[:, :h-1, :] + np.abs(np.diff(a, axis=1))[:, :, :w-1])
    t = BALDOSA
    bh, bw = (g.shape[1]//t)*t, (g.shape[2]//t)*t
    H = g[:, :bh, :bw].reshape(k, bh//t, t, bw//t, t).mean(axis=(2, 4))
    mu, sd = H.mean(axis=0), H.std(axis=0)
    p = (mu / max(mu.mean(), 1e-6)) * (sd / np.maximum(mu, 1e-6))
    iy, ix = np.unravel_index(int(p.argmax()), p.shape)
    return float(p.max()), iy * t, ix * t


def main():
    mapa = os.path.join(AQUI, ".ia", "mapa.txt")
    if not os.path.exists(mapa):
        print("  ningun plano paso por el modelo")
        return 0
    salida = os.path.join(AQUI, ".ia", "revision")
    os.makedirs(salida, exist_ok=True)
    filas = []
    for linea in open(mapa):
        if not linea.strip():
            continue
        c = linea.rstrip("\n").split("|")
        dst = os.path.join(RAIZ, c[4])
        w, h = int(c[5]), int(c[6])
        r = puntuar(dst, w, h)
        if r:
            filas.append((r[0], r[1], r[2], c[4], os.path.basename(c[1]), w, h))
    filas.sort(reverse=True)
    print(f"  {len(filas)} intermedios, ordenados por sospecha. MIRAR los de arriba.\n")
    print(f"  {'puntaje':>8}  {'intermedio':10} {'fuente':40} recorte extraido")
    for p, y, x, ruta, src, w, h in filas:
        nom = os.path.basename(ruta).replace(".mov", "")
        png = os.path.join(salida, f"{nom}_{int(p)}.png")
        x0, y0 = max(0, x - 120), max(0, y - 80)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(RAIZ, ruta),
                        "-frames:v", "1", "-vf",
                        f"crop={min(360, w-x0)}:{min(240, h-y0)}:{x0}:{y0},"
                        f"scale=1080:-1:flags=neighbor", png], capture_output=True)
        print(f"  {p:8.1f}  {nom:10} {src[:40]:40} {os.path.relpath(png, RAIZ)}")
    print(f"\n  los recortes quedaron en {os.path.relpath(salida, RAIZ)}")
    print("  el puntaje ORDENA, no dictamina: el caso conocido de 0:15 salio sexto de 16")
    return 0


if __name__ == "__main__":
    sys.exit(main())
