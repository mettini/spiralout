#!/bin/zsh
# 1080 -> 4K UHD: lanczos + grano fino (anti-banding) + tags BT.709 (evita el shift azul en TV).
# El fade-to-black final ya viene horneado del ensamble 1080.
IN=/Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4
OUT=/Users/emilianomettini/outbound_work/OUTBOUND_4K.mp4
GRAIN=${GRAIN:-3}      # grano fino anti-banding. Bajar si mancha, subir si banding.
LOG=/Users/emilianomettini/outbound_work/r4k.log
echo "START $(date) grain=$GRAIN" > $LOG
# -t 480: trim a 8:00 exactos (alinea con el master de audio; el sobrante son 2s de negro)
ffmpeg -y -hide_banner -loglevel error -i "$IN" -t 480 \
 -vf "scale=3840:2160:flags=lanczos,noise=alls=${GRAIN}:allf=t,format=yuv420p" \
 -c:v libx264 -crf 16 -preset slow -profile:v high -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" \
 -c:a aac -b:a 320k -movflags +faststart \
 "$OUT" >> $LOG 2>&1 && echo "4K DONE $(date)" >> $LOG || echo "4K FAIL" >> $LOG
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
$PY -c "import subprocess;print('dur',subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height','-of','default=nk=1:nw=1','$OUT']).decode().strip().replace(chr(10),' '))" >> $LOG 2>&1
ls -la "$OUT" >> $LOG 2>&1
echo "done"
