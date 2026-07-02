#!/bin/zsh
W=/Users/emilianomettini/outbound_work
BL=/Applications/Blender.app/Contents/MacOS/Blender
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
LOG=$W/humo_afuera.log
export BL_W=480 BL_H=270
cp $W/bl_common.py /tmp/bl_common.py 2>/dev/null
echo "HA START $(date)" > $LOG
# --- HUMO (1608 frames) ---
mkdir -p $W/render_raw/humo
$BL -b -P $W/a_humo.py -- 1608 OUT=$W/render_raw/humo >> $LOG 2>&1
echo "humo raw=$(ls $W/render_raw/humo|wc -l) $(date)" >> $LOG
mkdir -p $W/scenes/humo
$PY $W/post.py $W/render_raw/humo $W/scenes/humo 1.12 2.5 1.28 >> $LOG 2>&1
echo "humo grim=$(ls $W/scenes/humo|wc -l) $(date)" >> $LOG
# --- AFUERA (1632 frames) ---
mkdir -p $W/render_raw/afuera
$BL -b -P $W/a_afuera.py -- 1632 OUT=$W/render_raw/afuera >> $LOG 2>&1
echo "afuera raw=$(ls $W/render_raw/afuera|wc -l) $(date)" >> $LOG
mkdir -p $W/scenes/afuera
$PY $W/post.py $W/render_raw/afuera $W/scenes/afuera 1.12 2.5 1.28 >> $LOG 2>&1
echo "afuera grim=$(ls $W/scenes/afuera|wc -l) $(date)" >> $LOG
echo "HA DONE $(date)" >> $LOG
