# Framework spec — ÆM composition engine v0

## Propósito
Mini framework Python para componer música multipista de manera declarativa. Inspirado en el modelo conceptual de un DAW (pistas + eventos en el tiempo + efectos por pista), ejecutado completamente en código (no GUI, no tiempo real).

**Diseñado para:**
- Composición rápida iterativa (script-based, edit-run-listen).
- Síntesis from scratch con primitivas (sine, saw, noise) y composites (drone, voz, kick).
- Estéreo via panning equal-power.
- Render offline a WAV.

**No diseñado para:**
- Reproducción en tiempo real / DAW interactivo.
- MIDI in/out.
- Cientos de tracks o instrumentos profesionales.

## Domain model

```
┌──────────────────────┐
│   Composition        │   el tema
│   - duration: float  │
│   - name: str        │
│   - tracks: [Track]  ◆──── has many ────┐
└──────────────────────┘                  │
                                          ▼
                              ┌──────────────────────────────┐
                              │   Track                      │   una pista mono
                              │   - name: str                │
                              │   - gain: float              │
                              │   - pan: float ∈ [-1, +1]    │
                              │   - events: [(t, audio)]     │   eventos en el tiempo
                              │   - effects: [Callable]      │   cadena de FX
                              └──────────────────────────────┘
```

**Tipos:**
- `Event` = `Tuple[float, np.ndarray]` — (start_time_seconds, audio_buffer)
- `Effect` = `Callable[[np.ndarray], np.ndarray]` — función pura que transforma audio
- `Audio` = `np.ndarray` (float64, mono, sample rate fijo en `SR`)

**Invariantes:**
- `pan ∈ [-1, +1]` — equal-power panning
- `gain ≥ 0`
- `start_time ≥ 0` y `start_time + len(audio)/SR ≤ duration` (no enforced, se hace clipping en render)
- Audio buffers son float; se normalizan en el export final

## Render pipeline

```
─── Track.render_mono(total_dur) ────────────────────────────
buffer = zeros(total_dur × SR)
for (start_time, audio_event) in events:
    n_start = int(start_time × SR)
    n_end   = min(n_start + len(audio_event), len(buffer))
    buffer[n_start : n_end] += audio_event[:n_end - n_start]
buffer *= gain
for effect in effects:
    buffer = effect(buffer)
return buffer       # mono float ndarray

─── Composition.render_stereo() ─────────────────────────────
master_l = zeros(N); master_r = zeros(N)
for track in tracks:
    mono = track.render_mono(duration)
    angle = (track.pan + 1) × π/4         # [0, π/2]
    master_l += mono × cos(angle)         # equal-power
    master_r += mono × sin(angle)
return stack([master_l, master_r], axis=-1)   # shape (N, 2)

─── Composition.export_wav(filename, peak=0.85) ─────────────
audio = render_stereo()
audio *= peak / max(|audio|)              # peak normalize
write_wav(filename, SR, int16(audio × 32767))
```

## Public API

### `Composition`
| Método | Firma | Notas |
|---|---|---|
| constructor | `Composition(duration: float, name: str = 'untitled')` | duración en segundos |
| `add_track` | `(track: Track) -> Track` | fluent — retorna el track |
| `render_stereo` | `() -> np.ndarray` | shape `(N, 2)` |
| `export_wav` | `(filename: str, peak: float = 0.85)` | int16 PCM |
| `list_tracks` | `()` | debug, stdout |

### `Track`
| Método | Firma | Notas |
|---|---|---|
| constructor | `Track(name: str, gain: float = 1.0, pan: float = 0.0)` | |
| `add` | `(start_time: float, audio: np.ndarray) -> Track` | fluent |
| `fx` | `(effect_fn: Callable) -> Track` | fluent |
| `render_mono` | `(total_dur: float) -> np.ndarray` | |

### Synthesis primitives (módulo-level)
- `sine(freq, dur, amp=1.0) -> ndarray`
- `saw(freq, dur, amp=1.0) -> ndarray`
- `noise(dur, amp=1.0) -> ndarray`
- `silence(dur) -> ndarray`

### Composite instruments
- `detuned_drone(freqs: list, dur, amp, n_voices=3, detune_cents=10)` — drone estable con voces desafinadas
- `voice_pad(freq, dur, vibrato_rate=4.0, vibrato_depth=0.005, amp=0.3, n_harmonics=3)` — pad estilo voz (FM + armónicos)
- `kick(amp=0.8, dur=0.6, f0=80, fe=35)` — kick con pitch envelope
- `hihat(dur=0.04, amp=0.3)` — ruido con envolvente corta
- `melody(notes: list[(freq, dur)], amp=0.3, vibrato=True)` — melodía secuencial

