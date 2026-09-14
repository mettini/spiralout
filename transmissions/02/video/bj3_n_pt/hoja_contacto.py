#!/usr/bin/env python3
"""Una hoja de contacto con un cuadro de cada plano, para revisar CON EL OJO.

    python3.10 transmissions/02/video/bj3_n_pt/hoja_contacto.py [video]

POR QUE EXISTE. `validar_render.py` mide negro, quietud, saltos y cortes. NO ve formas:
en 4:12 habia una barra negra vertical dura en el agua (un objeto real de la fuente que el
modelo afilo y el grado estiro) y la validacion la dio por buena, porque no es ninguna de
las cuatro cosas que mide.

Esa clase de defecto (algo que se lee como un objeto reconocible) hoy no la detecta ningun
numero de este repo: el detector de lineas rectas de `verificar.py` corre sobre material
CRUDO, donde la marca todavia es tenue, y sobre material ya gradado dispara siempre porque
despues de la curva dura todo borde es duro.

Asi que se mira. Esto arma la hoja para poder mirar los 61 planos de una.
"""
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
NEGRO = 6.0


def main():
    video = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "out", "bj3_n_pt_1080.mp4")
    plan = video[:-4] + ".plan.txt"
    if not os.path.exists(plan):
        plan = os.path.join(AQUI, "out", "bj3_n_pt_1080.plan.txt")
    filas = [l.rstrip("\n").split("|") for l in open(plan) if l.strip()]
    salida = os.path.join(AQUI, "out", "hoja")
    os.makedirs(salida, exist_ok=True)
    for f in os.listdir(salida):
        os.remove(os.path.join(salida, f))
    t = NEGRO
    partes = []
    for i, f in enumerate(filas, 1):
        d = float(f[3])
        # el medio del plano: ni la entrada ni la salida
        png = os.path.join(salida, f"{i:03d}.png")
        # SIN `drawtext`: en macOS el ffmpeg de brew suele venir sin fontconfig y el filtro
        # falla en silencio, dejando la hoja vacia. El numero de plano va en el nombre del
        # archivo, que para revisar alcanza.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t + d/2:.2f}", "-i", video,
                        "-frames:v", "1", "-vf", "scale=480:270", png], capture_output=True)
        if os.path.exists(png):
            partes.append(png)
        t += d
    # de a 5 por fila
    filas_png = []
    # EL ULTIMO RENGLON SE RELLENA. Con 61 planos el ultimo grupo tiene 1 sola imagen, y
    # `vstack` se niega a apilar renglones de anchos distintos: la hoja salia vacia.
    negro = os.path.join(salida, "_negro.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=c=black:s=480x270:d=1", "-frames:v", "1", negro],
                   capture_output=True)
    for k in range(0, len(partes), 5):
        grupo = partes[k:k + 5]
        while len(grupo) < 5:
            grupo.append(negro)
        out = os.path.join(salida, f"fila_{k//5:02d}.png")
        ent = []
        for p in grupo:
            ent += ["-i", p]
        subprocess.run(["ffmpeg", "-v", "error", "-y"] + ent
                       + ["-filter_complex", f"hstack=inputs={len(grupo)}", out],
                       capture_output=True)
        filas_png.append(out)
    ent = []
    for p in filas_png:
        ent += ["-i", p]
    final = os.path.join(salida, "hoja_contacto.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ent
                   + ["-filter_complex", f"vstack=inputs={len(filas_png)}", final],
                   capture_output=True)
    print(f"  {len(partes)} planos -> {os.path.relpath(final, AQUI)}")
    print("  y cada uno suelto en out/hoja/NNN.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
