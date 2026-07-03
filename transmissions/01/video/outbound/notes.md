# Outbound — 3D raymarched re-render

## v6 (artist iteration #6 — junio 2026, "muy bien outbound + 2 fixes")

El artista aprueba v5 ("muy bien outbound") y pide 2 fixes específicos.
Render time: 38m36s (~6.2fps ffmpeg final / 8.5fps python). 363MB mp4.

### Fix 1 — Shift boundaries left 30s

Las dos transiciones finales caen sobre cambios musicales reales.

- portal→partida: 6:30 → **6:00** (boundary 390 → 360)
- partida→afuera: 7:30 → **7:00** (boundary 450 → 420)
- afuera se extiende 30s extra (cierre con más aire)

SCENES v6:
```
("nacer",   0.0,   75.0),
("tunel",   75.0,  211.0),
("humo",    211.0, 263.0),
("bloom",   263.0, 312.0),
("portal",  312.0, 360.0),   # v6: -30s
("partida", 360.0, 420.0),   # v6: -30s
("afuera",  420.0, 480.0),   # v6: +30s closing
```

Las transiciones especiales (light-flash portal→partida, 9s xfade
partida→afuera) se preservan — solo cambia el boundary.

### Fix 2 — Discrete BELL/HEART events

El artista se queja de bells sin light, lights sin bell, sync off.
Causa: v5 usa `u_sparkle` (centroid spike) + `u_rms_air` (envelope
smoothed) → respuesta promediada al envelope, no a eventos discretos.

**Nuevo modelo**: lista hard-coded de timestamps + uniforms
`u_sparkle_amp` / `u_heart_amp` driveados por Gaussian bumps
discretos. Cada event = bump 0..1 con peak a t+80ms y window 400ms.

```python
BELL_EVENTS  = [40.00, 47.00, 50.27, 57.07, 59.33, 65.00, 69.50, 72.43]
HEART_EVENTS = [12.00, 18.00, 22.00, 27.00]
EVENT_WINDOW_S = 0.4
EVENT_SIGMA_S  = 0.08
```

**Análisis de audio** (`outbound.npz`):
- `rms_air` peaks (smooth 0.3s, thresh mu+1·std, gap 0.2s) en 0-75s:
  → 50.27, 57.07, 59.33, 69.50, 72.43 (band-detected real)
- `rms_sub` está SATURADO en 0-30s (clip a 1.0) → no se pueden detectar
  peaks; honramos los timestamps del artista directamente.
- Tiempos del artista 40, 47, 65 NO tienen señal en el aire-band del
  npz pero el artista los escucha → añadimos como events extra
  (perceptual ground-truth > detector).

**Render del ovulo (NACER)**:
- `r = 0.95 + ... + 0.019*u_heart_amp` → ±2% radius scale a cada heart
- sparkle redesigned: estrellita pequeña (1.4%) + 4 rayos + halo difundido
  (radio 0.20), todo multiplicado por `u_sparkle_amp` → cada bell tiene
  su destello propio, sin parpadeo de envelope ni dependencia de
  centroid spikes erráticos.

Se retira el viejo `sparkle_window` gate (t=42-70) y los tipos A/B
con cadencias sinusoidales — innecesarios cuando los disparos son
discretos.

### Verificación (verify_v6/contact_v6.png)

- Frames t=12, 18, 22, 27: ovulo presente, pulse subliminal (±2% sutil)
- Frames t=40, 47, 50, 57: sparkle activo (center dot + halo brillando)
- Frames t=358 (portal still), 362 (partida light-flash entry)
- Frames t=418 (partida pre-7:00 xfade), 422 (afuera with beams)
- Frame t=478: fade-out (40% brightness, near end)

Ambas transiciones nuevas (6:00, 7:00) confirmadas visualmente.

## v5 (artist iteration #5 — junio 2026, "muy groso, un pelín más")

8 fixes finos sobre v4. El artista lo da por casi-final.

