# 04 · Poster vertical / IG carousel

**Uso**: poster vertical para print (A3, A2), carousel IG (slide 4:5),
flyer impreso, póster en pared.

**Resolución**:
- Print A3 (29.7×42 cm 300dpi): **3508×4961**
- IG portrait: **1080×1350**
**Aspecto**: 4:5 vertical
**Formato**: PNG si va con texto encima, JPG sRGB para final

---

## Prompt principal

```
vertical 4:5 portrait poster, deep cosmic black background dominant,
ÆM logotype large in pixelated phosphor green at the top, "HELIOPAUSE"
in monospace VT323 typography below in smaller scale with generous
letter-spacing, hexagram 24 (復 Fù) symbol pixel art prominent
centered, dotted Voyager 1 trajectory subtle behind, tracklist in
monospace at the bottom-left in coordinate label style "01 OUTBOUND
08:00 / 02 CROSSING 13:00 / 03 RECURSION 03:00", "TRANSMISSION 01"
mission badge in lower-right corner, monochromatic phosphor green
#a6d65f on cosmic black #0d1014, vintage NASA mission documentation
1977 aesthetic, retro CRT phosphor monitor, pixel-perfect grid edges,
no antialiasing, contemplative cosmic loneliness, generous padding
margins, minimalist composition like a 1980s Criterion Collection
poster
```

## Negative

```
[base anterior] + landscape, horizontal, busy composition, modern UI,
glossy finish, photorealistic, character, face, neon, synthwave,
gradient, multiple colors, watercolor
```

## Settings

- Resolution: **832×1024** o **1024×1280** (después upscale a 1080×1350 o A3)
- Steps: 4-6
- CFG: 1.0-1.5

---

## Variaciones

### V1 — Print poster minimalista
```
vertical poster minimalist composition, single hexagram 24 symbol
pixel art huge centered occupying 60% of the frame, ÆM HELIOPAUSE
typography small at the top in monospace, "復 FÙ · THE TURNING POINT"
small at the bottom, lots of negative space, deep cosmic black with
single phosphor green symbol, vintage Swiss design poster aesthetic
mixed with retro CRT terminal, 1980s sci-fi minimalism
```

### V2 — IG carousel slide 1 (intro)
```
vertical poster IG portrait 4:5, ÆM logotype centered upper-third in
pixel CRT phosphor green, "HELIOPAUSE" in monospace below, single
small hexagram 24 symbol in lower-third, deep cosmic black background,
subtle vignette, generous padding, minimal composition, retro NASA
control panel aesthetic
```

### V3 — IG carousel slide 2 (tracklist focus)
```
vertical poster IG portrait, deep cosmic black background, tracklist
prominently centered in monospace VT323 phosphor green:
"01 — OUTBOUND — 08:00
02 — CROSSING — 13:00
03 — RECURSION — 03:00"
generous letter-spacing, ÆM small upper-left, hexagram 24 symbol
small lower-right, vintage NASA mission documentation aesthetic
```

### V4 — IG carousel slide 3 (concept)
```
vertical poster IG portrait, technical diagram of the heliopause
threshold, sun symbol upper portion, dotted Voyager 1 trajectory
crossing a curved boundary line in the middle, interstellar void in
the lower portion, coordinate annotations "TRANSMISSION 01 / 42HZ /
SPIRAL 1" in monospace phosphor green, vintage NASA mission diagram
aesthetic, minimal composition, deep cosmic black
```

---

## Iteración

1. Para serie IG (carousel): generar V2, V3, V4 con **mismo seed** para
   coherencia visual. Postear los 3 como slides en orden.
2. Para print: generar V1 a max resolution + agregar tipografía VT323
   real en Figma encima.
3. Para A3 print: hires fix a 3508×4961.

## Tip

Si vas a print, **pedí color profile sRGB** explícito al exportar.
Adobe RGB / ProPhoto distorsionan colores en imprenta.
