#!/usr/bin/env python3
"""Arma la lista de planos del video cumpliendo las CUATRO reglas por construccion.

    python3.10 transmissions/02/bj3_n_pt/video/planos.py > lista.txt

POR QUE EXISTE ESTE ARCHIVO
--------------------------------------------------------------------------------
Las reglas estan en `PLAN_RONDA6.md` §V2 y las definio el user:

    1. Ninguna combinacion de fuente + recorte + variante + grado dos veces
    2. Ninguna fuente mas de 3 veces en todo el video
    3. Dos apariciones de la misma fuente nunca en el mismo minuto
    4. Dos planos consecutivos nunca comparten fuente

Estaban escritas a mano en el shell y se rompian solas: el primer minuto salio con el
mismo clip solar CINCO veces. La guarda del montaje solo miraba la 1 y la 4, asi que las
otras dos pasaban sin que nada las frenara.

Aca las cuatro se cumplen porque el asignador NO PUEDE elegir una fuente que las rompa:

    regla 2 -> cada fuente tiene un presupuesto de 3 y se descuenta
    regla 3 -> se lleva registro de que fuentes ya salieron en el minuto en curso
    regla 4 -> la fuente del plano anterior queda excluida
    regla 1 -> cada aparicion consume un recorte distinto del pool de esa fuente

Si el pool de un acto se queda sin fuentes elegibles, esto ABORTA. Es a proposito: es
preferible que no salga el video a que salga rompiendo las reglas.

EL PRESUPUESTO
--------------------------------------------------------------------------------
28 fuentes por 3 apariciones son 84 planos posibles. El video necesita 77. El margen es
de 7, o sea que no sobra: si se saca una fuente hay que sacar planos o traer otra.
"""
import collections
import concurrent.futures as cf
import json
import zlib
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FTE = os.path.join(AQUI, "fuentes")
GEN = os.path.join(AQUI, "generado")
LLUVIA = os.environ.get("CLIPS", os.path.expanduser("~/Downloads/Videos-Aem"))
PALMA_SRC = os.environ.get("PALMA_SRC", os.path.expanduser("~/Downloads/IMG_4842.MOV"))

F_VEL = 1.0   # la velocidad del plano en curso, para la validacion
MAX_POR_FUENTE = 3
MIN_DUR = 7.0   # ningun plano puede durar menos, salvo los generados que son de 3 s

# LAS VENTANAS LIMPIAS SALEN DE `ventanas.json`, que produce `ventanas.py` escaneando
# cada fuente cada 0,5 s. NO se escriben a mano.
#
# Se escribian a mano y se desactualizaban en silencio: `sol2` tenia puesto [8, 290]
# cuando su ultima ventana limpia termina en 175. Un plano arrancaba en 145,9 y a 16x
# consumia 144 s, o sea que se metia 115 s adentro de material sucio y con cortes. Eso
# producia los saltos de 4:44, 9:02, 9:24 y 9:37: el plano mostraba una imagen y saltaba
# a otra en el medio.
try:
    with open(os.path.join(AQUI, "ventanas.json")) as _fh:
        VENTANAS = {k: [tuple(v) for v in vs] for k, vs in json.load(_fh).items()}
except FileNotFoundError:
    sys.exit("ABORTA: falta ventanas.json. Corre primero:\n"
             "    python3.10 transmissions/02/bj3_n_pt/video/ventanas.py")

# ---------------------------------------------------------------- las fuentes
# (clave, ruta, categoria, velocidad, tratamiento, [recortes...])
#
# `velocidad` es el factor de setpts. 1.0 es tiempo real. Los recortes son uno por
# aparicion posible, y son distintos entre si para que la regla 1 se cumpla sola.
#
# Los clips DEL USER son verticales (3840x2160 con rotacion -90 = 2160x3840). Los de la
# palmera van sobre x>1250, que es donde estan las hojas: el edificio vive en x<900.
F = {}


def src(clave, ruta, cat, vel, trat, recortes, variantes=None, ventana=None):
    F[clave] = dict(ruta=ruta, cat=cat, vel=vel, trat=trat, recortes=recortes,
                    variantes=variantes or ["", "negate", "transpose=1"],
                    ventana=ventana or [])


