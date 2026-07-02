# 24 — Guía de thumbnails (YouTube / visualizers)

> Knowledge del proyecto. Cómo hacer un thumbnail que **funcione** (que se
> entienda y llame en el feed), no solo un frame lindo del video.
> Aprendido a los golpes con los visualizers de Heliopause.

## La regla madre

**Un sujeto. Un mensaje. Un segundo.** Si a tamaño de estampilla no se
entiende de qué es en 1 segundo, no sirve — por más lindo que sea grande.

## El test que manda (hacelo SIEMPRE antes de guardar)

Reducí el thumbnail a **168×94 px** (el tamaño real en el feed mobile, donde
pasa el 63% del watch time). Miralo así de chico:
- ¿Se lee al toque qué es? ¿Hay UN foco claro?
- Si es un manchón/mush o no sabés dónde mirar → **rehacer**.

## Los ABC

1. **Un solo sujeto dominante.** Que **llene el frame**. Sacá todo lo demás.
   Máximo **2-3 elementos**. A tamaño chico, 4+ elementos = caos.
2. **Alto contraste.** Sujeto brillante/saturado contra fondo oscuro/neutro.
   El contraste es lo que hace que el ojo no lo pueda ignorar a 120px.
3. **NADA de detalle fino.** Fractales/campos densos (Kaliset, Mandelbrot
   full) se hacen **mush** en chico y **no aportan** — el detalle infinito NO
   se lee. Usá una **forma grande y simple**, no una textura.
4. **Composición limpia.** Sujeto centrado o en tercios, con aire (negative
   space). No lo llenes.
5. **Consistencia de serie.** Los N videos de un release comparten un
   **template** (misma composición, mismos colores de marca, mismo trato) →
   se reconocen como set y entrenan al ojo del público. Marca > variedad.
6. **Legibilidad > fidelidad al video.** El thumbnail no tiene que ser un
   frame exacto: podés recortar, agrandar el sujeto, subir contraste/brillo,
   oscurecer el fondo. Es una pieza de diseño, no un screenshot.

## Specs técnicos

- **1280×720** mínimo (16:9). Exportar **1920×1080**, `.jpg`, **< 2 MB**.
- Dejá **libre la esquina inferior-derecha** (ahí va el timer del video).
- Nada crítico en los bordes (se recorta según UI).

## Cómo lo aplicamos en Spiral Out / Heliopause

- Identidad = **verde anegrado / fósforo**, oscuro y grim. PERO el thumbnail
  necesita **empujar contraste y brillo en el sujeto** para que popee chico
  (el grim puro del video no popea en el feed).
- **Set de la trilogía**: cada track = **UNA forma cósmica central, grande y
  simple**, sobre fondo oscuro, con un acento brillante:
  - **Outbound** → el óvulo/planeta (una esfera).
  - **Crossing** → una sola forma fuerte (portal / silueta), NO el campo
    Kaliset lleno de detalle.
  - **Recursion** → el anillo/mandala (una forma concéntrica).
- Misma composición (sujeto centrado, aire, viñeta oscura) para que se lean
  como trilogía.

## Proceso paso a paso

1. Scrubear el video buscando frames con **una forma dominante simple** (no
   texturas densas).
2. Recortar/componer centrado, con aire.
3. Subir contraste + saturación + brillo del sujeto; oscurecer/viñetear el
   fondo para separar.
4. **Reducir a 168×94 y verificar.** Iterar hasta que a ese tamaño se lea
   claro y con foco.
5. Chequear que los N del set se vean como familia.

## Anti-patrones (lo que ya nos falló)

- ❌ Campo fractal/kaleidoscópico completo (Kaliset/Mandelbrot) → mush en chico.
- ❌ Frame oscuro/monocromo sin foco → no popea, no se sabe dónde mirar.
- ❌ Muchos elementos compitiendo.
- ❌ Usar "el frame más lindo" en vez de diseñar para el tamaño real del feed.

Relacionado: `docs/13_visual_style_guide.md`, `docs/14_design_system.md`,
thumbnails en `transmissions/01/artwork/youtube_thumbnails/`.
