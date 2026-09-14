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
RAIZ_REPO = AQUI
while RAIZ_REPO != "/" and not os.path.isdir(os.path.join(RAIZ_REPO, ".git")):
    RAIZ_REPO = os.path.dirname(RAIZ_REPO)
FTE = os.path.join(AQUI, "fuentes")
GEN = os.path.join(AQUI, "generado")
LLUVIA = os.environ.get("CLIPS", os.path.expanduser("~/Downloads/Videos-Aem"))
PALMA_SRC = os.environ.get("PALMA_SRC", os.path.expanduser("~/Downloads/IMG_4842.MOV"))

F_VEL = 1.0   # la velocidad del plano en curso, para la validacion
_RUTA_EN_CURSO = ""   # y su archivo, para decidir el tmix
# La UNICA fuente que alterna luminancia entre cuadros consecutivos, medido.
PARPADEAN = {"SDO_20170910_131_AR12673X8_4k.webm"}
MAX_POR_FUENTE = 3
MIN_DUR = 8.0   # ningun plano puede durar menos, salvo los generados que son de 3 s
# CALIBRADO CONTRA EL VIDEO QUE VIO EL USER, y descontando el grano.
#
# Sobre el archivo final el iceberg que marco como "estatica" da 0,28 y el plano de 0:15
# que marco da 0,31. Pero esas cifras INCLUYEN el grano, que es ruido temporal y le suma
# diferencia entre cuadros a cualquier plano: medido, aporta 0,32 sobre material liso y
# 0,03 sobre material que ya se mueve. O sea que los dos planos que el user marco tienen
# movimiento real CERO: lo unico que se movia ahi era el grano.
#
# Esta medicion se hace SIN grano, asi que el piso va en 0,40: por encima del ruido de
# fondo y por debajo de lo que el user dio por bueno.
# 0,45 Y NO 0,60. El margen mas alto suena mejor y NO se puede pagar: medido, con 0,60 la
# categoria `cielo` se queda con 21 apariciones para 20 slots, y con ese filo las reglas de
# repeticion (una fuente por minuto, nunca dos seguidas) dejan al asignador sin nadie. A
# 0,45 el presupuesto de cielo salta a 30. Sigue habiendo 12% sobre lo que pide el examen.
MOV_MINIMO = 0.45

# CATEGORIAS RESERVADAS: se dejan para ULTIMO recurso cuando el acto no las pide.
#
# El user lo dijo cuando se armo la estructura: "los animales trata de guardarlo para
# cuando habla tipo 7:40 en adelante, no gastes la bala antes". Igual se gastaban: los
# actos que pedian agua o fuego se quedaban sin fuentes, caian al relleno "cualquier
# categoria" y se llevaban un bicho. Medido: medusa salia en 4:44 y sifonoforo en 5:20, y
# con eso los dos llegaban 3/3 al cierre, que es justo el acto que los necesita.
#
# PREFERENCIA Y NO PROHIBICION. Prohibirlos del todo se probo y hace inviable el plan:
# `descarga` tiene UNA fuente para 4 slots y `fuego` tres para 10, asi que esos actos
# SIEMPRE dependieron del relleno. Sin bichos disponibles el relleno se llevaba un cielo,
# y el cielo se agotaba (27 de 27 gastadas para las 9:42) dejando al acto 6 sin nada.
# El cuello real no es el presupuesto sino la VENTANA LIMPIA: las fuentes generadas
# tienen presupuesto de sobra pero ninguna llega a los 10 s, asi que el unico relleno
# posible es cielo. Dejandolos como ultimo recurso se guarda la bala igual, pero el plan
# cierra.
RESERVADAS = {"alien", "criatura"}

# Las fuentes cuya ventana declarada PISA a la medida (ver `ventanas_de`).
VENTANA_MANDA = {"abisal", "sol3", "medusa", "pelo"}

# MATERIAL OSCURO DE ORIGEN: prueba primero la curva LEVANTADA.
#
# La curva dura manda todo lo que entra por debajo del 38% al 5% de salida. Sobre un bicho
# del fondo del mar eso es pantalla negra, y el generador la probaba primero igual porque
# su validacion predictiva la daba por buena. Medido sobre el render real, el mismo
# encuadre de `sifon`:
#
#     curva dura     peor visible 30,1   peor movimiento 0,28   -> pantalla negra
#     curva alzada   peor visible 78,0   peor movimiento 1,53   -> pasa comodo
#
# Es la fuente la que decide el orden, no el azar de cual se probo primero.
OSCURAS = {"sifon", "abisal", "medusa"}

# ENCUADRES DESCARTADOS SOBRE EL RENDER, no sobre una prediccion.
#
# `validar_render.py` mide los planos que `montaje.sh` ya dejo en `.montaje/` y anota los
# que no sirven. Predecir la cadena no alcanzo: seis planos pasaron la validacion de este
# archivo y fallaron sobre el video, y la diferencia no la explican ni el `minterpolate`
# (1,00 -> 0,97) ni el blur (1,00 -> 0,75) ni el encode (1,44 contra 0,93 real).
#
# Asi que la prediccion sigue como PRIMER filtro (barata, descarta lo obvio) y la palabra
# final la tiene la medicion sobre el archivo. Lo que cae aca no se vuelve a elegir.
_EXCL = os.path.join(AQUI, "excluidos.txt")
EXCLUIDOS = set()
if os.path.exists(_EXCL):
    EXCLUIDOS = {l.strip() for l in open(_EXCL) if l.strip() and not l.startswith("#")}

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
# LOS RECORTES DEL MATERIAL SOLAR SON CERRADOS, y no es una decision estetica.
#
# Estaban entre 1800 y 4096 px de ancho, o sea que agarraban el disco entero. A esa escala
# el movimiento del plasma se PROMEDIA A CERO y el plano queda como una foto: medido, los
# discos daban 0,03 a 0,32, que es menos de lo que aporta el grano (0,32). Es la causa de
# fondo del "esta escena es estatica" del user, y no que el material no sirva.
#
# Con el recorte cerrado sobre una region activa el MISMO archivo da:
#
#     sol   800:450:2600:2500    0,22 -> 0,68
#     sol2  700:394:2400:2300    0,32 -> 1,08
#     sol3  700:394:1900:2300    0,06 -> 1,97   (y 4,14 en otro punto de la ventana)
#     fl1   800:450:2600:1100    0,12 -> 0,63
#     fl6   800:450:1200:2500    0,25 -> 0,83
#
# Los tres recortes de cada fuente apuntan a regiones distintas, asi que la regla de "un
# recorte distinto por aparicion" sigue dando encuadres que se leen como otra cosa.
src("sol",   f"{FTE}/SDO_20170910_131_AR12673X8_4k.webm", "cielo", 4.0, "sol",
    ["800:450:2600:2500", "1100:619:2600:1800", "900:506:1900:2300"], ventana=[2.4, 6.6])
src("sol2",  f"{FTE}/SDO_20170904_171_AR12673X_4kcomplete.webm", "cielo", 2.0, "sol",
    ["700:394:2400:2300", "900:506:1900:2300", "700:394:1900:2300"], ventana=[8, 290])
