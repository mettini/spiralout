#!/usr/bin/env python3
"""El examen de entrega. Trece criterios medibles, sin opinion.

    python3.10 transmissions/02/bj3_n_pt/video/qa_entrega.py

POR QUE EXISTE
--------------------------------------------------------------------------------
Pregunta del user: "como vas a validar, y en base a que, para afirmar que ya esta para
subir". Hasta aca yo verificaba cosas sueltas y despues decia que estaba bien, y varias
veces estaba mal: mire el archivo equivocado, medi una cadena distinta de la que se
renderiza, o di por resuelto algo que no habia verificado sobre la salida.

Esto corre TODO sobre el archivo final y devuelve PASA o FALLA por criterio. Si algo
falla, no esta para entregar. No hay criterio de "se ve bien".
"""
import collections
import json
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "out", "bj3_n_pt_1080.mp4")

# La raiz del repo se BUSCA, no se cuenta en niveles: contarlos rompio al mover la
# carpeta del lab a `transmissions/02/`, que baja un nivel mas.
RAIZ = AQUI
while RAIZ != "/" and not os.path.isdir(os.path.join(RAIZ, ".git")):
    RAIZ = os.path.dirname(RAIZ)
AUDIO = os.path.join(RAIZ, "transmissions", "02", "themes", "bj3_n_pt",
                     "finals", "v1", "01_bj3_n_pt_master.wav")
# el plan congelado JUNTO a ese entregable, no el ultimo que se genero

MOOG = [501, 524, 544, 564, 582, 603, 627]   # cambios de enunciado, de melodia.py
resultados = []


def marca(nombre, ok, detalle):
    resultados.append((ok, nombre, detalle))
    print(f"  [{'PASA' if ok else 'FALLA'}]  {nombre:38} {detalle}")


FPS_QA = 4.0        # cada cuanto se mira el archivo final
VISIBLE_MINIMO = 30.0  # si el percentil 99,5 del cuadro no llega aca, no hay nada
                       # en pantalla. NO se mide por luz media: hay planos legitimos
                       # con media 4,9 que son plasma brillante sobre negro (pico 223)
VENTANA_S = 2.0     # el tramo mas corto que el ojo lee como "una escena"
SALTO_MAX = 55.0    # diferencia de luz entre cuadros vecinos: arriba de esto es corte
# EL MISMO PISO QUE `planos.py`, y no otro. Tenerlos distintos (el generador exigia 0,40
# y esto 1,00) hacia que el examen reprobara planos que el generador habia aceptado bien:
# no median cosas distintas, median lo mismo con dos varas.
#
# El valor sale de lo que el user marco y de lo que dejo pasar, sobre archivos
# RENDERIZADOS: marco como estatico 0,28 y 0,31, y dejo pasar 1,00, 1,03, 1,77 y 1,80.
# 0,40 esta por encima de lo que rechazo. Es tambien el techo real de este material: con
# 0,90 la categoria cielo se queda con 4 fuentes para 20 slots y el plan no cierra.
MOV_MINIMO = 0.40   # abajo de esto el plano parece una foto
TRAMO_MINIMO = 6.0  # ninguna escena percibida puede durar menos


def escanear(f):
    """Todo el video a 4 cuadros por segundo, en gris. De aca salen los criterios.

    POR QUE ESTA FUNCION EXISTE. La version anterior de este examen medía EL PLAN y no el
    archivo: las duraciones salian del `.plan.txt` (donde ningun plano baja de 8 s) y la
    limpieza de `ventanas.json` (ventanas medidas a mano). Por eso dio LISTO PARA ENTREGAR
    sobre un video que tenia 5,4 s de pantalla negra en 6:08, un salto de luz de 1 a 204
    en 6:13, tramos percibidos de 2,9 s y 39 planos negros o quietos.

    Se lee UNA vez y se derivan todos los criterios: 671 s a 4 fps en 96x54 son 14 MB.
    """
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-an",
                        "-vf", f"fps={FPS_QA},scale=96:54,format=gray",
                        "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    n = len(o) // (96 * 54)
    return np.frombuffer(o[:n*96*54], dtype=np.uint8).reshape(n, -1).astype(np.float32)


def rachas(mascara, fps=FPS_QA):
    """Los tramos seguidos donde la mascara es verdadera, como (segundo, duracion)."""
    out, i = [], 0
    while i < len(mascara):
        if mascara[i]:
            j = i
            while j < len(mascara) and mascara[j]:
                j += 1
            out.append((i / fps, (j - i) / fps))
            i = j
        else:
            i += 1
    return out


