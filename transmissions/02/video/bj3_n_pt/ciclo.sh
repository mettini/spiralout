#!/usr/bin/env bash
# El ciclo completo, hasta que el examen pase o se agote el margen.
#
#   bash transmissions/02/video/bj3_n_pt/ciclo.sh [vueltas]
#
# Cada vuelta: planificar -> reconstruir -> montar -> medir sobre el archivo.
# Los encuadres que no sirven quedan en `excluidos.txt` y la vuelta siguiente no los
# vuelve a elegir. Cuando el examen pasa, rinde el 4K y vuelve a examinarlo.
#
# POR QUE ES UN CICLO Y NO UNA CORRIDA. La validacion del generador es optimista y no
# puede dejar de serlo: no ve el blur de `mejorar.py`, ni el encode, ni la sustitucion por
# el intermedio del modelo, que en tiempo de planificacion todavia no existe. Asi que la
# unica verdad es el archivo, y el camino es medir el archivo y volver a planificar.
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AQUI"
MAX="${1:-12}"
LOG="$AQUI/out/ciclo.log"
: > "$LOG"

decir() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
antes=""

for (( v=1; v<=MAX; v++ )); do
  decir "=== vuelta $v de $MAX ==="

  decir "  planificando..."
  if ! python3.10 planos.py > /tmp/ciclo_plan.txt 2>/tmp/ciclo_plan.log; then
    decir "  ABORTO al planificar:"
    grep -A4 ABORTA /tmp/ciclo_plan.log | head -6 | tee -a "$LOG"
    decir "  el material se quedo sin encuadres sanos. Corto aca."
    break
  fi
  n=$(wc -l < /tmp/ciclo_plan.txt | tr -d ' ')
  decir "  plan: $n planos"
  cp /tmp/ciclo_plan.txt out/bj3_n_pt_1080.plan.txt

  decir "  reconstruyendo con el modelo..."
  python3.10 mejorar.py out/bj3_n_pt_1080.plan.txt > /tmp/ciclo_mejorar.log 2>&1
  tail -1 /tmp/ciclo_mejorar.log | tee -a "$LOG"

  decir "  montando 1080..."
  bash montaje.sh > /tmp/ciclo_montaje.log 2>&1
  if [[ ! -s out/bj3_n_pt_1080.mp4 ]]; then
    decir "  el montaje no dejo archivo. Corto."
    tail -5 /tmp/ciclo_montaje.log | tee -a "$LOG"
    break
  fi

  decir "  midiendo los planos sobre el archivo..."
  python3.10 validar_render.py > /tmp/ciclo_validar.log 2>&1
  malos=$?
  head -12 /tmp/ciclo_validar.log | tee -a "$LOG"

  decir "  examen de entrega:"
  python3.10 qa_entrega.py out/bj3_n_pt_1080.mp4 > /tmp/ciclo_qa.log 2>&1
  qa=$?
  grep -E "FALLA|LISTO PARA|NO ESTA" /tmp/ciclo_qa.log | tee -a "$LOG"

  if [[ $qa -eq 0 && $malos -eq 0 ]]; then
    decir "  EL 1080 PASA TODO. Rindiendo el 4K..."
    bash montaje.sh --4k > /tmp/ciclo_4k.log 2>&1
    if [[ -s out/bj3_n_pt_4k.mp4 ]]; then
      decir "  4K listo. Examen del 4K:"
      python3.10 qa_entrega.py out/bj3_n_pt_4k.mp4 > /tmp/ciclo_qa4k.log 2>&1
      grep -E "FALLA|LISTO PARA|NO ESTA" /tmp/ciclo_qa4k.log | tee -a "$LOG"
    else
      decir "  el 4K no salio:"
      tail -5 /tmp/ciclo_4k.log | tee -a "$LOG"
    fi
    decir "=== TERMINADO en la vuelta $v ==="
    break
  fi

  # GUARDA CONTRA GIRAR EN FALSO. Si el examen falla pero no se anoto ningun encuadre
  # nuevo, la vuelta que viene va a generar EL MISMO plan y fallar igual. Paso: la medicion
  # por plano daba 0 malos y el examen encontraba cortes internos, porque miden el mismo
  # defecto con vecindarios distintos. Antes de seguir, que haya cambiado algo.
  ahora=$(grep -vc '^#' excluidos.txt)
  if [[ "${antes:-}" == "$ahora" ]]; then
    decir "  el examen falla pero no hay nada nuevo que excluir: la vuelta siguiente"
    decir "  daria el mismo plan. Corto para no girar en falso."
    break
  fi
  antes="$ahora"
  decir "  quedan defectos, sigo. Exclusiones acumuladas: $ahora"
done
decir "=== fin del ciclo ==="
