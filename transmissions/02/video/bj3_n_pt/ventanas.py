#!/usr/bin/env python3
"""Escanea cada fuente DENSO y saca sus ventanas limpias.

    python3.10 transmissions/02/bj3_n_pt/video/ventanas.py            # todas
    python3.10 transmissions/02/bj3_n_pt/video/ventanas.py archivo    # una

POR QUE EXISTE
--------------------------------------------------------------------------------
El escaneo anterior muestreaba cada 4 segundos y dejo pasar, al aire y en el master:

    3:43  una bandera, un reloj en pantalla y un lanzamiento de cohete  (pd_glm_rayos)
    5:12  un mapa con lineas punteadas blancas                          (pd_iceberg)
    3:23  un logo                                                        (IMG_4740)

Cuatro segundos es una eternidad: una placa de dos segundos pasa entera entre dos
muestras. Aca se muestrea cada 0,5 s y se cruzan TRES senales distintas, porque ninguna
sola alcanza:

    texto      pixeles claros, quietos entre cuadros y con bordes duros
    grafico    lineas rectas largas (mapas, marcos, barras) que no existen en la
               naturaleza y si en cualquier placa o superposicion
    logo       un bloque que se mantiene identico durante segundos en la misma posicion

La salida son las VENTANAS LIMPIAS de cada archivo, que es lo que `planos.py` consume.
Si un archivo no tiene ninguna ventana util, no se usa: es preferible perder una fuente
a que salga un cohete en el video.
"""
import json
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
FTE = os.path.join(AQUI, "fuentes")
GEN = os.path.join(AQUI, "generado")
LLUVIA = os.environ.get("CLIPS", os.path.expanduser("~/Downloads/Videos-Aem"))
PALMA = os.environ.get("PALMA_SRC", os.path.expanduser("~/Downloads/IMG_4842.MOV"))

PASO = 0.5          # cada cuanto se mira, en segundos
ANCHO, ALTO = 320, 180
MIN_VENTANA = 6.0   # una ventana mas corta que esto no sirve para ningun plano largo


