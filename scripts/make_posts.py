#!/usr/bin/env python3
"""Genera los posts estáticos de fragmento (modo B) para IG feed.

Template aprobado: fragmento cifrado en font Atari CRT (fósforo, bone-white,
scanlines + glow) sobre fondo plano de marca, con la marca hexagrama + un
readout "AEM · HELIOPAUSE · SPIRAL OUT". 1080×1350 (IG portrait).

Fragmentos: de transmissions/01/release/textos.md (mezcla ES/EN — el playbook
permite publicar en idiomas distintos). Font: EightBit Atari (real 8-bit),
esperada en /tmp/EightBitAtari.ttf (o pasar por env FONT).

Uso:  python3 scripts/make_posts.py    → escribe redes/aem/social/post_NN.png
"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.environ.get("FONT", "/tmp/EightBitAtari.ttf")
HEX = os.path.join(ROOT, "transmissions/01/artwork/hexagram/hexagram_24_avatar_1024.png")
OUTDIR = os.path.join(ROOT, "redes/aem/social")
os.makedirs(OUTDIR, exist_ok=True)

W, H = 1080, 1350
BG = (13, 16, 20)
INK = (228, 232, 214)  # bone white fósforo

# Fragmentos curados (de textos.md §4/§5.4) — mezcla ES/EN
FRAGMENTS = [
    "no es lo que mandamos. es lo que volvió.",
    "what returned is not what we sent.",
    "la espiral no asciende: evoluciona sin volver a ser la misma.",
    "salir, en rigor, fue el verbo que lo inventó.",
    "the wind that had been pushing ceased to push.",
    "una onda no atraviesa un medio: es el medio atravesándose.",
    "lo que estaba pasando no se cerraba: caracoleaba.",
    "a note, while heard, forgets it was ever a note.",
    "avanzar sin cambio es la única forma estable de existir.",
]


def make_post(text, path):
    im = Image.new("RGB", (W, H), BG)
    noise = Image.effect_noise((W, H), 14).convert("L").point(lambda p: int((p - 128) * 0.12 + 128))
    im = ImageChops.overlay(im, Image.merge("RGB", (noise, noise, noise)))
    # fragmento (font chico -> nearest x2 = pixel Atari grande)
    S = 2; cw, ch = W // S, H // S
    tl = Image.new("RGB", (cw, ch), (0, 0, 0)); d = ImageDraw.Draw(tl)
    f = ImageFont.truetype(FONT, 26)
    lines = textwrap.wrap(text, 16)
    y = (ch - len(lines) * int(26 * 1.5)) // 2
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((cw - w) // 2, y), ln, font=f, fill=INK); y += int(26 * 1.5)
    tl = tl.resize((W, H), Image.NEAREST)
    sl = Image.new("L", (W, H), 255); ds = ImageDraw.Draw(sl)
    for yy in range(0, H, 4):
        ds.line([(0, yy), (W, yy)], fill=95)
    tl = ImageChops.multiply(tl, Image.merge("RGB", (sl, sl, sl)))
    glow = tl.filter(ImageFilter.GaussianBlur(7)).point(lambda p: int(p * 0.55))
    out = ImageChops.screen(im, glow)
    out = ImageChops.screen(out, tl.filter(ImageFilter.GaussianBlur(0.6))).convert("RGBA")
    # marca + readout
    if os.path.exists(HEX):
        hexi = Image.open(HEX).convert("RGBA").resize((90, 90))
        out.alpha_composite(hexi, ((W - 90) // 2, H - 170))
    d2 = ImageDraw.Draw(out); fs = ImageFont.truetype(FONT, 13)
    tag = "AEM . HELIOPAUSE . SPIRAL OUT"; w = d2.textlength(tag, font=fs)
    d2.text(((W - w) // 2, H - 60), tag, font=fs, fill=(120, 130, 120))
    out.convert("RGB").save(path)


if __name__ == "__main__":
    for i, frag in enumerate(FRAGMENTS, 1):
        p = os.path.join(OUTDIR, f"post_{i:02d}.png")
        make_post(frag, p)
        print("->", os.path.relpath(p, ROOT))