# RECORTES Y VENTANA MEDIDOS SOBRE EL RENDER (con el blur que le toca, sigma 3,5). El
# recorte 2100:1500 era el que la hacia fallar, y fuera del tramo 35-100 la visibilidad se
# cae a 38. Con esto da visibilidad 164 a 192 y movimiento 0,46 a 0,86.
src("sol3",  f"{FTE}/SDO_20170904_304_AR12673X_4k.webm", "cielo", 1.5, "sol",
    ["700:394:1900:2300", "700:394:2400:2300", "900:506:1900:2300"], ventana=[35, 100])
# fl5 LLEVA RECORTE PROPIO. El generico le caia en una zona muerta del cuadro y medía
# 0,23, o sea que el descarte previo la tiraba; con el recorte de abajo da 1,24. Es la
# misma leccion que con los discos: lo que estaba mal era adonde apuntaba el recorte, no
# el material.
RECORTE_PROPIO = {"fl5": ["600:337:2400:1600", "700:393:2400:1600", "900:506:2300:1500"],
                  "fl6": ["800:450:1200:2500", "1100:619:2600:1800", "800:450:1200:1100"],
                  # fl4: el generico le daba un encuadre que sobre el render quedaba quieto
                  "fl4": ["600:337:699:751", "820:461:655:727", "600:337:699:1691"]}
for k, f, w in (("fl1", "pd_flare_2022nov", 4.85), ("fl2", "pd_flare_2022abr", 4.57),
                ("fl3", "pd_flare_2024feb", 4.85), ("fl4", "pd_flare_may131", 4.55),
                ("fl5", "pd_flare_may171", 4.55), ("fl6", "pd_flare_may304", 4.55)):
    # TRES TAMAÑOS, no tres posiciones del mismo tamaño. Medido sobre `pd_flare_2022abr`,
    # el movimiento se sostiene hasta 2500 px de recorte (0,67) y a 1400 da 2,08: o sea
    # que en las fulguraciones el movimiento es de escala GRANDE y no hace falta cerrar.
    # Y el recorte grande escala 1,5x en vez de 5,5x, asi que no necesita ni modelo ni
    # blur. El asignador se queda con el que pase el piso; si el grande pasa, mejor
    # imagen gratis.
    src(k, f"{FTE}/{f}.webm", "cielo", 3.5, "sol",
        RECORTE_PROPIO.get(k, ["2000:1125:1600:800", "1400:788:2300:930",
                               "800:450:2600:1100"]), ventana=[0.2, w])

# --- lluvia y planeta. Los cuatro clips del user.
# LOS RECORTES DE r39 ERAN TAJADAS. Median 190 y 130 px de alto sobre un cuadro de 3840 y
# caian en zona oscura: sobre el render daban pantalla negra. Medidos con la cadena real,
# los de abajo dan visibilidad 187 y movimiento 14,9.
src("r39", f"{LLUVIA}/IMG_4739.MOV", "lluvia", 1.5, "campo",
    ["600:337:702:700", "600:337:312:700", "600:337:312:1576"], ventana=[0.1, 9.7])
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
# `pd_glm_rayos` SE VA DEFINITIVAMENTE. No es material de rayos: es una visualizacion
# de TRAFICO AEREO y el cuadro esta lleno de iconos vectoriales de aviones. Salieron al
# aire en 2:45, 4:56 y 5:32, y el user los marco: "son todos avioncitos chiquitos que
# carajo". Ademas la fuente tiene cortes internos adentro de las ventanas que
# `ventanas.py` dio por limpias, y esos cortes produjeron los tramos de 2,9 s de 5:05 y
# de 3,9 s de 5:35.
#
# Por que no lo agarro el detector: `ventanas.py` busca texto, lineas rectas largas y
# bloques quietos. Un icono de avion de 30 px que ademas se MUEVE no es ninguna de las
# tres cosas. Esta clase de defecto no la puede ver una heuristica de bordes, asi que la
# fuente se saca y no se intenta rescatar por ventanas.
#
# Con glm afuera, `descarga` se queda sin nadie (`pd_tormenta_argentina` no tiene ni una
# ventana limpia). Entran dos fuentes que estaban en la carpeta sin declarar:
#
#   gotas    cc0_gotas_ventana.webm   17,6 s limpios, agua sobre vidrio: es exactamente
#            el repiqueteo del acto 2, que es donde estaban los slots de descarga
#   rayoale  pd_rayos_alemania.ogv    5,4 s limpios. A 2,5x un plano de 12 s consume 4,8 s
#            y entra. Es la unica descarga real que queda
src("gotas", f"{FTE}/cc0_gotas_ventana.webm", "agua", 2.0, "agua",
    ["1000:563:140:80", "1120:630:60:40", "880:495:300:170"], ventana=[0.5, 17.7])
src("rayoale", f"{FTE}/pd_rayos_alemania.ogv", "descarga", 2.5, "cielo",
    ["700:394:34:100", "620:349:74:130", "560:315:104:150"], ventana=[13.0, 18.0])
# `pd_iceberg` tiene MAPA superpuesto con lineas punteadas blancas, que salio en 5:12.
# Se queda pero solo dentro de sus ventanas limpias medidas, no de punta a punta.
src("hielo", f"{FTE}/pd_iceberg.webm", "agua", 1.5, "campo",
    ["2200:1238:800:450", "1800:1013:1200:700", "1500:844:1600:900"], ventana=[23, 38])

# TRES FUENTES QUE ESTABAN EN LA CARPETA Y NADIE HABIA REGISTRADO.
#
# Buscando material para descomprimir el final apareció que `fuentes/` tenia 9 archivos
# que `planos.py` no declaraba: unos 350 s sin usar. De esos se descartaron a ojo dos que
# no servian: `cc0_gotas_ventana` no son gotas sino una CIUDAD de noche con luces y
# edificios reconocibles, y `pd_polvo_sahara` es un grafico satelital con fronteras
# dibujadas y texto en pantalla.
src("sol4", f"{FTE}/SDO_20170910_171_AR12673X8_4k.webm", "cielo", 1.5, "sol",
    ["600:337:1600:2800", "700:393:1600:2800", "600:337:2000:2800"])
src("sol5", f"{FTE}/SDO_20170910_304_AR12673X8_4k.webm", "cielo", 1.5, "sol",
    ["600:337:2000:1200", "600:337:2400:1600", "700:393:2400:1600"])

# --- fuego
src("lava1", f"{FTE}/usgs_lava_01.mp4", "fuego", 1.0, "arch",
    ["800:450:600:200", "620:350:880:330", "640:360:860:300"], ventana=[5.5, 20.5])
src("lava2", f"{FTE}/usgs_fuente_lava.mp4", "fuego", 1.0, "arch",
    ["500:280:1250:560", "560:315:1200:545", "480:270:1280:580"], ventana=[6.5, 65])
src("erup",  f"{FTE}/usgs_erupcion_2025.mp4", "fuego", 1.5, "arch",
    ["1100:619:420:230", "1000:563:460:260", "1200:675:380:280"], ventana=[55, 84])
