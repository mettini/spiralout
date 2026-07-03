# redes/ — assets para redes sociales

Pack de assets listos para usar en redes, **separados por marca**:

- `spiral-out/` — sello/lab. Marca = **espiral dotted + wordmark Courier New**.
- `aem/` — artista. Marca = **el cover del álbum Heliopause**.

Las dos NO se mezclan visualmente. Spiral Out usa la espiral como mark
universal; ÆM usa el album art como hero. Esto es intencional y está
documentado en `site/CLAUDE.md` y `docs/15_brand_accounts.md`.

---

## Brand identity — Spiral Out

### Paleta (mirrors `site/spiralout/index.html` `:root` y el OG generator)

| Token       | Hex        | Uso                                      |
|---|---|---|
| `--bg`      | `#0a0a0c`  | fondo (negro casi puro, levemente cálido) |
| `--fg`      | `#cfcfd2`  | texto principal (off-white frío)         |
| `--muted`   | `#555560`  | tagline / footer en site                 |
| `--accent`  | `#8a7a90`  | la **espiral**; hover; acento púrpura    |
| `--haze-a`  | `#503c5a`  | radial gradient púrpura (30% 20%)        |
| `--haze-b`  | `#283250`  | radial gradient azul (70% 80%)           |

El fondo de marca es `#0a0a0c` con DOS radial gradients overlap:
- ellipse @ 30% 20% — `#503c5a` α 0.35 → 0.08 → 0 (púrpura, top-left)
- ellipse @ 70% 80% — `#283250` α 0.30 → 0.06 → 0 (azul, bottom-right)

### Tipografía

- **Font único**: `'Courier New', Courier, ui-monospace, monospace`
- **Weight**: 300 (light)
- **Letter-spacing**: 0.4em (muy abierto)
- **Case**: lowercase siempre. NO uppercase, NO Title Case.
- **Wordmark exacto**: `s p i r a l   o u t` (una sola línea, tres espacios
  entre "spiral" y "out" para encoder el gap 2em del CSS original).

NO usar otras fonts. La estética typewriter ES la marca.

### El mark (la espiral)

- ~80 círculos en posiciones logarítmicas con radio creciente.
- Color: `#8a7a90` con `fill-opacity: 0.78`.
- Glow filter (`feGaussianBlur stdDeviation 6` + alpha 0.40).
- Centrado por **origen (0,0)** cuando va sola (iso/PFP) — el "vortex"
  apretado es el centro perceptual.
- Centrado por **bbox** cuando va junto al wordmark (logo compositions).

La geometría exacta vive en `scripts/generate_share_images.py` como
`SPIRAL_DOTS`. NO la modifiques sin sync con `site/spiralout/index.html`
(la espiral animada del home), y luego re-corré `task site:share` +
`task site:redes`.

---

## Estructura

```
redes/
├── spiral-out/
│   ├── iso/         ← solo la espiral (sin wordmark)
│   ├── logo/        ← espiral + wordmark "spiral out"
│   ├── avatar/      ← PFP listo (safe area para crop circular)
│   ├── hero/        ← banners / fondos temáticos
│   └── posts/       ← posts branded listos para subir
└── aem/
    ├── avatar/      ← cover del álbum
    ├── posts/       ← posts con el cover como hero
    ├── banner/      ← Bandcamp banner + hero
    └── og/          ← Open Graph
```

---

## Qué archivo va dónde — Spiral Out

### iso/ — solo la espiral

| Archivo                          | Dim   | Uso                                       |
|---|---|---|
| `iso_transparent.svg`            | vec   | sobre cualquier fondo; escalado infinito  |
| `iso_transparent_512.png`        | 512²  | mark chico (botones, footer, watermark)   |
| `iso_transparent_1024.png`       | 1024² | mark mediano                              |
| `iso_transparent_2048.png`       | 2048² | mark grande (print, hi-DPI)               |
| `iso_on_brand.svg`               | vec   | mark sobre fondo de marca (vectorial)     |
| `iso_on_brand_1024.png`          | 1024² | mark sobre fondo de marca                 |
| `iso_on_brand_2048.png`          | 2048² | idem, hi-res                              |

### logo/ — espiral + wordmark

| Archivo                                       | Dim       | Uso                            |
|---|---|---|
| `logo_horizontal_transparent.svg`             | vec       | logo wide, fondo libre         |
| `logo_horizontal_transparent_1920x480.png`    | 1920×480  | logo wide para overlay         |
| `logo_horizontal_on_brand.svg`                | vec       | logo wide con fondo de marca   |
| `logo_horizontal_on_brand_1920x480.png`       | 1920×480  | idem rasterizado               |
| `logo_stacked_transparent.svg`                | vec       | logo cuadrado, fondo libre     |
| `logo_stacked_transparent_1080.png`           | 1080²     | logo cuadrado rasterizado      |
| `logo_stacked_on_brand.svg`                   | vec       | logo cuadrado fondo de marca   |
| `logo_stacked_on_brand_1080.png`              | 1080²     | idem rasterizado               |

### avatar/ — PFP

| Archivo                  | Dim   | Plataforma                                  |
|---|---|---|
| `pfp_iso_1024.png`       | 1024² | **IG / X / Bluesky / SoundCloud / YT** PFP  |
| `pfp_iso_512.png`        | 512²  | fallback chico (forums, alguna plataforma) |
| `pfp_stacked_1024.png`   | 1024² | si querés wordmark visible (riesgoso en crop circular) |

Recomendado para PFP: **`pfp_iso_1024.png`** (el iso, no el stacked).
Las plataformas cropean a círculo — el wordmark queda cortado.

### hero/ — banners temáticos

