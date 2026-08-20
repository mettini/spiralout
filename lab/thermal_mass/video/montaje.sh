#!/usr/bin/env bash
# El video de `bj3 n pt` (TX02 track 1), 11:11 contra el master.
#
#   bash lab/thermal_mass/video/montaje.sh          # 1080p60, para revisar
#   bash lab/thermal_mass/video/montaje.sh --4k     # 3840x2160 60fps, entrega
#
# CUATRO TRAMOS, sobre los tiempos del arreglo (docs/39):
#
#   0:00 - 0:20   negro
#   0:20 - 1:30   el cielo: toma lenta, la estela formandose
#   1:30 - 5:00   el planeta: lluvia real deformada     <- el corte cae sobre la
#   5:00 - 7:50   las criaturas y las bocas                entrada del cuerpo
#   7:50 - 11:11  el cielo, el fogonazo y la lava
#
# Cortes SECOS. Sin fade, sin cross.
#
# TRES REGLAS QUE SALIERON DE EQUIVOCARSE, implementadas abajo:
#
# 1. MOVIMIENTO MEDIDO, no supuesto. La version anterior monto clips generados con
#    0,11 a 0,61 de movimiento entre cuadros al lado de lluvia con 9,64, y encima les
#    hizo zoom de camara para disimular. Ahora cada plano se mide DESPUES del recorte
#    (medir el cuadro entero subestima a una region chica que se mueve dentro de un
#    plano grande) y avisa si no llega al umbral.
# 2. NADA DE ZOOM. Si el material se mueve solo no hace falta, y si no se mueve el
#    zoom lo delata en vez de taparlo.
# 3. EL BLANCO NO LLEGA A 255. `normalize=whitept=white` clava el pixel mas brillante
#    de CADA plano en blanco puro, asi que todo quedaba quemado. El tope va en 0xB0.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLUVIA="${CLIPS:-$HOME/Downloads/Videos-Aem}"
GEN="$AQUI/generado"
FTE="$AQUI/fuentes"
AUDIO="$AQUI/../tema_1111_master.wav"
TMP="$AQUI/.montaje"
UMBRAL_MOV="${UMBRAL_MOV:-3.0}"

if [[ "${1:-}" == "--4k" ]]; then
  W=3840; H=2160; SALIDA="$AQUI/bj3_n_pt_4k.mp4"; CRF=20
else
  W=1920; H=1080; SALIDA="$AQUI/bj3_n_pt_1080.mp4"; CRF=26
fi
FPS=60

# `smoothing` es cuantos cuadros promedia para decidir la ganancia. Con 8 la ganancia
# cambia practicamente cuadro a cuadro, y sobre material oscuro o de bajo contraste se
# pone a OSCILAR: medido en 9:41, la luminancia alternaba entre 100 y 10 cada 3 cuadros
# durante 5 segundos seguidos. Eso es lo que se veia como "una secuencia de menos de un
# segundo", y es la misma causa del cuadro gris de 0:07 y de los fogonazos de 0:18 y 0:23.
# Con 250 la ganancia tarda varios segundos en moverse y no puede pegar saltos.
NORM="normalize=blackpt=black:whitept=0xB0B0B0:smoothing=250"
DURO="curves=all='0/0 0.38/0.05 0.62/0.72 1/0.78'"   # lluvia: material real, calle reconocible
# CURVA LEVANTADA. La DURO manda todo lo que entra abajo del 38% al 5% de salida, y un
# plano cuyo contenido vive en la mitad baja se va ENTERO a negro: medido, 32 de 62 planos
# tenian mas del 70% del cuadro casi negro y 12 estaban en negro total.
#
# No se cambia la DURO para todos, porque el resto del video ya estaba aprobado. `planos.py`
# mide el plano ya renderizado y solo a los que quedan demasiado oscuros les pone esta.
# Medido sobre el plano de lava que estaba 98% en negro: luminancia de 1,1 a 18,1 y
# contraste interno de 5,9 a 18,7.
ALZADA="curves=all='0/0.02 0.26/0.18 0.58/0.74 1/0.82'"
SUAVE="curves=all='0/0 0.30/0.12 0.70/0.80 1/0.86'"  # archivo y generados
# La interferencia gusta pero estaba en TODOS los planos y satura. Se baja de 11 a 6,
# y se agrega una version sin nada para que el recurso vuelva a ser puntual.
GRANO="noise=alls=6:allf=t+u"
GRANO_FUERTE="noise=alls=11:allf=t+u"
SIN_GRANO="null"

