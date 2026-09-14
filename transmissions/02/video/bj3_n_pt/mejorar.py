"""Reconstruye con Real-ESRGAN los planos cuya fuente esta aplastada en bloques.

POR QUE UN MODELO Y NO UN FILTRO. `nitidez.py` mide que 41 de los 62 planos vienen de
fuentes donde la compresion dejo mesetas planas de 8x8 en las zonas de bajo contraste.
El grado del video estira esa zona ~4,4 veces y las mesetas salen a la superficie; el
escalado a 4K las agranda y quedan cuadrados. Se probaron deblock, hqdn3d, smartblur y
gblur: ninguno recupera nada, porque debajo de la meseta NO HAY informacion. Un filtro
lineal solo puede promediar lo que ya esta. Lo unico que puede poner detalle donde no lo
hay es un modelo entrenado para eso.

DONDE SE APLICA. Solo donde el defecto se ve: fuente cuadriculada Y ampliada 2x o mas.
Los planos de fulguracion se recortan a 3400 px y se amplian 1,1x, asi que aunque la
fuente este igual de aplastada el bloque nunca crece: esos van con un blur barato.
Los 21 planos de fuente sana no se tocan.

DONDE SE UBICA EN LA CADENA. Antes del grado y ANTES de la camara lenta.

  - Antes del grado porque el modelo esta entrenado sobre imagen natural. Si primero se
    estira el contraste 4,4x, el modelo lee los escalones de bloque como bordes reales
    y los AFILA en vez de disolverlos.
  - Antes de la camara lenta porque `setpts` estira 1 cuadro de fuente en varios de
    salida. Procesar la salida es pagar el mismo cuadro varias veces: son 14160 cuadros
    contra 3996 unicos, o sea 12,6 h de GPU contra 3.

QUE DEJA. Un intermedio por plano en `.ia/`, que es el recorte ya reconstruido y nada
mas: sin grado, sin variante, sin ralentizar, a los fps de la fuente. Asi el montaje lo
consume igual que consumiria la fuente original y NO cambia ni un corte ni un encuadre:
el plan de planos queda intacto y las cuatro reglas de repeticion siguen valiendo tal
cual. Del mismo intermedio salen el 4K y el 1080 sin volver a pagar GPU.

    python3.10 mejorar.py out/bj3_n_pt_4k.plan.txt          # el pase completo
    python3.10 mejorar.py out/bj3_n_pt_4k.plan.txt --listar  # solo dice que haria
"""

import glob
import os
import subprocess
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos"))
from rrdb import cargar  # noqa: E402

import nitidez  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
# LA RAIZ SE BUSCA, NO SE CUENTA EN NIVELES: contarlos ya rompio al mover carpetas.
RAIZ = AQUI
while RAIZ != "/" and not os.path.isdir(os.path.join(RAIZ, ".git")):
    RAIZ = os.path.dirname(RAIZ)
SALIDA = os.path.join(AQUI, ".ia")
ANCHO_FINAL = 3840

# EL MODELO SOLO CUANDO AMPLIA 3,5x O MAS, o sea solo el x4.
#
# Con 2.0 entraban tambien los planos de 2x a 3,5x, que van por el modelo x2, y ESE
# EMPEORA. El x2 no tiene un upsampler mas corto: comprime la entrada con
# pixel_unshuffle(2), y a poca ampliacion se comporta como afilador en vez de
# reconstructor. Toma el borde del bloque de la fuente por estructura real y lo endurece,
# y de paso inventa chorreados en los bordes del cuadro. El resultado lee como MP4
# corrupto, no como falla de transmision.
#
# Se vio en el plano 58 (`sol2` en 10:15) y en el plano 1, que abre el video. Los dos son
# x2. Los diez planos que caian en esa franja pasan a blur, que sobre el mismo material
# da textura organica sin mosaico.
#
# Se intento detectarlo automaticamente y NO se pudo: cuatro metricas (meseta, salto en
# la rejilla, pico espectral, bordes alineados a los ejes) fallan todas, porque el defecto
# es exceso de FILO y no exceso de planitud. Lo que si discrimina perfecto es la escala
# del modelo, asi que la regla es esa.
FACTOR_MIN = 3.5
BALDOSA = 768        # los recortes grandes se procesan por partes o la GPU no entra
SOLAPE = 24          # las partes se pisan y se mezclan: sin esto se ve la costura
# Debajo de esto el recorte entra entero y baldosear solo cuesta: el solape se procesa
# dos veces. Partir un 540x302 en dos baldosas de 320 hacia el pase 1,8x mas lento.
SIN_PARTIR = 900_000


