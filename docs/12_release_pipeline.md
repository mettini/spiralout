# Pipeline de release — desde el concepto al disco en plataformas

Documento maestro. Explica todas las etapas que transforman una idea musical
en un release publicado. Sirve como guía conceptual + checklist + referencia.

## Estado actual del proyecto

```
✅ Concepto y narrativa             docs/00_concepto.md, 02_ep.md, 03_lore.md
✅ Diseño sonoro / paleta            docs/06_diseno_sonoro.md, skill aem-composer
✅ Framework de composición          framework/aem/
✅ Composición de los 3 temas        transmissions/01/themes/
✅ Render de demos (scratch)         transmissions/01/out/*.wav
✅ Arte de tapa FINAL del release    transmissions/01/artwork/cover_*.{jpg,png}
                                     (incluye TRANSMISSION 01, tracks, tiempos)
─────────────────────────────────────────────────────────────────────
⏳ Re-render a 44.1 kHz              ← próximo
⏳ Mastering                          ← próximo
⏳ Encadenado del EP (24:00)          ← próximo
⏳ Reemplazo de fuentes sintéticas
⏳ Export a formatos de release       ← FLAC + MP3 320 + WAV 44.1 / 24
⏳ Metadata + artwork embebido
⏳ Distribución (Bandcamp + agregador)
```

## Pipeline visual

```
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 1 — COMPOSICIÓN     (ya hecho ✓)             │
        │  Concepto → arrangement → compose.py → demo WAV     │
        │  Skill: aem-composer                                │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 2 — PRODUCCIÓN                               │
        │  • Re-render a 44.1 kHz / 24-bit                    │
        │  • (Opcional) Reemplazar fuentes sintéticas         │
        │  • Validación QA                                    │
        │  Skill: aem-composer + aem-release                  │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 3 — MIXING                                   │
        │  • Balance entre tracks (ya parcial)                │
        │  • Pan / depth                                      │
        │  • Bus processing por sección                       │
        │  Hoy: hecho dentro del compose                      │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 4 — MASTERING                                │
        │  • EQ del bus master                                │
        │  • Glue compression                                 │
        │  • Stereo widening selectivo                        │
        │  • Limiter final                                    │
        │  • Loudness normalization (LUFS target)             │
        │  Skill: aem-release                                 │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 5 — ASSEMBLY DEL EP                          │
        │  • Concatenar los 3 temas con crossfades            │
        │  • Verificar transiciones                           │
        │  • Master único de 24:00 + 3 individuales           │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 6 — EXPORT FORMATOS                          │
        │  • WAV 44.1 / 24-bit  → distribución                │
        │  • FLAC               → Bandcamp HQ                 │
        │  • MP3 320 kbps       → preview                     │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 7 — METADATA + ARTWORK                       │
        │  • ID3 tags (artista, título, álbum, año, género)   │
        │  • Artwork embebido (3000×3000 jpg) — solo FLAC/MP3 │
        │  • ISRC codes (los da el agregador)                 │
        │  Skill: aem-release                                 │
        └────────────────────┬────────────────────────────────┘
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  ETAPA 8 — DISTRIBUCIÓN                             │
        │  • Bandcamp directo (sin agregador, gratis)         │
        │  • DistroKid / CD Baby / TuneCore → Spotify, Apple, │
        │    Tidal, YouTube Music, Amazon Music, Deezer       │
        │  • SoundCloud directo                               │
        │  Skill: aem-release                                 │
        └─────────────────────────────────────────────────────┘
```

## Detalle por etapa

### Etapa 2 — Producción

**Sample rate**: hoy renderizamos a 22050 Hz (la mitad del estándar). Para
release necesitamos **44100 Hz** (CD/streaming) o **48000 Hz** (video).

Cambio en código:
```python
# framework/aem/core.py
SR = 44100  # antes 22050
```

Implicancias:
- Doble RAM por render (antes ~200 MB pico para 8 min × 14 tracks; ahora ~400 MB).
- Doble tiempo de render.
- Beneficio: agudos limpios, más espacio en frecuencias altas.

