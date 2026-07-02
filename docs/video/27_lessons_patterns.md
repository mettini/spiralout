# 27 — Video pipeline: patterns & anti-patterns (lecciones caras)

> Aprendido a los golpes armando los 3 visualizers de Heliopause (fue ~un mes
> con idas y vueltas). Leé esto ANTES de arrancar el próximo video.

## ⭐ La lección #1 (la que costó todo de nuevo)

**Renderizá a 60fps (o 30), NO 24fps, para cualquier cosa con movimiento
lento/suave que se vea en YouTube/navegador.**

- 24fps sobre pantalla de 60Hz → **pulldown 3:2** (frames repartidos 2:3:2:3) →
  **judder** en el movimiento lento. El navegador NO lo maneja (QuickTime local
  sí, por eso engaña: local smooth / YouTube cortado).
- 60fps entra 1:1 en 60Hz y 2:1 en 120Hz → sin pulldown → smooth para todos.
- El "desync" también era esto (frames dropeados por decode desfasan A/V).
- Fix retroactivo: `minterpolate=fps=60:mi_mode=mci` + encode HW
  (`hevc_videotoolbox`, ~6× realtime; software x265 4K60 = ~12h, inviable).

## Patterns (hacer)

1. **Validá en el archivo que la PLATAFORMA sirve, no el local.** El mp4 local
   reproduce cada frame exacto; YouTube re-encodea (AV1/VP9) y el cliente
   decodea → ahí aparecen los problemas. Bajá el servido (`yt-dlp
   --cookies-from-browser chrome <url>`) y MEDÍ (cadencia PTS, diffs
   frame-a-frame) antes de concluir nada.
2. **Diseñá/validá en el CONTEXTO de consumo real:** resolución final, EN
   MOVIMIENTO (no stills), tamaño del feed (thumbnails a 168×94), y en la TV/
   navegador. Casi todos los errores fueron por juzgar en el contexto
   equivocado (still lindo, preview a 640, sin grano).
3. **Anti-banding horneado:** los verdes oscuros bandean con la compresión de
   YouTube. Meté ruido estructural **estático** (low+mid freq, fijo por frame
   para no "pumpear" en los P-frames) + grano fino. Sin grano = banding.
4. **Movimiento atado a la música**, no a números inventados. Derivá la
   velocidad/cadencia del control track (rms/flux). El user midió "la velocidad
   de la música", no adivinó.
5. **Persistí todo fuera de `/tmp`.** `/tmp` se auto-limpia y borró trabajo
   varias veces. Usá un workdir persistente.
6. **Medí un sample antes de un render largo.** Un frame/clip corto te da el
   tiempo real (evita comprometerse a 12h por mala estimación) y valida el look.
7. **Trim final a un pelín POR DEBAJO del segundo redondo** (target − 0.1s):
   YouTube **redondea para arriba** cualquier fracción (480.003s → 8:01).
8. **Esperá el procesado completo de YouTube** antes de juzgar calidad/fluidez,
   sobre todo en TV/cast (el 4K en TV llega ÚLTIMO; videos largos tardan más).
   Un privado con 0 vistas tiene cache frío → más buffering.
9. **QA vos mismo antes de mostrar** (a tamaño/movimiento real). Se le mostró
   basura obvia demasiadas veces (silueta "peón", banding, mush).

## Anti-patterns (NO hacer)

1. ❌ **Renderizar a 24fps para web** (ver lección #1).
2. ❌ **Concluir sobre el comportamiento en YouTube sin ver el archivo servido.**
   Especulé con AV1/priming sin bajarlo — pérdida de tiempo y credibilidad.
3. ❌ **Rabbit holes en un enfoque con mismatch de fondo.** El Mandelbrot: días
   con escape-time (speckle), denoise (popping), DE, slope shading… cuando el
   problema base era que **el detalle fino de un fractal NO se lee en
   movimiento**. Pivoteá temprano (→ Kaliset full-screen, patrón simple que sí
   se lee). Regla: si iterás 3 veces y el problema es estructural, cambiá de
   enfoque, no de parámetro.
4. ❌ **Juzgar movimiento con stills** / calidad final con un test low-res
   sin grano. El banding y el "no se nota el detalle" solo aparecen a escala
   real y en movimiento.
5. ❌ **Borrar antes de confirmar/backupear.** Borré los thumbnails viejos y el
   user quería uno; `rm` no va a la papelera y el dir no estaba en git.
6. ❌ **Usar "el frame más lindo" como thumbnail.** Un thumbnail es diseño para
   el feed (un sujeto, alto contraste, legible chico), no un screenshot. Ver
   `docs/24_thumbnail_guide.md`.
7. ❌ **Estimar tiempos de render sin medir.** Dije 12h/2h/etc. mal varias veces.

## Checklist mínimo para el próximo video

- [ ] Render a **60fps** (o 30). Nunca 24 para YouTube.
- [ ] Anti-banding (ruido estático + grano fino) horneado.
- [ ] Movimiento atado al control track (audio).
- [ ] Workdir persistente (no /tmp).
- [ ] Validar look en 4K + EN MOVIMIENTO antes de escalar.
- [ ] Encode HW (VideoToolbox) para 4K; medir un sample primero.
- [ ] BT.709 (tres tags) — forzar con `setparams` si la fuente viene mistag.
- [ ] Duración = target − 0.1s (que YouTube muestre el minuto redondo).
- [ ] Thumbnails según `docs/24_thumbnail_guide.md`, testeados a 168×94.
- [ ] Subir, **esperar procesado completo**, y validar en el **archivo servido**
      (yt-dlp) + en la TV.

Relacionado: `docs/24_thumbnail_guide.md`, memoria `reference_outbound_*`,
`feedback_no_rabbit_holes_use_my_vision`, `feedback_qa_yourself_before_showing`.
