# Concepto B — "2001 Star Gate" / flashero, sucio, críptico

> Segundo concepto visual para los videoclips de Heliopause, pedido por el
> usuario (2026-05-21). Complementa/contrasta con el Concepto A (fósforo/
> telemetría, ver `01_concept_python_shader.md`). **Capturado para FASE C** —
> no implementado aún. Estado: planificación.
>
> Cita del usuario: *"otro con espacio, polvo y demás, pero medio críptico
> medio sucio, medio flashero, como el final de la peli 2001 odisea del
> espacio, esa exploración flashera o ese viaje en la nave."*

---

## 1 — La referencia: el Star Gate de 2001 (Kubrick / Trumbull, 1968)

La secuencia "Jupiter and Beyond the Infinite": el astronauta Bowman atraviesa
un corredor de luz infinito. Lo que la hace eterna y *exactamente* lo que pide
el usuario:

- **Slit-scan** — la técnica madre de Douglas Trumbull. Se fotografía a través
  de una ranura móvil mientras la cámara avanza, estirando patrones en
  corredores de luz que fugan al infinito. Es el "viaje en la nave".
- **No se entiende del todo** — abstracto, no figurativo, *críptico*. No hay
  "planeta" ni "nave" visible: hay luz, velocidad y materia.
- **Sucio / orgánico** — los famosos planos de paisajes solarizados (valles,
  químicos en tanque filmados macro) con color **invertido y desaturado-raro**:
  no es neón limpio, es **enfermizo, terroso, mineral**. Polvo y fluido.
- **Flashero** — pulsos de color, sobreexposición, ritmo hipnótico. Trance.

Anclas conceptuales propias del proyecto que B respeta:
- **Hexagrama 24 / Fù (El Retorno)** — el corredor que fuga al infinito y
  *vuelve* (loop). El stargate es literalmente "atravesar un umbral", igual que
  la **heliopausa** (`docs/02_cosmologia.md`): el cruce de frontera.
- **Anti-iconografía del lore** (`docs/03_lore.md`): sin caras, sin planetas
  enteros, sin espiral dibujada. La espiral vive en el túnel/fuga, no en un trazo.
- Encaja perfecto con **Crossing** (el viaje, el polvo de los anillos, los
  tropezones) — B podría ser el lenguaje de *Crossing* mientras A es el de
  *Outbound*/*Recursion*. Decisión de Fase C.

---

## 2 — Dirección creativa (chequeo creative-direction)

- **Variable única:** *el umbral que se atraviesa sin fin* — no llegás, seguís
  cruzando. (Hermana de la variable de A "el retorno como deriva": acá el
  retorno es el túnel que loopea).
- **Materia prima compartida (Patrón 2):** igual que A — el audio maneja la
  velocidad de fuga del túnel, la densidad del polvo, los pulsos de color. Sin
  el audio el viaje no se mueve.
- **Inversión de tropo (Patrón 5):** el stargate "default" hoy es neón
  cyan/magenta limpio (synthwave). B lo **ensucia**: paleta mineral/enfermiza,
  grano de película, color solarizado, aberración cromática. Lo *sucio* ES la
  firma (igual que el grano CRT es la firma de A).
- **Decisión material (Patrón 3):** la imperfección (grano, halación, chroma,
  solarización) no es defecto — es el "viaje" hecho textura.

⚠️ **Riesgo creativo:** que quede en cliché psicodélico de protector de
pantalla. Antídotos: (1) movimiento *lento e hipnótico*, no epiléptico
(hexagrama 24: *movimiento natural*); (2) paleta **sucia y restringida**, no
arcoíris; (3) que la velocidad de fuga la dicte el audio, no un loop fijo.

---

## 3 — Cómo se logra en cada herramienta (todas gratis)

### Python + shader (recomendado — mismo motor que A)
El motor de `transmissions/01/video/` ya soporta esto con `--preset stargate`:
- **Túnel/fuga = feedback buffer con zoom fuerte** hacia el centro (Droste de
  alta velocidad = volar hacia adentro). Es la misma técnica del Concepto A pero
  con `u_spiralZoom` alto y rotación baja.
- **Slit-scan look** = streaks radiales: el polvo/ruido bajo zoom fuerte se
  estira en corredores. Coordenadas polares para acentuar la fuga.
- **Color sucio** = inyección de hue cíclico con **saturación baja (~0.5)** +
  paleta sesgada a mineral (verdes enfermos, ámbar terroso, magenta apagado).
- **Aberración cromática** (`u_chroma` en `post.frag`, ya implementado): separa
  RGB por radio → halación de lente vieja.
- **Solarización** = invertir parcialmente la curva de luminancia (post).
- **Grano pesado de película** (`u_grain` alto) + scanlines suaves.

Mapeo audio→uniforms (preset stargate, borrador):
| feature | uniform | efecto |
|---|---|---|
| `rms` (env lento) | `u_feedbackGain`/`u_decay` | qué tan largo el corredor (estela) |
| `rms_sub` | `u_spiralZoom` | velocidad de fuga (el "acelere" del viaje) |
| `rms_low` | `u_flowSpeed`/streaks | empuje del polvo en el túnel |
| `flux` | `u_glitch`+`u_chroma` | turbulencia / chicharreo / aberración |
| `rms_air` | `u_grain`/dust | polvo brillante, destellos finos |
| `centroid` | `u_hueBase` | deriva del tinte sucio (frío↔terroso) |
| `onset` | flash/solarize pulse | "flashes" puntuales del viaje |

### Hydra
Naturalísimo para esto: `kaleid`, `modulate(noise)`, y sobre todo `src(o0)` con
`scale(1.0X)` (zoom feedback = túnel infinito). `colorama`/`hue`/`luma` para el
color solarizado; `modulateScale` para la fuga. Ver `02_concept_hydra.md`.
Límite: textura excelente, control de paleta "sucia" requiere disciplina.

### AI open-source (Deforum/AnimateDiff)
Deforum con `zoom` keyframe alto = vuelo hacia adelante; prompt scheduling
("solarized chemical landscapes, slit-scan light corridor, dirty film grain,
desaturated mineral colors, abstract, no horizon"); ControlNet/IPAdapter para
no derivar. RIFE/Real-ESRGAN para terminar. Ver `03_concept_ai_opensource.md`.
Más caro en cómputo; mejor para planos cortos que para 13 min de Crossing.

---

## 4 — Propuesta de prototipo para B (cuando toque, Fase C)

Segmento candidato: **un tramo de *Crossing*** (el viaje), 20–30s, donde haya
movimiento/energía sostenida. Mismo pipeline Python+shader, `--preset stargate`.
MVP demostrable: que se lea "viaje hipnótico que fuga al infinito, sucio y
flashero, sin entenderse del todo" — y que la velocidad de fuga responda
audiblemente al sub-bass del track.

---

## Versión
v1 — 2026-05-21 — concepto B capturado a pedido del usuario. Slit-scan/stargate,
sucio/críptico/flashero. Reusa el motor Python+shader (preset `stargate`).
Pendiente: exploración en Fase C, decisión A vs B vs combo por movimiento.
