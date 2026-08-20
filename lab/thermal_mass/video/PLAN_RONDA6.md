# PLAN RONDA 6 · cambios a aplicar, para validar antes de procesar

> Escrito el 2026-08-13 con el feedback del user. **Nada de esto está ejecutado.**
> El orden es: validar audio → validar escenas nuevas → recién ahí el video.

---

# PARTE 1 · AUDIO (se valida primero)

## A1. El "paabummpuuu": causa raíz encontrada, y era de diseño

Reportado en 8:09, 8:48, 9:26, 10:06. Y los "saltos en la lluvia" de 8:58 y 9:36 son
lo mismo: **todos están separados por 39 segundos**.

Medido sobre la capa `moog` aislada, segundo por segundo:

```
8:12  ###
8:13  
8:14  
8:15  (SILENCIO)
8:16  (SILENCIO)
8:17  (SILENCIO)
8:18  (SILENCIO)
8:19  #########
8:20  ###############################
```

**No es un artefacto ni un click. El moog se calla cuatro segundos y vuelve a entrar.**
Eso pasa cada 39 s porque la capa repite una pasada de 35 s con una pausa de 4
(`PAUSA_S` en `moog.py`). Lo puse a propósito, con el argumento de que "son apariciones
y no un loop", y estaba equivocado: contra una cama sostenida, un corte de 4 s se
escucha como que la música se rompe.

Confirmación indirecta: el user identificó "8:19 casi 8:20 entra el moog" sin saber que
eso **era** la re-entrada del bucle.

### El fix

**Una sola línea continua desde 7:40 hasta el final, sin loop y sin pausas.** Eso
resuelve a la vez el corte cada 39 s y el pedido de que la melodía no se repita.

Implementación en `moog.py`:

- Sacar `PAUSA_S` y el `while` que coloca pasadas.
- Generar **una** secuencia de notas que cubra los 190 s de la ventana.
- Las notas se encadenan con `glide`, o sea que la voz nunca se apaga: el filtro y la
  amplitud quedan abiertos y solo cambia la altura.

## A2. La melodía no se repite nunca ~~ CORREGIDO: la regla estaba mal

Pedido textual: *"quizás que no se repita nunca la melodía. Cómo podemos hacer?"*

La regla que se escribió acá era: *"nunca se repite un par de notas consecutivas en toda
la ventana"*. **Está mal y es la causa de que las tres primeras versiones no sonaran a
melodía.** Una melodía se reconoce porque un motivo VUELVE; prohibir la repetición deja
un paseo al azar sobre cuatro alturas.

Lo que no se puede repetir es la **pasada entera** (el bucle de 35 s, que es lo que el
user marcó). El motivo tiene que repetirse.

Sumado a eso faltaban tres cosas más: 0% de movimiento por grado conjunto (con solo Mi,
Sol y Si todo intervalo es una 3ra o más, y eso el oído lo lee como arpegio de la
armonía), ningún pico, y ningún par antecedente / consecuente.

**La versión correcta está en `docs/45_como_se_arma_una_melodia.md`** e implementada en
`lab/thermal_mass/melodia.py`: forma A A' B A'' sobre los 200 s, motivo de ritmo fijo que
vuelve en tres de las cuatro frases, 77% de grados conjuntos usando Fa# La y Do como
notas de paso, y un pico único (Mi 640 Hz) al 54% de la ventana.

Y el registro: la línea subió dos octavas, de 80-120 Hz a 285-640. Abajo de ~150 Hz el
oído no percibe melodía, percibe bajo.

## A3. El cierre: la nota del Voyager (PENDIENTE DE TU OK)

Propuesta que quedó sin confirmar. La base está en 71,3 Hz y el drone del Voyager en
Heliopause en 73,42: la misma nota, 51 cents aparte.

La última nota del moog abandona el motivo y se queda en **36,71 Hz**, o sea el Re del
Voyager una octava abajo. Contra los 35,65 de la base late a **1,06 Hz**: no es acorde
ni melodía, es una interferencia lenta que no resuelve. Y es mucho más grave, que es lo
que se pidió para 10:19.

Si no cierra, el plan B es quedarse en el Mi sin resolver.

## A4. El QA que faltaba

`qa_scan_empalmes.py` no atrapó esto porque busca **saltos de nivel**, y acá el
problema era un **silencio**. Se agrega un segundo chequeo:

    huecos en una capa que deberia ser continua

Recorre cada capa dentro de su ventana de arreglo y avisa si hay más de 1,5 s por
debajo del 2% de su propio nivel. Con eso, un corte de 4 s salta de una.

## A5. Lo que se revisa aunque no se haya marcado

Compromiso de esta ronda: correr los tres QA sobre el master y reportar **todo** lo que
salga, no solo lo marcado.

- `qa_scan_spectral.py` (frituras)
- `qa_scan_empalmes.py` (saltos periódicos)
- el chequeo de huecos nuevo, capa por capa

---

# PARTE 2 · ESCENAS NUEVAS (se validan antes del video)

## N1. Para 4:50 a 6:30, el repiqueteo fuerte de lluvia

