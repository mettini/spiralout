# Spiral Out — repo umbrella

This repo is the **Spiral Out** project: an experimental sound lab exploring
the intersection of human composition and AI. It bundles **everything** under
one roof — not just an album.

> The repo is in the process of being renamed `spiral-out` (was `My First
> Album` originally). When you write paths in commit messages, docs or
> READMEs, treat "Spiral Out" as the project name.

## What's inside

| Subdir            | What it is                                                 | Owner |
|---|---|---|
| `site/spiralout/` | The public website (`spiralout.space`, Cloudflare Pages)   | [`site/CLAUDE.md`](site/CLAUDE.md) |
| `framework/`      | Python audio framework `aem` — pure-code composition       | [`framework/CLAUDE.md`](framework/CLAUDE.md) |
| `transmissions/`  | Releases. Each `NN/` is one "transmission" (EP/album)      | [`transmissions/CLAUDE.md`](transmissions/CLAUDE.md) |
| `player/`         | Local web debug player (Web Audio API, plain HTML/CSS/JS)  | — |
| `scripts/`        | Cross-cutting CLI utilities (QA, render, release, artwork) | — |
| `docs/`           | Concept / lore / brief / vision / design system docs       | — |

Each subdir has (or will have) its own `CLAUDE.md` with the rules of that
area. This file is the entry point.

## Names you'll see often

- **Spiral Out** — the lab / label / umbrella brand. Public face is `spiralout.space`.
- **ÆM** (AI + EM) — the first artist project on the label. The artist's
  collaborator-with-AI persona.
- **Heliopause / Transmission 01** — the first release. Three tracks:
  Outbound (8:00), Crossing (13:00), Recursion (3:00).
- **Voyager** — the recurring musical motif (a melodic line + signature FX)
  that threads through the album. **Protected by the user** — don't change
  voyager defaults without explicit approval and a `task qa:voyager` diff
  against the benchmark. See `memory/voyager_protegido.md`.
- **Transmission** — each release is called a transmission, numbered. Future
  releases live in `transmissions/02/`, `03/`, etc.

## How the user works

- Iterates with feedback loops: `task render:* → listen → adjust compose_*.py
  → re-render`. The player UI in `player/` is the listening surface.
- Cares about the **audio result**, not code purity for its own sake. Mix /
  mastering decisions need *audible* justification.
- Speaks Spanish in chat; the codebase is mostly Spanish in comments and
  docstrings. Match the existing tone.
- "menos opacity" / "más opacity" refers to the **subject of the photo**
  (image), not the literal CSS alpha — invert your intuition. See
  `memory/feedback_opacity_terminology.md`.

## Things that have bitten us (read before touching audio)

These are in memory but worth surfacing here too:

- **`np.abs()` as an exciter is a TRAP** — generates ~820 inter-modulations
  that sound like fritura. Use `tanh` instead. (`memory/abs_rectifier_exciter_antipattern.md`)
- **Noise filtered with cutoff > 1000 Hz sounds like fritura/static.** Bias
  high-cut to ≤ 800 Hz on noise-based textures. (`memory/pattern_noise_fritura.md`)
- **Muffled/tapado mixes** have four common causes: 1.5-3 kHz resonance,
  low-end stack, air shelf over nothing, glue too aggressive. Diagnose
  before reaching for EQ. (`memory/feedback_muffled_sound_diagnosis.md`)
- **`task qa:spectral` after EVERY render**, before reporting back to the
  user. Static code QA isn't enough. (`memory/feedback_qa_workflow.md`)
- **Reverb `decay` parameter is clamped to 1.0** since the May 2026 fix —
  values > 4 used to amplify catastrophically. (`memory/aem_effects_reverb_bug.md`)

## Top-level workflow

```bash
task --list                  # see everything
task install                 # python deps (numpy, scipy)
task install:release         # release deps (soundfile, pyloudnorm, mutagen, etc.)
task serve                   # local player at http://localhost:8765/player/
task render:all              # render the whole active transmission
task qa:all                  # spectral + perceptual + voyager regression
task release:plan            # status of the release pipeline
task site:dev                # local preview of spiralout.space
task site:deploy             # push site to Cloudflare Pages
```

`TX=02 task render:all` switches the active transmission for any render task.

## Skills the project uses

Project-local skills are in `.claude/skills/`:

- **`aem-composer`** — ambient/cinematic composition guidance (Eno, Roach,
  Stars of the Lid, Zimmer); trigger on composing/iterating tracks under
  `transmissions/*/themes/`.
- **`aem-release`** — mastering chain, LUFS targets 2026, metadata embedding
  (mutagen), distributor comparison; trigger when finishing tracks for
  release.

## Conventions across the whole repo

- Spanish in code comments / docstrings / variable docstrings.
- Python target: 3.10+ (see `Taskfile.yml` `PYTHON: python3.10`).
- Sample rate `SR = 22050` (mono per track, stereo emerges only on render).
- All rendered WAVs are git-ignored — they're reproducible from
  `compose_*.py`. Keep the `compose_*.py` snapshot small and committed.
- `.DS_Store` is in `.gitignore`; do not commit it.

## When in doubt

- Read the closest `CLAUDE.md` first (`site/`, `framework/`, `transmissions/`).
- Check `docs/10_plan.md` for the active execution plan.
- Check `transmissions/01/PLAN.md` for what's pending on the active release.
- Check `memory/MEMORY.md` for accumulated feedback.
