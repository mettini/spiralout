# Prompt library — bloques modulares ÆM

Vocabulario / building blocks que se combinan para armar prompts coherentes.
Si querés inventar un asset nuevo, mezclá bloques de acá.

---

## Style tags (estética visual)

```
retro CRT phosphor green monitor, 1980s vintage computer terminal,
shape-rendering crisp edges, no antialiasing, pixel-perfect grid,
vector wireframe in the style of Battlezone (1980), Tron (1982),
Elite (1984), early NASA control panel telemetry display, deep cosmic
black background, monospace technical typography in the style of DEC
VT320 terminal, vintage Apollo mission interface
```

Subset minimal:
```
retro CRT phosphor green, vintage NASA control panel, pixel art,
wireframe, dark cosmic background, minimal composition
```

---

## Mood tags (clima / emoción)

```
cosmic loneliness, contemplative isolation, transmission from the
edge, signal across the void, threshold crossing, interstellar drift,
liturgy of technology, oracular machine, deep listening, silence
made visual, the moment of return
```

Por tema del EP:
- **Outbound**: launch, departure, capsule sealed, signal active, going outward, ascending
- **Crossing**: dark depth, traversing the threshold, sub-bass weight, ritualistic cosmos, temple in space
- **Recursion**: spiral return, fù 復 hexagram 24, the turning point, light returning from below

---

## Motifs (elementos recurrentes)

Visuales conceptuales del proyecto que pueden aparecer como protagonistas
o como detalles de fondo:

- **ÆM ligature** — letras Æ+M en CRT phosphor
- **Hexagram 24 (復 Fù)** — 5 líneas yin + 1 yang abajo, pixel art
- **Voyager 1 trajectory** — elipse + dot + label "VOYAGER 1"
- **Wireframe landscape** — montañas + grid floor en perspectiva
- **Coordinate labels** — `TRANSMISSION 01`, `42HZ`, `ORIGIN: Em`, `SPIRAL/1`, `SIGNAL ACTIVE`
- **Tracklist with timestamps** — `01 OUTBOUND 08:00`
- **Heliopause boundary** — círculo o curva de transición sutil
- **Spiral** — espiral logarítmica abstracta
- **CRT scanlines** — líneas horizontales sutiles del monitor
- **Vignette** — bordes oscurecidos del frame
- **Signal waveform** — onda sinusoidal estilizada
- **Star field** — puntos blancos puntuales en el fondo profundo
- **Tape reels / vintage equipment** — para el aspecto analógico

---

## Color palette (siempre)

```
phosphor green #a6d65f as primary accent (text, symbols, lines),
phosphor dim #6a9034 for shadows, deep dark background #0d1014, NO
neon, NO cyan, NO magenta, NO synthwave colors, monochromatic
green-on-black with rare warm amber accent #d4a04a for highlights only
```

---

## Negative prompt base (siempre incluir)

```
photo, photorealistic, 3d render, blur, soft, neon, synthwave, vaporwave,
cyan, magenta, pink, purple, rainbow, gradient, watercolor, painting,
character, anime, cartoon, mascot, face, smile, person looking at camera,
ornament, decorative, signature, watermark, text artifacts, glitched text,
extra hands, deformed, low quality, jpeg artifacts, oversaturated,
high contrast, HDR
```

Si vas por estilo más "documental":
```
[base anterior] + clean studio lighting, modern minimalism, white
background, glossy finish
```

---

## Composition recipes (lo que SIEMPRE funciona)

### A — Lockup esquina superior izquierda + símbolo centrado

```
ÆM logo small in upper-left corner in pixelated phosphor green, large
hexagram 24 symbol centered, monospace coordinate labels in lower-left
corner, deep cosmic black background dominant
```

### B — Símbolo lateral + texto vertical

```
hexagram 24 symbol on the left third of the frame, ÆM HELIOPAUSE
typography on the right two-thirds in monospace phosphor green,
generous padding, vintage NASA telemetry layout
```

### C — Wireframe landscape como base

```
wireframe vector landscape with mountains and grid floor at the
bottom third of the frame in the style of Battlezone (1980), deep
cosmic black sky above with subtle star field, central element [X],
ÆM logo in upper-left corner
```

### D — Diagrama técnico

```
technical NASA-style diagram showing Voyager 1 elliptical trajectory
with dot marker labeled "VOYAGER 1", coordinate annotations in
monospace typography, dotted lines, all in phosphor green on cosmic
black background, vintage 1977 mission documentation aesthetic
```

---

## Tipografía dentro de la imagen (cuándo aparece)

Si el prompt incluye texto:
```
text in DEC VT320 terminal monospace font, pixelated phosphor green
characters, ALL CAPS, generous letter-spacing
```

Pero típicamente: **mejor agregar el texto DESPUÉS** en Figma/Photoshop.
Las AI suelen inventar texto inteligible — más confiable poner el texto
con tipografía real (VT323 desde Google Fonts) sobre la imagen base.

---

## Cómo combinar bloques

Estructura recomendada de prompt:

```
[COMPOSITION RECIPE] + [MOTIFS principales] + [MOOD] + [STYLE TAGS]
+ [COLOR PALETTE]
```

Ejemplo (hero background):

```
wireframe vector landscape with mountains and grid floor in the style
of Battlezone (1980) at the bottom third, deep cosmic black sky with
subtle star field above, hexagram 24 (復 Fù) symbol pixel art centered
in the upper portion, dotted Voyager 1 elliptical trajectory crossing
through, contemplative isolation, threshold crossing mood, retro CRT
phosphor green monitor aesthetic, vintage NASA control panel layout,
pixel-perfect grid, monochromatic green-on-black, cosmic loneliness,
no antialiasing
```

---

## Referencias visuales (mood board mental)

- **Game**: Battlezone (1980), Tron (1982), Elite (1984), Eve Online UI
- **Sci-fi film**: Solaris (1972 Tarkovsky), 2001: A Space Odyssey
  (control panels, HAL displays), Annihilation (cosmic dread),
  Interstellar (data overlays), Alien (1979 Nostromo terminals)
- **Real**: NASA Voyager mission documentation (1977), Apollo control
  panels, Soviet space program telemetry, vintage submarine sonar displays
- **Music covers**: Lustmord — Heresy, Steve Roach — Structures from
  Silence, Brian Eno — Music for Airports, Aphex Twin — Selected
  Ambient Works, early Warp Records (Plaid, Autechre — geometric)
