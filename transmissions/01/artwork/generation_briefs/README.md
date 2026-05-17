# Pack de generación de artwork — ÆM Heliopause Transmission 01

Briefs listos para pegar en **Draw Things** (Mac App Store, gratis,
optimizado Apple Silicon, soporta FLUX/SDXL local). Cada brief incluye:
prompt principal + negative + settings + 3 variaciones + notas de
iteración + mood references.

Construidos con el contexto narrativo del proyecto:
- Concepto: heliopausa, voyager, sonda interestelar, transmisión, cruce, espiral
- Lore: ÆM como señal anónima, mensaje desde el borde del sistema solar
- Hexagrama 24 (復 Fù): el retorno, punto de inflexión
- Estética: retro CRT phosphor green, vintage NASA control panel, wireframe Tron, pixel art

---

## Setup inicial (una vez)

### Opción A — CLI Python (RECOMENDADA — automatizable, sin GUI)

Ya está implementado en el proyecto. Workflow:

```bash
task gen:install                              # 1. instala torch+diffusers (una vez, ~3 min)
task gen:list                                 # 2. lista briefs disponibles
task gen:artwork -- 00_artist_photo --n 4    # 3. genera 4 imagenes del brief
```

**Modelos disponibles** (auto-bajan primera vez en `~/.cache/huggingface`):
- **SDXL Turbo** (~7 GB, rápido, 4 steps) ← **default** · `task gen:artwork`
- **SDXL base 1.0** (~13 GB, calidad alta, 25 steps) · `task gen:artwork:hq`
- **FLUX.1 schnell** (~24 GB, calidad SOTA, requiere ≥32 GB RAM) · `task gen:artwork:flux`

**Hardware**: Mac M1/M2/M3 con MPS (Metal Performance Shaders). Verificá con:
```bash
python3 -c "import torch; print(torch.backends.mps.is_available())"
```

**Output**: `transmissions/01/artwork/generated/<brief_id>/<timestamp>_NN.png`

```bash
task gen:open                                 # abre la carpeta en Finder
```

### Opción B — Draw Things (GUI, también gratis)

App Mac nativa, GUI completa, mismos modelos open source.

1. **Bajar Draw Things** del Mac App Store (gratis):
   https://apps.apple.com/us/app/draw-things-ai-generation/id6444050820

2. **Bajar modelo** (FLUX.1 schnell o SDXL):
   - Abrir Draw Things → Settings → Model Browser
   - Click Download
   - Esperar (largo la primera vez, después es local)

3. **Settings recomendados**:
   - Sampler: **Euler A**
   - Steps: **4** (FLUX schnell / SDXL Turbo)
   - CFG scale: **1.0** (FLUX usa CFG bajo)
   - Negative prompt: usar el del brief

4. **Workflow**:
   - Abrir el `.md` del asset
   - Copy/paste **prompt** y **negative** del brief en Draw Things
   - Setear **resolution** del brief
   - Generar 4-8 imágenes

---

## Dos líneas estéticas paralelas

El proyecto tiene DOS direcciones visuales que coexisten:

**Línea A · CRT phosphor** (identidad central) — verde phosphor sobre
negro, vintage NASA, wireframe Tron/Battlezone, pixel art. **Mantiene
coherencia con el cover de tapa, design system, UI player.**

**Línea B · Sci-fi 70s pintado** (material promocional) — ilustraciones
estilo Chris Foss, Don Davis NASA Voyager mission art, Moebius, Roger
Dean, Carl Sagan Cosmos. Paleta cósmica RICA (purples, deep blues,
golden, amber). Painterly oil illustration. **Para posters, hero
backgrounds, social media — donde la imagen tiene que volar.**

Los briefs con sufijo **`_painterly`** son línea B. Los demás son línea A.

---

## Briefs disponibles

### Identidad / perfil
| brief | uso | aspect | resolución |
|---|---|---|---|
| [`00_artist_photo.md`](00_artist_photo.md) | Apple Music profile, Bandcamp avatar, Spotify for Artists | 1:1 | 1500×1500 |

### Hero / banners
| brief | uso | línea | aspect |
|---|---|---|---|
| [`01_hero_background.md`](01_hero_background.md) | wallpaper / hero CRT | A | 16:9 |
| [`01_hero_background_painterly.md`](01_hero_background_painterly.md) | hero painterly sci-fi 70s | B | 16:9 |
| [`02_spotify_canvas.md`](02_spotify_canvas.md) | mobile vertical loop Spotify | A | 9:16 |
| [`03_bandcamp_banner.md`](03_bandcamp_banner.md) | header Bandcamp | A | 5.4:1 |

### Social / posters
| brief | uso | aspect | resolución |
|---|---|---|---|
| [`04_poster_print.md`](04_poster_print.md) | poster vertical para print / IG carousel | 4:5 | 1080×1350 (o 2400×3000 print) |
| [`05_social_square.md`](05_social_square.md) | post cuadrado IG / general social | 1:1 | 1080×1080 |
| [`06_story_vertical.md`](06_story_vertical.md) | Stories IG / Reels cover / TikTok | 9:16 | 1080×1920 |
| [`09_flyer_event.md`](09_flyer_event.md) | flyer listening session / live | 4:5 | 1080×1350 |

### Variantes de cover
| brief | uso |
|---|---|
| [`08_track_variants.md`](08_track_variants.md) | cover alternativa por track (3 covers, uno cada uno) |

### Library
| archivo | uso |
|---|---|
| [`prompt_library.md`](prompt_library.md) | bloques modulares (paleta, mood, motifs, style tags) que se combinan |

---

## Iteración recomendada

**Round 1**: generar **4-8 imágenes** por brief usando el prompt principal. Elegir 1-2 que tiren bien.

**Round 2**: con seed fijo de la mejor → variar el prompt incrementalmente (cambiar 1 detalle por vez, ej "deep blacks" → "deep blacks with subtle scanlines"). Esto da consistencia entre variaciones.

**Round 3**: para video (Canvas, banner animado), exportar el frame estático y animar aparte (CSS / SVG / After Effects / Pika).

---

## Anti-AI tells (rerollear si aparecen)

- **Faces detrás del símbolo** (FLUX a veces inventa caras donde no debería)
- **Texto inventado / glitched** que no es ÆM
- **Manos extra**, dedos raros (típico AI)
- **Watermarks** que no son ÆM
- Sombras que no condicen con la fuente de luz
- Saturación cyan/magenta (= synthwave cliché, NO ÆM)

Si una imagen tiene cualquiera de estos, rerollar (mismo prompt, otro seed).

---

## Una vez generado un asset

Guardar en `transmissions/01/artwork/generated/<asset>.png`. Si te
interesa la imagen ya lista para distribución (con sRGB color profile,
JPG comprimido), pasala por:

```bash
python3 scripts/optimize_artwork.py input.png output.jpg --max-size 3000 --quality 92
```

(script todavía no implementado — si lo necesitás, lo armo).

---

## Si Draw Things no te tira

Alternativas también gratis y locales:
- **DiffusionBee** (gratis, Mac, GUI, más viejo): https://diffusionbee.com/
- **ComfyUI** (gratis, GUI node-based, más control, complejo de setup)
- **HuggingFace Diffusers** Python lib (cero GUI, código)

Si preferís pago / online: Midjourney, DALL-E 3 (ChatGPT Plus). Los
prompts están escritos para FLUX pero funcionan en otros modelos con
ajustes mínimos (Midjourney usa `--ar` para aspect ratio en vez de
resolution explícita; DALL-E ignora negative prompts).
