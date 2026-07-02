#!/bin/zsh
IN=/Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4
OUT=/Users/emilianomettini/git/spiralout/transmissions/01/video/out/1-outbound_v23.mp4
LOG=/Users/emilianomettini/outbound_work/rhevc2.log
VF="scale=3840:2160:flags=lanczos,noise=alls=3:allf=t,format=yuv420p"
cd /tmp
echo "START $(date)" > $LOG
# 2-pass x265 a bitrate objetivo 48 Mbps (arriba de v22=40)
ffmpeg -y -hide_banner -loglevel error -i "$IN" -t 480 -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -pix_fmt yuv420p \
 -x265-params "pass=1:colorprim=bt709:transfer=bt709:colormatrix=bt709" -an -f null /dev/null >> $LOG 2>&1 && echo "PASS1 OK $(date)" >> $LOG || echo "PASS1 FAIL" >> $LOG
ffmpeg -y -hide_banner -loglevel error -i "$IN" -t 480 -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -tag:v hvc1 -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -x265-params "pass=2:colorprim=bt709:transfer=bt709:colormatrix=bt709" \
 -c:a aac -b:a 320k -movflags +faststart \
 "$OUT" >> $LOG 2>&1 && echo "HEVC2 DONE $(date)" >> $LOG || echo "HEVC2 FAIL" >> $LOG
ls -la "$OUT" >> $LOG 2>&1
