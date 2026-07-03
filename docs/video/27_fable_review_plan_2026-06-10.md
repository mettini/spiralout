# Review Fable + plan ejecutable — banding/oscuridad YouTube

> 2026-06-10. Review independiente del brief `26_brief_video_pipeline_2026-06-10.md`.
> Diagnóstico verificado empíricamente (no especulado). Plan ejecutable por
> cualquier modelo; cada fase tiene criterio de éxito medible.

## TL;DR

1. **El pipeline de color está BIEN** — verificado con encode sintético
   roundtrip: BT.709 correcto de punta a punta, error < 0.001. Descartar esa
   línea de investigación.
2. **El banding del bloom NO es un problema de grain/dither — es un problema
   de SEÑAL**: frames de la zona 4:20–5:00 usan ~31 niveles de luma 8-bit
   para todo el frame 4K (medido: t=4:25 → Y 60–91), con pendientes de hasta
   **800 px por nivel**. Ningún grain sobrevive al re-encode de YouTube;
   cuando VP9 borra el grain, la señal subyacente cuantiza en bandas de
   cientos de px. La solución es cambiar la señal (rango + estructura de baja
   frecuencia), no seguir inyectando ruido. Los 4 fracasos de la noche del
   06-09 ya lo demostraban.
3. **El detector es estructuralmente ciego a este banding**: analiza patches
   de 128×128 px; las bandas reales miden 268–800 px de ancho → la mayoría de
   los patches no contienen NINGUNA transición → "CLEAN". El disconnect
   detector ↔ ojo humano queda explicado mecánicamente. Hay que arreglar el
   detector ANTES de seguir iterando, o seguimos optimizando contra una
   métrica ciega.
4. **"Oscuro en YouTube"**: pendiente de A/B real (Fase 0), pero el candidato
   principal es la referencia de preview: QuickTime/macOS muestra video
   BT.709 más claro que Chrome/YouTube (gamma ~1.96 vs 2.2). Si la brightness
   se vino tuneando contra QuickTime (gamma lift 0.70 → 0.78 fue a ojo), el
   upload se ve más oscuro para todo el mundo menos para nosotros. Además la
   escena es objetivamente MUY oscura: a 4:25 el pixel más brillante del
   frame es Y=91/255 (~25% de brillo).

## Evidencia medida (2026-06-10)

### Color pipeline — OK (hipótesis BT.601/709 refutada)

Frame sintético rgb48le con los verdes del proyecto pasado por el comando
ffmpeg EXACTO de `render.py::render_full` (ffmpeg 8.1.1):

| Color fuente | YUV medido en archivo | Esperado BT.709 | Esperado BT.601 |
|---|---|---|---|
| (0.062, 0.155, 0.092) | Y=0.1748 Cb=-0.0185 Cr=-0.0381 | Y=0.1750 Cb=-0.0183 Cr=-0.0383 ✓ | Y=0.1658 (no) |
| (0.40, 0.80, 0.50) | Y=0.6582 Cb=-0.0918 Cr=-0.1641 | Y=0.6582 Cb=-0.0915 Cr=-0.1636 ✓ | Y=0.6177 (no) |

ffmpeg 8.x negocia el colorspace correctamente con `format=yuv420p10le` +
flags de salida. Roundtrip decode → RGB idéntico al fuente. **No tocar.**

### Bloom 4:20–5:00 — pendientes medidas en `1-outbound_v11.mp4`

Perfil radial de luma (8-bit equiv) desde el centro del frame:

| t | rango Y del frame | peor zona oscura | px por nivel de luma |
|---|---|---|---|
| 4:25 (265s) | 60–91 | r=600–800, Y≈76 | **~800 px/nivel** |
| 4:35 (275s) | 55–142 | r=1000–1200, Y≈81 | **~268 px/nivel** |
| 4:45 (285s) | 48–193 | r=1600–1800, Y≈59 | **~134 px/nivel** |
| 4:52 (292s) | 48–220 | r=1400–1900, Y≈63 | ~77 px/nivel |

Regla práctica: con > ~50 px/nivel en luma < 100, el banding post-YouTube es
inevitable sin estructura espacial adicional. El master 10-bit tiene 4× más
pasos (por eso el master local se ve liso); el problema aparece exactamente
al caer a 8-bit en el VP9 de YouTube.

### Por qué fallaron grain/dither (confirmación de iter_results_2026-06-09)

- El dither actual de `finalize()` es **±8/255 RGB independiente** (16/255
  pico a pico) — eso es ruido cromático enorme, no dither. VP9 gasta bits en
  intentar preservarlo y después lo promedia a cero dentro de cada bloque
  DCT → las bandas reaparecen y encima perdimos bitrate.
