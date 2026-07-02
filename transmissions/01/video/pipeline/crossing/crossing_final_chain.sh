#!/bin/zsh
cd /Users/emilianomettini/crossing_work
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
AUD=/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/02_crossing_master.wav
OUT4K=/Users/emilianomettini/git/spiralout/transmissions/01/video/out/2-crossing_v5.mp4
LOG=_final_chain.log
echo "CHAIN START $(date)" > $LOG
# 1) esperar humo loop (720) + delirium (2160)
while [ "$(ls humo_loop_hq 2>/dev/null|wc -l|tr -d ' ')" -lt 720 ] || [ "$(ls mandel_final 2>/dev/null|wc -l|tr -d ' ')" -lt 2160 ]; do sleep 30; done
echo "renders done $(date) humo=$(ls humo_loop_hq|wc -l) del=$(ls mandel_final|wc -l)" >> $LOG
# 2) compositar full 1080
$PY crossing_master_final.py >> $LOG 2>&1
echo "frames=$(ls final_frames|wc -l) $(date)" >> $LOG
# 3) master 1080 con audio
ffmpeg -y -hide_banner -loglevel error -framerate 24 -i final_frames/f%05d.png -i "$AUD" \
 -map 0:v -map 1:a -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -c:a aac -b:a 320k -shortest \
 CROSSING_FINAL_1080.mp4 >> $LOG 2>&1
echo "1080 done $(date)" >> $LOG
# 4) 1080 -> 4K HEVC 2-pass + grano FINO (alls=2) + BT.709
VF="scale=3840:2160:flags=lanczos,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,noise=alls=2:allf=t,format=yuv420p"
cd /tmp
ffmpeg -y -hide_banner -loglevel error -i /Users/emilianomettini/crossing_work/CROSSING_FINAL_1080.mp4 -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -x265-params "pass=1:colorprim=bt709:transfer=bt709:colormatrix=bt709" -an -f null /dev/null >> /Users/emilianomettini/crossing_work/$LOG 2>&1
ffmpeg -y -hide_banner -loglevel error -i /Users/emilianomettini/crossing_work/CROSSING_FINAL_1080.mp4 -vf "$VF" \
 -c:v libx265 -b:v 48M -preset medium -tag:v hvc1 -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -x265-params "pass=2:colorprim=bt709:transfer=bt709:colormatrix=bt709" \
 -c:a aac -b:a 320k -movflags +faststart "$OUT4K" >> /Users/emilianomettini/crossing_work/$LOG 2>&1 && echo "4K DONE $(date)" >> /Users/emilianomettini/crossing_work/$LOG || echo "4K FAIL" >> /Users/emilianomettini/crossing_work/$LOG
ls -la "$OUT4K" >> /Users/emilianomettini/crossing_work/$LOG 2>&1
