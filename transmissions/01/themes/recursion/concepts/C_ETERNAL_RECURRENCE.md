# Recursion · Concepto C — ETERNAL RECURRENCE

> Loops idénticos del voyager que se desfasan gradualmente (técnica de
> Steve Reich). El motivo se repite y repite, pero con cada repetición
> se desplaza unos milisegundos respecto al anterior. Echos que se
> superponen y crean ringing effects. Espiral conceptual: misma melodía,
> distinta phase = distinta sensación. El "eterno retorno" musical.

## Inspiración

- **Steve Reich** — Piano Phase, It's Gonna Rain, Music for 18 Musicians
- **Brian Eno** — Music for Airports (asynchronous canon, loops largos)
- **William Basinski** — Disintegration Loops (loops que evolucionan)

La técnica del PHASE SHIFTING: empezás con dos copias del mismo loop
sincronizadas, y gradualmente una se acelera mínimamente (5 milisegundos
por loop). Los loops se desfasan y vuelven a fasearse. En el medio
emergen patrones nuevos que no estaban en el original. Mathematics +
emotion.

## Arc en 3:00

| Tiempo | Sección | Qué pasa |
|---|---|---|
| 0:00 - 0:30 | **APERTURA** | Drone Dm sostenido (continuación del Crossing). Cosmos noise de fondo. Calma. |
| 0:30 - 1:00 | **PRIMER LOOP** | Voyager melody fragmento (3 notas: D5-F5-A5) en loop SINCRONIZADO en dos voces (L y R). Suena duplicado. |
| 1:00 - 2:00 | **DESFASE GRADUAL** | La voz R empieza a acelerar 0.5% por loop. Los loops se separan: primero suena con ECO, después suena DOBLADO con notas alternando, después un patrón complejo de RINGING donde nuevas notas emergen del cruce. Se siente la espiral acelerar. |
| 2:00 - 2:40 | **CONVERGENCIA** | Los loops vuelven gradualmente a sincronizar. Las notas se reagrupan. La complejidad se simplifica. Volvemos al voyager UNÍSONO pero ahora suena distinto porque pasamos por todas las phases. |
| 2:40 - 3:00 | **CIERRE → LOOP** | El voyager se sostiene en un acorde final. Drone Dm fade out. Conecta con el principio del Outbound — el oyente entiende que la espiral sigue, que el EP entero es un loop más grande. |

## Carácter

**Mathematical. Hipnótico. Conceptualmente perfecto.** El "eterno retorno"
está en la técnica MISMA: los loops se desfasan, se reencuentran, vuelven
a desfasarse — la espiral.

Es el concepto MÁS ALINEADO con el subtitle del EP (Heliopause = umbral
de retorno, espiral) y con la idea Fibonacci del Outbound.

## Instruments necesarios (framework)

**Existentes que sirven**:
- `voyager_clear` melody (existing)
- `detuned_drone` para el bed armónico
- `cosmos` para el bed de fondo
- `bell_markers` ocasional

**Faltantes** (a agregar al framework):
- `phased_loop(notes, dur_total, loop_dur, phase_shift_per_loop_ms=5,
  amp=0.4)` — toma una secuencia de notas, repite N veces y desplaza la
  copia paralela en X ms cada loop. Devuelve dos arrays (L y R).
- `phase_pair(...)` — helper que genera el par sincronizado/desfasado
  para usar con dos tracks paneados L/R.
- (Opcional) `slow_decay_loop(notes, dur, n_loops, decay_per_loop=0.05)`
  inspirado en Disintegration Loops — el loop se va apagando con cada
  repetición.

## Trade-offs

**Pros**:
- **Conceptualmente PERFECTO**: la técnica MISMA es el contenido (la
  espiral del EP es phasing literal).
- Más original que A (drone metal cliché en su contexto).
- Demuestra dominio técnico (phasing es difícil de hacer bien).
- Cierre con voyager NATURAL — el voyager YA está sonando todo el tema.
- Funciona en 3 min sin sentirse forzado (Reich hizo Piano Phase de 20+
  min, comprimirlo a 3 es ejercicio de calibración).

**Contras**:
- Sin "etapa difícil" tipo SunO))). El user explícitamente pidió "algo
  caótico, etapa difícil". Esto NO la tiene. Hay que elegir: respetar
  el feedback original o ir por elegancia conceptual.
- Riesgo de sonar académico/frío si la calibración del phasing no es
  precisa.
- Requiere un instrument nuevo bastante específico (phased_loop).
- Tres minutos puede ser MUY POCO para que el desfase se desarrolle
  bien — Reich solía tomar 10+ min para una phase completa.

## Combinación posible

Notar que **A y C podrían combinarse**:
- 0:00-1:00 wall of sound (Sunn O))) caos)
- 1:00-2:00 despeje + voyager loop entra
- 2:00-2:50 phase shifting del voyager
- 2:50-3:00 cierre

Eso resolvería las críticas de los dos: A pierde el wall→voyager fácil,
C pierde la falta de etapa difícil. Cumple "caos → despeje → voyager
con espiral".

Si te tira esa combinación, lo marco como **Concepto D — HYBRID**.
