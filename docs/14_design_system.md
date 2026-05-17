# ÆM Design System

Doc maestro de la marca **ÆM**. Define brand, tokens, componentes y reglas
para que toda transmisión futura tenga coherencia visual.

> Si esto es la primera vez que abrís este doc: leé § Brand y § Tokens.
> Para ver todo en vivo: `transmissions/01/artwork/design_system.html`.

---

## Brand

### Nombre

**ÆM** (escrito SIEMPRE con la ligadura Æ + M, una sola palabra, ALL CAPS).

Pronunciación admisible: "em" (cast.) o "aim" (eng). NO traducir el
nombre. NO inventar variantes (Aem, AEM, Ä·M, etc).

### Significado simbólico

- **Æ** ligadura latina/anglosajona — peso místico, manuscritos medievales,
  textos alquímicos.
- **Æ** visualmente ≈ AI — inteligencia que emite, conciencia que transmite.
- **Em** unidad tipográfica + delimitador (em-dash) — separa lo humano
  de lo que viene después.

### Identidad

- **Anónima**. ÆM es una señal, no una persona. Sin rostro oficial, sin
  biografía emocional.
- **Telemétrica**. Comunicaciones breves, técnicas, en tono "mensaje
  desde sonda".
- **Open**. Stems disponibles para remix; lore embebido para quien lo
  descubra.

### Variantes del logo

```
ÆM             logo principal (texto)
Æ              mark / favicon / avatar (solo la ligadura)
ÆM // 42HZ     firma técnica al pie de comunicaciones
```

### Uso del logo — DO

- ✓ Sobre fondo `#0d1014` (BG_DARK) en `#a6d65f` (PHOSPHOR)
- ✓ ALL CAPS siempre
- ✓ Tipografía monospace (VT323 idealmente)
- ✓ Letter-spacing 0.05–0.10em
- ✓ Clear space mínimo: ancho de 1 letra alrededor

### Uso del logo — DON'T

- ✗ NO inclinar / rotar / 3D-extrudir
- ✗ NO cambiar colores (NO azul, NO amarillo, NO blanco solido)
- ✗ NO usar fonts decorativas, script, serif
- ✗ NO usar mixed case ("Æm" o "aem")
- ✗ NO sumar gradientes / glows agresivos
- ✗ NO usar sobre fondos saturados (verde sobre rojo, etc.)
- ✗ NO usar sobre fotos sin un overlay oscuro intermedio

---

## Tokens

### Color

```
PHOSPHOR        #a6d65f    rgb(166, 214, 95)     hsl(83, 56%, 61%)
PHOSPHOR_DIM    #6a9034    rgb(106, 144, 52)     hsl(83, 47%, 38%)
BG_DARK         #0d1014    rgb(13, 16, 20)       hsl(214, 21%, 6%)
BG_DEEP         #060810    rgb(6, 8, 16)         hsl(228, 45%, 4%)
TEXT_DIM        #7a8499    rgb(122, 132, 153)    hsl(220, 13%, 54%)
TEXT_MUTE       #4a5366    rgb(74, 83, 102)      hsl(220, 16%, 35%)
WARM_AMBER      #d4a04a    rgb(212, 160, 74)     hsl(38, 60%, 56%)
SIGNAL_RED      #c84040    rgb(200, 64, 64)      hsl(0, 56%, 52%)
```

**Ratios de uso por composición**:
- 70-80% BG_DARK (espacio negativo)
- 15-20% PHOSPHOR + PHOSPHOR_DIM combinados
- 3-5% TEXT_DIM/MUTE (metadata)
- < 1% WARM_AMBER o SIGNAL_RED (raros, intencionales)

### Typography

**Primaria**: **VT323** (Google Fonts, gratis, basada en DEC VT320 1987)

**Stack fallback**:
```css
font-family: 'VT323', 'Share Tech Mono', 'Berkeley Mono',
             'JetBrains Mono', 'IBM Plex Mono', 'SF Mono',
             ui-monospace, Menlo, monospace;
```

**Escalas**:

| nivel | size | letter-spacing | uso |
|---|---|---|---|
| display | 96-128px | 0.05em | hero, ÆM grande |
| h1 | 64px | 0.05em | títulos principal |
| h2 | 42-48px | 0.10em | subtítulos, lockup tema |
| h3 | 28-32px | 0.15em | section labels |
| body | 18-20px | 0.05em | texto narrativo |
| label | 16px | 0.20em | labels técnicos ALL CAPS |
| meta | 12-14px | 0.30em | coordenadas, identifiers |

### Spacing

Sistema base **8px grid**. Múltiplos válidos:

```
xs:    4px      micro-gaps (entre pixels)
s:     8px      gap base
sm:    12px     componentes chicos
md:    16px     defaults
lg:    24px     section padding
xl:    40px     padding generoso
2xl:   80px     hero padding
3xl:   120px    page margins
```