# --- solar. Nueve fuentes distintas, no una repetida nueve veces.
#     Las seis fulguraciones de la NASA son 4096x4096 y duran 4,5 s: alcanza para tres
#     recortes distintos porque el cuadro es enorme, no porque el clip sea largo.
# LAS VELOCIDADES SALEN DE LAS VENTANAS MEDIDAS, no al revés. Un plano de `dur` segundos
# a velocidad `v` consume `dur/v` segundos de fuente, y eso tiene que caber adentro de UNA
# ventana limpia. Medido en `ventanas.json`:
#
#     SDO_20170904_171 (sol2)   ventanas de ~30 s  ->  a 16x un plano de 12 s pedia 192 s
#     SDO_20170904_304 (sol3)   una sola de 215 s  ->  aguanta cualquier cosa
#     SDO_20170910_131 (sol)    3,4 s              ->  solo sirve muy ralentizada
#     las seis fulguraciones    4,3 s              ->  idem
#
# Por eso sol2 baja de 16x a 2x y sol pasa a 4x. A 16x sol2 se metia 115 s adentro de
# material sucio con cortes, y eso producia los saltos de 4:44, 9:02, 9:24 y 9:37.
#
# LA VELOCIDAD DE LAS SOLARES CORTAS es alta y no es una decision estetica: es
# aritmetica. El clip corto tiene 4,2 s limpios y las fulguraciones 4,5 s. A 1,5x un
# plano de 10 s consume 6,7 s de fuente, o sea que NO ENTRA, y el asignador se quedaba
# sin opciones para los planos largos del acto 6. A 3,0x consume 3,3 s y entran todos.
# Con la mezcla de cuadros encima no se entrecorta.
src("sol",   f"{FTE}/SDO_20170910_131_AR12673X8_4k.webm", "cielo", 4.0, "sol",
    ["1900:1069:2100:1750", "2200:1238:1800:1900", "1600:900:2700:2000"], ventana=[2.4, 6.6])
src("sol2",  f"{FTE}/SDO_20170904_171_AR12673X_4kcomplete.webm", "cielo", 2.0, "sol",
    ["2600:1462:1300:1500", "4096:2304:0:1000", "1800:1013:2400:2100"], ventana=[8, 290])
src("sol3",  f"{FTE}/SDO_20170904_304_AR12673X_4k.webm", "cielo", 1.5, "sol",
    ["3000:1688:700:1300", "2800:1575:1100:1450", "2400:1350:1500:1750"], ventana=[30, 205])
for k, f, w in (("fl1", "pd_flare_2022nov", 4.85), ("fl2", "pd_flare_2022abr", 4.57),
                ("fl3", "pd_flare_2024feb", 4.85), ("fl4", "pd_flare_may131", 4.55),
                ("fl5", "pd_flare_may171", 4.55), ("fl6", "pd_flare_may304", 4.55)):
    src(k, f"{FTE}/{f}.webm", "cielo", 3.5, "sol",
        ["2600:1462:750:1300", "3400:1913:350:1100", "2000:1125:1050:1500"], ventana=[0.2, w])

# --- lluvia y planeta. Los cuatro clips del user.
src("r39", f"{LLUVIA}/IMG_4739.MOV", "lluvia", 1.5, "campo",
    ["500:190:800:2400", "2000:130:80:2600", "1700:110:200:1900"], ventana=[0.1, 9.7])
src("r40", f"{LLUVIA}/IMG_4740.MOV", "lluvia", 2.0, "charco",
    ["900:506:560:1700", "800:450:620:1500", "1200:675:420:1600"], ventana=[0.3, 10.2])
src("r41", f"{LLUVIA}/IMG_4741.MOV", "lluvia", 1.5, "campo",
    ["700:400:800:1500", "800:280:700:1800", "700:300:900:1900"], ventana=[0.1, 3.4])
# arranca en 1.5 y no en 0.2: los primeros cuadros dan lineas rectas en el recorte
src("r42", f"{LLUVIA}/IMG_4742.MOV", "lluvia", 1.5, "campo",
    ["900:120:700:2700", "600:200:900:2900", "1200:110:400:3000"], ventana=[1.5, 7.8])
src("palma", PALMA_SRC, "planeta", 1.5, "palma",
    ["860:484:1280:200", "900:506:1240:1600", "820:461:1320:2800"], ventana=[0.3, 11.8])