# DERIVADO. `erup` tiene 200 s usables y la regla 2 la limita a 3 apariciones, o sea que
# quedaban ~165 s bloqueados por el tope. Esto es la region 120-190 (que `erup` no usa,
# su ventana es 55-84) con barril fuerte y rotacion: otra region MAS una distorsion, asi
# que no lee como repeticion. Se guarda como archivo para entrar como una fuente normal,
# sin tocar el pipeline. Se probaron 5 derivados y este fue el unico que paso: los otros
# salian casi negros, casi blancos, o con la costura del espejo a la vista.
src("magma", f"{FTE}/deriv_magma.mp4", "fuego", 1.0, "arch",
    ["1600:900:160:90", "1300:731:310:175", "1100:619:410:230"])

# --- criaturas
# EL PELO. Los recortes bajan de 340-700 px a 260-300: con 700 px de ancho en el segundo
# 40 se veia el lomo y el anca del animal contra el pasto. Un recorte fijo sobre un bicho
# que camina NO se queda abstracto, y hay que verificarlo en el punto de entrada real y
# no en el que se probo.
# La ventana es 42-55 s y no cualquiera: se midio la COMPACIDAD de la mancha oscura en
# 42 combinaciones de punto de entrada y recorte, y solo el tramo final del clip da pelo
# sin silueta reconocible. Antes de eso el animal camina y el lomo entra en cuadro.
src("pelo",   f"{FTE}/cc0_bison_yukon.webm", "criatura", 3.2, "pelo",
    # RECORTES DE 800 PX Y NO DE 300. Los de 300 escalaban 12,8x a 4K y a esa escala
    # cualquier movimiento del pelo lee como un salto: el examen los marcaba como corte
    # interno vuelta tras vuelta. Medido con la cadena real, con 800 px el ratio de corte
    # cae de 5,2 a 1,2 (el umbral es 4) y el movimiento queda en 4 a 5,9.
    ["800:450:800:280", "900:506:700:250", "700:394:900:300"], ventana=[42, 55])
# ARRANCA EN 14,5 Y NO ANTES. La fuente tiene un EMPALME cerca del segundo 13,8: se ve a
# ojo (tres cuadros de la misma toma y el cuarto es otra imagen), salio al aire en 9:05 y
# partio el plano en un tramo de 1,2 s. La deteccion automatica no lo agarra: con el grado
# puesto el cambio queda en 35 contra una mediana de 12, o sea debajo del umbral, porque
# el bicho se mueve mucho y le sube la mediana a su propio plano.
src("abisal", f"{FTE}/pd_bicho_abisal.webm", "criatura", 1.5, "arch",
    ["1200:675:360:200", "1000:563:500:280", "900:506:600:330"], ventana=[14.5, 24.7])
src("medusa", f"{FTE}/noaa_medusa_01.mp4", "alien", 2.0, "medusa",
    # recortes MEDIDOS sobre el render (visibilidad 59 a 155, movimiento 1,19 a 3,84)
    # ARRANCA EN 12. La ventana medida incluia [0,3 - 8,2] y ahi la fuente tiene un CORTE:
    # medido con la cadena real, el ratio en ss=2 da 6,3 a 9,8 (el umbral es 4), mientras
    # que de 12 en adelante queda en 2,6 a 3,4.
    ["380:214:900:560", "296:166:983:603", "500:281:800:500"], ventana=[12, 29])
# EL SIFONOFORO ES UN BICHO OSCURO SOBRE FONDO NEGRO y sus recortes caian en la parte
# vacia: sobre el render daban pantalla negra dos veces seguidas. Medidos, los de abajo
# dan visibilidad 67 y movimiento 1,92.
# `noaa_sifonoforo` SE SACA. Es un bicho oscuro del fondo del mar y no llega al piso de
# visibilidad de ninguna forma:
#
#   recorte cerrado   sirve sobre la fuente (67) pero a 600 px el factor es 6,4 y lo manda
#                     por el MODELO; despues del modelo y del encode el render mide 28
#   recorte grande    esquiva el modelo pero el bicho se diluye: 29, 25, 22 y 16 segun se
#                     abre el recorte
#
# Fallo seis vueltas seguidas del ciclo, siempre en el ultimo plano. `medusa` sola cubre
# los tres slots de `alien` con margen (medido sobre el render: visibilidad de 59 a 155 y
# movimiento de 1,19 a 3,84 en las tres duraciones que pide el arreglo), asi que la
# categoria no se queda sin nadie.
# LA VENTANA SE CIERRA SOBRE EL TRAMO BRILLANTE. Medido con el recorte y la curva que se
# usan, la visibilidad a lo largo del clip va 48, 44, 47, 112, 40, 46: el bicho entra en
# cuadro cerca del segundo 14. Con la ventana abierta de 10 a 22 el asignador caia en los
# tramos vacios y el plano arrancaba en negro, cuatro corridas seguidas.
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
     # LOS SLOTS DE `descarga` SE ABREN A AGUA Y LLUVIA. Con `glm` afuera queda una
     # sola fuente de descarga (`rayoale`, presupuesto 3) y el acto pedia tres: el
     # asignador se quedaba sin nadie en el minuto 5 y caia al relleno, que es
     # exactamente como se colaban bichos en pleno repiqueteo.
     [(12, ["lluvia"]), (12, ["descarga", "agua", "lluvia"]), (12, ["agua"]),
      (12, ["lluvia"]), (12, ["descarga", "agua", "lluvia"]), (12, ["agua"]),
      (12, ["lluvia"]), (12, ["descarga", "agua", "lluvia"])]),
    # la transicion. Todavia SIN criaturas: la bala se guarda para las voces.
    ("3 · antes de la voz",
     [(11, ["lluvia"]), (11, ["cielo"]), (11, ["generado"]), (11, ["cielo"]),
      (11, ["generado"]), (11, ["fuego"]), (10, ["cielo"])]),
    # UN plano de 13 s y no dos de 7 y 6.
    #
    # Eran los dos unicos planos del video por debajo de 8 s (el resto vive entre 9 y 12)
    # y encima iban PEGADOS y de la misma categoria. El user: "la de los cangrejos /
    # langostas, en un momento mostras dos o tres tomas seguidas y no respetas el tiempo
    # de cada escena". Las reglas 2, 3 y 4 no lo frenaban porque son fuentes distintas.
    #
    # Se juntan en uno solo en vez de estirar los dos a 9: 13 s es lo que dura el acto y
    # tiene que seguir durando lo mismo, porque hay siete cortes que caen sobre cambios
    # de enunciado del moog y correr el acto los corre a todos.
    ("4 · el alien", [(13, ["alien", "criatura"])]),
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
      # ULTIMO SLOT DEL ACTO 6: lista larga a proposito. Pedia solo agua o fuego y a esta
      # altura del video las dos estan agotadas, asi que caia en el relleno y se llevaba
      # un bicho JUSTO antes del cierre, que es el acto que pide bichos: quedaban medusa
      # y sifonoforo pegados en 10:27. Con alternativas reales el asignador tiene de
      # donde elegir y no toca la reserva.
      (12, ["fuego"]),
      (12, ["agua", "fuego", "lluvia", "cielo", "planeta", "descarga", "generado"])]),
                                                              # corte en 627
    # EL CIERRE YA NO SON TRES ALIEN SEGUIDOS.
    #
    # Pedia (16, 18, 12) todos de categoria "alien", y fuentes alien hay DOS: medusa y
    # sifonoforo. O sea que el cierre era medusa, sifonoforo, medusa: los mismos dos
    # bichos alternandose. El user lo marco asi: "la de los cangrejos / langostas, en un
    # momento mostras dos o tres tomas seguidas y no respetas el tiempo de cada escena".
    # No lee como tres escenas, lee como una sola picada en tres.
    #
    # Ahora van DOS alien con algo en el medio que corta. El plano del medio ofrece
    # varias categorias porque a esta altura del video casi todas las fuentes estan
    # gastadas o con la ventana limpia demasiado corta, y con una sola opcion el
    # asignador se queda sin nadie y aborta.
    #
    # El acto sigue durando 46 s, que es lo que tiene que durar: correrlo correria los
    # siete cortes que caen sobre los cambios de enunciado del moog.
    # LAS DURACIONES DE ESTE ACTO ESTAN ATADAS A LA REGLA 3 y no se tocan a la ligera.
    #
    # El acto arranca en 627 s (10:27) y hay DOS fuentes alien. Las dos van a salir en el
    # minuto 10, asi que el tercer plano TIENE que caer en el minuto 11 o la regla 3 deja
    # al asignador sin nadie. O sea: los dos primeros tienen que sumar 33 s o mas.
    #
    #     627 + 20 + 13 = 660 = 11:00  ->  minuto 11, entra
    #     627 + 18 + 10 = 655 = 10:55  ->  minuto 10, ABORTA (probado)
    #
    # El acto sigue durando 46 s en total, que es lo que no se puede mover: correrlo
    # correria los siete cortes que caen sobre los cambios de enunciado del moog.
    # LOS SLOTS DE `alien` ACEPTAN `criatura` COMO SALIDA. Con `sifon` afuera (ver la nota
    # en las fuentes) queda `medusa` sola, o sea 3 apariciones para 3 slots y cero margen:
    # cualquier encuadre que no pase hace abortar el plan entero. `criatura` (pelo, abisal)
    # tiene 6 para 3, asi que presta sin quedarse corta. Se sigue prefiriendo `alien`
    # porque va primero en la lista.
    ("7 · el cierre", [(20, ["alien", "criatura"]),
                       (13, ["descarga", "lluvia", "cielo", "generado", "agua", "fuego"]),
                       (13, ["alien", "criatura"])]),
]

