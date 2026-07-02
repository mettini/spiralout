#!/bin/zsh
cd /Users/emilianomettini/crossing_work
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
AUD=/Users/emilianomettini/git/spiralout/transmissions/01/release/masters/02_crossing_master.wav
echo "MASTER START $(date)" > _master.log
$PY crossing_master_v1.py >> _master.log 2>&1
echo "frames: $(ls master_frames/|wc -l)" >> _master.log
ffmpeg -y -hide_banner -loglevel error -framerate 24 -i master_frames/f%05d.png -i "$AUD" \
 -map 0:v -map 1:a -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p -c:a aac -shortest \
 _CROSSING_V1.mp4 >> _master.log 2>&1 && echo "ENCODE DONE $(date)" >> _master.log || echo "ENCODE FAIL" >> _master.log
ls -la _CROSSING_V1.mp4 >> _master.log 2>&1
