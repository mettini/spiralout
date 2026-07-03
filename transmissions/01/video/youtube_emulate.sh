#!/bin/bash
# Reproduce YouTube's SDR 4K re-encoding pipeline locally.
#
# v2 (2026-06-12): calibrado contra el archivo REAL que YouTube sirvió para
# outbound (yt-dlp, formato 313): VP9 2160p a ~10 Mbps (NO 20) con keyframes
# cada ~3-5s. El emulador anterior era 2x optimista en bitrate y no modelaba
# el GOP pumping (keyint corto → pops periódicos en contenido oscuro).
# Output: VP9 8-bit yuv420p BT.709 at 10 Mbps, keyint 150.
# Source: cualquier mp4 (HDR HLG o SDR).
#
# Uso: ./youtube_emulate.sh input.mp4 output.webm

set -e
INPUT="$1"
OUTPUT="${2:-${INPUT%.mp4}_YT_EMULATED.webm}"

if [ -z "$INPUT" ]; then
  echo "Uso: $0 input.mp4 [output.webm]"
  exit 1
fi

# Detect HDR HLG and add tonemap if needed
COLOR_TRC=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of default=nw=1:nk=1 "$INPUT")
if [ "$COLOR_TRC" = "arib-std-b67" ] || [ "$COLOR_TRC" = "smpte2084" ]; then
  echo "Input is HDR ($COLOR_TRC). Applying tonemap → SDR."
  VF="zscale=t=linear:npl=100,tonemap=tonemap=mobius:peak=10:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p"
else
  echo "Input is SDR. Skipping tonemap."
  VF="format=yuv420p"
fi

echo "Encoding to VP9 20M 8-bit BT.709 (YouTube SDR 4K spec)..."
ffmpeg -y -hide_banner -loglevel warning -stats \
  -i "$INPUT" \
  -vf "$VF" \
  -c:v libvpx-vp9 \
  -b:v 10M -maxrate 12M \
  -row-mt 1 -tile-columns 4 -tile-rows 2 \
  -threads 16 -speed 2 \
  -g 150 \
  -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a libopus -b:a 192k \
  -shortest \
  "$OUTPUT"

echo ""
echo "Done. Output: $OUTPUT"
ls -lh "$OUTPUT"
ffprobe -v error -show_entries stream=codec_name,pix_fmt,color_primaries,color_transfer,color_space -of default=nw=1 "$OUTPUT"
