# Recursion · Concepto A — BLACK MASS RETURN

> Inicialmente caótico, etapa difícil tipo Sunn O))). Walls of sound,
> drones distorsionados masivos. Después se despeja, vuelta a voyager,
> conecta con el principio.

## Inspiración

- **Sunn O)))** — Life Metal, Monoliths & Dimensions
- **Earth** — Hex; Or Printing in the Infernal Method
- **Boris** — Flood

Drone metal puro. Slow tempos extremos, distortion massive, feedback
resonante, drop A tunings. La música SE SIENTE en el cuerpo más que se
escucha.

## Arc en 3:00

| Tiempo | Sección | Qué pasa |
|---|---|---|
| 0:00 - 0:55 | **WALL OF SOUND** | Distorted drone masivo en D (drop A). Sub-bass agresivo. Feedback resonante. Sin ritmo, sin melodía. Catedral oscura colapsando. |
| 0:55 - 1:10 | **PEAK** | El wall culmina. Distortion al máximo. Algo está por romperse. |
| 1:10 - 2:00 | **EL DESPEJE** | Gradualmente las capas de distortion se sacan una a una. Filtros LPF abren. Aparece luz — un drone más limpio emerge debajo del caos. |
| 2:00 - 2:30 | **VOYAGER REGRESA** | Voyager melody completa, limpia, brillante. Después del caos suena REVELACIÓN. |
| 2:30 - 3:00 | **CIERRE → LOOP** | Voyager se repite con eco, fade out. Los últimos segundos preparan armónicamente el primer compás del Outbound. Si el EP loopea, no hay corte. |

## Carácter

**Heavy. Difícil. Confrontacional.** El oyente no puede ser pasivo en el
primer minuto — el wall of sound demanda atención (o rendición).

Después del despeje, el voyager suena como recompensa. Como salir del
infierno y ver el cielo. Es un arco emocional FUERTE pero corto (3 min).

## Instruments necesarios (framework)

**Existentes que sirven**:
- `detuned_drone` con muchos voices + cents alto = drone disonante
- `distort` (efecto) — al máximo (amount=4-5)
- `sub_rumble` (28 Hz) — base agresiva
- `voyager_clear` melody para el cierre
- `bell_markers` para puntuar

**Faltantes** (a agregar al framework):
- `wall_of_sound(notes, dur, distortion=4.0, feedback_simulated=True)` —
  drone masivo distortionado con simulación de feedback (capas rotativas
  con ligera desafinación que generan beating)
- `feedback_squeal(freq, dur, decay)` — note alta sostenida con sweep de
  pitch sutil simulando feedback de amp
- `sub_punisher(freq, dur, mod_depth=0.6, distortion=2.0)` — sub-bass
  con modulación + saturación

## Trade-offs

**Pros**:
- Conecta directamente con el feedback inicial del usuario
- Contraste DRAMÁTICO con Crossing (oscuridad pura → catarsis)
- 3 min suficiente para el arco si está bien curvado
- Cierre con voyager = "vuelta a casa" emocionalmente fuerte

**Contras**:
- 1 minuto de wall of sound puede ser MUCHO si el oyente no está preparado
- Requiere buen render de distortion (calibración)
- Riesgo de "sobre-distortar" — el limit del peak post-normalize del master
- El cambio de wall→voyager puede sonar abrupto si la transición no está
  bien curvada (downlifters, filter sweeps abriendo)
