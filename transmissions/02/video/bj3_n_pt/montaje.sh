#!/usr/bin/env bash
# El video de `bj3 n pt` (TX02 track 1), 11:11 contra el master.
#
#   bash transmissions/02/bj3_n_pt/video/montaje.sh          # 1080p60, para revisar
#   bash transmissions/02/bj3_n_pt/video/montaje.sh --4k     # 3840x2160 60fps, entrega
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
# La RAIZ del repo se busca, no se cuenta en niveles: contarlos ya rompio una vez al
# mover la carpeta. El master y los entregables viven en rutas fijas desde la raiz.
RAIZ="$AQUI"; while [[ "$RAIZ" != "/" && ! -d "$RAIZ/.git" ]]; do RAIZ="$(dirname "$RAIZ")"; done
AUDIO="$RAIZ/transmissions/02/themes/bj3_n_pt/finals/v1/01_bj3_n_pt_master.wav"
OUT="$AQUI/out"; mkdir -p "$OUT"
TMP="$AQUI/.montaje"
UMBRAL_MOV="${UMBRAL_MOV:-3.0}"

if [[ "${1:-}" == "--4k" ]]; then
  # CRF 18 y no 20: el 4K salia a 27,3 Mbps y para 4K60 con grano eso es poco (YouTube
  # recomienda del orden de 53 a 68). El grano es el que mas sufre: es ruido, no se
  # predice entre cuadros, y al encoder es lo primero que le sobra cuando le faltan bits.
  W=3840; H=2160; SALIDA="$OUT/bj3_n_pt_4k.mp4"; CRF=18
else
  W=1920; H=1080; SALIDA="$OUT/bj3_n_pt_1080.mp4"; CRF=26
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
# EL GRADO CORRE EN 16 BITS Y RECIEN ACA VUELVE A 8.
#
# La cadena estira el contraste ~4,4 veces (normalize 1,5 . eq 1,7 . curva 1,7). Hecha en
# 8 bits eso deja huecos: medido sobre un degradado liso, 60 niveles de gris de salida
# contra 193 manteniendo la precision, y los huecos se ven como bandas concentricas.
# Cuantizar al final y con el grano encima (que hace de tramado) las elimina.
GRANO="format=gray,noise=alls=6:allf=t+u"
GRANO_FUERTE="format=gray,noise=alls=11:allf=t+u"
SIN_GRANO="format=gray"

t_campo()    { echo "crop=$1,format=gray16le,$NORM,eq=contrast=1.9:brightness=-0.06,$DURO,scale=$W:$H,$GRANO"; }
t_rotado()   { echo "crop=$1,format=gray16le,rotate=$2:c=black,crop=$3,$NORM,eq=contrast=1.8,$DURO,scale=$W:$H,$GRANO"; }
t_arrastre() { echo "crop=$1,format=gray16le,tmix=frames=4,$NORM,eq=contrast=2.0:brightness=-0.05,$DURO,scale=$W:$H,$GRANO"; }
t_difuso()   { echo "crop=$1,format=gray16le,gblur=sigma=9,unsharp=13:13:2.4,$NORM,eq=contrast=1.7,$DURO,scale=$W:$H,$GRANO"; }
t_arch()     { echo "crop=$1,format=gray16le,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$GRANO"; }
# Tercer nivel, pedido del user: "me gusta que haya quizas un videito un poco mas
# vivido, tampoco distorsiono mucho". Casi sin tocar, para que contraste con el resto.
t_vivo()     { echo "crop=$1,format=gray16le,$NORM,eq=contrast=1.25,scale=$W:$H,$SIN_GRANO"; }
t_limpio()   { echo "crop=$1,format=gray16le,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$SIN_GRANO"; }

