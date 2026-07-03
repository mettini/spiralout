# Técnicas de transición para Crossing — investigación 2026-05-29

> El artista: "¿todo tiene que ser un fade? Con imágenes tan dispares, investigá
> técnicas". Acá las técnicas + cuándo usarlas + cómo implementarlas ($0, ffmpeg).
> Las transiciones van **al ritmo de la música**.

## El principio
Footage abstracto + glow sobre NEGRO. Lo que mejor funciona: anclar la transición
en un **elemento visual compartido** (centro de luz, color, forma) o en un **golpe
de la música**. El fade plano es lo PEOR para material disímil (lava todo a gris).

## Catálogo (por uso en Crossing)

| Técnica | Cuándo | Cómo ($0) |
|---|---|---|
| **Hard cut al beat** ("pum") | cambios de ritmo, energía | concat sin transición; el corte cae en el onset de la música |
| **Match cut** (ancla visual) | core de luz ↔ luz entre rocas; agujero ↔ túnel | elegir frames donde A y B comparten el mismo punto/forma y cortar ahí |
| **Flash / luz** (fadewhite) | descargas, rayos, impactos | `xfade=transition=fadewhite:duration=0.15` (flash corto) o meter 1-2 frames quemados |
| **Iris / radial** (circleopen, radial) | entrar al ojo/mandala/túnel | `xfade=transition=circleopen` o `radial` centrado en el agujero |
| **Zoom / punch-in** (match de escala) | amber que crece → mandala; mandala → túnel | escalar A hacia el ancla (zoompan/scale) y cortar a B con la misma escala |
| **Dissolve aditivo / screen** | glow sobre negro (no ensucia) | `xfade=transition=dissolve` o blend `screen` en el solape (los brillos se encadenan) |
| **Glitch / datamosh** | señal sucia, cruce picante | solape de 2-4 frames con grim_post warp+CA al mango (`--scale` alto) |
| **Pixelize / hblur** | degradación de señal | `xfade=transition=pixelize` / `hblur` |
| **Fade velado** (fade/fadeblack) | respiros lentos SOLO | `xfade=transition=fade` — usar POCO |

> ffmpeg `xfade` trae ~50 `transition=` (fade, fadewhite, fadeblack, dissolve,
> circleopen, circleclose, radial, smoothleft/right/up/down, wipe*, slide*,
> pixelize, hblur, distance, diagtl, …). Lista: `ffmpeg -h filter=xfade`.

## Plan de transiciones para el flujo (storyboard doc 13)
1. lego-planet → planeta cerca: **hard cut** (pum) o **zoom/punch-in** (acercándose)
2. planeta → core de luz: **hard cut al cambio de ritmo** (pum), anclado al centro
3. core de luz → rocas: **match cut** por el centro de luz (la luz entre rocas)
4. rocas → fractal: **hard cut** (pum) + el fractal entra con viñeta-túnel
5. fractal/amber → mandala: **zoom/punch-in** (el amber crece) o **circleopen**
6. mandala → túnel kaleid: **iris/radial** centrado en el agujero (entramos)
7. túnel → estrellas: **dissolve aditivo** o salir del radial a negro→estrellas

## Implementación
`assemble.py` ahora acepta por-corte: `tipo[:dur]` (cut, flash, dissolve, iris,
radial, zoom, glitch, pixelize, fade). Así el montaje NO es todo fade.
Sync a música: cuando tengamos onsets del master, los offsets de corte se calzan
a esos tiempos (paso siguiente).
