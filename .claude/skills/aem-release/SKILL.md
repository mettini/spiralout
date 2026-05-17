---
name: aem-release
description: Knowledge de mastering, metadata y distribución para llevar el EP de demos scratch a release publicado. Activar cuando se trabaje con master chain (EQ + glue compression + limiter + LUFS), assembly del EP (concatenación con crossfades), export a formatos de release (WAV 44.1/24, FLAC, MP3 320, AAC), embedding de metadata + artwork (mutagen), o distribución (DistroKid/CD Baby/TuneCore/Bandcamp). Codifica targets de loudness streaming 2026, anti-patterns de over-compression, lessons learned sobre WAV vs FLAC para artwork, y comparación de agregadores.
---

# ÆM Release — knowledge de producción / mastering / distribución

Este skill se aplica DESPUÉS de la composición. Cubre el camino desde un
WAV scratch a un release publicado en plataformas. Complementa al skill
`aem-composer` (que cubre la creación).

## Filosofía

Mastering ≠ "hacerlo más fuerte". Mastering = balance, cohesión, headroom,
target loudness para que suene consistente con el resto del catálogo del
oyente en su plataforma.

Para AMBIENT específicamente: **preservar dinámica > maximizar loudness**.
Heavy limiting destruye el género. El streaming va a normalizar igual; mejor
sonar quieto y dinámico que aplastado.

## Reglas de oro mastering

### M1 — Headroom antes del master
La composición debe entregarse al master con peak de **-6 dBFS** (no -1.4
como hoy con `peak=0.85`). El limiter del master necesita espacio para
trabajar. Cambiar:
```python
comp.export_wav(filename, peak=0.5)   # antes 0.85
```

### M2 — Sample rate y bit depth
- Composición/render: **44.1 kHz / 32-bit float** (máximo headroom)
- Master delivery: **44.1 kHz / 24-bit WAV** (para distribución y FLAC)
- Plataforma final: la conversión la hace el agregador / Bandcamp

### M3 — Master chain orden
```
input → EQ → glue compression → stereo widening → limiter → LUFS normalize → output
```
NO invertir el orden. Limiter SIEMPRE último (o segundo a último si hay
loudness normalize después).

### M4 — LUFS targets (streaming 2026)
| plataforma | target | true peak |
|---|---|---|
| Spotify | -14 LUFS | -2 dBTP |
| Apple Music | -16 LUFS | -1 dBTP |
| YouTube Music | -14 LUFS | -1 dBTP |
| Tidal | -14 LUFS | -1 dBTP |
| Amazon Music | -14 LUFS | -2 dBTP |

**Sweet spot universal: -14 LUFS / -1 dBTP**. Un solo master sirve para
todas (con normalization activa, suena igual de fuerte percibido).

Para ambient: **-16 a -18 LUFS** está MEJOR (más dinámica, streaming sube
el volumen levemente).

### M5 — High-pass siempre
Cortar todo debajo de 25 Hz en el master final. Esa banda no es audible
pero ocupa headroom. Excepción: si el sub-bass del tema tiene componente
intencional debajo de 30 Hz (como el sub42 nuestro), bajar el HPF a 20 Hz.

### M6 — Stereo NO en bajos
El sub-bass DEBE estar en mono (centrado). Stereo widening solo en
mids/highs (>200 Hz). Sino el sistema PA en clubs cancela el sub.

### M7 — Limiter para ambient: lookahead largo, release lento
Lookahead 5-10ms, release 100-300ms. Más natural en pads/drones que un
brick-wall agresivo de electronic music.

## Master chain en código (framework AEM)

Ubicación: `framework/aem/master.py` — agregar `master_chain()` ahí.

