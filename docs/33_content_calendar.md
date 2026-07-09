# 33 — Calendario de contenido (IG, 3 meses)

> ~12 posts / 12 semanas (1/semana). Cargar en bloque en un scheduler free
> (Metricool o Buffer) y postea solo. Estrategia → `docs/31`. Assets ya
> producidos. Fechas relativas (W1 = la semana que arranques).

## Cómo se carga (una vez)
1. IG en modo **Business/Creator** (paso 1 foundation) conectado al scheduler.
2. Subir los assets: **Reels** = `transmissions/01/video/out/clip_*.mp4`;
   **feed** = `redes/aem/social/post_*.png`.
3. Pegar el caption de cada slot (abajo) y programar 1/semana. Listo, corre solo.
4. Regenerar posts si hace falta: `python3 scripts/make_posts.py`.

## Reglas de caption (voz `textos.md`)
- Sin "out now", sin agradecimientos, sin explicar. El fragmento habla solo.
- **Link** al álbum en bio (IG no deja link en caption) → el caption cierra con
  "link in bio" discreto, o nada.
- **Hashtags**: solo en **Reels** (los necesitan para descubrimiento), set chico
  y de nicho. En **feed**, sin hashtags (rompen el misterio).
  Set Reels: `#darkambient #ambientmusic #dronemusic #spaceambient #experimentalmusic`

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