def _pesos(escala):
    return glob.glob("/Users/emilianomettini/.cache/huggingface/hub/"
                     f"models--ai-forever--Real-ESRGAN/snapshots/*/RealESRGAN_x{escala}.pth")[0]


def _fps(ruta):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=r_frame_rate", "-of", "default=nw=1:nk=1", ruta],
                       capture_output=True, text=True).stdout.strip().split()[0].rstrip(",")
    n, d = o.split("/")
    return float(n) / float(d)


def _tam_real(fuente, recorte):
    """El tamaño que ffmpeg ENTREGA de verdad para ese recorte, que no es el que se pide.

    Las fuentes son yuv420p: el croma va de a dos pixeles, asi que `crop` REDONDEA los
    lados impares para abajo, en silencio. Seis recortes del plan tienen el alto impar y
    ffmpeg devolvia una fila menos de la pedida.

    Leyendo del pipe la cantidad de bytes de la fila de mas, cada cuadro se corria una
    fila respecto del anterior y el corrimiento se acumulaba: en el video se veia una
    linea que cruzaba y volvia a entrar la misma toma, derivando. Con `transpose` la
    deriva sale de costado en vez de vertical.

    Preguntar por el tamaño en vez de asumirlo es la unica forma de que esto no vuelva:
    la comprobacion contra las dimensiones DECLARADAS del intermedio no sirve, porque
    esas las escribi yo.
    """
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0",
                        "-f", "lavfi", f"movie='{fuente}',crop={recorte}"],
                       capture_output=True, text=True).stdout.strip()
    w, h = (int(v) for v in o.split(","))
    return w, h


def _pasar(red, t, escala):
    """Corre la red sobre un tensor, tolerando lados impares.

    El modelo x2 no tiene un upsampler mas corto: comprime la entrada con
    pixel_unshuffle(2), que EXIGE lados pares. Los recortes del video no lo son (hay uno
    de 1900x1069) y las baldosas del borde menos todavia. Se rellena replicando el borde,
    se pasa, y se recorta la salida al tamaño exacto que corresponde.
    """
    h, w = t.shape[-2:]
    py, px = h % 2, w % 2
    if escala == 2 and (py or px):
        t = torch.nn.functional.pad(t, (0, px, 0, py), mode="replicate")
    y = red(t).clamp(0, 1)
    return y[..., :h * escala, :w * escala]


@torch.no_grad()
def ampliar(red, img, escala, disp):
    """img float32 HxWx3 en 0..1 -> HxWx3 ampliado. Va por baldosas con solape."""
    alto, ancho, _ = img.shape
    if alto * ancho <= SIN_PARTIR:
        t = torch.from_numpy(img).permute(2, 0, 1)[None].to(disp)
        if disp == "mps":
            t = t.half()
        y = _pasar(red, t, escala)[0].permute(1, 2, 0)
        return (y * 65535.0).round().to(torch.uint16).cpu().numpy()
    out = np.zeros((alto * escala, ancho * escala, 3), np.float32)
    peso = np.zeros((alto * escala, ancho * escala, 1), np.float32)
    for y0 in range(0, alto, BALDOSA):
        for x0 in range(0, ancho, BALDOSA):
            # se toma la baldosa con un borde extra para que el modelo tenga contexto
            ya, yb = max(0, y0 - SOLAPE), min(alto, y0 + BALDOSA + SOLAPE)
            xa, xb = max(0, x0 - SOLAPE), min(ancho, x0 + BALDOSA + SOLAPE)
            t = torch.from_numpy(img[ya:yb, xa:xb]).permute(2, 0, 1)[None].to(disp)
            if disp == "mps":
                t = t.half()
            r = _pasar(red, t, escala)[0].permute(1, 2, 0).float().cpu().numpy()
            out[ya * escala:yb * escala, xa * escala:xb * escala] += r
            peso[ya * escala:yb * escala, xa * escala:xb * escala] += 1.0
    return out / np.maximum(peso, 1e-6)


