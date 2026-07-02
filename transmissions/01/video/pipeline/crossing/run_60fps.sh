#!/bin/zsh
OUTDIR=/Users/emilianomettini/git/spiralout/transmissions/01/video/out
LOG=/Users/emilianomettini/crossing_work/_60fps.log
MI="minterpolate=fps=60:mi_mode=mci"
TAGS="setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709"
VT="-c:v hevc_videotoolbox -b:v 70M -tag:v hvc1 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a aac -b:a 320k -movflags +faststart"
echo "60FPS(HW) START $(date)" > $LOG
ffmpeg -y -hide_banner -loglevel error -i /Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4 \
 -vf "${MI},scale=3840:2160:flags=lanczos,${TAGS},noise=alls=2:allf=t,format=yuv420p" ${=VT} $OUTDIR/1-outbound_v24_60fps.mp4 >> $LOG 2>&1 && echo "OUTBOUND DONE $(date)" >> $LOG || echo "OUTBOUND FAIL" >> $LOG
ffmpeg -y -hide_banner -loglevel error -i /Users/emilianomettini/crossing_work/CROSSING_V6_1080.mp4 \
 -vf "${MI},scale=3840:2160:flags=lanczos,${TAGS},noise=alls=2:allf=t,format=yuv420p" ${=VT} $OUTDIR/2-crossing_v7_60fps.mp4 >> $LOG 2>&1 && echo "CROSSING DONE $(date)" >> $LOG || echo "CROSSING FAIL" >> $LOG
ffmpeg -y -hide_banner -loglevel error -i /Users/emilianomettini/git/spiralout/transmissions/01/video/recursion/final_4k.mp4 \
 -vf "scale=1920:1080,${MI},scale=3840:2160:flags=lanczos,${TAGS},noise=alls=2:allf=t,format=yuv420p" ${=VT} $OUTDIR/3-recursion_v3_60fps.mp4 >> $LOG 2>&1 && echo "RECURSION DONE $(date)" >> $LOG || echo "RECURSION FAIL" >> $LOG
echo "ALL 60FPS DONE $(date)" >> $LOG