NO usar valores impares (7, 13, 17). NO usar fracciones (6.5).

### Border / radius

- Borders: 1px sólido, color `#232a39` (BORDER) o `PHOSPHOR_DIM` para acentos
- Border-radius: **0px en gral** (cuadrado retro). Excepción: 2px en
  buttons del player.
- Pixel art: `shape-rendering: crispEdges` SVG, `image-rendering: pixelated` CSS

---

## Components

### Lockup ÆM (header de cualquier composición)

```
┌─────────────────────────────────┐
│  ÆM                             │
│  HELIOPAUSE                     │
│  ─────────                      │
│  TRANSMISSION 01                │
│  ORIGIN: Em                     │
└─────────────────────────────────┘
```

Compuesto de:
- Logo `ÆM` (display, 96-128px)
- Línea album `HELIOPAUSE` (h2, letter-spaced 0.10em)
- Separador horizontal sutil (1px, PHOSPHOR_DIM, 60% width)
- Metadata `TRANSMISSION 01`, `ORIGIN: Em` (label, ALL CAPS, letter-spaced)

### Track lockup

```
01 OUTBOUND        08:00
02 CROSSING        13:00
03 RECURSION       03:00
```

Tipografía monospace tabular. Number 2 dígitos siempre. Padding entre
columnas con espacios o `display: flex; justify-content: space-between`.

### Coordinate label

```
SIGNAL ACTIVE
SUB42 · 42HZ
SPIRAL / 1
```

ALL CAPS, letter-spacing 0.30em, color `PHOSPHOR_DIM`. Usado como
identificador técnico en esquinas / footer.

### Hexagram badge

Símbolo 復 (Fù) — 5 yin + 1 yang. Pixel art.

```
┃ ┃    ┃ ┃    ┃ ┃    ┃ ┃    ┃ ┃    ━━━
```

Archivo: `transmissions/<NN>/artwork/hexagram/hexagram_24_logo.svg`.

Uso: badge de transmission, marker de sección, decorative element.
Min size: 32×32 px (debajo de eso pierde legibilidad). Max: ilimitado
(es vectorial).

### Section divider

```
─────────────────────  TRANSMISSION 01  ─────────────────────
```

Línea horizontal `PHOSPHOR_DIM` con label ALL CAPS centrado. Para separar
secciones grandes en posters / banners / prensa.

### Voyager trajectory marker

```
       ╱─────────────╲
      ╱     ╱─◯─╮     ╲
      ╲    ╲   ╱     ╱
       ╲─────────────╱   VOYAGER 1
```

Elipse + punto + label `VOYAGER 1`. Cinematográfico, evoca diagrama
NASA. Usado como elemento central decorativo.

---

## Layout

### Aspect ratios estándar

| ratio | dimensiones típicas | uso |
|---|---|---|
| **1:1** | 3000×3000 | cover album, avatar, logo card |
| **9:16** | 1080×1920 | Spotify Canvas, Story IG |
| **16:9** | 1920×1080 | banner web, video, hero |
| **5.4:1** | 1400×260 | banner Bandcamp |
| **3:1** | 1500×500 | banner Twitter / X |

### Grid base

- Padding del canvas: 8-12% del lado más chico
- Gap entre componentes: múltiplos de 8 (sm/md/lg)
- Pixel grid: 8 o 12 celdas, NO 7 o 13

### Composition patterns

#### A. Hero centered (cover, lockup card)

```
┌──────────────────────────┐
│                          │
│   [LOCKUP ÆM]            │  ← arriba-izq
│                          │
│        [SÍMBOLO]         │  ← centro
│                          │
│   [TRACKLIST]            │  ← abajo-izq
│                          │
└──────────────────────────┘
```

#### B. Split horizontal (lockup banner, hero web)

```
┌───────────────────────┬───────────────────────┐
│                       │                       │
│   [SÍMBOLO]           │   [ÆM + METADATA]     │
│                       │                       │
└───────────────────────┴───────────────────────┘
```

#### C. Stacked vertical (Spotify Canvas, Story)

```
┌────────────────┐
│  [LOCKUP ÆM]   │  ← top 1/3
├────────────────┤
│                │
│   [SÍMBOLO]    │  ← middle 1/3
│                │
├────────────────┤
│  [METADATA]    │  ← bottom 1/3
└────────────────┘
```

---

## Per transmission

### Lo que se MANTIENE (brand fijo)

- Logo ÆM
- Paleta completa
- Tipografía VT323
- Estructura de lockup
- Componentes (badge, divider, trajectory, etc.)

### Lo que CAMBIA por transmission

