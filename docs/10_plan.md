# Pendientes y plan de ejecución

Lista viva, crece a medida que aparecen cosas.

## En curso
- Escuchar `outbound_FULL.wav` y dar feedback / iterar.
- Producir *Crossing* (13:00) y *Recursion* (21:00) con el engine.

## Hecho
- Arte de tapa **FINAL** ✓ — versión refinada con AI gen externa (Concept G CRT + wireframe landscape + envejecimiento). Guardar el archivo de alta calidad en `My First Album/04_arte_FINAL.png` cuando esté.
- **Outbound full track v0** ✓ — 8:00 renderizado (`out/outbound/master/outbound_FULL.wav` + stems en `out/outbound/stems/outbound_FULL/`). Pendiente de feedback / iteración.
- **Reorganización del repo** ✓ — `framework/aem/` modular, `tracks/<tema>/`, `out/`, `player/` con UI debug, `docs/` con conceptos. `Taskfile.yml` para los comandos comunes.
- **Skill `aem-composer`** ✓ — `.claude/skills/aem-composer/SKILL.md` codifica el knowledge de composición ambient/cinematic (técnicas de Eno/Roach/Stars of the Lid/Zimmer/Lustmord/Dune + lessons learned del feedback). Reglas de oro (R1-R10), técnicas de transición (T1-T9), anti-patterns (AP1-AP11), mapping feedback→fix, paletas por tema. Checklist de QA. Se aplica automáticamente cuando se trabaja en composición.
- **Estructura `transmissions/<NN>/`** ✓ — cada transmission del artista tiene su carpeta con `themes/<tema>/{arrangement,compose,prototypes,finals}` + `out/` (cache de renders). Transmission 01 = release inicial 24 min (8+13+3) en lugar de 42 (Fibonacci visión).
- **Outbound v1 final** ✓ — snapshot en `transmissions/01/themes/outbound/finals/v1/`.
- **Crossing — 3 prototipos** ✓ — DARK MASS (Lustmord-style), DUNE CHANT (vocal grave protagonista), VOID DRIFT (passing objects + heart beat suave). 90s c/u en `transmissions/01/themes/crossing/prototypes/`. Storyboard del tema completo en `arrangement.md`.

## Próximo
- **Domain**: buscar uno copado para el artista o para un studio. Ideas a explorar:
  - `spiraloutmusic.com` / `spiraloutstudio.com` (*spiral out* es además guiño a Tool — *Lateralus*).
  - `aem.space` / `aem.fm` / `aem.audio`.
  - `transmission01.com` (escalable: `02`, `03`...).
  - `heliopause.fm`.
  - `æm.space` (con la ligadura, si los IDN lo permiten).
  - Decidir si va por **artista** (`aem.*`) o **studio** (`spiralout.*`) o ambos.
  - Verificar disponibilidad en Namecheap / Cloudflare cuando lo abordemos.
- Producir *Crossing* y *Recursion* con el engine (mismos paths conceptuales que se decidan en Outbound).
- Bajar samples reales: Voyager Golden Record (archive.org, dominio público), CMB radiation (freesound.org).

## Más adelante
- Plan de publicación: Spotify, Bandcamp, Apple Music, SoundCloud.
- Sitio web minimalista (estética panel de control de tierra).
- Plan de lanzamiento / promo.
- Transmisión 02 (cuando haya algo que reportar).

## Decisiones abiertas
- Path final del Outbound (v0 / v1 / v2).
- Tipografía exacta de la tapa (Berkeley Mono / JetBrains / IBM Plex Mono).
- Dominio definitivo.
- Estrategia de release: drop directo o teaser previo.
