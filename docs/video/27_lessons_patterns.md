# 27 — Video pipeline: patterns & anti-patterns (lecciones caras)

> Aprendido a los golpes armando los 3 visualizers de Heliopause (fue ~un mes
> con idas y vueltas). Leé esto ANTES de arrancar el próximo video.

## ⭐ La lección #1 (la que costó todo de nuevo)

**Renderizá a 60fps (o 30), NO 24fps, para cualquier cosa con movimiento
lento/suave que se vea en YouTube/navegador.**

- 24fps sobre pantalla de 60Hz → **pulldown 3:2** (frames repartidos 2:3:2:3) →
  **judder** en el movimiento lento. El navegador NO lo maneja (QuickTime local
  sí, por eso engaña: local smooth / YouTube cortado).
- 60fps entra 1:1 en 60Hz y 2:1 en 120Hz → sin pulldown → smooth para todos.
- El "desync" también era esto (frames dropeados por decode desfasan A/V).
- Fix retroactivo: `minterpolate=fps=60:mi_mode=mci` + encode HW
  (`hevc_videotoolbox`, ~6× realtime; software x265 4K60 = ~12h, inviable).

## Patterns (hacer)

1. **Validá en el archivo que la PLATAFORMA sirve, no el local.** El mp4 local
   reproduce cada frame exacto; YouTube re-encodea (AV1/VP9) y el cliente
   decodea → ahí aparecen los problemas. Bajá el servido (`yt-dlp
   --cookies-from-browser chrome <url>`) y MEDÍ (cadencia PTS, diffs
   frame-a-frame) antes de concluir nada.
2. **Diseñá/validá en el CONTEXTO de consumo real:** resolución final, EN
   MOVIMIENTO (no stills), tamaño del feed (thumbnails a 168×94), y en la TV/
   navegador. Casi todos los errores fueron por juzgar en el contexto
   equivocado (still lindo, preview a 640, sin grano).
3. **Anti-banding horneado:** los verdes oscuros bandean con la compresión de
   YouTube. Meté ruido estructural **estático** (low+mid freq, fijo por frame
   para no "pumpear" en los P-frames) + grano fino. Sin grano = banding.
4. **Movimiento atado a la música**, no a números inventados. Derivá la
   velocidad/cadencia del control track (rms/flux). El user midió "la velocidad
   de la música", no adivinó.
5. **Persistí todo fuera de `/tmp`.** `/tmp` se auto-limpia y borró trabajo
   varias veces. Usá un workdir persistente.
6. **Medí un sample antes de un render largo.** Un frame/clip corto te da el
   tiempo real (evita comprometerse a 12h por mala estimación) y valida el look.
7. **Trim final a un pelín POR DEBAJO del segundo redondo** (target − 0.1s):
   YouTube **redondea para arriba** cualquier fracción (480.003s → 8:01).
8. **Esperá el procesado completo de YouTube** antes de juzgar calidad/fluidez,
   sobre todo en TV/cast (el 4K en TV llega ÚLTIMO; videos largos tardan más).
   Un privado con 0 vistas tiene cache frío → más buffering.
9. **QA vos mismo antes de mostrar** (a tamaño/movimiento real). Se le mostró
   basura obvia demasiadas veces (silueta "peón", banding, mush).


## El cuadriculado del 4K: la meseta de la fuente (agosto 2026, `bj3_n_pt`)

**El síntoma.** El 4K salía con cuadrados grandes, sobre todo en el primer minuto.

**La hipótesis equivocada (la mía).** "Los recortes son muy chicos, hay que ampliarlos."
Medí y daba lindo: 50 de 62 planos se amplían más de 2x, la mediana era 3,8x, y había
recortes de 280 px estirados a 3840 (13,7x). Parecía cerrado.

**Por qué era falsa.** `pelo` se amplía 13,7x y NO se cuadricula: se ablanda. `sol2` se
amplía 7,1x y sí. Si la causa fuera el factor, el orden estaría al revés.

**La causa real.** El cuadriculado es una propiedad de LA FUENTE, no del escalado. Los
webm del SDO y varios más traen las zonas de bajo contraste aplastadas por el codec en
mesetas planas de 8x8. A contraste nativo son invisibles. Pero el grado del video estira
esa zona **4,4 veces** (`normalize` 1,5 × `eq` 1,7 × curva 1,7), las mesetas salen a la
superficie, y recién ahí el escalado las agranda.