# PARA LOS EDIFICIOS. La saturacion no sirve: aplastar niveles no toca la GEOMETRIA, y
# una ventana sigue siendo un rectangulo brillante con bordes rectos. Lo que delata no es
# el brillo, es que hay horizontales y verticales perfectas. Van las cuatro cosas juntas:
# lente que curva las rectas, rotacion no cardinal, desenfoque fuerte con reafilado (los
# bordes se vuelven gradientes) y recorte mucho mas cerrado (sin contexto no hay edificio).
#   $1 recorte · $2 k1 de lente · $3 angulo · $4 recorte final tras rotar
t_geom()     { echo "crop=$1,lenscorrection=k1=$2:k2=-0.10,format=gray16le,rotate=$3:c=black,crop=$4,gblur=sigma=11,unsharp=13:13:2.8,$NORM,eq=contrast=1.9:brightness=-0.05,$DURO,scale=$W:$H,$GRANO"; }

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
t_gen()      { echo "crop=$1,${2:+$2,}format=gray16le,$NORM,eq=contrast=${3:-1.7}:brightness=${5:--0.06},${4:-$SUAVE},scale=$W:$H,$GRANO"; }
t_charco_v() { echo "crop=$1,lenscorrection=k1=-0.32:k2=-0.10,${2:+$2,}format=gray16le,$NORM,eq=contrast=1.9,$DURO,scale=$W:$H,$GRANO"; }

t_pelo()     { echo "crop=$1,${2:+$2,}format=gray16le,$NORM,eq=contrast=${3:-1.45}:brightness=0.02,${4:-$MEDIO},scale=$W:$H,$GRANO"; }

# EL tmix VA SOLO EN LA FUENTE QUE PARPADEA. Se puso para matar un estrobo de 10 Hz y
# esta bien puesto, pero se aplicaba a TODO el material solar. Medido sobre las trece
# fuentes solares, la unica que alterna de verdad es SDO_20170910_131 (movimiento crudo
# 12,57, prueba de cuadros alternos positiva); el resto no alterna. Y promediar ocho
# cuadros cuesta movimiento: pd_flare_may131 cae de 6,16 a 1,30 y pd_flare_2024feb de
# 2,10 a 0,46. O sea que el remedio de una fuente dejaba quietas a las otras doce, que es
# lo que el user marco como "esta escena es estatica".
#   $5 = nombre del archivo fuente
PARPADEAN="SDO_20170910_131_AR12673X8_4k.webm"
t_sol()      { local tm=""; case " $PARPADEAN " in *" $5 "*) tm="tmix=frames=8," ;; esac
               echo "crop=$1,${2:+$2,}format=gray16le,${tm}$NORM,eq=contrast=${3:-1.7},${4:-$SUAVE},scale=$W:$H,$GRANO"; }

t_palma()    { echo "crop=$1,${2:+$2,}format=gray16le,$NORM,eq=contrast=1.9:brightness=-0.06,$DURO,scale=$W:$H,$GRANO"; }

# LA FIRMA DEL TRAMO DE LLUVIA (4:40 a 6:20). `lenscorrection` despues del recorte, que no
# aparece en ningun otro momento del video: sirve para que se note que ahi pasa algo.
# LAS MEDUSAS. Se pidio "un pelin mas de luz": brightness pasa de -0.06 a -0.02.
t_medusa()   { echo "crop=$1,format=gray16le,$NORM,eq=contrast=1.85:brightness=-0.02,$DURO,scale=$W:$H,$GRANO"; }

