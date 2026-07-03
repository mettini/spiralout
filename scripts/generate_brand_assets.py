"""Generate the Spiral Out brand asset pack under `redes/spiral-out/`.

Reuses the visual language from `scripts/generate_share_images.py`
(palette, spiral geometry, hazes, glow, Courier wordmark) so every
output is brand-coherent.

Outputs (Spiral Out only — ÆM cover-based assets are populated by a
sibling step in `task site:redes`):

  redes/spiral-out/
  ├── iso/                    ← just the dotted spiral mark
  │   ├── iso_transparent.svg
  │   ├── iso_transparent_512.png
  │   ├── iso_transparent_1024.png
  │   ├── iso_transparent_2048.png
  │   ├── iso_on_brand.svg
  │   ├── iso_on_brand_1024.png
  │   └── iso_on_brand_2048.png
  ├── logo/                   ← spiral + 'spiral out' wordmark
  │   ├── logo_horizontal_transparent.svg
  │   ├── logo_horizontal_on_brand.svg
  │   ├── logo_horizontal_on_brand_1920x480.png
  │   ├── logo_stacked_transparent.svg
  │   ├── logo_stacked_on_brand.svg
  │   └── logo_stacked_on_brand_1080x1080.png
  ├── avatar/                 ← PFP-ready (safe area for circle crop)
  │   ├── pfp_iso_1024.png
  │   ├── pfp_iso_512.png
  │   └── pfp_stacked_1024.png
  ├── hero/                   ← thematic backgrounds (no text, or minimal)
  │   ├── hero_16x9_1920x1080.jpg
  │   ├── hero_youtube_2560x1440.jpg
  │   ├── hero_x_bluesky_1500x500.jpg
  │   ├── hero_bandcamp_2400x460.png
  │   └── hero_soundcloud_2480x520.jpg
  └── posts/                  ← branded post-ready (with logo composed)
      ├── post_square_1080.jpg
      ├── post_portrait_1080x1350.jpg
      ├── post_story_1080x1920.jpg
      ├── post_pinterest_1000x1500.jpg
      └── og_1200x630.jpg
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Reuse brand primitives.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_share_images import (  # noqa: E402
    BG, FG, MUTED, HAZE_A, HAZE_B,
    DEFS, background_rects, spiral_group, text, svg_header,
    svg_to_jpg, write_variant, have,
    SPIRAL_DOTS,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "redes" / "spiral-out"

# Spiral bounding box (matches generate_share_images.py) — CENTERS only.
SP_W = 54.22
SP_H = 43.86
SP_BOX_CX = 6.03
SP_BOX_CY = -6.04

# True VISUAL extent of the spiral (per axis, in spiral units): includes
# each dot's radius (~max 1.0) plus a small ~0.5 buffer for the gaussian
# glow. Use these for collision / padding math — NOT the SP_W/SP_H above,
# which only cover dot centers and underestimate the bounding box.
SP_VIS_X_LEFT  = 22.1   # |min x center| (~ 21.08) + dot r (~1) + glow buffer
SP_VIS_X_RIGHT = 34.1   # max x center (~ 33.14) + dot r + glow
SP_VIS_Y_TOP   = 29.0   # |min y center| (~ 27.97) + dot r + glow
SP_VIS_Y_BOT   = 16.9   # max y center (~ 15.89) + dot r + glow
SP_VIS_W = SP_VIS_X_LEFT + SP_VIS_X_RIGHT   # 56.2
SP_VIS_H = SP_VIS_Y_TOP + SP_VIS_Y_BOT      # 45.9

WORDMARK = "s p i r a l   o u t"
LS_RATIO = 0.40
WIDTH_FACTOR = 19 * 0.6 + 18 * LS_RATIO  # ≈ 18.6

# ── Brand spacing constants ────────────────────────────────────────────
# Every layout is computed from these. Change them once → everything reflows.
#
# Naming: *_RATIO is "fraction of the relevant canvas dimension". Vertical
# pads use canvas height; horizontal use canvas width; gaps use the axis
# perpendicular to the stacking.

# ISO logo — JUST the spiral mark. Padding is what the user perceives as
# "the empty rim around the mark". We want presence — the mark should fill
# the canvas confidently, not float in a sea of black.
ISO_PAD_RATIO = 0.08

# PFP iso — circular-crop, vortex-centered.
#
# The spiral is highly asymmetric: the outer arm extends much further from
# the vortex (origin) than the inner arm. If we center by visual bounding
# box, the vortex sits visibly off-center inside the inscribed circle and
# outliers from the longest arm clip the circle border.
#
# For an avatar the user reads the SPIRAL EYE as the logical center — so
# we center by origin (vortex at canvas center) and scale by the longest
# radial distance from the vortex, leaving a uniform breathing margin
# around every dot (no matter which arm it sits on).
#
# PFP_TARGET_RADIAL_RATIO: the max-distance dot lands at this fraction of
# the inscribed circle radius. 0.75 = ~25% breathing margin around the
# outermost dot — visually generous, looks like a proper avatar logo at
# every thumbnail size (32-110 px).
PFP_TARGET_RADIAL_RATIO = 0.75

# Cached longest radial distance from origin to any dot edge.
# Used to scale the PFP iso variant.
_MAX_RADIAL = max(math.sqrt(x * x + y * y) + r for x, y, r in SPIRAL_DOTS)

# Optical (mass-weighted) centroid of the spiral, weighting each dot by
# its area (r²). The spiral is asymmetric: dots in the long outer arm have
# bigger radii and pull the perceived center away from the vortex (origin).
# For the PFP we place THIS centroid at the canvas center — the avatar
# reads as visually balanced regardless of the spiral's asymmetry.
_W_TOTAL    = sum(r * r for _, _, r in SPIRAL_DOTS)
_CENTROID_X = sum(x * r * r for x, _, r in SPIRAL_DOTS) / _W_TOTAL
_CENTROID_Y = sum(y * r * r for _, y, r in SPIRAL_DOTS) / _W_TOTAL

# Longest radial distance FROM THE CENTROID to any dot edge. Used to
# size the PFP so every dot stays inside the circle with breathing room.
_MAX_RADIAL_FROM_CENTROID = max(
    math.sqrt((x - _CENTROID_X) ** 2 + (y - _CENTROID_Y) ** 2) + r
    for x, y, r in SPIRAL_DOTS
)

# PFP-tuned colors — overrides the default brand palette specifically for
# avatars. The site palette (`#0a0a0c` bg + soft gradients) blends with
# IG/X dark-mode backgrounds; the spiral mark at α 0.78 reads as muted
# grey at thumbnail size. PFP variant uses a slightly chromatic purple
# base + stronger hazes + brighter mark fill (mirrors `favicon.svg`).
PFP_BG       = "#15101c"   # dark indigo-purple (vs #0a0a0c near-black)
PFP_MARK     = "#a89ab0"   # brighter mark (matches favicon.svg stroke)
PFP_HAZE_A_A = 0.55        # alpha for the purple haze (vs 0.35)
PFP_HAZE_B_A = 0.45        # alpha for the blue haze (vs 0.30)

# Stacked composition (iso ON TOP, wordmark BELOW). Used by:
#   - logo_stacked_* (1080² brand-color or transparent)
#   - pfp_stacked_*  (1024² PFP variant)
#   - posts (square / portrait / story / pinterest)
STACKED_PAD_X_RATIO = 0.10
STACKED_PAD_Y_RATIO = 0.10
STACKED_GAP_RATIO   = 0.10   # vertical gap (× canvas h) iso ↔ wordmark
STACKED_FONT_RATIO  = 0.045  # font_size as fraction of canvas h (cap)

# Horizontal composition (iso LEFT, wordmark RIGHT, on one line).
# Used by logo_horizontal_* and the wide hero/OG.
HORIZONTAL_PAD_X_RATIO = 0.07
HORIZONTAL_PAD_Y_RATIO = 0.18
HORIZONTAL_GUTTER_RATIO = 0.08  # × canvas w, the empty zone between iso & wm

# Wide banner (X/Bluesky header, Bandcamp, SoundCloud — w/h >= 3).
# Wordmark dominant left, spiral accent right; explicit edge margins.
BANNER_PAD_X_RATIO = 0.06
BANNER_PAD_Y_RATIO = 0.16
BANNER_GUTTER_RATIO = 0.06  # × canvas w


def _fit_font_size(max_w: float, *, h: float, ratio_cap: float,
                   min_fs: int = 18) -> int:
    """Largest int font_size such that wordmark_width(fs) <= max_w AND
    fs <= h * ratio_cap. Returns at least min_fs."""
    by_w = int(max_w / WIDTH_FACTOR)
    by_h = int(h * ratio_cap)
    return max(min_fs, min(by_w, by_h))


def place_spiral(target_cx: float, target_cy: float, scale: float,
                 opacity: float = 0.78, center_by: str = "vbbox") -> str:
    """Place the spiral with its center at (target_cx, target_cy).

    center_by (default 'vbbox'):
      'vbbox'  — center of the VISUAL bounding box (dot centers + radii +
                 glow buffer). This is the convention used by the original
                 site OG (og-home.svg) and gives symmetric visual padding
                 around the spiral. DEFAULT — use this for any composition.
      'bbox'   — center the dot-centers bbox (ignores radii). Almost
                 identical to 'vbbox' (~0.3 px diff at scale 10).
      'origin' — center the spiral's own origin (0,0). The vortex sits at
                 the target. Visual bbox is NOT centered — outliers extend
                 mostly up-right. Only use when intentional.
    """
    if center_by == "origin":
        return spiral_group(target_cx, target_cy, scale, opacity=opacity)
    if center_by == "vbbox":
        vis_cx = (SP_VIS_X_RIGHT - SP_VIS_X_LEFT) / 2   # +6.0
        vis_cy = (SP_VIS_Y_BOT - SP_VIS_Y_TOP) / 2      # -6.05
        ox = target_cx - vis_cx * scale
        oy = target_cy - vis_cy * scale
        return spiral_group(ox, oy, scale, opacity=opacity)
    # 'bbox' fallback: bbox of dot CENTERS (no radii). Kept for parity
    # with generate_share_images.py.
    ox = target_cx - SP_BOX_CX * scale
    oy = target_cy - SP_BOX_CY * scale
    return spiral_group(ox, oy, scale, opacity=opacity)


def wordmark_width(font_size: float) -> float:
    return WIDTH_FACTOR * font_size


def svg_open_transparent(w: int, h: int, title: str, desc: str) -> str:
    """Same header as svg_header() but WITHOUT the background rects so the
    PNG output has transparent areas where the bg would be."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n\n'
        f"{DEFS.format(HAZE_A=HAZE_A, HAZE_B=HAZE_B, BG=BG)}\n\n"
    )


