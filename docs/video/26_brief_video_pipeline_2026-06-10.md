# Brief — Pipeline de videos Spiral Out / Heliopause

> Estado al 2026-06-10. Para handoff/ping-pong a otro modelo.

## 1 — Contexto del proyecto

- **Repo**: `/Users/emilianomettini/git/spiralout/`
- **Proyecto**: Spiral Out — sello/lab de música ambient con IA.
- **Artista**: ÆM (AI + Em).
- **Release activo**: **Transmission 01 / Heliopause** — 3 tracks musicales con
  3 videos asociados.
- **Estética visual**: campos verde-oscuro tipo Turrell, gradientes lentos
  (Skyspace / Aten Reign / Ganzfeld), elementos arquitectónicos (óvulo,
  túnel, bloom, partida), no figurativo.
- **Destino final**: YouTube 4K SDR (no HDR — testeado y descartado, ver §5).

## 2 — Los 3 videos y su ubicación

Carpeta base: `transmissions/01/video/`

| # | Track     | Duración | Render script                  | Master path                          |
|---|-----------|----------|--------------------------------|--------------------------------------|
| 1 | Outbound  | 8:00     | `outbound/render.py`           | `out/1-outbound.mp4` (=v11 baseline) |
| 2 | Crossing  | 13:00    | `crossing/render.py`           | `out/2-crossing.mp4`                 |
| 3 | Recursion | 3:00     | `recursion/render.py`          | `out/3-recursion.mp4`                |

YT trims (clipped a 7:59.36 / 12:59.36 / 2:59.36):
- `out/1-outbound_yt.mp4`
- `out/2-crossing_yt.mp4`
- `out/3-recursion_yt.mp4`

Pipeline render: **shader GLSL** (moderngl) → frames raw rgb48le → **ffmpeg HEVC
main10 10-bit BT.709 SDR**. No hay editor visual intermedio.

## 3 — Status actual por video

### Crossing
- **Detector YT emulado: 0.05% avg, 0.83% max — PASA**.
- Verdict técnico: **subible como está**.
- No requiere intervención adicional.

### Recursion
- 12fps source convertido a 24fps via ffmpeg `minterpolate` (mci, aobmc).
- Detector: limpio.
- Verdict: **subible**.
- Caveat: no validado visualmente en TV física (stutter de TV theoretically
  resuelto pero sin confirmación).

### Outbound — **EN PROCESO, ISSUE PERSISTENTE**
- Detector YT emulado v15 (último): avg 0.0%, max 2.0% — CLEAN ✓ según
  detector.
- **PERO** el user reporta que **sigue viendo banding/macroblocking
  visualmente entre 4:20 y 5:00** (zona del "bloom"), incluso después de
  todas las técnicas aplicadas.
- Test actual: `/tmp/outbound_720_grain.mp4` (720p) con grain shader v15
  adaptativo. Detector dice CLEAN, user dice banding visible.
- **Disconnect detector ↔ percepción humana sin resolver.**

## 4 — Qué consideramos un video "PRO"

Quality target inegociable según el user: **upload a YouTube SIN BANDING NI
MACROBLOCKING visible en ningún frame**.

Threshold cuantitativo (de `25_pipeline_bible.md`):
- Detector banding YT-emulado: `< 0.5% banded` en todos los frames.

Visual:
- Sin bloques cuadrados de 16×16 en zonas planas.
- Sin escalones visibles en gradientes lentos.
- Grain perceptible solo como "atmósfera", no como "ruido TV".

## 5 — Issues encontrados (cronológicos)

### Issue 1: HDR HLG castigado por YouTube SDR fallback
- HLG upload → YouTube serve VP9 8-bit fallback → banding catastrófico.
- **Fix aplicado**: encode SDR BT.709 directo, descartar HDR.

### Issue 2: Bug crítico hash21 GLSL — pérdida de precisión float32
- En `outbound/render.py` `finalize()`, `hash21` recibía `u_seed > 300000`
  → mult * 443 = 1e8 → fract(garbage) → dither efectivo al ~5% del intentado.
- Era el **root cause histórico** de todo el banding inicial.
- **Fix aplicado** (v10): `float s = fract(u_seed * 0.000312345);` mantiene
  el seed en rango precisado.

### Issue 3: Scene jumps a 0:03 y 6:39 reportados por user
- Resultaron ser artefactos del bug hash21. Una vez fixed → desaparecieron.

