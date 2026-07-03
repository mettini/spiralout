---
name: qa-turrell
description: Rúbrica curatorial estricta sobre obra de James Turrell. ACTIVAR cuando se diseñe o renderice CUALQUIER asset visual que invoque "Turrell", "Skyspace", "Ganzfeld", "Aten Reign", "Roden Crater" o "campo perceptual de luz". Se aplica ANTES de codear, ANTES de renderizar, y como QA final sobre stills y MP4. Si la pieza no pasa los 7 chequeos no se puede llamar Turrell y NO se entrega como tal. Codifica antipatrones derivados de los fracasos previos del proyecto (sombras-que-no-son-Turrell, "spot de luz en corner", "interferencia de dither", contact-sheet a 3 frames, claim sin curaduría).
---

# qa-turrell — Curaduría dura sobre obra de James Turrell

Skill de **enforcement**. No es inspiración, es **rejilla**. Si la pieza no
pasa, no se llama Turrell y no se renderiza ni se entrega. Punto.

## 1 — Qué ES Turrell (corto)

**Turrell esculpe con luz.** Tres frases:

1. La luz es **sustancia tangible**, no efecto sobre fondo. Un rojo Turrell no
   está *en* el aire, **es** el aire.
2. **La obra es la percepción del espectador.** La forma de la pieza es lo
   que tu ojo HACE cuando entra al campo, no lo que "muestra" el campo.
3. **Tiempo lentísimo, sin eventos.** Sus Skyspaces cambian de color al ritmo
   del crepúsculo (40-60 min por ciclo). Nunca hay "ahora pasa esto". Hay
   "ya pasó", silenciosamente.

## 2 — Las 5 series (referencia obligada)

| Serie | Qué es | Lección operativa |
|---|---|---|
| **Skyspaces** (1976–presente) | Cámaras arquitectónicas con un **óculo** abierto al cielo. LED interior shifta color muy lento. El cielo se ve de colores imposibles enmarcado por el óculo. | Sólo dos elementos: campo + óculo. Ambos cambian a tiempos desfasados. La arquitectura encuadra. |
| **Ganzfeld** (1976–presente) | Cuartos donde no podés decir dónde termina la pared y empieza el aire. **Sin bordes**, sin profundidad. Pura sustancia de color. | Cero gradientes con bordes detectables. Cero figuras. La pantalla tiene que leer como aire coloreado, no como gráfica. |
| **Aten Reign** (Guggenheim 2013) | La cúpula del Guggenheim convertida en **anillos concéntricos elípticos** que pasan por la rueda cromática durante 60 min. Espectador acostado en el piso. | Geometría arquitectónica radial perfecta. Transiciones cromáticas continuas, sin saltos. |
| **Roden Crater** (1977–presente) | Volcán en Arizona tallado durante 50 años como observatorio celeste. Cámaras alineadas con eventos cósmicos. | Naturaleza cósmica encuadrada por arquitectura hecha a mano. Apertura al cosmos como sujeto. |
| **Wedgework / Shallow Space** (1969–) | Habitaciones con luz fluorescente que parecen tener planos sólidos coloreados flotando. Te confunde la percepción de profundidad. | La luz puede leer como sólido si lo tratás como volumen, no como brillo. |

## 3 — Antipatrones (lo que NO es Turrell)

Banderas rojas. Si la pieza tiene cualquiera de esto, **NO** es Turrell.

- ❌ **Sombras**, manchas oscuras, "mancha que se mueve", figuras oscuras de
  cualquier tipo. Turrell trabaja con luz, no con su ausencia ni con objetos
  oscuros sobre fondo.
- ❌ **Eventos dramáticos**: "ahora aparece una luz", "ahora explota el centro",
  "ahora se acerca el túnel". Turrell no tiene eventos. Tiene estados que
  cambian sin que vos te des cuenta hasta que ya cambiaron.
- ❌ **Movimiento de cámara**. Pan, zoom, parallax — todo prohibido. El frame
  es una pared. El sujeto es lo que pasa adentro del frame, no la cámara.
- ❌ **Bordes duros**, contornos definidos, geometría con edge claro (salvo
  el óculo arquitectónico que es geometría sí pero infinitamente blanda en
  su luz interior).
- ❌ **Figuras reconocibles**: caras, paisajes, animales, símbolos, glifos,
  planetas. Nada figurativo. Ni siquiera abstracto-reconocible.
- ❌ **Gradiente vertical fuerte tipo cielo-piso**: si lo abusás se lee como
  paisaje, no como aire. Turrell sí usa transiciones de luma pero tan
  imperceptibles que parecen sin gradiente.
- ❌ **Grano analógico/film**: la luz Turrell es **limpia**. El grano es de
  fotografía, no de Skyspace. (Excepción: grano técnico solo como dither,
  invisible a viewing distance.)
