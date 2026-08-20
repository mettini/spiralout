#!/usr/bin/env bash
# Concepto de video para el track 1 de TX02: la lluvia deformada.
#
# Criterio de encuadre (validado con stills antes de animar, ver docs/39): fragmento
# apretado y ESTIRADO, nunca el plano entero. El plano entero siempre delata la calle.
# El vertical del telefono no se respeta: se recorta, se rota y se estira.
#
# Los saltos entre clips son cortes secos. Sin fade, sin cross, sin nada.
#
# El ritmo de corte sigue el arco de la base: `mix_v2_arco` tarda 16 s en entrar y 15
# en salir, asi que los planos son largos en los bordes y se acortan hacia el centro.
#
# Salida: 1920x1080 a 30 fps, que es formato de CONCEPTO para validar. El final va a
# 4K obligatorio (memory/feedback_video_must_be_4k.md) y a 60 fps
# (memory/feedback_render_60fps_for_youtube.md).
#
#   bash lab/thermal_mass/video/concepto.sh
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIPS="${CLIPS:-$HOME/Downloads/Videos-Aem}"
AUDIO="$AQUI/../mix_v3.wav"
TMP="$AQUI/.segmentos"
SALIDA="$AQUI/concepto_1080.mp4"

W=1920; H=1080; FPS=30
GRANO="noise=alls=9:allf=t+u"

# Los cuatro tratamientos. Cada uno recorta un fragmento y lo estira a 16:9.
f_barcode() {   # 4741: el agua chorreando sobre la senda. Queda en bandas duras.
  echo "crop=2160:520:0:$1,scale=$W:$H,format=gray,eq=contrast=2.4:brightness=-0.08,unsharp=5:5:1.0,$GRANO"
}
f_cortina() {   # 4740: el agua picada. Cortina de textura, irreconocible.
  echo "crop=1500:500:330:$1,scale=$W:$H,format=gray,eq=contrast=2.5:brightness=-0.12,unsharp=5:5:1.2,$GRANO"
}
f_blanqueo() {  # 4739: el blanqueo. Es el que tiene el agudo en el audio.
  echo "crop=2160:600:0:$1,scale=$W:$H,format=gray,eq=contrast=1.95:brightness=0.05,gblur=sigma=1.3,$GRANO"
}
f_nocturno() {  # 4742: las rayas de lluvia de noche, rotadas.
  echo "crop=1400:900:400:$1,transpose=1,scale=$W:$H,format=gray,eq=contrast=2.8:brightness=-0.14,$GRANO"
}

# fuente | inicio | duracion | tratamiento | offset de recorte
#
# Ningun plano pide mas alla del final de su clip, asi que no hay costura de loop
# adentro de un plano. Los largos utiles son 4739=9,70s 4740=10,27s 4741=3,44s
# 4742=7,84s. El 4741 dura 3,4 s: de ahi que sus planos sean estocadas cortas.
#
# 6 s de negro + 114 s de planos = 120 s, que es el largo exacto de mix_v3.
PLANOS=(
  "4739|0.2|9.0|blanqueo|2200"   # entra con lo mas lavado, mientras la base sube
  "4740|0.3|9.5|cortina|1500"
  "4741|0.1|3.2|barcode|120"     # primera estocada
  "4742|0.2|7.4|nocturno|1400"
  "4739|1.0|8.0|blanqueo|1500"
  "4741|0.2|3.0|barcode|400"
  "4740|1.0|8.5|cortina|900"
  "4742|0.5|6.0|nocturno|900"
  "4741|0.1|2.6|barcode|900"     # el centro: planos mas cortos
  "4739|2.0|5.0|blanqueo|2600"
  "4740|2.0|5.5|cortina|2100"
  "4741|0.3|2.4|barcode|1500"
  "4742|1.0|4.5|nocturno|2000"
  "4740|4.0|4.5|cortina|1200"
  "4741|0.2|2.8|barcode|700"
  "4739|0.5|5.5|blanqueo|1900"
  "4739|1.5|6.0|blanqueo|2800"
  "4740|5.0|4.6|cortina|1800"
  "4742|0.3|7.0|nocturno|1700"   # se abre de nuevo mientras la base cae
  "4740|0.5|9.0|cortina|2400"
)

rm -rf "$TMP"; mkdir -p "$TMP"

# Negro de apertura. La base arranca en silencio y tarda 3 s en asomar, asi que el
# negro no es un recurso: es lo que esta pasando en el audio.
# PENDIENTE (docs/39): definir si aca va telemetria/barcode en vez de negro puro.
ffmpeg -v error -y -f lavfi -i "color=c=black:s=${W}x${H}:r=$FPS:d=6" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 "$TMP/000.mp4"
echo "file '$TMP/000.mp4'" > "$TMP/lista.txt"

i=1
total=6
for p in "${PLANOS[@]}"; do
  IFS='|' read -r src ss dur trat off <<< "$p"
  # Guarda: si el plano pide mas alla del final del clip, ffmpeg lo trunca EN
  # SILENCIO y el video termina mas corto que el audio. Que avise.
  largo="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIPS/IMG_$src.MOV")"
  if awk -v a="$ss" -v b="$dur" -v c="$largo" 'BEGIN{exit !(a+b > c)}'; then
    echo "ERROR: el plano $i pide IMG_$src [$ss +$dur] y el clip dura $largo s" >&2
    exit 1
  fi
  total="$(awk -v t="$total" -v d="$dur" 'BEGIN{printf "%.1f", t+d}')"
  filtro="$(f_"$trat" "$off")"
  out="$(printf '%s/%03d.mp4' "$TMP" "$i")"
  ffmpeg -v error -y -ss "$ss" -i "$CLIPS/IMG_$src.MOV" -t "$dur" \
    -vf "$filtro,fps=$FPS" -an -c:v libx264 -pix_fmt yuv420p -crf 18 "$out"
  echo "file '$out'" >> "$TMP/lista.txt"
  printf '  %2d  %s  %5.1fs  %s\n' "$i" "$src" "$dur" "$trat"
  i=$((i + 1))
done

# Concatenacion y audio pegado aparte. El corte es seco por definicion: el demuxer
# concat no interpola nada entre segmentos.
#
# Se re-encodea con crf alto a proposito. El grano temporal (`noise=allf=t`) cambia
# cada pixel en cada cuadro, o sea que es incompresible: a crf 18 estos 2 minutos
# pesaban 736 MB, que no sirve ni para mirarlo. Esto es una copia de revision. El
# master final se rinde aparte en 4K y con bitrate de verdad.
ffmpeg -v error -y -f concat -safe 0 -i "$TMP/lista.txt" -i "$AUDIO" \
  -c:v libx264 -preset fast -crf 28 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest "$SALIDA"

echo
echo "   planos: $((i-1))   duracion planeada: ${total}s"
echo "-> $SALIDA"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "$SALIDA"