def svg_open_on_brand(w: int, h: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n\n'
        f"{DEFS.format(HAZE_A=HAZE_A, HAZE_B=HAZE_B, BG=BG)}\n\n"
        f"{background_rects(w, h)}\n"
    )


# ----------------------- ISO (just the spiral mark) ------------------------

def build_iso(w: int, h: int, *, transparent: bool,
              padding_ratio: float = ISO_PAD_RATIO) -> str:
    """Dotted spiral mark, centered by its OPTICAL center, scaled so the
    full visual extent (dots + glow) fills the padded canvas tightly.

    Centering: the spiral is asymmetric — origin-centered puts the vortex
    at the canvas center but the cola of outliers extends mostly up-right,
    leaving the bottom-left visually emptier. We center on the *midpoint
    of the visual bbox* instead, so the mark sits visually balanced in the
    canvas rectangle.
    """
    title = "Spiral Out"
    desc = "Dotted spiral logo mark."
    body = [svg_open_transparent(w, h, title, desc) if transparent
            else svg_open_on_brand(w, h, title, desc)]
    avail_w = w * (1 - 2 * padding_ratio)
    avail_h = h * (1 - 2 * padding_ratio)
    scale = min(avail_w / SP_VIS_W, avail_h / SP_VIS_H)
    body.append(place_spiral(w / 2, h / 2, scale))   # default: vbbox-center
    body.append("</svg>\n")
    return "\n".join(body)