# --- agua y descarga
src("rio",  f"{FTE}/pd_rapidos_grand_canyon.webm", "agua", 3.0, "agua",
    ["620:349:330:210", "700:394:280:180", "820:461:300:200"], ventana=[8, 86])
src("rayo", f"{FTE}/pd_tormenta_argentina.webm", "descarga", 1.5, "cielo",
    ["1500:844:300:120", "1150:647:640:390", "1000:563:800:480"], ventana=[0.3, 9.4])
# `pd_glm_rayos` QUEDO AFUERA. Es un video institucional de NOAA y adentro tiene un
# lanzamiento de cohete, una bandera y un reloj en pantalla. Salio al aire en 3:43. Se
# podria usar por ventanas, pero una fuente que contiene un cohete no vale el riesgo.
# `pd_iceberg` tiene MAPA superpuesto con lineas punteadas blancas, que salio en 5:12.
# Se queda pero solo dentro de sus ventanas limpias medidas, no de punta a punta.
src("hielo", f"{FTE}/pd_iceberg.webm", "agua", 1.5, "campo",
    ["2200:1238:800:450", "1800:1013:1200:700", "1500:844:1600:900"], ventana=[23, 38])

# --- fuego
src("lava1", f"{FTE}/usgs_lava_01.mp4", "fuego", 1.0, "arch",
    ["800:450:600:200", "620:350:880:330", "640:360:860:300"], ventana=[5.5, 20.5])
src("lava2", f"{FTE}/usgs_fuente_lava.mp4", "fuego", 1.0, "arch",
    ["500:280:1250:560", "560:315:1200:545", "480:270:1280:580"], ventana=[6.5, 65])
src("erup",  f"{FTE}/usgs_erupcion_2025.mp4", "fuego", 1.5, "arch",
    ["1100:619:420:230", "1000:563:460:260", "1200:675:380:280"], ventana=[55, 84])

# --- criaturas
# EL PELO. Los recortes bajan de 340-700 px a 260-300: con 700 px de ancho en el segundo
# 40 se veia el lomo y el anca del animal contra el pasto. Un recorte fijo sobre un bicho
# que camina NO se queda abstracto, y hay que verificarlo en el punto de entrada real y
# no en el que se probo.
# La ventana es 42-55 s y no cualquiera: se midio la COMPACIDAD de la mancha oscura en
# 42 combinaciones de punto de entrada y recorte, y solo el tramo final del clip da pelo
# sin silueta reconocible. Antes de eso el animal camina y el lomo entra en cuadro.
src("pelo",   f"{FTE}/cc0_bison_yukon.webm", "criatura", 3.2, "pelo",
    ["300:169:1600:520", "280:158:1350:150", "300:169:1560:190"], ventana=[42, 55])
src("abisal", f"{FTE}/pd_bicho_abisal.webm", "criatura", 1.5, "arch",
    ["1200:675:360:200", "1000:563:500:280", "900:506:600:330"], ventana=[2, 36])
src("medusa", f"{FTE}/noaa_medusa_01.mp4", "alien", 2.0, "medusa",
    ["820:461:429:449", "620:348:726:482", "480:270:923:582"], ventana=[13.5, 29])
src("sifon",  f"{FTE}/noaa_sifonoforo.mp4", "alien", 2.0, "arch",
    ["1000:563:460:250", "700:394:600:260", "820:461:520:280"], ventana=[10, 22])
src("b02", f"{GEN}/bicho_02.mp4", "generado", 1.5, "arch",
    ["560:280:110:150", "460:300:30:200", "570:285:100:145"], ventana=[0.05, 2.6])
src("b03", f"{GEN}/bicho_03.mp4", "generado", 1.5, "arch",
    ["620:300:70:120", "600:290:80:130", "580:300:90:140"], ventana=[0.05, 2.6])
src("b05", f"{GEN}/bicho_05.mp4", "generado", 1.5, "arch",
    ["600:300:80:110", "560:290:100:130", "580:280:90:150"], ventana=[0.05, 2.6])
src("boca", f"{GEN}/boca_01.mp4", "generado", 1.5, "arch",
    ["600:300:80:110", "470:300:25:220", "580:290:90:115"], ventana=[0.05, 2.6])

VARIANTES = ["", "negate", "transpose=1", "hflip", "vflip", "negate,hflip",
             "negate,transpose=1", "transpose=2", "negate,vflip"]


