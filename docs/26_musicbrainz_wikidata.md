# 26 — MusicBrainz + Wikidata · planillas para pegar

> Campos exactos para cargar ÆM / Heliopause / Spiral Out. Vos creás las
> cuentas y pegás; yo dejo los valores. Datos canónicos =
> `transmissions/01/release/metadata_proposal.md`.

## ⚠️ Orden importa (por el tema notability)

1. **MusicBrainz primero.** No tiene barrera de notability — cualquiera puede
   agregar un artista/release. Hacelo ahora (~30 min).
2. **Wikidata DESPUÉS, y con cuidado.** Wikidata **sí** exige notability +
   fuentes independientes. Un proyecto debut sin prensa puede ser **borrado**
   por los editores. **Recomiendo esperar** a tener 1-2 reseñas de blogs
   (las del pitch) para citar como fuentes. Si igual querés cargarlo ya,
   dejá el MusicBrainz ID como identificador (P434) — ayuda a sostenerlo.

MusicBrainz también es lo que alimenta a Last.fm, ListenBrainz, Roon, etc. →
más ROI inmediato que Wikidata.

---

## A · MusicBrainz

Cuenta (editor, handle neutro): https://musicbrainz.org/register

Links directos para crear cada entidad (logueado):
- **Add Artist** (ÆM) → https://musicbrainz.org/artist/create
- **Add Label** (Spiral Out) → https://musicbrainz.org/label/create
- **Add Release** (Heliopause — acá cargás release group + tracks + ISRCs de una) → https://musicbrainz.org/release/add

Orden sugerido: Label → Artist → Release (así al crear el release ya podés
linkear el label y el artista existentes).

### A1 · Artist
| Campo | Valor |
|---|---|
| Name | `ÆM` |
| Sort name | `AEM` (alfabeto plano — en MB el sort name es para ordenar; `Æ`→`AE`) |
| Type | **Other** (proyecto/persona faceless — no es persona real ni banda) |
| Area | *(dejar vacío — el proyecto es sin origen declarado)* |
| Disambiguation | `project on the Spiral Out label` — neutra, distingue de los otros mil AEM SIN encasillar en un género (no es descripción de estilo, solo lo distingue). |
| URLs (relationships) — **URLs de ARTISTA, no de álbum** (MB rechaza `/album/` en el artista) | homepage `https://spiralout.space/aem/` · Bandcamp `https://aemtransmissions.bandcamp.com` · SoundCloud `https://soundcloud.com/aemtransmissions` · YouTube `https://www.youtube.com/@aem.transmissions` · Spotify `https://open.spotify.com/artist/0aWMHS1wSqci4Omo4RRJ2K` · Apple Music `https://music.apple.com/us/artist/æm/6773984882` · Qobuz `https://www.qobuz.com/ar-es/interpreter/m-74/10851141` · *(Tidal/Amazon de artista: sacar de la app si querés — son secundarias)* |

### A2 · Label
| Campo | Valor |
|---|---|
| Name | `Spiral Out` |
| Type | **Imprint** |
| Area | *(vacío)* |
| Disambiguation | `experimental sound lab / label (spiralout.space)` |
| URL | `https://spiralout.space` |

### A3 · Release Group
| Campo | Valor |
|---|---|
| Title | `Heliopause` |
| Artist | `ÆM` |
| Primary type | **Album** *(3 tracks/24 min es borde EP; Album es defendible y es lo que dice la metadata. Si preferís, EP también sirve.)* |
| Secondary type | *(ninguno)* |

### A4 · Release (la edición concreta)
| Campo | Valor |
|---|---|
| Title | `Heliopause` |
| Release group | `Heliopause` (el de arriba) |
| Artist | `ÆM` |
| Date | `2026-05-16` (fecha de release confirmada) |
| Country | `[Worldwide]` (XW) |
| Label | `Spiral Out` · Catalog# **⚠️ CD Baby (si asignó)** |
| Barcode (UPC) | **⚠️ del panel CD Baby** |
| Status | `Official` |
| Packaging | `None` (digital) |
| Language | `[No lyrics]` · Script `Latin` |
| Format | `Digital Media` |

