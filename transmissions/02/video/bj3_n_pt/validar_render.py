#!/usr/bin/env python3
"""Mide los planos YA RENDERIZADOS y anota los que no sirven.

    python3.10 transmissions/02/video/bj3_n_pt/validar_render.py

POR QUE EXISTE, Y POR QUE REEMPLAZA A PREDECIR
--------------------------------------------------------------------------------
`planos.py` valida cada encuadre reconstruyendo a mano la cadena de filtros de
`montaje.sh`. Esa reconstruccion NO reproduce el render: seis planos del video pasaron la
validacion y fallaron sobre el archivo. Se persiguio la diferencia por tres lados y
ninguno la explica:

    minterpolate (la mezcla de cuadros)   no mueve la aguja: 1,00 -> 0,97
    el blur de `mejorar.py`               baja poco: 1,00 -> 0,75
    el encode H.264 a CRF 26              acerca pero no alcanza: 1,44 contra 0,93 real

Seguir adivinando la cadena es el mismo error que origino todo esto, que fue un examen que
medía el PLAN en vez del archivo. `montaje.sh` deja cada plano como `.montaje/NNN.mp4`, o
sea que el archivo que se va a ver EXISTE: se mide ese.

QUE HACE. Mide cada plano renderizado con los mismos criterios del examen final y escribe
`excluidos.txt` con los encuadres que no sirven. `planos.py` lee ese archivo y no vuelve a
elegirlos, asi que la proxima corrida busca otra cosa para esos slots.

El ciclo completo es:

    bash montaje.sh                  -> deja los planos en .montaje/
    python3.10 validar_render.py     -> mide y anota los malos en excluidos.txt
    python3.10 planos.py > plan.txt  -> re-elige solo esos (los demas caen igual)
    bash montaje.sh                  -> reusa los buenos por firma, rehace los cambiados
"""
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, ".montaje")
EXCLUIDOS = os.path.join(AQUI, "excluidos.txt")

# LOS MISMOS UMBRALES QUE `qa_entrega.py`. Si divergen, el generador acepta lo que el
# examen despues rechaza, que es exactamente el problema que este archivo viene a cerrar.
FPS = 4.0
VENTANA_S = 2.0
VISIBLE_MINIMO = 30.0
MOV_MINIMO = 0.40
SALTO_MAX = 55.0


def medir(ruta):
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-an",
                        "-vf", f"fps={FPS},scale=96:54,format=gray",
                        "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    n = len(o) // 5184
    if n < 6:
        return None
    return np.frombuffer(o[:n*5184], dtype=np.uint8).reshape(n, -1).astype(np.float32)


def revisar(a):
    """Devuelve el motivo por el que este plano no sirve, o None."""
    paso = int(VENTANA_S * FPS)
    luz = a.mean(axis=1)
    vis = np.percentile(a, 99.5, axis=1)
    dif = np.abs(np.diff(a, axis=0)).mean(axis=1)
    seg = lambda i: f"{i / FPS:.1f}s"
    for i in range(0, len(a) - paso + 1):
        if vis[i:i + paso].max() < VISIBLE_MINIMO:
            return f"pantalla negra en {seg(i)} (nada por encima de {vis[i:i+paso].max():.0f})"
    for i in range(0, len(dif) - paso + 1):
        if dif[i:i + paso].mean() < MOV_MINIMO:
            return f"quieto en {seg(i)} (movimiento {dif[i:i+paso].mean():.2f})"
    salto = np.abs(np.diff(luz))
    if len(salto) and salto.max() > SALTO_MAX:
        i = int(salto.argmax())
        return f"salto de luz en {seg(i)} ({luz[i]:.0f} -> {luz[i+1]:.0f})"
    med = float(np.median(dif))
    # 5x Y NO 6x: es el mismo factor que usa `qa_entrega.py`. Con 6 se le escapaba un corte
    # interno de `abisal` que el examen si marcaba, o sea que otra vez habia dos varas.
    # 4x Y NO 5x. Con 5 se escapaba el corte del plano de `pelo`: su ratio contra la
    # mediana del PROPIO plano daba 4,2 (el pelo se mueve mucho y le sube la mediana),
    # mientras que el examen lo veia en 5,0 porque su vecindario cruza al plano de al lado.
    if len(dif) and dif.max() > max(25.0, 4.0 * med):
        return f"corte interno en {seg(int(dif.argmax()))} (cambio {dif.max():.0f} contra {med:.0f})"
    return None