O sea: el cuadrado no lo crea el escalado, lo crea **el grado**, y el escalado lo agranda.

**Cómo medirlo** (`transmissions/02/video/bj3_n_pt/nitidez.py`). Partir el recorte crudo
en baldosas de 8x8 y comparar dos dispersiones: la de adentro de cada baldosa contra la
de entre baldosas. Una imagen normal tiene detalle en las dos escalas; una hecha de
mesetas es plana adentro y escalonada afuera. El cociente `adentro/entre` se desploma:
0,06 a 0,20 en las fuentes aplastadas contra 0,5 a 0,8 en las sanas.

**Lo que NO funciona.** `deblock`, `hqdn3d`, `smartblur` y `gblur`: ninguno cambió nada.
No es un artefacto que se pueda deshacer, es que **debajo de la meseta no hay
información**. Un filtro lineal solo promedia lo que ya está.

**Lo que sí.** Un modelo, porque hay que SINTETIZAR el detalle que falta. Real-ESRGAN
(`mejorar.py` + `modelos/rrdb.py`), escrito en torch puro: el paquete oficial arrastra
`basicsr`, que no compila contra torch 2.11, y la red son 80 líneas.

**El modelo x2 EMPEORA. Usar solo el x4, o sea solo cuando amplía 3,5x o más.** El x2 de
Real-ESRGAN no tiene un upsampler más corto: comprime la entrada con `pixel_unshuffle(2)`,
y a poca ampliación se comporta como afilador en vez de reconstructor. Toma el borde del
bloque de la fuente por estructura real y lo endurece, y de paso inventa chorreados en los
bordes del cuadro. El resultado lee como MP4 corrupto, no como falla de transmisión. Diez
planos salieron así, incluido el que abre el video, y lo cazó el user mirando.

No se puede detectar automáticamente: se probaron cuatro métricas (meseta dentro/entre
baldosas, salto en la rejilla, pico espectral, proporción de bordes alineados a los ejes)
y **ninguna discrimina**, porque el defecto es exceso de FILO y no exceso de planitud. La
que sí correlaciona perfecto es la escala del modelo, así que la regla es esa. Sobre esos
mismos planos, un `gblur` da textura orgánica sin mosaico.

**Dónde ubicarlo en la cadena** (las dos decisiones que más importan):

1. **Antes del grado.** El modelo está entrenado sobre imagen natural. Si primero se
   estira el contraste 4,4x, lee los escalones de bloque como bordes reales y los AFILA.
2. **Antes de la cámara lenta.** `setpts` estira un cuadro de fuente en varios de salida;
   procesar la salida es pagar el mismo cuadro varias veces. Fueron 3996 cuadros únicos
   contra 14160 de salida: 3 h de GPU en vez de 12,6.

**El defecto que casi meto encima.** Guardaba el intermedio en 8 bits. El modelo entrega
19462 niveles distintos y yo los tiraba a 84; después el grado los abría en bandas
concéntricas bien visibles (60 niveles de gris de salida contra 193 manteniendo la
precisión). **Las bandas eran mías, no del modelo.** Se arregla con intermedio en ProRes
de 10 bits y el grado entero en `gray16le`, volviendo a 8 recién junto al grano, que hace
de tramado. En fuente sana no cambia nada (media 121,7 contra 122,4, mismos percentiles).

**Cómo integrarlo sin re-abrir lo aprobado.** El intermedio guarda el recorte reconstruido
Y NADA MÁS: sin grado, sin variante, sin ralentizar, a los fps de la fuente. Entra donde
entraría la fuente, con el primer `crop` vuelto nulo. Así el plan de planos queda intacto
y las cuatro reglas de repetición se siguen cumpliendo. Guarda obligatoria: abortar si el
plano usa un grado medido en píxeles (segundo `crop`, `gblur`, `unsharp`), porque el
intermedio es N veces más grande y esos parámetros quedarían fuera de escala.

## Anti-patterns (NO hacer)