- El grain per-pixel (v13–v15) vive en frecuencias DCT altas = lo primero
  que cualquier encoder a bitrate finito descarta. **No existe amplitud de
  grain fino que sobreviva al re-encode de YouTube y sea invisible.** Es un
  callejón sin salida comprobado con 7 iteraciones.
- Lo que SÍ sobrevive a cualquier encoder: detalle de **baja frecuencia
  espacial** (escala 100–500 px). Está en los coeficientes DCT bajos, que el
  encoder preserva siempre.

### Hallazgos colaterales

- `out/1-outbound.mp4` está **corrupto** (moov atom faltante — encode
  interrumpido). El brief lo lista como "v11 baseline": FALSO, el v11 real es
  `out/1-outbound_v11.mp4`. Borrar o re-generar el corrupto.
- El emulador YouTube solo modela el rendition 2160p (VP9 20M). Si el viewer
  mira en 1440p (~9M), 1080p (~2.5M) o el test era el archivo 720p upscaleado
  a fullscreen, la degradación real es mucho peor que lo emulado. Validar
  contra el rendition que se mira de verdad.
- Iterar grain a 720p (`/tmp/outbound_720_grain.mp4`) no es representativo
  del 4K: el grain es per-pixel (cambia de escala) y el upscale a fullscreen
  ensancha las bandas 3×.

## Plan ejecutable

### Fase 0 — calibrar la referencia (necesita al user, ~10 min)

1. Subir `1-outbound_v11.mp4` (trim `_yt`) **unlisted** a YouTube si no está.
2. Mismo frame pausado (ej. 4:25) en: YouTube en Chrome / master en QuickTime
   / master en Chrome local / contact-sheet PNG. Screenshot de cada uno.
3. Diff numérico de los screenshots (cualquier modelo lo hace con PIL).
   - Si QuickTime ≫ Chrome → la referencia de brightness estaba contaminada:
     se corrige UNA vez la gamma del shader contra Chrome/YouTube y listo.
   - Si Chrome local ≈ YouTube → YouTube NO oscurece nada; era el preview.
4. Preguntas al user (bloquean Fase 3): ¿en qué display mira y a qué calidad
   (engranaje del player: 2160p? Auto?)? ¿El banding lo vio en YouTube real
   o en el archivo 720p local?

**Criterio de éxito**: número concreto de delta gamma entre referencia y
destino. Regla nueva de la biblia: **la referencia visual oficial es Chrome
reproduciendo el archivo YT-emulado** (o YouTube unlisted). QuickTime no es
referencia nunca más.

### Fase 1 — detector v11: ojos para bandas anchas (~30 min, sin render)

`banding_detect.py`:

1. Además del análisis actual, **downsamplear el frame 8× (lanczos) y correr
   la misma firma run-length** — una banda de 800 px pasa a 100 px y entra en
   el patch. Alternativa equivalente: medir px/nivel sobre perfiles suavizados
   (la métrica de este review).
2. Sumar métrica `worst_px_per_level` en zonas Y<100 al reporte por frame.
3. Re-validar: los frames 4:25/4:35/4:45 del v11 DEBEN dar dirty (hoy dan
   clean). Agregar al test bench un gradiente sintético de 30 niveles/4K.

**Criterio de éxito**: detector marca dirty los frames donde el user ve
banding. Recién entonces detector y ojo miden lo mismo y se puede iterar.

### Fase 2 — fix de señal en el shader (la solución real)

Todo en `outbound/render.py`, escena bloom (+ `finalize()`):

1. **Atmósfera de baja frecuencia**: FBM 3D a escala grande (100–500 px en
   pantalla, animado lento) modulando halo y fondo del bloom, amplitud
   ±2–3% de luma. Estéticamente es humo/niebla — coherente con la escena
   (bloom nace del humo) y con la estética Turrell. Esto le da al encoder
   estructura real que preservar: es LO que sobrevive a YouTube.
2. **Abrir el rango tonal del bloom temprano**: la escena 4:20–4:40 vive en
   Y 60–91; llevarla a ~Y 45–140 (más contraste = menos px/nivel). Es un
   cambio estético sutil → validar con stills A/B antes de animar (regla
   "stills before animation").
3. **Arreglar el dither**: reemplazar el ±8/255 RGB independiente por dither
   **luma-only ±1.5/255** (un solo hash, mismo valor a R,G,B). El dither
   correcto rompe la cuantización del propio master 10-bit; contra YouTube no
   pelea nadie más.
