# transmissions/ — releases

Each directory `NN/` is one **transmission** (EP / album). `01/` is
**Heliopause / Transmission 01** (ÆM), currently in late mastering / pre-release.

## Why "transmissions" and not "releases"

It's the brand: each release is framed as a transmission from the
threshold. The numbering is global and monotonic — `01/`, `02/`, … —
regardless of artist. New artist on the label = new transmission number,
not a new top-level folder.

## Active transmission

The Taskfile uses `TX` as the active transmission var (default `01`).
Switch with:

```bash
TX=02 task render:all
TX=01 task qa:all
```

Tasks resolve to `transmissions/{{.TX}}/...`. If you forget to set `TX`,
you're operating on `01`.

## Layout (one transmission)

```
transmissions/NN/
├── README.md             ← what this transmission is
├── PLAN.md               ← what's pending (the user reviews this)
├── themes/               ← one folder per track
│   ├── <track>/
│   │   ├── arrangement_full.md         storyboard for the full track
│   │   ├── compose_full.py             renders the full track
│   │   ├── prototypes/                 60-90s sketches (v0, v1, v2…)
│   │   │   ├── arrangement_v0.md
│   │   │   └── compose_v0.py
│   │   └── finals/                     approved versions (versioned snapshots)
│   │       └── v1/
│   │           ├── master.wav          ← gitignored (heavy)
│   │           ├── stems/              ← gitignored (heavy)
│   │           ├── compose_snapshot.py ← versioned (small, source of truth)
│   │           └── version.md          ← versioned (decisions, audible diffs)
│   ├── maquetas/                       legacy 30s prototypes per genre
│   └── _archive/                       deprecated approaches kept for reference
├── out/                  ← scratch renders (gitignored, regenerable)
│   ├── index.json        ← player UI manifest (committed)
│   └── <track>/
│       ├── master/<comp_id>.wav
│       └── stems/<comp_id>/<track>.wav + manifest.json
├── samples/              ← reference / Voyager Golden Record / CMB (gitignored)
├── artwork/              ← cover art + design system
│   ├── cover_master_3000.png        master PNG (heavy, backup)
│   ├── cover_streaming_3000.jpg     3000x3000 sRGB JPG for FLAC/MP3 metadata
│   ├── cover_1500.jpg               1500x1500 lighter backup
│   ├── banners/                     Bandcamp / social banners
│   ├── generated/                   AI-gen artwork iterations
│   ├── generation_briefs/           text briefs that fed the gen
│   └── hexagram/                    secondary mark / motif
└── release/             ← release-grade deliverables (gitignored, regenerable)
    ├── RELEASE_PLAN.md
    ├── masters/        ← final mastered WAVs
    ├── distribution/   ← {flac,mp3,wav_44k,aac} per platform
    ├── metadata_proposal.md
    ├── textos.md
    ├── lab/            ← parallel experiments (e.g. clear_experiment was merged → master v2)
    └── backups/
```

## What's gitignored vs versioned

The `.gitignore` policy here is deliberate. **Versioned:**

- All `compose_*.py` and `arrangement_*.md` (the source).
- `out/<track>/index.json` (small, manifests the player needs).
- `finals/v*/version.md` and `finals/v*/compose_snapshot.py` (trace of
  approved versions — small).
- `artwork/` (the artwork is part of the deliverable, the JPG/PNGs go in).
- `README.md`, `PLAN.md`, `RELEASE_PLAN.md`, `metadata_proposal.md`,
  `textos.md`.

**Gitignored** (regenerable from compose + render pipeline):

- All scratch master/stems WAVs (`out/*/master/`, `out/*/stems/`).
- Final master WAVs and stems (`finals/v*/master.wav`, `finals/v*/stems/`).
- `release/` entirely (masters, distribution bundles, lab, backups).
- `samples/raw/`, `samples/voyager_golden_record/`, `samples/cmb_recordings/`.

If you're tempted to commit a WAV: don't. Render it instead.

## Compose workflow (per track)

1. Edit `compose_full.py` (or a prototype).
2. `task render:<track>` or `task render:<track>:v0`.
3. **`task qa:spectral`** — mandatory before claiming "done". Static code
   QA is not enough — there are issues you only see in the FFT.
4. Open the player (`task serve`) and listen. Solo each track to verify.
5. Iterate.