### Issue 4: ovulo pulse demasiado fuerte a 0:09
- Removido continuous `rms_sub`, solo eventos discretos.

### Issue 5: gradfun + noise ffmpeg post-shader empeoraban
- Agregar grain DESPUÉS del shader (en `ffmpeg -vf`) competía con el dither
  del shader. Eliminado en v15.

### Issue 6 (ACTUAL): Banding/macroblocking persistente en zona del bloom 4:20-5:00
- Detector matemático dice CLEAN.
- User reporta visualmente que **el banding sigue** en esa zona.
- 4 estrategias post-render con ffmpeg fallaron anoche (overlay grain plate
  iter 1-2, noise filter iter 3-4 — todos peores que baseline).
- Shader-level grain v13 (amp 5/255 fijo) → fix matemático pero grid pattern
  visible.
- Shader-level grain v14 (rotación temporal + amp 3/255) → detector clean,
  pero ya en este punto el user dijo que veía banding 4:20-5:00.
- Shader-level grain v15 (adaptativo por luminancia 2.5-7/255 + rotación) →
  detector clean, user **SIGUE VIENDO BANDING**.
- **Disconnect entre detector y vista humana sin resolver.**

## 6 — Técnicas y tools aplicadas

### Tools propios construidos
- `transmissions/01/video/youtube_emulate.sh` — emula localmente VP9 8-bit
  20Mbps BT.709 (SDR fallback de YouTube) sin necesidad de upload.
- `transmissions/01/video/banding_detect.py` — detector programático con
  run-length signature en patches 128×128 + transitions filter. v10
  validado con test bench sintético.

### Stack PRO aplicado al render (`outbound/render.py` v15)

| Técnica | Detalle | Status |
|---|---|---|
| Shader-level film-grain estructural | `grain_luma()` FBM 2-octavas, rotación temporal 6Hz, **adaptativo por luminancia** (2.5 → 7/255 según luma). SOLO LUMA (no chroma). | ✅ aplicado v15 |
| Bug hash21 precision fix | `fract(u_seed * 0.000312345)` | ✅ aplicado v10 |
| HEVC main10 10-bit pix_fmt yuv420p10le | x265 main10 profile | ✅ aplicado |
| SDR BT.709 directo | sin HDR HLG | ✅ aplicado |
| Bitrate 100 Mbps VBR | techo YouTube 4K (era 80 antes) | ✅ aplicado v15 |
| `psy-rd=2.5 aq-strength=1.0` | x265 fine-tune | ✅ aplicado v15 |
| Dither hash multi-componente 16/255 | post-grain, rotaciones de coords | ✅ ya estaba |
| Gamma lift 0.78 | brightness SDR | ✅ ya estaba |

### Stack PRO pendiente (planeado para 4K final)

| Técnica | Por qué | Status |
|---|---|---|
| AV1 SVT con `--svtav1-params film-grain=10:film-grain-denoise=1` | encode alternativo, grain synthesis al decode | ⚠️ script listo en `/tmp/encode_av1.sh`, sin correr aún |
| f3kdb deband VapourSynth | segunda capa anti-banding | ❌ plugin no instalado, compile ~1h |

### Stack rechazado / no aplicado y por qué
- **OCIO color management**: nuestro pipeline es single-color-space (shader
  Rec.709 → output Rec.709 SDR). OCIO sirve para multi-space (S-Log →
  grading → Rec.709 → HDR P3). No aporta al caso.
- **DaVinci Resolve Studio Film Grain**: requiere license $299, rechazado
  por user.
- **VapourSynth f3kdb deband**: plugin no disponible vía brew, requiere
  compile.
- **gradfun + noise ffmpeg filters post-shader**: empeoraron en todos los
  tests (competían con grain del shader).

## 7 — El problema vivo ahora

**Detector dice CLEAN. User dice banding visible en 4:20-5:00.**

Posibles causas a investigar (no descartadas):
1. **Display del user vs emulator local**: monitor del user puede tener
   pipeline 8-bit con menos dither que el VP9 emulator, mostrando bandas
   que el detector no captura.
2. **Banding temporal entre frames**: el detector analiza frame-por-frame,
   no inter-frame. Si la rotación temporal del grain v15 (cada 6Hz, ti steps)
   produce "saltos" perceptibles entre frames adyacentes, el user los
   vería como banding aunque cada frame individual sea clean.