def sello(txt):
    """Numero estable a partir de un texto.

    `hash()` de Python esta ALEATORIZADO por proceso desde la 3.3, asi que la variante
    de cada plano salia distinta en cada corrida: el plan no era reproducible y el
    reuso de planos del montaje casi no servia (9 de 63 en la ultima corrida). Con
    crc32 el mismo plan da el mismo resultado siempre.
    """
    return zlib.crc32(txt.encode())

# ---------------------------------------------------------------- la estructura
# (nombre del acto, [(duracion, [categorias elegibles])...])
#
# El orden de categorias es una PREFERENCIA, no una obligacion: si la primera no tiene
# fuentes disponibles se pasa a la siguiente. Asi la estructura narrativa se mantiene
# aunque el presupuesto obligue a sustituir.
# Cada slot lleva VARIAS categorias aceptables, en orden de preferencia. Con una sola
# el presupuesto no cierra: hay 3 fuentes de fuego (9 apariciones) y el plan pedia 11, y
# 2 de agua (6) contra 9 pedidas. Con alternativas el asignador reparte solo y la
# estructura narrativa se mantiene igual.
# LA PROGRESION, reordenada con tres pedidos concretos:
#
#   "cuando se siente el repiqueteo fuerte de la lluvia ahi es cuando tenes que mostrar
#    mas de agua, no tanto planetita"
#   "los animales trata de guardarlo para cuando habla tipo 7:40 en adelante, no gastes
#    la bala antes"
#   "al principio mas tomas del planeta ... una plantita del planeta mostra recien en el
#    minuto 2"
#
# Asi que: el acto del repiqueteo (4:44 a 6:20) es AGUA Y DESCARGA sin nada de planeta,
# las criaturas no aparecen hasta el acto 6, y la vegetacion entra pasado el minuto 2.
#
# Y ningun plano baja de 9 s salvo los generados. Se marcaron varios como "toma muy
# corta"; con 63 planos en 667 s el promedio queda en 10,6.
ACTOS = [
    ("0 · el cielo", [(9, ["cielo"]), (9, ["cielo"]), (9, ["cielo"]), (9, ["cielo"]),
                      (9, ["cielo"]), (8, ["cielo"]), (8, ["cielo"])]),
    # el planeta. La vegetacion recien despues del minuto 2, o sea del plano 11 en mas
    ("1 · el planeta",
     [(11, ["lluvia"]), (11, ["cielo"]), (11, ["lluvia"]), (11, ["agua"]),
      (11, ["cielo"]), (11, ["lluvia"]), (11, ["cielo"]), (10, ["lluvia"]),
      (11, ["cielo"]), (11, ["agua", "descarga"]),
      (11, ["planeta"]),                                   # 2:00 · la primera vegetacion
      (11, ["lluvia"]), (11, ["cielo"]), (10, ["planeta"]), (11, ["lluvia"]),
      (11, ["cielo"]), (11, ["planeta"]), (10, ["lluvia"]), (11, ["cielo"]),
      (11, ["fuego"])]),
    # EL REPIQUETEO. Solo agua y descarga: nada de planeta, nada de cielo.
    # OCHO planos de 12 s y no nueve de 11: en el minuto 5 caian seis planos y las
    # fuentes de agua disponibles son cinco, asi que el asignador se quedaba corto y
    # metia una criatura en pleno repiqueteo. Con planos mas largos entran cinco por
    # minuto y el acto se sostiene con agua sola, que es lo que se pidio.
    ("2 · el repiqueteo",
     [(12, ["lluvia"]), (12, ["descarga"]), (12, ["agua"]), (12, ["lluvia"]),
      (12, ["descarga"]), (12, ["agua"]), (12, ["lluvia"]), (12, ["descarga"])]),
    # la transicion. Todavia SIN criaturas: la bala se guarda para las voces.
    ("3 · antes de la voz",
     [(11, ["lluvia"]), (11, ["cielo"]), (11, ["generado"]), (11, ["cielo"]),
      (11, ["generado"]), (11, ["fuego"]), (10, ["cielo"])]),
    ("4 · el alien", [(7, ["alien"]), (6, ["alien"])]),
    ("5 · el estallido", [(10, ["fuego"]), (10, ["fuego"])]),
    # LOS CORTES CAEN SOBRE LA MELODIA: 501, 524, 544, 564, 582 y 603 s, y el acto
    # empieza en 489. Aca entran los animales, con las voces y con el moog. La lava
    # tambien, que segun el user "esta linda con el moog".
    ("6 · el moog y los animales",
     [(12, ["fuego"]),                                        # corte en 501
      (12, ["criatura"]), (11, ["fuego"]),                    # corte en 524
      (10, ["cielo"]), (10, ["fuego"]),                       # corte en 544, EL PICO
      (10, ["criatura"]), (10, ["fuego"]),                    # corte en 564
      (9, ["cielo"]), (9, ["criatura"]),                      # corte en 582
      (11, ["fuego"]), (10, ["cielo"]),                       # corte en 603
      (12, ["fuego"]), (12, ["agua", "fuego"])]),             # corte en 627
    # 16+18 = 34, o sea que el tercer plano arranca en 11:01 y cae en el MINUTO 11. Con
    # 15+15 arrancaba en 10:57, los tres quedaban en el minuto 10, y como solo hay dos
    # fuentes alien la regla 3 obligaba a meter otra cosa en el cierre.
    ("7 · el cierre", [(16, ["alien"]), (18, ["alien"]), (12, ["alien"])]),
]