NEGRO = 6


def ventanas_de(clave):
    """Las ventanas usables: lo medido POR lo declarado, de mayor a menor.

    `ventanas.json` dice donde la fuente esta limpia de texto, logos y cortes. El
    parametro `ventana=` de `src()` dice que PARTE de eso queremos usar, y es donde se
    anota lo que se aprende mirando (por ejemplo que el sifonoforo recien entra en cuadro
    cerca del segundo 14, y que antes el plano arranca en negro).

    Hasta ahora `ventana=` no hacia NADA: esta funcion leia solo el json y la descartaba,
    asi que cada declaracion escrita a mano en las fuentes era letra muerta. Se cruzan.
    """
    medidas = VENTANAS.get(os.path.basename(F[clave]["ruta"]), [])
    # SOLO MANDA LO DECLARADO EN LAS FUENTES DONDE SE MIDIO A PROPOSITO.
    #
    # Cuando se hizo que `ventana=` funcionara (antes era letra muerta), las declaraciones
    # VIEJAS empezaron a recortar material bueno: son anteriores a `ventanas.json` y mucho
    # mas conservadoras. Medido, `hielo` pasaba de 6 ventanas usables a 2, y con eso el
    # plan dejaba de cerrar (abortaba en 9:42 por falta de fuego).
    #
    # Asi que la declaracion solo pisa donde se aprendio algo concreto mirando:
    #   sifon    el bicho recien entra en cuadro cerca del segundo 14
    #   abisal   la fuente tiene un empalme en el 13,8 que hay que esquivar
    pedida = F[clave].get("ventana") if clave in VENTANA_MANDA else None
    pedida = pedida or []
    if pedida:
        a0, b0 = pedida[0], pedida[1]
        cruce = []
        for a, b in medidas:
            a2, b2 = max(a, a0), min(b, b0)
            if b2 - a2 > 0.5:
                cruce.append((a2, b2))
        medidas = cruce or medidas      # si el cruce queda vacio, manda lo medido
    return sorted(medidas, key=lambda w: w[1] - w[0], reverse=True)


def entra(clave, dur):
    """Si la ventana limpia de la fuente alcanza para un plano de `dur` segundos.

    Sin esto el asignador elegia fuentes imposibles: el clip solar corto tiene 4,2 s
    limpios y le tocaba un plano de 7 s, que a 1,5x consume 4,67. El montaje abortaba
    recien al renderizar, despues de hacer nueve planos al pepe.
    """
    if clave in DESCARTADAS:
        return False
    v = F[clave]
    consumo = dur * (1.0 / v["vel"] if v["vel"] else 16.0)
    # el plano ENTERO tiene que caber adentro de UNA ventana limpia, no repartido
    return any((b - a) >= consumo + 0.4 for a, b in ventanas_de(clave))


def elegir(cands, gastado, del_minuto, previa, dur, cat_previa=None, demanda=None,
           pedidas=None, cat_siguiente=None):
    """La fuente con mas presupuesto libre entre las que NO rompen ninguna regla.

    La regla 4 prohibe repetir la FUENTE anterior, pero no la CATEGORIA, y eso dejaba
    pasar dos bichos marinos seguidos: el user marco "en un momento mostras dos o tres
    tomas seguidas". medusa y sifonoforo son fuentes distintas pero leen como lo mismo.

    Es una regla BLANDA y no dura a proposito: hay actos enteros de una sola categoria
    (el acto 0 son siete planos de cielo) y una regla dura los haria imposibles. Se
    intenta primero sin repetir categoria y, si no queda nadie, se acepta repetirla.
    """
    def _libres(evitar_cat):
        return [c for c in cands
                if gastado[c] < MAX_POR_FUENTE     # regla 2
                and c not in del_minuto            # regla 3
                and c != previa                    # regla 4
                and not (evitar_cat and F[c]["cat"] == evitar_cat)
                and entra(c, dur)]                 # y que la ventana limpia alcance
    libres = _libres(cat_previa) or _libres(None)
    if not libres:
        return None

    # SE ELIGE POR HOLGURA, no por presupuesto bruto.
    #
    # Elegir "la fuente con mas presupuesto libre" parece justo y no lo es: `cielo` tiene
    # nueve fuentes (27 apariciones) contra una sola de `descarga` (3), asi que el relleno
    # se llevaba siempre un cielo. Y el cielo hace falta despues: hay actos que lo piden
    # de primera. Resultado medido: las 27 apariciones de cielo gastadas para las 9:42 y
    # el acto 6 abortando a las 9:53 por falta de cielo.
    #
    # La holgura es lo que le sobra a la categoria DESPUES de cubrir lo que todavia le
    # van a pedir. Una categoria muy pedida mas adelante deja de ser candidata comoda
    # aunque hoy tenga mucho presupuesto.
    def holgura(c):
        cat = F[c]["cat"]
        libre = sum(MAX_POR_FUENTE - gastado[k] for k, v in F.items() if v["cat"] == cat)
        return libre - (demanda or {}).get(cat, 0)

    def prioridad(c):
        cat = F[c]["cat"]
        # una reservada que este acto NO pidio va ultima: se usa solo si no hay otra
        ultimo = 0 if (cat in RESERVADAS and pedidas and cat not in pedidas) else 1
        # MIRA EL SLOT QUE VIENE. El relleno se llevaba un bicho justo antes del acto que
        # pide bichos, y quedaban dos pegados: medido, medusa cerrando el acto 6 y
        # sifonoforo abriendo el cierre a las 10:27. Evitar la categoria del proximo slot
        # cuesta nada aca y ahorra el par pegado alla.
        choca = 0 if (cat_siguiente and cat == cat_siguiente
                      and (not pedidas or cat not in pedidas)) else 1
        return (ultimo, choca, holgura(c), MAX_POR_FUENTE - gastado[c])

    return max(libres, key=prioridad)