1. **Fade-in desde negro 0-5s** (`render_frame`): el frame se multiplica
   por `smoothstep(0, 5, t_sec)` (`fade_in = x*x*(3-2x)` con `x=t/5`).
   Tapa el arranque fulero del ovulo. A t=0 todo negro, a t=5 full.
2. **Stripes 0:08 fix**: `finalize()` rediseñado con dither multi-componente
   isotrópico — tres hashes con coords rotadas (rot1/rot2/rot3) y jitter
   por canal RGB separado. Anti-bandas axiales. Además el fade-in #1
   cubre el frame a 0:08 (~74% transparencia).
3. **Sweep R→L 0:14 fix**: causado por `sparkle_window = 1.0 -
   smoothstep(55,70,t)` que dejaba el sparkle FULL ACTIVO desde t=0 →
   cualquier centroid spike disparaba un destello visible como sweep.
   Ahora: `sparkle_window = smoothstep(42, 48, t) * (1 - smoothstep(70, 73, t))`.
   Los tilin tilin reales son a 50.27, 57.07, 59.33, 69.50, 72.43.
4. **Sparkle redesign**:
   - DIFUNDIDO: halo expandido (radio 0.20-0.28 con respiración lenta).
   - DIM: peak intensity al 70% (`* 0.70` final).
   - DOS TIPOS:
     - **A (fast/small)**: rayos de difracción + center dot ×0.85 driven
       por `u_sparkle` (centroid spike). Cadencia 3 Hz (era 4).
     - **B (slow/soft)**: halo radial sin rayos, sin breath lento
       (`sin(t*0.8)`) driven por `u_rms_air`. Sostiene 200-300ms.
   - Air event times en npz: 50.27, 57.07, 59.33, 69.50, 72.43.
5. **Túnel slower**: `zCam = -u_time * 2.85` (era 4.5) — 37% más lento.
   El corredor respira.
5b. **Túnel core dim + walls boost**: core ×1.30 (era 1.9, ~30% menos),
    halo_wide ×0.60 (era 0.85), walls lit ×1.22 (diffuse 0.86, rim 1.05,
    surf 1.10) — la estructura del corredor se ve, el core no domina.
5c. **Black mark central removido**: `pow(vanish, 1.4) * 0.30` → 
    `smoothstep(0.40, 1.0, vanish) * 0.18`. Sin pico exponencial que
    creaba un pequeño hueco oscuro de transición al medio.
6. **Tunel→humo a 3:28**: boundary SCENES `tunel 75-211` / `humo 211-263`
   (era 208). XFADE window 8s pre / 2s post → 203→213, boundary 211 = 3:31
   con transition AT 3:28 (start of post).
7. **Mandala close a 4:51**: `open_phase smoothstep(0, 0.57, scene_t)` /
   `close_phase smoothstep(0.57, 0.90, scene_t)`. A scene_t=0.57 (291s
   = 4:51) empieza a cerrar.
8. **Portal→partida a 6:30**: boundary 380 → 390 en SCENES. Portal +10s,
   partida 60s. LIGHT_FLASH transition centrada en 390.

### v5 verification frames
0, 2, 5, 8, 14, 50, 52, 58, 75, 90, 120, 208, 211, 290, 291, 350, 380,
390, 391, 450.

---

## v4 (artist iteration #4 — junio 2026, "definitivamente este va a ser el nuevo video")

11 fixes literales sobre v3:

1. **0:00-0:01 planeta+bg juntos**: removido `fade_in = t/2.0` global en
   `render_frame`. El planeta y el fondo aparecen simultáneamente desde
   el primer frame. `fade` ahora solo es `fade_out`.
2. **Ovulo levemente más brillante**: `iris_col *= 0.55` → `0.68` en
   SCENE_NACER.
3. **Sparkle TINY star**: rediseñado como diffraction-spike clásico.
   - Center dot: radius 1.2% del planeta (era no-radial blob).
   - 4 rayos (diffraction spikes): `max(cos(2*tang)^80, cos(2*tang+π/2)^80)`.
   - Decay radial agresivo (`exp(-rAng*12)`) → rayos cortos y delgados.
   - El resto del planeta NO se ilumina (sparkle es aditivo solo donde
     hay rayo o center_dot).