def build_pfp_iso(w: int, h: int) -> str:
    """PFP-tuned iso mark: tighter padding + bumped contrast for IG/X dark
    mode. Uses PFP_* color overrides (brighter mark, deeper-purple bg,
    stronger hazes) so the avatar reads at 32-110 px thumbnail sizes.
    """
    title = "Spiral Out"
    desc = "Dotted spiral logo mark — PFP variant."

    # Custom DEFS — punched-up gradients (vs site OG soft hazes).
    pfp_defs = f"""  <defs>
    <radialGradient id="pfp-haze-purple" cx="30%" cy="20%" r="75%" fx="30%" fy="20%">
      <stop offset="0%"   stop-color="#503c5a" stop-opacity="{PFP_HAZE_A_A}" />
      <stop offset="60%"  stop-color="#503c5a" stop-opacity="0.12" />
      <stop offset="100%" stop-color="#503c5a" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="pfp-haze-blue" cx="70%" cy="80%" r="75%" fx="70%" fy="80%">
      <stop offset="0%"   stop-color="#283250" stop-opacity="{PFP_HAZE_B_A}" />
      <stop offset="60%"  stop-color="#283250" stop-opacity="0.10" />
      <stop offset="100%" stop-color="#283250" stop-opacity="0" />
    </radialGradient>
    <filter id="pfp-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feColorMatrix in="blur" type="matrix"
        values="1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0
                0 0 0 0.55 0" result="softGlow" />
      <feMerge>
        <feMergeNode in="softGlow" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>"""

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{desc}</desc>\n\n'
        f'{pfp_defs}\n\n'
        f'  <rect width="{w}" height="{h}" fill="{PFP_BG}" />\n'
        f'  <rect width="{w}" height="{h}" fill="url(#pfp-haze-purple)" />\n'
        f'  <rect width="{w}" height="{h}" fill="url(#pfp-haze-blue)" />'
    ]

    # Optical centroid (mass-weighted) at canvas center; scale so the
    # furthest dot from THAT centroid sits at PFP_TARGET_RADIAL_RATIO of
    # the inscribed circle radius. The visual mass of the spiral lands at
    # the canvas center → balanced avatar despite the spiral's asymmetric
    # geometry. The vortex (origin) is offset slightly so the centroid
    # ends up at canvas center.
    inscribed_r = min(w, h) / 2
    scale = (inscribed_r * PFP_TARGET_RADIAL_RATIO) / _MAX_RADIAL_FROM_CENTROID
    ox = w / 2 - _CENTROID_X * scale
    oy = h / 2 - _CENTROID_Y * scale

    circles = "\n".join(
        f'    <circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}"/>'
        for x, y, r in SPIRAL_DOTS
    )
    body.append(
        f'  <g transform="translate({ox} {oy}) scale({scale})" '
        f'filter="url(#pfp-glow)" fill="{PFP_MARK}" fill-opacity="1.0">\n'
        f"{circles}\n"
        f"  </g>"
    )
    body.append("</svg>\n")
    return "\n".join(body)