NEGRO = 6


def ventanas_de(clave):
    """Las ventanas limpias medidas para esa fuente, de mayor a menor."""
    v = VENTANAS.get(os.path.basename(F[clave]["ruta"]), [])
    return sorted(v, key=lambda w: w[1] - w[0], reverse=True)


def entra(clave, dur):
    """Si la ventana limpia de la fuente alcanza para un plano de `dur` segundos.

    Sin esto el asignador elegia fuentes imposibles: el clip solar corto tiene 4,2 s
    limpios y le tocaba un plano de 7 s, que a 1,5x consume 4,67. El montaje abortaba
    recien al renderizar, despues de hacer nueve planos al pepe.
    """
    v = F[clave]
    consumo = dur * (1.0 / v["vel"] if v["vel"] else 16.0)
    # el plano ENTERO tiene que caber adentro de UNA ventana limpia, no repartido
    return any((b - a) >= consumo + 0.4 for a, b in ventanas_de(clave))


def elegir(cands, gastado, del_minuto, previa, dur):
    """La fuente con mas presupuesto libre entre las que NO rompen ninguna regla."""
    libres = [c for c in cands
              if gastado[c] < MAX_POR_FUENTE     # regla 2
              and c not in del_minuto            # regla 3
              and c != previa                    # regla 4
              and entra(c, dur)]                 # y que la ventana limpia alcance
    if not libres:
        return None
    return max(libres, key=lambda c: (MAX_POR_FUENTE - gastado[c], -len(F[c]["cat"])))


# Los parametros de cada tratamiento, IGUALES a los de `montaje.sh`. Estaban solo alla y
# aca se medía con una cadena simplificada (contraste fijo 1.8, sin brightness), asi que
# la prediccion no coincidia con lo que se renderizaba: se marcaban planos como buenos y
# salian negros igual.
TRATO = {                      # tratamiento: (contraste, brillo, curva por defecto)
    "sol":    (1.7,  -0.06, "duro"),
    "palma":  (1.9,  -0.06, "duro"),
    "pelo":   (1.45,  0.02, "duro"),
    "charco": (1.9,  -0.06, "duro"),
    "campo":  (1.9,  -0.06, "duro"),
    "agua":   (1.9,  -0.06, "duro"),
    "medusa": (1.85,  0.02, "duro"),
    "arch":   (1.7,  -0.06, "suave"),
}
CURVA_SUAVE = "0/0 0.30/0.12 0.70/0.80 1/0.86"


def cadena(recorte, variante, trat, curva_nom, curva):
    """El filtro TAL COMO lo arma `montaje.sh`, para que medir y renderizar coincidan."""
    c, b, _ = TRATO.get(trat, TRATO["arch"])
    vf = [f"setpts={F_VEL}*PTS", f"crop={recorte}"]
    if trat == "charco":
        vf.append("lenscorrection=k1=-0.32:k2=-0.10")
    if variante:
        vf.append(variante)
    vf.append("format=gray")
    if trat == "sol":
        vf.append("tmix=frames=8")
    vf += ["normalize=blackpt=black:whitept=0xB0B0B0:smoothing=250",
           f"eq=contrast={c}:brightness={b}", f"curves=all='{curva}'"]
    return vf


