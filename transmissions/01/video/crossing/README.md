# Crossing — posta

13 minutos. Tránsito a través de la heliopausa. Single fragment shader.

**Master final**: `../out/2-crossing.mp4` (copia de `final_4k.mp4`).

## Files

- `render.py` — shader completo (campo + silueta + phases + bells + voyager)
- `final_4k.mp4` — última render exitosa
- `.venv` → symlink al venv compartido

## Regenerar

```bash
./.venv/bin/python render.py             # full 4K (50-60 min)
./.venv/bin/python render.py --pretest   # contact sheet + still 4K (1 min)
```

## Audio source

`../../release/masters/02_crossing_master.wav`

## Control track

`../control/crossing.npz`

## Referencia técnica

`../../../../docs/video/20_technical_reference_videos.md` — sección 2
