# Reporte — 3 tracks × 3 tecnologías (batch nocturno 2026-05-21)

> Reporte del trabajo pedido: mp4 de los 3 tracks con las 3 tecnologías +
> recomendación de mezcla. Resumen ejecutivo arriba; detalle abajo.

## Matriz de entregables

| Track | Python (mp4) | Hydra (mp4) | AI |
|---|---|---|---|
| **Recursion** (3:00) | ✅ `out/recursion_delirio_v5.mp4` | ✅ `hydra/out/recursion_delirio_hydra.mp4` (en paleta) | 📄 receta |
| **Outbound** (8:00) | ✅ `out/outbound_v2.mp4` | ⚠️ `hydra/out/outbound_delirio_hydra.mp4` (arcoíris, fuera de paleta) | 📄 receta |
| **Crossing** (13:00) | ✅ `out/crossing_v1.mp4` | ⚠️ `hydra/out/crossing_delirio_hydra.mp4` (arcoíris) | 📄 receta |

✅ = mp4 listo para ver · ⚠️ = mp4 existe pero necesita pase de paleta · 📄 = receta lista, sin mp4 (ver AI abajo)

## Las 3 tecnologías — qué dan y estado

### 🟢 Python + shader (motor `transmissions/01/video/`) — LA COLUMNA
- 3 tracks renderizados, cada uno con storyboard ("director") que muta la forma por fases:
  - **Outbound**: nacer → DESPEGUE/TÚNEL (protagonista) → humo → mandala + floración de color → afuera. Sin rayas, sin relámpagos (decisión usuario).
  - **Crossing** (lo picante): entrada → polvo de Saturno → tropezones (rocas) → **INVERSIÓN a mitad** → RAYAS horizontales → stargate sucio → salida. Relámpagos sparse (no abusados).
  - **Recursion**: nacer → humo → túnel → mandala (caleidoscopio) → colapso/loop, con floración de color en el pico.
- Look fósforo verde + floración de color sucio (stargate) en los picos. **Es el look que aprobaste.**
- Audio-reactivo real (mismo control track NumPy que generó el audio), reproducible (scripts commiteados, mp4 gitignored), corre 100% local.

### 🟡 Hydra (`transmissions/01/video/hydra/`) — TEXTURA, estética distinta
- Logré renderizarlo a **mp4 headless** (sin browser) con `_headless/render.mjs` + el `a.fft` alimentado desde nuestro control track. Reproducible: `node render.mjs <segundos>` con env vars `HYDRA_PATCH/WAV/OUT/CONTROL`.
- **Recursion**: sale lindo y en paleta (mandala ámbar-verde sobre negro). Estética más gráfica/plana que Python — un lenguaje genuinamente distinto.
- **Outbound / Crossing**: ⚠️ renderizaron OK pero salieron **arcoíris/caóticos** (el `colorama` de los patches se desbocó fuera de la paleta fósforo). Se ven pero NO alinean con la dirección. **Necesitan un pase de paleta** (clamp de colorama / tinte fósforo / menos detalle voronoi). No es un blocker técnico — es ajuste de arte.

### 🟠 AI open-source (`transmissions/01/video/ai/`) — SOLO RECETA (sin mp4)
- **No se pudo generar mp4 de AI esta noche** — y era esperable: necesita modelos de Stable Diffusion (varios GB), Forge/ComfyUI instalado, y GPU; en este Mac vía MPS son **horas por track**. No es honesto dejarlo corriendo a ciegas toda la noche sin validar.
- Lo que SÍ está listo y corre: `audio_to_keyframes.py --track {recursion,outbound,crossing}` (reusa el control track → keyframes Deforum + prompt-schedule por escena), `scenes_*.json`, `prompts_*.txt`, `deforum_settings_*.json`, `comfyui_animatediff_recursion.json`. Todo versionado.
- Para materializarlo hace falta: una GPU (o Colab Free) + seguir el README. Recomendación: usarlo como **restyle (vid2vid) sobre el render de Python**, no como generador desde cero.

## Recomendación sobre MEZCLAR las tecnologías

(La decisión final es tuya — esto es mi lectura honesta.)

**Sí, vale mezclarlas, pero en capas, no en partes iguales:**

1. **Python = base/columna de los 3 tracks** y del master continuo. Es lo controlable, reproducible, en paleta, y lo que aprobaste. La estructura (storyboard por fases + audio) vive acá.
2. **Hydra = acentos de textura** en momentos puntuales (el colapso/feedback de Recursion, el chicharreo del vinilo, una transición). Su estética bold aporta contraste — pero como *capa/inserto*, no como columna (no tiene timeline y la paleta se le va). Primero hay que arreglarle la paleta a Outbound/Crossing.
3. **AI = acabado opcional** (restyle vid2vid) sobre tramos selectos del render Python, si conseguís GPU y querés esa textura. No como generador base (caro, flickerea).

**En una frase:** Python manda la película; Hydra y AI entran como texturas/acabados en momentos elegidos, no como pistas paralelas equivalentes.

## Qué está sólido vs qué necesita trabajo

**Sólido:** Python los 3 tracks (dirección aprobada) · Hydra Recursion · todas las recetas AI · el pipeline reproducible (incluido Hydra headless).

**Necesita trabajo:** paleta de Hydra Outbound/Crossing · materializar AI (GPU) · matar el anillo concéntrico residual en Python · afinar el stargate (slit-scan real) · **master continuo de 24:00 + loop seams** entre temas (Hexagrama 24) · tunear curvas finas (dónde entra el color, densidad de relámpagos, etc.).

## Rutas de archivos
- Python mp4: `transmissions/01/video/out/{recursion_delirio_v5,outbound_v2,crossing_v1}.mp4`
- Hydra mp4: `transmissions/01/video/hydra/out/*_hydra.mp4`
- AI recetas: `transmissions/01/video/ai/`
- Docs: `docs/video/00_PLAN_status.md` (estado), `01`–`05` (conceptos/research), este `06` (reporte).
