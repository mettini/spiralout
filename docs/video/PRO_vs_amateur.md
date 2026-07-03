# Qué diferencia un video PRO de uno no-PRO

> Doc base. Antes de medir un output con la rúbrica QA, hay que tener claro
> contra qué se mide. Esto no es opinión — son atributos verificables que
> distinguen el trabajo PRO del amateur, recogidos de las categorías reales
> de la industria. Si querés que algo se vea PRO, tiene que cumplir estos.
>
> Última actualización: 2026-05-25 (después de aceptar que mis 4 maquetas
> anteriores eran amateur, no PRO).

---

## 0 · Categorías de "PRO" — no es una sola cosa

| Categoría | Referencia | Características clave |
|-----------|------------|------------------------|
| **VFX Hollywood** | Interstellar, Gravity, Marvel | Equipos de 100+ artistas, millones USD, render farms, meses por shot |
| **Comercial / Motion Graphics** | Apple ads, brand films | Agencias, 2-6 semanas por proyecto, motion design + grading |
| **Music video / VJ touring** | Anyma, Tame Impala, JJUUJJUU, Lustmord live | 1-5 artistas, 1-6 meses, mezcla generativo + custom |
| **Visionary digital art** | Android Jones, Refik Anadol, Beeple | 1 artista, herramientas custom, look único como firma |
| **Demoscene / generative code** | Inigo Quilez, Cabbibo, Shadertoy stars | 1 coder, virtuosismo matemático puro, <10KB code |
| **AI video pro** | Sora, Gen-3 con prompt engineering pulido | Curation + dirección + post |

Nuestro target realista para Spiral Out: **algo entre demoscene + VJ touring + visionary digital art**. NO Hollywood VFX (no podemos). NO comercial (no es el mood).

Eso significa: virtuosismo matemático + voz autoral + sync con música = el target.

---

## 1 · Atributos universales de PRO (aplican a TODAS las categorías)

### 1.1 **Lighting** — luz que se siente física
- **Amateur**: ambient + 1 key light. La esfera tiene un highlight blanco y una sombra plana.
- **PRO**:
  - **3-point lighting** o más (key, fill, rim, kicker).
  - **Subsurface scattering** en materiales orgánicos (piel, cera, polvo): luz que penetra y sale por otro lado.
  - **Global illumination**: bounce light (un objeto rojo cerca de una pared blanca → tinge la pared).
  - **Volumetric lighting**: rayos de luz visibles a través de niebla/polvo (god rays). En espacio: scattering atmosférico de anillos.
  - **Area lights** no point lights — sombras suaves de fuentes con extensión.
  - **Light wrap**: el borde iluminado se "envuelve" sobre el sujeto, no es un corte duro.

### 1.2 **Materiales (PBR — Physically Based Rendering)**
- **Amateur**: diffuse color sólido o noise plano.
- **PRO**:
  - **Albedo + Roughness + Metallic + Normal + Displacement** maps independientes.
  - **Anisotropy** en materiales con grano (madera, metal cepillado).
  - **Fresnel** (reflectancia varía con ángulo).
  - **Subsurface** en lo orgánico.
  - Materiales reaccionan a luz CORRECTAMENTE: un anillo de partículas catching light DEL OTRO LADO se ve translúcido.

### 1.3 **Detail density a múltiples escalas (fractal detail)**
- **Amateur**: blob suave a una sola escala. Zoom 200% = aún el mismo blob.
- **PRO**:
  - Detalle visible a 4 escalas: macro (silueta), medio (formas), micro (textura), nano (grano).
  - Cada escala tiene su propia variación, no es uniforme.
  - Megascans / photogrammetry: rocas reales tienen detalle a sub-mm escala visible en close-up.

### 1.4 **Composition** — el frame es deliberado
- **Amateur**: sujeto al centro, simétrico, no hay foreground/background.
- **PRO**:
  - **Rule of thirds** o golden ratio para subject placement.
  - **Foreground / midground / background** distintos, con parallax al mover cámara.
  - **Leading lines**, framing, negative space intencional.
  - El ojo del espectador se guía con luz, contraste, foco.