def planificar(plan):
    """Cruza el plan con la medicion y reparte cada plano en modelo / blur / nada."""
    filas = [l.rstrip("\n").split("|") for l in open(plan) if l.strip()]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        med = list(ex.map(nitidez.medir, ["|".join(f) + "\n" for f in filas]))
    modelo, blur = [], []
    for i, (f, m) in enumerate(zip(filas, med), start=1):
        if m is None:
            continue
        nombre, _, ancho, coc, sigma = m
        if sigma <= 0:
            continue
        factor = ANCHO_FINAL / ancho
        # EL MATERIAL SOLAR VUELVE A PASAR POR EL MODELO, y hay que saber por que.
        #
        # En 0:15 salio al aire, nitido y abajo a la derecha, algo con forma de renglon
        # de TEXTO. El user lo marco como "algo se escapa del blur". No estaba en la
        # fuente: medido en el mismo instante y la misma region, el crudo es una mancha de
        # bloques de compresion sin ninguna estructura y el intermedio del modelo la
        # convirtio en glifos con forma de letras. Un GAN de superresolucion entrenado
        # sobre imagen natural lee cualquier resto de ruido como detalle a reconstruir, y
        # reconstruye ALGO.
        #
        # Se intento mezclar la salida del modelo con la fuente ampliada guiando la mezcla
        # por el detalle local, y NO SIRVE: medido sobre ese mismo cuadro, la region del
        # texto inventado tiene mas varianza local (mediana 0,0110) que el cuadro entero
        # (0,0027), asi que ninguna estadistica local separa lo inventado de lo real. El
        # unico filtro honesto seria no correrle el modelo a ese material.
        #
        # PERO AHORA NO ALCANZA CON EL BLUR. Los recortes del solar pasaron de 1800-4096 px
        # a 700 (ver la nota en `planos.py`: con el recorte ancho el movimiento del plasma
        # se promedia a cero y el plano queda como una foto). A 700 px el escalado a 4K es
        # 5,5x sobre material con cociente de meseta 0,09, y ahi el blur solo deja la
        # imagen mushy.
        #
        # Asi que el modelo vuelve, con la exposicion acotada: las fulguraciones ahora
        # ofrecen recortes grandes (hasta 2500 px, factor 1,5) porque su movimiento es de
        # escala grande y lo sostienen, asi que caen del lado del blur. Solo los discos del
        # SDO, cuyo movimiento es churn de escala chica, necesitan los 700 px y el modelo.
        #
        # LA ALUCINACION SE VIGILA, no se da por resuelta: `qa_entrega.py` puntua cada
        # baldosa por energia de alta frecuencia CONTRA su inestabilidad temporal, que es
        # lo que si separa el caso conocido (la region del texto quedo en el percentil 92
        # de inestabilidad y con 12,5 veces la energia media del cuadro, mientras que por
        # varianza local quedaba apenas sobre la mediana).
        # EL MATERIAL SOLAR NO PASA POR EL MODELO. Decidido con dos casos confirmados a
        # ojo y tres intentos de deteccion fallidos, no por prudencia generica.
        #
        # LOS DOS CASOS. En 0:15 del video anterior salio al aire, nitido y abajo a la
        # derecha, algo con forma de renglon de texto (el user: "algo se escapa del
        # blur"). Se reprodujo en el plan nuevo, en `sol3`: la fuente ahi es una mancha
        # oscura lisa y el modelo la convirtio en glifos con recuadro. O sea que NO
        # alcanza con apuntar el recorte a una region activa: lo inventa en las zonas
        # planas que rodean a esa region.
        #
        # LOS TRES INTENTOS DE DETECTARLO, todos medidos y todos fallidos:
        #
        #   varianza local de la fuente    la region del texto tiene MAS varianza local
        #                                  (0,0110) que el cuadro entero (0,0027)
        #   inestabilidad temporal         el caso conocido puntua 9,5 y sale SEXTO de 16
        #                                  intermedios: el umbral que lo atrapa reprueba
        #                                  cinco inocentes
        #   banda de contraste             la region inventada tiene mas contraste local
        #                                  que el plasma REAL en las tres escalas medidas
        #                                  (0,0049 contra 0,0040 a 16 px; 0,0154 contra
        #                                  0,0130 a 64 px)
        #
        # No hay estadistica barata que separe lo inventado de lo real en este material.
        #
        # LO QUE CUESTA. Los recortes solares son de 600 a 900 px (ver `planos.py`: con el
        # recorte ancho el plano queda quieto), o sea 4,3x a 6,4x de escalado a 4K, y con
        # blur solo esa imagen queda BLANDA. Es un costo real y hay que saberlo. Se elige
        # blando antes que texto inventado, porque lo segundo el user ya lo marco.
        if f[6] == "sol":
            # PISO 7,0 Y NO 2,6. Con 2,6 los planos solares salian CUADRICULADOS, que es
            # justo el defecto que el user marco en el 4K anterior: se veian los cuadrados
            # de compresion, no una imagen blanda. Es aritmetica: el bloque mide 8 px en la
            # fuente y estos recortes escalan 5,5x a 6,4x, o sea que el cuadrado llega a
            # 44-51 px en pantalla. Para disolverlo el blur tiene que ser del orden del
            # bloque, no de un cuarto.
            #
            # Medido sobre un plano solar de 700 px: a sigma 3,5 los bordes rectos siguen
            # ahi y a 7,5 la zona lee como nube. El costo en movimiento es chico y entra
            # sobrado: 1,31 a sigma 3,5 contra 1,14 a 7,5, y el examen pide 0,40.
            # EL PISO QUEDA EN 2,6, Y ESO DEJA CUADRICULADOS LOS DISCOS SOLARES. Hay que
            # saberlo: es una decision tomada con numeros, no un descuido.
            #
            # EL PROBLEMA. El bloque de compresion mide 8 px en la fuente y los recortes de
            # los discos escalan 5,5x a 6,4x, o sea que el cuadrado llega a 44-51 px en
            # pantalla. Con sigma 2,6 no se disuelve: se ven los cuadrados.
            #
            # POR QUE NO SE SUBE. Se probo y el blur que hace falta se come el movimiento,
            # que es el otro criterio del examen:
            #
            #     piso fijo 7,0        arregla los discos y tira 3 fulguraciones a 0,23-0,40
            #     piso factor x 1,2    sigue tirando fl1 (0,40), fl6 (0,33) y sol4 (0,32)
            #
            # El examen pide 0,40, asi que las dos veces el video dejaba de pasar. Con 2,6
            # pasa los 11 criterios y el costo es visual y acotado: cinco planos solares.
            #
            # LAS SALIDAS REALES, ninguna barata: material solar con menos compresion, o
            # aceptar el modelo en esos planos sabiendo que inventa (ver la nota de arriba),
            # o recortes mas grandes ahi, que los deja quietos (ver `planos.py`).
            blur.append((i, nombre, max(sigma, 2.6)))
        elif factor >= FACTOR_MIN:
            modelo.append((i, nombre, f, ancho, coc, factor))
        else:
            blur.append((i, nombre, sigma))
    return modelo, blur