**Bit depth**: hoy 16-bit PCM. Para mastering pro se trabaja en **24-bit** o
**32-bit float**. El release final puede ser 16-bit (CD), 24-bit (HQ), o
ambos.

**Reemplazo de fuentes sintéticas** (decisión a tomar):
- Voyager Golden Record samples (archive.org, dominio público)
- CMB cosmic microwave background recordings (freesound.org)
- Strings/cello acústicos para los pads cinematográficos
- Field recordings reales (criptas/cuevas para Crossing dark)

Reemplazar 100% es trabajo grande. Híbrido (algunas síntesis + algunos
samples clave) es razonable. Otra opción: dejarlo full sintético — Stars
of the Lid o Eno también lo hacen.

### Etapa 4 — Mastering

El paso que más SEPARA un demo de un release. Cadena típica:

1. **EQ del bus** — balance espectral final
   - High-pass corte ~25 Hz (sub inaudible que ocupa headroom)
   - Brillo en mids/highs si suena opaco
   - Cortes quirúrgicos en frecuencias problemáticas

2. **Glue compression** — cohesión
   - Ratio bajo (1.5:1 a 2:1)
   - Threshold suave (1-3 dB de reducción)
   - Hace que el mix "respire junto"

3. **Stereo widening** — selectivo
   - NO ampliar bajo (el sub debe quedar en mono)
   - Ampliar mids/highs donde corresponda

4. **Limiter** — techo final
   - True peak ceiling: -1 dBTP (estándar streaming)
   - Para ambient: poco hard limiting, preservar dinámica

5. **LUFS normalize** — apuntar a target
   - **-14 LUFS integrated** = sweet spot streaming (Spotify/YouTube/Tidal/Amazon)
   - **-16 LUFS** = ideal Apple Music
   - Ambient PUEDE ir más bajo (-16 a -18) sin problema; la dinámica
     respira mejor

**Para ambient específicamente**: heavy limiting destruye el género.
Preservar 8-10 dB de rango dinámico. Streaming va a normalizar; mejor sonar
quieto y dinámico que aplastado.

### Etapa 5 — Assembly del EP

El concepto en `02_ep.md` dice:
> "sin silencios entre tracks — fade encadenado, una transmisión continua"

Hay que generar:
- 3 archivos individuales (Outbound 8:00, Crossing 13:00, Recursion 3:00)
  para distribución por separado
- 1 master único de 24:00 con crossfades de 5-10s entre temas para
  Bandcamp / playlists / experiencia continua

Crossfade típico: 8s. Outbound último 8s × 0.5 + Crossing primer 8s × 0.5
mezclados.

### Etapa 6 — Export formatos

| formato | uso | size aprox 24min |
|---|---|---|
| WAV 44.1/24 | distribución (DistroKid/CDBaby) | ~350 MB |
| FLAC | Bandcamp HQ + preservación | ~150 MB |
| MP3 320 kbps | preview / soundcloud | ~55 MB |
| AAC 256 (m4a) | Apple Music delivery | ~45 MB |
| **MIDI** | colaboración con músicos / DAWs / remixers | ~5 KB total |

Lib: `soundfile` (mejor que `scipy.io.wavfile` para 24-bit), `pydub` o
`ffmpeg-python` para MP3/AAC, `mido` para MIDI.

**MIDI export** (`task export:midi`): genera 3 archivos `.mid` con las
partes melódicas/armónicas/rítmicas (voyager, bassline, drones, heart
pulse, voices, bells). NO incluye texturas de noise/synthesis. Es para
colaboración — un productor puede abrir el MIDI en Logic/Ableton y
re-tocar las melodías con instrumentos VST profesionales. Ver skill
`aem-release` sección "MIDI export".

### Etapa 7 — Metadata + artwork

**WAV no soporta artwork embebido** — esto es importante. Para Bandcamp /
Apple Music los archivos relevantes son FLAC/MP3/AAC.

Tags estándar (Vorbis comments para FLAC, ID3v2 para MP3):
- TITLE, ARTIST, ALBUM, ALBUMARTIST
- DATE (año), TRACKNUMBER, TRACKTOTAL
- GENRE (Ambient / Drone / Dark Ambient / Electronic)
- COMPOSER, COPYRIGHT
- ISRC (lo da el agregador)
- COMMENT (links, créditos)
- Artwork (jpg 3000×3000 típico)

