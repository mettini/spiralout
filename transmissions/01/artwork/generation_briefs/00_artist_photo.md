# 00 · Foto del artista

**Uso**: Apple Music profile, Bandcamp avatar, Spotify for Artists, perfil
de redes. **Obligatoria** para tener perfil en plataformas.

**Resolución**: 1500×1500 mínimo (Spotify acepta hasta 4000×4000)
**Aspecto**: 1:1 cuadrado
**Formato**: JPG sRGB, ≤ 4 MB

ÆM es **anónimo, sin rostro oficial**. Tres opciones (elegir una):

---

## Opción A — Logo art (recomendada — alineada con identidad)

**Prompt**:
```
the letters "ÆM" in retro CRT phosphor green pixel font, large centered,
monochromatic phosphor green #a6d65f on deep cosmic black background
#0d1014, slight CRT scanlines, subtle vignette, vector pixel art with
crisp edges and no antialiasing, monospace letterspacing, minimal
composition, 1980s sci-fi terminal aesthetic, vintage NASA control
panel, cosmic loneliness, square format
```

**Negative**:
```
photo, photorealistic, 3d render, blur, soft, neon, synthwave,
vaporwave, cyan, magenta, pink, gradient, character, face, person,
mascot, ornament, decorative, signature, watermark, glitched text,
extra letters, oversaturated
```

**Settings**: Resolution 1024×1024 (después upscale a 1500), Steps 4, CFG 1.0

---

## Opción B — Símbolo abstracto del lore (hexagrama 24)

**Prompt**:
```
abstract pixel art symbol of I Ching hexagram 24 (復 Fù — return, the
turning point), five broken yin lines and one solid yang line at bottom,
phosphor green #a6d65f on cosmic black #0d1014, large centered, vector
pixel art with crisp edges and no antialiasing, monospace coordinate
labels around the symbol like "HEX 24" and "復 FÙ", retro CRT terminal
aesthetic, vintage 1977 NASA mission documentation style, square format,
contemplative minimal, no decorative elements
```

**Negative**: igual que opción A

**Settings**: igual que opción A

---

## Opción C — Silueta cinematográfica (si querés cara)

**Prompt**:
```
cinematic silhouette of a person from behind sitting in front of a CRT
monitor displaying green phosphor terminal text, dark room interior,
single light source from screen casting monochromatic green light on
the figure, vintage 1980s computer terminal, deep blacks, moody
contemplative atmosphere, cosmic loneliness, square 1:1 composition,
4k cinematic, film grain, like a still from a 1979 sci-fi film
(Alien, Solaris)
```

**Negative**:
```
[base anterior] + smile, looking at camera, multiple people, modern
office, laptop, color photography, bright colors, decorative
```

**Settings**: igual

---

## Iteración

1. Generar **6-8 imágenes** con la opción elegida.
2. Elegir 2-3 que tiren bien.
3. Con seed fijo de la mejor → variar incrementalmente:
   - "+ subtle scanlines" / "- scanlines"
   - "+ slight vignette" / "darker vignette"
   - "+ noise grain" / "clean"
4. Render final a 1500×1500 (usar hires fix si hace falta).

## Nota

Si la opción A te tira pero querés algo MÁS, considerá pedirla con la
hexagrama integrada al ÆM:
```
the letters "ÆM" in pixelated phosphor green centered top-half, hexagram
24 (5 broken lines + 1 solid) symbol pixel art centered bottom-half, ...
```

Eso unifica las dos identidades visuales.
