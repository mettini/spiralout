# 31 — Plan de difusión (ÆM / Heliopause) — MASTER

> El plan ordenado y realista para mover el proyecto, dimensionado al apetito
> real: **hacer lo "de manual" para que se mueva algo, pagar poco, y que las
> redes corran casi solas.** Nada de grind. Ejecución detallada de Reddit +
> YouTube ads → `docs/32`. Voz/textos → `transmissions/01/release/textos.md`.
> Actualizado 2026-07-09.

---

## 0. Principio rector
ÆM es **faceless** y **dripea sin calendario rígido** (sin "out now", sin
agradecimientos, sin rogar). "Sin calendario" ≠ "sin plan": hay **banco de
contenido** + **cadencia flexible** + **automatización**. La marca es el
misterio; el plan es interno.

## 1. Expectativas honestas (leer antes de esperar nada)
Proyecto **nuevo, faceless, de nicho, ~0 seguidores**. La verdad:
- Esto es **lento y de nicho**. No se busca viralidad.
- El **ambient NO explota en IG** — vive en **Bandcamp / YouTube / Spotify /
  Reddit**. IG es **canal de APOYO** (presencia + algún Reel que pegue), no el motor.
- **El motor real** = (a) estar **bien plantado/encontrable**, (b) **reach pago
  dirigido al nicho** (YouTube), (c) **participación en comunidad** (Reddit/Discord).
- Objetivo del user: dejar todo "de manual" hecho + un poco de ads + posteo
  automatizado. Movimiento modesto y sostenible, sin aspirar a más.

## 2. Las 3 formas de "mover" (no se mezclan)
- **Pago** (plata, poco esfuerzo): YouTube ads, IG boost, Reddit ads.
- **Orgánico MANUAL** (gratis, pero tiempo semanal): comentar Reddit 9:1,
  Discord, responder IG. *"Agregar gente"/follow-for-follow = spam, se descarta.*
- **Orgánico AUTOMATIZADO** (gratis, se setea una vez): postear con scheduler.
  **← lo que más se usa acá.**

## 3. El plan ordenado (UNA cosa a la vez)
1. **Foundation** — dejar la info "de manual" completa en todos lados. *(§4)*
2. **Ads** — pago dirigido, budget chico, una prueba por mes. *(§5)*
3. **Posteo automatizado** — el content bank goteando solo. *(§6)*
4. **Reddit/comunidad** — opcional, **último paso**, si hay ganas. *(§7)*

---

## 4. Paso 1 — Foundation (qué falta)
Lo pesado ya está: MusicBrainz ✅, Spotify Canvas ✅, press kit + one-sheet ✅,
tags Bandcamp ✅, Amazon for Artists ✅, clips + captions ✅.

Falta:
| Item | Quién | Nota |
|---|---|---|
| **Wikidata** (3 items) | user (Claude guía) | campos + MBIDs listos en `docs/26 §B` |
| **Last.fm** artist page (bio+tags+links) | user | ya se puede (streaming + MusicBrainz live) |
| **IG ÆM** — setup Creator | user | habilita posteo + (futuro) boost |
| Dossiers modo C *(opcional, contenido)* | Claude | espectrogramas/coordenadas |

## 5. Paso 2 — Ads (pago)
**Budget: ≤ $50/mes.** Regla de oro con poco budget: **UNA prueba por mes,
medir, quedarse con lo que rinde.** Probar todo junto = no se aprende nada.

### Rotación de pruebas
| Mes | Prueba | Budget | Medir |
|---|---|---|---|
| 1 | **YouTube discovery** (in-feed) | $50 (~$1.5/día) | views, CPV, watch-time, subs + **¿sube streaming en Spotify?** |
| 2 | según datos: doblar YouTube, o IG boost (si IG ya postea) | $50 | ídem |
| 3 | el que mejor rindió (o Discovery Mode, sin cash) | $50 | ídem |

### Por qué YouTube primero (y solo)
- Tenemos los **3 visualizers 4K** = mejor asset. El anuncio ES contenido.
- Targeting fino por **canales/artistas similares** (Lustmord, Cryo Chamber,
  Roach) — precisión que IG no da para nicho.