def procesar(idx, nombre, fila, ancho_pedido, factor):
    fuente = os.path.join(RAIZ, fila[1])
    ss, dur, recorte, vel = float(fila[2]), float(fila[3]), fila[4], float(fila[7])
    # el tamaño se PREGUNTA, no se deduce del recorte pedido
    ancho, alto = _tam_real(fuente, recorte)
    # x4 solo cuando hace falta de verdad; arriba de 960 px de recorte alcanza x2 y
    # cuesta la cuarta parte de memoria en el upsampler
    escala = 4 if factor >= 3.5 else 2
    dst = os.path.join(SALIDA, f"{idx:03d}.mov")
    firma_txt = f"{fila[1]}|{ss}|{dur}|{recorte}|{vel}|x{escala}|{ancho}x{alto}|prores10|v2"
    firma = dst + ".firma"
    if os.path.exists(dst) and os.path.exists(firma) and open(firma).read() == firma_txt:
        return dst, ancho * escala, alto * escala, True

    fps = _fps(fuente)
    # SOLO los cuadros unicos: la ralentizacion se aplica despues, en el montaje
    segundos = dur / vel
    n = max(1, int(round(segundos * fps)) + 2)

    lector = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-ss", f"{ss}", "-i", fuente, "-frames:v", str(n),
         "-vf", f"crop={recorte}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE)
    escritor = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le",
         "-s", f"{ancho * escala}x{alto * escala}", "-r", f"{fps}", "-i", "-",
         # PRORES DE 10 BITS, no H.264 de 8.
         #
         # El modelo entrega un degradado con 19462 niveles distintos. Al guardarlo en 8
         # bits quedaban 84, y el grado del video (que estira ~4,4x) los abria en bandas
         # concentricas bien visibles: 60 niveles de gris en el resultado contra 193 si
         # se mantiene la precision. Las bandas eran MIAS, no del modelo.
         #
         # Va por VideoToolbox porque usa el motor de medios del Mac y no le pelea ni la
         # GPU al modelo ni los nucleos al decodificador.
         "-c:v", "prores_videotoolbox", "-profile:v", "3", "-pix_fmt", "yuv422p10le", dst],
        stdin=subprocess.PIPE)

    red, disp = cargar(_pesos(escala), escala=escala)
    if disp == "mps":
        red = red.half()
    tam = ancho * alto * 3
    hechos = 0
    sobra = 0
    while True:
        crudo = lector.stdout.read(tam)
        if len(crudo) < tam:
            sobra = len(crudo)      # si sobran bytes, el tamaño esta mal y hay corrimiento
            break
        a = np.frombuffer(crudo, np.uint8).reshape(alto, ancho, 3).astype(np.float32) / 255.0
        y = ampliar(red, a, escala, disp)
        if y.dtype != np.uint16:                     # el camino baldoseado devuelve float
            y = (y * 65535.0 + 0.5).astype(np.uint16)
        escritor.stdin.write(y.tobytes())
        hechos += 1
        if hechos % 25 == 0:
            print(f"      {hechos}/{n}", flush=True)
    escritor.stdin.close()
    escritor.wait()
    lector.wait()
    del red
    if disp == "mps":
        torch.mps.empty_cache()
    if hechos == 0:
        raise RuntimeError(f"plano {idx} ({nombre}): no salio ningun cuadro")
    if sobra:
        os.remove(dst)
        raise RuntimeError(
            f"plano {idx} ({nombre}): sobraron {sobra} bytes sobre cuadros de {tam}. "
            f"El tamaño real ({ancho}x{alto}) no coincide con lo que entrega ffmpeg y "
            f"cada cuadro sale corrido. NO se guarda el intermedio.")
    open(firma, "w").write(firma_txt)
    return dst, ancho * escala, alto * escala, False