```python
def master_chain(stereo_audio, lufs_target=-16.0, true_peak=-1.0,
                 hpf_freq=25, glue_amount=0.15):
    """Master chain estandar para ambient.
      1. HPF en hpf_freq (corta sub-sub inaudible)
      2. Glue compression (saturación tanh suave en bus)
      3. (Optional) stereo widening en mids/highs
      4. Limiter true peak
      5. LUFS normalize a lufs_target
    """
    # 1. HPF
    out = np.zeros_like(stereo_audio)
    for ch in range(2):
        out[:, ch] = hpf(stereo_audio[:, ch], hpf_freq)

    # 2. Glue (tanh suave)
    out = np.tanh(out * (1 + glue_amount)) / np.tanh(1 + glue_amount)

    # 3. Stereo widening — TODO si necesario
    # 4. Limiter
    out = soft_limit(out, ceiling=10**(true_peak/20))

    # 5. LUFS normalize — necesita libreria pyloudnorm
    out = lufs_normalize(out, target=lufs_target)

    return out
```

Dependencia nueva sugerida: `pyloudnorm` (medición LUFS estándar BS.1770).

## Reglas de oro metadata

### MD1 — WAV NO soporta artwork embebido
Es la limitación más importante. Workflow:
- WAV: solo para distribución a agregadores (que extraen el audio)
- FLAC: artwork embebido + metadata Vorbis comments → Bandcamp
- MP3 320: artwork embebido + ID3v2 tags → preview / SoundCloud
- AAC/m4a: artwork embebido + iTunes metadata → Apple Music delivery

### MD2 — Tags obligatorios para release
- `TITLE` — nombre del track
- `ARTIST` — nombre artístico
- `ALBUMARTIST` — mismo artista (importante para que iTunes/Apple agrupe)
- `ALBUM` — Heliopause
- `DATE` — año de release (2026)
- `TRACKNUMBER` y `TRACKTOTAL` — 1/3, 2/3, 3/3
- `GENRE` — Ambient / Drone / Dark Ambient / Electronic
- `COMPOSER` — mismo artista
- `COPYRIGHT` — © 2026 ÆM
- `ISRC` — generado por agregador (formato AA-XXX-YY-NNNNN)

### MD3 — Artwork specs
- Resolución: **3000×3000 px** (Spotify acepta hasta 4000×4000)
- Formato: **JPG** o PNG (JPG comprime mejor para embebido)
- File size: < 4 MB (Spotify), < 10 MB (Bandcamp)
- Color profile: sRGB (NO Adobe RGB — distorsiona en plataformas)
- Aspecto: 1:1 cuadrado siempre

Ya tenemos `docs/arte/04_arte_concepto_G_crt_3000.png`. Convertir a JPG
antes de embeber (PNG es 3x más grande).

### MD4 — Mutagen patrones
```python
# FLAC con artwork
from mutagen.flac import FLAC, Picture
flac = FLAC(filepath)
flac['title'] = 'Outbound'
flac['artist'] = 'ÆM'
flac['album'] = 'Heliopause'
flac['date'] = '2026'
flac['tracknumber'] = '1/3'

picture = Picture()
picture.type = 3  # cover (front)
picture.mime = 'image/jpeg'
picture.data = open('artwork.jpg', 'rb').read()
flac.add_picture(picture)
flac.save()

# MP3 con ID3v2
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC
mp3 = ID3(filepath)
mp3['TIT2'] = TIT2(encoding=3, text='Outbound')
mp3['TPE1'] = TPE1(encoding=3, text='ÆM')
mp3['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3,
                   desc='Cover', data=open('artwork.jpg', 'rb').read())
mp3.save()
```

## Reglas de oro distribución

### D1 — Bandcamp primero
Drop inicial en Bandcamp (gratis, sin agregador). Validar audiencia, recibir
feedback, ajustar si hace falta. Después agregador para plataformas
streaming.

### D2 — Agregador ideal según perfil
- **DistroKid** ($24.99/año unlimited): bedroom producers, EPs/singles
  frecuentes, 0% comisión, rápido a TikTok. **Recomendado para ÆM.**
- **CD Baby** ($14.99/álbum one-time, 9% comisión): catálogo permanente,
  baja frecuencia de release (1-2 por año).
- **TuneCore** ($24.99 Rising / $54.99 Pro): publishing administration
  incluido, mejor para covers o si querés royalties de publishing.

### D3 — ISRC: dejar que el agregador los genere
Salvo que tengas registrado tu propio prefijo en IFPI (proceso complicado),
dejá que el agregador genere los ISRC. Los formatea estilo
`AA-XXX-YY-NNNNN` automáticamente.

