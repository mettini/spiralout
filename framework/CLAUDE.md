# framework/ — the `aem` audio framework

A small Python framework for **declarative multi-track composition** with
offline render to WAV. Not a DAW. Not a real-time engine. It's a library
that gives you `Composition`, `Track`, and a stack of pure-function effects;
you write Python; you get a WAV.

## Layers (read bottom-up)

```
synth.py         → primitives (sine, saw, noise, silence)
instruments.py   → composites (detuned_drone, voice_pad, kick, hihat, melody, riser, flute_motif)
motifs.py        → musical motifs (voyager_motif, voyager_safe_fx, VARIATIONS, VOYAGER_NOTES, VOYAGER_NOTCH_FREQS)
effects.py       → per-track FX (fade, lpf, hpf, reverb, distort, lfo_amp, notch_eq)
master.py        → stereo-bus FX (dirty_intro, master chain v2)
auto_fixes.py    → pre-export structural fixes (HPF stack tame, sustain compressor)
voyager_factory.py → presets for the Voyager motif (roach_octlow, tool_classic, flute_warm, safe_basic)
composition.py   → the model: Track, Composition (.render_*(), .export_wav(), .export_stems())
core.py          → SR (= 22050) + time helpers
```

## Mental model

- `Composition(duration_s, name=...)` — a fixed-length canvas.
- `Track(name, gain, pan, color)` — mono. Events on a timeline. A chain of
  FX. Pan is equal-power. `color` is a hint the player UI uses to color
  waveforms.
- `Effect` is just a function `audio: np.ndarray -> np.ndarray`. Compose
  them via `track.fx(fn)`. They're applied in order, before the master.
- `master_fx` is a single function passed to `export_wav` that operates on
  the **final stereo sum** (post-pan, post-track-fx).

Fluent style is encouraged:
```python
drone = comp.add_track(Track('drone', gain=0.4, color='#7a5cb8'))
drone.add(0, detuned_drone([220, 277], 60))
drone.fx(lambda a: fade(a, fi=4, fo=4))
drone.fx(lambda a: reverb(a, decay=3, mix=0.4))
```

## Voyager — the protected motif ⚠️

The "voyager" is a melodic+FX signature that threads through Heliopause.
**It is the soul of the album.** Per user instructions:

- Use `voyager_safe()` / `voyager_safe_fx()` — the validated wrappers.
- For new placements use `voyager_factory.voyager_track(comp, ..., preset=...)`
  with a known preset (`roach_octlow` is the user-validated default).
- **Do not change voyager defaults** without explicit user approval AND a
  spectral / perceptual diff against the benchmark:
  ```bash
  task qa:voyager
  ```
- If a regression test fails, treat it as a release blocker.

Background: see `memory/voyager_protegido.md` and
`memory/heliopause_v2_merge_2026-05-15.md`.

## Master chain v2 (merged May 2026)

Live in `master.py`. Promoted from `lab/clear_experiment` after the user's
"underwater / muffled" feedback. Key choices, none of which should be
reverted casually:

- Mid scoop **−2.5 dB @ 280 Q=0.8** (wider than original).
- Surgical notch at **1960 Hz** — kills `chinchin` resonance from the
  voyager_swell/degraded without touching bell timbres.
- Exciter uses **`tanh`**, NOT `np.abs()`. abs() creates ~820
  inter-modulations that read as fritura/static on complex mixes.
  See `memory/abs_rectifier_exciter_antipattern.md`.
- Dual air shelf: **+1.5 dB @ 5 kHz + +2 dB @ 11 kHz**.
- Glue tanh **0.08** (not 0.15) — fewer accumulated even harmonics.
- Soft limiter **−0.5 dBTP** — more headroom than the −1 dB original.

## Auto-fixes (pre-export)

`auto_fixes.apply_auto_fixes(comp)` solves two structural classes of issues
that show up in every ambient composition here:

1. **Low-end stack** (100–300 Hz): drones, chants, voice_pads, pads, bells
   all crowd the same band. Per-track HPF at each track's lowest *useful*
   fundamental clears the band without needing the mid scoop to compensate.
2. **Sustain resonance** (Fletcher-Munson 1.5–3 kHz): bells and voyagers
   sustain harmonics in the ear-fatigue band. A single-band sustain
   compressor reduces sustain only, preserves attacks.

Call `apply_auto_fixes(comp)` **before** `comp.export_wav(...)`. If you
forget, the master chain alone won't catch the stacking.

## Effects pitfalls (learned the hard way)

- **Reverb `decay` is clamped to 1.0** (May 2026 fix). Values > 4 used to
  amplify catastrophically. Don't remove the clamp.
  See `memory/aem_effects_reverb_bug.md`.
- **Noise + LPF cutoff > 1000 Hz = fritura.** When using filtered noise as
  a texture (whoosh, bell-harmonics, voice_pad harmonics), keep cutoff
  ≤ 800 Hz unless you have a specific reason. See `memory/pattern_noise_fritura.md`.
- **Never use `np.abs()` as an exciter / rectifier.** Use `tanh` or a soft
  saturation function. Documented above.
- **Distortion stacks.** `distort` on a track plus `distort` in master
  multiplies the harmonic load. Pick one stage.

## Conventions

- `SR = 22050` Hz module-level constant. All durations are seconds,
  converted via `int(seconds * SR)` or `core.t_arr(...)`.
- All track audio is `float64 numpy arrays`, mono. Stereo is computed
  exactly once in `Composition.render_stereo()` via equal-power panning.
- Determinism: most functions are deterministic. `noise()` and `hihat()`
  use `np.random.randn` — fix the seed with `np.random.seed(...)` at the
  top of a compose file if you need reproducibility.
- The fluent style `.add(...).fx(...).fx(...)` is supported. Use it.

## Performance notes

Render is in-memory, no streaming. Worst case for Heliopause-class tracks:
8 min × 22050 Hz × ~14 tracks × float64 ≈ 200 MB peak. Fine on dev laptops.
If you push past that (multi-section assemblies, 22050 → 44100, more
tracks) you'll need to rethink — the framework is not streaming-aware.

## QA after every render

```bash
task render:outbound          # or whichever
task qa:spectral              # MANDATORY — catches inter-mods, stacks, peaks
task qa:perceptual            # optional, more expensive
task qa:voyager               # MANDATORY if you touched anything voyager-adjacent
```

`task qa:spectral` after every render is non-negotiable.
See `memory/feedback_qa_workflow.md`.

## When you change the framework

- If you change a primitive (e.g. `synth.sine`), ANY existing compose file
  may shift sound. Render `task render:all`, then `task qa:all`, then
  diff against the most recent finals in `transmissions/01/themes/*/finals/`.
- If you change `master.py`, the same applies — and you should explicitly
  flag the change to the user.
- New presets in `voyager_factory.py` are fine to add; don't replace existing ones.

## Things NOT to do here

- Don't add real-time audio (PortAudio, sounddevice). The framework is
  offline by design.
- Don't add a DSL layer over the Python API. The Python IS the DSL.
- Don't refactor the layer boundaries (synth → instruments → effects →
  master) without a strong reason. That layering is what keeps composition
  files readable.
- Don't introduce numpy-style global state (module-level random seeds,
  caches). Keep effects pure.
