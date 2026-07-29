#!/usr/bin/env python3
"""Extrae los fondos 1080x1350 para los posts de feed desde los visualizers 4K.

Paso SEPARADO de `make_posts.py` (que solo hace tipografia): esto necesita los
MP4 4K, que estan git-ignoreados. Los crops resultantes SI se commitean (chicos),
asi `make_posts.py` corre sin depender de los renders.

Cada entrada de FRAMES es (archivo, segundo, offset_x, slug). El offset_x es
sobre el 4K original (3840 de ancho); el crop es 1728x2160 (4:5) escalado a
1080x1350. offset 1056 = centrado.

Uso:  python3 scripts/make_post_backgrounds.py   -> redes/aem/social/_bg/*.jpg
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VID = os.path.join(ROOT, "transmissions/01/video/out")
OUTDIR = os.path.join(ROOT, "redes/aem/social/_bg")
os.makedirs(OUTDIR, exist_ok=True)

CROP_W, CROP_H = 1728, 2160  # 4:5 sobre el alto completo del 4K
CENTER_X = (3840 - CROP_W) // 2  # 1056

# (video, segundo, offset_x, slug)  — momentos elegidos a ojo sobre contact sheet
FRAMES = [
    ("1-outbound_v24_60fps.mp4", 30, CENTER_X, "limb"),        # limbo del planeta + estrellas
    ("1-outbound_v24_60fps.mp4", 120, CENTER_X, "core"),       # nucleo de luz + anillos
    ("1-outbound_v24_60fps.mp4", 300, CENTER_X, "mandala"),    # flor/mandala blanquecina (la mas clara)
    ("1-outbound_v24_60fps.mp4", 380, CENTER_X, "eye"),        # iris con radios (el "ovulo")
    ("2-crossing_v7_60fps.mp4", 350, CENTER_X, "lace"),        # encaje fractal con hueco negro
    ("3-recursion_v3_60fps.mp4", 20, CENTER_X, "curl"),        # turbulencia rizada
    ("3-recursion_v3_60fps.mp4", 100, CENTER_X, "cells"),      # celulas / burbujas concentricas
    ("3-recursion_v3_60fps.mp4", 60, CENTER_X, "rays"),        # rayos convergentes
    ("3-recursion_v3_60fps.mp4", 140, CENTER_X, "iris"),       # circulos concentricos
]


def extract(video, second, offset_x, slug):
    src = os.path.join(VID, video)
    if not os.path.exists(src):
        print(f"!! falta {video} (render 4K git-ignoreado) — se saltea {slug}")
        return None
    dst = os.path.join(OUTDIR, f"bg_{slug}.jpg")
    vf = f"crop={CROP_W}:{CROP_H}:{offset_x}:0,scale=1080:1350"
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", str(second),
           "-i", src, "-frames:v", "1", "-vf", vf, "-q:v", "3", dst, "-y"]
    subprocess.run(cmd, check=True)
    print("->", os.path.relpath(dst, ROOT), f"({os.path.getsize(dst) // 1024} KB)")
    return dst


if __name__ == "__main__":
    for video, second, offset_x, slug in FRAMES:
        extract(video, second, offset_x, slug)