def defectos_del_examen(video, filas):
    """Los defectos que ve el EXAMEN sobre el archivo final, mapeados a su plano.

    POR QUE HACE FALTA. El examen mira el video entero y usa un vecindario de 12 s para
    decidir si un cambio es un corte; la medicion por plano usa la mediana del propio
    plano. Con material que se mueve mucho las dos no coinciden, y paso lo peor que podia
    pasar: el examen FALLABA y la medicion por plano no anotaba nada, asi que la vuelta
    siguiente generaba el mismo plan y fallaba igual. El ciclo giraba sin avanzar.

    Con esto el ciclo se alimenta de la autoridad, que es el examen.
    """
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-an",
                        "-vf", f"fps={FPS},scale=96:54,format=gray",
                        "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    n = len(o) // 5184
    if n < 10:
        return []
    A = np.frombuffer(o[:n*5184], dtype=np.uint8).reshape(n, -1).astype(np.float32)
    dif = np.abs(np.diff(A, axis=0)).mean(axis=1)
    vis = np.percentile(A, 99.5, axis=1)
    lim = [6.0]
    for f in filas:
        lim.append(lim[-1] + float(f[3]))
    bordes = [round(x, 2) for x in lim]

    def plano_de(seg):
        for i in range(len(filas)):
            if lim[i] <= seg < lim[i + 1]:
                return i
        return None

    salida = []
    vecindario = int(6 * FPS)
    for i in range(len(dif)):
        seg = i / FPS
        if not (8.0 <= seg <= 663.0):
            continue
        a, b = max(0, i - vecindario), min(len(dif), i + vecindario)
        med = float(np.median(dif[a:b]))
        if dif[i] > max(30.0, 5.0 * med) and min(abs(seg - x) for x in bordes) > 0.6:
            j = plano_de(seg)
            if j is not None:
                salida.append((j, f"corte interno en {seg - lim[j]:.1f}s del plano "
                                  f"(el examen lo ve en {int(seg//60)}:{seg%60:04.1f})"))
    paso = int(VENTANA_S * FPS)
    for i in range(int(8.0 * FPS), min(len(A) - paso, int(663.0 * FPS))):
        if vis[i:i + paso].max() < VISIBLE_MINIMO:
            j = plano_de(i / FPS)
            if j is not None:
                salida.append((j, "pantalla negra que ve el examen"))
            break
    vistos = set()
    unicos = []
    for j, motivo in salida:
        if j not in vistos:
            vistos.add(j)
            unicos.append((j, motivo))
    return unicos


def main():
    plan = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "out", "bj3_n_pt_1080.plan.txt")
    filas = [l.rstrip("\n").split("|") for l in open(plan) if l.strip()]
    ya = set()
    if os.path.exists(EXCLUIDOS):
        ya = {l.strip() for l in open(EXCLUIDOS) if l.strip() and not l.startswith("#")}
    malos = []
    for i, f in enumerate(filas, 1):
        ruta = os.path.join(TMP, f"{i:03d}.mp4")
        if not os.path.exists(ruta):
            continue
        a = medir(ruta)
        if a is None:
            continue
        motivo = revisar(a)
        if motivo:
            clave = f"{f[0]}|{f[2]}|{f[4]}"
            malos.append((i, f[0], clave, motivo))
    # y los que ve el examen sobre el archivo final, que la medicion por plano puede no ver
    video = plan.replace(".plan.txt", ".mp4")
    if os.path.exists(video):
        ya_malos = {m[0] for m in malos}
        for j, motivo in defectos_del_examen(video, filas):
            if (j + 1) not in ya_malos:
                f = filas[j]
                malos.append((j + 1, f[0], f"{f[0]}|{f[2]}|{f[4]}", motivo))
    malos.sort()
    print(f"  {len(filas)} planos medidos sobre el archivo · {len(malos)} no sirven\n")
    for i, cl, clave, motivo in malos:
        print(f"    {i:3d} {cl:8} {motivo}")
    nuevas = {m[2] for m in malos} - ya
    if nuevas:
        with open(EXCLUIDOS, "a") as fh:
            if not ya:
                fh.write("# encuadres medidos sobre el RENDER y descartados. `planos.py` no los reusa.\n")
            for c in sorted(nuevas):
                fh.write(c + "\n")
        print(f"\n  {len(nuevas)} encuadres nuevos anotados en {os.path.basename(EXCLUIDOS)} "
              f"({len(ya) + len(nuevas)} en total)")
    else:
        print("\n  no hay encuadres nuevos para anotar")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