def cerrar_sobre_sujeto(ruta, ss, dur, recorte, variante, trat, factor):
    """Recorte mas cerrado, centrado en la parte luminosa del cuadro.

    Hay material que queda casi negro y NO es un problema de grado: el disco solar esta
    sobre el espacio, y la medusa y el sifonoforo sobre oceano profundo. El sujeto ocupa
    una fraccion del cuadro y el resto es negro de origen. Ninguna curva inventa detalle
    donde no hay nada; lo que corresponde es cerrar el encuadre sobre el sujeto.

    Devuelve None si el recorte cerrado no entra en la fuente.
    """
    import numpy as np
    import subprocess
    w, h, x, y = (int(v) for v in recorte.split(":"))
    vf = [f"crop={recorte}"]
    if variante:
        vf.append(variante)
    vf += ["format=gray", "scale=96:54"]
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta, "-t", str(dur),
                        "-vf", ",".join(vf) + ",fps=1", "-frames:v", "5",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(o) // (96 * 54)
    if n < 2:
        return None
    a = np.frombuffer(o[:n * 96 * 54], dtype=np.uint8).reshape(n, 54, 96).astype(float).mean(axis=0)
    m = a > max(np.percentile(a, 82), 12)
    if m.sum() < 20:
        return None
    ys, xs = np.nonzero(m)
    cx, cy = xs.mean() / 96, ys.mean() / 54       # centro del sujeto, en fraccion
    nw, nh = int(w * factor) // 2 * 2, int(h * factor) // 2 * 2
    nx = int(np.clip(x + cx * w - nw / 2, 0, x + w - nw))
    ny = int(np.clip(y + cy * h - nh / 2, 0, y + h - nh))
    if nw < 200 or nh < 120:
        return None
    return f"{nw}:{nh}:{nx}:{ny}"


def analizar(args):
    """UNA sola pasada de ffmpeg por candidata: revision y brillo del mismo material.

    Antes eran tres llamadas por candidata (validar, medir brillo, buscar el sujeto) y
    la generacion del plan no terminaba nunca: la mataron dos veces por lenta. Los tres
    calculos salen de los mismos cuadros, asi que se piden una vez sola.

    Devuelve (ok, luz, negro, ss, recorte, curva_nom).
    """
    import numpy as np
    import subprocess
    ruta, ss, dur, recorte, variante, trat, curva, curva_nom, vel, es_pelo = args
    global F_VEL
    F_VEL = vel
    def leer(vf, w, h, cuantos=8):
        o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta,
                            "-t", str(dur), "-vf", ",".join(vf) + f",fps={cuantos/max(dur,1):.3f}",
                            "-frames:v", str(cuantos), "-f", "rawvideo", "-"],
                           capture_output=True).stdout
        n = len(o) // (w * h)
        return None if n < 2 else np.frombuffer(o[:n*w*h], dtype=np.uint8).reshape(n, h, w).astype(float)

    # LA REVISION VA SOBRE MATERIAL CRUDO. Sobre cuadros ya gradados el detector de
    # lineas rectas dispara siempre: despues de la curva dura todo borde es duro. Son
    # dos necesidades distintas y necesitan dos pasadas.
    crudo = [f"setpts={vel}*PTS", f"crop={recorte}"]
    if variante:
        crudo.append(variante)
    crudo += ["format=gray", "scale=320:180"]
    m = leer(crudo, 320, 180)
    if m is None:
        return (False, 0.0, 1.0, ss, recorte, curva_nom)
    try:
        import verificar
        ok = not verificar.revisar(m, es_pelo=es_pelo)
    except Exception:
        ok = True
    if not ok:
        return (False, 0.0, 1.0, ss, recorte, curva_nom)

    # el brillo SI se mide sobre la cadena completa, que es lo que se va a ver
    g = leer(cadena(recorte, variante, trat, curva_nom, curva) + ["scale=96:54"], 96, 54, 6)
    if g is None:
        return (False, 0.0, 1.0, ss, recorte, curva_nom)
    return (True, float(g.mean()), float((g < 18).mean()), ss, recorte, curva_nom)


