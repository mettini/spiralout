# AI Video Generation Models — 2026 spec (Spiral Out lens)

> Última actualización: 2026-05-26. Mapa de modelos para generación de video
> usables en Spiral Out (visuales para transmissions, singles, blog graphics).
> Mirado desde lo que NOSOTROS necesitamos: oscurantismo, espacio, planos
> largos, sin humanos, no flickering.

## TL;DR — qué usar para qué

| Caso de uso | Recomendación primaria | Plan B |
|-------------|------------------------|--------|
| Crossing definitivo (13 min, planos largos, espacio) | **Veo 3** (via Google Workspace AI) | LTX-Video local |
| Singles visualizer (45-90s loops, abstracto) | SDXL Turbo img2img (`local_render_diffusers.py`) | AnimateDiff + SDXL |
| Cover-art / still frames | SDXL Base + refiner (`sdxl_base_concept.py`) | SDXL Turbo + img2img refinement |
| Short clips B-roll (5s) para post / social | LTX-Video | Sora 2 (si está aprobado el costo) |
| Blog graphics (still) | SDXL Base / DALL-E 3 | Compose programmatic (PIL) |
| Lyrics / hexagram overlay video | PIL programmatic + Hydra | (no necesita AI) |

---

## Por qué SDXL Turbo no es suficiente para crossing definitivo

Lo usamos en `local_render_diffusers.py` para Recursion y dio un resultado
distintivo (3 min, fosforo verde, planar). Para Crossing (13 min) reveló
3 limitaciones:

1. **Adherencia al negative débil**. Turbo es distillation 4-step → ignora
   muchas indicaciones del negative. Las figuras humanas atravesaron el
   `HUMAN_NEG` reforzado.
2. **No tiene noción de espacio 3D / cámara**. SDXL es text-to-image 2D.
   Cae en composiciones planas (tarot card, album cover, woodcut frame
   centrado) cuando el prompt es vago sobre composición.
3. **Frame-by-frame img2img → flickering**. Cada frame es una imagen
   independiente warped desde la anterior. No hay modelo de video debajo
   → el "scene change" se nota como salto. Reseed-per-scene ayuda pero
   también acentúa el corte.

**Cuándo SÍ usar Turbo**: contenido abstracto sin cámara, planos cortos
(<5s), o cuando el "delirio cambiante" es parte de la estética
(Recursion fue eso: el viaje fragmentado).

---

## Modelos LOCALES (corren en M-series Mac)

### 1. SDXL Turbo (lo que tenemos hoy)

- **Provider**: Stability AI · Hugging Face: `stabilityai/sdxl-turbo`
- **Tipo**: Image diffusion (1 frame at a time)
- **Pesos**: ~7 GB
- **Speed M2/M3 Pro**: ~1.1 s/frame @ 640x360 (4 steps)
- **Resolución nativa**: 512 cuadrado; bueno hasta 1024; degrada arriba
- **Licencia**: Stability Community License (free for non-commercial,
  comerciales ≤$1M revenue OK)
- **Pros**: rápido, validado, scriptable, anti-deriva ya implementado
- **Cons**: planar 2D, weak negative, flicker entre escenas
- **Fit Spiral Out**: Recursion ✓ · Crossing principal ✗ · B-roll abstract ✓

### 2. SDXL Base + Refiner

- **Provider**: Stability AI · `stabilityai/stable-diffusion-xl-base-1.0` + `..-refiner-1.0`
- **Tipo**: Image diffusion (single frame, ALTA calidad)
- **Pesos**: ~14 GB (base + refiner)
- **Speed M2/M3 Pro**: ~30 s/frame @ 1024 (20 steps base + 10 refiner)
- **Resolución nativa**: 1024
- **Pros**: adherencia a prompt MUY superior a Turbo · negative funciona ·
  composición coherente
- **Cons**: 30x más lento que Turbo. Para video frame-a-frame es
  prohibitivo (5 hs por 10 minutos de video @ 12fps).
