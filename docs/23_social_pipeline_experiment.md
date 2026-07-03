# 23 — Multi-platform social pipeline (experimento)

> **Status**: backlog. NO avanzar hasta:
> 1. Cuentas Tier 1 cerradas (✓ todas done)
> 2. Videos del álbum aprobados visualmente por el user (`yt-visualizer` ya en done formal, pero iterar si hay pedidos)
> 3. Decisión explícita del user de arrancar
>
> Diferencial: el user explícitamente dijo "no quiero ser tu mulo" — el
> diseño está condicionado a que la intervención humana sea mínima
> (idealmente ~15 min one-time, idealmente 0 si Computer Use cubre OAuth).

## Objetivo

Correr un experimento controlado de **distribución multi-plataforma
automatizada** durante 60-90 días para medir:

- Crecimiento de streams (Spotify / Apple / Tidal) sobre baseline
- Click-through a Bandcamp / sitio
- Follower growth por plataforma
- Qué tipo de content shard funciona (clip vertical, carrousel lore, still,
  loop Hydra, etc.)

NO es "spam flooding" — eso dispara shadowban en 48h en IG/TikTok. Es
**cadencia sostenida con shards variados y captions tuneados por
plataforma**.

## Stack propuesto

```
content_pipeline/
├── slicer.py            corta *_yt.mp4 en clips 15-30s + variantes IG/TikTok/Shorts
├── caption_pool.py      genera N captions ES/EN por clip vía Claude API
└── scheduler.py         cola de posts con timing inteligente por plataforma

posters/
├── bluesky.py           AT Protocol (gratis, API directa)
├── x.py                 X API v2 (free tier 1500 posts/mes)
├── mastodon.py          API abierta
├── youtube.py           YT Data API (OAuth refresh token)
└── postiz_client.py     IG/TikTok/Threads via Postiz instance

postiz/                  Postiz docker, self-hosted (Cloudflare Workers o local)

metrics/
└── daily_pull.py        streams + followers + clicks

dashboard/experiment.html  KPIs en vivo
```

### ¿Por qué Postiz?

- Open source, self-hostable, gratis
- Soporta 18+ plataformas
- **Ya pasaron Meta dev review con su app** → user piggybackea via OAuth
  (un click por plataforma) en lugar de armar app propia (1-2 semanas).
- Alternativa SaaS: Buffer ($6/canal/mes), Hypefury ($19/mes) — menos
  control, más simple. Postiz gana si querés scripting custom.

### Plataformas vs costo / fricción

| Plataforma | API | Costo posteo auto | Fricción setup |
|---|---|---|---|
| Bluesky | AT Protocol abierto | $0 | trivial — API directa, sin OAuth complejo |
| X | API v2 | $0 free tier 1500 posts/mes | OAuth simple |
| Mastodon | abierta | $0 | trivial |
| YouTube | Data API | $0 (quota generosa) | OAuth + refresh token |
| Instagram | Graph API | $0 via Postiz | OAuth via Postiz, sin Meta dev review propio |
| TikTok | Content Posting API | $0 via Postiz | OAuth via Postiz |
| Threads | Beta via Meta | $0 via Postiz | hereda OAuth IG |
| SoundCloud | CERRADA desde 2014 | ❌ | manual only |

## Minimización de "tu mano"

| Mecanismo | Tu intervención | Costo |
|---|---|---|
| Postiz + Claude Desktop Computer Use (beta 2026) | nada — Claude maneja el browser y completa OAuth, vos solo aprobás MFA si lo pide | gratis con Claude Pro |
| Postiz + Playwright headless + delegated session | nada — vos pasás cookies/token una vez | setup 30 min |
| Postiz + MCP server custom (Gmail + browser) | nada — Claude lee confirmation emails y clickea links | requiere armar MCP |
| Postiz + user-driven OAuth | ~15 min UNA vez para todas las plataformas | gratis |

**El default razonable es Computer Use**. Si falla en alguna plataforma,
ahí (y solo ahí) un click manual por excepción.

## Content pool — material ya disponible

Listado de qué se puede shardar del repo actual:

| Source | Shards generables | Formato output |
|---|---|---|
| `transmissions/01/video/out/1-outbound_v22_yt.mp4` | 16 clips de 30s | 1080×1920 IG Reels / TikTok / Shorts |
| `transmissions/01/video/out/2-crossing_v4_yt.mp4` | 26 clips de 30s | 1080×1920 |
| `transmissions/01/video/out/3-recursion_yt.mp4` | 6 clips de 30s | 1080×1920 |
| Hydra fósforo verde (`crossing_delirio*.js`) | loops perfect-loop 15s | 1080×1920 audio-reactive |
| `redes/spiral-out/iso/` + abstracts Blender Crossing | grids estáticos | 1080×1080 / 1080×1350 |
| Lore Heliopause + Voyager | carrousels 5-10 frames con quote+dato | 1080×1080 carrousel |
| Hexagram 24 (`transmissions/01/artwork/hexagram/`) | variantes animadas | 1080×1080 loops |

**Total disponible sin generar nada nuevo: ~50 piezas base**.

Aplicando 3-5 caption variants por pieza vía Claude API → pool de ~200-250
posts totales. Suficiente para 60-90 días de cadencia moderada.