# ----------------------- LOGO (spiral + wordmark) --------------------------

def build_logo_horizontal(w: int, h: int, *, transparent: bool) -> str:
    """Iso LEFT + gutter + wordmark RIGHT, single line. Cluster centered
    inside the safe rect (margins = HORIZONTAL_PAD_*_RATIO).
    """
    title = "Spiral Out — logo"
    desc = "Spiral mark with the 'spiral out' wordmark on one line."
    body = [svg_open_transparent(w, h, title, desc) if transparent
            else svg_open_on_brand(w, h, title, desc)]

    pad_x = w * HORIZONTAL_PAD_X_RATIO
    pad_y = h * HORIZONTAL_PAD_Y_RATIO
    box_w = w - 2 * pad_x
    box_h = h - 2 * pad_y
    gutter = w * HORIZONTAL_GUTTER_RATIO

    # Spiral fits the safe-rect height (visual extent — not bbox centers).
    spiral_scale = box_h / SP_VIS_H
    sp_vis_w = SP_VIS_W * spiral_scale

    max_text_w = box_w - sp_vis_w - gutter
    font_size = _fit_font_size(max_text_w, h=h, ratio_cap=0.42)
    wm_w = wordmark_width(font_size)
    ls = font_size * LS_RATIO

    cluster_w = sp_vis_w + gutter + wm_w
    left = pad_x + (box_w - cluster_w) / 2   # cluster centered in safe rect

    cy = h / 2
    # Visual-bbox-centered: spiral envelope spans [left, left + sp_vis_w]
    # horizontally and is vertically centered around cy.
    spiral_target_cx = left + sp_vis_w / 2
    body.append(place_spiral(spiral_target_cx, cy, spiral_scale))
    body.append(text(left + sp_vis_w + gutter + wm_w / 2,
                     cy + font_size * 0.35, WORDMARK,
                     size=font_size, ls=ls, preserve=True))
    body.append("</svg>\n")
    return "\n".join(body)