- **Fit Spiral Out**: cover-art, blog stills, keyframes. NO para video.
- **Ya lo usamos** en `sdxl_base_concept.py` para concepts.

### 3. AnimateDiff + SDXL (motion module)

- **Provider**: Yuwei Guo et al. · GitHub `guoyww/AnimateDiff`
- **Tipo**: Temporal LoRA sobre SDXL — genera CLIPS de 16 frames (~2.6s @ 6fps)
  con consistencia temporal nativa
- **Pesos**: motion module ~1.7 GB + checkpoint SDXL ~7 GB
- **Speed M2/M3 Pro**: ~3-5 min por clip de 16 frames @ 512
- **Resolución**: 512 nativo (768 funciona con artifacts)
- **Pros**: PRIMER nivel de continuidad temporal real local. No flickering
  intra-clip. Reusa LoRAs de SDXL (style transfer).
- **Cons**: Requiere ComfyUI o el wrapper Python. Solo 2-3 sec por clip;
  encadenar clips puede dar saltos entre ellos. Output 512 → resize lossy.
- **Fit Spiral Out**: visualizer singles ✓ · B-roll cortos ✓ · cinema 13 min ⚠
  (necesitaría ~300 clips encadenados).

### 4. LTX-Video (Lightricks)

- **Provider**: Lightricks · Hugging Face: `Lightricks/LTX-Video`
- **Tipo**: Real video model (DiT con video tokens). Text/img → video.
- **Pesos**: ~9 GB
- **Speed M2/M3 Pro**: ~3-5 min por clip de 5s @ 768x512
- **Resolución nativa**: 768x512
- **Pros**: continuidad temporal REAL (no LoRA hack). Rápido para video
  model. Open source. Buena fidelidad a prompts de "void / space / no figures".
- **Cons**: clips de máximo 5s. Para 13 min necesita ~156 clips → ~13 hs
  render local. Encadenado puede tener cortes visibles. Modelo joven, paleta
  saturada por default (necesita prompt + LoRA para "monochrome").
- **Fit Spiral Out**: Crossing definitivo (Plan B) ✓ · singles visualizer ✓ ·
  B-roll PRO ✓.

### 5. CogVideoX-5B-I2V (Zhipu)

- **Provider**: Zhipu AI · `THUDM/CogVideoX-5b-I2V`
- **Tipo**: Real video model, 49 frames (~6s @ 8fps) por clip
- **Pesos**: ~10 GB (5B params)
- **Speed M2/M3 Pro**: ~12-15 min por clip de 6s
- **Pros**: temporal consistency excelente, open source, fidelidad alta
- **Cons**: MUY lento en MPS (sin CUDA optimizations). Para 13 min:
  130 clips × 12 min = 26 hs render local. No viable overnight.
- **Fit Spiral Out**: si se tiene paciencia, clips individuales clave. NO
  para 13 min continuos.

### 6. HunyuanVideo (Tencent) / Wan 2.1 (Alibaba)

- **Provider**: Tencent · `tencent/HunyuanVideo` · Alibaba · `Wan-AI/Wan2.1`
- **Pesos**: 13-14 B params, ~28 GB cada uno
- **Requiere**: >32 GB VRAM (CUDA). Más rápido / mejor calidad SOTA open.
- **Fit Spiral Out**: NO corre en Mac M-series por ahora. Si en algún momento
  alquilamos GPU cloud (Runpod, Lambda Labs), serían el top choice open.

### 7. Stable Video Diffusion (SVD)

- **Provider**: Stability AI · `stabilityai/stable-video-diffusion-img2vid-xt`
- **Tipo**: Image-to-Video — toma una still y le da movimiento (14 / 25 frames)
- **Pesos**: ~9 GB
- **Speed M2/M3 Pro**: ~5-8 min por clip de 4s @ 1024x576
- **Pros**: arranca desde una still APROBADA (nuestro saturn distorted, mandala) y
  le da movimiento. Excelente para "animar nuestros picks sin perder identidad".
- **Cons**: movimiento sutil, no narrativo. El input domina; cambios drásticos
  son raros.