## Cadencia recomendada (vs "flood")

| Plataforma | Posts/día | Por qué ese número |
|---|---|---|
| TikTok | 2-3 | algoritmo premia frecuencia, tolera más volumen |
| Bluesky | 3-5 | audiencia indie/electrónica activa, low penalty |
| X | 2-4 | reach orgánico bajo, insistir es la única estrategia |
| IG Reels | 1-2 | overposting penaliza, 2 max |
| IG Feed | 1 cada 2-3 días | grid se ve mal si flood |
| YT Shorts | 1-2 | YT premia velocidad de Shorts |
| Mastodon | 2-3 | comunidad chica, no abusar |

Total ~10-18 posts/día across all platforms × 60 días = 600-1080 posts
totales en el experimento.

## Métricas — qué define "experimento exitoso"

### Métrica primaria (la que importa)
- **Streams Spotify/Apple/Tidal week-over-week** vs baseline pre-experimento

### Métricas secundarias
- Clicks → `spiralout.space` (GA4)
- Clicks → `aemtransmissions.bandcamp.com`
- Follower growth por plataforma (delta vs T0)
- Engagement rate por shard type (qué funciona)
- Cost per stream incremental (si todo es free, eso es siempre 0 — pero
  cuenta el time-cost del setup amortizado)

### Métricas anti-disaster
- Shadowban detection (engagement cae a 0 de golpe)
- Account locks / suspensions
- Spam reports

## Hipótesis a contrastar

Las tres más interesantes:

1. **"Hydra audio-reactivo viraliza más que still + caption"** —
   medirlo comparando engagement de los dos shards type.
2. **"Captions en ES outperforman a EN en Bluesky/Mastodon, EN outperforman
   a ES en IG/TikTok/X"** — A/B obvio.
3. **"60 días de cadencia sostenida producen un step-change en streams,
   no un crecimiento lineal"** — si cierto, hay valor en sostener; si
   falso, el experimento se puede cortar a 30 días.

## Riesgos identificados

| Riesgo | Mitigación |
|---|---|
| Shadowban por overposting | Cadencia conservadora; varianza en horario; captions únicos no copy-paste |
| Burnout del content pool | Re-shardear contenido old + agregar caption variants nuevas en lugar de generar piezas nuevas |
| Postiz cae / API change | Fallback a posters custom directos por plataforma |
| Métricas no se mueven | Aceptar como respuesta válida — el experimento valida nulidad también |
| Quemar la marca con shards pobres | Pre-aprobación del user del primer batch (vetar antes del drop) |

## Plan de arranque (cuando llegue el día)

Cuando el user diga "ahora sí":

1. **Día 1 — Sanity** (2 horas):
   - Levantar Postiz en docker local
   - Verificar OAuth flow vía Computer Use (probar 1 plataforma fácil — Mastodon)
   - Armar `slicer.py` con 1 clip test desde `2-crossing_v4_yt.mp4`
   - Postear test en Bluesky (API directa, sin Postiz) — verificación end-to-end

2. **Día 2-3 — Stack completo**:
   - Posters Bluesky / X / Mastodon
   - Postiz conectado a IG / TikTok / Threads / YT
   - `caption_pool.py` con Claude API
   - `scheduler.py` con cron

3. **Día 4 — Content batch**:
   - Generar primer batch de 50 posts (10 por plataforma × 5 plataformas)
   - User revisa + veta (15 min de su parte, primera vez solamente)
   - Schedule arranca

4. **Día 5+ — Operación**:
   - Cron tira posts según schedule
   - `daily_pull.py` corre todas las noches
   - `dashboard/experiment.html` se actualiza
   - User mira métricas cuando quiere, no requiere acción

5. **Día 30 / 60 / 90 — Análisis**:
   - Pull data, comparar contra baseline
   - Decidir si continuar, ajustar, o cerrar
   - Doc results en `experiment_results.md`

## Pre-requisitos antes de arrancar

Cumplido ✓ / Pendiente ⏳:

- ✓ Cuentas Tier 1 SO + ÆM activas
- ✓ Material audiovisual base (`*_yt.mp4` finales, Hydra, hexagram)
- ✓ Streaming live (Spotify/Apple/Tidal — métrica primaria medible)
- ⏳ Aprobación visual final del user sobre los videos
- ⏳ Decisión explícita del user de arrancar
- ⏳ (Implícito) Claude Desktop Computer Use o equivalente para minimizar
  OAuth manual

## Notas sobre voz

- **Spiral Out** (label): voz curatorial. Captions más analíticos /
  conceptuales. Cross-promo a ÆM siempre que se pueda.
- **ÆM** (artista): voz artística. Captions más líricos / lore-driven.
  Sin meta del proceso, sin "behind the scenes" técnico.

Ver `docs/15_brand_accounts.md` sección "Bios reusables" para tono base.

---

## Sobre por qué este doc existe (y no solo un task en el dashboard)

Una task de dashboard sirve para "hay que hacer X". Este experimento es
suficientemente grande para tener:
- Decisiones de stack pre-tomadas
- Riesgos catalogados
- Plan de arranque listo para ejecutar sin re-pensar

Cuando se active, este doc es el "go-bag" — no hay que reconstruir
contexto. Eso ahorra ~2 horas de discusión cuando el momento llegue.