t_campo()    { echo "crop=$1,format=gray,$NORM,eq=contrast=1.9:brightness=-0.06,$DURO,scale=$W:$H,$GRANO"; }
t_rotado()   { echo "crop=$1,format=gray,rotate=$2:c=black,crop=$3,$NORM,eq=contrast=1.8,$DURO,scale=$W:$H,$GRANO"; }
t_arrastre() { echo "crop=$1,format=gray,tmix=frames=4,$NORM,eq=contrast=2.0:brightness=-0.05,$DURO,scale=$W:$H,$GRANO"; }
t_difuso()   { echo "crop=$1,format=gray,gblur=sigma=9,unsharp=13:13:2.4,$NORM,eq=contrast=1.7,$DURO,scale=$W:$H,$GRANO"; }
t_arch()     { echo "crop=$1,format=gray,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$GRANO"; }
# Tercer nivel, pedido del user: "me gusta que haya quizas un videito un poco mas
# vivido, tampoco distorsiono mucho". Casi sin tocar, para que contraste con el resto.
t_vivo()     { echo "crop=$1,format=gray,$NORM,eq=contrast=1.25,scale=$W:$H,$SIN_GRANO"; }
t_limpio()   { echo "crop=$1,format=gray,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$SIN_GRANO"; }

# PARA LOS EDIFICIOS. La saturacion no sirve: aplastar niveles no toca la GEOMETRIA, y
# una ventana sigue siendo un rectangulo brillante con bordes rectos. Lo que delata no es
# el brillo, es que hay horizontales y verticales perfectas. Van las cuatro cosas juntas:
# lente que curva las rectas, rotacion no cardinal, desenfoque fuerte con reafilado (los
# bordes se vuelven gradientes) y recorte mucho mas cerrado (sin contexto no hay edificio).
#   $1 recorte · $2 k1 de lente · $3 angulo · $4 recorte final tras rotar
t_geom()     { echo "crop=$1,lenscorrection=k1=$2:k2=-0.10,format=gray,rotate=$3:c=black,crop=$4,gblur=sigma=11,unsharp=13:13:2.8,$NORM,eq=contrast=1.9:brightness=-0.05,$DURO,scale=$W:$H,$GRANO"; }

# LA PALMERA. Los clips del user son 3840x2160 con rotacion -90, o sea que ffmpeg los
# entrega VERTICALES de 2160x3840. Los recortes de la palmera estaban escritos para un
# cuadro apaisado de 1920x1080, asi que caian en el tercio izquierdo del cuadro vertical,
# que es justo donde esta el edificio con los balcones y los aires acondicionados. Los de
# lluvia si estaban escritos para vertical, y por eso esos nunca fallaron.
#
# Zona limpia verificada mirando el cuadro con grilla: x de 1250 a 2160 (el tercio
# derecho), que es donde estan las hojas contra el cielo. El edificio vive en x < 900.
#
# Y aca la variante va DESPUES del recorte, al reves que en el resto: si se antepone,
# rota el cuadro entero y las coordenadas del recorte dejan de significar lo que decian.
#   $1 recorte (sobre el cuadro vertical) · $2 variante opcional
# EL SOLAR CORTO PARPADEA. Medido crudo, sin ningun filtro, ese clip alterna la
# luminancia entre cuadros consecutivos (200 / 182 / 198 / 162 ...). `normalize`
# despues amplifica ese 36 hasta 90 y el resultado es un ESTROBO de 10 Hz: tres cuadros
# claros, tres oscuros, durante segundos. Es lo que el user marco como "una secuencia de
# menos de un segundo" en 9:41, y aparecia tambien en 0:40 y 8:32.
#
# Promediar 8 cuadros lo deja en 3 saltos de 299 contra 29 sin promediar. El costo esta
# medido y hay que decirlo: el movimiento real cae de 13,58 a 0,79, o sea que **el
# movimiento que este clip parecia tener ERA el parpadeo**. Sin estrobo queda casi
# quieto. Y no hay ninguna fuente solar en el repo con movimiento limpio: las cuatro
# largas miden 0,10 a 0,62. Entre estrobo e imagen quieta, va quieta.
#
# La variante va DESPUES del recorte, igual que en la palmera.
#   $1 recorte · $2 variante opcional · $3 contraste · $4 curva
# El PELO no tiene que leerse como un bisonte: recorte cerrado sobre el lomo, sin cuernos
# ni silueta. La curva MEDIA en vez de la DURA, porque con la dura el pelo se va a negro y
# "no se nota mucho que pasa". La de BLANCOS para el plano de textura.
MEDIO="curves=all='0/0 0.22/0.14 0.55/0.62 1/0.84'"
BLANCO="curves=all='0/0 0.18/0.16 0.48/0.72 1/0.97'"

