#!/bin/zsh
IN=/Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4
OUT=/Users/emilianomettini/git/spiralout/transmissions/01/video/out/1-outbound_v23.mp4
LOG=/Users/emilianomettini/outbound_work/rhevc.log
echo "START $(date)" > $LOG
ffmpeg -y -hide_banner -loglevel error -i "$IN" -t 480 \
 -vf "scale=3840:2160:flags=lanczos,noise=alls=3:allf=t,format=yuv420p" \
 -c:v libx265 -crf 19 -preset medium -tag:v hvc1 -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -x265-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" \
 -c:a aac -b:a 320k -movflags +faststart \
 "$OUT" >> $LOG 2>&1 && echo "HEVC DONE $(date)" >> $LOG || echo "HEVC FAIL" >> $LOG
ls -la "$OUT" >> $LOG 2>&1