**URLs de la release (pegar como relationships del Release — todas reales):**
- Bandcamp: `https://aemtransmissions.bandcamp.com/album/heliopause`
- Spotify: `https://open.spotify.com/album/5omJDu1rZwe9YFeAWONY6x`
- Apple Music: `https://music.apple.com/album/heliopause-ep/6773985527`
- Tidal: `https://tidal.com/album/528526670`
- Amazon Music: `https://music.amazon.com/albums/B0H34YZ4ZK`
- Qobuz: `https://www.qobuz.com/album/heliopause-aem/eotey7erxe23d`
- YouTube Music: `https://music.youtube.com/playlist?list=OLAK5uy_kJZJP4n5YQfW1XupmKEK5qQJ-YQzLZ198`
- SoundCloud: `https://soundcloud.com/aemtransmissions/sets/heliopause`

### A5 · Tracklist (recordings)
| # | Title | Length | ISRC |
|---|---|---|---|
| 1 | `Outbound` | `8:00` | `USHM82659668` |
| 2 | `Crossing` | `13:00` | `USHM82659669` |
| 3 | `Recursion` | `3:00` | `USHM82659670` |

> El ISRC se carga en cada **recording** (Edit → ISRCs). Formato sin guiones.

MBIDs generados (creados 2026-07-08):
- **Artist** (ÆM): `0b250427-9d41-4d4c-9d12-b06e48dbc708`
- **Release Group** (Heliopause): `a421892a-4f1d-4d70-8f0e-484f16a22a04`
- **Release** (Heliopause, edición concreta): `107211b1-01f1-4f72-a49a-11fd1e87c029`
- **Label** (Spiral Out): `60da02e2-3b09-4db6-a9c0-5e545e6044a5`

---

## B · Wikidata (después de MusicBrainz + idealmente ≥1 fuente)

Cuenta: https://www.wikidata.org → "Create a new item". Statement = `Propiedad → Valor`.

### B1 · Item ÆM (artista)
- **Label (en):** `ÆM` · **(es):** `ÆM`
- **Description (en):** `faceless music project` · **(es):** `proyecto de música sin rostro`
  *(sin género — no encasillar el proyecto; las transmissions varían de estilo)*
- **Also known as:** `AEM`
- Statements:
  - `instance of (P31)` → `musical project` (Q107458278) *(o `musical group` Q215380 si P31 no acepta)*
  - **NO poner `genre (P136)` en el artista** — el género va en el álbum (B2), no en ÆM.
  - `record label (P264)` → `Spiral Out` *(linkear al item B3 una vez creado)*
  - `official website (P856)` → `https://spiralout.space/aem`
  - `MusicBrainz artist ID (P434)` → `0b250427-9d41-4d4c-9d12-b06e48dbc708`
  - `country of origin (P495)` → *(opcional — dejar vacío para mantener faceless)*

### B2 · Item Heliopause (álbum)
- **Label (en):** `Heliopause` · **Description (en):** `2026 album by ÆM`
- **Description (es):** `álbum de 2026 de ÆM`
- Statements:
  - `instance of (P31)` → `album` (Q482994)
  - `performer (P175)` → `ÆM` (item B1)
  - `publication date (P577)` → `2026` (afinar al día exacto)
  - `record label (P264)` → `Spiral Out` (item B3)
  - `genre (P136)` → `ambient music` (Q189201)
  - `number of parts of this work (P2635)` → `3`
  - `MusicBrainz release group ID (P436)` → `a421892a-4f1d-4d70-8f0e-484f16a22a04`

### B3 · Item Spiral Out (sello)
- **Label (en):** `Spiral Out` · **Description (en):** `experimental music label and sound lab`
- **Description (es):** `sello y laboratorio de sonido experimental`
- Statements:
  - `instance of (P31)` → `record label` (Q18127)
  - `official website (P856)` → `https://spiralout.space`
  - `MusicBrainz label ID (P966)` → `60da02e2-3b09-4db6-a9c0-5e545e6044a5`

> Si un editor pone "notability" en duda: las fuentes válidas son reseñas de
> blogs independientes (no el propio sitio). Por eso conviene Wikidata
> **después** del pitch. Sin fuentes, dejá al menos los P434/P436/P966
> (MusicBrainz IDs) que dan verificabilidad.
