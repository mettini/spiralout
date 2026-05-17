# Recursion · Concepto B — GHOST IN THE MACHINE

> Caos sutil — no walls of sound sino paranoia psicológica. Glitches,
> vinyl crackle, voces invertidas, broken beats fragmentados. Después se
> calma. Voyager vuelve, pero alterado, frágil, "como recordando algo que
> ya no es exactamente eso". Cierre.

## Inspiración

- **Burial** — Untrue, Antidawn (vinyl crackle + broken beats + dark ambient)
- **William Basinski** — Disintegration Loops (loops que se degradan)
- **The Caretaker** — Everywhere at the End of Time (memoria que se pierde)

Tensión psicológica en lugar de fuerza física. La oscuridad acá es
INTERIOR — paranoia, recuerdos fragmentados, fantasmas en la transmisión.

## Arc en 3:00

| Tiempo | Sección | Qué pasa |
|---|---|---|
| 0:00 - 1:00 | **PERTURBACIÓN** | Glitches cortos esparcidos. Vinyl crackle constante de fondo. Bursts de noise muy cortos. Una voz invertida apenas reconocible. Broken beat fragmentado (kick que aparece y desaparece sin patrón). Drone Dm muy bajo, oscuro. Sensación: hay algo MAL pero no se sabe qué. |
| 1:00 - 1:50 | **EL DESPEJE** | Los glitches se van espaciando. El crackle se reduce. Un drone limpio emerge. Tensión psicológica baja. |
| 1:50 - 2:30 | **VOYAGER FRÁGIL** | Voyager melody con notas LIGERAMENTE off-pitch (pitch shift de ±5 cents random por nota). Vibrato más profundo. Reverb largo + LPF heavy. Como recordar un sueño. |
| 2:30 - 3:00 | **CIERRE → LOOP** | Voyager se va con eco. Un último crackle final. Conecta con el principio del Outbound — pero ya transformado, más íntimo. |

## Carácter

**Sutil. Inquietante. Personal.** No agrede al oyente: lo perturba.
Después del despeje, el voyager suena como REGRESO MELANCÓLICO — algo
que perdimos en el camino y volvemos a encontrar pero ya no es lo mismo.

## Instruments necesarios (framework)

**Existentes que sirven**:
- `granular_pulse` — para los glitches cortos
- `voyager_clear` melody para el cierre (con modificaciones)
- `kick` para los broken beats
- `bell_markers` ocasional

**Faltantes** (a agregar al framework):
- `vinyl_crackle(dur, density=0.3)` — capa constante de crackle/click
  randomizado. Inspirado en grabaciones de vinyl viejo
- `glitch_burst(dur=0.1, freq_range=(200, 4000))` — burst corto de noise
  filtrado tipo malfunctioning radio
- `pitch_shifted_melody(notes, amp, pitch_jitter_cents=5)` — melodía
  con shift random de cents por nota → "memoria distorsionada"
- `reverse_voice(freq, dur, amp)` — voice_pad pero con envelope reverso
  (suena como voz hablando al revés)

## Trade-offs

**Pros**:
- Más original / menos cliché que el wall of sound
- Conecta emocionalmente con el "voyager fragmento que vuelve" del
  Crossing storyboard
- Crackle + glitches dan textura RICA sin saturar
- Coherente con la estética dark ambient del Crossing

**Contras**:
- Requiere instruments más sofisticados (vinyl_crackle, glitch_burst,
  pitch shift)
- Sin "catarsis" fuerte — el oyente no recibe el "cielo después del
  infierno" que da el concept A
- Riesgo de sentirse plano si los glitches son muy uniformes (necesita
  variación dinámica)
- "Voyager frágil" puede sonar como "voyager mal hecho" si el
  pitch_jitter no está bien calibrado
