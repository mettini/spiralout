#!/bin/zsh
SRC=/Users/emilianomettini/git/spiralout/transmissions/01/video/recursion/final_4k.mp4
OUT=/Users/emilianomettini/git/spiralout/transmissions/01/video/out/3-recursion_v2.mp4
LOG=/Users/emilianomettini/outbound_work/rrec2.log
# setparams FUERZA los tags a bt709 a nivel frame (no convierte pixeles); luego grano + 8-bit
VF="setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,noise=alls=2:allf=t,format=yuv420p"
cd /tmp
echo "START $(date)" > $LOG
ffmpeg -y -hide_banner -loglevel error -i "$SRC" -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -pix_fmt yuv420p \
 -x265-params "pass=1:colorprim=bt709:transfer=bt709:colormatrix=bt709" -an -f null /dev/null >> $LOG 2>&1 && echo "P1 OK $(date)" >> $LOG || echo "P1 FAIL" >> $LOG
ffmpeg -y -hide_banner -loglevel error -i "$SRC" -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -tag:v hvc1 -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -x265-params "pass=2:colorprim=bt709:transfer=bt709:colormatrix=bt709" \
 -c:a copy -movflags +faststart \
 "$OUT" >> $LOG 2>&1 && echo "REC2 DONE $(date)" >> $LOG || echo "REC2 FAIL" >> $LOG
cp "$OUT" "${OUT%.mp4}_yt.mp4" && echo "YT COPY OK" >> $LOG