- **Fit Spiral Out**: Animar los picks aprobados sin perder identidad — sweet
  spot que aún no exploramos.

### 8. Deforum (legacy)

- **Provider**: Deforum collective · `deforum-art/deforum-stable-diffusion`
- **Tipo**: Frame-a-frame img2img con motion + keyframes (no es un modelo per se,
  es un PIPELINE sobre SD/SDXL)
- **Cómo lo usamos**: `deforum_settings_*.json` en `transmissions/01/video/ai/`
- **Pros**: control fino sobre motion (zoom, rot, traslación)
- **Cons**: requiere AUTOMATIC1111 GUI; el equivalente local lo hicimos en
  `local_render_diffusers.py`. Comparte limitaciones de Turbo/SDXL (planar,
  flicker).

---

## Modelos COMERCIALES (API / web)

### 9. Veo 3 (Google)

- **Provider**: Google DeepMind · vía Google AI Studio / Gemini API / Google Workspace
- **Tipo**: SOTA text-to-video
- **Speed**: ~1-3 min por clip de 8s @ 720p; ~5-7 min @ 1080p (cloud)
- **Costo**: vía Workspace AI / Vertex AI ~$0.50-2.00 / segundo de video
  (~$390-1560 por 13 min). Workspace Business plan tier tiene cuota incluida.
- **Pros**: PRIMERA opción para "vacío cósmico planos largos sin humanos" —
  el negative FUNCIONA, planos largos son su fuerte. Adherencia al prompt
  excelente. Sonido nativo opcional.
- **Cons**: closed source, costo por uso, ~8s por clip (necesita encadenar
  para piezas largas), licencia comercial vía Google (revisar para uso en
  releases comerciales).
- **Fit Spiral Out**: Crossing definitivo ★★★★★ · cover-art motion ★★★★ ·
  shorts/social ★★★★★

### 10. Sora 2 (OpenAI)

- **Provider**: OpenAI · vía ChatGPT Plus/Pro/Team o API
- **Tipo**: SOTA text-to-video
- **Speed**: ~30s-2min por clip de 5-20s @ 720p/1080p (cloud)
- **Costo**: Pro tier $200/mes (1080p + 20s clips); Plus $20/mes (limits);
  API tier por uso
- **Pros**: calidad de imagen TOP, control sobre cámara estable, planos
  cinematográficos. "Storyboard" mode permite encadenar.
- **Cons**: cap 20s por clip, modelo conservador (rechaza prompts ambiguos),
  watermark visible en tiers gratuitos.
- **Fit Spiral Out**: Crossing alt ★★★★ · singles visualizer ★★★★ ·
  cover art motion ★★★★

### 11. Kling 2.0 / Hailuo MiniMax / Runway Gen-4

- **Provider**: varios (Kuaishou, MiniMax, Runway)
- **Tipo**: text-to-video / img-to-video, clips 5-10s
- **Costo**: ~$30-90/mes para uso decente
- **Pros**: precios accesibles, image-to-video bueno (animar nuestros picks)
- **Cons**: calidad detrás de Veo 3 / Sora 2; estilo "Hollywood AI"
  predominante (cuesta sacar el look black metal / dark ambient)
- **Fit Spiral Out**: si no tenemos Veo/Sora, opción intermedia. Hailuo
  tiene buen "dreamlike abstract" que puede servir.

### 12. Luma Dream Machine

- **Provider**: Luma AI
- **Tipo**: text/img-to-video, 5-9s clips
- **Pros**: rápido, buena coherencia de cámara, tier gratis razonable
- **Cons**: estilo poppy/clean por default; necesita prompt fuerte para
  oscurantismo
- **Fit Spiral Out**: test rápido si Veo no responde para un prompt; cubrir
  emergencias

---

## Decision matrix — qué modelo elegir según objetivo

