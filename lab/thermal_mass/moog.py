#!/usr/bin/env python3
"""La voz tipo Moog: el motivo Em + H tocado por un monosintetizador.

    python3.10 lab/thermal_mass/moog.py

POR QUE ACA SI VA UN SYNTH

El intento anterior fue sacar la melodia del propio material, con resonadores
excitados por lluvia (`cuerdas.py`). Toco su techo: al excitar con ruido, la salida
hereda el grano, y el resultado suena lastimado y granular. Una cuerda real se excita
con friccion periodica, no con ruido, y un banco de resonadores sobre ruido no llega
ahi por mas Q que se le ponga.

Un oscilador ES periodico, asi que la voz sale limpia y sostenida por construccion.

Esto no le roba nada al track 3: lo que hace unico a +H es un patch modular que se
autoorganiza (`docs/22`, `docs/39`), no el hecho de que suene un synth. Una linea
monofonica es otra cosa.

QUE HACE A UN MOOG UN MOOG

1. Filtro escalera: pasa-bajos de 24 dB por octava CON RESONANCIA. La resonancia es
   la mitad del caracter.
2. Envolvente de filtro separada de la de amplitud: el brillo entra despues del
   ataque, no junto.
3. Sub-oscilador una octava abajo. Es de donde sale el peso.
4. Osciladores desafinados entre si: sin eso es un tono de test.
5. Glide entre notas. Y ademas es LA firma de Zimmer en Dune: el tono se arrastra en
   vez de saltar.

Afinacion: notas de `docs/43`, derivadas de la base (71,3 Hz), no de un afinador.
"""
import os
import sys

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, iirpeak, sosfilt, sosfilt_zi, tf2sos

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)

sys.path.insert(0, os.path.join(RAIZ, "framework"))

from aem.synths import voz_moog  # noqa: E402
from cuerdas import altura  # noqa: E402
from rain import seguir_arco  # noqa: E402
from render import (SEMILLA, SR, camara, fades, hp, lp, medir,  # noqa: E402
                    mono_graves, respiracion)

DUR = 120.0

# El motivo de docs/43, descendente. Registro grave: es un synth de bajo.
NOTAS = (("si", 11.0), ("sol", 9.0), ("mi", 15.0))
GLIDE_S = 2.4         # el arrastre entre notas, la firma de Zimmer en Dune
VENTANA_DESDE_S = 460 # desde donde empieza a repetir el motivo (el arreglo abre en 470)
PAUSA_S = 4.0         # respiro entre pasadas: no es un loop, son apariciones.
                      # Estaba en 9 y dejaba al moog callado 10 s justo al final
VENTANA_HASTA_S = 645 # ninguna pasada puede quedar cortada por el cierre