4. **Grain**: bajarlo a textura sutil (2–3/255 fijo) o sacarlo. Ya no es la
   herramienta anti-banding; era la herramienta equivocada.
5. Agregar `--start` a `render.py` (hoy solo tiene `--seconds`) para render
   de segmentos.

**Workflow de iteración**: render SOLO 4:10–5:10 (1800 frames) a **4K
nativo** — minutos, no horas. Nada de iterar a 720p.

**Criterio de éxito**: stills A/B aprobados por el user ANTES del re-render
full; segmento pasa Fase 3.

### Fase 3 — validación honesta multi-rendition

1. Emular **tres** renditions del segmento: 2160p VP9 20M (script actual),
   1440p ~9M, 1080p ~2.5M (agregar flag de resolución a
   `youtube_emulate.sh`).
2. Detector v11 sobre los tres + **el user mira el emulado en Chrome
   fullscreen en SU display** (el mismo archivo que midió el detector —
   nunca más detector sobre una cosa y ojo sobre otra).

**Criterio de éxito**: detector v11 clean en el rendition que el user mira
de verdad + user no ve bandas. Ambos sobre el mismo archivo.

### Fase 4 — cierre

1. Re-render full 4K con la config ganadora (horas, background).
2. Detector v11 full + emulación 2160p y el rendition del user.
3. Upload unlisted → check visual final del user → publicar.
4. Actualizar `25_pipeline_bible.md`: nueva regla px/nivel, referencia
   Chrome, dither luma-only, "estructura > ruido", y el postmortem del
   detector. Actualizar `dashboard/data.json`.

## Addendum 2026-06-10 (tarde) — resultados de ejecución

- **Detector v12** implementado en `banding_detect.py` (`detect_wide_bands`,
  métrica `wide_pct` + `worst_plateau_px`). Validado: frame 4:25 de outbound
  pasó de 0.00% (v10/v11) a 38.9% wide; en el VP9 emulado del bloom da
  98.3% con plateaus de 444 px. Bench sintético de Opus sigue PASS.
- **Fase 2 outbound**: variantes B (atmo 0.10 + contraste 1.30) y C (atmo
  0.18 + 1.45) en `outbound/render_fase2_{B,C}.py`. Métrica wide en bloom:
  A 38.9/19.0/14.0% → B 5.9/3.1/2.5% → C 4.5/2.1/1.9%. Stills A/B/C en
  `/tmp/fase2_ABC_contact.png`, esperando veredicto del user.
- **Recursion re-scaneado con v12**: avg wide 3.5%, max 8.3% → **CLEAN
  confirmado, subible**.
- **Crossing re-scaneado con v12**: avg wide **43.2%**, los 52 frames
  sampleados > 20%. Peores zonas: intro 0:02–2:47 (30–61%, plateaus
  208–388 px) y ~8:32 (56%). Verificado visualmente t=1:02: frame entero
  en luma 26–66 (40 niveles para todo el 4K). **El "PASA 0.05%" del brief
  salió del detector ciego — Crossing NO es subible como está.** Su fix va
  por otro camino que outbound (pipeline = clips Blender + build_13min.sh,
  no shader): plate de niebla FBM de baja frecuencia overlay en el build +
  apertura de contraste en los segmentos más chatos. Diseñar con stills
  primero, igual que outbound.
- **v16 de Opus** (`grain mix(4→10)/255`, 720p en `/tmp/outbound_720_grain.mp4`):
  render completo. Pronóstico: el grain per-pixel no sobrevive al VP9 de
  YouTube — verificar contra emulación antes de invertir más en esa línea.

## Addendum 2026-06-10 (noche) — deliverables v19/v2

Iteración ejecutada (Fable, autorizado por user): v17 (atmósfera 2-octavas
en 6 escenas + rango en bloom) → diagnóstico ×8 en VP9 emulado mostró
macroblocking DC residual → v18 (3ra octava media ~80-160px: la escala que
fuerza diffs entre bloques DC de VP9) → v19 (lift de luma en humo, Weber).
Crossing: fog plate FBM 3-octavas (480/190/96px) screen 0.12 + curves que
abre el rango oscuro, aplicado en post sobre el master (su pipeline no es
shader).

**Deliverables** (en `transmissions/01/video/out/`):
- `1-outbound_v19.mp4` (480.0s) + `1-outbound_v19_yt.mp4` (479.43s)
- `2-crossing_v2.mp4` (780.0s) + `2-crossing_v2_yt.mp4` (779.46s)
- `3-recursion_yt.mp4` sin cambios (v12 clean; deltas inter-frame parejos,
  interpolación 12→24 sana).