# SLOW MOTION FLUIDO. Ralentizar con `setpts` solo estira los tiempos: las fuentes son de
# 24 a 30 fps y a 3x quedan pocos cuadros unicos por segundo, o sea judder.
#
# Va `blend` y NO `mci`. `mci` reconstruye el movimiento buscando a donde se fue cada
# bloque, y sobre agua turbulenta no hay respuesta correcta: el agua se DERRITE. Era lo
# que hacia que el rio quedara raro. `blend` mezcla los vecinos, no inventa movimiento, y
# encima cuesta 25 veces menos.
FLUIDO="minterpolate=fps=60:mi_mode=blend"

# Con factor de lentitud propio Y mezcla de cuadros: `agf src ss dur factor filtro`
agf() { PLANOS+=("$1|$2|$3|setpts=$4*PTS,$FLUIDO,$5|$(awk -v s="$4" 'BEGIN{printf "%.4f", 1/s}')"); }

# Tratamiento generico: recorte primero, variante despues. Anteponer la variante rota
# las coordenadas del recorte, que es el error que dejo los edificios a la vista.
#   $1 recorte · $2 variante · $3 contraste · $4 curva · $5 brillo
t_gen()      { echo "crop=$1,${2:+$2,}format=gray,$NORM,eq=contrast=${3:-1.7}:brightness=${5:--0.06},${4:-$SUAVE},scale=$W:$H,$GRANO"; }
t_charco_v() { echo "crop=$1,lenscorrection=k1=-0.32:k2=-0.10,${2:+$2,}format=gray,$NORM,eq=contrast=1.9,$DURO,scale=$W:$H,$GRANO"; }

t_pelo()     { echo "crop=$1,${2:+$2,}format=gray,$NORM,eq=contrast=${3:-1.45}:brightness=0.02,${4:-$MEDIO},scale=$W:$H,$GRANO"; }

t_sol()      { echo "crop=$1,${2:+$2,}format=gray,tmix=frames=8,$NORM,eq=contrast=${3:-1.7},${4:-$SUAVE},scale=$W:$H,$GRANO"; }

t_palma()    { echo "crop=$1,${2:+$2,}format=gray,$NORM,eq=contrast=1.9:brightness=-0.06,$DURO,scale=$W:$H,$GRANO"; }

# LA FIRMA DEL TRAMO DE LLUVIA (4:40 a 6:20). `lenscorrection` despues del recorte, que no
# aparece en ningun otro momento del video: sirve para que se note que ahi pasa algo.
# LAS MEDUSAS. Se pidio "un pelin mas de luz": brightness pasa de -0.06 a -0.02.
t_medusa()   { echo "crop=$1,format=gray,$NORM,eq=contrast=1.85:brightness=-0.02,$DURO,scale=$W:$H,$GRANO"; }

