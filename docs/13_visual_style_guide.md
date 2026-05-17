# Visual style guide — ÆM / Heliopause

Doc maestro de estética visual del proyecto. Para alimentar AI image
generators (Stable Diffusion / FLUX) y mantener coherencia entre piezas
(arte de tapa, foto del artista, banners, Spotify Canvas, posts).

---

## Línea artística

**Una frase**: *Panel de control de tierra para una sonda interestelar
que ya no responde.*

### Núcleo estético
- **Retro sci-fi terminal** — phosphor monitor verde, CRT, vector wireframe
  estilo Tron / Battlezone (1980).
- **Pixel art geométrico** — formas crudas, sin antialiasing, shape-rendering
  crispEdges.
- **Cosmic minimal** — espacio negro, pocos elementos, mucho aire.
- **Vintage NASA / Soviet space program** — tipografía monoespaciada,
  diagramas técnicos, coordenadas, identificadores alfanuméricos.
- **Liturgia técnica** — el panel de control como oráculo. Hexagrama 24,
  ÆM logo, símbolos científicos sin jerarquía clara.

### Lo que NO es
- NO ilustración detallada / realista
- NO 3D photoreal
- NO synthwave neón (cyan/magenta/pink) — confundible con vaporwave
- NO grunge / texturas decorativas / fonts elaborados
- NO emojis, NO mascotas, NO faces

---

## Paleta de colores

Definitiva. **NO improvisar otros colores** salvo que sea decisión consciente.

```
PHOSPHOR          #a6d65f   accent principal — texto, símbolos, líneas
PHOSPHOR_DIM      #6a9034   media — sombras del phosphor, líneas atenuadas
BG_DARK           #0d1014   fondo principal — negro azulado del CRT
BG_DEEP           #060810   negro más profundo (vacío cósmico, opcional)
WARM_AMBER        #d4a04a   accent muy raro (alertas, highlights — usar 2-3 veces total)
TEXT_DIM          #7a8499   metadatos secundarios
TEXT_MUTE         #4a5366   labels terciarios, separadores
SIGNAL_RED        #c84040   solo errores / alarmas / cierre dramático
```

Ratio típico: **75% bg negro · 20% phosphor (full + dim) · 5% otros**.

NO saturación alta. NO gradients extremos. Todo se siente "monitor de
phosphor verde que tiene 30 años en el rack".

Ver swatches en vivo: `transmissions/01/artwork/hexagram/preview.html`.

---

## Tipografía

### Primaria — **VT323**

