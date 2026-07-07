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

# ---------- 2) Spotify Canvas (loop seamless: zoom+flicker+grano) ----------
ffmpeg -y -loglevel error -loop 1 -i "$CANVAS_STILL" -t 6 -r 30 \
 -vf "scale=1188:2112:force_original_aspect_ratio=increase,crop=1188:2112,zoompan=z='1.04+0.03*sin(2*PI*on/180)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,eq=brightness='0.02*sin(2*PI*t/6)':saturation=1.05,noise=alls=3:allf=t,format=yuv420p" \
 -c:v libx264 -preset slow -crf 23 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -movflags +faststart "$OUT/aem_canvas_v1.mp4"

# ---------- 3) clips verticales 9:16 con fragmento cifrado ----------
# overlay de texto via PIL (el ffmpeg de homebrew no trae drawtext)
overlay () { # $1=texto $2=png
python3.10 - "$1" "$2" << PY
import sys,textwrap
from PIL import Image, ImageDraw, ImageFont
txt,out=sys.argv[1],sys.argv[2]; W,H=1080,1920
im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
f=ImageFont.truetype("$FONT",40); y=int(H*0.80)
for ln in textwrap.wrap(txt,28):
    w=d.textlength(ln,font=f); x=(W-w)/2
    d.text((x+2,y+2),ln,font=f,fill=(0,0,0,150))
    d.text((x,y),ln,font=f,fill=(255,255,255,235)); y+=52
im.save(out)
PY
}
clip () { # $1=src $2=ss(seg) $3=txtpng $4=out
ffmpeg -y -loglevel error -ss "$2" -t 18 -i "$1" -i "$3" \
 -filter_complex "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,fps=30[v];[v][1:v]overlay=0:0[o]" \
 -map "[o]" -map 0:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$4"
}
# momentos detectados de los control tracks + fragmento por track (textos.md §5.3)
overlay "to leave was the verb that invented it"          /tmp/_txt_ob.png
clip "$OUT/1-outbound_v24_60fps.mp4"  76  /tmp/_txt_ob.png "$OUT/clip_outbound_v1.mp4"
overlay "the wind that had been pushing ceased to push"   /tmp/_txt_cr.png
clip "$OUT/2-crossing_v7_60fps.mp4"  432  /tmp/_txt_cr.png "$OUT/clip_crossing_v1.mp4"
overlay "the spiral does not ascend  it evolves never the same" /tmp/_txt_rc.png
clip "$OUT/3-recursion_v3_60fps.mp4"  67  /tmp/_txt_rc.png "$OUT/clip_recursion_v1.mp4"

echo "OK -> crops en $APOUT/, canvas+clips en $OUT/"
