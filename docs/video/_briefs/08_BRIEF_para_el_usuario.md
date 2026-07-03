# Brief — qué corre detrás de cada video (no-vibe edition)

> El doc largo está en `07_video_stack_per_track.md`. Esto es lo concreto en
> 2 páginas: qué hace cada track, por qué, y qué controlamos.

---

## Los 3 tracks usan 3 stacks distintos

Por diseño, no por accident. Cada tema necesita un tipo de imagen distinto:

| Track | Stack | Modelo / motor | Razón |
|-------|-------|----------------|-------|
| **1-outbound** | Python + shader GLSL | OpenGL 4.1 (moderngl), 100% código nuestro | Determinista, controlable frame a frame, ideal para los 8 min "delirio + túnel + mandala" |
| **2-crossing** | Hydra (live-coding) | Hydra-synth + headless-gl (Node) | Textura orgánica de 13 min sin formas claras — exactamente lo que pediste para "desorientar" |
| **3-recursion** | AI local (Stable Diffusion) | `stabilityai/sdxl-turbo` corriendo en MPS (M3 Max) | Look pictórico abstracto que el shader no puede dar; 3 min cortos lo hacen viable (45 min de render) |

---

## Qué controla cada uno

### 1-outbound (shader)

**Lo que decidís vos**: el storyboard (`SCENES_OUTBOUND` en `render.py`). Es
un dict con keyframes — `[(t0, valor0), (t1, valor1), ...]` — uno por
parámetro (decay, zoom, rot, color, mandala-N, etc.).

**Lo que decide el audio**: dentro de cada keyframe, el audio modula el
parámetro en vivo (ej: el bombo dilata la pupila, el aire mueve el polvo).

**Lo que arreglamos hoy** (la franja rosa horizontal):
- La fórmula del hue (color) usaba `ang` directo, que salta de +π a -π en el
  eje horizontal izquierdo → pintaba una franja. Cambiado a `cos(ang)` que
  es continuo. **Sin franja.**
- El kaleidoscopio (la mandala) usaba N fraccionario en transiciones (ej:
  N=8.7 entre keyframes N=10 → N=6). El fold no encaja con N fraccionario y
  deja costura. Ahora se redondea a entero. **Sin costura.**
- Además rotamos lentamente la fase del kaleidoscopio para que las costuras
  residuales no se acumulen siempre en el mismo eje.

### 2-crossing (Hydra)

**Lo que decidís vos**: el "patch" (un archivo `.js` de ~400 líneas) con 7
escenas (CAOS → DESORIENTACIÓN → LAVA → RELÁMPAGOS → RAYAS → STARGATE →
SALIDA). Cada escena es una cadena de operaciones Hydra: noise, modulate,
rotate, blend, color, etc.

**Lo que decide el audio**: `a.fft[0..3]` (SUB/LOW/MID/HIGH) inyectado del
control track. Cada parámetro de cada escena puede ser una función:
`brightness(() => -0.2 + a.fft[3] * 0.4)`.

**Lo que cambiamos hoy** (lava antes + intro caótico):
- **Lava (escena INVERSIÓN) movida de 6:30 → 4:50** y ampliada (180 s vs 80
  s antes). Lo que te gustó está más temprano y dura más.
- **Escenas 1 y 2 reemplazadas**. Antes era bruma + polvo + nébula + tropezones
  (calmo, formas visibles). Ahora son:
  - **CAOS** (0–140 s): polvo en la cara, `noise()` alta freq, `scale(>1)`
    con feedback fuerte = motion trails radiales. Sin formas.
  - **DESORIENTACIÓN** (110–240 s): el pico cuando "se pudre la momia". Se
    apilan técnicas hydra anti-orientación: `modulateRotate(src(o0))` (cada
    píxel rota según el feedback → no hay arriba ni abajo) +
    `modulateScale(src(o0))` (fractal infinito → no hay escala anclada) +
    dos `rotate` apilados con signos opuestos (conflicto de giro) + `noise`
    en cascada de 3 escalas distintas (vectores contradictorios). **No
    podés fijar la vista en nada.**

### 3-recursion (AI local)

**Lo que decidís vos**: los prompts (`prompts_recursion_delirio.txt`) — 1
prompt por escena del track. Y el "scene graph"
(`scenes_recursion_delirio.json`) — qué prompt manda en qué intervalo
temporal.