t_charco()   { echo "crop=$1,${2:+lenscorrection=$2,}format=gray,$NORM,eq=contrast=1.9,$DURO,scale=$W:$H,$GRANO"; }
t_fuego()    { echo "crop=$1,${2:+lenscorrection=$2,}format=gray,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$GRANO"; }

# LAS VARIANTES. Cambiar el recorte NO es variar: el contenido sigue siendo el mismo.
# Lo que cambia la lectura de la imagen, de mas a menos:
#   negate     el mismo material en negativo se lee como OTRO material
#   transpose  gira 90° y cambia el eje de la composicion entera
#   hflip/vflip rompe la orientacion que el ojo ya memorizo
# Se anteponen al tratamiento, asi una fuente que aparece diez veces se ve distinta
# las diez.
v_neg()  { echo "negate,$1"; }
v_gir()  { echo "transpose=1,$1"; }
v_gir2() { echo "transpose=2,$1"; }
v_hf()   { echo "hflip,$1"; }
v_vf()   { echo "vflip,$1"; }
v_nh()   { echo "negate,hflip,$1"; }
v_ng()   { echo "negate,transpose=1,$1"; }

# 6 s de negro y un fade de 2 s. Es el UNICO fade de entrada del video: el audio arranca
# en silencio y la base tarda 16 s en asomar, asi que el fade acompana esa entrada.
NEGRO=6
FADE=2

# ---------------------------------------------------------------------------------
# LA LISTA DE PLANOS SALE DE `planos.py`, NO DE ACA.
#
# Antes estaba escrita a mano en este archivo y las reglas de repeticion (PLAN_RONDA6
# §V2) se rompian solas: el primer minuto salio con el mismo clip solar cinco veces. La
# guarda de este script solo miraba dos de las cuatro reglas.
#
# `planos.py` las cumple POR CONSTRUCCION: el asignador no puede elegir una fuente que
# rompa alguna, y si se queda sin fuentes elegibles aborta en vez de entregar un video
# que las viole.
# ---------------------------------------------------------------------------------
# el plan se GUARDA, no se tira: `qa_entrega.py` tiene que medir el plan que se uso
# para este render y no regenerar uno nuevo, que ademas tarda diez minutos.
LISTA="$AQUI/ultimo_plan.txt"
python3.10 "$AQUI/planos.py" > "$LISTA" || { echo "planos.py fallo" >&2; exit 1; }

PLANOS=()
while IFS='|' read -r clave ruta ss dur recorte variante trat vel curva; do
  [[ -z "$clave" || "$clave" == \#* ]] && continue
  # la curva la decide `planos.py`: "alzada" para los planos que median casi negros
  case "$curva" in
    alzada) C="$ALZADA" ;;
    suave)  C="$SUAVE" ;;
    *)      C="$DURO" ;;
  esac
  # el material de archivo (`arch`) sigue con la SUAVE cuando no se lo levanto
  if [[ "$trat" == "arch" && "$curva" != "alzada" ]]; then C="$SUAVE"; fi
  case "$trat" in
    sol)    f="$(t_sol   "$recorte" "$variante" 1.7 "$C")" ;;
    palma)  f="$(t_palma "$recorte" "$variante")" ;;
    pelo)   f="$(t_pelo  "$recorte" "$variante" 1.45 "$C")" ;;
    charco) f="$(t_charco_v "$recorte" "$variante")" ;;
    campo)  f="$(t_gen "$recorte" "$variante" 1.9 "$C")" ;;
    agua)   f="$(t_gen "$recorte" "$variante" 1.9 "$C")" ;;
    medusa) f="$(t_gen "$recorte" "$variante" 1.85 "$C" 0.02)" ;;
    *)      f="$(t_gen "$recorte" "$variante" 1.7 "$C")" ;;
  esac
  # LA MEZCLA DE CUADROS VA EN TODO PLANO RALENTIZADO, no solo en los muy lentos.
  # Medido sobre el video anterior: entre 58% y 98% de los cuadros eran repetidos en los
  # nueve puntos que se muestrearon, porque las fuentes son de 24 a 30 fps, la salida es
  # 60, y encima los planos van ralentizados. Cada cuadro unico se sostenia entre 2,5 y 8
  # cuadros de salida, y eso es el "entrecortado" que se marco.
  #
  # Va `blend` y no `mci`: `mci` reconstruye el movimiento y sobre agua turbulenta
  # DEFORMA, hace que el agua se derrita. `blend` solo mezcla los vecinos, y cuesta 25
  # veces menos.
  if awk -v v="$vel" 'BEGIN{exit !(v > 1.02)}'; then f="$FLUIDO,$f"; fi
  PLANOS+=("$ruta|$ss|$dur|setpts=$vel*PTS,$f|$(awk -v v="$vel" 'BEGIN{printf "%.4f", 1/v}')")