def main():
    plan = sys.argv[1] if len(sys.argv) > 1 else "out/bj3_n_pt_4k.plan.txt"
    solo_listar = "--listar" in sys.argv
    os.makedirs(SALIDA, exist_ok=True)
    modelo, blur = planificar(plan)
    filas_por_idx = {i: f for i, f in enumerate(
        [l.rstrip("\n").split("|") for l in open(plan) if l.strip()], start=1)}
    print(f"  modelo: {len(modelo)} planos   blur: {len(blur)} planos")
    if solo_listar:
        for i, nombre, f, ancho, coc, factor in modelo:
            print(f"    {i:3d} {nombre:<9} recorte {ancho:>5}  coc {coc:.2f}  x{factor:.1f}"
                  f"  -> modelo x{4 if factor >= 3.5 else 2}")
        for i, nombre, s in blur:
            print(f"    {i:3d} {nombre:<9} blur sigma {s}")
        return

    mapa = []
    for k, (i, nombre, f, ancho, coc, factor) in enumerate(modelo, start=1):
        print(f"  [{k}/{len(modelo)}] plano {i} {nombre} recorte {ancho} x{factor:.1f}", flush=True)
        dst, w, h, reusado = procesar(i, nombre, f, ancho, factor)
        print(f"      {'reusado' if reusado else 'listo'} -> {w}x{h}", flush=True)
        # LA CLAVE LLEVA LA DURACION. Sin ella dos planos que usan la misma fuente, el
        # mismo arranque y el mismo recorte pero duran distinto colapsan en una sola
        # entrada, y el mas largo se lleva el intermedio del mas corto: el build aborto
        # con "el plano 40 pide 025.mov y dura 10,07 s". Pasa de verdad, hay dos casos
        # (lava1 y rio), porque las reglas de repeticion permiten reusar una fuente con
        # otro largo.
        mapa.append(f"{f[1]}|{f[2]}|{f[3]}|{f[4]}|{os.path.relpath(dst, RAIZ)}|{w}|{h}")
    with open(os.path.join(SALIDA, "mapa.txt"), "w") as fh:
        fh.write("\n".join(mapa) + "\n")
    with open(os.path.join(SALIDA, "blur.txt"), "w") as fh:
        fh.write("\n".join(f"{filas_por_idx[i][1]}|{filas_por_idx[i][2]}|"
                            f"{filas_por_idx[i][3]}|{filas_por_idx[i][4]}|{s}"
                            for i, _, s in blur) + "\n")
    print(f"\n  {len(mapa)} intermedios en .ia/  +  {len(blur)} planos con blur")


if __name__ == "__main__":
    main()
