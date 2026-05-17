# Plan de trabajo — transmission 01

Plan vivo. Cuando el usuario me dé luz verde sobre los pendientes
abiertos, ejecuto en este orden.

## Pendientes abiertos (esperando decisión del usuario)

### 1. Recursion — elegir concepto
Tres conceptos en `themes/recursion/concepts/`:
- **A — BLACK MASS RETURN** (Sunn O))) drone metal)
- **B — GHOST IN THE MACHINE** (Burial-style glitch + crackle)
- **C — ETERNAL RECURRENCE** (Steve Reich phase music)
- **D — HYBRID A+C** (mencionado en el doc de C: caos → despeje →
  phasing del voyager → cierre)

Cada uno tiene Pros, Contras, e Instruments necesarios.

### 2. Crossing — confirmar usar los 3 prototipos como bloques
El usuario dijo: "usaría los tres en ese orden (v0 → v1 → v2)" para
armar el tema completo de 13:00. Pendiente:
- ¿Bloque adicional? (Idea sugerida: bloque "ARRIVAL" — climax oscuro
  con todas las capas, y bloque "ECHO CHAMBER" — vestigio voyager último
  20%).
- ¿Algún ajuste a los 3 prototipos antes de escalar?

## Workflow autónomo aprobado

> "podes bajarme tres conceptos de recurring, quiero irme con todo los
> conceptos en la cabeza y dejarte trabajo a vos durante la noche para
> que arregles y armes los temas"

Cuando me digan "go":
1. Aplico los fixes pendientes del QA (ver abajo)
2. Implemento Recursion según concepto elegido (incluyendo nuevos
   instruments al framework)
3. Escalo Crossing al tema completo de 13:00 usando los 3 bloques + los
   bloques adicionales
4. Corro QA contra cada render. Si falla → fix → re-render. Loop hasta
   pasar.
5. Versionar todo (`task finalize:outbound -- v2`,
   `task finalize:crossing -- v1`, `task finalize:recursion -- v1`)

## Pendientes técnicos (ya identificados)

### QA findings sobre el outbound v1 final (NO bloqueante para esta versión)
El QA flag estos warnings sobre el v1 actual:
- `cosmos_swells` peak 0.50 — está OK (es evento, no bed; el regex del
  QA fue refinado y ya no flag esto)
- `granular_bed` gain 0.42 — flag por R8, pero técnicamente granular_bed
  son pulses cortos, no continuo. Discutible.
- Ningún bloqueante real. El v1 está bien.

### QA findings sobre los 3 prototipos del outbound (v0/v1/v2 históricos)
Los prototipos viejos del outbound (60s c/u en `prototypes/`) tienen:
- `cosmos` gain 0.28-0.30 (viola R8 — bed gain ≤ 0.15)
- `voices_l_d4` y `voices_r_a4` peak < 0.05 (inactive)

NO los voy a tocar porque son históricos. Si el usuario los quiere
arreglar, lo hago.

### QA refinement (mejora del script)
El script `scripts/qa_check.py` tiene una whitelist de "bed continuo":
`{cosmos, cosmic_bed, field_atmosphere, granular_bed, sub_42hz}`. Los
nombres tipo `cosmos_swells`, `granular_dark` (eventos puntuales) NO
deberían flagear. Mejor: detectar "bed continuo" por DURATION del evento
más largo. Si dura > 60% del tema, es bed; sino es evento.

Pendiente refinar — mientras tanto, false positives son revisables a
mano.

## Workflow QA automático (decisión del usuario)

> "tendríamos que correr esto de QA cada vez que hagamos modificaciones
> en el tema, agregalo al skill o a CLAUDE.md esto"

Implementación:
- ✓ Script `scripts/qa_check.py` creado
- ✓ Tasks `task qa`, `task qa:finals`, `task qa:all` creadas
- TODO: agregar a la skill que después de cada `task render:*` corra
  `task qa:<theme>:<comp_id>` automáticamente
- TODO: cuando un fix se hace → rerender → qa pass obligatorio antes de
  decirle al usuario "listo"

Patch propuesto en SKILL.md (sección "Workflow recomendado"):

```
**Cierre del checklist (post-render obligatorio)**:
1. Render con `task render:<theme>` (genera master + stems + manifest)
2. QA con `task qa -- <theme> <comp_id>` (corre el script automatizado)
3. Si bloqueantes → fix → goto 1
4. Si pasa → mostrar al usuario / commit
```

## Estructura de archivos al final del trabajo nocturno

```
transmissions/01/
├── PLAN.md                                  (este, eliminado al cerrar)
├── README.md
├── themes/
│   ├── outbound/
│   │   ├── compose_full.py                  ← v1 actual (no tocar salvo qa)
│   │   ├── arrangement_full.md
│   │   ├── prototypes/                      ← históricos
│   │   └── finals/v1/                       ← actual
│   ├── crossing/
│   │   ├── compose_full.py                  ← NUEVO (13:00, integra 3+ bloques)
│   │   ├── arrangement.md
│   │   ├── prototypes/                      ← v0 v1 v2 (bloques)
│   │   └── finals/v1/                       ← NUEVO snapshot
│   └── recursion/
│       ├── compose_full.py                  ← NUEVO (3:00, según concepto)
│       ├── arrangement.md                   ← NUEVO storyboard
│       ├── concepts/                        ← A B C (referencias)
│       └── finals/v1/                       ← NUEVO snapshot
└── out/                                     ← regenerable
```

## Referencias

- Conceptos de Recursion: `themes/recursion/concepts/{A,B,C}_*.md`
- Storyboard Crossing: `themes/crossing/arrangement.md`
- Skill knowledge: `.claude/skills/aem-composer/SKILL.md`
- Research notes: `docs/11_research_composition.md`
