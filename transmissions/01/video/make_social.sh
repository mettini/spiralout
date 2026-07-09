#!/usr/bin/env bash
# Genera el material social de ÆM/Heliopause desde assets existentes:
#   - crops de foto press (marca hexagrama) en 3 orientaciones
#   - Spotify Canvas (1080x1920 loop) desde un still de 02_spotify_canvas/
#   - clips verticales 9:16 desde los visualizers, con fragmento cifrado (textos.md)
# Los mp4 caen en out/ (gitignored). Regenerable. Correr desde la raíz del repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
ART=transmissions/01/artwork
OUT=transmissions/01/video/out
CANVAS_STILL="$ART/generated/02_spotify_canvas/20260503_190326_02.png"
ARTIST="$ART/generated/00_artist_photo/artist_photo_3000.png"
FONT="/System/Library/Fonts/Supplemental/Courier New.ttf"
BG=0x0d1014
mkdir -p "$OUT"

# ---------- 1) crops foto press (recompone la marca sobre bg, no cropea) ----------
APOUT="$ART/generated/00_artist_photo"
ffmpeg -y -loglevel error -i "$ARTIST" -vf "scale=-1:1720,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=$BG,scale=1920:1080" "$APOUT/press_horizontal_1920x1080.jpg"
ffmpeg -y -loglevel error -i "$ARTIST" -vf "scale=2160:-1,pad=2160:2700:(ow-iw)/2:(oh-ih)/2:color=$BG,scale=1080:1350" "$APOUT/press_vertical_1080x1350.jpg"
ffmpeg -y -loglevel error -i "$ARTIST" -vf "scale=1500:1500" "$APOUT/press_square_1500.jpg"

# ---------- 2) Spotify Canvas — UNO POR TRACK (fragmento del visualizer de cada tema) ----------
# Fragmento LIMPIO: 60fps (rate nativo -> sin judder), crop 9:16, 6s. SIN fade,
# SIN crossfade, SIN reversa (el "mini fade" del crossfade no gustaba). Spotify
# loopea; el corte del loop se acepta tal cual.
mkc () { # $1=visualizer  $2=ss(seg)  $3=out.mp4
  ffmpeg -y -loglevel error -ss "$2" -t 6 -i "$1" -an \
   -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=60" \
   -r 60 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart "$3"
}
mkc "$OUT/1-outbound_v24_60fps.mp4"  80 "$OUT/canvas_outbound.mp4"    # core de luz
mkc "$OUT/2-crossing_v7_60fps.mp4"  300 "$OUT/canvas_crossing.mp4"    # kaleido del delirio
mkc "$OUT/3-recursion_v3_60fps.mp4"  62 "$OUT/canvas_recursion.mp4"   # rayos radiales

# ---------- 3) clips verticales 9:16 con fragmento cifrado ----------
# Clips LIMPIOS (sin texto). Decisión: el visualizer no lleva texto encima —
# el fragmento cifrado va en la DESCRIPCIÓN del post (ver textos.md §4/5), no en el video.
# 9:16, 18s, 60fps, con audio. Momentos aprobados por track.
clip () { # $1=src $2=ss(seg) $3=out
ffmpeg -y -loglevel error -ss "$2" -t 18 -i "$1" \
 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=60" \
 -r 60 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$3"
}
clip "$OUT/1-outbound_v24_60fps.mp4"  76 "$OUT/clip_outbound.mp4"
clip "$OUT/2-crossing_v7_60fps.mp4"  432 "$OUT/clip_crossing.mp4"
clip "$OUT/3-recursion_v3_60fps.mp4"  67 "$OUT/clip_recursion.mp4"

echo "OK -> crops en $APOUT/, canvas+clips en $OUT/"
