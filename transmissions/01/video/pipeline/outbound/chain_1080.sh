#!/bin/zsh
PY=/Users/emilianomettini/git/spiralout/transmissions/01/video/.venv_detect/bin/python
W=/Users/emilianomettini/outbound_work
LOG=$W/chain.log
echo "CHAIN START $(date)" > $LOG
# 1) esperar a que terminen los dos renders
while pgrep -f tunel_np_1080.py >/dev/null || pgrep -f "a_ovulo.py" >/dev/null; do sleep 30; done
echo "renders done $(date)  tunnel=$(ls $W/tunel_np_1080 | wc -l)  ovulo_raw=$(ls /tmp/anim/ov1080/raw | wc -l)" >> $LOG
# 2) post_sync ovulo 1080
$PY $W/ovulo_post_1080.py >> $LOG 2>&1
echo "ovulo grim=$(ls /tmp/anim/ov1080/grim | wc -l) $(date)" >> $LOG
# 3) ensamble 1080
zsh $W/run_1080.sh >> $LOG 2>&1
echo "CHAIN DONE $(date)" >> $LOG
tail -3 $W/r1080.log >> $LOG
