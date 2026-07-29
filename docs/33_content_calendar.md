# 33 — Calendario de contenido (IG, 3 meses)

> ~12 posts / 12 semanas (1/semana). Cargar en bloque en un scheduler free
> (Metricool o Buffer) y postea solo. Estrategia → `docs/31`. Assets ya
> producidos. Fechas relativas (W1 = la semana que arranques).

## Paso 0 — revisar los 12 antes de cargar nada

```bash
task serve   # → http://localhost:8765/redes/aem/social/review.html
```

Los 12 slots en orden, cada uno con su caption al lado, y botón `ok` / `rehacer`
por post (queda en localStorage, no toca archivos). El botón de abajo alterna
**v2 (con fondo)** ↔ **v1 (todo negro)** para comparar. Lo que marques `rehacer`
se regenera cambiando el slot en `SLOTS` de `scripts/make_posts.py`.

## Formato de los posts de feed (decidido 2026-07-26)

- **Fondo**: 6 de los 9 llevan **frame de los visualizers** (nucleo de luz, niebla
  verde, rayos, mandala, iris), 3 quedan **negro puro** — intercalados para que la
  grilla respire. Un feed de 9 tiles negros no frena el scroll; uno todo imagen
  pierde el silencio. La alternancia es la decisión.
- **Legibilidad**: el fondo se oscurece global (`DARKEN=0.62`) + scrim medido
  sobre la banda de texto hasta luminancia media ≤ 26 y pico ≤ 72 (QA automático
  en `legibility_fix`, imprime los números al generar). La tipografía no cambió.
- **Regenerar**: `python3 scripts/make_posts.py` (los fondos salen de
  `python3 scripts/make_post_backgrounds.py`, que necesita los MP4 4K).
  `--all-black` vuelve a la v1.

## ¿Los posts de feed van con música? NO — y no es opcional

Un post de feed es **imagen**: en IG no lleva audio. Y si lo subís como video
para ponerle música, **IG lo convierte en Reel** (todo video al feed pasa a
Reels desde 2022) — o sea que dejás de tener galería y te comés un Reel flojo
(imagen fija + audio rinde peor que los clips reales). Entonces:

- **Feed (post_01..09)** = sin audio, sin excepción.
- **Música** = los 3 **Reels** (`clip_*.mp4`), que ya llevan el audio del track.

## Cómo se carga en el scheduler (una vez, ~20 min)
1. IG ÆM en modo **Creator** ✅ (hecho 2026-07-26) — necesario para publicar por API.
2. Cuenta de **Buffer** free (3 canales, 10 posts en cola por canal) registrada con
   el mail de la marca, no el personal. Conectar el canal `@aem.transmissions`.
3. Subir los assets: **Reels** = `transmissions/01/video/out/clip_*.mp4`;
   **feed** = `redes/aem/social/post_*.png`.
4. Pegar el caption de cada slot (abajo) y programar 1/semana. Listo, corre solo.
5. Si Buffer no deja publicar **Reels** al perfil Creator, los 3 clips van a mano
   (son 3, uno cada 4 semanas) y por Buffer va solo el feed.

## Reglas de caption (voz `textos.md`)
- Sin "out now", sin agradecimientos, sin explicar. El fragmento habla solo.
- **Link** al álbum en bio (IG no deja link en caption) → el caption cierra con
  "link in bio" discreto, o nada.
- **Hashtags**: solo en **Reels** (los necesitan para descubrimiento), set chico
  y de nicho. En **feed**, sin hashtags (rompen el misterio).
  Set Reels: `#darkambient #ambientmusic #dronemusic #spaceambient #experimentalmusic`
  → van **al final del caption**, separados por dos saltos de línea (IG corta el
  caption a 2 líneas en el feed, así que quedan atrás del "ver más"). En Buffer
  free el campo *First Comment* y el *hashtag manager* son pagos — verificado
  2026-07-26 en la cuenta; escribirlos a mano en el caption no cuesta nada.
  Ojo: los "Tags" del composer de Buffer NO son hashtags, son etiquetas internas.

## Calendario

| Sem | Tipo | Asset | Caption |
|---|---|---|---|
| **W1** | Reel | `clip_outbound.mp4` | `outbound.` + (2ª línea) `to leave was, in truth, the verb that invented it.` + hashtags |
| W2 | Feed | `post_01.png` | *(el fragmento ya está en la imagen; caption vacío o un `·`)* |
| W3 | Feed | `post_02.png` | vacío / `·` |
| W4 | Feed | `post_03.png` | vacío / `·` |
| **W5** | Reel | `clip_crossing.mp4` | `crossing.` + `a trajectory that doubts is not a curve: an orbit that breaks to find its new distance.` + hashtags |
| W6 | Feed | `post_04.png` | vacío / `·` |
| W7 | Feed | `post_05.png` | vacío / `·` |
| W8 | Feed | `post_06.png` | vacío / `·` |
| **W9** | Reel | `clip_recursion.mp4` | `recursion.` + `the spiral does not ascend: it evolves, never the same.` + hashtags |
| W10 | Feed | `post_07.png` | vacío / `·` |
| W11 | Feed | `post_08.png` | vacío / `·` |
| W12 | Feed | `post_09.png` | vacío / `·` |

> **Fragmentos de los feed posts** (por si querés ponerlos también en caption o
> el otro idioma): post_01 *no es lo que mandamos…* / 02 *what returned…* / 03
> *la espiral no asciende…* / 04 *salir, en rigor…* / 05 *the wind that had been
> pushing…* / 06 *una onda no atraviesa…* / 07 *lo que estaba pasando…* / 08 *a
> note, while heard…* / 09 *avanzar sin cambio…* (fuente `textos.md §4/§5.4`).

## Notas
- **Reels = la captación** (lo único que llega a no-seguidores). Feed = galería.
- **Stories = no** hasta tener followers.
- Cuando se acaben los 12, hay **más fragmentos** en `textos.md` (13 en total) +
  se pueden sumar **dossiers modo C** (por producir) para otra tanda.
- Si un Reel pega, ahí sí se evalúa **IG boost** (mes 2-3, `docs/31 §5`).
