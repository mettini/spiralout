# Spiral Out — repo umbrella

Repo del proyecto **Spiral Out**: laboratorio experimental de sonido en la
intersección entre composición humana y AI. Bundlea **todo** bajo un solo
techo, no solo el album.

Primera transmisión: **ÆM / Heliopause — Transmission 01** (3 temas, 24 min).

> Repo: `spiralout` en `github.com/mettini/spiralout`. Carpeta local:
> `~/git/spiralout/`. (Originalmente "My First Album").

## Estructura

```
spiral-out/
├── README.md                  (este archivo — punto de entrada)
├── CLAUDE.md                  contexto para Claude (umbrella)
├── Taskfile.yml               TODO el pipeline expuesto como `task <nombre>`
├── .gitignore                 outputs renderizables, samples pesados, etc.
│
├── docs/                      concepto / lore / brief / vision / design system
├── framework/                 ÆM Python audio framework (composición declarativa)
│   ├── CLAUDE.md
│   ├── README.md
│   └── aem/
├── transmissions/             releases (cada NN/ = una transmisión)
│   ├── CLAUDE.md
│   └── 01/                    ÆM / Heliopause / Transmission 01
├── site/                      website (spiralout.space, Cloudflare Pages)
│   ├── CLAUDE.md
│   └── spiralout/             home + /aem + share images + favicons
├── player/                    debug web player (Web Audio API, sin build)
└── scripts/                   utilidades CLI (QA, render, release, artwork, share)
```

Cada subdir tiene su propio `CLAUDE.md` con las reglas de su área.

## Quickstart

```bash
task install                  # deps Python (numpy, scipy)
task install:release          # deps release (soundfile, pyloudnorm, mutagen, …)
task serve                    # player local en http://localhost:8765/player/
task render:all               # renderea TODO lo de la transmission activa
task qa:all                   # QA exhaustivo (estatico + spectral + voyager + …)
task release:plan             # status del pipeline de release
```

`TX=02 task render:all` cambia la transmission activa (default `01`).

---

# Task reference — TODO lo que hace el pipeline

Lista completa expuesta por el Taskfile. `task --list` lo dumpea todo.

## Setup

| comando | qué hace |
|---|---|
| `task install` | instala numpy + scipy (base) |
| `task install:release` | instala soundfile, pyloudnorm, mutagen, pydub, Pillow, mido (release) |
| `task gen:install` | instala torch + diffusers + transformers + accelerate (AI artwork) |
| `task site:install` | instala wrangler globalmente (Cloudflare Pages CLI) |
| `task site:login` | autentica con Cloudflare via OAuth en el browser (una vez) |

## Player local

| comando | qué hace |
|---|---|
| `task serve` | arranca el player en background y abre el browser |
| `task serve:fg` | arranca en foreground (ctrl+c para parar) |
| `task serve:stop` | mata el player local |
| `task serve:status` | dice si está corriendo y en qué puerto |
| `task serve:logs` | tail del log |
| `task open` | abre el player en el browser (asume server arriba) |

## Render — por tema y por prototipo

### Outbound (8:00)
| comando | qué hace |
|---|---|
| `task render:outbound` | full master + stems |
| `task render:outbound:v0` | prototipo BALANCED (60s) |
| `task render:outbound:v1` | prototipo TEXTURE (60s) |
| `task render:outbound:v2` | prototipo RHYTHMIC (60s) |
| `task render:outbound:all` | full + 3 prototipos + rebuild index |

### Crossing (13:00)
| comando | qué hace |
|---|---|
| `task render:crossing` | full master + stems |
| `task render:crossing:v0` | prototipo DARK MASS (Lustmord-style) |
| `task render:crossing:v1` | prototipo DUNE CHANT (vocal grave) |
| `task render:crossing:v2` | prototipo VOID DRIFT (espacial) |
| `task render:crossing:all` | full + 3 prototipos + rebuild index |

### Recursion (3:00)
| comando | qué hace |
|---|---|
| `task render:recursion` | full master + stems |
| `task render:recursion:A` | proto A — BLACK MASS RETURN (Sunn O))) drone metal) |
| `task render:recursion:B` | proto B — GHOST IN THE MACHINE (Burial glitch) |
| `task render:recursion:C` | proto C — ETERNAL RECURRENCE (Reich phase music) |
| `task render:recursion:all` | full + 3 prototipos + rebuild index |

