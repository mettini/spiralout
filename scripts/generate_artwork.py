"""Genera artwork con Stable Diffusion XL Turbo (open source) en local.

Workflow:
  1. Lee un brief .md de transmissions/01/artwork/generation_briefs/
     (extrae el bloque entre primer 'Prompt' y 'Negative')
  2. Lee el negative prompt (entre 'Negative' y siguiente '##')
  3. Genera N imagenes con MPS (Metal Performance Shaders) en Apple Silicon
  4. Guarda en transmissions/01/artwork/generated/<brief_id>/<timestamp>_NN.png

Uso:
  python3 scripts/generate_artwork.py 00_artist_photo --n 4
  python3 scripts/generate_artwork.py 01_hero_background --n 6 --width 1024 --height 576
  python3 scripts/generate_artwork.py --list

Modelos soportados (auto-bajan primera vez):
  - stabilityai/sdxl-turbo (~7 GB) — DEFAULT, rapido (4 steps)
  - stabilityai/stable-diffusion-xl-base-1.0 (~13 GB) — calidad alta, mas lento
  - black-forest-labs/FLUX.1-schnell (~24 GB) — calidad SOTA, requiere mas RAM

Requisitos:
  pip install diffusers transformers accelerate torch
  Mac M1/M2/M3 con >= 16 GB RAM (SDXL Turbo) o >= 32 GB (FLUX)
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIEFS_DIR = PROJECT_ROOT / 'transmissions' / '01' / 'artwork' / 'generation_briefs'
OUTPUT_DIR = PROJECT_ROOT / 'transmissions' / '01' / 'artwork' / 'generated'

# Negative global — se concatena al negative de cada brief.
# Refuerza estética del proyecto y evita texto inventado por el AI.
GLOBAL_NEGATIVE = (
    'text, letters, words, typography, characters, alphabet, writing, '
    'signs, captions, logos with letters, glitched text, typography artifacts, '
    'watermark, signature, copyright notice'
)


def parse_brief(brief_path: Path, variation_idx: int = 0):
    """Extrae prompt + negative del brief markdown.

    Heurística robusta:
      - Toma TODOS los bloques ``` del archivo
      - Filtra los que estan bajo una seccion con "Negative" o "Settings"
      - De los restantes, devuelve el bloque #variation_idx (0 = principal)
      - El primer bloque bajo una sección que contenga "Negative" es el negative

    Args:
        variation_idx: 0 = prompt principal. 1, 2, 3, ... = variaciones V1, V2, V3...
                       (en briefs como 01_hero_background_painterly que tienen
                       una seccion "## Variaciones" con multiples ``` blocks)
    """
    text = brief_path.read_text()

    # Encontrar todos los bloques ``` con su contexto (cabecera anterior)
    blocks = []  # lista de (header_anterior, contenido_bloque)
    for m in re.finditer(r'```([^`]+)```', text, re.DOTALL):
        # Encontrar la última cabecera "## ..." o "**Negative**" o "**Prompt**"
        # antes de este bloque
        before = text[:m.start()]
        last_header = ''
        for h_pat in [r'\*\*([Nn]egative[^\*]*)\*\*', r'\*\*([Pp]rompt[^\*]*)\*\*',
                       r'^##\s*([^\n]+)']:
            for hm in re.finditer(h_pat, before, re.MULTILINE):
                last_header = hm.group(1).strip()
        blocks.append((last_header, m.group(1).strip()))

    if not blocks:
        raise ValueError(f'No se encuentran bloques ``` en {brief_path}')

    # Filtrar bloques NO negative
    prompt_blocks = [b for h, b in blocks if 'negative' not in h.lower()
                     and 'settings' not in h.lower()]
    negative_blocks = [b for h, b in blocks if 'negative' in h.lower()]

    if not prompt_blocks:
        raise ValueError(f'No se encuentra prompt no-negative en {brief_path}')

    if variation_idx >= len(prompt_blocks):
        raise ValueError(
            f'Brief {brief_path.name} tiene {len(prompt_blocks)} prompt block(s), '
            f'pediste variation_idx={variation_idx} (0-based). '
            f'Validos: 0..{len(prompt_blocks) - 1}'
        )

    prompt = prompt_blocks[variation_idx]
    negative = negative_blocks[0] if negative_blocks else ''

    # Si el negative es solo una referencia ("igual que opcion A", "[base anterior]"),
    # buscar el primer negative real
    while negative and ('igual' in negative.lower() or '[base anterior]' in negative.lower()):
        negative_blocks = negative_blocks[1:]
        if not negative_blocks:
            negative = ''
            break
        negative = negative_blocks[0]

    return prompt, negative


def list_briefs():
    print('Briefs disponibles:')
    for f in sorted(BRIEFS_DIR.glob('*.md')):
        if f.name in ('README.md', 'prompt_library.md'):
            continue
        print(f'  {f.stem}')


def generate(brief_id: str, n_images: int, width: int, height: int,
             model: str, steps: int, seed: int = None, variation: int = 0):
    """Genera N imagenes para un brief."""
    # Lazy imports — pesados
    print('cargando torch + diffusers (puede tardar la primera vez)...')
    import torch  # noqa: F401
    from diffusers import AutoPipelineForText2Image
    from PIL import Image  # noqa: F401

    brief_path = BRIEFS_DIR / f'{brief_id}.md'
    if not brief_path.exists():
        candidates = list(BRIEFS_DIR.glob(f'{brief_id}*'))
        if candidates:
            brief_path = candidates[0]
        else:
            print(f'ERROR: no existe brief {brief_id}', file=sys.stderr)
            print('Disponibles:', file=sys.stderr)
            list_briefs()
            sys.exit(1)

    prompt, negative = parse_brief(brief_path, variation_idx=variation)
    # Concatenar negative global (anti-text) al del brief
    if negative:
        full_negative = f'{negative}, {GLOBAL_NEGATIVE}'
    else:
        full_negative = GLOBAL_NEGATIVE

    print(f'\n=== {brief_path.stem} ===')
    print(f'Modelo: {model}')
    print(f'Resolucion: {width}x{height} · Steps: {steps} · N: {n_images}')
    print(f'\nPrompt:\n{prompt[:200]}{"..." if len(prompt) > 200 else ""}')
    print(f'\nNegative:\n{full_negative[:150]}...')
    print()

    # Setup pipeline
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f'Device: {device}')

    # MPS + fp16 en SDXL = NaN al decodificar -> PNG negro 1.8KB.
    # Probamos varios fixes (vae fp16-fix, upcast_vae) sin exito en MPS.
    # Solucion robusta: correr TODO el pipeline en fp32 cuando estamos en MPS.
    # Cuesta ~2x RAM (SDXL Turbo: ~14GB en vez de ~7GB) pero garantiza no NaN.
    # Las attention/vae slicing optimizations bajan los picos a ~10-12GB.
    pipe = AutoPipelineForText2Image.from_pretrained(
        model,
        torch_dtype=torch.float32,
    )
    pipe = pipe.to(device)

    # Memory optimizations — bajan picos de ~25GB a ~10-12GB en fp32.
    # NO usar enable_vae_tiling en MPS: rompe el decoder y devuelve frames negros.
    if device == 'mps':
        pipe.enable_attention_slicing(slice_size='auto')
        pipe.enable_vae_slicing()

    # SDXL Turbo se entrena para CFG=0 -> ignora negative_prompt y ahorra memoria.
    is_turbo = 'turbo' in model.lower()
    guidance = 0.0 if is_turbo else 1.5

    # Generar — si es una variacion, mete las imagenes en subdir _vN
    out_dir = OUTPUT_DIR / brief_path.stem
    if variation > 0:
        out_dir = out_dir / f'v{variation}'
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S')

    for i in range(n_images):
        s = seed + i if seed is not None else None
        generator = torch.Generator(device=device).manual_seed(s) if s is not None else None
        print(f'  {i+1}/{n_images} generating...')
        kwargs = dict(
            prompt=prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            generator=generator,
        )
        if not is_turbo:
            kwargs['negative_prompt'] = full_negative
        image = pipe(**kwargs).images[0]
        out_path = out_dir / f'{timestamp}_{i+1:02d}.png'
        image.save(out_path)
        print(f'    -> {out_path}')

    print(f'\nGenerado en: {out_dir}')
    print(f'Total: {n_images} imagen(es)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('brief', nargs='?', help='ID del brief (ej "00_artist_photo")')
    ap.add_argument('--list', action='store_true', help='Listar briefs disponibles')
    ap.add_argument('--n', type=int, default=4, help='Cantidad de imagenes (default 4)')
    ap.add_argument('--width', type=int, default=1024)
    ap.add_argument('--height', type=int, default=1024)
    ap.add_argument('--model', default='stabilityai/sdxl-turbo',
                    help='Modelo HF (sdxl-turbo, stable-diffusion-xl-base-1.0, FLUX.1-schnell)')
    ap.add_argument('--steps', type=int, default=4, help='Inference steps (4 para turbo, 20-30 para SDXL base)')
    ap.add_argument('--seed', type=int, default=None, help='Seed (para reproducibilidad)')
    ap.add_argument('--variation', type=int, default=0,
                    help='Indice de variacion (0=principal, 1=V1, 2=V2, ...). '
                         'Solo valido en briefs con seccion "## Variaciones".')
    args = ap.parse_args()

    if args.list or not args.brief:
        list_briefs()
        return

    generate(args.brief, args.n, args.width, args.height,
             args.model, args.steps, args.seed, variation=args.variation)


if __name__ == '__main__':
    main()