Lib: **mutagen** (estándar Python).

### Etapa 8 — Distribución

**Comparación 2026**:

| | DistroKid | CD Baby | TuneCore | Bandcamp directo |
|---|---|---|---|---|
| modelo | suscripción | one-time | suscripción | gratis |
| precio | $24.99/año unlimited | $9.99/single, $14.99/álbum | $24.99/año (Rising) o $54.99 (Pro) | gratis |
| comisión | 0% | 9% | 0% | 15% del primer pago, 10% después |
| velocidad | rápido (TikTok) | medio | medio | inmediato |
| catálogo | depende suscripción | permanente | depende suscripción | permanente |
| ideal para | bedroom producers que sacan EPs/singles seguido | catálogo permanente, baja frecuencia | covers, publishing | indie directo a fans |

**Recomendación para esta primera transmisión**:
1. **Bandcamp directo** primero (gratis, sin agregador) — drop suave a fans/early listeners
2. Después **DistroKid** ($24.99/año) para llegar a Spotify/Apple/Tidal

ISRC codes: cada track del release necesita un ISRC único. Te los genera
gratis tu agregador. Si querés autogenerar (artistas con prefijo propio),
tenés que registrarte en IFPI.

## Costos del release (estimado total)

| ítem | costo aprox | obligatorio? |
|---|---|---|
| Bandcamp directo | $0 (15% comisión sobre ventas) | recomendado primero |
| DistroKid Musician | $24.99/año | sí, para Spotify/Apple |
| Mastering automatizado (LANDR/eMastered) | $5-20 por track | opcional, mejor que nada |
| Mastering engineer | $80-150 por track | opcional, calidad superior |
| Hosting de imágenes (artwork HQ) | gratis (Imgur/CDN propio) | no |
| Domain (heliopause.fm o similar) | $10-30/año | opcional |
| **TOTAL básico** (sin mastering pro, sin domain) | **$25/año** | |

## Decisiones que tomar antes de seguir

- [ ] ¿Reemplazamos síntesis con samples reales? (sí parcial / sí completo / no)
- [ ] ¿Mastering pro o automatizado?
- [ ] ¿Bandcamp solo o también Spotify/Apple desde el primer drop?
- [ ] ¿Domain propio o solo links a perfiles de plataformas?
- [ ] ¿Lanzar como EP único de 24:00 o 3 tracks separados?
- [ ] ¿Stems gratis disponibles para remix? (en línea con la ética open mencionada en `02_ep.md`)

## Comandos task del pipeline

Ver `Taskfile.yml` y `task --list` para todos los comandos. Pipeline
completo (cuando estén implementados todos):

```bash
task render:all                  # ✓ ya implementado — genera demos scratch
task qa:all                      # ✓ ya implementado — valida la mezcla

# pipeline de release:
task master:bounce:all           # ✓ aplica master chain a los 3 temas
task ep:assemble                 # ✓ concatena 3 temas con crossfades
task export:formats:full         # ✓ FLAC + MP3 320 + WAV 24/44.1 + continuous
task export:midi                 # ✓ MIDI de partes melódicas/armónicas/rítmicas
task release:check               # ✓ validación final (LUFS, peaks, etc)
task expose:masters              # ✓ expone masters al player web

# pendientes:
task tag                         # embebe metadata + artwork (próximo)
task release:bundle              # orquesta todo end-to-end
```

## Skills

- `aem-composer` (`.claude/skills/aem-composer/SKILL.md`) — composición
- `aem-release` (`.claude/skills/aem-release/SKILL.md`) — mastering, metadata, distribución

## Próximos pasos sugeridos

1. **Doc + skill + tasks** ✓ (este momento)
2. Subir SR a 44.1 kHz + re-render
3. Implementar master chain básico
4. Concatenar EP
5. Decidir samples reales (ver opciones en archive.org)
6. Implementar export formats + tagging
7. Bandcamp drop privado para validar
8. DistroKid → Spotify/Apple