**Lo que decide el audio**: el control track modula `strength` (cuánto
img2img respeta el frame anterior vs el prompt), `zoom`, `rotation` y
disparos de `reinject` (re-inyecciones de txt2img fresco que evitan que el
latente se "lave" a verde plano).

**Modelo**: `stabilityai/sdxl-turbo` corriendo en Apple Silicon (MPS).
Fallback `runwayml/stable-diffusion-v1-5` si Turbo no carga. Resolución
final 768×432 a 12 fps (el AI dirige hacia look pictórico → fps bajo lo
realza). 1.3 s por frame en M3 Max → ~45 min para los 3 minutos.

**Lo que arreglamos hoy** (el corte abrupto al final):
- Post-process con ffmpeg: vignette animado (de PI/4 a PI/8 en los últimos
  10 s → cierra como túnel) + fade-to-black de 4 s. Sin re-renderizar el
  AI. Sugiere "entrar al túnel / volver al Spiral" (Hexagrama 24 → Outbound).

---

## Cosas que controlamos vs no controlamos

| Aspecto | Outbound (shader) | Crossing (Hydra) | Recursion (AI) |
|---------|-------------------|-------------------|----------------|
| Forma exacta de cada frame | ✅ determinista | ✅ determinista (mismo control track + mismo patch ⇒ mismo mp4) | ❌ no — el AI tiene seed pero generaciones distintas se ven diferentes |
| Velocidad de iteración | minutos | segundos (live coding) | horas (render largo) |
| Mapeo audio → visual | uniforms (fácil de tunear) | `a.fft[]` en cualquier parámetro | indirecto vía scene graph + reinject |
| Estilo visual | controlable al 100% | controlable al 100% | dirigido por prompt; vibe del modelo manda |

---

## Por qué 3 videos separados (no 24 min continuo)

Razones concretas:
1. **No mixing**: cada stack es distinto. Concatenar requiere transiciones
   que ya intentamos antes (agujero negro Outbound→Crossing) y agregan
   fragilidad sin sumar mucho.
2. **Calza con plataformas**: Spotify Canvas (loop por track), YouTube
   (track por track), Bandcamp (mismo).
3. **El seam Hexagrama 24** (Recursion → Outbound) es **decisión del player**,
   no del render. Hoy: fade-túnel al final de Recursion + apertura suave de
   Outbound = se siente continuo si los ponés en queue.

---

## Archivos clave (para mantener)

- `transmissions/01/video/render.py` + `shaders/*.frag` — todo Outbound.
- `transmissions/01/video/hydra/crossing_delirio.js` — todo Crossing.
- `transmissions/01/video/ai/local_render_diffusers.py` + `prompts_*.txt` +
  `scenes_*.json` — todo Recursion.
- `transmissions/01/video/control/*.npz` — control tracks (gitignored,
  regenerables desde el master + `analyze.py`).
- `transmissions/01/video/out/{1-outbound,2-crossing,3-recursion}.mp4` —
  los 3 finales (gitignored, regenerables).

---

## Cómo re-renderizar cualquiera de los 3 (en una línea)

```bash
# 1-outbound
python3.10 transmissions/01/video/render.py --control transmissions/01/video/control/outbound.npz --wav transmissions/01/release/masters/01_outbound_master.wav --out transmissions/01/video/out/1-outbound.mp4 --preset outbound --w 1280 --h 720 --seconds 480 --crf 20

# 2-crossing
cd transmissions/01/video/hydra/_headless && HYDRA_PATCH=../crossing_delirio.js HYDRA_WAV=../../release/masters/02_crossing_master.wav HYDRA_CONTROL=control_crossing.json HYDRA_OUT=../../out/2-crossing.mp4 node render.mjs 780

# 3-recursion (assumiendo que recursion_ai_v2_full.mp4 ya está renderizado)
ffmpeg -y -i transmissions/01/video/ai/out/recursion_ai_v2_full.mp4 -vf "vignette=angle='if(lt(t,170), PI/4, PI/4 - (PI/8)*(t-170)/10)':eval=frame, fade=t=out:st=176:d=4" -af "afade=t=out:st=176:d=4" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart transmissions/01/video/out/3-recursion.mp4
```
