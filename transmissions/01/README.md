# Transmission 01 — primera entrega

Versión condensada del EP **Heliopause** para la primera transmisión.

## Estructura

| # | Tema | Duración | Estado |
|---|---|---|---|
| 1 | **Outbound** | 8:00 | v6 ✓ — técnicas Lustmord/Burial aplicadas |
| 2 | **Crossing** | 13:00 | full ✓ — con peak "momia se pudre" |
| 3 | **Recursion** | 3:00 | full ✓ — híbrido A (Sunn O))) ) + B (Burial) |
| | **Total** | **24:00** | |

> Nota: La visión completa del EP (Fibonacci 8+13+21=42) está en
> `docs/02_ep.md`. Esta primera transmisión es una versión condensada
> (8+13+3=24) para release inicial. Las versiones largas pueden venir
> en transmissions futuras.

## Arte de tapa final ✓

`transmissions/01/artwork/`:
- `cover_master_3000.png` — master PNG (8 MB) — backup calidad máxima
- `cover_streaming_3000.jpg` — 3000×3000 sRGB JPG (1.8 MB) — para metadata
  embebido en FLAC/MP3 + delivery a agregadores
- `cover_1500.jpg` — 1500×1500 backup (475 KB) — para preview / web /
  Bandcamp page / social

Contenido del arte: ÆM logo, HELIOPAUSE, TRANSMISSION 01, ORIGIN Em,
tracklist (01 OUTBOUND 08:00, 02 CROSSING 13:00, 03 RECURSION 03:00),
trayectoria de Voyager 1, wireframe landscape, SPIRAL/1.

## Estructura de archivos

```
transmissions/01/
├── README.md                          (este)
├── themes/
│   ├── outbound/
│   │   ├── arrangement_full.md        storyboard del tema completo
│   │   ├── compose_full.py            compose en curso
│   │   ├── prototypes/                prototipos 60s (v0, v1, v2)
│   │   │   ├── arrangement_v0.md
│   │   │   ├── compose_v0.py
│   │   │   ├── compose_v1.py
│   │   │   └── compose_v2.py
│   │   └── finals/                    versiones aprobadas
│   │       └── v1/
│   │           ├── master.wav
│   │           ├── stems/
│   │           ├── compose_snapshot.py
│   │           └── version.md
│   ├── crossing/
│   │   ├── arrangement.md             storyboard + 3 prototipos descritos
│   │   └── prototypes/                prototipos 90s
│   │       ├── compose_v0.py          DARK MASS
│   │       ├── compose_v1.py          DUNE CHANT
│   │       └── compose_v2.py          VOID DRIFT
│   ├── recursion/
│   │   └── concept_notes.md           ideas iniciales (a implementar)
│   └── maquetas/                      prototipos historicos por genero
│       ├── legacy_compose.py
│       └── finals/                    m1..m8 (30s c/u)
└── out/                               (regenerable con task render:*)
    ├── outbound/
    │   ├── master/
    │   └── stems/
    ├── crossing/
    │   ├── master/
    │   └── stems/
    └── index.json                     consumido por el player
```

## Comandos

Desde el root del proyecto:

```bash
task serve                    # arranca el player
task render:outbound          # rerendear outbound completo
task render:crossing:all      # los 3 prototipos de crossing
task render:all               # todo
task finalize:outbound -- v2  # snapshot del outbound como v2
```

El player (http://localhost:8765/player/) muestra todas las composiciones
de la transmission activa (default `01`). Para cambiar:
`http://localhost:8765/player/?tx=02` (cuando exista).