| Objetivo | Modelo | Por qué |
|----------|--------|---------|
| 13 min cinematográfico, espacio profundo, sin humanos | **Veo 3** | Único modelo donde el negative "no figures, no horizon, no ground" funciona consistentemente |
| 13 min con narrativa esoterica abstracta open source | **LTX-Video** local | Continuidad temporal real, controlable, gratis |
| Animar nuestros picks aprobados (saturn, mandala) | **SVD (Stable Video Diffusion)** | Toma still aprobada y la mueve sin romper identidad |
| Singles 45-90s loops abstractos | **SDXL Turbo** + img2img (ya tenemos) | Validado para Recursion; rápido para iteración |
| Visualizer YouTube 8 min track | **AnimateDiff + SDXL** | Continuidad de 2-3s, encadenable, contenido abstracto va bien |
| Cover art motion para social | **Veo 3** | Calidad pristine para hero shots de 5-8s |
| Concept stills (planeta, ojo, mandala fractal) | **SDXL Base + refiner** | Adherencia y calidad sin temporal constraints |
| Lyrics + hexagram overlay | **PIL programático** (no AI) | Pixel-perfect control |

---

## Notas de licencia para uso comercial (releases pagas)

Antes de subir contenido AI-generated a DistroKid / Bandcamp:

- **SDXL family**: Stability Community License. Permite uso comercial si
  revenue <$1M/año. ÆM clean.
- **AnimateDiff**: Apache 2.0 (motion module). El SDXL underlying mantiene
  su licencia. ÆM clean.
- **LTX-Video**: Open RAIL++. Permite comercial con restrictions normales
  (no contenido ilegal, sin deepfakes humanos). ÆM clean.
- **CogVideoX**: Apache 2.0. ÆM clean.
- **HunyuanVideo / Wan2.1**: revisar Tencent / Alibaba terms para uso
  fuera de Asia. Generalmente OK comerciales con attribution.
- **Veo 3 (Google)**: revisar Workspace Business / Vertex AI commercial use
  clauses. Suele requerir attribution o tier paga.
- **Sora 2 (OpenAI)**: outputs OpenAI son owned by user under their terms;
  permitido comercial en tier paga.

⚠ **Para Heliopause / Transmission 01**: validar los terms para cada
generador antes del release T-day. SDXL Turbo (lo usado en Recursion)
está clean. Si introducimos Veo 3 o Sora 2 para Crossing, leer y guardar
screenshot de los terms del día.

---

## Pipeline propuesto para Spiral Out (mid 2026)

```
                       ┌─────────────────────────────┐
   IDEA / SCENE PROMPT │ Decision matrix arriba      │
                       └────────────┬────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
      LOCAL PIPELINE          COMMERCIAL              ANIMATE PICKS
              │                     │                     │
   SDXL Turbo / AnimateDiff   Veo 3 / Sora 2          SVD
   LTX-Video / CogVideoX                              (img→video)
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                    ┌──────────────────────────────┐
                    │  ffmpeg compose + audio mux  │
                    │  task qa:video (rubric PRO)  │
                    │  → release / upload          │
                    └──────────────────────────────┘
```

---

## Próximos experimentos validados (en queue)

- **PoC #1**: Veo 3 — 1 clip de 8s para "ship approaching ringed planet,
  pure void, no figures" + 1 clip "passing through ring dust" para validar
  adherencia.
- **PoC #2**: LTX-Video local — descargar, generar 1 clip de 5s con el
  mismo prompt, comparar.
- **PoC #3**: Stable Video Diffusion — feed nuestro `saturn distortion`
  pick + ver qué movimiento natural propone.
- **PoC #4**: AnimateDiff — encadenar 5 clips de 2s para validar que
  el join entre clips no rompa la sensación.

Resultados de las PoCs van a `docs/video/10_video_models_poc_results.md`
(a crear cuando tengamos data).

---

## Referencias

- Lightricks LTX-Video paper · 2025
- Stability AI SDXL paper · 2023
- Yuwei Guo et al. — AnimateDiff · 2023
- Tencent HunyuanVideo · 2024
- OpenAI Sora 2 system card · 2025
- Google DeepMind Veo 3 announcement · 2025
- Alibaba Wan 2.1 release · 2025