### D4 — Pre-save campaigns
DistroKid y CD Baby ofrecen pre-save links. Útil para acumular streams el
día del release (sube en algoritmos). Para ambient, menos crítico que para
géneros mainstream.

### D5 — Subir 1 versión, no 2
Spotify/Apple normalizan por sí mismos — NO subir "versión Spotify" y
"versión Apple". Un solo master a -14 LUFS funciona en todas.

## Anti-patterns

### AP-M1 — "Lo masterizo apuntando a -8 LUFS para que se escuche fuerte"
Falso. Spotify/Apple van a NORMALIZAR a -14/-16 LUFS. Tu track va a sonar
APLASTADO al mismo volumen percibido que uno hecho con dinámica preservada.
Para ambient esto es desastroso.

### AP-M2 — "Aplico el master chain DESPUÉS del peak normalize"
Mal orden. El master chain viene primero, normalize/LUFS adjustment al
final. Sino el limiter no tiene headroom para trabajar.

### AP-M3 — "WAV con artwork embebido"
WAV NO soporta artwork. Si necesitás cover, exportá FLAC o MP3.

### AP-M4 — "Embebo el PNG de 30 MB como artwork"
Convertir a JPG primero (~500 KB para 3000×3000). PNG en metadata es over.

### AP-M5 — "Subo 24-bit a Spotify para mejor calidad"
Spotify codifica en Ogg Vorbis 320 kbps. Subir 24-bit no mejora nada vs
16-bit. La diferencia se pierde en el codec. Lo que SÍ importa es el
mastering (LUFS, true peak, dinámica).

### AP-M6 — "Sigo el peak target del compose (0.85) sin cambiar para master"
0.85 = -1.4 dBFS. NO da headroom para limiter. Al renderizar para master,
bajar a `peak=0.5` (-6 dBFS) o `peak=0.25` (-12 dBFS).

### AP-M7 — "Stereo widening al sub-bass"
Cancela el sub en sistemas PA mono-summed (clubs). Sub SIEMPRE en mono.

### AP-M8 — "Subir el mismo track a Bandcamp y agregador con distinto título"
Confunde algoritmos y métricas. Mismo título, mismo ISRC, mismo artwork
en TODAS las plataformas.

## Checklist de pre-release

Antes de cada upload, validar:

- [ ] Sample rate 44.1 kHz (o 48 kHz si va a video)
- [ ] Bit depth 24-bit (16-bit OK pero 24 es estándar pro)
- [ ] LUFS integrated medido cerca del target (-14 a -16 para ambient)
- [ ] True peak ≤ -1 dBTP (medido con true peak meter, no sample peak)
- [ ] Dynamic range ≥ 8 LU
- [ ] Sub-bass en mono (verificar con stereo correlation meter)
- [ ] Sin clipping en ningún sample (verificar con peak meter)
- [ ] Metadata completo (title, artist, album, date, tracknumber, genre)
- [ ] Artwork embebido (FLAC/MP3) o adjunto (WAV)
- [ ] Filename consistente: `01 - Outbound.flac`, `02 - Crossing.flac`, etc.
- [ ] Verificar reproducción en al menos: smartphone speakers, auriculares,
      monitores. Si suena bien en los tres → release.

## Tools / libraries

| capa | tool | propósito |
|---|---|---|
| sample rate / format | `soundfile` | WAV 24-bit/32-float, FLAC |
| LUFS measurement | `pyloudnorm` | BS.1770 standard |
| MP3 encoding | `pydub` (con ffmpeg) o `lameenc` | MP3 320 |
| AAC encoding | `pydub` (con ffmpeg) | m4a |
| Metadata | `mutagen` | ID3v2, Vorbis, MP4 |
| Artwork conversion | `Pillow` | PNG → JPG, resize, sRGB |
| MIDI export | `mido` | partes melódicas/armónicas/rítmicas a .mid |
| Online mastering | LANDR / eMastered / CloudBounce | $5-20 por track |

## MIDI export — qué SÍ y qué NO