def build_logo_stacked(w: int, h: int, *, transparent: bool,
                       pad_y_ratio: float = STACKED_PAD_Y_RATIO,
                       gap_ratio: float = STACKED_GAP_RATIO,
                       font_ratio: float = STACKED_FONT_RATIO) -> str:
    """Iso TOP, wordmark BOTTOM, cluster centered in the safe rect.
    Uses STACKED_*_RATIO constants. Reused by logo, pfp, and posts.
    """
    title = "Spiral Out — logo"
    desc = "Spiral mark above the 'spiral out' wordmark."
    body = [svg_open_transparent(w, h, title, desc) if transparent
            else svg_open_on_brand(w, h, title, desc)]
    cx = w / 2

    pad_x = w * STACKED_PAD_X_RATIO
    pad_y = h * pad_y_ratio
    box_w = w - 2 * pad_x
    box_h = h - 2 * pad_y
    gap = h * gap_ratio

    font_size = _fit_font_size(box_w, h=h, ratio_cap=font_ratio)
    wm_w = wordmark_width(font_size)
    ls = font_size * LS_RATIO

    # Spiral box = remaining vertical space (also bounded by box width).
    spiral_box_h = box_h - gap - font_size
    spiral_scale = min(spiral_box_h / SP_VIS_H, box_w / SP_VIS_W)
    sp_vis_h = SP_VIS_H * spiral_scale

    cluster_h = sp_vis_h + gap + font_size
    cluster_top = pad_y + (box_h - cluster_h) / 2

    # Visual bbox center at (cx, cluster_top + sp_vis_h / 2).
    body.append(place_spiral(cx, cluster_top + sp_vis_h / 2, spiral_scale))

    wordmark_baseline_y = cluster_top + sp_vis_h + gap + font_size * 0.85
    body.append(text(cx, wordmark_baseline_y, WORDMARK,
                     size=font_size, ls=ls, preserve=True))
    body.append("</svg>\n")
    return "\n".join(body)


# ----------------------- HERO (thematic backgrounds) -----------------------

def build_hero(w: int, h: int, *, mode: str = "wide_banner",
               spiral_opacity: float = 0.55) -> str:
    """Hero/banner with the brand palette.

    Every element (spiral outer dots + wordmark letterspacing tail) sits
    inside the SAFE RECTANGLE (margin = BANNER_PAD_* / HORIZONTAL_PAD_*).
    Cluster is centered inside the safe rect.

    mode:
      'wide_banner'   — w/h >= 3:1. Wordmark LEFT, spiral accent RIGHT.
      'sixteen_nine'  — 1920x1080 / 2560x1440. Spiral LEFT, wordmark RIGHT.
    """
    title = "Spiral Out"
    desc = "Brand hero — dotted spiral on the atmospheric background."
    body = [svg_open_on_brand(w, h, title, desc)]

    if mode == "wide_banner":
        pad_x = w * BANNER_PAD_X_RATIO
        pad_y = h * BANNER_PAD_Y_RATIO
        box_w = w - 2 * pad_x
        box_h = h - 2 * pad_y
        gutter = w * BANNER_GUTTER_RATIO

        spiral_scale = box_h / SP_VIS_H
        sp_vis_w = SP_VIS_W * spiral_scale

        # Solve font_size so the wordmark fits the remaining text zone.
        max_text_w = box_w - sp_vis_w - gutter
        font_size = _fit_font_size(max_text_w, h=h, ratio_cap=0.42)
        wm_w = wordmark_width(font_size)
        ls = font_size * LS_RATIO

        cluster_w = wm_w + gutter + sp_vis_w
        left = pad_x + (box_w - cluster_w) / 2   # cluster centered in safe rect
        cy = h / 2

        text_anchor_x = left + wm_w / 2
        body.append(text(text_anchor_x, cy + font_size * 0.35, WORDMARK,
                         size=font_size, ls=ls, preserve=True))
        # Visual-bbox center of the spiral sits inside its slot.
        spiral_target_cx = left + wm_w + gutter + sp_vis_w / 2
        body.append(place_spiral(spiral_target_cx, cy, spiral_scale,
                                 opacity=spiral_opacity))

    elif mode == "sixteen_nine":
        pad_x = w * HORIZONTAL_PAD_X_RATIO
        pad_y = h * HORIZONTAL_PAD_Y_RATIO
        box_w = w - 2 * pad_x
        box_h = h - 2 * pad_y
        gutter = w * HORIZONTAL_GUTTER_RATIO

        spiral_scale = box_h / SP_VIS_H
        sp_vis_w = SP_VIS_W * spiral_scale

        max_text_w = box_w - sp_vis_w - gutter
        font_size = _fit_font_size(max_text_w, h=h, ratio_cap=0.18)
        wm_w = wordmark_width(font_size)
        ls = font_size * LS_RATIO

        cluster_w = sp_vis_w + gutter + wm_w
        left = pad_x + (box_w - cluster_w) / 2
        cy = h / 2

        spiral_target_cx = left + sp_vis_w / 2
        body.append(place_spiral(spiral_target_cx, cy, spiral_scale,
                                 opacity=spiral_opacity))
        text_anchor_x = left + sp_vis_w + gutter + wm_w / 2
        body.append(text(text_anchor_x, cy + font_size * 0.35, WORDMARK,
                         size=font_size, ls=ls, preserve=True))

    else:
        raise ValueError(f"unknown hero mode: {mode!r}")

    body.append("</svg>\n")
    return "\n".join(body)