def voz(dur=DUR):
    """La voz, con el modelo Huovilainen del framework (`aem/synths.py`).

    Nada de esto es de oido: la escalera es el modelo del circuito real, verificada
    en 24 dB por octava y con el pico de resonancia en el corte.
    """
    n = int(dur * SR)
    notas = [(altura(nombre, octava=1), largo) for nombre, largo in NOTAS]

    x = voz_moog(notas, glide_s=GLIDE_S, detune_cents=7.0, sub=0.62,
                 corte_base=90.0, corte_barrido=2100.0, resonancia=0.78,
                 drive=16.0, sr=SR,
                 env_filtro=(3.2, 4.0, 0.55, 6.0),
                 env_amp=(2.2, 3.0, 0.82, 7.5))

    # El LPF era lo que mas lo tapaba. Con drive 16 la escalera genera pocos armonicos
    # propios, asi que el techo lo define el filtro escalera y no hace falta cortar
    # arriba: se sube de 2000 a 3500. El user pidio "una bocanada de aire fresco", y
    # eso es contenido arriba, no volumen.
    # APLANAR EL LATIDO. Medido, la envolvente ondulaba ~6 dB entre 0,5 y 6 Hz y eso
    # se escucha como un "pumpumpum" en una nota grave sostenida. Se divide por su
    # propia envolvente lenta, que quita la ondulacion sin tocar el ataque ni la caida
    # (esos son mucho mas lentos que 0,5 Hz y quedan intactos).
    env = np.convolve(np.abs(x), np.ones(int(0.35 * SR)) / int(0.35 * SR), "same")
    lento = np.convolve(env, np.ones(int(3.0 * SR)) / int(3.0 * SR), "same")
    # LIMITE DE 2x, y este limite no es cosmetico. Sin el, la division levanta la COLA
    # que estaba decayendo hasta el nivel pleno, o sea que destruye el fade natural del
    # final de cada pasada. Con el moog repitiendo cada 39 s eso dejaba un corte seco
    # audible en 8:09, 8:48, 9:27, 10:06 y 10:46, exactamente uno por ciclo.
    ganancia = np.clip((lento / (env + 1e-6)) ** 0.7, 0.0, 2.0)
    x = x * ganancia
    # y ademas un fade propio en los bordes de la pasada, para que el empalme entre
    # repeticiones no dependa de que la envolvente haya quedado bien
    borde = int(0.35 * SR)
    x[:borde] *= np.linspace(0, 1, borde)
    x[-borde:] *= np.linspace(1, 0, borde)
    x /= np.abs(x).max() or 1.0

    x = lp(np.stack([x, x], axis=1), 3500)

    # el ancho: el mismo material corrido, no un widener
    x = np.stack([x[:, 0], np.roll(x[:, 1], int(0.019 * SR))], axis=1)
    x = hp(x, 34)
    x = mono_graves(x, 150)
    x = respiracion(x, 0.08, periodo=47.0)      # otro primo libre

    # Segunda pasada sobre la cola: de 7 s a 4, mas abierta y con la mitad de mezcla.
    # Un bajo con cola larga es barro, y lo que se pidio es limpieza.
    cola = camara(x, 4, ir_lowpass=2600, wet=0.25, semilla=17000, pre_ms=60)
    x = 0.96 * x + 0.24 * cola[:len(x)]

    # Repetir el motivo hasta llenar la ventana que le da el arreglo.
    #
    # ANTES estaba mal: se colocaba UNA pasada del motivo (35 s) en el 52% del tema,
    # o sea de 349 a 383 s, mientras que el arreglo de `tema.py` recien lo deja pasar
    # a partir de los 470 s. La compuerta abria sobre silencio y el moog directamente
    # no sonaba. Ahora la capa cubre desde VENTANA[0] hasta el final.
    salida = np.zeros((n, 2))
    paso = len(x) + int(PAUSA_S * SR)
    pos = int(VENTANA_DESDE_S * SR)
    # Solo se coloca una pasada si entra ENTERA antes del cierre. Antes se colocaba
    # una que arrancaba a los 636 s y quedaba cortada al mediar: se escuchaba como si
    # el moog volviera a tocar de la nada y despues cortara seco.
    # Se coloca toda pasada que ARRANQUE antes del limite, aunque no entre entera: la
    # envolvente del arreglo la desvanece igual. Exigir que entre completa dejaba al
    # moog callado los ultimos 60 s, que es peor que una pasada recortada por un fade.
    limite = int(VENTANA_HASTA_S * SR)
    while pos < limite:
        fin = min(n, pos + len(x))
        salida[pos:fin] += x[:fin - pos]
        pos += paso
    salida = hp(salida, 30)
    salida = fades(salida, 3.0)
    return salida / (np.abs(salida).max() or 1.0)


def main():
    np.random.seed(SEMILLA)
    print("  motivo (docs/43), registro grave:")
    for nombre, largo in NOTAS:
        print(f"    {nombre.capitalize():5} {altura(nombre, octava=1):7.2f} Hz   {largo:.1f}s")
    print(f"  glide {GLIDE_S}s entre notas\n")

    sr, base = wavfile.read(os.path.join(AQUI, "mix_v3.wav"))
    base = base.astype(np.float64) / 32768.0
    n = min(len(base), int(DUR * SR))
    base = base[:n]

    mg = seguir_arco(voz()[:n], base)
    lufs = pyln.Meter(SR).integrated_loudness(base)
    med = pyln.Meter(SR)
    mg = pyln.normalize.loudness(mg, med.integrated_loudness(mg), lufs)
    if np.abs(mg).max() > 0.98:
        mg *= 0.98 / np.abs(mg).max()

    mezcla = base + mg * 10 ** (-11 / 20)
    mezcla = mezcla / np.abs(mezcla).max() * 10 ** (-6.0 / 20)

    for nombre, x in (("moog", mg), ("mix_v6", mezcla)):
        ruta = os.path.join(AQUI, f"{nombre}.wav")
        wavfile.write(ruta, SR, (x * 32767).astype(np.int16))
        print(f"  -> {os.path.relpath(ruta, RAIZ)}")

    print(f"\n  {'':16}{'LUFS':>6} {'pico':>6} {'truePk':>7} {'crest':>6} {'corr':>6}   "
          f"{'20-60':>5} {'60-120':>5} {'120-250':>6} {'250-500':>6} {'500-1k':>5} {'1k-3k':>5}")
    for nombre, x in (("mix_v3 (antes)", base), ("moog", mg), ("mix_v6", mezcla)):
        medir(nombre, x)


if __name__ == "__main__":
    sys.exit(main())
