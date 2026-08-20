#!/usr/bin/env bash
# Clip de validacion de las fuentes NUEVAS, ya con el grado del video puesto.
#
#   bash lab/thermal_mass/video/prueba_nuevas.sh
#
# Son tres fuentes que no estaban en el repo, bajadas de Wikimedia Commons:
#
#   cc0_bison_yukon.webm       1920x1080  CC0            bisontes muy cerca, BAJO LLUVIA
#   ccby_relampagos_4k.webm    3840x2160  CC BY 3.0      relampagos, camara lenta
#   pd_rapidos_grand_canyon    1280x 720  dominio publ.  rapidos, camara lenta (NPS)
#
# Lo del bisonte NO tiene que leerse como "un bisonte": el recorte va cerrado sobre el
# lomo, sin cuernos ni silueta de cabeza, para que quede pelo y nada mas.
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FTE="$AQUI/fuentes"; TMP="$AQUI/.prueba"; SALIDA="$AQUI/pruebas/nuevas.mp4"
W=1280; H=720; FPS=60; CRF=22
N="normalize=blackpt=black:whitept=0xB0B0B0:smoothing=250"
DURO="curves=all='0/0 0.38/0.05 0.62/0.72 1/0.78'"
SUAVE="curves=all='0/0 0.30/0.12 0.70/0.80 1/0.86'"
# Curva ABIERTA, para el pelo. El DURO manda el 38% inferior a casi negro y el pelo
# desaparece; con esta se ve la textura sin que el bicho se vuelva reconocible.
MEDIO="curves=all='0/0 0.22/0.14 0.55/0.62 1/0.84'"
# Curva de BLANCOS: el techo sube de 0.84 a 0.97 y el medio se levanta. El pelo pasa de
# gris a blanco de verdad sin que se pierda el dibujo.
BLANCO="curves=all='0/0 0.18/0.16 0.48/0.72 1/0.97'"
# SLOW MOTION FLUIDO. Ralentizar con `setpts` solo estira los tiempos: los rapidos son de
# 24 fps y a 3x quedan 8 cuadros unicos por segundo, o sea judder. `minterpolate` sintetiza
# los cuadros del medio siguiendo el movimiento, y el resultado corre parejo a 60.
# `mi_mode=mci` reconstruye el movimiento, y sobre AGUA TURBULENTA eso DEFORMA: el
# algoritmo busca a donde se movio cada bloque y en un rapido no hay respuesta correcta,
# asi que el agua se derrite. Por eso el rio quedaba "raro". `blend` mezcla los cuadros
# vecinos: no inventa movimiento, solo deja estela. Ademas cuesta 25 veces menos.
FLUIDO="minterpolate=fps=60:mi_mode=blend"
G="noise=alls=6:allf=t+u"
BIS="$FTE/cc0_bison_yukon.webm"; REL="$FTE/ccby_relampagos_4k.webm"; RAP="$FTE/pd_rapidos_grand_canyon.webm"

# fuente | inicio | dur | filtro
PLANOS=(
  # 1 · "mas zoom sobre el cuadrante de arriba a la derecha, porque se nota el movimiento
  #     de la pierna". Recorte de 480 a 340 px, corrido arriba y a la derecha.
  "$BIS|28|7|crop=340:191:1450:172,setpts=3.2*PTS,$FLUIDO,format=gray,$N,eq=contrast=1.45:brightness=0.02,$MEDIO"
  # 2 · aprobado con la curva de blancos
  "$BIS|44|7|crop=460:259:1380:300,transpose=2,crop=259:460,setpts=2.2*PTS,$FLUIDO,format=gray,$N,eq=contrast=1.75,$BLANCO"
  # 3 · aprobado tal cual
  "$BIS|12|7|crop=700:394:900:80,transpose=1,crop=394:700,setpts=2.0*PTS,format=gray,$N,eq=contrast=2.0,$DURO"
  # 4 · aprobado tal cual. El unico rayo que va hacia ABAJO
  "$REL|1.4|6|crop=1900:1069:60:180,setpts=1.5*PTS,format=gray,$N,eq=contrast=1.7,$SUAVE"
  # 5 · aprobado, con los rayos yendo para arriba
  "$REL|3.0|6|crop=1500:844:200:300,negate,vflip,setpts=1.5*PTS,format=gray,$N,eq=contrast=1.8,$DURO"
  "$REL|4.4|6|crop=1700:956:120:220,negate,vflip,setpts=1.5*PTS,format=gray,$N,eq=contrast=1.8,$DURO"
  # 6 · DOS VERSIONES DEL RIO, para elegir. Las dos con mezcla de cuadros en vez de
  #     compensacion de movimiento, que era lo que lo deformaba.
  #     6a: dado vuelta (el agua cae para arriba)
  "$RAP|20|6|crop=620:349:330:210,vflip,setpts=3.0*PTS,$FLUIDO,format=gray,$N,eq=contrast=1.9,$DURO"
  #     6b: el MISMO momento y el mismo recorte, pero derecho. Antes estaba en el segundo
  #     30 del clip, que es agua calma, y por eso salia quieto: la comparacion no servia.
  "$RAP|20|6|crop=620:349:330:210,setpts=3.0*PTS,$FLUIDO,format=gray,$N,eq=contrast=1.9,$DURO"
  # 7 · aprobado tal cual
  "$RAP|55|7|crop=820:461:300:200,negate,setpts=1.5*PTS,format=gray,$N,eq=contrast=1.8,$DURO"
)
rm -rf "$TMP"; mkdir -p "$TMP" "$AQUI/pruebas"; : > "$TMP/l.txt"
i=0
for p in "${PLANOS[@]}"; do
  IFS='|' read -r src ss dur f <<< "$p"
  o="$(printf '%s/%02d.mp4' "$TMP" "$i")"
  ffmpeg -v error -y -ss "$ss" -i "$src" -t "$dur" -vf "$f,scale=$W:$H,$G,fps=$FPS" -an \
    -c:v libx264 -preset veryfast -pix_fmt yuv420p -crf "$CRF" "$o"
  m="$(python3.10 -c "
import subprocess,numpy as np
o=subprocess.run(['ffmpeg','-v','error','-i','$o','-vf','scale=160:160,format=gray','-frames:v','90','-f','rawvideo','-'],capture_output=True).stdout
n=len(o)//(160*160)
a=np.frombuffer(o[:n*160*160],dtype=np.uint8).reshape(-1,160*160).astype(float)
b=a-a.mean(axis=1,keepdims=True)
print(f'{np.abs(np.diff(b,axis=0)).mean():.2f}')" 2>/dev/null || echo 0)"
  echo "file '$o'" >> "$TMP/l.txt"
  printf '  %d  %-28s %ds  movimiento %5s\n' "$i" "$(basename "$src" | cut -c1-28)" "$dur" "$m"
  i=$((i+1))
done
ffmpeg -v error -y -f concat -safe 0 -i "$TMP/l.txt" -c:v libx264 -preset medium -crf "$CRF" \
  -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 "$SALIDA"
rm -rf "$TMP"
echo; echo "-> $SALIDA"