def brillo(ruta, ss, dur, recorte, variante, curva, trat="arch", curva_nom="duro"):
    """Luminancia media y fraccion casi negra del plano ya gradado."""
    import numpy as np
    import subprocess
    vf = cadena(recorte, variante, trat, curva_nom, curva) + ["scale=96:54"]
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta, "-t", str(dur),
                        "-vf", ",".join(vf) + ",fps=1", "-frames:v", "6",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(o) // (96 * 54)
    if n < 2:
        return 0.0, 1.0
    a = np.frombuffer(o[:n * 96 * 54], dtype=np.uint8).reshape(n, -1).astype(float)
    return a.mean(), float((a < 18).mean())


# Las dos curvas, en el mismo orden que en `montaje.sh`
CURVA_DURO = "0/0 0.38/0.05 0.62/0.72 1/0.78"
CURVA_ALZADA = "0/0.02 0.26/0.18 0.58/0.74 1/0.82"
LUZ_MINIMA = 10.0        # abajo de esto el plano es pantalla negra
NEGRO_MAXIMO = 0.72      # y esto es cuanto del cuadro se acepta casi negro


def valida(ruta, ss, dur, recorte, variante, trat):
    """Revisa el plano tal como va a salir. Devuelve None si esta bien, o el motivo.

    Esto vive ACA y no solo en `verificar.py` a proposito: si el generador puede emitir
    planos que despues el verificador rechaza, la unica salida es iterar a mano cada vez,
    y eso ya paso demasiadas veces en este video. Con la validacion adentro, el generador
    prueba los otros recortes y las otras ventanas de la fuente antes de rendirse.
    """
    try:
        import verificar
    except Exception:
        return None                       # sin el modulo se sigue, no se aborta
    m = verificar.render(ruta, ss, dur, recorte, variante, str(F_VEL))
    if m is None:
        return "no se pudo leer"
    fallas = verificar.revisar(m, es_pelo=(trat == "pelo"))
    return "; ".join(fallas[:1]) if fallas else None


