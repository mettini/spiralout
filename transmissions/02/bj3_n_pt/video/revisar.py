#!/usr/bin/env python3
"""Detecta placas de titulo y marcas de agua en material de archivo.

    python3.10 transmissions/02/bj3_n_pt/video/revisar.py clip.mp4 [otro.mp4 ...]

POR QUE EXISTE

Se montaron clips del USGS con el cartel "Lava Flow / May 20, 2018 / Video from the
U.S. Geological Survey" quemado en la imagen, y con el logo del USGS de marca de agua.
Aparecio en el video terminado en el minuto 8, en 8:07 y en 8:34. Es la unica clase de
error que se lee como error y no como decision estetica.

COMO LO DETECTA

Una placa de texto y una marca de agua tienen la misma firma: **son brillantes y NO se
mueven**. Entonces se calcula, pixel por pixel, el desvio estandar a lo largo del
tiempo. Donde el desvio es casi cero y el brillo es alto, hay algo pegado encima.

Con eso se saca:
  - la ventana limpia del clip, en segundos
  - que zonas del cuadro estan contaminadas, por si el resto sirve recortando

No reemplaza mirar el clip, pero atrapa lo que el ojo se saltea cuando hay 180 planos.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ALTO, ANCHO = 108, 192      # suficiente para ver una placa, barato de procesar
QUIETO = 6.0                # desvio temporal por debajo de esto = no se mueve
BRILLANTE = 150             # y con este brillo encima = algo pegado
MIN_AREA = 0.004            # fraccion del cuadro para que valga la pena avisar


def leer(f, ss, dur, fps=4):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', f, '-t', str(dur),
                        '-vf', f'fps={fps},scale={ANCHO}:{ALTO},format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True).stdout
    n = len(o) // (ANCHO * ALTO)
    if n < 3:
        return None
    return np.frombuffer(o[:n * ANCHO * ALTO], dtype=np.uint8).reshape(n, ALTO, ANCHO).astype(float)


def dur_de(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip() or 0)


def pegado(a):
    """Mascara de lo que esta quieto, brillante Y CON BORDES: placa o marca de agua.

    El criterio de bordes es lo que separa una placa de un cielo. Un cielo tambien es
    brillante y casi quieto, pero es LISO. El texto y un logo tienen bordes filosos.
    Sin este tercer criterio el detector marcaba el 18% del cuadro de un plano aereo
    como si fuera un cartel.
    """
    if a is None:
        return None, 0.0
    med = a.mean(axis=0)
    quieto = a.std(axis=0) < QUIETO
    # densidad de borde: gradiente local sobre el promedio temporal
    gy = np.abs(np.diff(med, axis=0, prepend=med[:1]))
    gx = np.abs(np.diff(med, axis=1, prepend=med[:, :1]))
    borde = (gx + gy) > 18
    m = quieto & (med > BRILLANTE) & borde
    return m, m.mean()


def hoja(f, n=12):
    """Hoja de contacto: n cuadros repartidos a lo largo del clip, en una grilla.

    La deteccion automatica de abajo sirve de PISTA, no de veredicto: en un plano
    aereo las rocas del crater tambien son brillantes, quietas y con bordes, asi que
    marca de mas. Para un punado de clips, mirar es mas confiable que afinar umbrales.
    Esta es la herramienta que hubiera evitado montar el cartel del USGS.
    """
    d = dur_de(f)
    dest = f.rsplit('.', 1)[0] + '_hoja.png'
    ts = [d * (i + 0.5) / n for i in range(n)]
    tmp = tempfile.mkdtemp()
    trozos = []
    for i, t in enumerate(ts):
        q = os.path.join(tmp, f'{i:02d}.png')
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', f,
                            '-frames:v', '1', '-vf', 'scale=320:180', q], capture_output=True)
        if r.returncode == 0 and os.path.exists(q):
            trozos.append(q)
    if len(trozos) < 4:
        print('  hoja FALLO: no se pudieron extraer cuadros')
        shutil.rmtree(tmp, ignore_errors=True)
        return
    m = len(trozos)
    entradas = [x for q in trozos for x in ('-i', q)]
    filtro = ''.join(f'[{i}:v]' for i in range(m)) + f'xstack=inputs={m}:layout=' + \
        '|'.join(f'{(i % 4) * 320}_{(i // 4) * 180}' for i in range(m))
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + entradas +
                   ['-filter_complex', filtro, dest], capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'  {n} cuadros, uno cada {d/n:.1f}s')
    print(f'  hoja -> {dest}')


def zonas(m):
    """En que tercios del cuadro cae lo pegado, para saber si se puede recortar."""
    nombres = []
    for iy, fy in ((0, 'arriba'), (1, 'medio'), (2, 'abajo')):
        for ix, fx in ((0, 'izq'), (1, 'centro'), (2, 'der')):
            sub = m[iy * ALTO // 3:(iy + 1) * ALTO // 3, ix * ANCHO // 3:(ix + 1) * ANCHO // 3]
            if sub.mean() > 0.01:
                nombres.append(f'{fy}-{fx}')
    return nombres


def escanear_salida(f, paso=2.0, umbral=0.006):
    """Escanea el VIDEO YA ARMADO buscando texto quemado.

    Confiar en la ventana limpia de cada fuente no alcanzo: la de `usgs_lava_01` estaba
    anotada como "15 a 27 s" cuando la placa de cierre arranca a los 21, y el cartel
    salio al aire tres veces (8:18, 8:25, 9:08, 9:17).

    Esto revisa el resultado, que es lo unico que el espectador ve. Cualquier tramo
    marcado hay que ir a mirarlo.

        python3.10 revisar.py --salida video.mp4
    """
    d = dur_de(f)
    print(f'\n  ESCANEO DE SALIDA: {f.split("/")[-1]}  {d:.0f}s')
    malos = []
    t = 0.0
    while t < d - paso:
        a = leer(f, t, paso, fps=8)
        m, fr = pegado(a)
        if m is not None and fr > umbral:
            malos.append((t, fr))
        t += paso
    if not malos:
        print('    limpio: no se detecto texto quemado')
    else:
        print(f'    {len(malos)} tramos sospechosos, IR A MIRARLOS:')
        for t, fr in malos:
            print(f'      {int(t)//60}:{int(t)%60:02d}  {100*fr:.2f}% del cuadro')
    return malos



def escanear_fogonazos(f, paso=4.0, umbral_salto=45, umbral_estrobo=3):
    """Busca FOGONAZOS de un cuadro y ESTROBOS, que el escaneo de texto no ve.

    Los dos vienen de lo mismo: `normalize` adaptando la ganancia con una ventana
    corta. Sobre material oscuro o de bajo contraste la ganancia se pone a oscilar y
    la imagen alterna entre casi blanco y casi negro varias veces por segundo.

    Medido en la version con `smoothing=8`: en 9:41 la luminancia iba de 100 a 10 cada
    tres cuadros durante cinco segundos seguidos. El user lo describio como "una
    secuencia de menos de un segundo". Tambien producia el cuadro gris de 0:07 y los
    fogonazos de 0:18 y 0:23.

    fogonazo = un salto de luminancia grande que se DESHACE enseguida (va y vuelve).
    estrobo  = varios de esos seguidos adentro de una misma ventana.
    """
    d = dur_de(f)
    hallazgos = []
    t = 0.0
    while t < d - paso:
        m = leer(f, t, paso, fps=30)
        if m is None or len(m) < 6:
            t += paso
            continue
        lum = m.reshape(len(m), -1).mean(axis=1)
        sal = np.diff(lum)
        # ida y vuelta: un salto grande seguido de otro grande en sentido contrario
        vuelve = [i for i in range(len(sal) - 1)
                  if abs(sal[i]) > umbral_salto and sal[i] * sal[i + 1] < 0
                  and abs(sal[i + 1]) > umbral_salto * 0.6]
        if len(vuelve) >= umbral_estrobo:
            hallazgos.append((t, len(vuelve), "ESTROBO"))
        elif vuelve:
            hallazgos.append((t + vuelve[0] / 30, 1, "fogonazo"))
        t += paso
    print(f"\n  FOGONAZOS Y ESTROBOS: {os.path.basename(f)}")
    if not hallazgos:
        print("    limpio: sin saltos de luminancia que vayan y vuelvan")
    else:
        for t, n, tipo in hallazgos[:20]:
            print(f"    {int(t)//60}:{int(t)%60:02d}  {tipo}"
                  + (f" ({n} idas y vueltas en {int(paso)}s)" if n > 1 else ""))
    return hallazgos


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if sys.argv[1] == '--fogonazos':
        for f in sys.argv[2:]:
            escanear_fogonazos(f)
        return 0
    if sys.argv[1] == '--salida':
        for f in sys.argv[2:]:
            escanear_fogonazos(f)
            escanear_salida(f)
        return 0
    for f in sys.argv[1:]:
        hoja(f)
    for f in sys.argv[1:]:
        d = dur_de(f)
        print(f'\n  {f.split("/")[-1]}   {d:.1f}s')

        # 1. lo que esta pegado TODO el clip: marca de agua
        todo = leer(f, 0, d, fps=2)
        m_todo, frac = pegado(todo)
        if m_todo is not None and frac > MIN_AREA:
            print(f'    MARCA DE AGUA en todo el clip ({100*frac:.2f}% del cuadro): '
                  f'{", ".join(zonas(m_todo))}')
            print(f'    -> ningun recorte puede tocar esas zonas')

        # 2. ventana por ventana: placas de titulo
        paso = 1.0
        sucios = []
        t = 0.0
        while t < d - paso:
            a = leer(f, t, paso, fps=6)
            m, fr = pegado(a)
            if m is not None and fr > MIN_AREA:
                # descontar la marca de agua permanente: solo avisar si hay MAS
                extra = fr - (frac if m_todo is not None else 0)
                if extra > MIN_AREA:
                    sucios.append((t, extra, zonas(m)))
            t += paso

        if not sucios:
            print('    sin placas. Todo el clip es usable')
        else:
            print(f'    PLACAS en {len(sucios)} tramos de 1s:')
            for t, fr, z in sucios:
                print(f'      {t:5.1f}s  {100*fr:5.2f}% del cuadro  {", ".join(z)}')
            libres, ini = [], 0.0
            malos = {int(t) for t, _, _ in sucios}
            for seg in range(int(d) + 1):
                if seg in malos:
                    if seg - ini >= 2:
                        libres.append((ini, seg))
                    ini = seg + 1
            if d - ini >= 2:
                libres.append((ini, d))
            print('    VENTANAS LIMPIAS: ' +
                  ' · '.join(f'{a:.0f} a {b:.0f}s' for a, b in libres))
    return 0


if __name__ == '__main__':
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())
