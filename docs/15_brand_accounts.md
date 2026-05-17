# 15 — Brand accounts checklist

Cuentas que tenés que sacar (en orden de prioridad), bios sugeridas y la
estrategia de cross-linking. Tres marcas en juego:

- **Spiral Out** — label / sitio umbrella. Una persona, varias trayectorias.
- **ÆM** — artist project propio (release: Heliopause / Transmission 01).
- **Helen Olhausen** — artist project que sale en agosto 2026 (nuevo) + tiene
  un disco de 2021 para revivir.

Regla general: el **artista** es la unidad principal (Spotify, Apple Music,
YouTube son artist-first). **Spiral Out es amplificador, no generador**.

---

## A. ÆM — el artista propio

### Prioridad 1 (sacar ahora — antes del release)

| Plataforma | Handle sugerido | Notas |
|---|---|---|
| **Bandcamp** | `aemtransmissions` | ya existe (`aemtransmissions.bandcamp.com`) |
| **Instagram** | `@aem.transmissions` (o `@aemtransmissions`) | hoy es la red más relevante para ambient/visual |
| **YouTube** | canal `ÆM` (sin contenido aún, dejarlo listo) | va a recibir el Topic auto-generado post CD Baby |
| **Bluesky** | `@aem.bsky.social` o `aem.transmissions.bsky.social` | comunidad experimental/ambient migró en 2025 |

### Prioridad 2 (post-release, se "reclaman", no se crean a mano)

| Plataforma | Cómo |
|---|---|
| **Spotify for Artists** | post-distribución vía CD Baby → claim con el link del primer single/album |
| **Apple Music for Artists** | mismo pattern (CD Baby pasa el catalog → vos verificás identidad) |
| **YouTube Official Artist Channel** | claim vía CD Baby dashboard, mergea tu canal manual con el Topic auto-generado |

### Prioridad 3 (opcional)

- **Soundcloud** — comunidad ambient activa, sirve para teasers / WIPs
- **last.fm** — se genera solo cuando alguien scrobblea (no necesitás crear)

### NO sacar

- TikTok (otro mundo, requiere dedicación específica que no vas a tener)
- Threads (overlap con Bluesky/IG, una persona no maneja todo)
- Facebook (irrelevante para indie ambient en 2026)

### Bio template para ÆM

```
ÆM = AI + Em.
Transmissions composed in Python, the language of contemporary AI.
Each release = one transmission from the spiral.
Heliopause / Transmission 01 — out now.
spiralout.space/aem
```

(Para IG: misma idea + emojis si querés. Para Bluesky / X: igual texto.)

### Links cruzados (linktree alternativo)

No uses Linktree. Es lento, agrega un layer extra, y no rankea para SEO.
Usá `spiralout.space/aem` directo: ya es tu landing con links a Bandcamp y
plataformas. Si querés algo más estilo "all my links" hacés
`spiralout.space/aem/links` que sea una página chiquita con todos los
destinos (Bandcamp, Spotify, Apple, IG, YouTube, Bluesky).

---

## B. Spiral Out — el paraguas

### Prioridad 1

| Plataforma | Handle sugerido | Notas |
|---|---|---|
| **Sitio** | `spiralout.space` | ya está, deployed en Cloudflare Pages |
| **Instagram** | `@spiralout.space` | una sola red, reshare + anuncios |
| **Bandcamp** | `spiralout.bandcamp.com` (label page, opcional) | Bandcamp soporta "labels" como entidad — más profesional |

### NO sacar (todavía)

- Spiral Out en YouTube, X/Bluesky, TikTok — esperá a tener un segundo
  artista o un segundo alias tuyo. Dos cuentas activas para una persona
  alcanza.

### Bio template para Spiral Out

```
Experimental sound lab.
Transmissions from the threshold where signal meets silence.
Releases · framework · writings.
spiralout.space · hello@spiralout.space
```

---

## C. Helen Olhausen — el artista existente

### Estado actual a auditar

Antes de crear nada, **auditar qué ya existe**. Tener una hoja:

- [ ] Spotify artist profile (probablemente exista del disco 2021) — claim/verify
- [ ] Apple Music artist (mismo)
- [ ] Bandcamp page (existe?)
- [ ] YouTube canal o Topic
- [ ] Instagram / X / etc

Si hay perfiles huérfanos (Spotify auto-generado sin foto/bio), **reclamar
todos antes del release de agosto**. Es paso 0.

### Si no existen — crear

Mismo set que ÆM (Bandcamp, IG, YouTube, Bluesky), bajo el handle
`@helenolhausen` o el que esté disponible.

### Bio template para Helen

Pendiente — necesitamos el ángulo editorial de Helen. Ver
[`docs/09_brief_vision_helen.md`](09_brief_vision_helen.md) (existente)
y completar con bio formal cuando definas el concepto del disco de agosto.

---

## Orden de ejecución sugerido

**Esta semana**:
1. Sacar IG @aem.transmissions
2. Crear canal YouTube ÆM (vacío)
3. Sacar Bluesky de ÆM
4. Auditar qué existe de Helen
5. Sacar IG de Spiral Out (handle ya seguro porque tenés el dominio)

**Próximas 2 semanas**:
6. Pegar bios + foto de perfil consistente (la tapa del album sirve para ÆM)
7. Primer post de "coming soon" en IG ÆM
8. Reclamar perfiles huérfanos de Helen si existen
9. Decidir foto y handle Helen

**Después de la distribución de Heliopause via CD Baby**:
10. Reclamar Spotify for Artists ÆM
11. Reclamar Apple Music for Artists ÆM
12. Claim Official Artist Channel YouTube (vía CD Baby)

Esto último (10-12) tarda 1-2 semanas post-release. **Distribuir mínimo
3-4 semanas antes del release date** para que Spotify editorial pueda
recibir pitch (requiere ≥7 días de anticipación).

---

## Linkeo cruzado entre cuentas — SEO + GEO + Wikidata

Cada perfil debe linkear a los demás con `sameAs` o el equivalente. Esto
le dice a Google y a los LLMs "estas cuentas son la misma entidad":

**ÆM cross-links** (poner en bio de cada red):
- IG bio: `🌀 spiralout.space/aem · bandcamp · spotify · youtube`
- Bandcamp: links a Spotify, Apple, YouTube, IG, Bluesky
- Schema.org en `/aem/index.html`: `sameAs` array con TODAS las URLs

**Spiral Out cross-links**:
- IG bio: `experimental sound lab · spiralout.space`
- Sitio: schema.org Organization con `sameAs` a Bandcamp label + IG

Mantener una lista canónica de URLs en
[`docs/16_seo_geo_playbook.md`](16_seo_geo_playbook.md).
