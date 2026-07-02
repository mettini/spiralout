#!/bin/zsh
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
AUD=/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/01_outbound_master.wav
S=/Users/emilianomettini/outbound_work/scenes; LOG=/Users/emilianomettini/outbound_work/r1080.log
TUN=/Users/emilianomettini/outbound_work/tunel_np_1080
echo "START $(date)" > $LOG
# Ensamble a 1920x1080 (mismo timing/transiciones que el preview aprobado). Todo desde scenes/ persistente.
ffmpeg -y -hide_banner -loglevel error \
 -framerate 24    -t 82   -i $S/ovulo/f%03d.png \
 -framerate 24    -t 138  -i $TUN/f%04d.png \
 -framerate 24    -t 67   -i $S/humo/f%03d.png \
 -framerate 24    -t 52   -i $S/florseq/f%03d.png \
 -framerate 24    -t 13.5 -i $S/dis_full/f%03d.png \
 -framerate 24 -start_number 504 -t 42 -i $S/estelas/f%03d.png \
 -framerate 24    -t 12   -i $S/kaleido/f%03d.png \
 -framerate 24    -t 60   -i $S/mandala/f%03d.png \
 -framerate 24    -t 68   -i $S/afuera/f%03d.png \
 -i "$AUD" \
 -filter_complex "\
 [0:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v0];\
 [1:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v1];\
 [2:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v2];\
 [3:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v3];\
 [4:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v4];\
 [5:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v5];\
 [6:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v6];\
 [7:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,settb=AVTB[v7];\
 [8:v]scale=1920:1080:flags=lanczos,fps=24,format=yuv420p,fade=t=out:st=58:d=8,settb=AVTB[v8];\
 [v0][v1]xfade=transition=fade:duration=4:offset=76[a];\
 [a][v2]xfade=transition=fade:duration=15:offset=196[b];\
 [b][v3]xfade=transition=fade:duration=5:offset=258[c];\
 [c][v4]xfade=transition=fade:duration=2:offset=307[d];\
 [d][v5]xfade=transition=fade:duration=2:offset=318[e];\
 [e][v6]xfade=transition=fade:duration=1.5:offset=357[g];\
 [g][v7]xfade=transition=fade:duration=2:offset=366[h];\
 [h][v8]xfade=transition=fade:duration=8:offset=414[vout]" \
 -map "[vout]" -map 9:a -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k \
 /Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4 >> $LOG 2>&1 && echo "1080 DONE $(date)" >> $LOG || echo "1080 FAIL" >> $LOG
$PY -c "import subprocess;print('dur',subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/Users/emilianomettini/outbound_work/OUTBOUND_1080.mp4']).decode().strip())" >> $LOG 2>&1
echo "done"