# YouTube channel art — explicit safe-area composition.
# YouTube renders the banner image at different crops per device:
#   - Mobile:  1235 × 338  (mobile-safe — anything outside is invisible on phones)
#   - Tablet:  1855 × 423
#   - Desktop: 2560 × 423
#   - TV:      2560 × 1440 (full canvas)
# We MUST put the mark + wordmark inside the mobile-safe rect so it survives
# on phones. The rest of the canvas is atmospheric bg only.
YT_BANNER_W = 2560
YT_BANNER_H = 1440
YT_SAFE_W   = 1235
YT_SAFE_H   = 338


def build_youtube_banner(spiral_opacity: float = 0.55) -> str:
    title = "Spiral Out — YouTube channel art"
    desc = ("Spiral mark and 'spiral out' wordmark composed inside "
            "YouTube's mobile-safe 1235x338 area, on the brand background.")
    body = [svg_open_on_brand(YT_BANNER_W, YT_BANNER_H, title, desc)]

    # Mobile-safe rectangle, centered on the canvas.
    safe_x = (YT_BANNER_W - YT_SAFE_W) / 2
    safe_y = (YT_BANNER_H - YT_SAFE_H) / 2

    # Internal padding inside the safe rect (cluster never touches mobile
    # crop edges).
    pad_x = YT_SAFE_W * 0.06   # 74 px
    pad_y = YT_SAFE_H * 0.10   # 34 px
    box_w = YT_SAFE_W - 2 * pad_x
    box_h = YT_SAFE_H - 2 * pad_y
    gutter = YT_SAFE_W * 0.05  # 62 px between spiral and wordmark

    # Spiral fills the safe box height (visual envelope).
    spiral_scale = box_h / SP_VIS_H
    sp_vis_w = SP_VIS_W * spiral_scale

    # Wordmark fits whatever horizontal space is left.
    max_text_w = box_w - sp_vis_w - gutter
    font_size = _fit_font_size(max_text_w, h=YT_SAFE_H, ratio_cap=0.55)
    wm_w = wordmark_width(font_size)
    ls = font_size * LS_RATIO

    cluster_w = sp_vis_w + gutter + wm_w
    cluster_left = safe_x + pad_x + (box_w - cluster_w) / 2
    cy = YT_BANNER_H / 2

    spiral_target_cx = cluster_left + sp_vis_w / 2
    body.append(place_spiral(spiral_target_cx, cy, spiral_scale,
                             opacity=spiral_opacity))
    text_anchor_x = cluster_left + sp_vis_w + gutter + wm_w / 2
    body.append(text(text_anchor_x, cy + font_size * 0.35, WORDMARK,
                     size=font_size, ls=ls, preserve=True))

    body.append("</svg>\n")
    return "\n".join(body)


# ----------------------- pipeline -----------------------------------------

def svg_to_png(svg_path: Path, png_path: Path, w: int, h: int) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsvg-convert", "-w", str(w), "-h", str(h),
         str(svg_path), "-o", str(png_path)],
        check=True,
    )


