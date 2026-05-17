"""Generate share images (OG, Instagram, Pinterest) for spiralout.space.

Produces TWO families:

  HOME (spiralout.space) — symbolic mark:
    Dotted spiral on the home background color with a subtle dual-radial
    gradient and the "spiral out" wordmark in Courier New (matching the
    home page's <h1>).

  AEM (spiralout.space/aem) — artist promo:
    The Heliopause album cover composited on the same dark background,
    with "ÆM — Heliopause / Transmission 01" caption.

Variants per family, sized for 2026 social specs:
  1200x630   — Open Graph (FB / LinkedIn / Discord / WhatsApp / Twitter / iMessage / Threads / Bluesky / Mastodon / Telegram)
  1080x1080  — Instagram feed square (also generic square fallback)
  1080x1350  — Instagram feed portrait (4:5, highest reach)
  1080x1920  — Instagram / TikTok story (9:16); safe area is the central 1080x1420
  1000x1500  — Pinterest pin (2:3)

Outputs:
  site/spiralout/og-home.{svg,jpg}                  (1200x630, primary OG)
  site/spiralout/share/home-{variant}.{svg,jpg}
  site/spiralout/aem/og-image-wide.{svg,jpg}        (1200x630, primary OG)
  site/spiralout/aem/share/aem-{variant}.{svg,jpg}

Requires: rsvg-convert + ImageMagick (`magick`) on PATH.
The /aem album cover JPG must exist at:
  transmissions/01/artwork/cover_1500.jpg   (preferred — small, sharp)
or transmissions/01/artwork/cover_streaming_3000.jpg
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "spiralout"
ART_DIR = ROOT / "transmissions" / "01" / "artwork"

# ---- spiral geometry ---------------------------------------------------------
# Dot positions copied from site/spiralout/index.html (the live home spiral).
# Each tuple is (cx, cy, r) in "spiral units"; the actual pixel size is set by
# a per-variant scale + translate.
SPIRAL_DOTS: list[tuple[float, float, float]] = [
    (0.40, 0.00, 0.40), (0.40, 0.13, 0.41), (0.36, 0.26, 0.42),
    (0.28, 0.38, 0.42), (0.15, 0.48, 0.43), (0.00, 0.53, 0.44),
    (-0.17, 0.53, 0.45), (-0.35, 0.48, 0.45), (-0.51, 0.37, 0.46),
    (-0.63, 0.21, 0.47), (-0.70, 0.00, 0.48), (-0.71, -0.23, 0.48),
    (-0.64, -0.46, 0.49), (-0.49, -0.67, 0.50), (-0.27, -0.84, 0.51),
    (-0.00, -0.93, 0.51), (0.31, -0.94, 0.52), (0.61, -0.85, 0.53),
    (0.90, -0.65, 0.54), (1.11, -0.36, 0.54), (1.24, -0.00, 0.55),
    (1.25, 0.41, 0.56), (1.12, 0.82, 0.57), (0.86, 1.19, 0.57),
    (0.48, 1.48, 0.58), (0.00, 1.64, 0.59), (-0.54, 1.65, 0.59),
    (-1.08, 1.49, 0.60), (-1.58, 1.15, 0.61), (-1.96, 0.64, 0.62),
    (-2.18, 0.00, 0.62), (-2.20, -0.71, 0.63), (-1.98, -1.44, 0.64),
    (-1.52, -2.09, 0.65), (-0.85, -2.60, 0.66), (-0.00, -2.89, 0.66),
    (0.95, -2.91, 0.67), (1.91, -2.62, 0.68), (2.77, -2.02, 0.69),
    (3.45, -1.12, 0.69), (3.84, -0.00, 0.70), (3.87, 1.26, 0.71),
    (3.48, 2.53, 0.72), (2.67, 3.68, 0.72), (1.49, 4.58, 0.73),
    (0.00, 5.10, 0.74), (-1.67, 5.13, 0.74), (-3.35, 4.62, 0.75),
    (-4.88, 3.55, 0.76), (-6.08, 1.97, 0.77), (-6.76, 0.00, 0.78),
    (-6.80, -2.21, 0.78), (-6.12, -4.45, 0.79), (-4.71, -6.48, 0.80),
    (-2.62, -8.06, 0.81), (-0.00, -8.97, 0.81), (2.93, -9.03, 0.82),
    (5.90, -8.13, 0.83), (8.60, -6.25, 0.83), (10.70, -3.48, 0.84),
    (11.90, -0.00, 0.85), (11.98, 3.89, 0.86), (10.78, 7.83, 0.86),
    (8.29, 11.41, 0.87), (4.61, 14.19, 0.88), (-0.00, 15.79, 0.89),
    (-5.16, 15.89, 0.90), (-10.39, 14.30, 0.90), (-15.14, 11.00, 0.91),
    (-18.83, 6.12, 0.92), (-20.95, 0.00, 0.93), (-21.08, -6.85, 0.93),
    (-18.98, -13.79, 0.94), (-14.59, -20.08, 0.95), (-8.12, -24.98, 0.96),
    (-0.00, -27.80, 0.96), (9.09, -27.97, 0.97), (18.29, -25.18, 0.98),
    (26.64, -19.36, 0.98), (33.14, -10.77, 0.99),
]

# ---- color palette (mirrors site/spiralout/index.html :root) ----------------
BG      = "#0a0a0c"
FG      = "#cfcfd2"
MUTED   = "#7a7a84"   # spiral fill & tagline color (slightly lighter than --muted #555560 for share visibility)
HAZE_A  = "#503c5a"   # purple haze (top-left)
HAZE_B  = "#283250"   # blue haze (bottom-right)

# ---- SVG building blocks ----------------------------------------------------

DEFS = """  <defs>
    <!-- Mirrors the home page CSS:
           radial-gradient(ellipse at 30% 20%, rgba(80,60,90,0.15) 0%, transparent 50%),
           radial-gradient(ellipse at 70% 80%, rgba(40,50,80,0.12) 0%, transparent 55%)
         Ellipses sized larger than the spec because rsvg + JPG flatten the
         softest tail of the gradient — slightly higher alpha + wider falloff
         keeps it perceptible without becoming heavy. -->
    <radialGradient id="haze-purple" cx="30%" cy="20%" r="65%" fx="30%" fy="20%">
      <stop offset="0%"   stop-color="{HAZE_A}" stop-opacity="0.35" />
      <stop offset="50%"  stop-color="{HAZE_A}" stop-opacity="0.08" />
      <stop offset="100%" stop-color="{HAZE_A}" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="haze-blue" cx="70%" cy="80%" r="65%" fx="70%" fy="80%">
      <stop offset="0%"   stop-color="{HAZE_B}" stop-opacity="0.30" />
      <stop offset="55%"  stop-color="{HAZE_B}" stop-opacity="0.06" />
      <stop offset="100%" stop-color="{HAZE_B}" stop-opacity="0" />
    </radialGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feColorMatrix in="blur" type="matrix"
        values="1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0
                0 0 0 0.40 0" result="softGlow" />
      <feMerge>
        <feMergeNode in="softGlow" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>"""


def background_rects(w: int, h: int) -> str:
    # Base color + the two radial hazes. No vignette: it was muting the hazes.
    return (
        f'  <rect width="{w}" height="{h}" fill="{BG}" />\n'
        f'  <rect width="{w}" height="{h}" fill="url(#haze-purple)" />\n'
        f'  <rect width="{w}" height="{h}" fill="url(#haze-blue)" />'
    )


def spiral_group(cx: float, cy: float, scale: float, opacity: float = 0.78) -> str:
    circles = "\n".join(
        f'    <circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}"/>'
        for x, y, r in SPIRAL_DOTS
    )
    return (
        f'  <g transform="translate({cx} {cy}) scale({scale})" '
        f'filter="url(#glow)" fill="#8a7a90" fill-opacity="{opacity}">\n'
        f"{circles}\n"
        f"  </g>"
    )


def text(x: float, y: float, content: str, *, size: int, ls: float = 0,
         color: str = FG, italic: bool = False, weight: str = "300",
         anchor: str = "middle", preserve: bool = False) -> str:
    """Build an SVG <text>. Set preserve=True for content that relies on
    runs of multiple spaces (SVG collapses whitespace by default — without
    xml:space=preserve, "a   b" renders as "a b").
    """
    style = ' font-style="italic"' if italic else ""
    space = ' xml:space="preserve"' if preserve else ""
    return (
        f'  <text x="{x}" y="{y}" '
        f'font-family="\'Courier New\', Courier, ui-monospace, monospace" '
        f'font-weight="{weight}" font-size="{size}" letter-spacing="{ls}" '
        f'fill="{color}" text-anchor="{anchor}"{style}{space}>{content}</text>'
    )


def svg_header(w: int, h: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n\n'
        f"{DEFS.format(HAZE_A=HAZE_A, HAZE_B=HAZE_B, BG=BG)}\n\n"
        f"{background_rects(w, h)}\n"
    )


# ---- home family ------------------------------------------------------------

@dataclass(frozen=True)
class Variant:
    name: str
    w: int
    h: int
    layout: str   # "wide" | "stack"


HOME_VARIANTS: list[Variant] = [
    Variant("og",        1200,  630, "wide"),
    Variant("square",    1080, 1080, "stack"),
    Variant("portrait",  1080, 1350, "stack"),
    Variant("story",     1080, 1920, "stack"),
    Variant("pinterest", 1000, 1500, "stack"),
]


def build_home_svg(v: Variant) -> str:
    """Logo composition: spiral + 'spiral out' wordmark, on ONE line, no
    subtitle. Visually centered. Spiral and text must not touch.
    """
    title = "Spiral Out"
    desc = (
        "Dotted spiral mark next to the 'spiral out' wordmark on a dark "
        "atmospheric background with a subtle radial gradient."
    )
    body = [svg_header(v.w, v.h, title, desc)]

    # The dotted spiral has an asymmetric bounding box in "spiral units":
    #   x: [-21.08, 33.14]  → width  ≈ 54.22, box-center at x = +6.03
    #   y: [-27.97, 15.89]  → height ≈ 43.86, box-center at y = -6.04
    # The <g transform="translate(ox oy) scale(s)"> puts the spiral's (0,0)
    # at (ox, oy). To center the *bounding box* on a target point we offset
    # the origin by -(box_center * scale).
    SP_W, SP_H = 54.22, 43.86
    SP_BOX_CX = 6.03   # box center x in spiral units
    SP_BOX_CY = -6.04  # box center y in spiral units

    def place_spiral(target_cx: float, target_cy: float, scale: float) -> str:
        ox = target_cx - SP_BOX_CX * scale
        oy = target_cy - SP_BOX_CY * scale
        return spiral_group(ox, oy, scale)

    cx = v.w / 2
    cy = v.h / 2

    # Wordmark — EXACT match to home <h1>:
    #   <span>s p i r a l</span><span style="margin-left:2em">o u t</span>
    #   + CSS letter-spacing: 0.4em
    # Each letter is pre-spaced with a real space char, plus we add SVG
    # letter-spacing 0.4em on top. Three spaces between "spiral" and "out"
    # encode the 2em + letter-spacing gap. SVG collapses whitespace by
    # default — preserve=True is mandatory.
    WORDMARK = "s p i r a l   o u t"             # 19 chars (incl. 3 inner spaces)
    LS_RATIO = 0.40                              # CSS letter-spacing 0.4em
    # Courier glyph advance ≈ 0.6 × font_size; 19 glyphs + 18 letter-spacings.
    WIDTH_FACTOR = 19 * 0.6 + 18 * LS_RATIO      # = 18.6

    def wordmark_width(font_size: float) -> float:
        return WIDTH_FACTOR * font_size

    def fit_font_size(max_w: float, *, min_fs: int = 18, max_fs: int = 96) -> int:
        for fs in range(max_fs, min_fs - 1, -1):
            if wordmark_width(fs) <= max_w:
                return fs
        return min_fs

    if v.layout == "wide":
        # 1200x630: spiral on the left, wordmark on the right, ONE line.
        # The spiral has *outlying* dots on its outer arm that stick out
        # further than the inner body — measuring the gutter only from the
        # bounding-box edge leaves an isolated dot too close to the text.
        # We use a big breathing gutter (140) and let the wordmark shrink
        # to fit. Per user feedback 2026-05-16.
        spiral_scale = 4.8
        sp_box_w = SP_W * spiral_scale            # ≈ 260
        gutter = 140

        # Comp at ~84% of canvas width → margins ~95 px each side.
        target_comp_w = v.w * 0.84
        font_size = fit_font_size(target_comp_w - sp_box_w - gutter,
                                  min_fs=24, max_fs=44)
        wm_w = wordmark_width(font_size)
        ls = font_size * LS_RATIO

        comp_w = sp_box_w + gutter + wm_w
        left = (v.w - comp_w) / 2

        body.append(place_spiral(left + sp_box_w / 2, cy, spiral_scale))
        body.append(text(left + sp_box_w + gutter + wm_w / 2,
                         cy + font_size * 0.35, WORDMARK,
                         size=font_size, ls=ls, preserve=True))
    else:
        # Stacked: spiral on top, wordmark on a single line below — both
        # horizontally centered, vertically balanced with breathing room.
        # The airy home spacing dictates a smaller font here than a tight
        # spacing would allow, but stacked canvases give us plenty of room.
        target_wm_w = v.w * 0.78
        font_size = fit_font_size(target_wm_w, min_fs=28, max_fs=80)
        ls = font_size * LS_RATIO

        gap = max(80, int(v.h * 0.06))

        spiral_box_max_w = v.w * 0.50
        spiral_box_max_h = v.h * 0.50
        spiral_scale = min(spiral_box_max_w / SP_W, spiral_box_max_h / SP_H)
        sp_box_h = SP_H * spiral_scale

        # Center the (spiral + gap + wordmark) cluster on the canvas.
        cluster_h = sp_box_h + gap + font_size
        cluster_top = (v.h - cluster_h) / 2

        spiral_box_center_y = cluster_top + sp_box_h / 2
        body.append(place_spiral(cx, spiral_box_center_y, spiral_scale))

        wordmark_baseline_y = cluster_top + sp_box_h + gap + font_size * 0.85
        body.append(text(cx, wordmark_baseline_y, WORDMARK,
                         size=font_size, ls=ls, preserve=True))

    body.append("</svg>\n")
    return "\n".join(body)


# ---- aem family --------------------------------------------------------------

def _find_album_cover() -> Path:
    candidates = [
        ART_DIR / "cover_1500.jpg",
        ART_DIR / "cover_streaming_3000.jpg",
        SITE / "aem" / "cover.jpg",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "Album cover not found. Tried: " + ", ".join(str(c) for c in candidates)
    )


def _embed_image(path: Path) -> str:
    """Embed a JPG as a base64 data URI so the SVG is self-contained."""
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{data}"


AEM_VARIANTS: list[Variant] = [
    Variant("og",        1200,  630, "wide"),
    Variant("square",    1080, 1080, "stack"),
    Variant("portrait",  1080, 1350, "stack"),
    Variant("story",     1080, 1920, "stack"),
    Variant("pinterest", 1000, 1500, "stack"),
]


def build_aem_svg(v: Variant, cover_uri: str) -> str:
    """The album cover is the hero. Layout is minimal: cover front-and-center,
    a small wordmark/caption only where there's vertical room (stacked variants).
    """
    title = "ÆM — Heliopause / Transmission 01"
    desc = (
        "Heliopause album cover by ÆM, released on Spiral Out."
    )
    body = [svg_header(v.w, v.h, title, desc)]

    cx = v.w / 2

    if v.layout == "wide":
        # 1200x630: cover centered-left, title block centered-right.
        # Cover sized to fit height with comfortable vertical margin.
        margin = 70
        cover_size = v.h - 2 * margin                # 490 on 1200x630
        cover_x = 80                                  # left margin
        cover_y = (v.h - cover_size) // 2
        body.append(
            f'  <image href="{cover_uri}" x="{cover_x}" y="{cover_y}" '
            f'width="{cover_size}" height="{cover_size}" preserveAspectRatio="xMidYMid slice" />'
        )
        body.append(
            f'  <rect x="{cover_x}" y="{cover_y}" width="{cover_size}" '
            f'height="{cover_size}" fill="none" stroke="#1f1f24" stroke-width="2" />'
        )

        # Title block — right of cover, vertically centered.
        text_x = cover_x + cover_size + 90            # 660
        body.append(text(text_x, 260, "ÆM",              size=62, ls=14,
                         anchor="start"))
        body.append(text(text_x, 340, "heliopause",      size=42, ls=8,
                         anchor="start"))
        body.append(text(text_x, 392, "transmission 01", size=20, ls=6,
                         color=MUTED, anchor="start"))
        body.append(text(text_x, 488, "spiralout.space/aem",
                         size=16, ls=4, color=MUTED, anchor="start"))
    elif v.w == v.h:
        # 1080x1080 — cover ONLY, edge-to-edge with a tiny inset for the
        # dark border. The album art is itself square and contains all the
        # branding (ÆM, title, tracklist), so we trust the art and ship clean.
        inset = 30
        size = v.w - 2 * inset
        body.append(
            f'  <image href="{cover_uri}" x="{inset}" y="{inset}" '
            f'width="{size}" height="{size}" preserveAspectRatio="xMidYMid slice" />'
        )
        body.append(
            f'  <rect x="{inset}" y="{inset}" width="{size}" height="{size}" '
            f'fill="none" stroke="#1f1f24" stroke-width="2" />'
        )
    else:
        # Portrait, story, pinterest: cover at top, caption stack below.
        # Sizes are auto-fit so the caption stack always lands inside the
        # canvas with safe bottom margin (≥80px) and respects the story UI
        # safe area (top 250px clear).
        bottom_margin = 80
        top_margin = 280 if v.h >= 1920 else int(v.h * 0.10)

        # Reserve space for caption stack first, then size the cover.
        size_title = max(50, int(v.w / 17))           # ÆM
        size_album = int(size_title * 0.80)           # heliopause
        size_meta  = max(20, int(size_title * 0.34))  # transmission 01
        size_url   = max(18, int(size_title * 0.28))  # spiralout.space/aem
        # Vertical rhythm
        gap_after_cover = int(v.h * 0.055)
        gap_1 = int(size_title * 0.55)                # ÆM → heliopause
        gap_2 = int(size_album * 0.65)                # heliopause → transmission
        gap_3 = int(size_meta * 1.6)                  # transmission → url
        caption_h = size_title + gap_1 + size_album + gap_2 + size_meta + gap_3 + size_url

        max_cover_by_h = v.h - top_margin - gap_after_cover - caption_h - bottom_margin
        cover_size = int(min(v.w * 0.84, max_cover_by_h))
        cover_x = int(cx - cover_size / 2)
        cover_y = top_margin

        body.append(
            f'  <image href="{cover_uri}" x="{cover_x}" y="{cover_y}" '
            f'width="{cover_size}" height="{cover_size}" preserveAspectRatio="xMidYMid slice" />'
        )
        body.append(
            f'  <rect x="{cover_x}" y="{cover_y}" width="{cover_size}" '
            f'height="{cover_size}" fill="none" stroke="#1f1f24" stroke-width="2" />'
        )

        y0 = cover_y + cover_size + gap_after_cover + size_title
        body.append(text(cx, y0, "ÆM",
                         size=size_title, ls=int(size_title * 0.18)))
        y1 = y0 + gap_1 + size_album
        body.append(text(cx, y1, "heliopause",
                         size=size_album, ls=int(size_album * 0.14)))
        y2 = y1 + gap_2 + size_meta
        body.append(text(cx, y2, "transmission 01",
                         size=size_meta, ls=6, color=MUTED))
        y3 = y2 + gap_3 + size_url
        body.append(text(cx, y3, "spiralout.space/aem",
                         size=size_url, ls=4, color=MUTED))

    body.append("</svg>\n")
    return "\n".join(body)


# ---- render pipeline --------------------------------------------------------

def have(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def svg_to_jpg(svg_path: Path, jpg_path: Path, w: int, h: int) -> None:
    """Rasterize SVG via rsvg-convert and convert to a web-optimized JPG."""
    tmp_png = jpg_path.with_suffix(".tmp.png")
    subprocess.run(
        ["rsvg-convert", "-w", str(w), "-h", str(h),
         str(svg_path), "-o", str(tmp_png)],
        check=True,
    )
    subprocess.run(
        ["magick", str(tmp_png), "-strip", "-quality", "85",
         "-interlace", "Plane", str(jpg_path)],
        check=True,
    )
    tmp_png.unlink(missing_ok=True)


def write_variant(svg: str, svg_path: Path, jpg_path: Path, w: int, h: int) -> None:
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg)
    svg_to_jpg(svg_path, jpg_path, w, h)
    print(f"  ✓ {jpg_path.relative_to(ROOT)}  ({jpg_path.stat().st_size // 1024} KB)")


def main() -> int:
    if not (have("rsvg-convert") and have("magick")):
        print("ERROR: requires rsvg-convert and ImageMagick on PATH.", file=sys.stderr)
        return 1

    print("→ home family")
    for v in HOME_VARIANTS:
        svg = build_home_svg(v)
        if v.name == "og":
            svg_path = SITE / "og-home.svg"
            jpg_path = SITE / "og-home.jpg"
        else:
            svg_path = SITE / "share" / f"home-{v.name}.svg"
            jpg_path = SITE / "share" / f"home-{v.name}.jpg"
        write_variant(svg, svg_path, jpg_path, v.w, v.h)

    print("→ aem family")
    cover = _find_album_cover()
    print(f"  using album cover: {cover.relative_to(ROOT)}")
    cover_uri = _embed_image(cover)
    for v in AEM_VARIANTS:
        svg = build_aem_svg(v, cover_uri)
        if v.name == "og":
            svg_path = SITE / "aem" / "og-image-wide.svg"
            jpg_path = SITE / "aem" / "og-image-wide.jpg"
        else:
            svg_path = SITE / "aem" / "share" / f"aem-{v.name}.svg"
            jpg_path = SITE / "aem" / "share" / f"aem-{v.name}.jpg"
        write_variant(svg, svg_path, jpg_path, v.w, v.h)

    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
