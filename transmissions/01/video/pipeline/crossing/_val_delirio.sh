#!/bin/zsh
cd /Users/emilianomettini/crossing_work
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
AUD=/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/02_crossing_master.wav
# esperar generacion (2160 frames)
while [ "$(ls kali_delirium 2>/dev/null|wc -l|tr -d ' ')" -lt 2160 ]; do sleep 30; done
echo "delirio listo $(date)" > _val_delirio.log
# ventana ~6:35-6:58 (build al bloom de color): frames 1500..1776 (12fps)
# clip nativo 12fps -> 24fps, audio desde 6:35 (395s)
ffmpeg -y -hide_banner -loglevel error -framerate 12 -start_number 1500 -i kali_delirium/f%04d.png -frames:v 276 -r 24 -filter:v "scale=1280:720" _tmp_val_v.mp4 >> _val_delirio.log 2>&1
ffmpeg -y -hide_banner -loglevel error -i _tmp_val_v.mp4 -ss 395 -t 23 -i "$AUD" -map 0:v -map 1:a -c:v libx264 -crf 14 -pix_fmt yuv420p -c:a aac -shortest _tmp_val_1080.mp4 >> _val_delirio.log 2>&1
ffmpeg -y -hide_banner -loglevel error -i _tmp_val_1080.mp4 -vf "scale=3840:2160:flags=lanczos,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,noise=alls=2:allf=t,format=yuv420p" -c:v libx265 -crf 18 -preset medium -tag:v hvc1 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -x265-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" -c:a aac -b:a 320k -movflags +faststart _CX_DELIRIO_val_4K.mp4 >> _val_delirio.log 2>&1
echo "VAL DELIRIO DONE $(date)" >> _val_delirio.log