- Thumbnails: `artwork/youtube_thumbnails/{1-outbound,2-crossing}_thumb_v2.jpg`
  (los viejos eran lavado/negro a tamaño sidebar).

**Métricas** (detector v12, wide_pct):
- Outbound master full: avg 12.0% (v11) → **7.9%** (v19); zonas 22-36% → ≤14.6%.
  Único outlier: fade-in 0:02 (45%, transitorio).
- Outbound emulado VP9 ventana crítica: 44.1% (v11) → ~35% (v19). El VP9
  20Mbps local sigue aplastando los darks; el residuo es orgánico (×8 sin
  escaleras coherentes), clase perceptual distinta al banding geométrico
  original.
- Crossing master: 43.2% → **14.9%**; emulado segmento peor: 86.8% → 21.2%.

**Límite conocido**: el emulador es el peor caso (VP9 vainilla). YouTube real
preprocesa y suele servir AV1 en 4K (mejor con gradientes). Próximo paso
correcto = upload unlisted y ojos del user en Chrome 2160p/1440p — NO un v20
a ciegas (regla no-rabbit-holes). Levers restantes si YouTube real falla:
blue-noise dither, amp de atmósfera (costo estético), aceptar.


## Addendum 2026-06-12 — v22/v3: diagnóstico real con archivos de YouTube

Bajamos los archivos QUE YOUTUBE SIRVE (yt-dlp + cookies) y cambió todo:
- **YT 2160p = VP9 ~10Mbps** (el emulador asumía 20) con keyframe cada 3-5s;
  1080p = 0.35Mbps. Emulador recalibrado (youtube_emulate.sh v2).
- **"Saltos que van y vuelven" (0:09, 6:10) = GOP pumping**: keyframes de YT
  exactos en esos timestamps con pops SAD 20-30x baseline. Causa: nuestro
  ruido TEMPORAL (grain 6Hz + dither re-seedeado por frame). Fix v20: ruido
  estático mínimo → pops 20-30x → <3x (validado emulado). Crossing nunca
  pumpeó (su textura era estructural) = experimento natural que valida.
- **"Cortes en los Julia" = path de c cruzando el borde del Mandelbrot** (el
  set se desintegra/rearma). Fix v3.21: c recorre la cardioide → Julia
  SIEMPRE conexo. Validado: 0 anomalías en 3120 frames.
- **Banding visible = LINEAS DE CONTORNO de cuantización** (screenshot del
  user amplificado x6: curvas topográficas de 1 nivel). Las métricas de
  plateaus NO pesaban la continuidad de bordes (el ojo sí). Gate nuevo:
  amplificado x6 en condición de pantalla, CERO líneas continuas.
  Fix v22: rango tonal radial REAL en bloom/humo (12-24 niveles en pantalla
  → 80-131) + hue travel (el tono viaja con la luma y rompe contornos).

**Deliverables finales** (out/): `1-outbound_v22.mp4` + `_yt` (479.43s),
`2-crossing_v3.mp4` + `_yt`. Ambos pasan el gate de contornos en el encode
final. Masters ~2.4GB c/u (el contenido encoder-friendly comprime 3-4x menos
que con ruido temporal — señal de que YT también lo va a tratar mejor).

**Reglas nuevas (biblia)**:
1. Validar contra LO QUE YOUTUBE SIRVE (yt-dlp), no contra specs.
2. Ruido temporal = veneno (GOP pumping). Textura estática o estructural.
3. Gate de contornos x6 obligatorio antes de entregar.
4. QA de continuidad temporal (cortes/loops, cut_loop_detect2.py) por render.
5. Paths paramétricos de fractales: garantizar conexidad (cardioide).

## Antipatrones nuevos para la biblia

1. **NO iterar anti-banding con grain/noise per-pixel** — 7 iteraciones lo
   probaron; el techo es matemático (DCT), no de tuning.
2. **NO usar dither RGB independiente de alta amplitud** — es ruido cromático
   que regala bitrate.
3. **NO validar con detector en un archivo y ojo en otro** (4K emulado vs
   720p local = el disconnect de esta semana).
4. **NO tunear brightness en QuickTime** — referencia es Chrome/YouTube.
5. **Regla px/nivel**: en zonas Y<100, mantener pendientes < ~50 px por nivel
   8-bit O cubrirlas con estructura de baja frecuencia. Chequearlo en
   `--pretest` antes de render full.