- ❌ **Textura**: nada de Worley, FBM, ridge noise, displacement de paredes,
  god rays. Esa estética pertenece a otro lenguaje (Lustmord visual, Tarkovsky
  zone, Kiefer pintura) — NO a Turrell.
- ❌ **Saturación viva**: Turrell evita rojos primarios sin matiz. Sus colores
  son **cuasi-monocromos sutiles** — un rojo que duda entre rosa y bordó,
  un azul que está al borde de violeta. Pureza chillona = no Turrell.
- ❌ **"Bells light en corner"**: spots de luz en esquinas son **lens flare
  cinematográfico**, no Turrell.

## 4 — Rúbrica de aceptación: las 7 preguntas

Aplicar SOBRE STILLS de 4K (varios, no uno) ANTES de comprometer render largo.
**Para llamarse Turrell, la pieza tiene que pasar los 7.** Si falla uno solo,
itera el shader; no es Turrell todavía.

1. **Sustancia, no superficie**: ¿la pantalla se siente como **aire de
   color** o como **color sobre fondo**? (Test: ¿podrías imaginarte metiendo
   la mano y agarrando luz?)

2. **Ausencia de bordes detectables**: ¿podés señalar dónde termina un color y
   empieza otro? Si la respuesta es "sí, ahí, esa línea", falla. Turrell
   transiciona sin que el ojo pueda anclar dónde.

3. **Cero figuras, cero eventos**: ¿hay alguna forma, mancha, evento, drift,
   "algo que está pasando ahí"? Tiene que ser **no**. Sólo aire.

