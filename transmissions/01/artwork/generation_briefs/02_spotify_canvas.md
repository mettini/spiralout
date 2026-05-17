# 02 · Spotify Canvas (mobile vertical loop)

**Uso**: Spotify mobile — el video loop 3-8s que aparece detrás del
artwork mientras suena el track. Es OPCIONAL pero **suma muchísimo**
visualmente. La mayoría de users de Spotify están en mobile.

**Resolución**: 1080×1920 (9:16 vertical)
**Formato**: MP4 H.264, 24-30 fps, max 8s, max 8MB
**Cómo entregar**: Spotify for Artists upload tool (después del release)

Una imagen estática NO sirve para Canvas. Hay que generar el frame y
después animarlo. Workflow:
1. Generar imagen estática con AI (este brief)
2. Animar con CSS / SVG / After Effects / Pika / DaVinci

---

## Prompt frame estático

```
vertical 9:16 cinematic poster, deep cosmic black background dominant,
hexagram 24 (復 Fù) symbol pixel art prominent centered in the upper
half, monochromatic phosphor green #a6d65f on cosmic black #0d1014,
small ÆM logo in upper-left corner in pixelated phosphor green,
"HELIOPAUSE" typography in monospace VT323 below the symbol with
generous letter-spacing, dotted Voyager 1 trajectory faint in the
background, "TRANSMISSION 01" coordinate label in lower-center, retro
CRT vintage NASA control panel aesthetic, pixel-perfect grid edges,
contemplative cosmic loneliness, mobile poster composition with
generous padding for play UI overlay at the bottom
```

## Negative

```
[base anterior] + horizontal, landscape orientation, busy composition,
text artifacts, decorative elements, character, face, neon, synthwave
```

## Settings

- Resolution: **1024×1792** (FLUX usa multiples de 64; después
  upscale a 1080×1920)
- Steps: 4
- CFG: 1.0

---

## Variaciones por track (opcional — un Canvas distinto por tema)

### Outbound Canvas
```
[base prompt] + warm amber accents in subtle highlights only, ascending
elements (arrows or rising lines), Voyager 1 trajectory clearly going
outward, "01 OUTBOUND 08:00" label, mood of departure and ascent
```

### Crossing Canvas
```
[base prompt] + deeper blacks, denser star field, hexagram 24 symbol
glowing slightly more, threshold imagery (boundary line cosmic),
"02 CROSSING 13:00" label, mood of dark depth and traversal
```

### Recursion Canvas
```
[base prompt] + spiral pattern subtle in the background centered behind
the hexagram, infinite loop visual metaphor, "03 RECURSION 03:00"
label, mood of return and contemplation
```

---

## Animar la imagen (después de generar)

Opciones simples:

### A — Loop estático con efectos sutiles (CSS/After Effects)
- Imagen base + scanlines moviéndose sutilmente verticales (CSS animation)
- Vignette pulsante muy lento (3-8s loop)
- Star field con shimmer aleatorio (very subtle)
- Resultado: mp4 export 5-8s

### B — Hexagrama "respirando"
- Imagen base con el hexagrama exportado en SVG separado
- Hexagrama: scale 1.0 → 1.05 → 1.0 (3s loop) + opacidad 0.85 → 1.0
- Resto de la imagen estático
- Renderizar a mp4 5s

### C — Trajectory marker moviéndose
- Imagen base con el dot de "VOYAGER 1" en SVG separado
- El dot se mueve a lo largo de la trajectory (loop 8s)
- Cuando llega al final, fade out + reaparece al principio

### Tools para animar
- **CSS + html2canvas + record screen**: rápido, browser
- **After Effects** (pago) — el más pro
- **DaVinci Resolve** (gratis)
- **Pika / Runway** (online, AI animation): subís imagen, te genera el loop animado

---

## Iteración

1. Generar 6-8 frames estáticos.
2. Elegir 1-2.
3. Animar la elegida con uno de los métodos arriba.
4. Export MP4 H.264, 1080×1920, < 8s, < 8MB.
5. Subir a Spotify for Artists después del release.