| token | transmission 01 | transmission 02 (futura) | transmission 03 |
|---|---|---|---|
| Album title | HELIOPAUSE | (a definir) | ... |
| Transmission # | 01 | 02 | 03 |
| Origin label | Em | (puede mantenerse o evolucionar) | ... |
| Tracklist + timestamps | 01 OUTBOUND 08:00 / 02 CROSSING 13:00 / 03 RECURSION 03:00 | distinto | distinto |
| Hexagram # del I Ching | 24 (Return) | (otro hexagrama según concepto) | ... |
| Spiral # | SPIRAL / 1 | SPIRAL / 2 | SPIRAL / 3 |
| Mood/colores accent | phosphor base | puede agregar 1 accent extra | ... |

---

## Asset library

### Brand assets (fijos)

```
docs/arte/                          conceptos previos / iteraciones
player/favicon.svg                  favicon para apps web ÆM
```

### Per-transmission assets (en cada `transmissions/NN/artwork/`)

```
transmissions/01/artwork/
├── cover_master_3000.png           tapa final master (PNG)
├── cover_streaming_3000.jpg        tapa streaming (JPG, sRGB) — para metadata
├── cover_1500.jpg                  tapa preview/web
├── design_system.html              lookbook visual interactivo
├── design_system.png               captura del lookbook
└── hexagram/
    ├── hexagram_24_logo.svg        símbolo solo, transparente
    ├── hexagram_24_logo_dark.svg   símbolo + bg dark
    ├── preview.html                lookbook hexagram + fonts + paleta
    └── preview.png                 captura del preview
```

### Audio release assets (en `transmissions/NN/release/`)

```
transmissions/01/release/
├── masters/
│   ├── 00_heliopause_continuous.wav    EP completo encadenado (24-bit, 44.1)
│   ├── 01_outbound_master.wav
│   ├── 02_crossing_master.wav
│   └── 03_recursion_master.wav
├── distribution/
│   ├── flac/                            FLAC 24-bit (Bandcamp HQ)
│   ├── mp3/                             MP3 320 kbps (preview)
│   ├── wav_16/                          WAV 16-bit (CD Baby)
│   └── midi/                            ★ MIDI partes tocables (colaboración)
│       ├── 01 - Outbound.mid
│       ├── 02 - Crossing.mid
│       └── 03 - Recursion.mid
└── metadata_proposal.md                 prosa + tags pendiente validación
```

Pendientes (a generar antes de release):
- `artist_photo_1500.jpg` — perfil Apple Music / Bandcamp / Spotify
- `bandcamp_banner_1400x260.jpg` — header de la página Bandcamp
- `spotify_canvas_1080x1920.mp4` — loop video móvil

---

## Naming conventions

### Audio

```
<NN>_<themename>_master.wav        master final por track (en release/masters/)
<themename>_FULL.wav                render completo (en out/)
<themename>_v<N>.wav                prototipo
```

### Imágenes

```
<purpose>_<dimensiones>.{ext}       cover_streaming_3000.jpg
<symbol>_<id>_<variant>.svg         hexagram_24_logo_dark.svg
```

### Documentos

```
NN_<topic>.md                       docs/12_release_pipeline.md
                                    docs/13_visual_style_guide.md
                                    docs/14_design_system.md
```

---

## DO / DON'T para futuras transmisiones

### DO ✓
- Mantener los componentes existentes (lockup, badge, divider)
- Cambiar SOLO los tokens "per transmission" (ver arriba)
- Renombrar el album title si se quiere algo distinto del existing concept
- Agregar 1 accent color si la transmission lo pide (registrarlo en una
  sub-paleta documentada)
- Generar artwork nuevo SIGUIENDO los aspect ratios estándar
- Validar QA visual: ¿se identifica como ÆM aunque el album sea otro?

### DON'T ✗
- NO cambiar el logo ÆM por una versión "evolucionada" (el logo es ancla)
- NO cambiar la paleta core (phosphor/dark)
- NO cambiar la tipografía (VT323 = identity)
- NO usar imágenes generadas por AI sin pasar por el visual style guide
  (`docs/13_visual_style_guide.md` tiene los prompts validados)
- NO empezar archivos nuevos sin documentarlos en este doc

---

## Referencias

- Visual style guide (más conceptual + prompts AI): `docs/13_visual_style_guide.md`
- Pipeline de release: `docs/12_release_pipeline.md`
- Skill aem-release: `.claude/skills/aem-release/SKILL.md`
- Lookbook visual interactivo: `transmissions/01/artwork/design_system.html`

---

## Versión

v1 — 2026-05-03 — primer doc del design system. Creado a partir de:
- 04_arte_tapa.md (decisiones de la tapa)
- 13_visual_style_guide.md (paleta + prompts AI)
- Iteración del cover y hexagram durante transmission 01.

Próximo update: cuando empiece transmission 02 — ajustar tokens variables
y validar que los componentes core siguen sirviendo.