3. **Grain adaptativo insuficiente en gradiente medio**: la fórmula
   `mix(2.5, 7.0, smoothstep(0.05, 0.6, luma))` puede dejar gap en luma
   media (0.2-0.5) donde la banda del halo del bloom vive.
4. **Bloque YUV 16×16 que el detector ignora**: detector trabaja en patches
   128×128, podría missar artefactos sub-resolución.

## 8 — Próximos pasos sugeridos

1. **Investigar disconnect detector ↔ percepción**: extraer SECUENCIA de
   frames (no solo stills) de 4:20-5:00 en v15 y revisar inter-frame
   stability del grain.
2. **Test específico**: re-render bloom-segment-only (60s) con varias
   variantes de adaptativo (curva diferente, smoothstep distinto) sin
   tocar el resto del video.
3. **Pedir al user**: screenshot del display actual + descripción precisa
   (¿bandas verticales? ¿horizontales? ¿pulsan? ¿se mueven con la cámara?).
4. **Considerar**: ¿el "banding" que reporta es realmente banding o es la
   propia naturaleza del shader (radial bloom rings)? Comparar v11 vs v15
   en mismo frame.

## 9 — Archivos clave para inspección

- `transmissions/01/video/outbound/render.py` — el render del que sigue
  el issue. Buscar función `grain_luma` y `finalize` (líneas ~270-380).
- `transmissions/01/video/youtube_emulate.sh` — emulator.
- `transmissions/01/video/banding_detect.py` — detector v10.
- `docs/video/25_pipeline_bible.md` — biblia del pipeline (target,
  arquitectura, antipatterns).
- `docs/video/_iteration_logs/checkpoint_2026-06-08.md` — checkpoint
  histórico.
- `docs/video/_iteration_logs/iter_results_2026-06-09.md` — log de las 4
  iteraciones ffmpeg que fallaron.
- `/tmp/outbound_720_grain.mp4` — último render 720p v15 actual (5.6 GB).

## 10 — Preguntas abiertas para Fable

1. ¿Por qué el detector da CLEAN y el user reporta banding visual? ¿Cómo
   reconciliar?
2. ¿Hay tecnica de grain temporalmente más smooth que rotación discreta cada
   6 Hz?
3. ¿Conviene cambiar a grain Worley/cellular en vez de FBM value-noise para
   atacar mejor el halo radial del bloom?
4. Si todo lo demás falla: ¿vale la pena bypassear YouTube SDR fallback con
   premium hack (subir a 8K virtualmente)?

## 11 — Documentación de referencia (para profundizar)

### Pipeline técnico de video (críticos para este issue)

- [`docs/video/25_pipeline_bible.md`](25_pipeline_bible.md) — **LA BIBLIA**.
  Quality targets, arquitectura, técnicas, antipatrones, tuning guide.
  **Leer primero.**
- [`docs/video/24_pro_pipeline.md`](24_pro_pipeline.md) — Pipeline pro
  híbrido Python + DaVinci Resolve adoptado 2026-06-08. Explica por qué
  cambiamos del DIY pipe directo.
- [`docs/video/22_banding_detection_validation.md`](22_banding_detection_validation.md)
  — Documentación del detector y validation pipeline.
- [`docs/video/21_distribution_encoding.md`](21_distribution_encoding.md) —
  Encoding config para distribución (codecs, bitrates, color spaces).
- [`docs/video/20_technical_reference_videos.md`](20_technical_reference_videos.md)
  — Referencia técnica general.
- [`docs/video/PRO_vs_amateur.md`](PRO_vs_amateur.md) — Diferencia entre
  approach amateur y PRO.
- [`docs/video/QA_pro_rubric.md`](QA_pro_rubric.md) — Rúbrica QA PRO.

### Iteration logs (historial reciente del issue)

- [`docs/video/_iteration_logs/checkpoint_2026-06-08.md`](_iteration_logs/checkpoint_2026-06-08.md)
  — Checkpoint pre-noche.
- [`docs/video/_iteration_logs/iter_results_2026-06-09.md`](_iteration_logs/iter_results_2026-06-09.md)
  — **Las 4 iteraciones ffmpeg fallidas anoche**. Crítico para no repetir.
- [`docs/video/_iteration_logs/23_iteration_log_2026-06-08.md`](_iteration_logs/23_iteration_log_2026-06-08.md)
  — Log iteración previo.

### Per-track documentación

- [`transmissions/01/video/README.md`](../../transmissions/01/video/README.md)
  — Overview de los 3 videos.