Es la zona donde se pidió tratamiento especial y no se hizo nada. Un minuto y medio con
una sola secuencia no va.

**El sonido de ahí son gotas discretas**, así que la imagen tiene que ser impactos.
Opciones, en orden de cuánto sirven:

| Opción | Estado |
|---|---|
| **Que el user filme un charco con gotas cayendo** | pendiente de decisión. Es lo mejor: su material mide 9,64 de movimiento contra 1,06 del archivo |
| Agua golpeando el piso, cualquier superficie mojada | idem |
| `IMG_4740` recortado sobre las salpicaduras | ya está en el repo, se puede usar ya |

**Y un tratamiento propio para esa zona**, distinto del resto del video, para que se
note que ahí pasa algo: `lenscorrection` (curva las líneas rectas) más inversión de
negativo en los impactos. Que la zona tenga su propia firma visual.

## N2. Nada más se necesita

Con las nueve fuentes actuales más lo del charco alcanza. El problema no era falta de
material, era el bucle.

---

# PARTE 3 · VIDEO

## V1. Sacar el bucle del acto 2. Es la causa de todo lo demás

El acto 2 está escrito como `for i in 1 2 3 4 5` sobre 6 planos. **No son planos
parecidos, son los mismos cinco veces.** Por eso a los 7 minutos se sigue viendo el
mismo bosque y el mismo volcán.

Medido sobre el script: el solar tiene **16 apariciones con 11 combinaciones**, o sea 5
repetidas exactas. Y hay 7 pares de firma idéntica.

**Todos los planos se escriben o se generan uno por uno. Ningún bucle.**

## V2. Las reglas de repetición, explícitas y verificables

1. Ninguna combinación de **fuente + recorte + variante + grado** aparece dos veces en
   todo el video.
2. Ninguna fuente aparece más de **3 veces** en total, contando cada variación como
   toma distinta.
3. Dos apariciones de la misma fuente nunca caen en el **mismo minuto**.
4. Dos planos consecutivos nunca comparten fuente.

Se agrega una **guarda al script** que aborta si alguna se rompe, y que imprime la
tabla de firmas. Sin eso volvemos a discutir lo mismo.

## V3. Los edificios en 2:30-2:40 y 3:00

Pregunta del user: *"qué se puede hacer que no sea saturación?"*

**La saturación no sirve para esto y esa es la respuesta.** Aplastar niveles no toca la
GEOMETRÍA: una ventana sigue siendo un rectángulo brillante con bordes rectos, y un
aire acondicionado sigue siendo una caja. Lo que delata no es el brillo, es que hay
horizontales y verticales perfectas.

Lo que sí las destruye:

| Técnica | Qué le hace |
|---|---|
| **`lenscorrection`** | Curva la imagen entera. Una recta deja de ser recta y el rectángulo desaparece |
| **Rotación no cardinal** (7°, 23°, 41°) | No quedan horizontales ni verticales |
| **Desenfoque fuerte más reafilado** | Los bordes se vuelven gradientes, no líneas |
| **Recorte mucho más cerrado** | Sin contexto no hay edificio |

Para esos dos planos van las cuatro juntas, no una.

## V4. Las medusas, sincronizadas de verdad

Hoy la imagen entra en **7:34** y la voz en **7:36**. Ya se pidió una vez y no se
cumplió.

Se corrige haciendo que el plano anterior dure 2 s más. Y se agrega al script una
**verificación de que el corte cae en el segundo pedido**, imprimiendo el tiempo real
de cada momento clave (alien, estallido, cada entrada del moog).

## V5. Las medusas, cómo se ven

Pedido: más lentas, un poco más de zoom, un pelín más de luz, y **que no tengan el
movimiento de una medusa terrestre**.

- Velocidad a 0,4x (hoy 0,67x).
- Recorte más cerrado todavía.
- `brightness` +0,04, apenas.
- **Reversa** en la escena final, que es lo que rompe el movimiento reconocible: una
  medusa pulsando al revés no se lee como animal.

## V6. Las entradas del moog, sincronizadas con cambio de imagen

Pedido: que cada entrada del moog coincida con un corte.

Como la línea del moog va a ser continua (A1), las "entradas" pasan a ser los cambios
de nota. El script va a leer los tiempos de nota desde `moog.py` y **colocar un corte
en cada uno**.

Y la entrada principal, 8:19-8:20, va con un plano único y sostenido, no con lo que hay
hoy.

## V7. La interferencia

Ya se bajó de 11 a 6 y hay dos tratamientos sin grano. Se revisa que los planos que el
user marcó (8:20 y 10:26) efectivamente no la lleven.

---

# ORDEN DE EJECUCIÓN

1. **Audio**: A1, A2, A4. Render y los tres QA. **El user valida el master.**
2. **A3** solo si confirma la idea del Re del Voyager.
3. **Escenas nuevas**: decidir si filma el charco. **El user valida los paths.**
4. **Recién ahí** el video: V1 a V7, con las guardas nuevas.
5. Escaneo de textos sobre la salida.
6. 4K solo con visto bueno.