4. **Arquitectura sí o no, pero coherente**: ¿hay un óculo o algún elemento
   arquitectónico (anillo concéntrico, rectángulo del techo, marco)? Si lo
   hay, debe ser **geométricamente perfecto** y sus bordes deben ser
   arquitectura, no objeto. Si no lo hay, el frame entero es campo Ganzfeld
   y tiene que estar libre de gradientes detectables (ver #2).

5. **Tiempo cinemático lento real**: ¿en 30 segundos de motion, alguien que
   mira casualmente puede decir "se ve diferente que recién"? Si **sí**, es
   demasiado rápido. La velocidad Turrell: un Skyspace toma 40-60 min para
   pasar del azul atardecer al violeta. Tu 13:00 de Crossing tiene que tener
   **una sola** trayectoria cromática lentísima, no estaciones marcadas.

6. **Paleta cuasi-monocromática matizada**: ¿los colores tienen ambigüedad
   (rojo-que-duda-entre-rosa-y-bordó)? ¿o son rojo / verde / azul puros? El
   primero pasa, el segundo no.

7. **¿Lo firmaría Turrell?** (la pregunta final, no negociable). Si en una
   sala junto a *Aten Reign*, *Pleiades*, *Skyspace del Roden Crater* alguien
   colgara tu video y un crítico de The Art Newspaper viniera a reseñar la
   muestra, ¿escribiría "Turrell ha extendido su obra al video" o escribiría
   "el video colgado al final es una decepción que no dialoga con la obra
   del artista"? Honestidad obligatoria. Si dudás, **no es Turrell**.

## 5 — Workflow obligatorio para piezas Turrell-claim

Esto es proceso. Saltar pasos = no se llama Turrell.

### Paso 0 — Antes de tocar código
Releer la sección 1 y 2 de este skill. Tener presentes las 5 series. Si no
podés citar de memoria al menos 3 de las 5 sin googlear, **no estás listo**
para implementar Turrell. Leelas otra vez.

### Paso 1 — Concepto antes que código
Escribir el `concept.md` ANTES del primer shader:
- ¿Cuál de las 5 series es la referencia? (Skyspace? Aten Reign? Ganzfeld?)
- ¿Qué elementos arquitectónicos? (campo solo, campo + óculo, anillos
  concéntricos)
- ¿Cuál es la trayectoria cromática única en los 13:00? (un solo arco, no
  estaciones — ej: azul cobalto profundo → violeta atardecer → rosa-bordó
  → gris-violeta → casi-blanco frío, con velocidad similar a un crepúsculo
  filmado en time-lapse 10×)
- ¿Por qué este concepto es Turrell y no otra cosa? (1 párrafo argumentando)

### Paso 2 — Stills primero, motion después
Renderizar **mínimo 6 stills a 4K** en momentos clave del journey
cromático (t=0, t=2:30, t=5:00, t=6:30, t=9:30, t=12:30). PNG. Mirarlos.

Aplicar las **7 preguntas de la rúbrica** a cada still. Si alguno falla:
iterar shader, re-render still, repetir.

### Paso 3 — Contact sheet 15 frames del motion preview
Antes del render 4K full, generar contact sheet 1080p con 15 frames
distribuidos cada ~50 segundos. Mirar la grilla entera.

Aplicar la **pregunta 5** (tiempo) específicamente: ¿se ve diferente entre
frames consecutivos? Si dos frames adyacentes (separados por 50s) muestran
diferencia obvia, demasiado rápido. Bajar la velocidad de transición.

### Paso 4 — Render full 4K
**Sólo si pasos 2 y 3 pasan.** No antes.

### Paso 5 — Contact sheet del MP4 final (no del pretest)
Después del render full, extraer 15-20 frames del MP4 real con ffmpeg y
generar contact sheet. Aplicar las 7 preguntas otra vez. El render final
puede romper algo que el pretest no rompía (encoding artifacts, banding,
color shift).

### Paso 6 — La pregunta final
Antes de entregar el path al usuario, mirar el MP4 una vez (no scrubbing,
viendo). Preguntar honestamente: **¿lo firmaría Turrell?**

Si la respuesta NO es un sí inmediato y firme, **no entregar**. Iterar.

## 6 — Antipatrones de proceso (errores cometidos en este proyecto)

Estos son fallos reales del proyecto que el skill debe prevenir.

### 6.1 — QA con 3 frames en lugar de contact sheet
**Síntoma**: "miré frames a t=0, t=mid, t=end, todo OK". Después motion: todo
negro durante 2 minutos entre los samples.
**Regla**: mínimo 15 frames distribuidos. Contact sheet obligatorio.

### 6.2 — "Casi pasa" no pasa
**Síntoma**: agente o yo mismo decimos "pasa la rúbrica pero le falta X / con
caveat / borderline". → falla. No es Turrell.
**Regla**: la rúbrica es booleana. Pasa o no pasa. Sin medio tono.

### 6.3 — "Sombra que se devora la pantalla" llamada Turrell
**Síntoma**: implementar shadow drift over dark green field y llamarlo
"Turrell con sombra atrás de capas". → Turrell **no tiene sombras**.
**Regla**: si hay forma oscura sobre campo claro, NO es Turrell. Renombrar
("dark ambient field con sombra reactiva", por ej.) o iterar a Turrell real.

### 6.4 — Patrones de dither visible
**Síntoma**: interleaved-gradient noise pattern hex visible al zoom 200% en
gradientes oscuros. El espectador lo percibe como interferencia.
**Regla**: encodear 10-bit yuv420p10le sin dither shader, o blue noise real
(void-and-cluster precomputado), nunca IGN approximation.

### 6.5 — Renderizar antes de aprobar stills
**Síntoma**: lanzar render full 13min × 4K antes de validar concepto en
stills. 50 min de espera + máquina liquidada para descubrir que no pasa la
rúbrica.
**Regla**: paso 2 y 3 son OBLIGATORIOS antes del paso 4.

### 6.6 — Confiar en self-report de sub-agente
**Síntoma**: sub-agente dice "pasa la rúbrica" y yo paso el path sin abrir
el archivo. El user encuentra el problema.
**Regla**: antes de comunicar path al user, yo (main thread) abro el archivo
y aplico la rúbrica yo mismo. Sub-agente report es **insumo**, no veredicto.

### 6.7 — Llamar "Turrell" a algo que no lo es porque suena bien
**Síntoma**: arrancar el proyecto con "te hago una pieza Turrell" sin
haber pasado por la sección 1-2 de este skill. Después arreglar a posteriori.
**Regla**: si vas a invocar a Turrell, leés este skill ANTES. Si no lo vas a
invocar, no lo invocás (decís "campo oscuro contemplativo" o lo que sea).

## 7 — Cómo aplicar este skill

- Cuando el usuario dice "Turrell", "Skyspace", "Aten Reign", o describe algo
  que se parece a un campo perceptual de luz → cargar este skill antes de
  cualquier acción.
- Cuando se va a escribir un shader o concept.md que invoque Turrell → leer
  secciones 1-4 antes de codear.
- Cuando se va a renderizar un still o video que se va a etiquetar como
  Turrell → aplicar workflow sección 5 obligatorio.
- Antes de pasarle path al usuario de algo "Turrell" → aplicar las 7 preguntas
  + la pregunta final.
- Si en cualquier punto el agente / yo dudo si algo es Turrell → **no es
  Turrell**. Renombrar o iterar.

## 8 — Refs visuales para tener en RAM mental

(URLs / nombres de obras para consultar cuando se diseña)

- *Aten Reign* (2013, Guggenheim NY) — referencia para anillos concéntricos
- *Meeting* (1986, MoMA PS1) — Skyspace, óculo cuadrado al cielo
- *Pleiades* (1983, Mattress Factory) — ganzfeld muy oscuro
- *Twilight Epiphany* (2012, Rice University) — Skyspace al amanecer/atardecer
- *Roden Crater* (1977–presente) — naked-eye observatory en cráter volcánico
- *Bridget's Bardo / Wide Out* — wedgework con planos de luz aparente
- *Catso, Red* (1967) — proyección que parece sólido geométrico

## 9 — Frase final, en serio

**Si la pieza no la firmaría Turrell, no la llamés Turrell.** El nombre
implica curaduría. Curar mal a un artista vivo es una falta de respeto al
artista y al espectador.