done < "$LISTA"
echo "  ${#PLANOS[@]} planos leidos de planos.py"

# LA GUARDA DE LAS CUATRO REGLAS, otra vez sobre la lista YA construida. `planos.py` las
# cumple por construccion, pero esto verifica el resultado final: si alguna vez alguien
# vuelve a escribir planos a mano en este archivo, el build tiene que abortar igual.
CHK="$(mktemp)"
for p in "${PLANOS[@]}"; do
  IFS='|' read -r src ss dur filtro vel <<< "$p"
  printf '%s\t%s\t%s\t%s\n' "$(basename "$src")" "$ss" "$dur" "$filtro" >> "$CHK"
done
python3.10 - "$CHK" "$NEGRO" <<'PY' || { rm -f "$CHK"; exit 1; }
import sys, collections
filas=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
# los minutos se cuentan desde el ARRANQUE DEL VIDEO, o sea contando el negro inicial.
# Medirlos desde el primer plano corre todo 6 s y manda planos al minuto equivocado.
NEGRO=float(sys.argv[2])
MAX=3; err=[]
for k,c in collections.Counter((f[0],f[1],f[3]) for f in filas).items():
    if c>1: err.append(f"REGLA 1: {k[0]} [{k[1]}] con el mismo filtro {c} veces")
cnt=collections.Counter(f[0] for f in filas)
for k,c in cnt.most_common():
    if c>MAX: err.append(f"REGLA 2: {k} aparece {c} veces, el maximo es {MAX}")
t=NEGRO; pm=collections.defaultdict(list)
for i,f in enumerate(filas,1):
    pm[(f[0],int(t//60))].append(i); t+=float(f[2])
for k,v in sorted(pm.items(), key=lambda x:x[0][1]):
    if len(v)>1: err.append(f"REGLA 3: {k[0]} {len(v)} veces en el minuto {k[1]}")
for i in range(1,len(filas)):
    if filas[i][0]==filas[i-1][0]: err.append(f"REGLA 4: planos {i} y {i+1} = {filas[i][0]}")
if err:
    print(f"\n  ABORTA: {len(err)} violaciones de PLAN_RONDA6 §V2\n", file=sys.stderr)
    for e in err[:30]: print("    "+e, file=sys.stderr)
    sys.exit(1)
print(f"  guarda: {len(filas)} planos, {len(cnt)} fuentes, las CUATRO reglas se cumplen")
PY
rm -f "$CHK"

# Los cortes del acto del moog tienen que caer sobre los cambios de enunciado. Los
# tiempos se leen de `melodia.py`, no se copian a mano.
MOOG_T="$(cd "$AQUI/.." && python3.10 -c "
import sys, os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), '..', '..', 'framework'))
import melodia as m
arr, _ = m.tiempos(m.ajustar(m.aplanar(m.CIERRE_ELEGIDO)))
print(' '.join(f'{m.DESDE_S + t:.0f}' for t in arr))" 2>/dev/null || echo "")"
echo "  la melodia cambia de enunciado en: ${MOOG_T:-(no se pudo leer)}"

