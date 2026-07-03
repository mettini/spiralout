# Pipeline pro — adopción 2026-06-08 (hybrid Python + DaVinci Resolve)

> Reemplaza el approach DIY de pipe directo Python→ffmpeg. Resuelve el problema
> de banding en YouTube SDR fallback que perseguimos durante Heliopause.

## Por qué cambiamos

Pipeline DIY (Heliopause 2026-05/06):

```
shader.glsl → render Python → rgb48le pipe → ffmpeg HEVC → MP4
```

Pros:
- Code-driven, version controlable, reproducible
- Match ideológico con el framework `aem` (audio code-driven)

Contras (los que nos pagaron caro):
- **Banding inevitable en YouTube SDR fallback** — VP9 8-bit 20Mbps smoothea
  cualquier dither que hagamos a nivel pixel desde shader
- Color management ad-hoc (gamma lift por código, sin OCIO)
- Imposible iterar grade rápido (cada cambio = re-render full)
- No tenemos las herramientas que la industria tunneó por 20 años

## Pipeline pro nuevo

```
shader.glsl → render Python → ProRes 4444 (~700 Mbps, 10-bit, prácticamente sin compresión)
                                      ↓
                              DaVinci Resolve (Free):
                                - color grade (rápido, visual)
                                - Film Grain effect (built-in perceptual)
                                - export YouTube 2160p preset
                                      ↓
                              MP4 final → upload YouTube
```

### Por qué funciona donde DIY falla

**El problema con DIY**: nuestro dither a nivel pixel (shader hash) genera
patrones de muy baja amplitud que VP9 considera "noise eliminable". El
encoder de YouTube lo borra y aparecen bandas.

**Solución pro**: Resolve aplica film grain con DOS propiedades clave:
1. **Patrón perceptualmente diseñado** (no random, distribución blue noise)
2. **Amplitud suficiente** (típicamente 8-20/255) para que el encoder lo
   trate como detalle importante, no como ruido eliminable
3. **Temporal coherence** — el grain tiene patrón temporal natural

VP9 + grain de Resolve preserva el grain porque psy-rd lo identifica como
detalle visual. Los bandas se rompen ANTES de llegar al encoder de YouTube.

## Workflow concreto (per video)

### Step 1 — Render Python a ProRes 4444

Modificar render.py para output ProRes 4444 directo:

```python
args = [
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{W}x{H}", "-r", str(fps),
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "rgb",
    "-i", "-",
    "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
    "-qscale:v", "9",  # quality scale 1-31, 9 = high quality
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-c:a", "pcm_s16le",
    "out.mov",
]
```

Tamaño esperado: ProRes 4444 a 4K @ 30fps = ~700 Mbps = ~5 GB por minuto de
video. Heavy pero es el formato profesional intermedio standard.

### Step 2 — Import a Resolve

1. Abrir DaVinci Resolve Free (free download:
   https://www.blackmagicdesign.com/products/davinciresolve)
2. New Project → name "Heliopause Outbound" etc
3. Media tab → drag ProRes file
4. Project Settings (Shift+9):
   - Timeline format: 3840x2160 30p (outbound) / 24p (crossing/recursion)
   - Color science: DaVinci YRGB Color Managed
   - Output color space: Rec.709 Gamma 2.4

### Step 3 — Apply Film Grain en Color page

1. Edit tab → drag ProRes a timeline
2. Color tab (cog icon)
3. En el node:
   - Open Effects (Shift + Cmd + B)
   - ResolveFX Texture → **"Film Grain"**
   - Drag to clip (or add as node)
4. Grain settings:
   - Preset: **"Kodak 5219 500T"** (35mm popular, balanced)
   - Grain Intensity: 0.40 - 0.60 (suficiente para romper bandas)
   - Saturation: 0.60 (un poco menos saturated)
5. Preview con scrubbing pesado en zonas oscuras (bloom de outbound, partida,
   inicio crossing)

Si grain demasiado visible: bajar intensity. Si bandas aún visibles: subir.

### Step 4 — Deliver

1. Deliver tab
2. Preset: **"YouTube"** (en el sidebar izquierdo)
3. Customize:
   - Resolution: 3840x2160
   - Frame rate: keep source (24, 30 según video)
   - Codec: H.265 (HEVC)
   - Quality: Restrict to **80,000 Kb/s** (80 Mbps)
   - Color profile: Rec.709 Gamma 2.4
4. Add to render queue → start render
5. Output va a la carpeta que configuraste

### Step 5 — Validación con YouTube emulator

Antes de subir, validar:

```bash
cd transmissions/01/video
./youtube_emulate.sh resolve_output.mp4 /tmp/yt_test.webm
.venv_detect/bin/python banding_detect.py /tmp/yt_test.webm
```

Si banded_pct < 0.5% en todos los frames críticos → upload OK.

## Limitaciones del approach

- **Resolve Free tiene limites**: max 60fps en delivery, no Dolby Vision, no
  más de 4 nodos por clip. Para Heliopause con sus 3 videos simples no es
  problema.
- **Workflow manual**: cada video requiere intervención humana en Resolve.
  No es automatizable como el shader Python.
- **ProRes intermedio es heavy**: ~5GB/min. Para Heliopause = ~120 GB total
  (los 3 ProRes + outputs). Ok para SSD libre.

## Research notes Blender para Transmission 02

Para los próximos transmissions queremos considerar Blender como render
engine en vez del shader Python custom. Razones:

1. **Geometry Nodes** — permite procedural composition tipo Houdini pero
   open source. Cosas como el spiral fractal de partida se podrían armar
   visualmente y procedural a la vez.
2. **Cycles/Eevee rendering** — engines pro con OCIO color management
   built-in. Ya no peleamos con color space ad-hoc.
3. **EXR sequence output nativo** — 32-bit float per frame, máxima
   precisión, ningún compromise antes de Resolve.
4. **Shader editor visual** — mantenemos code-driven con scripting Python
   pero podemos prototipar visual.

### Lo que hay que investigar antes de adoptar Blender

- **Audio reactivity en Blender**: ¿drivers desde Python script? ¿bake
  envelope a curva de animación? ¿uso de Sound Sequencer?
- **Performance render Cycles a 4K**: ¿segundos por frame en M3 Max? ¿GPU
  rendering con Metal funciona?
- **Pipeline Blender → ProRes → Resolve**: ¿export EXR sequence o directo
  ProRes desde Blender? ¿qué calidad pierde?
- **Plugins/Add-ons relevantes**:
  - Animation Nodes (procedural)
  - Sverchok (geometry nodes alternative)
  - Audvis (audio reactivity)
- **Learning curve estimada**: 1-2 semanas para tener pipeline básico
  funcionando. 1 mes para fluidez.

### Decisión sobre Transmission 02

- Si T02 quiere visual más procedural/escultórico: empezar con Blender
- Si T02 quiere mantener estética "campos perceptuales tipo Turrell" como
  Heliopause: seguir con Python shader + Resolve híbrido
- Si T02 quiere AI-generated heavy: Veo 3 / Sora 2 + Resolve (ver
  09_ai_video_models_2026.md)

## Referencias

- DaVinci Resolve docs: https://www.blackmagicdesign.com/products/davinciresolve/training
- ResolveFX Film Grain manual: built-in Resolve, también explicado en
  https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_Reference_Manual.pdf
- ProRes 4444 spec: https://support.apple.com/downloads/Apple_ProRes_White_Paper.pdf
- Blender for video: https://docs.blender.org/manual/en/latest/render/index.html