| Archivo                          | Dim       | Plataforma                          |
|---|---|---|
| `hero_16x9_1920x1080.jpg`        | 1920×1080 | hero web / video thumbnail / placeholder |
| `hero_youtube_2560x1440.jpg`     | 2560×1440 | **YouTube channel art** (safe area central 1546×423) |
| `hero_x_bluesky_1500x500.jpg`    | 1500×500  | **X / Twitter header** + **Bluesky banner** |
| `hero_bandcamp_2400x460.png`     | 2400×460  | **Bandcamp banner**                 |
| `hero_soundcloud_2480x520.jpg`   | 2480×520  | **SoundCloud header**               |

### posts/ — post-ready

| Archivo                          | Dim         | Plataforma                                 |
|---|---|---|
| `og_1200x630.jpg`                | 1200×630    | Open Graph (default): FB / LinkedIn / WhatsApp / Discord / X / iMessage / Threads / Bluesky / Mastodon / Telegram |
| `post_square_1080.jpg`           | 1080×1080   | **IG feed square**                         |
| `post_portrait_1080x1350.jpg`    | 1080×1350   | **IG feed portrait 4:5** (mayor reach)     |
| `post_story_1080x1920.jpg`       | 1080×1920   | **IG / TikTok story + Reels cover**        |
| `post_pinterest_1000x1500.jpg`   | 1000×1500   | **Pinterest pin** 2:3                      |

---

## Qué archivo va dónde — ÆM

### avatar/ — cover del álbum como PFP

| Archivo                       | Dim   | Plataforma                              |
|---|---|---|
| `avatar_cover_512.jpg`        | 512²  | fallback chico                          |
| `avatar_cover_1024.jpg`       | 1024² | IG / X / Bluesky / SoundCloud PFP       |
| `avatar_cover_1500.jpg`       | 1500² | **Spotify / Apple Music artist pic**    |
| `avatar_cover_3000.png`       | 3000² | master — DistroKid / CD Baby            |

### posts/

| Archivo                          | Dim         | Plataforma                  |
|---|---|---|
| `post_square_1080.jpg`           | 1080×1080   | IG feed square              |
| `post_portrait_1080x1350.jpg`    | 1080×1350   | IG feed portrait            |
| `post_story_1080x1920.jpg`       | 1080×1920   | IG / TikTok story           |
| `post_pinterest_1000x1500.jpg`   | 1000×1500   | Pinterest pin               |

### banner/

| Archivo                            | Dim       | Plataforma                       |
|---|---|---|
| `bandcamp_banner_2400x460.png`     | 2400×460  | **Bandcamp banner**              |
| `hero_1024x576.png`                | 1024×576  | hero web / placeholder           |

### og/

| Archivo            | Dim       | Plataforma                                |
|---|---|---|
| `og_1200x630.jpg`  | 1200×630  | Open Graph (link previews universales)    |

---

## Lo que falta (TODO)

- **YouTube channel art para ÆM**: 2560×1440. No existe — ÆM no tiene
  branding wide propio porque su mark es el cover cuadrado. Decidir:
  ¿hacer un YT banner con el cover + título + tracklist al estilo del
  Bandcamp banner?
- **X/Bluesky header para ÆM**: 1500×500. Mismo issue que YouTube.
- **Spotify Canvas (vertical video loop)**: 1080×1920 video 3-8s.
  Pendiente — existe `transmissions/01/artwork/generated/02_spotify_canvas/`
  con experimentos pero ningún render final.
- **SoundCloud header para ÆM**: 2480×520. Idem.

---

## Re-generar

`redes/spiral-out/` es **output determinístico** de un solo script:

```bash
python3 scripts/generate_brand_assets.py
```

El script reutiliza la geometría de la espiral, paleta y wordmark de
`scripts/generate_share_images.py` (el generator del site). Lo que cambia
acá vs el site:

- **Spacing consistente**: todos los layouts (iso, logo, pfp, hero, posts)
  usan los mismos `*_RATIO` constants. Cambiar uno → reflow uniforme.
- **Posts generados localmente**: a diferencia del primer intento, NO
  copia desde `site/spiralout/share/*`. Esto es para que el spacing acá
  no esté atado al spacing del site, que está optimizado para link
  previews y no para crop circular / safe areas de redes.

Si cambia algo de marca (paleta, geometría de la espiral, wordmark):
1. Editá `site/spiralout/index.html` (CSS + SVG inline del home)
2. Sync a `scripts/generate_share_images.py` (los building blocks)
3. Corré `python3 scripts/generate_brand_assets.py` + `task site:share`

---

## Do's & Don'ts

### Do

- Usar **lowercase + Courier New 300 + letter-spacing wide** en cualquier
  texto branded.
- Usar el **fondo de marca** (`#0a0a0c` + los dos radial gradients) cuando
  necesites un nuevo asset — copiá el bloque `DEFS` de `generate_share_images.py`.
- Centrar la espiral por su **origen** cuando va sola (vortex al centro).
- Cross-promo Spiral Out ↔ ÆM via bios linkeadas, NO mezclando assets.

### Don't

- ❌ Web fonts. Ni Inter, ni Helvetica, ni nada — sólo Courier New.
- ❌ Uppercase ni Title Case en el wordmark — siempre `s p i r a l   o u t`.
- ❌ Cambiar el color de la espiral. Siempre `#8a7a90` con α 0.78.
- ❌ Mezclar el mark Spiral Out con el cover ÆM en el mismo asset.
- ❌ Usar el **hexagrama 24** como logo de Spiral Out — el hexagrama es del
  *Transmission 01 / Heliopause* (I Ching reference), NO es brand mark.
- ❌ Reemplazar el SVG por raster — el mark tiene que ser vector para
  favicons + OG + animación en home.