# REANUDABLE. Cuatro builds se cortaron por la mitad y cada vez se perdian todos los
# planos ya hechos. Ahora cada plano guarda al lado su firma (fuente + arranque + filtro)
# y si al volver a correr la firma coincide, ese plano se reusa tal cual.
#
#   bash montaje.sh            reusa lo que sirva
#   bash montaje.sh --limpio   fuerza rehacer todo
if [[ "${1:-}" == "--limpio" || "${2:-}" == "--limpio" ]]; then rm -rf "$TMP"; fi
mkdir -p "$TMP"
: > "$TMP/lista.txt"

ffmpeg -v error -y -f lavfi -i "color=c=black:s=${W}x${H}:r=$FPS:d=$NEGRO" \
  -c:v libx264 -pix_fmt yuv420p -crf "$CRF" "$TMP/000.mp4"
echo "file '$TMP/000.mp4'" >> "$TMP/lista.txt"

i=1; total=$NEGRO; flojos=0; aciertos=0
for p in "${PLANOS[@]}"; do
  IFS='|' read -r src ss dur filtro vel <<< "$p"
  largo="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src")"
  if awk -v a="$ss" -v b="$dur" -v v="$vel" -v c="$largo" 'BEGIN{exit !(a+b*v > c)}'; then
    echo "ERROR: plano $i pide $(basename "$src") [$ss + $dur x$vel] y dura $largo s" >&2; exit 1
  fi
  out="$(printf '%s/%03d.mp4' "$TMP" "$i")"
  fir="$out.firma"
  # CADA PLANO SE PIDE POR CANTIDAD DE CUADROS, no por duracion.
  #
  # Con `-t $dur` ffmpeg entrega un numero entero de cuadros que puede quedar corto: 26
  # de 62 planos salian entre 0,03 y 0,12 s mas cortos, y la deriva acumulada al final
  # era de -1,65 s. Eso corre TODO el montaje hacia atras, y con el los siete cortes que
  # tienen que caer sobre los cambios de nota del moog.
  #
  # Con `-frames:v` la duracion es exacta por construccion: cuadros / fps.
  ncuadros="$(awk -v d="$dur" -v f="$FPS" 'BEGIN{printf "%d", d*f + 0.5}')"
  firma_actual="$src|$ss|$dur|$ncuadros|$filtro"
  if [[ -s "$out" && -f "$fir" && "$(cat "$fir")" == "$firma_actual" ]]; then
    echo "file '$out'" >> "$TMP/lista.txt"
    total="$(awk -v t="$total" -v d="$dur" 'BEGIN{printf "%.1f", t+d}')"
    printf '  %3d  %-24s %5.1fs  (reusado)  acum %6.1fs\n' \
      "$i" "$(basename "$src")" "$dur" "$total"
    i=$((i + 1)); continue
  fi
  if [[ "$filtro" == *reverse* ]]; then
    # `reverse` BUFFEREA HASTA EL FINAL DEL ARCHIVO. Con `-t` del lado de la salida,
    # ffmpeg lee de $ss hasta EOF, lo da vuelta, y el primer cuadro del plano termina
    # siendo el ULTIMO del archivo: o sea la placa de cierre. Hay que recortar la
    # ENTRADA, no la salida. Costo: la placa de NOAA al aire en el plano final.
    fuente_t="$(awk -v d="$dur" -v v="$vel" 'BEGIN{printf "%.3f", d*v}')"
    ffmpeg -v error -y -ss "$ss" -t "$fuente_t" -i "$src" -vf "$filtro,fps=$FPS" -an \
      -frames:v "$ncuadros" -c:v libx264 -preset veryfast -pix_fmt yuv420p -crf "$CRF" "$out"
  else
    ffmpeg -v error -y -ss "$ss" -i "$src" -vf "$filtro,fps=$FPS" -an \
      -frames:v "$ncuadros" -c:v libx264 -preset veryfast -pix_fmt yuv420p -crf "$CRF" "$out"
  fi

  # LA GUARDA DE MOVIMIENTO. Mide la FUENTE con su recorte, sin gradar.
  #
  # Medir el plano ya tratado estaba mal: con el grado duro el 80% del cuadro queda en
  # negro y la diferencia media entre cuadros se desploma aunque lo visible se mueva
  # perfecto (las palmeras pasaban de 6,1 en la fuente a 2,7 tratadas). Lo que hay que
  # saber es si el MATERIAL se mueve; el grado es otra decision.
  recorte="$(echo "$filtro" | sed -n 's/.*\(crop=[0-9:]*\).*/\1/p' | head -1)"
  # `vel` es cuantos segundos de fuente se consumen por segundo de salida. Medir siempre
  # a velocidad nativa mentia en las dos direcciones: subestimaba los planos ACELERADOS
  # (un solar a 16x se veia como 0,15 cuando en pantalla se mueve a 3,4) y sobreestimaba
  # los RALENTIZADOS. Se toma un cuadro cada `vel` y despues se corrige el resto.
  m="$(python3.10 -c "