### 1.5 **Color grading**
- **Amateur**: colores raw del render. Saturación uniforme. Cada frame tiene paleta distinta.
- **PRO**:
  - **LUT cinematográfico** consistente (teal+orange, bleach bypass, cross-processed, etc.).
  - **Film emulation**: Kodak Vision3, Fuji Eterna, etc. Da grano específico + curva tonal.
  - **Color story por shot**: cada escena tiene 2-3 colores principales que evolucionan con la narrativa.
  - **Black point lift + roll-off**: nunca negro puro (#000) — siempre hay algo. Igual con blancos.

### 1.6 **Camera motion**
- **Amateur**: cámara estática o movimiento lineal predictible.
- **PRO**:
  - **Parallax real** entre layers de profundidad.
  - **Handheld jitter** (microvibration) cuando aplica → más orgánico.
  - **Lens-physics**: focal length, perspective distortion, breathing en focus pulls.
  - **Motion blur PER-PIXEL** basado en velocity vectors (no blur uniforme).
  - **Easing curves** (no lineal — cubic, ease-in-out, anticipation).

### 1.7 **Depth of field (DoF)**
- **Amateur**: todo en foco siempre, o blur uniforme.
- **PRO**:
  - **Lens-physics DoF**: falloff que sigue la ecuación del círculo de confusión.
  - **Bokeh shape** depende de la apertura (5/6/7/8 lados según diafragma).
  - **Chromatic aberration** en el círculo de confusión: cyan adentro, magenta afuera del bokeh.
  - **Focus pulls** que mantienen anclaje narrativo.

### 1.8 **Post-processing pipeline**
- **Amateur**: render directo, sin post.
- **PRO** (multi-pass):
  1. **Bloom** (multi-pass downsample/upsample, no single-shader fake).
  2. **Lens flares** (anamorphic stretch + ghosts + halation).
  3. **Chromatic aberration** wavelength-realistic.
  4. **Film grain** con respuesta del stock de film.
  5. **Vignette** lens-physics (no smoothstep flat).
  6. **Sharpening** lens-aware (no global unsharp mask).
  7. **Color grading** (LUT final).
  8. **Letterboxing** si aplica (2.39:1 cinemascope).

### 1.9 **Atmosphere / volumetrics**
- **Amateur**: void vacío entre objects.
- **PRO**:
  - **Volumetric fog/dust** entre cámara y sujeto.
  - **God rays** (light shafts a través de geometry).
  - **Atmospheric scattering** (Mie + Rayleigh) para skies.
  - **Particulate systems**: miles/millones de partículas con física, no 6 hash-dots.

### 1.10 **Temporal coherence / motion blur**
- **Amateur**: cada frame es independiente, frames flicker porque noise random.
- **PRO**:
  - **Temporal anti-aliasing (TAA)**: smoothing entre frames.
  - **Motion blur per-pixel** integrado en velocity buffer.
  - **24fps cinemático** con shutter angle 180° para natural blur (no 30/60fps stiff).
  - **Noise estable**: blue noise stratified, no random hash que parpadea.

### 1.11 **Concept clarity / artistic voice**
- **Amateur**: ejercicio técnico sin razón. "Hice un shader que hace X."
- **PRO**: cada visual sirve un concepto narrativo o emocional claro. Hay POR QUÉ es así.

### 1.12 **Layer count / complejidad de composición**
- **Amateur**: 1-3 capas (sujeto + fondo + grano).
- **PRO**: 20-50 capas (sujeto + lights + atmosphere + lens dirt + flares + grain + chromatic + bloom + LUT + vignette + dust + ghosts + ...).

### 1.13 **Anti-aliasing y edges**
- **Amateur**: bordes pixelados, jaggies visibles en bordes diagonales.
- **PRO**: MSAA 4x+, super-sampling (render a 2x y downsample), TAA. Bordes nunca aliasean.

### 1.14 **Iteración / craft**
- **Amateur**: primer output que parece OK = ship it.
- **PRO**: 10-100 iteraciones, micro-ajustes, comparison frames, feedback loops.

---

## 2 · Atributos específicos para video abstracto/generativo (nuestro caso)

Para demoscene / VJ / visionary art, además de los universales:

### 2.1 **Variación dentro de la estructura**
- No tiene que ser narrativo, pero **algo cambia constantemente** a múltiples escalas temporales: micro (frame a frame), meso (cada 5-10s), macro (cada 30-60s).

### 2.2 **Reactividad al audio (cuando aplica)**
- Cada onset audible tiene reflejo visual SINCRO (≤1 frame de delay).
- Cada banda espectral del audio tiene su mapeo visual.
- No es solo "scale crece con RMS" — es "el bell de 220Hz hace que SOLO el anillo dorado pulse".

### 2.3 **Iconografía clara pero abstracta**
- El espectador tiene **algo a lo que agarrarse**: un punto focal, una forma recognible, un movimiento característico.
- Pero NO es ilustración literal. Es sugerencia.

### 2.4 **Loops seamless**
- VJ visuals deben loopear sin costura visible.
- El último frame conecta con el primero.

### 2.5 **Stage-readability**
- En vivo en escenario grande: el visual aguanta a 30m de distancia.
- Saturación + contraste suficiente para no perderse contra luces de stage.

### 2.6 **Signature style**
- El estilo es reconocible. Si vieras 5 frames en Twitter sin contexto, identificarías al artista.

---

## 3 · Aplicación a nuestros 4 elementos de crossing

### Saturn approach
**Referencia PRO**: *Interstellar* approach a Gargantua (Double Negative + DNEG VFX). *2001 A Space Odyssey* (Trumbull slit-scan + practical effects).

**Atributos que mi versión actual NO tiene**:
- ❌ Volumetric atmospheric scattering en los anillos (los anillos catching backlight = brilla sutil).
- ❌ Particles (anillos como millones de granitos, no toros sólidos).
- ❌ Photogrammetry o normal maps en el planeta (banded gases REALES, no noise crudo).
- ❌ Lens flare anamorphic cuando el sol pasa cerca del borde.
- ❌ Cinematic color grade (teal/orange shadows + warm rim).
- ❌ DoF real (planet sharp, background stars con blur sutil).
- ❌ Composición rule-of-thirds (en mi versión está centrado plano).

**Qué la haría PRO**:
1. Blender Cycles + asset de Saturn con texturas 8K + ring particle system + HDRI stars.
2. O: shader raymarched con volumetric scattering en los anillos + post multi-pass (bloom + flare + grade).

### Stones
**Referencia PRO**: *Gravity* (2013) debris scenes (Framestore VFX). *The Expanse* asteroid sequences.

**Atributos que falta**:
- ❌ Geometry real (photogrammetry → rocas con cada detalle a milímetros).
- ❌ PBR materials (rough, normal, displacement maps).
- ❌ Motion blur per-pixel correcto.
- ❌ Volumetric dust + god rays a través del cluster.
- ❌ Lens optics: focal length apropiado, perspective real (no mi proyección genérica).
- ❌ Cada roca girando con momentum diferente (no todas igual).

**Qué la haría PRO**:
1. Blender + Megascans rocks + rigid body sim + Cycles render + post.
2. O: shader avanzado con triplanar texturing + motion vectors + DoF.

### Bokeh lights
**Referencia PRO**: cualquier comercial de Apple/Nike. *In the Mood for Love* (Christopher Doyle cinematography). Anyma touring bokeh layers.

**Atributos que falta** (lo mío era un chiste):
- ❌ Anisotropic bokeh shape (cat-eye, hexagonal según iris blades).
- ❌ Spectral chromatic aberration (no solo R↔B, todo el espectro).
- ❌ Ghosts del lens (orbs reflejados de cada elemento del lens).
- ❌ Halation (el highlight sangrа en rojo en el borde de luz brillante — emulación de film).
- ❌ Sensor noise apropiado al stock.
- ❌ Animación tipo focus pull real, no pulse random.

**Qué la haría PRO**:
1. Stock footage REAL de bokeh anamorphic 4K (Pexels, Pond5) → compositar.
2. O: shader proper con lens-physics + multi-element ghost + halation.

### Mandala
**Referencia PRO**: Android Jones digital art. Alex Grey paintings. Anyma Visionary mandalas (Eternity tour).

**Atributos que falta**:
- ❌ 3D depth (no flat 2D KIFS).
- ❌ Color theory deliberate (no `mix(c1, c2, smoothstep)` random).
- ❌ Multi-pass post: bloom + chroma + grade separados.
- ❌ Animación con "respiración" (dilatación lenta + onsets).
- ❌ Resolución del detalle (KIFS profundo, no 7 iteraciones).

**Qué la haría PRO**:
1. 3D KIFS raymarched + multi-pass post + LUT.
2. O: AI generative (StyleGAN trained on mandalas) con prompt curado.

---

## 4 · Tools que diferencian PRO de amateur

| Need | Amateur uses | PRO uses |
|------|-------------|----------|
| 3D objects | SDF en shader | Blender Cycles / Houdini + photogrammetry |
| Materials | flat color | Substance Painter / Designer + PBR maps |
| Particles | hash-dots | Blender particle system / Houdini |
| Lighting | ambient + key | HDRI + area lights + volumetrics |
| Color grade | nada | DaVinci Resolve + LUTs |
| Post | shader inline | Nuke / AE multi-pass |
| AI video | random prompts | Curated prompts + img2vid (SVD/Runway Gen-3) + multi-shot |
| Stock | nada | Pexels / Pond5 / Storyblocks 4K |
| Compositing | none | Nuke / Fusion / AE |

---

## 5 · Mi escala honesta de calidad

```
[1] random shader experiment ← donde estaban mis 4 maquetas
[2] decent indie demo
[3] good VJ amateur
[4] solid Shadertoy regular
[5] published Shadertoy / cabbibo level
[6] festival selection demoscene
[7] commercial / brand spot
[8] mid-tier VJ touring (small acts)
[9] high-end VJ (Anyma, Refik Anadol, Tame Impala)
[10] Hollywood VFX
```

Spiral Out target realista: **6-8**. Eso ya es 5-6 niveles arriba de donde estaban mis maquetas.

---

## 6 · Implicaciones para nuestro stack

Para subir 5 niveles desde donde estaba (nivel 1) a target (6-8), las opciones reales:

### Opción A — Blender Cycles + assets reales
- **Pro**: free, local, calidad realmente cinematográfica posible.
- **Costo**: 4-8 hours setup por escena + 30-120 min render por shot.
- **Skill**: requiere conocer Blender's node graph + materials + lighting.

### Opción B — AI video models
- **SVD local**: gratis pero img2vid limitado (2-4 segundos).
- **RunwayML Gen-3 / Luma / Pika**: pagos pero calidad cinematográfica out-of-the-box.
- **Pro**: rápido (minutos por clip).
- **Contra**: sub o créditos pagados, control limitado, tendencia a "AI uncanny".

### Opción C — Stock footage + compositing
- **Pro**: realismo garantizado (es real footage), rápido.
- **Contra**: menos único, requiere AE/DaVinci/Resolve.

### Opción D — GLSL multi-pass avanzado + post-process pipeline
- **Pro**: queda en el repo, reproducible.
- **Costo**: 8-16 horas por shader PRO (ej: volumetric raymarcher con multi-pass post).
- **Skill**: conocimiento avanzado de math/lighting/post.

### Stack recomendado para crossing 3er concepto:
- **Saturn**: Blender (assets+lighting+Cycles) → mp4 → Hydra composer
- **Stones**: Blender (Megascans + sim) → mp4 → Hydra composer
- **Bokeh**: Stock 4K real bokeh footage → DaVinci color grade → Hydra composer
- **Mandala**: GLSL multi-pass advanced (worth doing in code, único)
- **Composer**: Hydra carga 4 mp4 como s0-s3 + audio reactive

---

## 7 · Conclusión

Mi rúbrica anterior pasaba cosas nivel 1 como PRO porque no tenía referencias concretas. La nueva rúbrica DEBE:

1. Antes de validar un output, mostrar **lado a lado** con frame de referencia PRO real.
2. Pasar SOLO si supera nivel 6 en mi escala honesta.
3. Si no llega: **no mostrar, decir "no llegué"** y proponer fix con la opción A/B/C/D específica.

El próximo paso es definir el QA actualizado con benchmarks visuales y un proceso de comparación. Eso es lo que vamos a hacer juntos.