4. **Continents/clouds animadas**: `surface_drift = t*0.02` advecta el
   patrón angular de los fibers; `fbm_drift = t*0.025` desplaza las
   coordenadas 3D del fbm. Movimiento subliminal pero visible comparando
   t=15 vs t=60.
5. **Transición a EXACTAMENTE 1:15.0**: nuevo `ASYMMETRIC_XFADE` para
   xfade post-boundary. `("nacer","tunel")` → `(0.0, 8.0)` significa
   ventana de xfade va de boundary+0 a boundary+8 = 75.0 → 83.0. Hasta
   t=75 ovulo intacto. Dive in-scene gateado a `smoothstep(75, 83, t)`.
   `scene_at()` ahora soporta xfade asimétricas en ambos sentidos.
6. **1:13-1:14 hint glow**: en SCENE_NACER, `hint_k = smoothstep(73, 75, t)`
   activa un bright dot + halo verde-claro en el centro del ovulo,
   anticipando el core del túnel.
7. **Tunnel core más difumiado**: `vanish = exp(-axialDist * 3.5)` (era
   8.0). Adicional `halo_wide = exp(-axialDist * 1.4) * 0.55`. Los rings
   ahora se mezclan con el core (no se ve "ball separada en el fondo").
8. **Tunel→humo 8s, 3:20→3:30**: `SPECIAL_XFADE` actualizado a 10.0s
   y `ASYMMETRIC_XFADE[("tunel","humo")] = (8.0, 2.0)` → window 200→210
   con boundary en 208.
9. **5:49 enrolling rhythm**: en SCENE_PORTAL, `enroll_k = smoothstep(37, 47, t)`
   (37s local = 312+37 = 349 global). Acelera roll de cámara (+0.85 rad/s),
   duplica morph speed de los fold params, agrega rot extra entre folds,
   y aplica hue rotation drift `+sin(t*0.6)*0.08` con saturation boost.
10. **6:20 light flash transition**: nuevo composite mode `u_mode=3`
    (LIGHT_FLASH). En lugar de fade-to-black hace un whiteout corto
    (bell `exp(-((w-0.5)/0.18)^2)` con luz verde-clara `(0.92, 1.0, 0.78)`).
    Adicional, SCENE_PARTIDA reforzada para arrancar YA en movimiento:
    cam oscilla con `sin(u_time*0.35)*0.35`, target drifteando, roll
    continuo, spin acelerado `u_time*0.35` (era 0.22). El primer frame
    nunca está frenado.
11. **7:36 partida→afuera xfade +50%**: `SPECIAL_XFADE[("partida","afuera")] = 9.0`
    (era 6.0).

