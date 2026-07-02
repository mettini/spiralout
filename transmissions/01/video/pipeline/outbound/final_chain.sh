#!/bin/zsh
W=/Users/emilianomettini/outbound_work
# esperar humo/afuera
while ! grep -q "HA DONE" $W/humo_afuera.log 2>/dev/null; do sleep 30; done
# ensamble 1080
zsh $W/run_1080.sh > $W/final_chain.log 2>&1
echo "FINAL1080 $(date) $(ls -la $W/OUTBOUND_1080.mp4 2>/dev/null)" >> $W/final_chain.log