def write_svg(svg: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def write_png_from_svg(svg: str, svg_path: Path, png_path: Path,
                       w: int, h: int) -> None:
    write_svg(svg, svg_path)
    svg_to_png(svg_path, png_path, w, h)
    size_kb = png_path.stat().st_size // 1024
    print(f"  ✓ {png_path.relative_to(ROOT)}  ({size_kb} KB)")


def write_jpg_from_svg(svg: str, svg_path: Path, jpg_path: Path,
                       w: int, h: int) -> None:
    write_svg(svg, svg_path)
    svg_to_jpg(svg_path, jpg_path, w, h)
    size_kb = jpg_path.stat().st_size // 1024
    print(f"  ✓ {jpg_path.relative_to(ROOT)}  ({size_kb} KB)")


def main() -> int:
    if not (have("rsvg-convert") and have("magick")):
        print("ERROR: requires rsvg-convert and ImageMagick on PATH.",
              file=sys.stderr)
        return 1

    # Tear down any previous run to avoid stale files.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # ---- ISO (just the spiral) -------------------------------------------
    print("→ iso (just the spiral mark)")
    iso_dir = OUT / "iso"
    iso_dir.mkdir()

    svg_iso_t = build_iso(2048, 2048, transparent=True)
    write_svg(svg_iso_t, iso_dir / "iso_transparent.svg")
    for size in (512, 1024, 2048):
        write_png_from_svg(svg_iso_t,
                           iso_dir / f"_iso_transparent_{size}.svg",
                           iso_dir / f"iso_transparent_{size}.png",
                           size, size)
        (iso_dir / f"_iso_transparent_{size}.svg").unlink(missing_ok=True)

    svg_iso_b = build_iso(2048, 2048, transparent=False)
    write_svg(svg_iso_b, iso_dir / "iso_on_brand.svg")
    for size in (1024, 2048):
        write_png_from_svg(svg_iso_b,
                           iso_dir / f"_iso_on_brand_{size}.svg",
                           iso_dir / f"iso_on_brand_{size}.png",
                           size, size)
        (iso_dir / f"_iso_on_brand_{size}.svg").unlink(missing_ok=True)

    # ---- LOGO (spiral + wordmark) ----------------------------------------
    print("→ logo (spiral + wordmark)")
    logo_dir = OUT / "logo"
    logo_dir.mkdir()

    svg_log_h_t = build_logo_horizontal(1920, 480, transparent=True)
    write_svg(svg_log_h_t, logo_dir / "logo_horizontal_transparent.svg")
    write_png_from_svg(svg_log_h_t,
                       logo_dir / "_logo_horizontal_transparent.svg",
                       logo_dir / "logo_horizontal_transparent_1920x480.png",
                       1920, 480)
    (logo_dir / "_logo_horizontal_transparent.svg").unlink(missing_ok=True)

    svg_log_h_b = build_logo_horizontal(1920, 480, transparent=False)
    write_svg(svg_log_h_b, logo_dir / "logo_horizontal_on_brand.svg")
    write_png_from_svg(svg_log_h_b,
                       logo_dir / "_logo_horizontal_on_brand.svg",
                       logo_dir / "logo_horizontal_on_brand_1920x480.png",
                       1920, 480)
    (logo_dir / "_logo_horizontal_on_brand.svg").unlink(missing_ok=True)

    svg_log_s_t = build_logo_stacked(1080, 1080, transparent=True)
    write_svg(svg_log_s_t, logo_dir / "logo_stacked_transparent.svg")
    write_png_from_svg(svg_log_s_t,
                       logo_dir / "_logo_stacked_transparent.svg",
                       logo_dir / "logo_stacked_transparent_1080.png",
                       1080, 1080)
    (logo_dir / "_logo_stacked_transparent.svg").unlink(missing_ok=True)

    svg_log_s_b = build_logo_stacked(1080, 1080, transparent=False)
    write_svg(svg_log_s_b, logo_dir / "logo_stacked_on_brand.svg")
    write_png_from_svg(svg_log_s_b,
                       logo_dir / "_logo_stacked_on_brand.svg",
                       logo_dir / "logo_stacked_on_brand_1080.png",
                       1080, 1080)
    (logo_dir / "_logo_stacked_on_brand.svg").unlink(missing_ok=True)

    # ---- AVATAR (PFP, safe area for circle crop) -------------------------
    print("→ avatar (PFP — circle-crop safe)")
    av_dir = OUT / "avatar"
    av_dir.mkdir()

    # ISO with extra padding so the spiral stays inside the circle crop.
    svg_pfp_iso = build_pfp_iso(1024, 1024)
    write_svg(svg_pfp_iso, av_dir / "_pfp_iso.svg")
    svg_to_png(av_dir / "_pfp_iso.svg", av_dir / "pfp_iso_1024.png", 1024, 1024)
    svg_to_png(av_dir / "_pfp_iso.svg", av_dir / "pfp_iso_512.png", 512, 512)
    (av_dir / "_pfp_iso.svg").unlink(missing_ok=True)
    print(f"  ✓ {(av_dir / 'pfp_iso_1024.png').relative_to(ROOT)}")
    print(f"  ✓ {(av_dir / 'pfp_iso_512.png').relative_to(ROOT)}")

    # Stacked logo as PFP — slightly more bottom padding so the wordmark
    # has air from the platform's bottom-of-circle crop.
    svg_pfp_st = build_logo_stacked(1024, 1024, transparent=False,
                                    pad_y_ratio=0.14, gap_ratio=0.12)
    write_svg(svg_pfp_st, av_dir / "_pfp_stacked.svg")
    svg_to_png(av_dir / "_pfp_stacked.svg", av_dir / "pfp_stacked_1024.png",
               1024, 1024)
    (av_dir / "_pfp_stacked.svg").unlink(missing_ok=True)
    print(f"  ✓ {(av_dir / 'pfp_stacked_1024.png').relative_to(ROOT)}")

    # ---- HERO (thematic backgrounds) -------------------------------------
    print("→ hero (thematic backgrounds & banners)")
    hero_dir = OUT / "hero"
    hero_dir.mkdir()

    heroes = [
        # (name, w, h, mode, opacity, as_jpg)
        ("hero_16x9_1920x1080",      1920, 1080, "sixteen_nine", 0.70, True),
        ("hero_x_bluesky_1500x500",  1500,  500, "wide_banner",  0.60, True),
        ("hero_bandcamp_2400x460",   2400,  460, "wide_banner",  0.60, False),  # PNG (Bandcamp prefers PNG)
        ("hero_soundcloud_2480x520", 2480,  520, "wide_banner",  0.60, True),
    ]
    for name, w, h, mode, op, as_jpg in heroes:
        svg = build_hero(w, h, mode=mode, spiral_opacity=op)
        svg_p = hero_dir / f"_{name}.svg"
        write_svg(svg, svg_p)
        if as_jpg:
            jpg_p = hero_dir / f"{name}.jpg"
            svg_to_jpg(svg_p, jpg_p, w, h)
            print(f"  ✓ {jpg_p.relative_to(ROOT)}  ({jpg_p.stat().st_size // 1024} KB)")
        else:
            png_p = hero_dir / f"{name}.png"
            svg_to_png(svg_p, png_p, w, h)
            print(f"  ✓ {png_p.relative_to(ROOT)}  ({png_p.stat().st_size // 1024} KB)")
        svg_p.unlink(missing_ok=True)

    # YouTube banner — explicit safe-area composition (1235x338 mobile-safe
    # inside a 2560x1440 canvas). Cluster fits the safe rect; the rest is bg.
    yt_svg = build_youtube_banner()
    yt_svg_p = hero_dir / "_hero_youtube_2560x1440.svg"
    yt_jpg_p = hero_dir / "hero_youtube_2560x1440.jpg"
    write_svg(yt_svg, yt_svg_p)
    svg_to_jpg(yt_svg_p, yt_jpg_p, YT_BANNER_W, YT_BANNER_H)
    print(f"  ✓ {yt_jpg_p.relative_to(ROOT)}  ({yt_jpg_p.stat().st_size // 1024} KB)")
    yt_svg_p.unlink(missing_ok=True)

    # ---- POSTS (branded, generated locally with consistent spacing) ------
    # Posts are stacked (square/portrait/story/pinterest) or horizontal (og).
    # We GENERATE them here (instead of copying from the site) so spacing
    # is consistent with the rest of this asset pack.
    print("→ posts (generated locally — consistent spacing)")
    posts_dir = OUT / "posts"
    posts_dir.mkdir()

    posts = [
        # (name, w, h, mode, jpg/png)
        ("og_1200x630",              1200,  630, "horizontal", True),
        ("post_square_1080",         1080, 1080, "stacked",    True),
        ("post_portrait_1080x1350",  1080, 1350, "stacked",    True),
        ("post_story_1080x1920",     1080, 1920, "stacked",    True),
        ("post_pinterest_1000x1500", 1000, 1500, "stacked",    True),
    ]
    for name, w, h, mode, as_jpg in posts:
        if mode == "horizontal":
            svg = build_logo_horizontal(w, h, transparent=False)
        elif mode == "stacked":
            # Story (9:16, 1080×1920): IG/TikTok overlay UI at top (~250 px)
            # and bottom (~250 px) — bump pad_y_ratio so the cluster sits
            # inside the safe area.
            if h >= 1900:
                svg = build_logo_stacked(w, h, transparent=False,
                                         pad_y_ratio=0.16, gap_ratio=0.09)
            else:
                svg = build_logo_stacked(w, h, transparent=False)
        else:
            raise ValueError(mode)
        svg_p = posts_dir / f"_{name}.svg"
        write_svg(svg, svg_p)
        if as_jpg:
            jpg_p = posts_dir / f"{name}.jpg"
            svg_to_jpg(svg_p, jpg_p, w, h)
            print(f"  ✓ {jpg_p.relative_to(ROOT)}  ({jpg_p.stat().st_size // 1024} KB)")
        else:
            png_p = posts_dir / f"{name}.png"
            svg_to_png(svg_p, png_p, w, h)
            print(f"  ✓ {png_p.relative_to(ROOT)}  ({png_p.stat().st_size // 1024} KB)")
        svg_p.unlink(missing_ok=True)

    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
