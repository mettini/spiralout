#!/bin/bash
# Chain render para Transmission 01 — pipeline HDR HLG completo.
#
# Cadena:
#   1. Outbound HDR render (~2h40 @ slow preset)
#   2. Crossing HDR render (~3h30 @ slow preset)
#   3. Recursion HDR transcode (~1h)
#   4. Generate _yt.mp4 trimmed -0.75s para los 3
#   5. Copy masters a out/ (para uso)
#
# Total estimado: ~7-8 horas overnight.
# Llamar con: caffeinate -i bash render_all_hdr_chain.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/chain.log"

echo "=== HDR HLG chain started: $(date) ===" | tee -a "$LOG"

# ─── 1. OUTBOUND ────────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[1/4] OUTBOUND render @ $(date)" | tee -a "$LOG"
cd "$SCRIPT_DIR/outbound"
if [ -f final_4k.mp4 ]; then
  mv -f final_4k.mp4 final_4k_pre_hdr.mp4
fi
./.venv/bin/python render.py > render_hdr.log 2>&1
echo "  outbound done @ $(date)" | tee -a "$LOG"
ls -lh final_4k.mp4 | tee -a "$LOG"

# ─── 2. CROSSING ────────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[2/4] CROSSING render @ $(date)" | tee -a "$LOG"
cd "$SCRIPT_DIR/crossing"
if [ -f final_4k.mp4 ]; then
  mv -f final_4k.mp4 final_4k_pre_hdr.mp4
fi
./.venv/bin/python render.py > render_hdr.log 2>&1
echo "  crossing done @ $(date)" | tee -a "$LOG"
ls -lh final_4k.mp4 | tee -a "$LOG"

# ─── 3. RECURSION (transcode SDR -> HDR HLG) ────────────────────────────
echo "" | tee -a "$LOG"
echo "[3/4] RECURSION transcode @ $(date)" | tee -a "$LOG"
cd "$SCRIPT_DIR"
RECURSION_SRC="$SCRIPT_DIR/_archive/out_originals_hydra/3-recursion_hydra.mp4"
if [ ! -f "$RECURSION_SRC" ]; then
  RECURSION_SRC="$SCRIPT_DIR/out/3-recursion.mp4"
fi
echo "  source: $RECURSION_SRC" | tee -a "$LOG"
mkdir -p "$SCRIPT_DIR/recursion"
ffmpeg -y -hide_banner -loglevel warning \
  -i "$RECURSION_SRC" \
  -vf "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,zscale=p=2020:t=arib-std-b67:m=2020_ncl:r=tv,format=yuv420p10le" \
  -c:v libx265 -profile:v main10 -pix_fmt yuv420p10le \
  -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc \
  -x265-params "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:repeat-headers=1:bitrate=80000:vbv-maxrate=80000:vbv-bufsize=160000:nal-hrd=cbr:strict-cbr=1" \
  -preset slow \
  -c:a aac -b:a 320k -shortest -movflags +faststart \
  "$SCRIPT_DIR/recursion/final_4k.mp4"
echo "  recursion done @ $(date)" | tee -a "$LOG"
ls -lh "$SCRIPT_DIR/recursion/final_4k.mp4" | tee -a "$LOG"

# ─── 4. DUAL VERSIONS — master + _yt trimmed ────────────────────────────
echo "" | tee -a "$LOG"
echo "[4/4] DUAL VERSIONS (_yt trim 0.75s) @ $(date)" | tee -a "$LOG"

cd "$SCRIPT_DIR"
# outbound: 480.000 -> 479.250 (YT shows 7:59 max, evita 8:01)
ffmpeg -y -hide_banner -loglevel error \
  -i outbound/final_4k.mp4 -to 479.25 -c copy -avoid_negative_ts make_zero \
  outbound/final_4k_yt.mp4
echo "  outbound _yt done" | tee -a "$LOG"

# crossing: 780.000 -> 779.250
ffmpeg -y -hide_banner -loglevel error \
  -i crossing/final_4k.mp4 -to 779.25 -c copy -avoid_negative_ts make_zero \
  crossing/final_4k_yt.mp4
echo "  crossing _yt done" | tee -a "$LOG"

# recursion: 180 -> 179.250
ffmpeg -y -hide_banner -loglevel error \
  -i recursion/final_4k.mp4 -to 179.25 -c copy -avoid_negative_ts make_zero \
  recursion/final_4k_yt.mp4
echo "  recursion _yt done" | tee -a "$LOG"

# ─── 5. COPY masters a out/ ─────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[copy] masters to out/ @ $(date)" | tee -a "$LOG"
cp outbound/final_4k.mp4 out/1-outbound.mp4
cp crossing/final_4k.mp4 out/2-crossing.mp4
cp recursion/final_4k.mp4 out/3-recursion.mp4
cp outbound/final_4k_yt.mp4 out/1-outbound_yt.mp4
cp crossing/final_4k_yt.mp4 out/2-crossing_yt.mp4
cp recursion/final_4k_yt.mp4 out/3-recursion_yt.mp4

echo "" | tee -a "$LOG"
echo "=== CHAIN DONE @ $(date) ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Masters (full duration):" | tee -a "$LOG"
ls -lh out/{1,2,3}-*.mp4 | grep -v _yt | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "YT versions (-0.75s trimmed):" | tee -a "$LOG"
ls -lh out/*_yt.mp4 | tee -a "$LOG"