- [`transmissions/01/video/CONTEXT_VIDEO_PROJECT.md`](../../transmissions/01/video/CONTEXT_VIDEO_PROJECT.md)
  — Contexto del proyecto video.
- [`transmissions/01/video/outbound/README.md`](../../transmissions/01/video/outbound/README.md)
  — Outbound specifico.
- [`transmissions/01/video/outbound/notes.md`](../../transmissions/01/video/notes.md)
  — Notas técnicas outbound.
- [`docs/video/11_CROSSING_production_spec.md`](11_CROSSING_production_spec.md)
  — Production spec de Crossing.
- [`docs/video/13_crossing_storyboard.md`](13_crossing_storyboard.md) —
  Storyboard de Crossing.
- [`docs/video/14_transition_techniques.md`](14_transition_techniques.md) —
  Técnicas de transición (relevante para concept multimedia).

### Concept y visión

- [`docs/video/01_concept_python_shader.md`](01_concept_python_shader.md) —
  El concept del shader Python (relevante a outbound).
- [`docs/video/05_visual_research_references.md`](05_visual_research_references.md)
  — Referencias visuales investigadas.
- [`docs/video/07_video_stack_per_track.md`](07_video_stack_per_track.md) —
  Stack visual por track.
- [`docs/video/09_ai_video_models_2026.md`](09_ai_video_models_2026.md) —
  Knowledge base AI video models (SDXL, Veo 3, Sora 2, etc.).
- [`docs/video/02_concept_hydra.md`](02_concept_hydra.md),
  [`03_concept_ai_opensource.md`](03_concept_ai_opensource.md),
  [`04_concept_2001_stargate.md`](04_concept_2001_stargate.md) — alternative
  concepts explorados.

### Project context (umbrella Spiral Out)

- [`/Users/emilianomettini/git/spiralout/CLAUDE.md`](../../CLAUDE.md) —
  **Instrucciones del repo entero**. Explica nombre del proyecto, ÆM,
  Heliopause, voyager protegido, antipatterns de audio.
- [`docs/00_concepto.md`](../00_concepto.md) — Concepto general del
  proyecto.
- [`docs/05_brief.md`](../05_brief.md) — Brief original.
- [`docs/07_vision.md`](../07_vision.md) — Vision document.
- [`docs/13_visual_style_guide.md`](../13_visual_style_guide.md) — Style
  guide visual del proyecto.
- [`docs/14_design_system.md`](../14_design_system.md) — Design system.
- [`docs/12_release_pipeline.md`](../12_release_pipeline.md) — Release
  pipeline general.

### Memory persistente (cross-session, auto-recuerdos)

- [`memory/MEMORY.md`](../../memory/MEMORY.md) — Index de auto-memory.
  Relevantes a este issue:
  - `feedback_qa_yourself_before_showing.md` — antes de mostrar asset,
    validar source.
  - `feedback_qa_workflow.md` — workflow QA spectral pre-aviso.
  - `feedback_no_rabbit_holes_use_my_vision.md` — decir "no se puede"
    antes que encadenar PoCs.
  - `feedback_stills_before_animation.md` — clavar still antes de animar.

### Tools/scripts ejecutables (con path absoluto)

- `transmissions/01/video/youtube_emulate.sh <in> <out>` — Emula VP9 8-bit
  YouTube SDR fallback localmente.
- `transmissions/01/video/banding_detect.py <video>` — Detector banding.
  Activate `.venv_detect/bin/python` para correrlo. `--test` para validar.
- `transmissions/01/video/outbound/render.py` — Render outbound (`--width`,
  `--height`, `--out`, `--pretest`, `--no-audio`).
- `/tmp/encode_av1.sh <in> <out>` — Encode AV1 SVT con film-grain syntesis
  (script pendiente correr).
- `Taskfile.yml` (en repo root) — comandos top-level (`task --list` para
  ver todos).

### CLAUDE.md por subdirectorio

- [`/Users/emilianomettini/git/spiralout/CLAUDE.md`](../../CLAUDE.md) —
  repo umbrella.
- [`transmissions/CLAUDE.md`](../../transmissions/CLAUDE.md) — convenciones
  de releases / transmissions.
- [`site/CLAUDE.md`](../../site/CLAUDE.md) — convenciones del site (no
  crítico para video).
- [`framework/CLAUDE.md`](../../framework/CLAUDE.md) — convenciones del
  framework de audio (no crítico para video).