### Pipelines agregados
| comando | qué hace |
|---|---|
| `task render:all` | renderea TODO lo de la transmission activa |
| `task render:final` | 3 temas full + master:bounce:all + ep:assemble (sin prototipos) |
| `task render:full` | render COMPLETO + master + ep + QA exhaustivo (un solo comando) |
| `task index:rebuild` | reconstruye `transmissions/<TX>/out/index.json` |
| `task finalize:outbound -- <v>` | snapshot del outbound como versión final (ej `task finalize:outbound -- v2`) |

## Voyager — el motivo recurrente

El "voyager" es el alma del album. **Cambios al voyager requieren aprobación
del user + diff vs benchmark** (`task qa:voyager`).

| comando | qué hace |
|---|---|
| `task voyager:quena` | render Voyager QUENA (flauta espacial, reverb gigante) |
| `task voyager:tool` | render Voyager TOOL (stereo delay + bajo Wal + drone) |
| `task voyager:roach` | render Voyager STEVE ROACH (pad ambient layered) |
| `task voyager:all` | render los 3 sabores + rebuild index |
| `task voyager:benchmark` | ⚠️ regenera el benchmark — solo con aprobación del user |

## QA — siempre antes de avisar al user

**Regla**: después de cada render, correr `task qa:spectral` mínimo. El
scan estático solo no alcanza — hay frituras que solo se ven en la FFT.

| comando | qué hace |
|---|---|
| `task qa -- <theme> <comp_id>` | QA de una composición puntual (ej `task qa -- crossing crossing_v0`) |
| `task qa:scan` | QA estático de código (detecta T_NOISE_FRITURA en compose files) |
| `task qa:spectral` | QA espectral sobre WAVs (HOT 1.5-4 kHz + BRIGHT 4-8 kHz) |
| `task qa:stems` | QA por stem (transientes abruptos, onset/offset duros, frituras) |
| `task qa:perceptual` | densidad de capas + overlap melódico + transientes anómalos |
| `task qa:voyager` | regresión voyager_safe — diff espectral contra benchmark |
| `task qa:finals -- <theme> <ver>` | QA de un final versionado (ej `task qa:finals -- outbound v1`) |
| `task qa:all` | TODO junto (estático + spectral + voyager + stems + perceptual + runtime) |

## Mastering + EP

| comando | qué hace |
|---|---|
| `task master:bounce -- <theme>` | aplica master chain (HPF + glue + limiter + LUFS) a un tema |
| `task master:bounce:all` | master chain a los 3 temas |
| `task ep:assemble` | concatena los 3 masters con crossfades → master continuo del EP (24:00) |
| `task expose:masters` | expone los masters al player (aparecen como `<theme>_MASTER`) |
| `task review:masters` | abre carpeta de masters en Finder + lista contenido |

## Export — formatos de release

| comando | qué hace |
|---|---|
| `task export:formats` | masters → FLAC + MP3 320 + WAV 16-bit (3 tracks individuales) |
| `task export:formats:full` | igual + incluye el continuous EP |
| `task export:midi` | exporta los 3 temas a MIDI (partes melódicas/armónicas/rítmicas) |

## Release — distribución

| comando | qué hace |
|---|---|
| `task release:plan` | imprime el plan de release y dónde estamos |
| `task release:check` | valida masters: SR, bit depth, LUFS, true peak, stereo correlation |
| `task tag` | **WIP** — embebe metadata + artwork en FLAC y MP3 (mutagen) |
| `task release:bundle` | **WIP** — arma `transmissions/<TX>/release/distribution/` listo para upload |

## Artwork (AI image gen local, open source)

Workflow: `task gen:install` (una vez) → `task gen:list` → `task gen:artwork -- <brief>`.

Output: `transmissions/<TX>/artwork/generated/<brief>/<timestamp>_NN.png`.

| comando | qué hace |
|---|---|
| `task gen:list` | lista briefs de artwork disponibles |
| `task gen:artwork -- <brief>` | genera 4 imágenes con SDXL Turbo (default, ~7 GB, rápido) |
| `task gen:artwork:hq -- <brief>` | genera con SDXL base (~13 GB, mejor calidad, más lento) |
| `task gen:artwork:flux -- <brief>` | genera con FLUX.1 schnell (~24 GB, SOTA, requiere 32+ GB RAM) |
| `task gen:open` | abre la carpeta de artwork generado en Finder |
| `task gen:all` | genera 4 imágenes por cada brief (TODO el pack, 30-60 min) |

## Site (spiralout.space)