### Effects (todos `np.ndarray -> np.ndarray`)
- `fade(audio, fi=0, fo=0)` — fade in/out
- `lpf(audio, cutoff, order=2)` — low-pass Butterworth via `scipy.signal.filtfilt`
- `hpf(audio, cutoff, order=2)` — high-pass equivalente
- `reverb(audio, decay=2.0, mix=0.3)` — multi-tap delay con decaimiento exponencial
- `distort(audio, amount=2.0)` — saturación tanh

## Constraints / assumptions
- **Sample rate fijo**: `SR = 22050` (constante de módulo). Para cambiar, editar `engine.py` (todas las funciones la referencian).
- **Mono per track**: estéreo solo emerge en `Composition.render_stereo()` via panning.
- **Render offline**: in-memory, sin streaming. Una composición de 60s × 22050 Hz × 10 tracks × float64 ≈ 100 MB de RAM peak. Para 5+ minutos × 30 tracks habría que streamear o chunkear.
- **WAV export**: 16-bit PCM. Para 24-bit o float, modificar `export_wav`.
- **No realtime**: cero latencia management. Cada `export_wav` reprocesa todo.
- **Reverb cheap**: es multi-tap delay, no convolución con IR real. Suficiente para sketches; insuficiente para mezcla final.

## Extension points

| Quiero... | Cómo |
|---|---|
| Agregar instrumento | nueva función que retorne `np.ndarray` (puede combinar primitivas) |
| Agregar efecto | nueva función `np.ndarray -> np.ndarray` (numpy/scipy libre) |
| Cambiar pan a 3D / Ambisonics | override `Composition.render_stereo` con nuevo cálculo de matriz |
| Solo / mute | flag en `Track`; filter en loop de `render_stereo` |
| Automation (gain over time) | reemplazar `track.gain *= ...` por multiplicación por curva en lugar de scalar |
| MIDI input | adapter externo que parse MIDI y haga `track.add()` por nota |
| Real-time preview | reemplazar `wavfile.write` con `sounddevice.play` (mismo render) |

## Limitaciones conocidas
- Sin solo/mute (trivial de agregar — flag bool en `Track`).
- Sin automation: gain/pan por track son escalares fijos. Para variación temporal, dividir en múltiples eventos con distintos gains.
- Reverb es lo más débil del stack — no compite con plugins reales. Aceptable para sketches conceptuales.
- Sin sidechain ni FX cross-track.
- No valida superposición de eventos (se suman sin advertencia, puede saturar).
- Sin quantización temporal — todos los `start_time` son floats libres.
- Sin tipado estricto (no `mypy`). Si esto crece, agregar dataclasses + type hints completos.
- Sin tests unitarios.

## Roadmap propuesto

| Versión | Features |
|---|---|
| v1 | gain automation curves, solo/mute, per-event panning |
| v2 | WAV sample loading, pitch shifting, time stretching (rubberband) |
| v3 | real-time preview (sounddevice), live coding loop |
| v4 | MIDI sequencer adapter, importar desde DAW |
| v5 | convolution reverb con IRs reales (scipy.signal.fftconvolve), sidechain compressor |

## Files

```
framework/aem/
├── core.py            constantes (SR) y helpers temporales
├── synth.py           primitivas (sine, saw, noise, silence)
├── instruments.py     composites (drone, voice_pad, kick, hihat, melody, riser)
├── effects.py         por-pista (fade, lpf, hpf, reverb, distort)
├── master.py          master FX (dirty_intro)
├── composition.py     Track + Composition (render, stems, export)
└── __init__.py        re-exports principales

tracks/<tema>/
├── arrangement_*.md          documentación narrativa
└── compose_*.py              composición específica que usa el framework

out/
├── index.json                lista de composiciones (consumido por el player)
└── <tema>/
    ├── master/<id>.wav       render final
    └── stems/<id>/           stems individuales + manifest.json

player/
├── index.html · styles.css · app.js
└── serve.py                  http server local
```

**Patrón de uso**: una composición por track del EP (`tracks/outbound/compose_full.py`, `tracks/crossing/compose_full.py`, `tracks/recursion/compose_full.py`), todas importando del mismo `framework/aem/`.

## Notas para el arquitecto que lo lea
- El framework es deliberadamente pequeño (no abstrae más de lo necesario). Diseñado para iterar rápido, no para escalar.
- Las clases `Track` y `Composition` son thin — la mayor parte del trabajo lo hacen las funciones puras (synth + effects). Esto es por diseño: cada función es testeable en aislamiento.
- La cadena de efectos en `Track` es una *fold*: cada efecto se aplica al output del anterior. Composable sin fricción.
- La síntesis es completamente determinística salvo por `np.random.randn` en `noise()` y `hihat()`. Para tests reproducibles, fijar `np.random.seed`.
- No hay singleton ni estado global salvo `SR`.