import subprocess,numpy as np
vel=$vel
paso=max(1,round(vel))
vf='${recorte:-null},scale=160:160,format=gray'
if paso>1: vf='select=not(mod(n\,%d)),%s' % (paso,vf)
o=subprocess.run(['ffmpeg','-v','error','-ss','$ss','-i','$src','-t',str($dur*vel),'-vf',vf,
                  '-vsync','0','-frames:v','90','-f','rawvideo','-'],capture_output=True).stdout
n=len(o)//(160*160)
a=np.frombuffer(o[:n*160*160],dtype=np.uint8).reshape(-1,160*160).astype(float)
print(f'{np.abs(np.diff(a,axis=0)).mean()*vel/paso:.2f}' if n>2 else '0')" 2>/dev/null || echo 0)"
  aviso=""
  if awk -v m="$m" -v u="$UMBRAL_MOV" 'BEGIN{exit !(m < u)}'; then
    aviso="  <-- POCO MOVIMIENTO"; flojos=$((flojos + 1))
  fi

  printf '%s' "$firma_actual" > "$fir"
  echo "file '$out'" >> "$TMP/lista.txt"
  total="$(awk -v t="$total" -v d="$dur" 'BEGIN{printf "%.1f", t+d}')"
  # marcar si el corte cae sobre un cambio de enunciado del moog (tolerancia 1 s)
  sync=""
  for mt in $MOOG_T; do
    if awk -v a="$total" -v b="$mt" 'BEGIN{exit !(a-b < 1 && b-a < 1)}'; then
      sync="  <-- corte sobre la melodia (${mt}s)"; aciertos=$((aciertos + 1))
    fi
  done
  printf '  %3d  %-24s %5.1fs  mov %5s  acum %6.1fs%s%s\n' \
    "$i" "$(basename "$src")" "$dur" "$m" "$total" "$aviso" "$sync"
  i=$((i + 1))
done

echo
echo "  $i planos · ${total}s de video · el audio dura 671s · $flojos por debajo de $UMBRAL_MOV"
echo "  $aciertos cortes caen sobre un cambio de enunciado del moog"

# La vez pasada el video salio de 605 s contra 671 de audio porque la suma de planos
# quedo corta y nadie lo freno. Ahora aborta.
if awk -v t="$total" 'BEGIN{exit !(t < 671)}'; then
  echo "ERROR: los planos suman ${total}s y el audio dura 671s. Faltan planos." >&2
  exit 1
fi

# Los DOS unicos fundidos del video: entrada al principio y salida a negro al final.
# Todo el resto son cortes secos.
# el TMP ya no se borra al final: es lo que permite reanudar
ffmpeg -v error -y -f concat -safe 0 -i "$TMP/lista.txt" -i "$AUDIO" \
  -vf "fade=t=in:st=${NEGRO}:d=${FADE},fade=t=out:st=663:d=8" \
  -c:v libx264 -preset medium -crf "$CRF" -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 256k -shortest "$SALIDA"

# El plan se CONGELA al lado del entregable. Antes el examen leia `ultimo_plan.txt`, que
# es el mismo archivo que el build siguiente sobrescribe: correr el QA del 1080 mientras
# se renderizaba el 4K lo hacia fallar con el plan a medio escribir.
cp "$LISTA" "${SALIDA%.mp4}.plan.txt"
echo "-> $SALIDA"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "$SALIDA"