For the Voyager-bearing tracks, also `task qa:voyager` (regression against
the validated benchmark). Treat any drift as a release blocker.

## Promoting a prototype to final

When a `v1`/`v2`/etc. is approved by the user:

1. Render the version, copy the master + stems to `themes/<track>/finals/vN/`.
2. Drop in `compose_snapshot.py` (an immutable copy of the compose used).
3. Write a short `version.md` — what changed vs prior, audible diffs, what
   the user said.
4. Reference it from this transmission's `README.md`.

The stems + master are gitignored at the finals level (heavy), but the
snapshot + notes are not — trace of evolution survives.

## Mastering → release pipeline

End-to-end (see `docs/12_release_pipeline.md` for the full doc):

```
compose → render → mix (per-track FX + auto_fixes + master chain v2)
       → mastering chain → EP assembly (concat + crossfades)
       → export to release formats (WAV 44.1/24, FLAC, MP3 320, AAC)
       → embed metadata + artwork (mutagen)
       → distribute (DistroKid / CD Baby / Bandcamp)
```

Tasks:

```bash
task master:bounce            # bounce one track to mastered WAV
task master:bounce:all        # all tracks
task ep:assemble              # concat + crossfades → continuous EP master
task export:formats           # WAV/FLAC/MP3/AAC per-track
task export:formats:full      # same + continuous EP master
task tag                      # embed metadata + artwork (WIP)
task release:check            # validate LUFS / true peak / stereo correlation
task release:bundle           # full pipeline orchestration (WIP)
task release:plan             # status of where each track is
```

The release skill (`aem-release`) has the chain spec, LUFS targets for 2026
streaming, anti-patterns (over-compression, WAV-artwork-embed pitfalls),
and aggregator comparison. Invoke it when working on anything past the
mix stage.

## Voyager regression

```bash
task qa:voyager
```

Renders the voyager benchmark and diffs against the validated reference.
**Run this any time you touch:**

- Anything in `framework/aem/voyager_factory.py`.
- Voyager-adjacent code (`motifs.py`, the `voyager_safe*` wrappers).
- Master chain (`master.py`) — voyager spectrum can shift indirectly.

If the diff isn't clean, do not promote a version.

## Concept of "lab" inside release/

`release/lab/` is where parallel experiments live (e.g. the May 2026
`clear_experiment/` that became master chain v2 + auto_fixes). Pattern:

1. Copy current pipeline state to a new `lab/<experiment>/` folder.
2. Iterate freely without breaking main.
3. When approved by user, *merge upstream*: move the deltas into the
   framework + main compose files, then collapse the lab folder.
4. Leave a memory entry (`memory/<experiment>_merge_<YYYY-MM-DD>.md`)
   noting what got promoted.

Don't leave lab branches half-merged. They're confusing six months later.

## Where the cover lives

- `artwork/cover_master_3000.png` — master backup, 8 MB.
- `artwork/cover_streaming_3000.jpg` — 3000x3000 sRGB JPG, the one embedded
  in FLAC/MP3 metadata and uploaded to aggregators.
- `artwork/cover_1500.jpg` — 1500x1500, used by the site share-image
  generator and the Bandcamp page preview.

The site (`site/spiralout/aem/`) symlinks/copies its own `cover.jpg` —
don't repoint to the 3000x3000 (the page payload would be ~2 MB for no
reason).

## Adding a new transmission

```bash
mkdir transmissions/02
# copy 01/README.md skeleton, blank it out
# create themes/, artwork/, release/ scaffolds (empty)
TX=02 task render:all   # will fail until compose files exist — expected
```

Future transmissions don't have to use the same track count or duration
shape. The framework is per-track agnostic; the Taskfile renders whatever
`themes/<name>/compose_full.py` exists.

## Things NOT to do

- Don't commit WAVs. Even small ones. The pipeline is reproducible.
- Don't bypass `apply_auto_fixes(comp)` in a compose file. If you have a
  reason, leave a comment.
- Don't skip `task qa:spectral` before reporting work. It's the difference
  between "the code ran" and "the audio is OK".
- Don't promote a final without rendering `task qa:voyager` clean (when
  voyager-adjacent).
- Don't rename a `<track>/` folder without updating the player index and
  the Taskfile aliases — multiple things resolve by folder name.