def duracion(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v",
                        "-show_entries", "stream=nb_read_frames,r_frame_rate",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    try:
        fps_txt, n = r.split(",")[0], r.split(",")[1]
        a, b = fps_txt.split("/")
        return int(n) / (float(a) / float(b))
    except Exception:
        return 0.0


def cuadros(f, ss, n=2):
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", f,
                        "-frames:v", str(n), "-vf",
                        f"fps=4,scale={ANCHO}:{ALTO},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    m = len(o) // (ANCHO * ALTO)
    if m < n:
        return None
    return np.frombuffer(o[:n * ANCHO * ALTO], dtype=np.uint8).reshape(n, ALTO, ANCHO).astype(float)


def sucio(a):
    """Devuelve (hay_texto, hay_grafico, hay_logo, hay_corte) para un par de cuadros."""
    q, s = a[0], a[1]
    quieto = np.abs(s - q) < 3

    # TEXTO: claro, quieto, y con borde duro al lado
    gx = np.zeros_like(q)
    gx[:, :-1] = np.abs(np.diff(q, axis=1))
    texto = (quieto & (q > 190) & (gx > 60)).mean() > 0.0025

    # GRAFICO: lineas rectas LARGAS. Se cuentan filas y columnas donde el gradiente
    # perpendicular es alto en una fraccion grande del largo. Un mapa, un marco o una
    # barra dan eso; una nube, la lava o el agua no.
    gy = np.zeros_like(q)
    gy[:-1, :] = np.abs(np.diff(q, axis=0))
    filas = ((gy > 45).mean(axis=1) > 0.45).sum()
    cols = ((gx > 45).mean(axis=0) > 0.45).sum()
    grafico = (filas + cols) >= 2

    # LOGO: un bloque chico que no cambia NADA y tiene contraste propio
    logo = False
    for r0 in range(0, ALTO - 44, 44):
        for c0 in range(0, ANCHO - 60, 60):
            b = q[r0:r0 + 44, c0:c0 + 60]
            if quieto[r0:r0 + 44, c0:c0 + 60].mean() > 0.98 and b.std() > 42:
                logo = True
    # CORTE INTERNO. Muchas fuentes de archivo son piezas editadas: adentro tienen
    # cambios de plano. Si una ventana los contiene, el plano del video muestra una
    # imagen y salta a otra en medio, y eso se lee como "mostras algo menos de un
    # segundo". Es lo que hacia el salto de 4:44 y los de 9:02, 9:24 y 9:37.
    #
    # Un corte cambia el cuadro ENTERO de golpe; el movimiento cambia partes. Se pide
    # que la diferencia media sea alta Y que este repartida por todo el cuadro.
    dif = np.abs(s - q)
    corte = dif.mean() > 26 and (dif > 18).mean() > 0.55

    return texto, grafico, logo, corte


def ventanas(f, verboso=True):
    d = duracion(f)
    if d <= 0:
        return []
    malos = []
    t = 0.0
    while t < d - 0.3:
        a = cuadros(f, t)
        if a is not None:
            texto, grafico, logo, corte = sucio(a)
            # El "grafico" (lineas rectas largas) NO descalifica el tramo aca. Mira el
            # cuadro ENTERO, y el video recorta: `IMG_4842` salia inservible por las
            # rectas del edificio cuando los recortes usados lo esquivan por completo.
            # Esa senal vive en `verificar.py`, que revisa el plano ya recortado.
            if texto or logo or corte:
                malos.append(t)
        t += PASO
    # El minimo se adapta al largo del archivo. Con 6 s fijo, un generado de 3 s limpio
    # salia "INSERVIBLE" por ser corto y no por estar sucio, y quedaba afuera del video.
    minimo = min(MIN_VENTANA, max(1.0, d * 0.45))
    if not malos:
        return [(round(min(0.3, d * 0.05), 1), round(d - 0.3, 1))]
    libres, ini = [], 0.0
    for m in malos + [d]:
        if m - PASO - ini >= minimo:
            libres.append((round(ini + 0.3, 1), round(m - PASO - 0.3, 1)))
        ini = m + PASO
    if verboso:
        nom = os.path.basename(f)
        if not malos:
            print(f"  {nom[:44]:46} limpio entero ({d:.0f}s)")
        elif not libres:
            print(f"  {nom[:44]:46} INSERVIBLE: sucio en {len(malos)} puntos, "
                  f"sin ninguna ventana de {MIN_VENTANA:.0f}s")
        else:
            v = " ".join(f"{a:.0f}-{b:.0f}" for a, b in libres[:6])
            print(f"  {nom[:44]:46} {len(malos)} puntos sucios · ventanas: {v}")
    return libres


def main():
    fuentes = sys.argv[1:] or sorted(
        [os.path.join(FTE, x) for x in os.listdir(FTE)
         if x.endswith((".webm", ".mp4", ".ogv"))]
        + [os.path.join(GEN, x) for x in os.listdir(GEN) if x.endswith(".mp4")]
        + [os.path.join(LLUVIA, x) for x in os.listdir(LLUVIA) if x.endswith(".MOV")]
        + [PALMA])
    print(f"  escaneando {len(fuentes)} fuentes cada {PASO}s\n")
    tabla = {}
    for f in fuentes:
        tabla[os.path.basename(f)] = ventanas(f)
    # LA TABLA SE GUARDA. Antes esto quedaba en un log y las ventanas se copiaban a mano
    # a `planos.py`, donde se desactualizaban en silencio: `sol2` tenia escrito [8, 290]
    # cuando su ultima ventana limpia termina en 175, y por eso salieron los saltos.
    destino = os.path.join(AQUI, "ventanas.json")
    previo = {}
    if os.path.exists(destino):
        with open(destino) as fh:
            previo = json.load(fh)
    previo.update(tabla)          # correr con argumentos actualiza, no borra el resto
    tabla = previo
    with open(destino, "w") as fh:
        json.dump(tabla, fh, indent=1)
    print(f"\n  -> {os.path.relpath(destino, AQUI)}   "
          f"{sum(len(v) for v in tabla.values())} ventanas en {len(tabla)} fuentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
