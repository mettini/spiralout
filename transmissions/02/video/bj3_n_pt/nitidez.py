"""Mide CUADRICULADO por plano y dice cuanto suavizado necesita cada uno.

El 4K se veia con cuadrados grandes y la primera hipotesis (recorte chico, hay que
ampliarlo) resulto equivocada. La prueba: `pelo` se amplia 13,7x y NO se cuadricula, se
ablanda; `sol2` se amplia 7,1x y SI se cuadricula. La diferencia no es el factor, es la
FUENTE: los webm del SDO traen zonas de bajo contraste aplastadas por VP9 en mesetas
planas de 8x8. Invisibles a contraste nativo, pero el grado del video estira esa zona
~4,4 veces (normalize x1,5 . eq 1,7 . curva 1,7) y las mesetas salen a la superficie.
Despues el escalado las agranda y quedan cuadrados.

O sea: el cuadrado no es un artefacto del escalado, es informacion real de la fuente
puesta en evidencia por el grado. Ningun filtro lineal la puede recuperar porque abajo
no hay nada. Lo unico honesto es disolver la meseta para que lea blando y no cuadriculado.

COMO SE MIDE. Se parte el recorte crudo en baldosas de 8x8 (el paso de bloque de VP9 y
H.264) y se comparan dos dispersiones:

  - adentro de cada baldosa: cuanto varia el gris DENTRO del bloque
  - entre baldosas:          cuanto varia el gris ENTRE bloques

Una imagen normal tiene detalle en las dos escalas. Una imagen aplastada en bloques es
plana adentro y escalonada afuera, asi que el cociente `adentro / entre` se desploma.
Ese cociente es la medida: cuanto MAS BAJO, mas cuadriculada esta la fuente.

El suavizado sale de ahi y NO del factor de ampliacion, porque medir el factor fue
justamente lo que llevo al diagnostico equivocado.

    python3.10 nitidez.py out/bj3_n_pt_4k.plan.txt
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BALDOSA = 8          # paso de bloque de VP9 / H.264
CUADROS = 3          # cuantos instantes se miran por plano

# Debajo de este cociente la fuente esta hecha de mesetas y hay que disolverlas.
# Calibrado contra los dos casos que se miraron a ojo: sol2 (cuadriculado, hay que
# tratarlo) y pelo (limpio, tocarlo solo lo arruina).
UMBRAL = 0.42
SIGMA_MAX = 4.5      # mas que esto ya no es disolver, es borrar


def _leer(fuente, ss, recorte):
    """Devuelve el recorte CRUDO en gris, sin gradar. Es donde vive el bloque."""
    ancho, alto = (int(v) for v in recorte.split(":")[:2])
    ruta = fuente if os.path.isabs(fuente) else os.path.join(RAIZ, fuente)
    crudo = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{ss}", "-i", ruta, "-frames:v", "1",
         "-vf", f"crop={recorte},format=gray", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    if len(crudo) < ancho * alto:
        return None
    return np.frombuffer(crudo[:ancho * alto], dtype=np.uint8).astype(np.float32).reshape(alto, ancho)


def cociente(img):
    """adentro/entre. Bajo = mesetas planas = cuadriculado."""
    alto, ancho = img.shape
    ny, nx = alto // BALDOSA, ancho // BALDOSA
    if ny < 2 or nx < 2:
        return 1.0
    t = img[:ny * BALDOSA, :nx * BALDOSA].reshape(ny, BALDOSA, nx, BALDOSA).transpose(0, 2, 1, 3)
    t = t.reshape(ny, nx, -1)
    adentro = t.std(axis=2).mean()
    entre = t.mean(axis=2).std()
    if entre < 0.5:                 # zona uniforme: no hay nada que juzgar
        return 1.0
    return float(adentro / entre)


def sigma_para(coc):
    """Cuanto blur pide un cociente dado. Cero si la fuente esta sana."""
    if coc >= UMBRAL:
        return 0.0
    # cuanto mas lejos del umbral, mas plana la fuente y mas hay que disolver
    return round(min(SIGMA_MAX, SIGMA_MAX * (UMBRAL - coc) / UMBRAL), 1)


def medir(fila):
    c = fila.rstrip("\n").split("|")
    nombre, fuente, ss, dur, recorte = c[0], c[1], float(c[2]), float(c[3]), c[4]
    cocs = []
    for k in range(CUADROS):
        img = _leer(fuente, ss + dur * (k + 0.5) / CUADROS, recorte)
        if img is not None:
            cocs.append(cociente(img))
    if not cocs:
        return None
    coc = float(np.median(cocs))
    return nombre, os.path.basename(fuente), int(recorte.split(":")[0]), coc, sigma_para(coc)


def main(plan):
    filas = [l for l in open(plan) if l.strip()]
    with ThreadPoolExecutor(max_workers=4) as ex:      # 4 y no mas: la maquina se usa
        res = [r for r in ex.map(medir, filas) if r]
    print(f"{'plano':<10}{'fuente':<34}{'recorte':>8}{'coc':>7}{'sigma':>7}")
    for nombre, fuente, ancho, coc, s in res:
        marca = "  <-- disolver" if s > 0 else ""
        print(f"{nombre:<10}{fuente[:33]:<34}{ancho:>8}{coc:>7.2f}{s:>7.1f}{marca}")
    tocados = [r for r in res if r[4] > 0]
    print(f"\n{len(tocados)} de {len(res)} planos piden suavizado")
    porf = {}
    for nombre, fuente, ancho, coc, s in res:
        porf.setdefault(fuente, []).append(s)
    print("\nsigma sugerido por fuente (mediana):")
    for f, ss in sorted(porf.items(), key=lambda kv: -np.median(kv[1])):
        print(f"  {np.median(ss):>4.1f}  {f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/bj3_n_pt_4k.plan.txt")