def ranking(cands, gastado, del_minuto, previa, dur, cat_previa=None, demanda=None,
            pedidas=None, cat_siguiente=None):
    """Las fuentes elegibles ORDENADAS, no solo la primera.

    Antes esto devolvia una sola y, si ninguno de sus encuadres pasaba la revision, el
    generador emitia igual el "menos malo" (`mejor`). Asi entraron 24 planos negros o
    quietos de 61 sin que nada abortara. Con el ranking, si una fuente no da ningun
    encuadre sano se pasa a la siguiente, que es lo que habria que haber hecho siempre.
    """
    orden = []
    vistos = set()
    for evitar in (cat_previa, None):
        libres = [c for c in cands
                  if gastado[c] < MAX_POR_FUENTE and c not in del_minuto
                  and c != previa
                  and not (evitar and F[c]["cat"] == evitar)
                  and entra(c, dur) and c not in vistos]
        def holgura(c):
            cat = F[c]["cat"]
            libre = sum(MAX_POR_FUENTE - gastado[k] for k, v in F.items() if v["cat"] == cat)
            return libre - (demanda or {}).get(cat, 0)
        def prioridad(c):
            cat = F[c]["cat"]
            ultimo = 0 if (cat in RESERVADAS and pedidas and cat not in pedidas) else 1
            choca = 0 if (cat_siguiente and cat == cat_siguiente
                          and (not pedidas or cat not in pedidas)) else 1
            return (ultimo, choca, holgura(c), MAX_POR_FUENTE - gastado[c])
        for c in sorted(libres, key=prioridad, reverse=True):
            orden.append(c); vistos.add(c)
    return orden


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
    # EL tmix VA SOLO EN LA FUENTE QUE PARPADEA, no en todo el material solar.
    #
    # Se puso para matar un estrobo de 10 Hz y esta bien puesto, pero se le aplicaba al
    # tratamiento `sol` entero. Medido sobre las trece fuentes solares, la unica que
    # alterna de verdad es SDO_20170910_131 (movimiento crudo 12,57 y la prueba de
    # cuadros alternos da positiva); el resto mide entre 0,04 y 6,16 sin alternar.
    #
    # Y promediar ocho cuadros CUESTA movimiento: pd_flare_may131 cae de 6,16 a 1,30 y
    # pd_flare_2024feb de 2,10 a 0,46. O sea que el remedio de una fuente estaba dejando
    # quietas a las otras doce, que es justo lo que el user marco ("esta escena es
    # estatica, esta mal").
    if trat == "sol" and os.path.basename(_RUTA_EN_CURSO) in PARPADEAN:
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

    Devuelve (ok, luz, negro, mov, ss, recorte, curva_nom).
    """
    import numpy as np
    import subprocess
    ruta, ss, dur, recorte, variante, trat, curva, curva_nom, vel, es_pelo = args
    global F_VEL, _RUTA_EN_CURSO
    F_VEL = vel
    _RUTA_EN_CURSO = ruta
    def leer(vf, w, h, cuantos=8):
        o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta,
                            "-t", str(dur), "-vf", ",".join(vf) + f",fps={cuantos/max(dur,1):.3f}",
                            "-frames:v", str(cuantos), "-pix_fmt", "gray",
                            "-f", "rawvideo", "-"],
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
        return (False, 0.0, 1.0, 0.0, ss, recorte, curva_nom)
    # EL MOVIMIENTO SALE GRATIS de los cuadros que ya se leyeron. El user: "me parecio
    # ver una que no tiene animacion, como que es una foto y vas haciendo zoom de a
    # poco". Habia planos con movimiento medido en 0,10: eso es una imagen quieta. El
    # montaje ya lo medía pero solo AVISABA, y avisar no evita que salga al aire.
    mov = float(np.abs(np.diff(m, axis=0)).mean())
    try:
        import verificar
        ok = not verificar.revisar(m, es_pelo=es_pelo)
    except Exception:
        ok = True
    if not ok:
        return (False, 0.0, 1.0, mov, ss, recorte, curva_nom)

    # el brillo SI se mide sobre la cadena completa, que es lo que se va a ver
    # el `format=gray` del final no es redundante: ver la nota en `denso`
    g = leer(cadena(recorte, variante, trat, curva_nom, curva)
             + ["format=gray", "scale=96:54"], 96, 54, 6)
    if g is None:
        return (False, 0.0, 1.0, mov, ss, recorte, curva_nom)
    return (True, float(g.mean()), float((g < 18).mean()), mov, ss, recorte, curva_nom)


# LA REVISION DENSA. Los umbrales de abajo se miden a lo largo del plano y NO sobre su
# promedio, que es lo que dejo pasar todos los defectos que el user marco en el 4K:
#
#   6:08  cinco segundos y medio de pantalla NEGRA pura dentro de un plano cuyo promedio
#         daba luz 88, porque el resto del plano era brillante
#   5:47  el iceberg se va a negro SOLO en el medio del plano y vuelve: el ojo lo lee
#         como un fundido, y lo que vuelve dura 3 s
#   6:13  un salto de luminancia de 1 a 204 en un cuadro (fogonazo)
#   6:17  ocho cambios de imagen en 0,8 s (parpadeo)
#   4:12  movimiento 0,28 sobre el archivo final, o sea una foto, medido 4,5 de media
#
# Con 8 cuadros repartidos en 12 segundos nada de esto se ve: hay que mirar seguido.
VENTANA_S = 2.0      # el tramo mas corto que el ojo lee como "una escena"
FPS_DENSO = 4.0      # cuadros por segundo de la revision
SALTO_MAXIMO = 55.0  # diferencia de luz entre cuadros vecinos: arriba de esto es corte
PARPADEO_MAX = 3     # saltos alternados dentro de un segundo
# LOS UMBRALES DE LA VALIDACION LLEVAN MARGEN sobre los del examen, a proposito.
#
# La prediccion es OPTIMISTA: no ve el blur que mete `mejorar.py` (medido, 0,85 -> 0,35 en
# un plano solar), ni el encode, ni la sustitucion por el intermedio del modelo. El
# resultado era que el generador aceptaba planos justo en la linea y el render los empujaba
# justo abajo: de las tres fallas de la vuelta 8, dos estaban a menos del 15% del umbral
# (movimiento 0,35 contra 0,40 y visible 26 contra 30).
#
# Se probo cerrar la brecha rindiendo la candidata de verdad y no alcanza, porque los
# planos que van por el modelo usan un intermedio que en tiempo de planificacion todavia no
# existe. Asi que en vez de predecir mejor, se pide de mas: el examen exige visible 30 y
# movimiento 0,40, y aca se exige 45 y 0,60.
VISIBLE_MINIMO = 40.0  # el examen pide 30: 33% de margen


def denso(ruta, ss, dur, recorte, variante, trat, curva, curva_nom, vel):
    """Revisa el plano YA GRADADO a lo largo del tiempo. None si esta bien, o el motivo.

    Devuelve el primer defecto encontrado, con el segundo dentro del plano en el que
    aparece, para que el mensaje sirva sin tener que ir a mirar el video.
    """
    import numpy as np
    import subprocess
    w, h = 96, 54
    n = max(8, int(dur * FPS_DENSO))
    # SE MIDE EN TIEMPO DE SALIDA. `cadena` ya arranca con `setpts` (toma F_VEL), y `-t`
    # va del lado de la salida, asi que los cuadros que se leen son los que va a ver el
    # ojo: un plano ralentizado 2x se mueve la mitad por segundo, y medirlo en tiempo de
    # fuente lo daba por vivo cuando en pantalla esta casi quieto.
    #
    # Y LA SALIDA SE FUERZA A GRIS. `cadena` pone `format=gray` en el medio, pero
    # `normalize` solo existe en RGB, asi que ffmpeg vuelve a convertir y entrega 3 bytes
    # por pixel. Las lecturas anteriores dividian por 1 y promediaban Y, U y V juntas:
    # como en material gris U=V=128, un cuadro NEGRO medía ~85 de luz en vez de 0. De ahi
    # que el filtro de pantalla negra no disparara nunca.
    global F_VEL, _RUTA_EN_CURSO
    F_VEL = vel
    _RUTA_EN_CURSO = ruta
    vf = cadena(recorte, variante, trat, curva_nom, curva) + ["format=gray", f"scale={w}:{h}"]
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", ruta,
                        "-t", str(dur),
                        "-vf", ",".join(vf) + f",fps={FPS_DENSO}",
                        "-frames:v", str(n), "-pix_fmt", "gray",
                        "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    k = len(o) // (w * h)
    if k < 6:
        return "no se pudo medir"
    a = np.frombuffer(o[:k * w * h], dtype=np.uint8).reshape(k, -1).astype(np.float32)
    luz = a.mean(axis=1)
    dif = np.abs(np.diff(a, axis=0)).mean(axis=1)
    paso = max(2, int(VENTANA_S * FPS_DENSO))
    seg = lambda i: f"{i / FPS_DENSO:.1f}s"

    # 1. ningun tramo de 2 s puede quedar en PANTALLA NEGRA.
    #
    # No se mide por luz media: este video es dark ambient y hay planos legitimos con
    # media 4,9 que son un campo negro con filamentos de plasma BRILLANTES encima (pico
    # 223). Medir la media los reprobaba a todos y dejaba al acto 0, que son siete planos
    # de material solar seguidos, sin una sola fuente elegible.
    #
    # Lo que distingue una pantalla negra de un plano oscuro es si hay ALGO visible. Se
    # mira el percentil 99,5 del cuadro: en el negro de 6:08 da 3, y en cualquier plano
    # oscuro pero con contenido da 115 o mas.
    vis = np.percentile(a, 99.5, axis=1)
    for i in range(0, k - paso + 1):
        if vis[i:i + paso].max() < VISIBLE_MINIMO:
            return f"pantalla negra de {VENTANA_S:.0f}s en {seg(i)} (nada por encima de {vis[i:i+paso].max():.0f})"
    # 2. ni quedarse quieto: una foto con deriva no es una toma
    for i in range(0, k - paso):
        if dif[i:i + paso].mean() < MOV_MINIMO:
            return f"quieto en {seg(i)} (movimiento {dif[i:i+paso].mean():.2f})"
    # 3. ni saltar: eso es un corte interno de la fuente o un fogonazo
    salto = np.abs(np.diff(luz))
    if salto.max() > SALTO_MAXIMO:
        i = int(salto.argmax())
        return f"salto de luz en {seg(i)} ({luz[i]:.0f} -> {luz[i+1]:.0f})"
    # 4. ni cambiar de contenido de golpe en el medio: un corte interno de la fuente no
    #    siempre mueve la luz (dos tomas pueden tener el mismo brillo), pero SIEMPRE es
    #    un cuadro que no se parece a su vecino mientras el resto del plano si. Se mide
    #    contra la mediana del propio plano, que es lo que lo distingue de una toma
    #    movida de punta a punta. Es el defecto de 7:14, que el user leyo como "una
    #    escena de 1 o 2 segundos".
    med = float(np.median(dif))
    if dif.max() > max(25.0, 6.0 * med):
        i = int(dif.argmax())
        return f"corte interno en {seg(i)} (cambio {dif.max():.0f} contra {med:.0f} de mediana)"
    # 5. ni parpadear: saltos chicos que van y vuelven varias veces en un segundo
    ventana = int(FPS_DENSO)
    d = np.diff(luz)
    for i in range(len(d) - ventana):
        tramo = d[i:i + ventana]
        fuertes = np.abs(tramo) > 18
        cambios = int(np.sum(np.diff(np.sign(tramo[fuertes])) != 0)) if fuertes.sum() > 1 else 0
        if cambios >= PARPADEO_MAX:
            return f"parpadeo en {seg(i)} ({cambios} cambios en 1s)"
    return None


def brillo(ruta, ss, dur, recorte, variante, curva, trat="arch", curva_nom="duro"):
    """Luminancia media y fraccion casi negra del plano ya gradado."""
    import numpy as np
    import subprocess
    vf = cadena(recorte, variante, trat, curva_nom, curva) + ["format=gray", "scale=96:54"]
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


# DESCARTE PREVIO POR MOVIMIENTO. Se mide UNA vez por fuente, al arrancar.
#
# Sin esto la generacion del plan no terminaba nunca: para cada slot el asignador recorria
# las 28 fuentes en orden y le quemaba unas 36 llamadas a ffmpeg a cada una antes de pasar
# a la siguiente. Medido, 3 planos en una hora, o sea 20 horas para el video.
#
# Y la mayor parte de ese trabajo era tirado: los discos completos del SDO son placas
# QUIETAS (movimiento crudo de 0,04 a 0,06) y ninguna velocidad los rescata; acelerados 8x
# llegan a 0,45, debajo del piso. Se los medía de nuevo en cada uno de los 61 slots para
# llegar siempre a la misma conclusion.
#
# Aca se mide cada fuente en dos puntos de su primera ventana limpia, con su velocidad y
# su tratamiento reales, y la que no llega al piso queda afuera del todo.
_MOV_FUENTE = {}


def _mov_una(args):
    """Movimiento del plano ya gradado para UN encuadre. Sin grano: el grano es ruido
    temporal y le suma diferencia entre cuadros a todos por igual, o sea que taparia
    justo lo que se quiere medir."""
    import numpy as np
    import subprocess
    global F_VEL, _RUTA_EN_CURSO
    ruta, ss, dur, recorte, trat, vel, curva = args
    F_VEL = vel
    _RUTA_EN_CURSO = ruta
    vf = cadena(recorte, "", trat, "duro", curva) + ["format=gray", "scale=96:54"]
    o = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.2f}", "-i", ruta,
                        "-t", f"{dur:.2f}", "-vf", ",".join(vf) + ",fps=4",
                        "-frames:v", str(int(dur * 4)), "-pix_fmt", "gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(o) // (96 * 54)
    if n < 3:
        return 0.0
    m = np.frombuffer(o[:n*96*54], dtype=np.uint8).reshape(n, -1).astype(float)
    return float(np.abs(np.diff(m, axis=0)).mean())


def prescreen(verbose=True):
    """Mide el movimiento de cada fuente y saca de circulacion a las que no llegan.

    BARRE TODAS LAS VENTANAS Y TODOS LOS RECORTES, no uno. La primera version miraba un
    solo encuadre de la primera ventana y condenaba fuentes que sirven: `hielo` daba 0,02
    ahi y en el video renderizado dos de sus planos miden 2,94 y 3,79, porque tiene seis
    ventanas limpias y en otras hay movimiento de sobra. Lo que decide es si la fuente
    tiene ALGUN encuadre que se mueva, no si el primero que toco se movia.
    """
    fuera = []
    trabajos, indice = [], []
    for k in sorted(F):
        v = F[k]
        for (a, b) in ventanas_de(k)[:4]:
            largo = (b - a) * (v["vel"] or 1.0)
            dur = min(9.0, max(3.0, largo * 0.8))
            if dur / (v["vel"] or 1.0) > (b - a):
                continue
            for recorte in v["recortes"]:
                for frac in (0.15, 0.7):
                    ss = a + max(0.0, (b - a) - dur / (v["vel"] or 1.0)) * frac
                    trabajos.append((v["ruta"], ss, dur, recorte, v["trat"], v["vel"],
                                     CURVA_SUAVE if v["trat"] == "arch" else CURVA_DURO))
                    indice.append(k)
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        vals = list(pool.map(_mov_una, trabajos))
    for k, m in zip(indice, vals):
        _MOV_FUENTE[k] = max(_MOV_FUENTE.get(k, 0.0), m)
    # EL DESCARTE ES MAS PERMISIVO QUE EL FILTRO POR PLANO, a proposito. Esto es una
    # optimizacion para no perder minutos midiendo fuentes sin esperanza, no la autoridad:
    # quien decide sigue siendo `denso`, encuadre por encuadre, con el piso exacto. Una
    # fuente que en el muestreo grueso roza el piso puede tener un encuadre bueno.
    for k in sorted(F):
        if _MOV_FUENTE.get(k, 0.0) < MOV_MINIMO * 0.8:
            fuera.append((k, f"su mejor encuadre mueve {_MOV_FUENTE.get(k, 0.0):.2f}"
                             if k in _MOV_FUENTE else "sin ventana limpia"))
    if verbose:
        print(f"# descarte previo: {len(F) - len(fuera)} fuentes usables de {len(F)}, "
              f"{len(trabajos)} encuadres medidos", file=sys.stderr)
        for k, por in fuera:
            print(f"#     FUERA  {k:8} {F[k]['cat']:10} {por}", file=sys.stderr)
    return {k for k, _ in fuera}


DESCARTADAS = set()


def _revisar_actos():
    """La tabla de actos tiene que respetar MIN_DUR. Antes no se verificaba y habia dos
    slots de 7 y 6 s conviviendo con un MIN_DUR de 7."""
    cortos = [(a, d) for a, slots in ACTOS for d, _ in slots if d < MIN_DUR]
    if cortos:
        sys.exit("ABORTA: hay slots por debajo de MIN_DUR=%s: %s" % (MIN_DUR, cortos))


def _reanudar(ruta):
    """Rehace el estado del asignador a partir de un plan a medio escribir.

    Cada plano cuesta varias llamadas a ffmpeg y la corrida entera pasa los 20 minutos.
    Se corto tres veces. Con esto la cuarta arranca donde quedo la tercera en vez de
    volver a empezar, y el resultado es EL MISMO que si hubiera corrido de una: el
    asignador es determinista y su estado son cuatro cosas, todas deducibles del plan
    parcial.
    """
    if not ruta or not os.path.exists(ruta):
        return [], collections.Counter(), None, None, float(NEGRO)
    hechas = [l.rstrip("\n") for l in open(ruta) if l.strip() and not l.startswith("#")]
    gastado = collections.Counter()
    t = float(NEGRO)
    previa = cat_previa = None
    for l in hechas:
        c = l.split("|")
        gastado[c[0]] += 1
        t += float(c[3])
        previa = c[0]
        cat_previa = F[c[0]]["cat"] if c[0] in F else None
    return hechas, gastado, previa, cat_previa, t


def main():
    _revisar_actos()
    global DESCARTADAS
    DESCARTADAS = prescreen()
    seguir = None
    if "--continuar" in sys.argv:
        seguir = sys.argv[sys.argv.index("--continuar") + 1]
    lineas, gastado, previa, cat_previa, t = _reanudar(seguir)
    ya = len(lineas)
    if ya:
        print(f"# reanudando: {ya} planos ya decididos, van {t:.0f}s",
              file=sys.stderr, flush=True)
        for l in lineas:
            print(l, flush=True)
    minuto_actual = int(t // 60)
    # las fuentes ya usadas EN EL MINUTO EN CURSO, que es lo que mira la regla 3
    del_minuto = set()
    tt = float(NEGRO)
    for l in lineas:
        c = l.split("|")
        if int(tt // 60) == minuto_actual:
            del_minuto.add(c[0])
        tt += float(c[3])
    mapa = []
    saltear = ya
    # la lista plana de slots, para poder mirar lo que TODAVIA falta asignar
    planos_todos = [(a, d, cs) for a, sl in ACTOS for d, cs in sl]
    idx = -1

    for acto, slots in ACTOS:
        for dur, cats in slots:
            idx += 1
            if saltear > 0:                 # ya decidido en la corrida anterior
                saltear -= 1
                continue
            # cuantas veces se va a pedir cada categoria de aca en adelante
            demanda = collections.Counter(cs[0] for _, _, cs in planos_todos[idx + 1:])
            cat_siguiente = (planos_todos[idx + 1][2][0]
                             if idx + 1 < len(planos_todos) else None)
            m = int(t // 60)
            if m != minuto_actual:
                minuto_actual, del_minuto = m, set()
            cands = [k for k, v in F.items() if v["cat"] in cats]
            orden = ranking(cands, gastado, del_minuto, previa, dur, cat_previa, demanda,
                            cat_siguiente=cat_siguiente)
            # el relleno (cualquier categoria) va DESPUES de las pedidas, no en lugar de
            for k in ranking(list(F), gastado, del_minuto, previa, dur, cat_previa,
                             demanda, pedidas=cats, cat_siguiente=cat_siguiente):
                if k not in orden:
                    orden.append(k)
            if not orden:
                det = []
                for k in sorted(F):
                    r = []
                    if gastado[k] >= MAX_POR_FUENTE: r.append(f"gastada {gastado[k]}/3")
                    if k in del_minuto: r.append("ya salio este minuto")
                    if k == previa: r.append("es la anterior")
                    if not entra(k, dur): r.append("la ventana no alcanza")
                    det.append(f"      {k:8} {F[k]['cat']:10} " + (", ".join(r) if r else "LIBRE"))
                sys.exit(f"ABORTA: no queda fuente elegible para el plano de {dur}s en "
                         f"{int(t)//60}:{int(t)%60:02d}, acto {acto}, "
                         f"categorias {cats}\n" + "\n".join(det))

            # SE PRUEBAN LAS FUENTES EN ORDEN hasta que una entregue un encuadre SANO.
            #
            # Antes se elegia una sola fuente y, si ninguno de sus encuadres pasaba, se
            # emitia igual el "menos malo". De ahi salieron los 24 planos negros o
            # quietos. Ahora un encuadre que no pasa la revision densa simplemente no se
            # usa, y si la fuente entera no tiene ninguno bueno se pasa a la que sigue.
            elegida = elegido = None
            curva_eleg = "duro"
            motivos = []
            global F_VEL
            # SE PRUEBAN HASTA 8 FUENTES POR SLOT. Recorrer las 28 cuesta unos 14 minutos
            # y, si las ocho mejores del ranking no dan un encuadre sano, el problema es el
            # material y no la busqueda: mejor abortar y decirlo que seguir raspando.
            for cand in orden[:8]:
                v = F[cand]
                n = gastado[cand]
                F_VEL = v["vel"]
                consumo = dur * (1.0 / v["vel"] if v["vel"] else 16.0)
                cabe = [w for w in ventanas_de(cand) if (w[1] - w[0]) >= consumo + 0.4]
                candidatas = []
                for (a, b) in cabe:
                    hueco = (b - a) - consumo - 0.2
                    for frac in (((n * 0.37) % 1.0), 0.0, 0.55, 0.9, 0.25, 0.75):
                        for ir in range(len(v["recortes"])):
                            cs = a + 0.2 + hueco * frac
                            cr = v["recortes"][(n + ir) % len(v["recortes"])]
                            if f"{cand}|{cs:.2f}|{cr}" in EXCLUIDOS:
                                continue        # ya se renderizo y no sirvio
                            candidatas.append((cs, cr))
                variante = VARIANTES[(sello(cand) + n * 3) % len(VARIANTES)]
                base = CURVA_SUAVE if v["trat"] == "arch" else CURVA_DURO
                # SE EVALUA DE A TANDAS Y SE FRENA EN LA PRIMERA SANA.
                #
                # Calcular las 36 candidatas de cada fuente antes de mirar ninguna era
                # inviable: el primer plano del video se comia minutos sin emitir nada,
                # porque con el ranking se prueban varias fuentes por slot. Ahora la
                # revision barata corre de a 6 y, apenas una pasa, se le corre la densa:
                # si esa sirve, no se calcula ni una candidata mas.
                orden_curvas = (("alzada", CURVA_ALZADA), ("duro", base)) if cand in OSCURAS \
                    else (("duro", base), ("alzada", CURVA_ALZADA))
                for curva_nom, curva in orden_curvas:
                    for i0 in range(0, len(candidatas), 6):
                        tanda = candidatas[i0:i0 + 6]
                        trabajos = [(v["ruta"], round(cs, 2), dur, cr, variante, v["trat"],
                                     curva, curva_nom, v["vel"], v["trat"] == "pelo")
                                    for cs, cr in tanda]
                        with cf.ThreadPoolExecutor(max_workers=6) as pool:
                            salidas = list(pool.map(analizar, trabajos))
                        for ok, luz, negro, mov, cs, cr, cn in salidas:
                            # EL FILTRO BARATO YA NO DECIDE SOBRE EL NEGRO. Miraba la luz
                            # MEDIA y con eso descartaba el material solar entero antes de
                            # llegar a la revision buena: un campo negro con filamentos de
                            # plasma brillantes mide 4,9 de media y es un plano perfecto.
                            # Quien decide es `denso`, que mira si hay algo visible.
                            if not (ok and mov >= MOV_MINIMO * 0.7):
                                continue
                            falla = denso(v["ruta"], cs, dur, cr, variante, v["trat"],
                                          curva, cn, v["vel"])
                            if falla is None:
                                elegido = (cs, cr); curva_eleg = cn; elegida = cand
                                break
                            motivos.append(f"{cand} {cr} {cn}: {falla}")
                        if elegido:
                            break
                    if elegido:
                        break
                if elegido:
                    break
            if elegido is None:
                sys.exit(f"ABORTA: ninguna fuente entrega un plano sano de {dur}s en "
                         f"{int(t)//60}:{int(t)%60:02d} (acto {acto}, {cats}).\n"
                         "      probadas: " + ", ".join(orden) + "\n      "
                         + "\n      ".join(motivos[:12]))
            v = F[elegida]
            n = gastado[elegida]
            gastado[elegida] += 1
            del_minuto.add(elegida)
            previa = elegida
            cat_previa = v["cat"]
            variante = VARIANTES[(sello(elegida) + n * 3) % len(VARIANTES)]
            ss, recorte_eleg = elegido
            # la ruta va RELATIVA a la raiz: el plan se congela y se reusa, y con rutas
            # absolutas deja de servir apenas se mueve una carpeta. Paso exactamente eso
            # al reorganizar TX02: el plan del 1080 apuntaba a la ubicacion vieja.
            ruta_rel = os.path.relpath(v["ruta"], RAIZ_REPO)
            linea = "|".join([elegida, ruta_rel, f"{ss:.2f}", str(dur),
                              recorte_eleg, variante,
                              v["trat"], f"{v['vel']:.4f}", curva_eleg])
            lineas.append(linea)
            # SE ESCRIBE A MEDIDA, no al final. Cada plano cuesta varias llamadas a
            # ffmpeg y la corrida entera pasa los 20 minutos; la mataron dos veces y las
            # dos se perdio todo porque el volcado iba recien al terminar. Asi al menos
            # queda por donde iba.
            print(linea, flush=True)
            print(f"# {len(lineas):>3} {int(t)//60}:{int(t)%60:02d} {elegida}",
                  file=sys.stderr, flush=True)
            mapa.append((int(t), elegida, dur, acto))
            t += dur

    total = t
    print(f"# {len(lineas)} planos · {total:.0f}s de video · {len(gastado)} fuentes",
          file=sys.stderr)
    peor = gastado.most_common(1)[0]
    print(f"# la fuente mas usada: {peor[0]} con {peor[1]} apariciones (el maximo es "
          f"{MAX_POR_FUENTE})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
