# BRIEF — Video Crossing (Transmission 01 / ÆM)

> Documento de visión. CORREGIDO 2026-05-28 tras leer los archivos que el
> artista ya tenía authoreados (`ai/prompts_crossing_delirio.txt`,
> `hydra/SCENES.md`, `hydra/crossing_delirio_aire.js`). La versión anterior
> de este doc tenía la estética MAL (decía "B&W woodcut nordic" — eso fue
> invención del asistente, NO la visión del artista).

---

## 1. EL NORTE

13 minutos atravesando un umbral cósmico denso — el "cruce" de la sonda por
la heliopausa. Inmenso, oscuro, desorientante. Pero con una **impronta
estética muy específica y ya definida por el artista**: terminal de fósforo
verde / telemetría NASA vintage / glitch analógico. Abstracto, no figurativo.

---

## 2. ESTÉTICA (la impronta — NO negociable, ya definida)

- **FÓSFORO VERDE CRT** — `#a6d65f` (phosphor) / `#6a9034` (phosphor dim)
  sobre **negro CRT**. Es monocromático VERDE, NO blanco y negro.
- **WARM_AMBER `#d4a04a`** = accent RARO, 2-3 veces en TODO el video. No más.
- **Telemetría NASA vintage / terminal CRT** — scanlines analógicas, grain.
- **Glitch / datamosh / signal breakup / dropouts** como lenguaje, no adorno.
- **Abstracto NO-figurativo** — anti-iconografía estricta.
- **Color sucio mineral/solarizado** estilo final de 2001 (no neón, no
  vaporwave) SOLO en la sección stargate post-inversión.

---

## 3. ANTI-ICONOGRAFÍA (lo que el negative prompt PROHÍBE)

Del `prompts_crossing_delirio.txt` — NUNCA mostrar:

- ❌ Planetas literales, luna llena, tierra, saturno dibujado/fotorrealista
- ❌ Caras, ojos, personas, astronautas, manos, cuerpos
- ❌ Naves, cohetes, foto Hubble, nébula fotorrealista
- ❌ Espiral dibujada / ícono de swirl literal
- ❌ Neón, cyan, magenta, rosa, azul glow, synthwave, vaporwave, rainbow
- ❌ Barras de ecualizador, waveform, spectrum analyzer, VU meter
- ❌ Texto, watermark, viñeta, borde, ornamento
- ❌ Foto, fotorrealismo, 3D render limpio

> Nota: el saturno 3D fotorrealista que el asistente rendereó en Blender el
> 2026-05-28 viola DIRECTAMENTE esta lista. No es el camino.

---

## 4. SISTEMA: audio-reactivo en Hydra (YA CONSTRUIDO)

El video NO se genera con prompts de AI. Es un **patch de Hydra** (live-coding
visual / WebGL) construido por el artista, reactivo al audio:

- Feedback base `src(o0)` — la trayectoria de la sonda ES el grado de feedback.
- FFT 4 bins (`a.setBins(4)`):
  - `fft[0]=SUB` — heartbeat / columna 42 Hz
  - `fft[1]=LOW` — drones / bajo
  - `fft[2]=MID` — voces / pads / **motivo Voyager**
  - `fft[3]=HIGH` — aire / glitch / crackle
- Escenas = ventanas `win(t0,t1)` + `.blend()` sobre el feedback base.
- Anti-fritura: `thresh()` → glitch/polvo/crackle como eventos discretos.

Archivos:
- `hydra/crossing_delirio_aire.js` — patch más reciente (2026-05-24)
- `hydra/crossing_delirio.js` + `_v7_checkpoint.js` — versiones previas
- `control/crossing.npz` — track de control audio→visual
- `hydra/HEADLESS_NOTES.md` — cómo renderizar headless

---

## 5. ESTRUCTURA — 9 escenas Crossing (13:00 / 780s, sync al master)

De `hydra/SCENES.md`:

| # | Escena | Rango | Qué se ve | Banda FFT |
|---|--------|-------|-----------|-----------|
| 1 | ENTRADA AL UMBRAL | 0:00–1:30 | Campo casi negro + primer polvo + presencia central | SUB/LOW |
| 2 | POLVO DE LOS ANILLOS | 1:30–3:20 | Río de partículas arrastradas (polvo de Saturno, abstracto) | SUB/MID |
| 3 | NÉBULA DENSA | 3:20–5:00 | Membrana de densidad que ondula y llena el cuadro | LOW/MID |
| 4 | ROCAS / TROPEZONES | 5:00–6:30 | Rocas que ocluyen + impactos en transients | HIGH onsets |
| 5 | **INVERSIÓN** ⭐ | 6:30–7:50 | La órbita SE PARTE: `spin()` cruza +1→-1, todo se invierte | LOW giro inv. |
| 6 | RELÁMPAGOS | 7:50–9:20 | Flashes solarizados súbitos en onsets (descarga sucia) | HIGH onsets |
| 7 | RAYAS HORIZONTALES ⭐ | 9:20–10:50 | Rayas horizontales picantes (scan CRT roto) + crackle | HIGH scan |
| 8 | STARGATE | 10:50–12:10 | Corredor slit-scan, color sucio mineral solarizado (2001) | SUB/MID |
| 9 | SALIDA / GANCHO | 12:10–13:00 | El túnel se enrosca en espiral, color vuelve al verde | LOW/SUB |

- **Inversión a 6:30**: `spin()` = +1 antes, -1 después, cruza suave en ~20s.
  Es el punto de giro visual. Atado al hexagrama 24/42.
- Crossfade 16s entre escenas (tema muy largo).
- Loop del EP: Outbound → **Crossing** → Recursion → Outbound (cierra = Hexagrama 24).

---

## 6. SENSACIONES (palabras del artista, esta sesión)

- INMENSIDAD — universo gigante
- OSCURIDAD — negro profundo
- TERROR / DREAD — densidad picante, el cruce difícil
- DESORIENTACIÓN — la órbita que se parte, el giro que se invierte

---

## 7. SPECS TÉCNICOS

- **Resolución: 4K (3840×2160)** — el entregable final
- **Duración: 13:00** sync con `transmissions/01/release/masters/02_crossing_master.wav`
- **PRO** = release distribuible (YouTube/festivales/Bandcamp)
- 24fps (o el fps del patch, a confirmar)

---

## 8. LA TENSIÓN TÉCNICA REAL

El sistema (Hydra/WebGL) ya existe y ES la visión. El desafío NO es generar
contenido — es **renderizar el patch Hydra existente a 4K limpio, sincronizado
al master**, headless. Ver `hydra/HEADLESS_NOTES.md`.

El "crossing que estaba bien" que mencionó el artista es probablemente un
render de este patch. La pregunta es subir ese render a 4K PRO sin romper la
reactividad al audio ni la estética fósforo.

---

## 9. PRÓXIMO PASO PROPUESTO

Validar el render headless del `crossing_delirio_aire.js` a 4K (o a la máxima
res que Hydra/WebGL capture limpio) sincronizado con el master — NO inventar
contenido nuevo. Si ya hay un render "bien", partir de ese y subir calidad.
