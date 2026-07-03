# Rúbrica QA "PRO" — video de Spiral Out

> Antes de mostrarle al usuario CUALQUIER output de video, pasarlo por esta
> rúbrica. Si no aprueba 7 de 9, no se muestra. Si aprueba 5–6, se muestra
> SOLO si está marcado como variante experimental con su debilidad declarada.
> Si aprueba < 5, no se muestra, se itera.

Aplica a maquetas, iteraciones internas, y entregables.

---

## Los 9 criterios

### 1. **Form clarity** — ¿se entiende qué es?
- El concepto buscado (planeta, piedra, mandala, etc.) es **legible** aunque sea abstracto.
- Test: mostrarle un frame a alguien que NO conoce el proyecto. Si dice "un blob de color" en vez de "algo distante con anillos" → falla.
- Compatible con veladura/distorsión, pero la **silueta primaria** o **sugerencia formal** está presente.

### 2. **Visual density** — ¿hay TEXTURA o solo gradientes?
- No basta con colores que se mezclan suave.
- Test: zoom 200% sobre un frame. ¿Se sigue viendo detalle o se ve como un gradiente de Photoshop?
- PRO: ruido fino, micro-detalle, texturas que aguantan el zoom.
- Windows 95 fondo de pantalla = falla automática.

### 3. **Motion coherence** — ¿el movimiento parece deliberado?
- Cosas que se mueven deben hacerlo con dirección, momentum, vectores explicables.
- Anti-patrón: movimiento browniano random sin tendencia (Hydra crudo).
- PRO: cámara forward, parallax, partículas con velocidad inicial, atmósfera que deriva.

### 4. **Color discipline** — ¿una paleta o vómito de arcoíris?
- Máximo 3 colores principales por escena + neutros (negro, blanco).
- Anti-patrón: colorama() sin control, blends muddy, blancos puros saturados.
- PRO: paleta declarada (ej. violet dusk #5e4cc8 + amber ring #d4a04a + dust grey #2a2a30), respetada en TODOS los frames.

### 5. **Edges** — ¿control sobre dónde hay borde duro y dónde no?
- PRO: bordes intencionales. Una luz tiene halo (sin borde), una piedra tiene contorno (con borde, aunque sea sutil).
- Anti-patrón: TODO blurred por igual = soup (Hydra abusado), o TODO con borde duro = polygonal/cheap (voronoi+thresh).

### 6. **Depth** — ¿hay parallax / capas / atmósfera?
- Cosas cerca se mueven distinto que cosas lejos.
- Atmósfera (haze, dust) entre cámara y objetos lejanos.
- Anti-patrón: todo en un solo plano frontal.
- PRO: layers, foco selectivo, depth-of-field, fog cards.

### 7. **Resolution-appropriate detail** — ¿no se ve pixelado/aliased?
- Si renderás a 1080p, los detalles deben aguantar 1080p. Si renderás a 4K, lo mismo.
- Anti-patrón: shader con micro-detail que aliasea, o textura que tiene resolución para 480p mostrada en 4K.
- PRO: shaders multi-sampled (MSAA), AI a resolución nativa luego upscaled con lanczos, NO simplemente estirado.

### 8. **Conceptual abstraction** — ¿sugerencia o ilustración literal?
- El objetivo es que parezca el concepto SIN ser una ilustración 1:1.
- Ej: un planeta abstracto sí, una foto de la NASA de Saturno no.
- Anti-patrón: usar imagen reconocible directa sin trabajarla.
- PRO: distorsión, atmósfera, paleta no-natural, ángulo poco común, escala extrema.

### 9. **Sincronía con audio** — (cuando aplica) ¿la imagen RESPONDE a la música?
- Si el video acompaña audio, eventos audibles deben tener reflejo visual SINCRO.
- Anti-patrón: visual reactivo a noise random, no a onsets/bandas reales.
- PRO: control track real (rms_sub para latido, fft[3] para air/voyager, onset para bells), envelope smoothers.
- N/A para maquetas sin música.

---

## Cómo aplicar la rúbrica

Antes de mostrar:

1. Renderizar al menos un frame por escena clave.
2. Para cada criterio, dar **PASS / FAIL / N/A** con UNA frase justificando.
3. Si hay ≥ 3 FAIL en criterios 1–8 (1–7 si no aplica audio): NO mostrar. Iterar.
4. Si hay 1–2 FAIL: mostrar **con disclosure explícito** ("falla en criterio X porque Y, propongo fix Z").
5. Si hay 0 FAIL: mostrar normalmente.

---

## Anti-patrones acumulados (para no repetir)

De la sesión 2026-05-24/25 con el usuario:

- **"Windows 95 fondo de pantalla"** (Hydra noise crudo coloreado): falla density + depth.
- **"Ojo / lente"** cuando se buscaba planeta: falla form clarity.
- **"Ano"** cuando se buscaba mandala: falla form clarity + abstraction (la simetría sale básica).
- **"Negros totales"** durante respiros: falla density (no hay nada que ver).
- **"Aurora gradient bands"** cuando se buscaba planeta con anillos: falla form clarity + depth.
- **Blancos puros sobre violeta** en planeta: falla color discipline (clipping a 1.0).
- **Wrap echoes** por `scrollX/Y` en shape(): falla form clarity (aparece la misma cosa en 3 lugares).
- **Reactividad violenta a fft sub/low** en outbound 2:01: falla motion coherence (responde más rápido que la nota).
- **Color noise corruption** en transiciones: falla resolution + edges.

---

## Stack actual vs PRO

| Técnica disponible | Bueno para | Malo para |
|--------------------|-----------|-----------|
| **Hydra (`crossing_delirio.js`)** | feedback chain orgánico, atmósferas continuas, distorsión | objects con shape (planeta, piedras), bokeh real, mandala refinado |
| **Python+GLSL (`render.py`)** | shaders deterministas, raymarching SDF, post-process estilizado | iteración rápida (recompila shader), look pictórico (es demasiado preciso) |
| **AI local SDXL** | imágenes pictóricas/abstractas, "feel" cósmico, look painterly | precisión geométrica, latencia (3s/frame), tiende al verde |
| **ffmpeg post** | color grade, vignette, fade, chroma aberration, blur | generar contenido (solo procesa lo existente) |

Para PRO en Spiral Out, **mezclar técnicas**:
- Base GLSL raymarched (formas 3D reales) + Hydra overlay (feedback atmospheric) + ffmpeg post (grade final).
- O AI local (base painterly) + GLSL post-shader (refinamiento) + ffmpeg (grade).

---

## Decisión 2026-05-25

Producir CADA concepto del 3er maqueta de crossing con 3 variantes técnicas
distintas en paralelo (GLSL raymarched / AI local / Hydra). Aplicar rúbrica
a cada variante. El usuario elige la mejor por concepto, o ninguna si todas
fallan.
