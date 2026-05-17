---
name: dark-ambient-sound-design
description: "Sound design principles for Lustmord/Blackstar-style dark ambient — clean, vast, immense without sounding 'underwater'. Triggers on: 'dark ambient', 'lustmord', 'ambient', 'abajo del agua', 'tapado', 'underwater', 'sumergido', 'oscuro pero limpio', 'inmenso', 'inmensidad', 'goetia', 'blackstar', 'dark drone', 'space ambient', 'sounds muffled', 'falta aire', 'falta brillo', 'sounds dull', 'no se escucha claro'. Use when composing or mixing dark ambient music to ensure the mix sounds vast and clean rather than muffled or 'underwater'."
---

# Dark Ambient Sound Design — Lustmord/Blackstar style

Reference albums:
- **Lustmord** — *Goetia*, *The Place Where the Black Stars Hang*, *Carbon-Based Lifeforms*
- **David Bowie** — *Blackstar* (specifically the title track + "Lazarus")
- **Brian Eno** — *Apollo: Atmospheres and Soundtracks*
- **Tim Hecker** — *Ravedeath, 1972*

These tracks share a perceptual signature: **"vast empty space + clean sound"**. The listener feels immersed in a giant cathedral but every detail is crisp. The opposite of the common dark ambient mistake: muffled, "underwater" sound that suggests darkness but lacks air.

---

## The 5 Principles (apply ALL together)

### 1. Air shelf — aggressive high boost
**Where:** +6 dB high-shelf at 8 kHz (not 4 kHz).
**Why:** "Air" lives in 8-12 kHz, not in mid-treble. Boost at 4 kHz gets bright/aggressive without giving space. 8 kHz+ adds "transparency" and the sense of room without harshness.
**How (master chain):**
```python
from scipy.signal import iirfilter, sosfilt
def air_boost(audio, gain_db=6.0, freq=8000.0, sr=44100):
    sos = iirfilter(2, freq / (sr/2), btype='highpass', ftype='butter', output='sos')
    boost = sosfilt(sos, audio, axis=0)
    return audio + boost * (10 ** (gain_db / 20) - 1.0)
```

### 2. Mid scoop — kill the mud
**Where:** -2 dB peak/notch at 300 Hz, Q 0.7.
**Why:** Drones, chants and pads in 100-200 Hz easily accumulate "mud" in 200-400 Hz that masks everything else. Light cut keeps body, removes sludge.
**How:**
```python
from scipy.signal import iirpeak, sosfilt, tf2sos
def mid_scoop(audio, gain_db=-2.0, freq=300.0, q=0.7, sr=44100):
    b, a = iirpeak(freq / (sr/2), q)
    sos = tf2sos(b, a)
    notch = sosfilt(sos, audio, axis=0)
    return audio + notch * (10 ** (gain_db / 20) - 1.0)
```

### 3. M/S width — stereo immensity
**Where:** Boost Side channel × 1.25 (~+2 dB) in master chain.
**Why:** Standard L/R panning sounds "in front of you". Boosting the Side via Mid/Side encoding gives the sensation of "around you" — that vastness Lustmord is known for. Don't over-do it (>1.4 destroys mono compatibility).
**How:**
```python
def ms_width(audio, side_gain=1.25):
    L, R = audio[:, 0], audio[:, 1]
    M = (L + R) * 0.5
    S = (L - R) * 0.5 * side_gain
    out = np.empty_like(audio)
    out[:, 0] = M + S
    out[:, 1] = M - S
    return out
```

### 4. Open LPFs on stems — stop over-filtering
**Common mistake:** Cutting LPF at 1500 Hz on every stem to "avoid harshness". Result: nothing has overtones above 1.5 kHz → "underwater" feeling that no master chain can rescue.
**Fix:**
- Drones (sub-bass, mid drones): LPF **1800 Hz** (was 1300-1400)
- Chants/pads/vocal-ish: LPF **2400 Hz** (was 1800)
- Bells/pings/mellotron: LPF **2000 Hz** (was 1500)
- Walls of sound: LPF **2000 Hz** (was 1500)
- Sub-bass kicks (sub 100Hz): LPF **180-220 Hz** OK to keep

If you get "fritura" (harsh harmonics) at higher LPFs, use **notch_eq** at the specific problem frequency (e.g. A5/A6 at 880/1760 Hz in Fletcher-Munson zone) instead of bringing the whole LPF down.

### 5. Reverb mix — less wet, more pre-delay
**Common mistake:** Reverb mix 0.65-0.70 on every wet element. Result: "swamp of reverb" — fonts get drowned in their own tail.
**Fix:**
- Default reverb mix: **0.50** (was 0.65)
- Long-tail reverbs (decay > 6s): mix **0.55** max
- Use **pre_delay 80-150ms** on long reverbs — separates source from tail, prevents "submerged" feeling
- Consider reverb-as-send, not reverb-as-insert when stems pile up

---

## Diagnosis: "abajo del agua / underwater / muffled"

When user reports the mix sounds tapado/muffled/underwater, check in this order:

1. **LPF cutoffs across stems** — grep `lpf(a, [0-9]+)`. If most are < 2000 Hz, that's the cause. Apply principle 4.
2. **Reverb mix levels** — grep `mix=0\.[5-9]`. If many are > 0.55, apply principle 5.
3. **Master chain air boost** — if currently at 4 kHz or +2.5 dB, upgrade to 8 kHz +6 dB (principle 1).
4. **Mid scoop missing** — verify principle 2 is applied.
5. **No M/S width** — verify principle 3 is applied.

