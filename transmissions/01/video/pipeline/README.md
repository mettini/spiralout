# Pipeline de los visualizers (scripts fuente)

Scripts con los que se generaron los 3 visualizers de Heliopause (ver
`docs/video/27_lessons_patterns.md` y `release/youtube_published.md`).

- `outbound/` — óvulo (Blender GPU) + túnel numpy + humo/afuera (Blender vol) +
  compositores (estelas, flor/dismantle, mandala/kaleido) + ensamble + 4K.
- `crossing/` — humo (Blender) + sombra difusa (post) + **Kaliset** (delirio
  full-screen) + `crossing_master_final.py` (compositor) + 60fps + 4K.
- `bl_common.py` — helpers Blender compartidos.
- Sync: `../control/*.npz` (rms/flux/onset por track).

⚠️ **Paths hardcodeados** a `~/outbound_work` / `~/crossing_work` (los work dirs
se borraron por espacio). Para re-correr hay que ajustar rutas + regenerar
frames. Los outputs pesados (mp4/frames) NO se versionan (regenerables).
Lección clave: renderizar a **60fps** (no 24) — ver doc 27.
