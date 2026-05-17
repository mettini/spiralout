# ÆM framework

Mini framework Python para composición musical multipista, render offline a WAV.
Hecho para iterar rápido (edit → run → escuchar). No es un DAW: es código.

## Estructura

```
framework/aem/
├── __init__.py        # re-exports principales (Composition, Track, SR)
├── core.py            # SR + helpers temporales
├── synth.py           # primitivas: sine, saw, noise, silence
├── instruments.py     # composites: detuned_drone, voice_pad, kick, hihat, melody, riser
├── effects.py         # por-pista: fade, lpf, hpf, reverb, distort
├── master.py          # master FX: dirty_intro
└── composition.py     # Track, Composition (render, stems, export)
```

## Capas

```
synth.py        ── primitivas puras (sine, noise…)
   ↓
instruments.py  ── usan primitivas (drone, voz, kick…)
   ↓
effects.py      ── transforman audio (filtros, reverb…)
   ↓
master.py       ── operan sobre el estéreo final
   ↓
composition.py  ── modelo: Track + Composition
```

Una pista (`Track`) es: `eventos en el tiempo` + `cadena de FX` + `gain` + `pan`.
Una composición (`Composition`) es: `duración` + `lista de tracks`.

## Patrón de uso

```python
from aem import Composition, Track
from aem.synth import sine
from aem.instruments import detuned_drone, kick
from aem.effects import fade, reverb
from aem.master import dirty_intro

comp = Composition(60, name='ejemplo')

# pista 1: drone armónico
drone = comp.add_track(Track('drone', gain=0.4, color='#7a5cb8'))
drone.add(0, detuned_drone([220, 277, 330], 60))
drone.fx(lambda a: fade(a, fi=4, fo=4))
drone.fx(lambda a: reverb(a, decay=3, mix=0.4))

# pista 2: kick a 60 BPM
pulse = comp.add_track(Track('pulse', gain=0.6, color='#d04545'))
for i in range(30):
    pulse.add(15 + i, kick(amp=1.0, dur=0.6))

# render
master_fx = lambda a: dirty_intro(a, dirty_until=8, transition_dur=4)
comp.export_wav('out/ejemplo.wav', master_fx=master_fx)
comp.export_stems('out/ejemplo_stems/', master_fx=master_fx)
```

`export_wav` produce el WAV master.
`export_stems` produce un WAV por pista al mismo nivel relativo que el master,
más un `manifest.json` que el player UI consume para mostrar las pistas.

## Convenciones

- **Sample rate**: `SR = 22050` (módulo-level en `core.py`).
- **Audio**: float numpy arrays, mono per-track. El estéreo emerge solo en
  `Composition.render_stereo()` via panning equal-power.
- **Color por pista** (`Track(color='#hex')`): hint visual, lo lee la UI del
  player. Opcional.
- **Fluent**: `track.add(...).fx(...).fx(...)` encadenable.
- **Determinístico** salvo `np.random.randn` en `noise()` y `hihat()`. Para
  reproducibilidad fijar `np.random.seed`.

## Dependencias

```
numpy >= 1.25
scipy >= 1.10
```

## Limitaciones conocidas

- Sin automation de gain/pan en el tiempo (workaround: dividir en eventos
  con distintos gains).
- Sin solo/mute en el modelo (el player UI hace mute/solo en runtime via
  Web Audio).
- Reverb es multi-tap delay barato — no convolución.
- Render in-memory, sin streaming. Una composición de 8 min × 22050 Hz × 14
  tracks × float64 ≈ 200 MB peak.