def main():
    gastado = collections.Counter()
    previa = None
    minuto_actual = 0
    del_minuto = set()
    t = float(NEGRO)
    lineas, mapa = [], []

    for acto, slots in ACTOS:
        for dur, cats in slots:
            m = int(t // 60)
            if m != minuto_actual:
                minuto_actual, del_minuto = m, set()
            cands = [k for k, v in F.items() if v["cat"] in cats]
            elegida = elegir(cands, gastado, del_minuto, previa, dur)
            if elegida is None:                  # se prueba con cualquier categoria
                elegida = elegir(list(F), gastado, del_minuto, previa, dur)
            if elegida is None:
                # diagnostico: por que quedo sin opciones
                det = []
                for k in sorted(F):
                    r = []
                    if gastado[k] >= MAX_POR_FUENTE: r.append(f"gastada {gastado[k]}/3")
                    if k in del_minuto: r.append("ya salio este minuto")
                    if k == previa: r.append("es la anterior")
                    if not entra(k, dur): r.append("la ventana no alcanza")
                    det.append(f"      {k:8} {v['cat'] if False else F[k]['cat']:10} "
                               + (", ".join(r) if r else "LIBRE"))
                sys.exit(f"ABORTA: no queda fuente elegible para el plano de {dur}s en "
                         f"{int(t)//60}:{int(t)%60:02d}, acto {acto}, "
                         f"categorias {cats}\n" + "\n".join(det))
            v = F[elegida]
            n = gastado[elegida]                 # 0, 1 o 2: que aparicion es
            gastado[elegida] += 1
            del_minuto.add(elegida)
            previa = elegida

            consumo = dur * (1.0 / v["vel"] if v["vel"] else 16.0)
            # se elige la ventana limpia mas grande donde el plano entre entero, y
            # dentro de ella un punto distinto por cada aparicion
            cabe = [w for w in ventanas_de(elegida) if (w[1] - w[0]) >= consumo + 0.4]
            # se prueban combinaciones de ventana x recorte x posicion hasta que una pase
            # la revision cuadro por cuadro. La primera candidata es la de siempre, asi
            # que si todo esta bien no cambia nada.
            global F_VEL
            F_VEL = v["vel"]
            elegido = None
            curva_eleg = "duro"
            candidatas = []
            for iw, (a, b) in enumerate(cabe):
                hueco = (b - a) - consumo - 0.2
                for frac in (((n * 0.37) % 1.0), 0.0, 0.55, 0.9):
                    for ir in range(len(v["recortes"])):
                        candidatas.append((a + 0.2 + hueco * frac,
                                           v["recortes"][(n + ir) % len(v["recortes"])]))
            variante = VARIANTES[(sello(elegida) + n * 3) % len(VARIANTES)]

            # DOS PASADAS. Primero se busca un tramo que pase la revision Y que no quede
            # pantalla negra con la curva normal. Si ninguno lo logra, se repite la busqueda
            # con la curva levantada.
            #
            # La version anterior escalaba la curva pero NO verificaba que sirviera, y
            # tampoco probaba otro punto de entrada: si la region de la fuente ya era negra,
            # ninguna curva la salvaba. Quedaron 31 planos en pantalla negra de 62.
            mejor = None
            base = CURVA_SUAVE if v["trat"] == "arch" else CURVA_DURO
            for curva_nom, curva in (("duro", base), ("alzada", CURVA_ALZADA)):
                trabajos = [(v["ruta"], round(cs, 2), dur, cr, variante, v["trat"],
                             curva, curva_nom, v["vel"], v["trat"] == "pelo")
                            for cs, cr in candidatas]
                with cf.ThreadPoolExecutor(max_workers=6) as pool:
                    for ok, luz, negro, cs, cr, cn in pool.map(analizar, trabajos):
                        if not ok:
                            continue
                        if mejor is None or luz > mejor[0]:
                            mejor = (luz, cs, cr, cn)
                        if luz >= LUZ_MINIMA and negro <= NEGRO_MAXIMO and not elegido:
                            elegido = (cs, cr)
                            curva_eleg = cn
                if elegido:
                    break
            # SI NINGUNA EVITA LA PANTALLA NEGRA se prueba cerrando el encuadre sobre el
            # sujeto. Hay material que es oscuro por ENCUADRE y no por grado: el disco
            # solar esta sobre el espacio, la medusa sobre oceano profundo. El sujeto
            # ocupa una fraccion del cuadro y el resto es negro de origen; ninguna curva
            # inventa detalle donde no hay nada.
            #
            # Esto corre solo para los planos que lo necesitan, y despues de la busqueda
            # normal: calcularlo para todos costaba 372 llamadas a ffmpeg en serie y la
            # generacion del plan no terminaba.
            if not elegido and mejor:
                cerradas = []
                for factor in (0.62, 0.42, 0.30):
                    r = cerrar_sobre_sujeto(v["ruta"], round(mejor[1], 2), dur, mejor[2],
                                            variante, v["trat"], factor)
                    if r:
                        cerradas.append((mejor[1], r))
                if cerradas:
                    trabajos = [(v["ruta"], round(cs, 2), dur, cr, variante, v["trat"],
                                 CURVA_ALZADA, "alzada", v["vel"], v["trat"] == "pelo")
                                for cs, cr in cerradas]
                    with cf.ThreadPoolExecutor(max_workers=4) as pool:
                        for ok, luz, negro, cs, cr, cn in pool.map(analizar, trabajos):
                            if ok and (mejor is None or luz > mejor[0]):
                                mejor = (luz, cs, cr, cn)
                            if ok and luz >= LUZ_MINIMA and negro <= NEGRO_MAXIMO:
                                elegido = (cs, cr); curva_eleg = cn
                                break
            if not elegido and mejor:
                elegido = (mejor[1], mejor[2])
                curva_eleg = mejor[3]
            if elegido is None:
                sys.exit(f"ABORTA: ninguna combinacion de {elegida} pasa la revision para "
                         f"el plano de {dur}s en {int(t)//60}:{int(t)%60:02d}")
            ss, recorte_eleg = elegido
            lineas.append("|".join([elegida, v["ruta"], f"{ss:.2f}", str(dur),
                                    recorte_eleg, variante,
                                    v["trat"], f"{v['vel']:.4f}", curva_eleg]))
            mapa.append((int(t), elegida, dur, acto))
            t += dur

    total = t
    print("\n".join(lineas))
    print(f"# {len(lineas)} planos · {total:.0f}s de video · {len(gastado)} fuentes",
          file=sys.stderr)
    peor = gastado.most_common(1)[0]
    print(f"# la fuente mas usada: {peor[0]} con {peor[1]} apariciones (el maximo es "
          f"{MAX_POR_FUENTE})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