**Filosofía**: el framework genera AUDIO sintetizado (numpy). MIDI es
**partitura** — solo capturable para tracks con notas explícitas. Las
texturas de noise/synthesis no son representables.

### Sí se exporta a MIDI
- **Melodías**: voyager, voyager_counter, voyager_inverted, melody() events
- **Drones armónicos**: notas sostenidas (`detuned_drone([D, F, A], dur)`)
- **Bassline**: notas largas que siguen la armonía
- **Heart pulse / kicks**: percusión (canal 9 GM drums, nota 36)
- **Bells**: notas single puntuales
- **Voices**: voice_pad con freq específica
- **Chants**: chant_drone con freq base (formantes se pierden, queda la nota)

### NO se exporta a MIDI
- `cosmos` / `granular_bed` / `field_atmosphere` / `vinyl_crackle` — noise
- `wall_of_sound` — drones detuned + distort masivo (no tonal)
- `sub_punisher` / `sub_rumble` — sub-bass con LFO
- Whooshes / risers / downlifters / reverse_swells / glitches — sweeps
- `radio_interference` / `dirty_intro` — efectos master

### Patrón de uso (en script standalone)

```python
from aem.midi_helpers import make_builder, GM_INSTRUMENTS

mb = make_builder(bpm=120, ticks_per_beat=480)

# Melodía (lista de [start_seconds, [(freq, dur), ...]])
mb.add_melody_track('Voyager', [(120, VOYAGER_NOTES)],
                    program=GM_INSTRUMENTS['piano'], channel=3)

# Drone armónico (start, [freqs], duration)
mb.add_chord_track('Drone Dm', [(60, [146.83, 174.61, 220.00], 415)],
                   program=GM_INSTRUMENTS['pad_warm'], channel=1)

# Kicks
mb.add_kick_track('Heart Pulse', [30 + i for i in range(60)], channel=9)

# Single notes (bells, etc.)
mb.add_note_events_track('Bells', [(60, 587.33, 10), (120, 880.00, 12)],
                         program=GM_INSTRUMENTS['tubular_bells'])

mb.save('out.mid')
```

### Caso de uso de MIDI en el release

| audiencia | qué gana con MIDI |
|---|---|
| Productor/musico que quiere remasterizar | abre en su DAW, asigna instrumentos VST/sampler reales |
| Instrumentista que quiere grabar piano/cuerdas | tiene la partitura exacta sin transcribir |
| Remixer en Bandcamp (stems gratis) | catálogo completo: WAV stems + MIDI |
| Vos en el futuro (re-producción con mejores sintes) | abrís en Logic/Ableton sin recompilar Python |
| Compartir con músico que no programa | standard universal entendido por cualquiera |

NO sirve para: distribución a streaming. Spotify/Apple/Bandcamp consumen
audio (FLAC/MP3/WAV), no MIDI.

## Estructura de archivos del release

```
transmissions/01/release/
├── masters/                          # masters finales (WAV 24/44.1)
│   ├── 01_outbound_master.wav
│   ├── 02_crossing_master.wav
│   ├── 03_recursion_master.wav
│   └── 00_heliopause_continuous.wav  # EP encadenado de 24:00
├── distribution/                     # archivos para subir a agregador
│   ├── flac/
│   │   ├── 01 - Outbound.flac
│   │   ├── 02 - Crossing.flac
│   │   └── 03 - Recursion.flac
│   ├── mp3/                          # 320 kbps para preview
│   └── wav_44k/                      # WAV 16-bit para CD Baby si lo pide
├── artwork/
│   ├── cover_3000.jpg                # 3000×3000 sRGB JPG
│   └── cover_1500.jpg                # backup más chico
├── metadata.json                     # source of truth para todos los tags
└── README.md                         # checklist específica del release
```

`release/` debe estar en `.gitignore` — son outputs derivables.

## Referencias

Fuentes detalladas + URLs en `docs/11_research_composition.md`
(secciones que se agregan: mastering ambient LUFS 2026, metadata mutagen,
distribución agregadores 2026, samples Voyager Golden Record).

Doc maestro del pipeline completo: `docs/12_release_pipeline.md`.