t_charco()   { echo "crop=$1,${2:+lenscorrection=$2,}format=gray16le,$NORM,eq=contrast=1.9,$DURO,scale=$W:$H,$GRANO"; }
t_fuego()    { echo "crop=$1,${2:+lenscorrection=$2,}format=gray16le,$NORM,eq=contrast=1.7,$SUAVE,scale=$W:$H,$GRANO"; }

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
# EL PLAN SE REUSA SI YA ESTA CONGELADO. Regenerarlo cuesta unos diez minutos de ffmpeg
# validando cada candidata, y para pasar de 1080 a 4K el plan es EL MISMO: lo unico que
# cambia es la resolucion de salida. Regenerarlo ahi es tiempo de maquina tirado.
#
#   bash montaje.sh --4k              reusa el plan congelado del 1080 si existe
#   bash montaje.sh --replanificar    lo fuerza a regenerarlo
CONGELADO="$AQUI/out/bj3_n_pt_1080.plan.txt"
LISTA="$AQUI/ultimo_plan.txt"
if [[ "$*" == *--replanificar* || ! -s "$CONGELADO" ]]; then
  echo "  generando el plan (tarda: valida cada candidata con ffmpeg)"
  python3.10 "$AQUI/planos.py" > "$LISTA" || { echo "planos.py fallo" >&2; exit 1; }
else
  cp "$CONGELADO" "$LISTA"
  echo "  plan reusado de $(basename "$CONGELADO"): $(wc -l < "$LISTA" | tr -d ' ') planos"
fi

# LOS PLANOS RECONSTRUIDOS CON EL MODELO.
#
# `nitidez.py` mide que 41 de los 62 planos vienen de fuentes cuya compresion dejo
# mesetas planas de 8x8 en las zonas de bajo contraste. El grado las saca a la superficie
# y el escalado las agranda: son los cuadrados que se veian en el 4K. Debajo de la meseta
# no hay informacion, asi que ningun filtro las recupera (se probaron deblock, hqdn3d,
# smartblur y gblur, ninguno cambio nada). `mejorar.py` reconstruye con Real-ESRGAN los
# que ademas se amplian 2x o mas, y deja un intermedio por plano en `.ia/`.
#
# El intermedio es el recorte reconstruido Y NADA MAS: sin grado, sin variante, sin
# ralentizar, a los fps de la fuente. Entra en la cadena exactamente donde entraria la
# fuente, asi que NO cambia ni un encuadre ni un corte ni un tiempo: el plan de planos
# queda intacto y las cuatro reglas de repeticion se siguen cumpliendo igual.
#
# Los que estan cuadriculados pero casi no se amplian (las fulguraciones se recortan a
# 3400 px y se amplian 1,1x: el bloque nunca crece) van con un blur barato en vez del
# modelo.
# macOS trae bash 3.2, que no tiene arrays asociativos. Se consultan los mapas con awk.
# LA CLAVE LLEVA LA DURACION ademas de fuente, arranque y recorte. Sin ella dos planos
# que reusan la misma fuente con otro largo colapsan en una entrada y el mas largo se
# lleva el intermedio del mas corto. Pasa de verdad: lava1 y rio.
ia_buscar() {   # $1 = "fuente|arranque|duracion|recorte"  ->  "intermedio|ancho|alto"
  [[ -f "$AQUI/.ia/mapa.txt" ]] || return 0
  awk -F'|' -v k="$1" '$1"|"$2"|"$3"|"$4==k {print $5"|"$6"|"$7; exit}' "$AQUI/.ia/mapa.txt"
}
ia_blur() {     # $1 = misma clave  ->  sigma  o nada
  [[ -f "$AQUI/.ia/blur.txt" ]] || return 0
  awk -F'|' -v k="$1" '$1"|"$2"|"$3"|"$4==k {print $5; exit}' "$AQUI/.ia/blur.txt"
}
[[ -f "$AQUI/.ia/mapa.txt" ]] && echo "  $(wc -l < "$AQUI/.ia/mapa.txt" | tr -d ' ') planos reconstruidos con el modelo"
[[ -f "$AQUI/.ia/blur.txt" ]] && echo "  $(wc -l < "$AQUI/.ia/blur.txt" | tr -d ' ') planos con blur de desbloqueo"