Ideal master chain structure:
```
HPF (25 Hz) → Mid scoop (-2 dB @ 300 Hz) → Air shelf (+6 dB @ 8 kHz)
  → M/S width (×1.25) → Glue compression (tanh 0.15)
  → Soft limiter (-1 dBFS) → LUFS normalize (-16 or -14)
```

---

---

## Structural Anti-patterns (the "muffled/dirty even without master" problem)

If the user reports the mix sounds muffled, dirty, or "underwater" **even with the master chain bypassed**, the problem is structural — not in the master. Apply these in order:

### Anti-pattern 1: Low-end Stack
**Symptom:** Many stems competing in <300 Hz range — drones at 100-200Hz + chants at 70-110Hz + bass + sub + kicks + pads + voices_pad. Even at low individual gain, mutual masking creates a "gray mud" that no EQ on the master can rescue.

**Detection:** Count stems active simultaneously with energy <300 Hz. If > 4-5 are overlapping in time, you have a stack.

**Fix:** HPF at the lowest *useful* frequency for each non-sub stem:
- Chants/vocal-ish (fundamental 70-110 Hz): HPF at fundamental − 5-10 Hz (e.g. D2=73Hz → HPF 65, A2=110Hz → HPF 90, F2=87Hz → HPF 75)
- Pads/swells/voices: HPF **180-200 Hz** (no useful info below)
- Bells/pings: HPF **300 Hz** (bells live in 500Hz+)
- Mid-drones (Dm/Bb cluster): HPF **100 Hz** (sub-drone separate)
- Wind/whoosh/ambient FX: HPF **100-150 Hz**
- Field atmosphere (lpf < 500 Hz): leave OR HPF 60 Hz to clean inaudible sub

**Result:** Sub <100 Hz becomes exclusive territory of sub_rumble/bass/kicks. Mids 100-300 Hz exclusive of true low-mid drones. Everything above can breathe.

### Anti-pattern 2: Reverb Tail Accumulation
**Symptom:** Even at reverb mix 0.50, when 6-8 stems with decay 5-8s play simultaneously, their parallel tails sum into a constant "gray cloud". Each stem may sound clean in solo, but together they smear.

**Detection:** Count stems with `reverb(decay >= 5)` active simultaneously. If > 4, accumulation is likely.

**Fix:** Add `pre_delay_ms` to long reverbs to separate source from tail:
- Decay 5-6s → `pre_delay_ms=80`
- Decay 6-7s → `pre_delay_ms=100`
- Decay 7-8s+ → `pre_delay_ms=120`
- Bells with long decay (>6s): always `pre_delay_ms=100-120` (extreme separation needed)

The pre-delay creates a clean attack window where the source plays "dry" before the tail engulfs it. Sounds more "Lustmord cathedral" (source then echo) and less "submerged" (source mixed with own immediate cloud).

**More aggressive fix (refactor):** Move reverb from per-stem inserts to 1-2 shared send buses. Each stem sends % to bus, bus does the verb. The shared bus creates ONE coherent room instead of 8 different rooms layered.

### Anti-pattern 3: Continuous Density (no breath)
**Symptom:** > 5 stems always active. The mix has no "moments of breath" where the mind can rest. Perceived as exhausting/dirty even if technically clean.

**Detection:** Plot the activity timeline. If there's never a moment with < 4 active stems, density is the issue.

**Fix:** Use `amp_envelope` to duck non-protagonist elements during prominent moments. E.g. when a voyager event plays, duck cosmos/sub/drones to 30% for the 5-10s the voyager is the focus. Creates "spotlight" effect.

```python
# Example: duck cosmos during chant section 215-415s
cosmos.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (200, 1.0), (215, 0.5), (415, 0.5), (430, 1.0), (DURATION, 1.0),
]))
```

### Anti-pattern 4: Multiple Reverbs in Same "Room"
**Symptom:** All stems use the same reverb function with similar decay. Without algorithmic differentiation, all tails sound the same character → they fuse into one indistinct room.

**Fix:** Vary reverb params across stems — different decays (3s vs 6s vs 8s), different pre_delays (50ms vs 100ms vs 150ms), occasional plate vs hall. Even small variations help the ear separate elements.

### Anti-pattern 5: Mono Stems Panned (no real width)
**Symptom:** Stems are mono signals positioned via pan. The "stereo image" is just left/right balance, not real spatial width per stem.

**Fix:** For key elements, render as stereo from the start (slight detune L vs R, micro-delays, decorrelated noise mixed in). Or apply stereo widening (M/S processing) per-stem, not just at master.

---

## What NOT to do (preserves the "dark" character)

- **Don't push compression hard** — dark ambient breathes. Glue tanh 0.10-0.15 max.
- **Don't sidechain** — kills the floating quality.
- **Don't go above LUFS -14** — loud ≠ vast. -16 is the sweet spot for ambient.
- **Don't over-EQ low end** — sub 30-60 Hz should stay natural. Just HPF at 25 Hz to clean inaudible sub-sub.
- **Don't add stereo chorus or detune at master** — already detuned at stem level.
- **Don't use saturation/distortion at master** — only the gentle glue tanh.

---

## Backup before applying

Before making global changes (master chain or many stems), backup:
```
cp transmissions/<id>/release/masters/*.wav transmissions/<id>/release/backups/<date>_pre-change/masters/
cp framework/aem/master.py transmissions/<id>/release/backups/<date>_pre-change/code/
```

So user can A/B compare and rollback if needed.
