#!/usr/bin/env bash
# El tramo 4:50 a 6:30 del video: donde suena la lluvia clara y granular.
#
#   bash transmissions/02/bj3_n_pt/video/tramo_lluvia.sh
#
# POR QUE ESTE TRAMO TIENE TRATAMIENTO PROPIO
#
# Es la zona del repiqueteo fuerte, o sea gotas DISCRETAS. La imagen tiene que ser
# impactos y no flujo, por eso va el charco (`IMG_4740`, lluvia pegando en el asfalto)
# y no el volcan visto de lejos que habia antes.
#
# Y va MEZCLADO con fuego, no charco solo: cuatro charcos seguidos aburren por mas que
# cambie el tratamiento. Lo que hacia falta era contraste de MATERIA. El agua es
# oscura y discreta, el fuego es brillante y continuo, asi que cada corte invierte las
# dos cosas a la vez.
#
# FIRMA PROPIA DEL TRAMO: `lenscorrection`. Curva las lineas rectas, y eso no aparece
# en ningun otro momento del video. Sirve para que se note que aca esta pasando algo.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLUVIA="${CLIPS:-$HOME/Downloads/Videos-Aem}"
FTE="$AQUI/fuentes"
SALIDA="$AQUI/pruebas/tramo_lluvia.mp4"
TMP="$AQUI/.tramo"

W=1280; H=720; FPS=60; CRF=22
N="normalize=blackpt=black:whitept=0xB0B0B0:smoothing=8"
DURO="curves=all='0/0 0.38/0.05 0.62/0.72 1/0.78'"
SUAVE="curves=all='0/0 0.30/0.12 0.70/0.80 1/0.86'"
G="noise=alls=6:allf=t+u"

AGUA="$LLUVIA/IMG_4740.MOV"
FUEGO="$FTE/usgs_erupcion_2025.mp4"

# fuente | inicio | duracion | filtro completo
# Ninguna combinacion de recorte + lente + variante se repite en el tramo.
PLANOS=(
  "$AGUA|4.0|9|setpts=2.0*PTS,crop=900:506:560:1700,format=gray,$N,eq=contrast=1.9,$DURO"
  "$FUEGO|58|8|setpts=1.5*PTS,crop=1000:563:460:260,format=gray,$N,eq=contrast=1.7,$SUAVE"
  "$AGUA|1.0|8|setpts=2.0*PTS,crop=800:450:620:1500,lenscorrection=k1=-0.35:k2=-0.12,negate,format=gray,$N,eq=contrast=1.7,$DURO"
  "$FUEGO|66|8|setpts=1.5*PTS,crop=800:450:600:300,transpose=1,crop=450:253,format=gray,$N,negate,eq=contrast=1.7,$SUAVE"
  "$AGUA|6.0|9|setpts=2.5*PTS,crop=760:428:640:1900,tmix=frames=3,lenscorrection=k1=-0.28,format=gray,$N,eq=contrast=2.0,$DURO"
  "$FUEGO|74|8|setpts=1.5*PTS,crop=1100:619:380:220,hflip,format=gray,$N,eq=contrast=1.8,$SUAVE"
  "$AGUA|2.5|8|setpts=2.0*PTS,crop=1000:563:500:2100,transpose=2,crop=500:281,format=gray,$N,eq=contrast=1.9,$DURO"
  "$FUEGO|61|8|setpts=1.5*PTS,crop=900:506:520:340,lenscorrection=k1=0.30:k2=0.10,negate,format=gray,$N,eq=contrast=1.7,$SUAVE"
  "$AGUA|0.5|9|setpts=2.2*PTS,crop=1200:675:420:1600,vflip,format=gray,$N,eq=contrast=1.8,$DURO"
  "$FUEGO|78|8|setpts=1.5*PTS,crop=760:428:640:280,rotate=0.31:c=black,crop=560:315,format=gray,$N,eq=contrast=1.7,$SUAVE"
  "$AGUA|5.0|9|setpts=2.0*PTS,crop=700:394:700:2200,lenscorrection=k1=-0.40,format=gray,$N,eq=contrast=2.0,$DURO"
  "$FUEGO|56|8|setpts=1.5*PTS,crop=1200:675:340:200,negate,transpose=2,crop=600:338,format=gray,$N,eq=contrast=1.7,$SUAVE"
)

rm -rf "$TMP"; mkdir -p "$TMP" "$AQUI/pruebas"
: > "$TMP/lista.txt"
i=0; total=0
for p in "${PLANOS[@]}"; do
  IFS='|' read -r src ss dur filtro <<< "$p"
  out="$(printf '%s/%02d.mp4' "$TMP" "$i")"
  ffmpeg -v error -y -ss "$ss" -i "$src" -t "$dur" \
    -vf "$filtro,scale=$W:$H,$G,fps=$FPS" -an \
    -c:v libx264 -preset veryfast -pix_fmt yuv420p -crf "$CRF" "$out"
  m="$(python3.10 -c "
import subprocess,numpy as np
o=subprocess.run(['ffmpeg','-v','error','-i','$out','-vf','scale=160:160,format=gray',
                  '-frames:v','90','-f','rawvideo','-'],capture_output=True).stdout
n=len(o)//(160*160)
a=np.frombuffer(o[:n*160*160],dtype=np.uint8).reshape(-1,160*160).astype(float)
print(f'{np.abs(np.diff(a,axis=0)).mean():.1f}' if n>2 else '0')" 2>/dev/null || echo 0)"
  echo "file '$out'" >> "$TMP/lista.txt"
  total=$((total + dur))
  printf '  %2d  %-16s %2ds  mov %5s\n' "$i" "$(basename "$src" | cut -c1-16)" "$dur" "$m"
  i=$((i + 1))
done

ffmpeg -v error -y -f concat -safe 0 -i "$TMP/lista.txt" \
  -c:v libx264 -preset medium -crf "$CRF" -pix_fmt yuv420p "$SALIDA"
rm -rf "$TMP"
echo
echo "  $i planos · ${total}s (el tramo del tema dura 100s)"
echo "-> $SALIDA"