PLANOS=()
while IFS='|' read -r clave ruta ss dur recorte variante trat vel curva; do
  [[ -z "$clave" || "$clave" == \#* ]] && continue
  # el plan guarda rutas relativas a la raiz, para que sobreviva a mover carpetas
  ruta_rel="$ruta"
  [[ "$ruta" != /* ]] && ruta="$RAIZ/$ruta"
  # la curva la decide `planos.py`: "alzada" para los planos que median casi negros
  case "$curva" in
    alzada) C="$ALZADA" ;;
    suave)  C="$SUAVE" ;;
    *)      C="$DURO" ;;
  esac
  # el material de archivo (`arch`) sigue con la SUAVE cuando no se lo levanto
  if [[ "$trat" == "arch" && "$curva" != "alzada" ]]; then C="$SUAVE"; fi
  case "$trat" in
    sol)    f="$(t_sol   "$recorte" "$variante" 1.7 "$C" "$(basename "$ruta")")" ;;
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

  # SUSTITUCION POR EL INTERMEDIO. La clave es la IDENTIDAD del plano (fuente, arranque,
  # recorte) y no el numero de linea, porque este bucle saltea vacias y comentarios y los
  # indices se correrian.
  clave_ia="$ruta_rel|$ss|$dur|$recorte"
  ia_hit="$(ia_buscar "$clave_ia")"
  if [[ -n "$ia_hit" ]]; then
    IFS='|' read -r ia_ruta ia_w ia_h <<< "$ia_hit"
    # GUARDA. El intermedio es `escala` veces mas grande que el recorte original, asi que
    # cualquier filtro medido en PIXELES que venga despues quedaria fuera de escala: un
    # segundo `crop` (t_rotado, t_geom), un `gblur`, un `unsharp`. Hoy ningun plano del
    # modelo usa esos grados, pero si alguna vez lo hace esto tiene que frenar el build
    # en vez de sacar un encuadre corrido en silencio.
    resto="${f#*crop=[0-9]*:[0-9]*:[0-9]*:[0-9]*}"
    if [[ "$resto" == *crop=* || "$resto" == *gblur=* || "$resto" == *unsharp=* ]]; then
      echo "ERROR: el plano $clave usa un grado medido en pixeles y tiene intermedio." >&2
      echo "       Reescalá esos parametros por el factor del modelo o sacalo de mejorar.py." >&2
      exit 1
    fi
    # el primer crop pasa a ser el cuadro entero del intermedio, que ya viene recortado
    f="$(sed -E "s/crop=[0-9]+:[0-9]+:[0-9]+:[0-9]+/crop=${ia_w}:${ia_h}:0:0/" <<< "$f")"
    ruta="$RAIZ/$ia_ruta"
    ss=0
  else
    ia_sig="$(ia_blur "$clave_ia")"
    if [[ -n "$ia_sig" ]]; then
      # el blur va ANTES del grado: despues el contraste ya estiro el escalon del bloque
      f="${f/format=gray16le,/format=gray16le,gblur=sigma=${ia_sig},}"
    fi
  fi

  PLANOS+=("$ruta|$ss|$dur|setpts=$vel*PTS,$f|$(awk -v v="$vel" 'BEGIN{printf "%.4f", 1/v}')")
done < "$LISTA"
echo "  ${#PLANOS[@]} planos leidos de planos.py"

# PRUEBA EN SECO. Imprime la lista ya construida y sale, sin renderizar nada. Sirve para
# ver que la sustitucion por los intermedios quedo bien antes de pagar un build entero.
if [[ "${1:-}" == "--seco" || "${2:-}" == "--seco" ]]; then
  i=1
  for p in "${PLANOS[@]}"; do
    IFS='|' read -r s_src s_ss s_dur s_f s_vel <<< "$p"
    marca="   "; [[ "$s_src" == *.ia/* ]] && marca="IA "
    printf '%s%3d  %-34s ss=%-8s dur=%-5s %s\n' "$marca" "$i" "$(basename "$s_src")" "$s_ss" "$s_dur" "$s_f"
    i=$((i+1))
  done
  exit 0
fi

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
MOOG_T="$(cd "$RAIZ/transmissions/02/themes/bj3_n_pt" && python3.10 -c "
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
