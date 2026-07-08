# 25 — Press kit · ÆM — Heliopause / Transmission 01

> Capa **operativa** para pitches y carga en plataformas. NO reescribe la voz:
> la voz pública ya está fijada. Fuentes canónicas (no duplicar, levantar de acá):
>
> - **Voz pública / textos cifrados** → `transmissions/01/release/textos.md`
>   (bios, taglines, textos por track, 13 frases sociales ES+EN, playbook de posteo).
> - **Metadata + prosa larga** → `transmissions/01/release/metadata_proposal.md`.
> - **Cuento (fuente de los fragmentos)** → `docs/10_cuento.md` / `docs/10_cuento_en.md`.
> - **MusicBrainz / Wikidata** → `docs/26_musicbrainz_wikidata.md`.

## Regla de voz (NO romper)

**Misterio siempre. Nada de explicar.** ÆM es faceless. Lo público son
**fragmentos del cuento plantados solos, sin contexto** (ver `textos.md`).
Sin "out now", sin agradecimientos, sin foto de persona, sin responder "quién
es ÆM". Que la gente diga "qué es esta fumada" — ese es el objetivo.

- **Abouts de plataforma / redes** → fragmentos cifrados de `textos.md`. **Nunca** la prosa explicativa.
- **Mail de pitch a un blog** → única excepción: el periodista necesita datos
  para escribir. Ahí va la **tabla de hechos** (abajo) + 2-3 fragmentos +
  link. El texto que se *publica* sigue siendo cifrado.

## La voz, lista para pegar (de `textos.md`)

**Bio corta (Spotify About):**
> *Una onda no atraviesa un medio: es el medio atravesándose.*
> *Una nota, mientras es oída, no se acuerda de haber sido una nota: es la escucha misma.*

**Album tagline:** *No es lo que mandamos. Es lo que volvió.*

**Por track:** Outbound → *Salir, en rigor, fue el verbo que lo inventó.* ·
Crossing → *Una trayectoria que duda no es curva: es una órbita que se parte
para encontrar su nueva distancia.* · Recursion → *La espiral no asciende:
evoluciona sin volver a ser la misma.*

(EN + las 13 frases sociales + modos de posteo → `textos.md` §4–6.)

---

## Hechos clave (solo para journalists / formularios)

| Campo | Valor |
|---|---|
| Artista | **ÆM** ("AEM"; fallback `aem` si Æ rompe en upload) |
| Álbum | **Heliopause** (Transmission 01) |
| Sello | **Spiral Out** (spiralout.space) |
| Formato | 3 tracks · ~24 min · digital |
| Género | Ambient (Spotify/Apple, único tag) |
| Tags Bandcamp (LIVE) | ambient · atmospheric · cosmic ambient · dark ambient · deep space ambient · drone · experimental · space music · **Buenos Aires** (ubicación) |
| Año | 2026 · © 2026 ÆM · Distribuidor: CD Baby |
| Release date | **2026-05-16** |
| UPC / barcode | `823000591084` |
| Concepto | Composición humano + IA, código puro (framework `aem`). Faceless. |

| # | Track | Dur. | ISRC |
|---|---|---|---|
| 1 | Outbound | 8:00 | `USHM82659668` |
| 2 | Crossing | 13:00 | `USHM82659669` |
| 3 | Recursion | 3:00 | `USHM82659670` |

---

## Clip start para short-form (TikTok / CD Baby)

CD Baby deja elegir el **start time del clip de ~60s** que se usa en TikTok
(default = primeros 60s). En ambient el arranque es lento → hay que **empezar en
el climax** para que enganche. Calculado con la energía real del audio
(`transmissions/01/video/control/*.npz`):

| Track | Start | Por qué |
|---|---|---|
| Outbound | **6:52** (412s) | pico de energía @ 7:00 (cae ~8s dentro); climax final |
| Crossing | **7:23** (443s) | swell más fuerte @ 7:31 (alt: 0:04 = intro, sección más sostenida) |
| Recursion | **1:34** (94s) | payoff @ 1:42; arranca en la subida |

## Assets (a rolete — rutas en repo)

| Uso | Archivo |
|---|---|
| Cover streaming/press | `transmissions/01/artwork/cover_streaming_3000.jpg` |
| Imagen de artista (marca hexagrama, faceless) | `transmissions/01/artwork/generated/00_artist_photo/artist_photo_3000.png` |
| Logo ÆM | `transmissions/01/artwork/hexagram/hexagram_24_logo.svg` |
| Avatar / banners redes | `redes/aem/…` (avatar, banner, posts, og) |
| Fondos painterly (posts/fichas) | `transmissions/01/artwork/generated/01_hero_background_painterly/` |
| Canvas stills (para animar) | `transmissions/01/artwork/generated/02_spotify_canvas/` (768×1344) |
| Visualizers (fuente de clips) | `transmissions/01/video/out/*_60fps.mp4` |

Para posts hay 3 modos ya definidos en `textos.md §6`: **A** anotación marginal ·
**B** fragmento de transmisión · **C** ficha técnica (dossier desclasificado).

---

## Links

- Web: https://spiralout.space/aem · Contacto: em@spiralout.space
- Bandcamp: https://aemtransmissions.bandcamp.com/album/heliopause
- Spotify: https://open.spotify.com/album/5omJDu1rZwe9YFeAWONY6x
- Apple Music: https://music.apple.com/album/heliopause-ep/6773985527
- Tidal: https://tidal.com/album/528526670 · Amazon: https://music.amazon.com/albums/B0H34YZ4ZK · Qobuz: https://www.qobuz.com/album/heliopause-aem/eotey7erxe23d
- YouTube: https://www.youtube.com/@aem.transmissions · Playlist: https://www.youtube.com/playlist?list=PLmefLWsXYwXYM1AOKLVWOLIlxntLWOCYt · SoundCloud: https://soundcloud.com/aemtransmissions

## Pitch a blogs (Headphone Commute, Stationary Travels, A Closer Listen, Fluid Radio)
Mail corto: 1 línea de qué es (usar la tabla de hechos) + 2-3 fragmentos de
`textos.md` + link al álbum + cover adjunta. Firmar sobrio, sin romper el tono.
Post-release está OK (reseñan releases ya salidas).