1. ❌ **Renderizar a 24fps para web** (ver lección #1).
2. ❌ **Concluir sobre el comportamiento en YouTube sin ver el archivo servido.**
   Especulé con AV1/priming sin bajarlo — pérdida de tiempo y credibilidad.
3. ❌ **Rabbit holes en un enfoque con mismatch de fondo.** El Mandelbrot: días
   con escape-time (speckle), denoise (popping), DE, slope shading… cuando el
   problema base era que **el detalle fino de un fractal NO se lee en
   movimiento**. Pivoteá temprano (→ Kaliset full-screen, patrón simple que sí
   se lee). Regla: si iterás 3 veces y el problema es estructural, cambiá de
   enfoque, no de parámetro.
4. ❌ **Juzgar movimiento con stills** / calidad final con un test low-res
   sin grano. El banding y el "no se nota el detalle" solo aparecen a escala
   real y en movimiento.
5. ❌ **Borrar antes de confirmar/backupear.** Borré los thumbnails viejos y el
   user quería uno; `rm` no va a la papelera y el dir no estaba en git.
6. ❌ **Usar "el frame más lindo" como thumbnail.** Un thumbnail es diseño para
   el feed (un sujeto, alto contraste, legible chico), no un screenshot. Ver
   `docs/24_thumbnail_guide.md`.
7. ❌ **Estimar tiempos de render sin medir.** Dije 12h/2h/etc. mal varias veces.
8. ❌ **Atribuir un defecto de imagen al escalado sin mirar la fuente cruda.** El
   cuadriculado del 4K parecía upscale y era compresión de origen amplificada por el
   grado. Mirá el recorte crudo, sin gradar, ampliado con `neighbor`, ANTES de teorizar.
9. ❌ **Cuantizar a 8 bits en medio de una cadena que estira el contraste.** Si después
   viene un `normalize`+`eq`+`curves` que multiplica por 4, cada nivel perdido se abre en
   una banda. El grado va en 16 bits y se baja a 8 al final, junto al grano.
10. ❌ **Shipear un criterio de QA sin calibrarlo contra el archivo YA ARREGLADO.**
    Calibré el criterio de cuadriculado contra el video defectuoso (daba FALLA, bien) pero
    no contra el corregido: ahí también daba FALLA, con MÁS planos. Un criterio que grita
    lobo es peor que no tenerlo. Un criterio necesita los dos polos: falla en el malo Y
    pasa en el bueno.
11. ❌ **Confiar en un upscaler a poca ampliación.** Abajo de ~3,5x un modelo de
    super-resolución tiene poco que reconstruir y lo que hace es afilar lo que hay,
    incluidos los artefactos de compresión. Si la ampliación es chica, filtro, no modelo.
12. ❌ **Revisar por muestreo cuando el defecto es intermitente.** Miré tres o cuatro
    planos y di el pase; el defecto estaba en 10 de 61 incluido el primero. Para algo que
    aparece en algunos planos y en otros no, hoja de contactos de TODOS los planos
    afectados, no muestras.
13. ❌ **Encadenar métricas cuando la evidencia visual ya es concluyente.** Probé tres
    métricas de cuadriculado y las tres se dejaron engañar (meseta contra degradado liso,
    rejilla que ya no existe, pico espectral dominado por la imagen). Cuando el A/B visual
    es inequívoco, decilo y pasá a verificar cobertura, que sí es determinística.

## Checklist mínimo para el próximo video

- [ ] Render a **60fps** (o 30). Nunca 24 para YouTube.
- [ ] Anti-banding (ruido estático + grano fino) horneado.
- [ ] Grado en 16 bits, vuelta a 8 recién junto al grano.
- [ ] Correr `nitidez.py` sobre el plan: si alguna fuente da cociente < 0,42 y el plano
      se amplía 2x o más, va por el modelo (`mejorar.py`), no por filtro.
- [ ] Movimiento atado al control track (audio).
- [ ] Workdir persistente (no /tmp).
- [ ] Validar look en 4K + EN MOVIMIENTO antes de escalar.
- [ ] Encode HW (VideoToolbox) para 4K; medir un sample primero.
- [ ] BT.709 (tres tags) — forzar con `setparams` si la fuente viene mistag.
- [ ] Duración = target − 0.1s (que YouTube muestre el minuto redondo).
- [ ] Thumbnails según `docs/24_thumbnail_guide.md`, testeados a 168×94.
- [ ] Subir, **esperar procesado completo**, y validar en el **archivo servido**
      (yt-dlp) + en la TV.

Relacionado: `docs/24_thumbnail_guide.md`, memoria `reference_outbound_*`,
`feedback_no_rabbit_holes_use_my_vision`, `feedback_qa_yourself_before_showing`.

## Septiembre 2026 · lo que salió de arreglar `bj3 n pt` (TX02 track 1)

El user marcó ocho defectos sobre el 4K. Al medirlos, **casi todos tenían la misma causa de
fondo y ninguna era la que parecía**. Queda acá porque son errores de método, no de ese
video.

### 1. Medir el PLAN en vez del archivo

El examen daba "LISTO PARA ENTREGAR" sobre un video con 5,4 s de pantalla negra, un salto
de luz de 1 a 204 en un cuadro y tramos percibidos de 2,9 s. Leía las duraciones del
`.plan.txt` (donde ningún plano baja de 8 s) y la limpieza de `ventanas.json` (medida a
mano y desactualizada). **Lo que no se mide sobre el archivo que se entrega, no está
medido.**

### 2. Leer los bytes equivocados

`normalize` solo existe en RGB, así que ffmpeg entrega 3 bytes por píxel. El código dividía
por 1 y promediaba Y, U y V juntas: como en gris U=V=128, **un cuadro negro medía ~85 de
luz en vez de 0**. Por eso el filtro de pantalla negra no disparó nunca. Forzar
`format=gray` + `-pix_fmt gray` al final de toda cadena de medición.

### 3. Emitir "el menos malo" cuando nada pasa

El generador, si ninguna combinación pasaba los umbrales, emitía igual la mejor de las
malas. De ahí salieron 24 planos negros o quietos de 61 sin que nada abortara. Un fallback
silencioso convierte un umbral en una sugerencia.

### 4. Dos varas para la misma cosa

El generador exigía movimiento 0,40 y el examen 1,00, así que el examen reprobaba planos
que el generador había aceptado bien. Pasó tres veces con criterios distintos (movimiento,
factor de corte interno, ventana de análisis). **Si dos archivos miden lo mismo, el umbral
vive en un solo lado.**

### 5. Un remedio de una fuente aplicado a toda una familia

El `tmix=frames=8` estaba puesto para matar el estrobo de UNA fuente y se le aplicaba a las
trece solares. Medido, promediar ocho cuadros le costaba el movimiento a las otras doce
(una fulguración caía de 6,16 a 1,30). Buena parte del "es estática" salía de ahí.

### 6. El recorte ancho promedia el movimiento a cero

Los recortes solares agarraban el disco entero y el plasma se promediaba: 0,06 de
movimiento. Cerrados sobre una región activa, el MISMO archivo da 1,97. Los de la lluvia
del user eran tajadas de 130 px de alto en zona oscura.

### 7. El grano infla la medición

Aporta ~0,32 de diferencia entre cuadros sobre material liso. Los dos planos que el user
marcó como estáticos medían 0,28 y 0,31 CON grano: movimiento real cero.

### 8. Predecir la cadena no se puede

Se intentó reconstruir en el validador la cadena de filtros del montaje y no cierra: no ve
el blur que mete el paso de reconstrucción (medido, 0,85 -> 0,35), ni el encode, ni la
sustitución por el intermedio del modelo, que en tiempo de planificación no existe todavía.
**La salida fue medir los planos ya renderizados y realimentar** (`validar_render.py` ->
`excluidos.txt` -> replanificar), más pedir de más en la validación (margen del 50% sobre
el umbral del examen) porque la predicción es optimista.

### 9. Lo que ningún número ve

Una barra negra vertical dura en el agua, en 4:12. Es un objeto real de la fuente que el
modelo afiló y el grado estiró, y lee como algo recto y reconocible. Ninguna métrica del
repo la marca: el detector de líneas rectas corre sobre material crudo (donde todavía es
tenue) y sobre material gradado dispara siempre. **Esa clase de defecto se mira.** De ahí
salió `hoja_contacto.py`.
