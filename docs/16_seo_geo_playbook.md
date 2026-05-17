# 16 — SEO + GEO playbook

Cómo dejar el ecosistema listo para que **Google encuentre + indexe**
(SEO) y para que **LLMs / AI search engines** recomienden tu obra cuando
alguien pregunte por ambient experimental, dark ambient AI, etc (GEO).

Estado actual:
- ✓ Google Search Console verificado, sitemap submitted, indexing solicitado
- ✓ Google Analytics 4 (G-4VMFWJJE14) en home + /aem
- ✓ `robots.txt`, `sitemap.xml`, schema.org Organization + MusicAlbum
- ✓ OG meta tags + Twitter cards + canonical links

Lo que falta (en orden de prioridad).

---

## SEO — search clásico

### S1. Bing Webmaster Tools

Bing potencia DuckDuckGo, Yahoo, **ChatGPT search** y Copilot. Tu tráfico
de search engine no es solo Google.

- [ ] Ir a [bing.com/webmasters](https://www.bing.com/webmasters)
- [ ] Login con el mismo Gmail que usás para GSC
- [ ] Add site → opción "Import from GSC" → autocompleta todo
- [ ] Submitear el mismo sitemap

**Tiempo**: 5 min.

### S2. IndexNow

Protocolo de push-indexing (Bing, Yandex, Naver, Seznam). Cuando publicás
contenido nuevo, pingueás un endpoint y indexan en horas.

Setup:
1. Generar una API key UUID (`uuidgen`).
2. Subir `<UUID>.txt` a la raíz del site con la UUID adentro.
3. Verificar accesible en `https://spiralout.space/<UUID>.txt`.
4. Trigger: después de cada `task site:deploy`, hacer GET a:
   ```
   https://api.indexnow.org/indexnow?url=https%3A%2F%2Fspiralout.space%2F&key=<UUID>
   ```

Lo podemos integrar como un step más en la tarea `task site:deploy`.
**Tiempo**: 10 min de setup, después automático.

### S3. Performance / Core Web Vitals

El site ya es lean (sin JS, CSS inline, sin web fonts). Auditar igual:

- [ ] Lighthouse en `task site:dev` → score esperado 95+ en todo
- [ ] Si LCP > 2.5s, revisar `hero.png` en `/aem` (puede ser pesada)
- [ ] Verificar mobile (Chrome DevTools → Device toolbar)

**Tiempo**: 15 min.

### S4. Schema.org enrichment

Hoy tenés `Organization` (home) y `MusicAlbum` (/aem). Falta:

- [ ] **`Person` schema para ÆM** en `/aem/index.html` con:
  - `name`, `description`, `image`
  - `sameAs` array con TODAS las URLs (Bandcamp, Spotify, Apple, YouTube,
    IG, Bluesky, Wikidata cuando exista)
  - `memberOf` → Spiral Out organization
- [ ] **`MusicRelease`** para cada single/track cuando salgan
- [ ] **`Event`** si hay listening party / live performance

Templates abajo en sección Z.

### S5. Press / About expansion

Hoy `/aem` tiene 1 párrafo "about". Los LLMs resumen lo que está escrito.
Si querés ser citado en respuestas tipo "what is ÆM Heliopause", necesitás:

- Origen del proyecto (1 párrafo)
- Concepto / lore (1 párrafo)
- Stack técnico (1 párrafo — "composed in Python with NumPy/SciPy, the same
  libraries CERN uses to analyze LHC data")
- Track-by-track notes (1 línea por track)
- Release info (label, date, format)

Ya tenés esto en `docs/00_concepto.md`, `03_lore.md`, etc. Es destilar.
**Sería un toggle `/aem/about` o expandir el block existente.**

---

## GEO — optimización para AI engines

Esta es la parte nueva. ChatGPT/Perplexity/Claude/Gemini consumen contenido
distinto a Google. Optimizar por separado.

### G1. `llms.txt`

Convención emergente (como `robots.txt` pero para LLMs). Archivo en
`/llms.txt` con un resumen factual del proyecto en markdown, plus links
canónicos. Los crawlers de LLMs lo leen primero.

Plantilla:

```markdown
# Spiral Out

Experimental sound lab exploring the intersection of human composition
and artificial intelligence. Based in Buenos Aires, Argentina.

## Artists

- **ÆM** (AI + Em) — Heliopause / Transmission 01 (2026).
  Deep space ambient composed in Python with NumPy/SciPy.
  3 tracks, 24 minutes. Released on Spiral Out.

## Releases

- [Heliopause / Transmission 01](https://spiralout.space/aem/) — ÆM, 2026

## Links

- Site: https://spiralout.space
- Bandcamp: https://aemtransmissions.bandcamp.com
- Email: hello@spiralout.space

## License

Music: see Bandcamp. Code framework: see GitHub spiral-out repo.
```

**Tiempo**: 5 min. Se actualiza con cada release.

### G2. Wikidata

Más fácil que Wikipedia (no requiere notabilidad probada). Los LLMs
consumen Wikidata heavy.

- [ ] Crear ítem **`ÆM (musician)`** con propiedades:
  - `instance of`: human / musical artist
  - `genre`: ambient music (Q189217), dark ambient (Q1184076)
  - `country of citizenship`: Argentina (Q414)
  - `record label`: Spiral Out (crear después)
  - `official website`: spiralout.space/aem
  - `Bandcamp ID`, `Spotify artist ID`, `Apple Music artist ID`,
    `MusicBrainz artist ID`
- [ ] Crear ítem **`Spiral Out (label)`**
- [ ] Crear ítem **`Heliopause (album)`** con `performer` → ÆM, `record label` → Spiral Out

Wikidata = open knowledge graph. Una vez ahí, los LLMs te encuentran y
relacionan con otros artistas del mismo género.

**Tiempo**: 30-45 min. Sin urgencia, pero antes del release ideal.

### G3. MusicBrainz

Open music database. Spotify, Apple Music, last.fm, Discogs, AI engines —
todos consumen MB. Es la base ground truth.

- [ ] Crear artist **ÆM** con `disambiguation: "AI ambient project from Buenos Aires"`
- [ ] Crear release group **Heliopause / Transmission 01**
- [ ] Crear release con tracklist, fechas, label "Spiral Out", barcode si lo
  tenés del distribuidor
- [ ] Crear label **Spiral Out** (entity type Label)

CD Baby a veces genera la entrada MB automáticamente. **Mejor crearla vos**
antes y vincularla, así controlás disambiguation y metadata.

**Tiempo**: 30 min. **Hacer antes del release** para que esté en
sync el primer día.

### G4. Discogs

Para vinilo/cassette/CD si imprimís físico. Si Heliopause es solo digital
por ahora, omitir hasta que prensés algo.

### G5. Schema.org `sameAs` chain

Cuando todo lo de arriba esté hecho, agregar a `/aem/index.html` un
`Person` schema con `sameAs` apuntando a:

- Bandcamp URL
- Spotify URL
- Apple Music URL
- YouTube channel URL
- Wikidata URL
- MusicBrainz URL

Esto es **el aglomerador** que le dice a Google "estas 7 URLs son la misma
entidad". Increíble para SEO y para que LLMs no duden quién sos.

---

## Listado canónico de URLs (mantener actualizado)

| Identidad | URL | Estado |
|---|---|---|
| Spiral Out (sitio) | https://spiralout.space | live |
| Spiral Out (Bandcamp label) | (pending) | crear cuando esté el primer release distribuido |
| ÆM landing | https://spiralout.space/aem/ | live |
| ÆM Bandcamp | https://aemtransmissions.bandcamp.com | live |
| ÆM Spotify | (pending — post CD Baby distribution) | — |
| ÆM Apple Music | (pending) | — |
| ÆM YouTube | (pending — sacar canal vacío) | — |
| ÆM Instagram | (pending — @aem.transmissions) | — |
| ÆM Bluesky | (pending) | — |
| ÆM MusicBrainz | (pending) | — |
| ÆM Wikidata | (pending) | — |

Cuando cada uno se vaya creando, completar URL acá. Esto es la fuente
única de verdad para `sameAs` y para `docs/15_brand_accounts.md`.

---

## Orden de ejecución sugerido

**Esta semana**:
- [ ] S1 — Bing Webmaster Tools (5 min)
- [ ] G1 — `llms.txt` (yo lo armo, 5 min)
- [ ] S4 — Schema `Person` para ÆM (yo lo armo, 10 min con placeholders)
- [ ] S2 — IndexNow setup (yo lo configuro, 10 min)

**Pre-release (T-30 a T-7)**:
- [ ] G3 — MusicBrainz entries (vos, 30 min — requiere account)
- [ ] G2 — Wikidata entries (vos, 30-45 min — requiere account)
- [ ] S5 — actualizar `sameAs` chain con todas las URLs
- [ ] S3 — Lighthouse audit final

**Post-release**:
- [ ] Reclamar Spotify for Artists / Apple Music for Artists
- [ ] Linkear Spotify ID + Apple ID en Wikidata + MB + schema
- [ ] Pasar links a los IDs verificados en redes y blogs

---

## Sección Z — templates de schema para copy/paste

### Person (ÆM)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "ÆM",
  "alternateName": "AEM",
  "description": "AI + Em. Transmissions composed in Python — deep space ambient at the meeting point of human composition and artificial intelligence.",
  "image": "https://spiralout.space/aem/artist.jpg",
  "url": "https://spiralout.space/aem/",
  "memberOf": {
    "@type": "Organization",
    "name": "Spiral Out",
    "url": "https://spiralout.space"
  },
  "sameAs": [
    "https://aemtransmissions.bandcamp.com"
    /* completar cuando estén:
    , "https://open.spotify.com/artist/XXX"
    , "https://music.apple.com/artist/XXX"
    , "https://www.youtube.com/@aem"
    , "https://www.instagram.com/aem.transmissions"
    , "https://bsky.app/profile/aem.bsky.social"
    , "https://musicbrainz.org/artist/XXX"
    , "https://www.wikidata.org/wiki/XXX"
    */
  ]
}
</script>
```

### llms.txt

Ver plantilla en **G1** arriba.