| comando | qué hace |
|---|---|
| `task site:dev` | preview local del site en http://localhost:8788 (wrangler) |
| `task site:deploy` | deploy a Cloudflare Pages (proyecto `spiralout`, branch `main`) |
| `task site:list` | últimos deployments |
| `task site:share` | regenera todas las share images (OG, IG, Pinterest) para `/` y `/aem` |

Detalles del site (stack, tipografía, share image specs por red) → `site/CLAUDE.md`.

## Limpieza

| comando | qué hace |
|---|---|
| `task clean:out` | borra TODOS los WAVs renderizados de la transmission activa (con confirmación) — código intacto |
| `task clean:cache` | borra `__pycache__` y `*.pyc` del framework + scripts |

## Otros

| comando | qué hace |
|---|---|
| `task production:upgrade` | **WIP** — sube SR a 44.1 kHz en `framework/aem/core.py` y re-renderiza todo |
| `task --list` | dumpea todas las tasks (esta tabla, generada por taskfile) |

---

## El player

Debug player web local. Levantado con `task serve`:

- Dropdown para elegir composición (lee `transmissions/<TX>/out/index.json`).
- Play / pause / stop / restart.
- Click en cualquier waveform → seek.
- **M** mute, **S** solo por pista.
- Slider de gain por pista + master gain.
- Espacio = play/pause.
- "unmute all" / "unsolo all".

Suma stems en el browser via Web Audio API. Suena MUY similar al master pero
no idéntico: el `master_fx` (ej `dirty_intro`) opera sobre la suma estéreo
final, no sobre cada stem individual. Sirve para escuchar pistas individuales
y entender qué está sonando dónde.

## Workflow típico de iteración

1. Editás `transmissions/<TX>/themes/<track>/compose_full.py` (mover entrada
   de una pista, cambiar gain, agregar evento, etc).
2. `task render:<track>`.
3. **`task qa:spectral`** ← obligatorio antes de avisar al user.
4. En el player apretás `↻` reload (o cambiás de composición y volvés).
5. Solo a la pista que retocaste para verificar.
6. Unsolo, escuchás contexto.
7. Repetir.

Para tracks que tocan el voyager, agregar `task qa:voyager`.

## El framework

Mini framework Python para composición multipista, render offline a WAV.
Tres conceptos:

- **Composition** = el tema (duración + tracks).
- **Track** = una pista mono (eventos en el tiempo + cadena de fx + gain + pan).
- **Effect** = función pura `audio → audio`.

```python
from aem import Composition, Track
from aem.synth import sine
from aem.instruments import detuned_drone, kick
from aem.effects import fade, reverb
from aem.master import dirty_intro

comp = Composition(60, name='ejemplo')
drone = comp.add_track(Track('drone', gain=0.4))
drone.add(0, detuned_drone([220, 277], 60))
drone.fx(lambda a: fade(a, fi=4, fo=4))
drone.fx(lambda a: reverb(a, decay=3, mix=0.4))
comp.export_wav('out/ejemplo.wav', master_fx=lambda a: dirty_intro(a, 8, 4))
```

Doc completa: [`framework/README.md`](framework/README.md) y especificación
en [`docs/08_framework_spec.md`](docs/08_framework_spec.md). Reglas y
antipatterns: [`framework/CLAUDE.md`](framework/CLAUDE.md).

## Pipeline de release

Para llevar las composiciones de demo scratch a release publicado en
plataformas, ver [`docs/12_release_pipeline.md`](docs/12_release_pipeline.md).
Cubre las 8 etapas: composición → producción → mixing → mastering →
EP assembly → export → metadata → distribución.

Skills relevantes:
- `aem-composer` — composición ambient/cinematic (técnicas + checklist QA)
- `aem-release` — mastering, metadata, distribución (LUFS targets 2026,
  comparación de agregadores, anti-patterns)

## Dependencias

- Python 3.10+
- numpy, scipy (base) — `task install`
- soundfile, pyloudnorm, mutagen, pydub, Pillow, mido (release) — `task install:release`
- torch + diffusers + transformers + accelerate (artwork) — `task gen:install`
- wrangler (site deploy) — `task site:install`
- [task](https://taskfile.dev) — `brew install go-task`

Para las share images: `rsvg-convert` + ImageMagick (`brew install librsvg imagemagick`).

## Estado actual

Ver [`transmissions/01/PLAN.md`](transmissions/01/PLAN.md) para el plan de
ejecución y pendientes de la transmisión activa.
