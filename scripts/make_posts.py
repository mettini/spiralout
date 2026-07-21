#!/usr/bin/env python3
"""Genera los posts estáticos de fragmento (modo B) para IG feed.

Estilo APROBADO: idéntico al site — fondo negro, Courier New itálica en gris
claro, texto centrado, firma muted abajo. SIN imagen de fondo, SIN scanlines/
glow. Minimal, faceless, un fragmento de transmisión plantado solo.

Fragmentos en inglés (textos.md §5.4). 1080×1350 (IG portrait). PNG sin pérdida.

Uso:  python3 scripts/make_posts.py   → redes/aem/social/post_NN.png
"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "redes/aem/social")
os.makedirs(OUTDIR, exist_ok=True)

# tokens del site
BG = (10, 10, 12)      # --bg
FG = (207, 207, 210)   # --fg
MUTED = (116, 116, 126)  # --muted
COUR = "/System/Library/Fonts/Supplemental/Courier New.ttf"
COUR_I = "/System/Library/Fonts/Supplemental/Courier New Italic.ttf"

W, H = 1080, 1350

# Fragmentos en inglés (textos.md §5.4)
FRAGMENTS = [
    "what returned is not what we sent",
    "the spiral does not ascend: it evolves, never the same",
    "to leave was, in truth, the verb that invented it",
    "the wind that had been pushing ceased to push",
    "a wave is not what crosses a medium: it is the medium itself, crossing",
    "a note, while heard, no longer remembers having been a note",
    "what was happening did not close upon itself: it spiraled outward",
    "motion without change is the only stable form of being the body in transit knows",
    "a spiral does not contain a trajectory: it is the trajectory beholding itself from within",
]


M = 90  # margen izquierdo


def make_post(text, path):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # fragmento: Courier itálica, gris, ABAJO-IZQUIERDA (editorial / margen de dossier)
    size = 46
    f = ImageFont.truetype(COUR_I, size)
    lines = textwrap.wrap(text, 24)
    lh = int(size * 1.5)
    y = H - 260 - len(lines) * lh
    for ln in lines:
        d.text((M, y), ln, font=f, fill=FG)
        y += lh
    # firma muted debajo del fragmento
    y += 20
    d.text((M, y), "ÆM  .  HELIOPAUSE", font=ImageFont.truetype(COUR, 24), fill=MUTED)
    im.save(path)


if __name__ == "__main__":
    for i, frag in enumerate(FRAGMENTS, 1):
        p = os.path.join(OUTDIR, f"post_{i:02d}.png")
        make_post(frag, p)
        print("->", os.path.relpath(p, ROOT))
