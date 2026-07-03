# Outbound — posta

8 minutos. Despegue / journey al espacio. 6-7 escenas raymarched 3D.

**Master final**: `../out/1-outbound.mp4` (copia de `final_4k.mp4` de este dir).

## Files

- `render.py` — pipeline completo (shaders + scenes + ffmpeg stream)
- `final_4k.mp4` — última render exitosa (idéntica a `../out/1-outbound.mp4`)
- `notes.md` — log de cambios por versión
- `.venv` → symlink al venv compartido del proyecto

## Regenerar

```bash
./.venv/bin/python render.py
```

Output va a `final_4k.mp4`. Si lo apruebas, copiarlo a `../out/1-outbound.mp4`.

## Audio source

`../../release/masters/01_outbound_master.wav`

## Control track

`../control/outbound.npz`

## Referencia técnica

`../../../../docs/video/20_technical_reference_videos.md` — sección 1