[VT323 — Google Fonts](https://fonts.google.com/specimen/VT323) ·
gratis · pesa 21 KB. Exactamente la fuente del terminal **DEC VT320**
(1987) — el monitor de phosphor verde de la era. Es la tipografía que
usan películas como **Alien** (1979) en los displays del Nostromo, y
panels de **2001: A Space Odyssey**.

Aplicación:
- Headers, labels, identificadores técnicos
- Texto en HTML / web / video
- Contraseña: si vas a renderear texto, usá VT323.

Importar:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
```

```css
font-family: 'VT323', monospace;
```

### Secundarias (opcionales)

- **Share Tech Mono** — alternativa más limpia, también monospace retro
- **Major Mono Display** — más futurista, para títulos LARGE one-shot

### Reglas tipográficas

- **Letter-spacing generoso** en labels: 0.2em - 0.4em
- **ALL CAPS** para etiquetas, labels técnicos, identificadores
- Mixed case **raro** — solo para texto narrativo "humano"
- Jerarquía: 12-16px metadata, 18-24px labels, 36-96px headers
- VT323 se ve MEJOR en tamaños grandes (24px+) — en chico pierde el
  carácter retro

---

## Orientación / layout / grid

### Composiciones por aspect ratio

| ratio | uso | guideline |
|---|---|---|
| **1:1 cuadrado** | Cover de tapa, símbolo logo, avatar artista | composición centrada o asimétrica con lockup ÆM arriba-izq + diagrama centro-der |
| **1:1 pero portrait** (1080×1920) | Spotify Canvas (mobile vertical) | elementos clave centrados en mitad superior, espacio para play UI abajo |
| **16:9** (1920×1080) | Banner, hero, video | lockup izquierda + ÆM/info derecha, mucho aire arriba/abajo |
| **5.4:1 banner** (1400×260) | Bandcamp header | logo izq + tracklist o tagline der, símbolo decorativo centro |

### Grid base

- **Margin generoso**: 8-12% del ancho como padding mínimo
- Elementos alineados a un grid implícito (8px / 12px / 16px múltiplos)
- Pixel art = grid de 8 o 12 celdas, NUNCA 7 o 13 (rompen el ritmo)

### Composición — lo que SIEMPRE funciona

1. **Lockup en esquina superior izquierda** (estilo "ID de canal de
   transmisión") — ÆM + HELIOPAUSE en ALL CAPS letter-spaced
2. **Centro vacío grande** o con elemento simbólico (hexagrama, elipse,
   wireframe)
3. **Metadatos técnicos en columna izquierda inferior** — coordenadas,
   tracklist, identificadores
4. **Algún elemento alineado a la derecha** que rompa la simetría
   (etiqueta `VOYAGER 1`, marker, etc.)

Ejemplo: el cover actual de Heliopause sigue exactamente este patrón.

### Reglas de oro de layout

1. **Si dudás → menos**. Espacio negro > más elementos. Hay un MÍNIMO de
   3 elementos visuales clave: lockup ÆM, símbolo central, metadatos.
2. **Asimetría con peso visual balanceado**. NO simétrico literal — los
   ojos se aburren. Un elemento pesa a la izquierda, otro chico equilibra
   a la derecha.
3. **Pixel siempre cuadrado** (`shape-rendering="crispEdges"` SVG,
   `image-rendering: pixelated` CSS).
4. **Vignette MUY sutil** o scratch overlay para el "aged CRT feel".
   Opcional. Mejor sin que con grueso.

---

## Motivos visuales recurrentes

1. **Hexagrama 24** (復 Fù) — 5 líneas yin + 1 yang. El símbolo del retorno.
   Hecho con pixels cuadrados.
2. **ÆM logo** — pixelado/CRT phosphor verde. Aparece como mark estable.
3. **Voyager 1 trayectoria** — elipse + punto + label "VOYAGER 1".
4. **Wireframe landscape** — montañas + grid del piso (estilo Battlezone).
5. **Coordenadas / identificadores** — `TRANSMISSION 01`, `ORIGIN: Em`,
   `SIGNAL ACTIVE`, `42HZ`, `SPIRAL / 1`, etc.
6. **Sub-líneas técnicas** — dotted lines, dashes, separadores monospace.
7. **Tracklist con timestamps** — `01 OUTBOUND  08:00`.
8. **Borders sutiles** — la imagen como dentro de un monitor antiguo
  (vignette muy sutil, bordes con scratch/noise leve).

---

## Activos visuales del proyecto (estado actual)

```
docs/arte/
└── 04_arte_concepto_*.svg / .png   conceptos previos del cover

transmissions/01/artwork/
├── cover_master_3000.png           ✓ tapa final 3000×3000 (PNG master)
├── cover_streaming_3000.jpg        ✓ tapa 3000×3000 sRGB JPG (delivery)
├── cover_1500.jpg                  ✓ tapa 1500×1500 (preview/web)
└── hexagram/
    ├── hexagram_24_logo.svg            ✓ símbolo solo (transparente, 1200×1200)
    ├── hexagram_24_logo_dark.svg       ✓ símbolo + bg dark
    ├── hexagram_24_lockup.svg          ✓ símbolo + texto "HEX 24 / RETURN"
    └── hexagram_24_card_16_9.svg       ✓ banner 1920×1080 con ÆM + HEX 24

player/
└── favicon.svg                     ✓ ÆM mini favicon
```

### Por generar (prioridad para release)

| pieza | uso | tamaño |
|---|---|---|
| **Foto del artista** | perfil Apple Music / Bandcamp avatar / Spotify for Artists | 1500×1500 mín |
| **Banner Bandcamp** | header de la página | 1400×260 |
| **Spotify Canvas** | loop video móvil 3-8s | 1080×1920 video |

### Opcionales (post-release)

| pieza | uso | tamaño |
|---|---|---|
| Variantes de cover por track | si distribuís cada track como single | 3000×3000 |
| Press kit photos | si hacés prensa | varias |
| Lyric video / visualizer | YouTube | 1920×1080 |
| Posters / merchandising | físico | grande |

---

## AI image generation — recomendaciones para Mac (sin pagar)

### Mi recomendación: **Draw Things** (gratis, App Store, optimizado Apple Silicon)

- App Mac nativa, GUI completa, **gratis**, sin cuenta requerida.
- Soporta SDXL, FLUX, SD 1.5, LCM, ControlNet, LoRAs.
- Optimizado para chip M1/M2/M3/M4 (Metal Performance Shaders).
- Modelo recomendado para arrancar: **FLUX.1 schnell** (Apache 2.0, calidad
  SOTA, rápido — 4 steps por imagen).
- App store: https://apps.apple.com/us/app/draw-things-ai-generation/id6444050820

### Alternativas

- **DiffusionBee** (gratis, Mac, más viejo pero simple): https://diffusionbee.com/
- **ComfyUI** (gratis, GUI node-based, más control, complejo de setup)
- **Diffusers HuggingFace** (Python lib, cero GUI, máximo control via código)
- **Midjourney** / **DALL-E** (pago — para pasar de open source no aplican)

### Modelos para nuestra estética

Por orden de recomendación:

1. **FLUX.1 schnell** (Apache 2.0) — best quality, runs locally, ideal para
   arte conceptual. 4 steps inference.
2. **SDXL Base 1.0** (CreativeML Open RAIL++ — open source) — más viejo
   pero TONS de checkpoints custom para retro/sci-fi/pixel art.
3. **SDXL fine-tunes** — modelos custom con estética específica:
   - "Realistic Vision XL" (para fotos del artista realistas)
   - "DreamShaper XL" (para conceptual art)
   - "Pixel Art XL" (LoRA específico para pixel)
   - "Retro Diffusion" / "1980s Sci-Fi" LoRAs

---

## Prompts base — copy/paste templates

Sintaxis: `[subject], [style], [details], [lighting], [color]. Negative: [...]`

### Foto del artista — opciones

**A. Logo artistic (recomendada — alineada con identidad anónima)**

```
positive:
  the letters "ÆM" in retro CRT phosphor green pixel font, large centered,
  black background, vintage computer monitor aesthetic, slight scanlines,
  vignette, vector pixel art, crisp edges, monospace letterspacing,
  minimal composition, 80s sci-fi terminal, cosmic loneliness

negative:
  realistic, photo, blur, gradient, neon, synthwave, cyan, magenta, pink,
  colorful, soft, decorative, ornament, mascot, character, face, person,
  3d render, watercolor, painting, signature, watermark, text artifacts
```

**B. Símbolo abstracto del lore (hexagrama 24 stylized)**

```
positive:
  abstract pixel art symbol, I Ching hexagram 24 (five broken lines and
  one solid line at bottom), phosphor green on black, retro CRT terminal,
  vintage NASA control panel aesthetic, minimal geometric, crisp pixel
  edges, vector style, monospace technical labels around the symbol,
  shape rendering crisp, no antialiasing, 1980s computer art

negative:
  realistic, photo, gradient, blur, soft, decorative, character, face,
  3d, neon, vaporwave, synthwave, watercolor, signature
```

**C. Foto literal del artista (si querés cara)**

```
positive:
  silhouette of a person in front of a CRT monitor displaying green text,
  dark room, single light source from screen, monochromatic green
  phosphor light on the face, vintage computer terminal aesthetic, 1980s
  control room, cinematic, moody, contemplative, 4k

negative:
  bright colors, neon, cartoon, anime, smiling, multiple people, blur,
  watermark, signature, soft, decorative, low quality
```

### Banner Bandcamp (1400×260 — apaisado)

```
positive:
  ultra-wide horizontal banner, retro sci-fi control panel layout,
  pixelated ÆM logo on left in phosphor green, hexagram 24 symbol
  centered, wireframe vector landscape with grid floor on right, deep
  space background, monospace technical labels, vintage NASA aesthetic,
  cinematic minimal, black background dominant

negative:
  realistic, photo, neon, synthwave, colorful, gradient, character,
  3d, cartoon, decorative, watermark
```

### Spotify Canvas (1080×1920 vertical, 3-8s loop)

Para un loop video, AI image gen genera frames estáticos. Usá una imagen
base + una herramienta de motion (DALL-E motion / Runway / Pika).
Alternativa: ya tenemos los SVGs vectoriales — animar con CSS / JS / SVG
animation export a video es más controlable.

```
positive:
  vertical poster, retro sci-fi vintage NASA control panel, ÆM logo at top
  in pixelated phosphor green, hexagram 24 symbol centered with subtle
  glow, dotted line trajectory of Voyager probe, wireframe landscape at
  bottom, dark cosmic background, monospace technical labels, cinematic
  composition for mobile

negative:
  horizontal, realistic photo, neon, synthwave, character, 3d, cartoon,
  watermark, signature, decorative ornament
```

### Variantes de cover por track (si releaseás como singles)

**Outbound** — más warm, sub-bass, ascensión:
```
positive:
  album cover variant, ÆM Heliopause Outbound, vertical wireframe landscape
  with mountains rising, Voyager 1 elipse trajectory, pixelated ÆM logo
  in phosphor green, "01 OUTBOUND 08:00" label, dark cosmic background
  with subtle warm amber accents, retro CRT vintage NASA aesthetic
```

**Crossing** — más oscuro, denso, reverb visual:
```
positive:
  album cover variant, ÆM Heliopause Crossing, dark cosmic threshold,
  pixelated ÆM logo in dim phosphor green, hexagram-like geometric pattern,
  field of stars dissolving into noise, "02 CROSSING 13:00" label,
  Lustmord-influenced dark ambient cover aesthetic, deep blacks
```

**Recursion** — ouroboros, espiral, retorno:
```
positive:
  album cover variant, ÆM Heliopause Recursion, spiral pattern in pixel
  phosphor green, hexagram 24 symbol prominent, infinite loop visual
  metaphor, "03 RECURSION 03:00" label, dark cosmic background, retro
  CRT vintage NASA aesthetic, contemplative minimal composition
```

---

## Workflow recomendado

1. Bajar **Draw Things** del Mac App Store (gratis).
2. Descargar **FLUX.1 schnell** desde la app (settings → model browser).
3. Setear:
   - Sampler: Euler / DPM++ 2M
   - Steps: 4-8 (FLUX schnell es rápido)
   - CFG scale: 1-3 (FLUX usa baja CFG)
   - Resolution: 1024×1024 (cover) / 1024×1792 (Canvas) / 1792×1024 (banner)
4. Probar prompts del template de arriba.
5. Iterar — bajar variaciones, elegir las mejores.
6. Si querés mantener consistencia entre imágenes, usar mismo seed +
   ajustar el prompt incrementalmente.

---

## Referencias visuales (mood board mental)

- **Game**: *Battlezone* (1980), *Tron* (1982), *Elite* (1984)
- **Sci-fi film**: *Solaris* (1972, Tarkovsky — minimalismo cósmico),
  *2001: A Space Odyssey* (control panels), *Annihilation* (cosmic dread),
  *Interstellar* (data overlays)
- **Music covers**: Lustmord *Heresy*, Steve Roach *Structures from Silence*,
  Brian Eno *Music for Airports*, Aphex Twin *Selected Ambient Works*,
  early Warp Records (Plaid, Autechre — geometric pixel art)
- **Art**: el sitio web de la NASA Voyager mission (1977-2025), control
  panels de la era Apollo, displays de submarinos militares, terminales
  CRT verdes/ámbar de los 70s/80s
- **Type**: Berkeley Mono (Berkeley Graphics), JetBrains Mono, IBM Plex
  Mono, fonts de bitmap-era (Cathode terminal)

---

## Reglas de oro para mantener coherencia

1. **Si dudás → menos**. Espacio negro > más elementos.
2. **Verde phosphor único**: nunca cyan/azul/turquesa por error.
3. **Pixel siempre cuadrado**: `shape-rendering="crispEdges"` en SVG,
   `image-rendering: pixelated` en CSS.
4. **Tipografía monospace SIEMPRE** salvo que sea texto largo narrativo.
5. **Letter-spacing generoso** en labels.
6. **Etiquetas técnicas como contenido visual**: `TRANSMISSION 01`,
   `42HZ`, `ORIGIN: Em`, no son decoración — son parte del lore.
7. **Anti-AI tells**: si la AI agrega watermarks, manos extra, faces
   inexistentes, reroll. Generar muchas iteraciones, elegir las limpias.
