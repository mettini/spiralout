#!/bin/zsh
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
AUD=/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/01_outbound_master.wav
F=/tmp/anim/full; F2=/tmp/anim/full2; LOG=/tmp/anim/run_final6.log
echo "START $(date)" > $LOG
# ENSAMBLE con DISMANTLE insertado entre florseq (apertura) y estelas (viaje).
# La flor abre (florseq) -> dismantle (abierta se desmantela + pelotitas + viaje empieza) -> estelas.
ffmpeg -y -hide_banner -loglevel error \
 -framerate 24    -t 79   -i $F2/ovulo/grim/f%03d.png \
 -framerate 23.66 -t 138  -i $F/tunel/grim/f%03d.png \
 -framerate 24    -t 67   -i $F2/humo/grim/f%03d.png \
 -framerate 24    -t 52   -i /tmp/anim/florseq/grim/f%03d.png \
 -framerate 24    -t 11.6 -i /tmp/anim/dis_full/grim/f%03d.png \
 -framerate 24 -start_number 456 -t 42 -i /tmp/anim/estelas/grim/f%03d.png \
 -framerate 24    -t 12   -i /tmp/anim/kaleido/grim/f%03d.png \
 -framerate 24    -t 60   -i /tmp/anim/mandala/grim/f%03d.png \
 -framerate 24    -t 68   -i $F2/afuera/grim/f%03d.png \
 -i "$AUD" \
 -filter_complex "\
 [0:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v0];\
 [1:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v1];\
 [2:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v2];\
 [3:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v3];\
 [4:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v4];\
 [5:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v5];\
 [6:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v6];\
 [7:v]scale=960:540,fps=24,format=yuv420p,settb=AVTB[v7];\
 [8:v]scale=960:540,fps=24,format=yuv420p,fade=t=out:st=58:d=8,settb=AVTB[v8];\
 [v0][v1]xfade=transition=fade:duration=4:offset=73[a];\
 [a][v2]xfade=transition=fade:duration=15:offset=196[b];\
 [b][v3]xfade=transition=fade:duration=5:offset=258[c];\
 [c][v4]xfade=transition=fade:duration=2:offset=307[d];\
 [d][v5]xfade=transition=fade:duration=2:offset=316[e];\
 [e][v6]xfade=transition=fade:duration=1.5:offset=357[g];\
 [g][v7]xfade=transition=fade:duration=2:offset=366[h];\
 [h][v8]xfade=transition=fade:duration=8:offset=414[vout]" \
 -map "[vout]" -map 9:a -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac /tmp/anim/OUTBOUND_8MIN.mp4 >> $LOG 2>&1 && echo "FINAL6 DONE $(date)" >> $LOG || echo "FINAL6 FAIL" >> $LOG
$PY -c "import subprocess;print('dur',subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/tmp/anim/OUTBOUND_8MIN.mp4']).decode().strip())" >> $LOG 2>&1
