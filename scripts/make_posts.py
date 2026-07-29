#!/usr/bin/env python3
"""Genera los posts estáticos de fragmento (modo B) para IG feed.

Tipografía APROBADA (no tocar): Courier New itálica gris claro, abajo-izquierda,
firma muted debajo, leve blur de "señal" (0.6). Fondo negro del site.

Novedad: cada slot puede llevar **fondo** (frame de los visualizers, generado por
`make_post_backgrounds.py`) en vez de negro plano. El fondo NUNCA puede comerse
el texto: se oscurece global (DARKEN) + se aplica un scrim medido sobre la banda
de texto hasta que la luminancia cae bajo TARGET_* (QA automático, ver
`legibility_fix`). Los 9 slots llevan fondo (decidido 2026-07-26); `None` deja
el slot en negro puro y sigue soportado.

Fragmentos en inglés (textos.md §5.4). 1080×1350 (IG portrait). PNG sin pérdida.

Uso:  python3 scripts/make_posts.py            → redes/aem/social/post_NN.png
      python3 scripts/make_posts.py --all-black  → vuelve a la v1 (todo negro)
"""
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BLUR = 0.6      # leve difuminado "señal/transmisión" (aprobado); 0 = nítido
DARKEN = 0.62   # multiplicador global del fondo (misterio + cohesión con el site)
TARGET_MEAN = 26   # luminancia media máxima permitida en la banda de texto
TARGET_P99 = 72    # pico máximo permitido (evita un highlight justo sobre una letra)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "redes/aem/social")
BGDIR = os.path.join(OUTDIR, "_bg")
os.makedirs(OUTDIR, exist_ok=True)

# tokens del site
BG = (10, 10, 12)      # --bg
FG = (207, 207, 210)   # --fg
MUTED = (116, 116, 126)  # --muted
MUTED_ON_BG = (152, 152, 160)  # firma sobre fondo con imagen (ver make_post)
COUR = "/System/Library/Fonts/Supplemental/Courier New.ttf"
COUR_I = "/System/Library/Fonts/Supplemental/Courier New Italic.ttf"

W, H = 1080, 1350
M = 90  # margen izquierdo

# (fragmento, fondo) — el fondo se elige por afinidad con el fragmento.
# Los 9 llevan imagen (decidido 2026-07-26: el negro plano no frena el scroll).
# post_02 y post_03 usan las frases 13 y 11 de textos.md: las que tenian antes
# (#3 y #5) ya se usan en los captions de los Reels de recursion y outbound.
# `None` = negro puro, queda disponible por si se quiere volver a mezclar.
SLOTS = [
    ("what returned is not what we sent", "eye"),
    ("what was becoming ceased to be what had been launched: it became the crossing itself", "lace"),
    ("that pulse did not belong to it but to the medium that sustained it", "core"),
    ("the wind that had been pushing ceased to push", "cells"),
    ("a wave is not what crosses a medium: it is the medium itself, crossing", "curl"),
    ("a note, while heard, no longer remembers having been a note", "rays"),
    ("what was happening did not close upon itself: it spiraled outward", "mandala"),
    ("motion without change is the only stable form of being the body in transit knows", "limb"),
    ("a spiral does not contain a trajectory: it is the trajectory beholding itself from within", "iris"),
]


def layout(text):
    """Devuelve (líneas, font, y_inicial, y_firma) — la posición aprobada."""
    size = 46
    f = ImageFont.truetype(COUR_I, size)
    lines = textwrap.wrap(text, 24)
    lh = int(size * 1.5)
    y0 = H - 260 - len(lines) * lh
    y_sig = y0 + len(lines) * lh + 20
    return lines, f, y0, lh, y_sig


def band_stats(im, top, bottom):
    """Luminancia media y p99 de la banda de texto (solo la mitad izquierda,
    que es donde vive el texto)."""
    crop = im.convert("L").crop((0, max(0, top), int(W * 0.72), min(H, bottom)))
    px = sorted(crop.tobytes())  # imagen L → 1 byte por pixel
    mean = sum(px) / len(px)
    p99 = px[int(len(px) * 0.99)]
    return mean, p99


def legibility_fix(im, top, bottom):
    """Oscurece la banda de texto hasta que pasa TARGET_MEAN/TARGET_P99.

    Aplica un factor con feather hacia arriba (para que no se vea el borde del
    scrim). Itera hasta 8 veces; si no converge, avisa por stderr.
    """
    feather = 220
    for _ in range(8):
        mean, p99 = band_stats(im, top, bottom)
        if mean <= TARGET_MEAN and p99 <= TARGET_P99:
            return im, mean, p99
        # cuánto hay que bajar: el peor de los dos criterios
        factor = min(TARGET_MEAN / max(mean, 1e-6), TARGET_P99 / max(p99, 1e-6))
        factor = max(0.35, min(0.95, factor))  # de a poco, sin matar la textura
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        strength = int(255 * (1 - factor))
        md.rectangle([0, top, W, H], fill=strength)
        for i in range(feather):  # degradado arriba de la banda
            y = top - feather + i
            if y < 0:
                continue
            md.line([(0, y), (W, y)], fill=int(strength * i / feather))
        im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, mask)
    mean, p99 = band_stats(im, top, bottom)
    print(f"   !! no convergió (mean={mean:.1f} p99={p99}) — revisar a ojo", file=sys.stderr)
    return im, mean, p99


def make_post(text, bg_slug, path):
    lines, f, y0, lh, y_sig = layout(text)

    if bg_slug:
        src = os.path.join(BGDIR, f"bg_{bg_slug}.jpg")
        if not os.path.exists(src):
            print(f"   !! falta {os.path.relpath(src, ROOT)} — cae a negro", file=sys.stderr)
            im = Image.new("RGB", (W, H), BG)
        else:
            im = Image.open(src).convert("RGB").resize((W, H))
            im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im, DARKEN)
            im, mean, p99 = legibility_fix(im, y0 - 40, y_sig + 60)
            print(f"   banda de texto: mean={mean:.1f} p99={p99}")
    else:
        im = Image.new("RGB", (W, H), BG)

    # texto en capa aparte, con alpha, para difuminar solo el texto
    tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tl)
    y = y0
    for ln in lines:
        d.text((M, y), ln, font=f, fill=FG + (255,))
        y += lh
    # la firma sube un poco de brillo sobre fondo con imagen: el muted del site
    # está calibrado contra negro puro y sobre textura pierde contraste
    sig = MUTED_ON_BG if bg_slug else MUTED
    d.text((M, y_sig), "ÆM · HELIOPAUSE", font=ImageFont.truetype(COUR, 24), fill=sig + (255,))
    if BLUR > 0:
        tl = tl.filter(ImageFilter.GaussianBlur(BLUR))
    im = Image.alpha_composite(im.convert("RGBA"), tl).convert("RGB")
    im.save(path)


if __name__ == "__main__":
    all_black = "--all-black" in sys.argv
    for i, (frag, bg) in enumerate(SLOTS, 1):
        p = os.path.join(OUTDIR, f"post_{i:02d}.png")
        print("->", os.path.relpath(p, ROOT), f"[{'negro' if (all_black or not bg) else bg}]")
        make_post(frag, None if all_black else bg, p)