- Alimenta las **recomendaciones orgánicas** de YouTube.
- Setup + targeting + copy → `docs/32 §B`. Claude arma, user corre en Google Ads.

### Spotify pago: NO todavía
- **Marquee** (~$250+ mín) y **Showcase**: fuera de budget + necesitan volumen de
  streaming que no hay.
- **Discovery Mode**: sin cash (canje de regalías), pero solo sirve con play
  algorítmico existente → **prueba para más adelante**.
- Pitch de playlists pagas de terceros = scam/valor bajo → **skip**.
- Spotify se mueve cuando YouTube/orgánico le empuje streams.

### IG boost: NO todavía
- Boostear cuenta nueva/vacía = tirar plata. Rinde amplificando un Reel que **ya
  tiene tracción**. Se evalúa en mes 2-3 si un post pega.

## 6. Paso 3 — Posteo (automatizado)
### Realidad de IG con 0 followers
- **Feed posts** → alcance ~0 orgánico. Sirven como **galería** (que el perfil se
  vea vivo/legítimo cuando alguien entra desde YouTube/links/reseña).
- **Reels** → **el ÚNICO formato que llega a no-seguidores** (algoritmo por
  interés + hashtags `#darkambient #ambientmusic #drone`). **La prioridad.**
- **Stories** → solo las ven followers → con 0, alcance 0. **Skip hasta tener followers.**

### Qué se postea
- **Reels** = los 3 clips (visualizers limpios), espaciados. Captación.
- **Feed** = fragmentos modo B (font Atari CRT sobre fondo plano) — galería.
- **Stories** = no, por ahora.
- **Texto** = en la **descripción/caption**, NUNCA sobre el video (decidido 2026-07-09).

### Cadencia y volumen (dimensionado real)
- **~1 post/semana** (canal de apoyo, no hace falta más).
- **~12 posts / 3 meses** = **3 Reels** (los clips) + **~9 feed** (fragmentos/dossiers).

### Automatización
- Claude produce los ~9 posts de feed + captions + calendario (`docs/33`).
- User conecta IG (Business/Creator) a un **scheduler free** (Metricool o Buffer)
  y **carga la cola** → postea solo. Se setea una vez. (Ver `docs/23`.)

### Los 3 modos de post (de `textos.md §6`)
- **A** anotación marginal (fragmento manuscrito/máquina sobre papel).
- **B** fragmento de transmisión (frase en font Atari CRT sobre fondo plano). ← backbone del feed.
- **C** ficha técnica / dossier (espectrograma, coordenadas, timestamps — "leaks").

## 7. Paso 4 — Reddit / comunidad (opcional, ÚLTIMO)
- Es **orgánico MANUAL** (gratis, pero tiempo semanal). El user quiere
  explorarlo, pero al final y sin obligación.
- Plan detallado (subs, regla 9:1, timeline, cómo compartir) → `docs/32 §A`.
- Si no hay ganas de la rutina, se hace lo mínimo (un par de posts bien puestos)
  o se saltea. No es el foco.

---

## 8. Content bank (inventario)
- **13 fragmentos** cifrados ES+EN (`textos.md §4`) → captions + posts modo B.
- **3 clips** verticales LIMPIOS (`out/clip_*.mp4`) → Reels. ✅
- **3 Canvas** (`out/canvas_*.mp4`) → Spotify (subidos) / posibles loops. ✅
- **Crops foto press** (marca hexagrama) ✅ · **cover** ✅ · **hexagram** ✅ ·
  fondos painterly.
- **Dossiers modo C** → por producir (Claude).

## 9. Métricas (para saber qué funciona)
- **YouTube Ads**: views, CPV, view rate, watch-time, earned actions (subs/likes).
- **Spotify for Artists**: streams, saves, listeners en la ventana de cada prueba.
- **La pregunta clave por prueba**: ¿el gasto/acción **movió el streaming**? Si no,
  se descarta y se prueba otra cosa. Disciplina = una variable por vez.

## 10. Estado / próximo
- **Ahora**: producir los ~9 posts de feed + captions + calendario `docs/33`
  (Claude) · Wikidata (user, `docs/26 §B`).
- Después: setear scheduler + cargar cola · correr YouTube ads mes 1 · medir.