### Composite shader modes
- 0 mix (default)
- 1 edge_invade (no usado en v4)
- 2 eye_close (deprecado — era fade-to-black, no respeta fix #10)
- 3 light_flash (fix #10 — whiteout breve, NO black)

### Encoder
- libx264 high10 yuv420p10le CRF 17 preset fast, AAC 192k.
- rgb48le pipe (16-bit) → 10-bit color.

---

## v3 (artist iteration #3 — junio 2026)

14 fixes literales sobre v2:

1. **Apertura 0:00-0:02**: planeta/ovulo aparece INSTANTÁNEAMENTE. Halo y
   fondo emergen con la esfera, no antes. Pre-condición eliminada.
2. **Planeta más oscuro + atmosférico**: brillo base ×0.55; fibers a
   freq 40 (era 70) + blur fbm; spec freq 32 vs 48. Menos foto-real.
3. **Hoyo negro removido**: c_pupil de 0.10 → 0.55 (deep-green no negro).
   smoothstep pupila/iris más ancho (no bordes). Glow central sutil
   reemplaza al hoyo.
4. **Heartbeat ×0.25**: 0.0038*beat + 0.0055*rms_sub (eran 0.015 + 0.022).
5. **Beep light → starburst**: rayos delgados a 18-fold (cos(tang·9)^38)
   + cadencia rítmica con square wave a 4 Hz. Decay radial extendido
   (exp(-rAng·1.8)) → rayos van lejos.
6. **Ovulo→tunel a 1:15**: boundary t=75 (era 70). Dive-in 67-75s.
7. **Tunel core ball más chica + rings concéntricos**: vanish decay 5.5→8.0
   (ball concentrada). Cámara ya NO drift X/Y (eran sin/cos offsets que
   descentraban el túnel del core). Vanishing point ahora coincide con el
   core en pantalla.
8. **Tunel→humo a 3:28**: boundary t=208 (era 200).
9. **Bastones removidos (4:49-5:12)**: SCENE_BLOOM extendido a 263-312s
   (49s). Apertura hasta scene_t=0.67 (4:55), CIERRE progresivo 0.67-0.97
   (4:55-5:08), core glow crece monotónicamente. SIN pétalos 3D extruidos.
10. **5:30 NO FADE — dive into light**: bloom termina con core casi blanco
    (vec3(0.9,1.0,0.7) × close_phase). Portal arranca con entry_boost ×1.8
    en exp(-rv·3.5). Continuidad LUZ→LUZ.
11. **5:30-6:22 dynamic kaleidoscope**: SCENE_PORTAL nuevo. Folding
    params MORPHEANTES con sin(u_time*X), rotación entre folds que
    evoluciona, roll continuo de cámara (0.25 rad/s). Anti-cardboard.
12. **REORDER 7:00+**: SCENE_PARTIDA (espiral magnetar, le gusta) ahora
    380-450s. SCENE_AFUERA (humo amarillo + beams) ahora 450-480s (cierre).
13. **Eye-close transition**: composite shader nuevo modo `u_mode=2` —
    fade a→black + fade black→b con ventana corta de negro al medio
    (pestañeo). Usado en portal→partida (boundary 380).
14. **N/A**: el chamber se hizo dinámico (fix #11). No fue necesario
    removerlo.

### Transiciones (todas)
- nacer→tunel (2s): dive-into iris (diegética)
- tunel→humo (4s): mix smooth
- humo→bloom (6s): continuum, flor sobre nube
- bloom→portal (3s): dive-into-light (NO fade)
- portal→partida (4s): EYE-CLOSE (pestañeo único permitido)
- partida→afuera (6s): smooth dive

### Encoder
- libx264 high10 yuv420p10le CRF 17 preset fast, AAC 192k muxeado.
- rgb48le pipe (16-bit) → 10-bit color.

---

## v2 (artist iteration — junio 2026)

Sobre v1 ("interesante búsqueda, puede reemplazar al original"), 7 fixes
específicos pedidos por el artista:

### 1) Ovulo (0:00-1:10) — pulso retirado al inicio + sparkle
- 0-22s: iris completamente quieto. Sin heartbeat.
- 0-50s: **sparkle/destellito** en el CORE del iris cuando hay "beep voyager".
  Detección: spike de `centroid` sobre baseline (window 2s) — caracteriza
  el motivo agudo. Glow concentrado en core (rAng < 0.07), color verde claro.
- 22-65s: heartbeat sube SUTIL (~1/2 de la amplitud v1): factor 0.015 sobre
  beat + 0.022 sobre rms_sub (era 0.030 + 0.045 en v1).
- 62-70s: dive-in (ver #2).

### 2) Transición ovulo → tunel (1:08-1:20) — DIVE diegético
- v1: fade plano (artista lo odió).
- v2: cámara avanza Z 2.6 → 0.10 entre t=62s y t=70s. FOV se abre 40° → 85°.
  Iris crece en pantalla, halo y vignette se apagan, y un máscara circular
  negra crece desde el centro hasta tragarse el frame (la pupila ES el
  túnel). En t=70s casi todo es negro (matching tunel start).
- XFADE clásico reducido a 2s (solo cubre el cut).

### 3) Tunel (1:20-3:20) — core color/intensidad reactivo a voyager
- v1: vanishing point pulsando con rms_sub + onset (titilando).
- v2: `flux_smooth` (ventana 2s) modula el core:
  - Hue shift ±0.05 alrededor del verde base (HSV).
  - Intensity ±0.20 alrededor de base 0.55.
  - Plus respiración lenta (sin a 0.35 Hz) para que nunca quede congelado.
- Lectura: el motivo voyager (banda media + brillo melódico) hace que el
  core "respire" verde→amarillo→verde sin parpadear.

### 4) Humo (3:20-4:20) — sólo 60s (era 90)
- Estética sin cambios (volumetric raymarch nube verde).
- Acorta para abrir espacio al bloom.

### 5) Bloom (4:20-4:50) — nueva escena de transición
- Flor-mandala rose polar (`abs(cos(N·θ/2))`) creciendo durante 30s:
  - Radio: 0.05 → 0.55.
  - Pétalos: 6 → 12.
  - Saturación: GREEN_DEEP apagado → mezcla con AMBER cálido.
  - Glow central que crece, halo radial que expande.
- Fondo: el humo sigue presente pero atenuado (×1.0 → ×0.45).
- En t=4:50s la flor está abierta y entrega al portal dimensional.

### 6) Portal dimensional (4:50-6:20) — DIVE → KIFS tunnel → CHAMBER
- Tres sub-fases internas en SCENE_MANDALA gobernadas por u_scene_t:
  - **0.000-0.222 (290-310s, 20s) — DIVE**: cámara avanza al centro de los
    pétalos extruidos (SDF round-box × 12 simetría radial), zEye 3.0 → 0.05,
    FOV 45° → 85°. En el último 30% el centro se oscurece para entregar al
    túnel.
  - **0.222-0.444 (310-330s, 20s) — TÚNEL FRACTAL**: KIFS folded
    (`abs() + swap + scale·1.35 - offset` × 4 octavas) con anillos axiales,
    paredes radiales emisivas. Cross-blend con DIVE al inicio (8%).
  - **0.444-1.000 (330-380s, 50s) — CHAMBER**: cámara DENTRO de espacio
    plegado KIFS (6 octavas con swap xy/xz/yz + rotación entre folds).
    Paredes emisivas con patrones multi-octava radial (12-fold + 8-fold + 3D
    noise), venas brillantes (smoothstep 0.62-0.78), brasa amber en rim
    fresnel, AO por iteraciones, dos luces direccionales. Cámara hace
    orbit lento (0.06 rad/s) + drift vertical. La sensación es "templo de
    geometría sagrada" — distinto de cualquier cosa en crossing.

### 7) Chamber → afuera (6:15-6:25) — humo invade desde bordes
- XFADE 10s (más largo que default).
- Composite shader nuevo con `u_edge_invade=1.0`: el alpha de la escena B
  (afuera con beams + niebla) crece desde los bordes del frame hacia el
  centro. Lectura: niebla/humo invadiendo el chamber desde afuera.

Escenas AFUERA y PARTIDA: sin cambios (artista las quiere intactas).

### Nuevas señales de control
- `flux_smooth`: spectral flux con window 2s, normalizado p5..p95.
  Proxy del motivo voyager melódico. Modula tunel core hue/intensidad
  + un poco el chamber.
- `sparkle`: spike-detector sobre `centroid` (diferencia positiva vs
  baseline 2s ·1.4). Suavizado 100ms, escalado ×3. Dispara destellos en
  iris core y otros eventos.

### Encoder
- libx264 high10 yuv420p10le CRF 17 preset fast.
- Float32 framebuffer → rgb48le pipe → 10-bit color.
- AAC 192k muxeado con `01_outbound_master.wav`.

---

## v1 (referencia histórica)

Seis escenas raymarcheadas reales. Paleta verde anegrado + warm-amber raro.
Cada escena con técnica 3D distinta — no patrones 2D, no post del original.
Crossfades smoothstep 8s. Ver historia de git para detalle.
