#!/usr/bin/env python3
"""Clips generados para el video de Aerolite (TX02 track 1).

    python3.10 lab/thermal_mass/video/generar.py            # todo
    python3.10 lab/thermal_mass/video/generar.py cielo_01   # uno solo

DOS ESCENAS, bajadas por el user:

  A · el aerolito   cielo caotico, una luz, y algo cayendo
  B · las criaturas dos entidades hablando en un planeta con flora y fauna

NO se busca que queden bien. Se busca MATERIA PRIMA para deformar: todo esto pasa
despues por el mismo tratamiento que la lluvia (fragmento apretado, estirado, blanco
y negro aplastado), asi que lo unico que importa es que tenga la forma correcta y
algo de movimiento. Que se note que es generado es indistinto: despues no se entiende
que es.

CONFIG VALIDADA (memory/ltx_video_poc_learnings.md): guidance 6.0, prompts CORTOS de
menos de 50 tokens, y 768x512. Los defaults (guidance 3.0 y prompts largos) NO
funcionan: dan puré. Es un aprendizaje que ya costo una tarde, no lo toques sin medir.

Licencia: LTX-Video es Open RAIL++, permite uso comercial (docs/video/09).
"""
import os
import sys

import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "generado")

ANCHO, ALTO = 768, 512
CUADROS = 65          # 8k+1, requisito del modelo. A 24 fps son ~2,7 s
                      # Alcanza: de cada clip se usa un fragmento recortado
FPS = 24
GUIDANCE = 6.0        # NO bajar: con 3.0 (el default) sale puré
PASOS = 25            # 40 no aportaba: el material se deforma igual despues
SEMILLA = 24          # el hexagrama del proyecto

NEGATIVO = ("worst quality, blurry, jittery, distorted, watermark, text, "
            "people, faces, cartoon")

# Prompts cortos a proposito. Cada uno es una toma, no una escena.
#
# CRITERIO, aprendido probando: lo que sobrevive al tratamiento duro (blanco y negro
# aplastado) es COSA BRILLANTE SOBRE FONDO OSCURO. Un gris difuso sobre gris se va
# entero a negro y no queda nada.
#
# El primer intento de "chaotic storm clouds churning, dark sky" dio un atardecer
# tranquilo, casi sin movimiento, y tratado quedo en negro. Por eso ahora todos los
# prompts piden explicitamente algo luminoso contra algo oscuro, y verbos de
# movimiento violento en vez de adjetivos de atmosfera.
CLIPS = {
    # A · el aerolito
    "cielo_01": "violent lightning bolts inside black storm clouds",
    "cielo_02": "white lightning flashing behind dense black clouds",
    "cielo_03": "shaft of bright white light piercing black clouds",
    "cielo_04": "burning object falling, long trail of fire, night sky",
    "cielo_05": "bright fireball streaking across a black sky",
    # C · las bocas, para el tramo donde hablan las voces.
    #
    # LECCION: los prompts de abajo pedian ATMOSFERA ("silhouettes", "fog", "dim") y
    # el modelo devolvia una postal quieta. Medido: 0,11 a 0,61 de movimiento contra
    # 9,64 de la lluvia. Estos piden VERBOS y movimiento explicito, que es lo unico
    # que hace que LTX genere algo que se mueva.
    "boca_01": "extreme close up of a mouth opening and closing slowly",
    "boca_02": "distorted face stretching and warping, dark",
    "boca_03": "lips moving and speaking, extreme close up, low light",
    "boca_04": "a face slowly melting and reforming, dark background",
    # B · las criaturas. La silueta ya es contraste por definicion: cuerpo negro
    # contra fondo encendido. Por eso todos piden contraluz.
    "bicho_01": "two black silhouettes facing each other, bright fog behind",
    "bicho_02": "huge dark leaves backlit by strong white light",
    "bicho_03": "two dark shapes moving through tall grass, strong backlight",
    "bicho_04": "black silhouettes of tall plants against bright mist",
    "bicho_05": "dark creature silhouette between huge leaves, glowing fog",
}


def main():
    pedidos = sys.argv[1:] or list(CLIPS)
    faltan = [c for c in pedidos if c not in CLIPS]
    if faltan:
        print(f"no existe: {', '.join(faltan)}", file=sys.stderr)
        return 1

    os.makedirs(SALIDA, exist_ok=True)
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video

    dispositivo = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"  cargando LTX-Video en {dispositivo}...")
    # float16 y NO bfloat16: en Metal el bf16 cae en caminos lentos. Con bf16, 40
    # pasos y 97 cuadros, un clip tardaba 30 minutos.
    tipo = torch.float16 if dispositivo == "mps" else torch.bfloat16
    pipe = LTXPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=tipo)

    # MEMORIA. Sin esto el proceso se come 33 GB de 36 y la maquina queda inusable.
    # Dos frentes, y el segundo es el que mas pesa:
    #
    #   tiling/slicing en el VAE  -> el pico real no es el modelo sino decodificar
    #                                los 97 cuadros de una sola vez. Con tiling el
    #                                VAE trabaja por bloques y el pico se desploma.
    #   offload por modulo        -> deja en el dispositivo solo la parte que esta
    #                                corriendo (text encoder, transformer o VAE) y
    #                                el resto en RAM del sistema.
    #
    # Cuesta algo de velocidad. Con `--rapido` se corre como antes, para una maquina
    # que no este haciendo otra cosa.
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    if "--rapido" in sys.argv:
        pipe.to(dispositivo)
    else:
        try:
            pipe.enable_model_cpu_offload(device=dispositivo)
            print("  offload por modulo + VAE por bloques (usa ~1/3 de RAM)")
        except Exception as e:
            print(f"  sin offload ({e}); solo VAE por bloques")
            pipe.to(dispositivo)

    for nombre in pedidos:
        destino = os.path.join(SALIDA, f"{nombre}.mp4")
        if os.path.exists(destino) and "--rehacer" not in sys.argv:
            print(f"  {nombre}: ya existe")
            continue
        print(f"  {nombre}: {CLIPS[nombre]}")
        g = torch.Generator(device="cpu").manual_seed(SEMILLA)
        video = pipe(prompt=CLIPS[nombre], negative_prompt=NEGATIVO,
                     width=ANCHO, height=ALTO, num_frames=CUADROS,
                     num_inference_steps=PASOS, guidance_scale=GUIDANCE,
                     generator=g).frames[0]
        export_to_video(video, destino, fps=FPS)
        print(f"  -> {os.path.relpath(destino, AQUI)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