def cuadros(f, ss, dur, w=96, h=54, fps=4):
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", f, "-t", str(dur),
                        "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    n = len(o) // (w * h)
    return None if n < 2 else np.frombuffer(o[:n*w*h], dtype=np.uint8).reshape(n, -1).astype(float)


def main():
    if not os.path.exists(VIDEO):
        sys.exit("no hay video")
    PLAN = VIDEO[:-4] + ".plan.txt"
    if not os.path.exists(PLAN):
        sys.exit(f"falta {os.path.basename(PLAN)}: el plan se congela al terminar el build")
    filas = [l.split("|") for l in open(PLAN) if l.strip()]
    lim = [6.0]
    for f in filas:
        lim.append(lim[-1] + float(f[3]))

    edad = os.path.getmtime(VIDEO)
    print(f"  archivo: {os.path.basename(VIDEO)}  "
          f"{os.path.getsize(VIDEO)/1e6:.0f} MB  del {__import__('time').ctime(edad)}\n")

    # 1 · las cuatro reglas de repeticion (PLAN_RONDA6 §V2)
    cnt = collections.Counter(f[0] for f in filas)
    r2 = [k for k, c in cnt.items() if c > 3]
    t = 6.0; pm = collections.defaultdict(list)
    for i, f in enumerate(filas, 1):
        pm[(f[0], int(t // 60))].append(i); t += float(f[3])
    r3 = [k for k, v in pm.items() if len(v) > 1]
    r4 = [i for i in range(1, len(filas)) if filas[i][0] == filas[i-1][0]]
    firmas = collections.Counter((f[0], f[2], f[4], f[5]) for f in filas)
    r1 = [k for k, c in firmas.items() if c > 1]
    marca("1 · reglas de repeticion", not (r1 or r2 or r3 or r4),
          f"{len(cnt)} fuentes, ninguna mas de 3 veces, ninguna repetida por minuto")

    # el escaneo denso del archivo final, del que salen los criterios visuales
    A = escanear(VIDEO)
    luz = A.mean(axis=1)
    dif = np.abs(np.diff(A, axis=0)).mean(axis=1)
    paso = int(VENTANA_S * FPS_QA)
    # EL NEGRO DE ENTRADA Y EL FUNDIDO DE SALIDA SON INTENCIONALES y no se examinan: son
    # los 6 s de negro con 2 s de fade del arranque y los 8 s de fundido del final, que
    # `montaje.sh` pone a proposito. Sin esta ventana el criterio de pantalla negra se
    # queja de la primera imagen del video.
    # HASTA 663 Y NO 662: 663 es donde ARRANCA el fundido de salida que pone `montaje.sh`.
    # Con 662 el examen se perdia el ultimo plano entero y dio LISTO PARA ENTREGAR sobre un
    # video que estaba en NEGRO desde 11:00 hasta el final: se fundia algo que ya era negro.
    # Lo agarro `validar_render.py`, que mide plano por plano y no tiene ventana ciega.
    DESDE, HASTA = 8.0, 663.0
    ini_q, fin_q = int(DESDE * FPS_QA), int(HASTA * FPS_QA)
    def _en_ventana(seg):
        return DESDE <= seg <= HASTA

    # 2 · sin cortes internos de la fuente
    #
    # ANTES ESTE CRITERIO MIRABA `ventanas.json` y daba 61/61 limpios sobre un video que
    # tenia cortes internos en 2:48, 5:05, 5:35, 6:13 y 8:38. Las ventanas son una
    # medicion vieja hecha a mano sobre la FUENTE; esto mide el ARCHIVO: todo cambio de
    # imagen que no caiga sobre un corte del plan es un corte que no puse yo.
    # UN CORTE SE MIDE CONTRA EL VECINDARIO. Con un umbral fijo, el material que se mueve
    # mucho (la lluvia del user mide 42 de movimiento) lo cruza todo el tiempo y el
    # criterio marcaba 250 cortes donde no hay ninguno. Lo que delata un corte es que UN
    # cuadro no se parezca a su vecino mientras el resto del tramo si.
    bordes = [round(x, 2) for x in lim]
    vecindario = int(6 * FPS_QA)
    internos = []
    for i in range(len(dif)):
        a, b = max(0, i - vecindario), min(len(dif), i + vecindario)
        med = float(np.median(dif[a:b]))
        if dif[i] > max(30.0, 5.0 * med):
            seg = i / FPS_QA
            if _en_ventana(seg) and min(abs(seg - x) for x in bordes) > 0.6:
                internos.append(seg)
    marca("2 · sin cortes internos de la fuente", not internos,
          f"{len(internos)} cambios de imagen fuera de los cortes del plan"
          + (f" (el primero en {int(internos[0]//60)}:{internos[0]%60:04.1f})" if internos else ""))

    # 3 · duracion exacta, sin deriva
    dur_real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                     "format=duration", "-of", "csv=p=0", VIDEO],
                                    capture_output=True, text=True).stdout)
    marca("3 · sin deriva de duracion", abs(dur_real - 671.0) < 0.1,
          f"{dur_real:.2f}s contra 671,00 de audio")

    # 4 · los cortes sobre los cambios de nota del moog
    peor = max(min(abs(L - m) for L in lim) for m in MOOG)
    marca("4 · cortes sobre la melodia", peor < 0.1,
          f"el peor de los 7 esta a {peor:.2f}s")

    # 5 · sin judder: cuadros exactamente repetidos
    dup = []
    for t0 in (90, 300, 420, 520, 650):
        a = cuadros(VIDEO, t0, 5, fps=60)
        if a is None: continue
        dup.append(100 * (np.abs(np.diff(a, axis=0)).max(axis=1) == 0).mean())
    marca("5 · sin judder", max(dup) < 2, f"cuadros identicos: {max(dup):.0f}% peor caso")

    # 6 · sin fogonazos ni estrobos
    # LOS CORTES DEL PLAN NO SON FOGONAZOS. Este video va con cortes SECOS por diseño, asi
    # que un corte de un plano brillante a uno oscuro da un salto de luz enorme y es
    # exactamente lo que tiene que pasar. Medido: el "peor fogonazo" que marcaba este
    # criterio era el corte entre el plano 53 (luz 212) y el 54 (luz 11). Un fogonazo es un
    # salto ADENTRO de un plano.
    salto = np.abs(np.diff(luz)).copy()
    for b in lim:
        i = int(b * FPS_QA)
        salto[max(0, i - 2):i + 2] = 0.0
    salto = salto[ini_q:fin_q]
    peor_salto = float(salto.max())
    donde = (int(salto.argmax()) + ini_q) / FPS_QA
    marca("6 · sin fogonazos", peor_salto <= SALTO_MAX,
          f"el peor salto de luz es {peor_salto:.0f} en "
          f"{int(donde//60)}:{donde%60:04.1f}, el tope es {SALTO_MAX:.0f}")

    # 7 · ninguna escena percibida demasiado corta
    #
    # ANTES ESTO LEIA LA DURACION DEL PLAN y por eso decia "el mas corto dura 8s" sobre un
    # video donde el user vio tomas de 2 o 3 segundos. Lo que el ojo lee como una escena
    # termina cuando cambia la imagen, venga el cambio de un corte mio o de un corte que
    # la fuente traia adentro. Aca se cuentan los dos.
    marcas = sorted(set(bordes + [round(c, 2) for c in internos]))
    tramos = [(a, b - a) for a, b in zip(marcas, marcas[1:])]
    tramos = [(a, d) for a, d in tramos if _en_ventana(a)]
    cortos = [(a, d) for a, d in tramos if d < TRAMO_MINIMO]
    marca("7 · sin escenas relampago", not cortos,
          f"la mas corta dura {min(d for _, d in tramos):.1f}s"
          + (f", {len(cortos)} por debajo de {TRAMO_MINIMO:.0f}s" if cortos else ""))

    # 8 · sin pantalla negra
    #
    # ANTES ESTO CONTABA PLANOS y toleraba 29, o sea que toleraba el defecto en vez de
    # medirlo. Y encima contaba mal: leia la salida de ffmpeg como 1 byte por pixel cuando
    # `normalize` la entrega en RGB de 3, asi que promediaba Y, U y V juntas y un cuadro
    # NEGRO medía ~85 de luz en vez de 0.
    #
    # Ahora es simple y es sobre el archivo: no puede haber DOS SEGUNDOS seguidos en
    # negro en ningun lado. El user lo marco en 6:10 y habia 5,4 s.
    vis = np.percentile(A, 99.5, axis=1)
    oscuro = np.array([vis[i:i+paso].max() < VISIBLE_MINIMO for i in range(ini_q, fin_q - paso)])
    negras = [(a + DESDE, d) for a, d in rachas(oscuro)]
    peor_negro = max((d for _, d in negras), default=0.0)
    marca("8 · sin pantalla negra", not negras,
          f"{len(negras)} tramos en negro"
          + (f", el mas largo {peor_negro:.1f}s en "
             f"{int(negras[0][0]//60)}:{negras[0][0]%60:04.1f}" if negras else ""))

    # 11 · ningun plano quieto
    #
    # "esta escena es estatica, esta mal. Siempre tiene que haber dinamismo (un video), no
    # puede ser que me muestres una img y hagas zoom". Se mide sobre el ARCHIVO y por
    # tramos: un plano puede moverse al principio y quedarse quieto despues.
    quieto = np.array([dif[i:i+paso].mean() < MOV_MINIMO
                       for i in range(ini_q, fin_q - paso)])
    quietos = [(a + DESDE, d) for a, d in rachas(quieto)]
    marca("11 · sin planos quietos", not quietos,
          f"{len(quietos)} tramos sin movimiento"
          + (f", el mas largo {max(d for _, d in quietos):.1f}s en "
             f"{int(quietos[0][0]//60)}:{quietos[0][0]%60:04.1f}" if quietos else ""))

    # 10 · todo plano cuadriculado recibio tratamiento
    #
    # HONESTIDAD SOBRE QUE MIDE ESTE CRITERIO. La primera version intentaba medir el
    # cuadriculado SOBRE LA SALIDA y estaba mal: daba FALLA en el video ya arreglado.
    # Se probaron tres metricas y las tres se dejan engañar:
    #
    #   - cociente meseta (dentro/entre baldosas): un degradado LISO es plano adentro
    #     igual que una meseta. La salida del modelo es lisa por diseño, asi que la
    #     marcaba como cuadriculada.
    #   - salto en la rejilla: despues del modelo la grilla de la fuente ya no existe,
    #     asi que medir a ese paso no encuentra nada real.
    #   - pico espectral: lo domina la estructura de la imagen, no el bloque.
    #
    # Asi que este criterio NO mide la salida: mide COBERTURA. Todo plano cuya fuente
    # este aplastada en mesetas tiene que haber recibido tratamiento (el modelo si se
    # amplia 2x o mas, blur si no). Es deterministico y frena la regresion que importa:
    # que alguien rehaga el video sin correr `mejorar.py` y vuelvan los cuadrados.
    #
    # Lo que este criterio NO puede hacer es juzgar si el resultado se ve bien. Eso hoy
    # se valida a ojo sobre cuadros, y esta bien que se sepa.
    ia = os.path.join(AQUI, ".ia")
    try:
        sys.path.insert(0, AQUI)
        import nitidez
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as ex:
            med = list(ex.map(nitidez.medir, ["|".join(f) for f in filas]))
        anchoS = int(subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
            "-show_entries","stream=width","-of","default=nw=1:nk=1",VIDEO],
            capture_output=True,text=True).stdout.split()[0])
        def _claves(nombre):
            r = os.path.join(ia, nombre)
            if not os.path.exists(r):
                return set()
            return {"|".join(l.split("|")[:4]) for l in open(r) if l.strip()}
        tratados = _claves("mapa.txt") | _claves("blur.txt")
        sueltos = []
        for f, m in zip(filas, med):
            if m is None or m[4] <= 0:
                continue
            if "|".join([f[1], f[2], f[3], f[4]]) not in tratados:
                sueltos.append(f"{f[0]}(coc {m[3]:.2f})")
        marca("10 · cuadriculado tratado", not sueltos,
              f"{len(tratados)} planos tratados, {len(sueltos)} sin tratar"
              + (f": {', '.join(sueltos[:5])}" if sueltos else ""))
    except Exception as e:
        marca("10 · cuadriculado tratado", False, f"no se pudo medir: {type(e).__name__} {e}")

    # 9 · el audio
    qa = subprocess.run(["python3.10", os.path.join(RAIZ, "scripts", "qa_scan_spectral.py"),
                         AUDIO], capture_output=True, text=True).stdout
    if not qa.strip():
        qa = "sin salida del QA espectral"
    marca("9 · QA espectral del audio", "OK" in qa,
          (qa.strip().splitlines() or ["sin salida"])[-1][:52])

    print()
    fallan = [n for ok, n, _ in resultados if not ok]
    if fallan:
        print(f"  NO ESTA PARA ENTREGAR · fallan {len(fallan)} de {len(resultados)}")
        for n in fallan: print(f"      {n}")
        return 1
    print(f"  LISTO PARA ENTREGAR · pasan los {len(resultados)} criterios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
