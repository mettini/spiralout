# 48 : Google Ads playbook (análisis 2026-08-22)

> Auditoría de solo lectura de la cuenta Spiral Out, hecha el **22/08/2026**.
> No se tocó nada en la cuenta: esto es diagnóstico + plan.
> Continúa `docs/34` (setup y optimización del 06/08). Acá se **responde la
> pregunta que el 34 dejó abierta** ("¿se movieron los términos precisos?") y se
> arma el playbook reusable para TX02/TX03.
>
> **Restricción dura del user (textual): "no voy a poner mas budget, es mejorar
> lo que hay".** Todo lo de acá es a presupuesto constante o menor.

---

## 1. Estado actual de la cuenta

**CID 204-637-9068 · Spiral Out · mettini@gmail.com · moneda ARS · GMT-03:00**

Una sola campaña, un solo ad group, un solo anuncio.

| Campo | Valor |
|---|---|
| Campaña | `ÆM · Heliopause — in-feed test 01` (ID 24064623003) |
| Tipo | Video · formato **In-feed** (único) |
| Estado | Enabled, **Limited by budget** |
| Presupuesto | ARS 2.500,00/día |
| Puja | **Target CPV** (el importe no se ve sin entrar en modo edición) |
| Networks | Solo YouTube ✓ (sin fuga a Display ni partners) |
| Idiomas | English, Spanish |
| Geo | 9 países: MX, AR, US, UK, DE, CO, NL, CA, AU |
| Fechas | 26/07/2026 al 26/10/2026 |
| Ad schedule | All day (sin dayparting) |
| Bid adjustments activos | **None** |
| Devices | All eligible (computers, mobile, tablet, TV screens) |
| Frequency capping | **None** |
| Audience segments | **Ninguno** (targeting 100% contextual por keyword) |
| Related videos | 3 (los tres visualizers, colgados del único anuncio) |
| Optimization score | **77,7%** |

### Métricas del período completo (26/07 al 21/08, 27 días)

| Métrica | Valor |
|---|---|
| Impresiones | 21.577 |
| TrueView views | 775 |
| **TrueView view rate** | **3,59%** |
| **TrueView avg. CPV** | **ARS 83,59** |
| Costo | ARS 64.778,39 |
| Clics | 23 · CTR 0,11% |
| Conversiones | 0,00 (no hay ninguna acción de conversión activa, ver §4.4) |

### Corrección de benchmark (importante)

`docs/34 §4` fija como meta **"view rate >15-20% in-feed = bueno"**. Ese número
está mal: 15-30% es el benchmark de **in-stream skippable**, donde el view se
cuenta a los 30 segundos de reproducción automática. En **in-feed** el anuncio
es un thumbnail en el feed y el "view" es un clic deliberado del usuario, así
que el view rate se comporta como un CTR de thumbnail: el rango típico es 0,5%
a 3%.

**Con 3,59% la campaña está por encima del rango típico de in-feed.** El view
rate NO es el problema de esta campaña. El problema es el CPV.

> Nota: `docs/34` también fija un target de CPV de USD 0,02-0,05. No lo traduje
> a ARS porque no verifiqué el tipo de cambio del período. Comparar contra la
> propia serie de la cuenta (ARS 68,50 del arranque) es más confiable que
> comparar contra un target en dólares sin el FX.

---

## 2. Qué se ajustó antes y si funcionó

### Lo que realmente se tocó

El `change history` completo (14 cambios) dice esto:

| Fecha | Cambio |
|---|---|
| 26/07 19:41 | **Se removieron las conversiones de YouTube** (follow-on views, channel subscriptions, engagements) |
| 26/07 20:09 | Campaña creada, ad group, 12 keywords broad, 1 responsive video ad, 4 platforms |
| 30/07 19:33 | 1 budget amount increased |
| **06/08 14:11** | **2 broad match keywords paused** |
| **06/08 14:17** | **29 negative broad match keywords added** |
| 10/08 | Cambios de seguridad del sistema (automáticos) |

**No hubo ajuste de público ni de dispositivos.** Las categorías `Audience` y
`Bidding` del historial están vacías (chips grises), `Active bid adj` está en
`None` y no hay ningún audience segment cargado. Coincide con lo que el propio
`docs/34 §6` declara: *"No se tocó dispositivo, horario, edad ni geo"*. El único
ajuste real del 06/08 fue **de keywords**.

### Antes vs después, a presupuesto constante

Comparo 30/07 al 05/08 (7 días, pre-ajuste, ya con delivery estable) contra
06/08 al 21/08 (16 días, post-ajuste). El gasto diario es prácticamente idéntico
en los dos tramos, así que la comparación es limpia.

| | Pre (30/07-05/08) | Post (06/08-21/08) | Δ |
|---|---|---|---|
| Gasto/día | ARS 2.534,65 | ARS 2.548,28 | +0,5% |
| Impresiones/día | 1.086,4 | 779,1 | **-28,3%** |
| **Views/día** | **37,0** | **29,0** | **-21,6%** |
| **CPV** | **ARS 68,50** | **ARS 87,87** | **+28,3%** |
| View rate | 3,41% | 3,72% | +9,3% |
| CTR | 0,12% | 0,11% | -8% |

**Veredicto: el ajuste del 06/08 no mejoró la eficiencia, la empeoró.**

El view rate subió un poco (3,41% → 3,72%), que era el objetivo declarado, pero
el CPV subió 28% y el CPV es el que manda cuando el presupuesto es fijo. A igual
plata se compran 8 views menos por día.

Puesto en plata: con los ARS 40.772,49 gastados después del 06/08, al CPV viejo
de 68,50 se habrían comprado **595 views**. Se compraron **464**. **131 views
perdidas** por el cambio.

> Caveat honesto: parte del alza de CPV puede ser inflación de subasta en ARS y
> no efecto del cambio. No lo puedo aislar. Pero la causa estructural sí se ve
> en el detalle de keywords de abajo, y apunta en la misma dirección.

### Por qué subió el CPV: se pausaron las baratas

Rendimiento por keyword del período completo (26/07 al 21/08):

| Keyword | Estado | Impr | Views | View rate | **CPV** | Costo |
|---|---|---|---|---|---|---|
| cosmic ambient | **Paused** | 5.446 | 195 | 3,58% | **77,77** | 15.165,43 |
| dark ambient | Eligible | 3.838 | 126 | 3,28% | 79,14 | 9.971,18 |
| steve roach | Eligible | 3.165 | 102 | 3,22% | 70,30 | 7.170,47 |
| atrium carceri | Eligible | 2.813 | 108 | 3,84% | **97,94** | 10.577,91 |
| lustmord | Eligible | 2.406 | 94 | 3,91% | **102,70** | 9.653,64 |
| space ambient | Eligible | 1.918 | 70 | 3,65% | **107,59** | 7.531,50 |
| ambient music | **Paused** | 1.402 | 49 | 3,50% | **55,97** | 2.742,30 |
| deep space ambient | Eligible | 256 | 17 | **6,64%** | 71,74 | 1.219,54 |
| drone music | Eligible | 253 | 13 | 5,14% | **51,88** | 674,47 |
| dark drone | Eligible | 41 | 1 | 2,44% | 71,95 | 71,95 |
| dungeon synth | Eligible | 29 | 0 | 0% | : | 0,00 |
| cryo chamber | Eligible | 10 | 0 | 0% | : | 0,00 |

Las dos keywords que se pausaron el 06/08 son **la primera y la segunda más
baratas con volumen real**: `ambient music` a ARS 55,97 y `cosmic ambient` a
ARS 77,77, ambas por debajo del promedio. Lo que quedó activo y absorbió el
presupuesto liberado es la camada cara: `space ambient` 107,59, `lustmord`
102,70, `atrium carceri` 97,94.

### Respuesta a la pregunta abierta de `docs/34`

> *"¿Se movieron los términos precisos? Si siguen muertos, no hay volumen en
> esos términos."*

Se movieron **parcialmente, y no los que importaban**. Comparando la tabla del
34 (al 05/08) contra la de hoy:

- **Despertaron los términos medios**, no los finos: `space ambient` pasó de 22
  a 1.918 impresiones, `dark ambient` de 698 a 3.838, `steve roach` de 596 a
  3.165, `atrium carceri` de 537 a 2.813, `lustmord` de 432 a 2.406.
- **Los términos finos siguen muertos**: `deep space ambient` 256, `drone music`
  253, `dark drone` 41, `dungeon synth` 29, `cryo chamber` 10. Los cinco juntos
  suman **589 impresiones, el 2,7% del total**, en 16 días con el presupuesto
  liberado a disposición.

**Conclusión: no hay volumen en los términos finos. La hipótesis del 06/08 queda
cerrada como negativa.** No era un problema de distribución de presupuesto, era
falta de inventario. El presupuesto liberado no fue a donde se esperaba: fue a
la segunda camada de términos, que son más caros que los que se pausaron.

Corolario sobre `drone music`: el 34 celebraba su 12,1% de view rate, pero era
una muestra de 66 impresiones. Con 253 impresiones bajó a 5,14%. Sigue siendo el
mejor CPV de la cuenta (51,88) y el segundo mejor view rate, pero **no tiene
volumen para sostener la campaña**.

---

## 3. Recomendaciones del optimization score

El score es **77,7%**. Hay tres recomendaciones pendientes y **una sola aporta
puntaje**.

### 3.1. "Optimize your budgets" (+22,3%) → **DESCARTAR**

Es el 100% del score que falta. Sus propias proyecciones semanales:

| Proyección de Google | Valor |
|---|---|
| TrueView views | **+304** |
| TrueView avg. CPV | **+ARS 163** |
| Costo | **+ARS 109.000** |

Dos razones para descartarla, y la segunda es la buena:

1. Viola la restricción del user (más presupuesto).
2. **Es mal negocio con los números de Google.** ARS 109.000 por 304 views da un
   costo marginal de **ARS 358 por view**, 4,3 veces el CPV actual de 83,59. Y
   Google mismo avisa que el CPV promedio sube ARS 163. Es comprar inventario
   peor y más caro.

**Consecuencia asumida: el score se queda clavado en 77,7% para siempre.** Está
bien. El optimization score de Google pondera fuerte las recomendaciones de
gasto: no es un KPI del proyecto y no hay que perseguirlo.

### 3.2. "Link your Google Analytics 4 property" (ID 538059451) → **APLICAR**

Aporta **0% al score** (está en la categoría Measurement, sin badge de
porcentaje). No cuesta plata ni toca el presupuesto, y conecta el tráfico del ad
con `spiralout.space`.

Es decisión del user: implica compartir datos entre productos de Google. Si la
respuesta es sí, la aplica él desde el panel.

### 3.3. "Try the new Google Ads mobile app" → **IGNORAR**

0% de score, es promoción de producto. No es una recomendación de optimización.

### 3.4. La recomendación que Google NO hace y es la más importante

**Reactivar las conversiones de YouTube.** El 26/07 a las 19:41 se removieron
las tres acciones de conversión:

- `YouTube follow-on views` → "Include in Conversions" cambiado a "No"
- `YouTube channel subscriptions` → "Include in Conversions" cambiado a "No"
- `Engagements (YouTube hosted)` → removida de los account-default goals

Por eso la cuenta reporta **0,00 conversiones** en todo el período. Son
exactamente las **earned actions** que `docs/34 §4` define como *la* métrica a
mirar ("subs, likes, views a los otros videos"). Se está tirando el dato que el
propio plan dice que es el más importante.

Sin esto no se puede responder la pregunta de fondo: **¿los 775 views se
convirtieron en alguien que se quedó?** No cuesta un peso reactivarlas.

---

## 4. Cómo optimizar TrueView a presupuesto constante

Ordenado por impacto esperado. Los cálculos de "views ganadas" son sobre la
ventana de 27 días y asumen que la plata liberada se recompra al CPV de los
segmentos buenos.

> **Regla de posicionamiento que no se rompe:** ÆM es faceless, misterioso,
> nicho ambient. **Nada de acá masifica el público.** Todas las acciones son
> podas: sacan segmentos caros que no resuenan, no agregan audiencia genérica.
> Por eso no hay ninguna recomendación de "ampliar targeting", "sumar audiencias
> afines" ni "activar optimized targeting".

### 4.1. Reactivar `cosmic ambient` y `ambient music` (impacto alto)

Es la reversión del ajuste del 06/08, pero **en un escenario distinto al que lo
motivó**. La razón original para pausarlas fue la contaminación: `cosmic
ambient` metía el anuncio en canales de dormir bebés y relax profundo. **Esa
contaminación hoy está bloqueada por las 29 negativas**, que se cargaron seis
minutos después de la pausa y nunca convivieron con las keywords activas.

Nunca se testeó `cosmic ambient` **con** las negativas puestas. Eso es lo que
hay que probar.

- `ambient music`: CPV 55,97 (el más barato con volumen), 36% por debajo del mix
  actual de 87,87.
- `cosmic ambient`: CPV 77,77, 11% por debajo del mix actual.

Impacto esperado: el CPV del mix vuelve de 87,87 hacia la zona 72-78. Sobre un
gasto mensual de ~ARS 76.400, eso es pasar de ~870 views/mes a **1.000-1.060
views/mes**. **+15% a +22% sin tocar el presupuesto.**

Cómo controlarlo: reactivar de a una, `ambient music` primero (la más barata y
la de menor volumen, o sea el riesgo más chico), y mirar el CPV del mix a los
5 días.

### 4.2. Excluir Alemania (impacto alto, riesgo nulo)

Rendimiento por país (26/07 al 21/08):

| País | Impr | Views | View rate | **CPV** | Costo |
|---|---|---|---|---|---|
| Colombia | 1.398 | 65 | **4,65%** | **59,98** | 3.898,57 |
| Mexico | 8.707 | 296 | 3,40% | **62,19** | 18.409,38 |
| Argentina | 3.547 | 124 | 3,50% | 69,67 | 8.638,89 |
| United States | 2.786 | 123 | **4,41%** | 84,68 | 10.415,88 |
| Netherlands | 845 | 26 | 3,08% | 90,22 | 2.345,68 |
| United Kingdom | 1.512 | 65 | **4,30%** | 110,69 | 7.194,55 |
| Canada | 770 | 32 | 4,16% | 155,57 | 4.978,26 |
| Australia | 545 | 20 | 3,67% | 174,79 | 3.495,74 |
| **Germany** | **1.467** | **24** | **1,64%** | **225,06** | **5.401,45** |

**Alemania es el peor país en las dos dimensiones a la vez**: el view rate más
bajo de todos (1,64%, menos de la mitad del promedio) y el CPV más alto (225,06,
2,7 veces el promedio). Gastó ARS 5.401 (8,3% del total) para traer 24 views
(3,1% del total).

No es "caro pero rinde". Es caro **y** no resuena. Excluir.

Esos ARS 5.401 recomprados a CPV 62 (MX/CO) dan 87 views. **Neto +63 views.**

### 4.3. Bajar 18-24 (impacto alto, refuerza el posicionamiento)

Rendimiento por edad (26/07 al 21/08):

| Edad | Impr | Views | View rate | **CPV** | Costo |
|---|---|---|---|---|---|
| **18-24** | **1.672** | **40** | **2,39%** | **197,35** | **7.894,11** |
| 25-34 | 4.014 | 119 | 2,96% | 90,06 | 10.716,60 |
| 35-44 | 3.236 | 82 | 2,53% | 66,13 | 5.423,06 |
| 45-54 | 2.728 | 73 | 2,68% | 98,47 | 7.188,34 |
| **55-64** | 1.945 | 82 | **4,22%** | **60,68** | 4.976,13 |
| 65+ | 1.565 | 63 | 4,03% | 134,16 | 8.452,35 |
| **Unknown** | 6.417 | 316 | **4,92%** | **63,70** | 20.127,80 |

18-24 es el peor bucket con volumen: view rate 2,39% y CPV 197,35 (2,4x el
promedio). Consume el 12,2% del gasto para traer el 5,2% de los views.

**Esto no es masificar al revés, es lo contrario: es afinar hacia donde el nicho
ya está.** Los buckets que rinden son 55-64 (view rate 4,22%, CPV 60,68) y el
enorme `Unknown` (4,92%, CPV 63,70, probablemente usuarios sin sesión o con
privacidad activada, que es un perfil muy coherente con el público de dark
ambient). El dark ambient no es música de 18-24.

Recomendación: excluir 18-24, o bid adjustment -50% si se prefiere ser
conservador. **No excluir `Unknown` bajo ningún concepto: es el mejor segmento
de la cuenta** (41% de los views a CPV por debajo del promedio).

Esos ARS 7.894 recomprados a CPV 63,70 dan 124 views. **Neto +84 views.**

Sobre género: Female 3,08% / CPV 88,90 contra Male 3,00% / CPV 102,25. La
diferencia de view rate es ruido. **No tocar género**, no hay señal.

### 4.4. Reactivar las conversiones de YouTube (impacto: desbloquea todo)

Ver §3.4. No gana views por sí solo, pero sin esto las próximas decisiones se
siguen tomando a ciegas. Es la que hay que hacer primero en orden cronológico,
aunque no sea la de mayor impacto directo.

### 4.5. Poner frequency capping (impacto medio, gratis)

Hoy está en `None`. 21.577 impresiones en 27 días sobre un público nicho
repartido en 9 países significa que hay usuarios viendo el mismo thumbnail
muchas veces. En in-feed, si alguien no clickeó el thumbnail las primeras dos
veces, no lo va a clickear la quinta.

Un cap de 2-3 impresiones por usuario por semana redirige impresiones hacia
usuarios nuevos **sin gastar un peso más**.

No pude cuantificarlo porque no vi los datos de frecuencia (ver §6), pero la
dirección es correcta y el downside es nulo.

### 4.6. Rotar 2 o 3 anuncios en vez de 1 (impacto medio, gratis)

Hay **un solo anuncio** en la cuenta. El ad rotation ya está en *"Optimize:
prefer best performing ads"*, pero con un anuncio no hay nada que optimizar: la
función está encendida y ociosa.

Los tres visualizers están cargados como **related videos** del anuncio único,
no como anuncios separados. Subir Recursion (3:00) y Crossing (13:00) como
anuncios adicionales en el mismo ad group le da al sistema thumbnails y títulos
distintos para elegir. Costo cero, y es la palanca más directa sobre el view
rate (que en in-feed es, literalmente, performance de thumbnail).

`docs/24` es la guía de thumbnails.

### 4.7. Computers: bid adjustment -50%, NO excluir (impacto medio, con matiz)

Rendimiento por dispositivo (26/07 al 21/08):

| Dispositivo | Impr | Views | View rate | **CPV** | Costo |
|---|---|---|---|---|---|
| Tablets | 6.355 | 292 | **4,59%** | **75,06** | 21.916,22 |
| Mobile phones | 14.044 | 460 | 3,28% | 82,18 | 37.802,02 |
| **Computers** | **1.178** | **23** | **1,95%** | **220,01** | **5.060,15** |
| TV screens | **0** | 0 | : | : | **0,00** |

Computers es el peor: CPV 220,01 (2,6x el promedio) y el view rate más bajo.
ARS 5.060 por 23 views.

**Pero acá corresponde frenar.** `docs/34 §6` dice: *"lo de desktop además
estaba mal medido: en ambient la tele y la compu es donde se escucha largo, no
donde se clickea"*. Ese argumento era correcto contra un análisis por clics, y
sigue siendo parcialmente válido acá: el view rate mide qué tan barato es
**conseguir** el view, no cuánto vale ese view después. Es perfectamente posible
que los 23 views de desktop tengan 10 veces el watch-time de los de mobile.

**No se puede saber, porque las conversiones de YouTube están apagadas (§3.4).**

Recomendación honesta: bid adjustment **-50%** en computers (baja el gasto sin
cerrar la puerta) y **no decidir de verdad hasta tener 2 semanas de earned
actions**. Si el watch-time de desktop justifica el CPV, se revierte.

Si igual se prefiere cortar: esos ARS 5.060 a CPV 75,06 dan 67 views, neto +44.

### 4.8. TV screens está habilitado y da 0 impresiones (dato para TX02)

`Devices: All eligible devices (computers, mobile, tablet, and TV screens)`,
pero TV tuvo **0 impresiones y ARS 0 de gasto en 27 días**.

Motivo: **el formato In-feed no se sirve en pantallas de TV.** El ajuste de
dispositivo dice que está permitido, pero el inventario no existe para ese
formato.

Es una pena, porque para visualizers ambient de 8 a 13 minutos la TV es el
contexto natural de escucha. Abrir ese inventario requiere **in-stream
skippable**, que cambia la economía del view (el view se cuenta a los 30
segundos de reproducción automática, el CPV sube pero el watch-time es real).

**No lo recomiendo como cambio global a este presupuesto.** Queda anotado como
el experimento de TX02 (§5).

### Resumen del impacto acumulado

Los segmentos malos (Alemania + 18-24 + computers) se solapan entre sí (un
usuario alemán de 20 años en desktop cuenta en los tres), así que las ganancias
no son aditivas. Estimación conservadora del conjunto §4.1 + §4.2 + §4.3:

- CPV objetivo: de **ARS 83,59** a la zona de **ARS 65-70**.
- Views: **+15% a +25%** sobre los 775 actuales, con **el mismo presupuesto**.

---

## 5. Playbook reusable para TX02 y TX03

Lo que hay que repetir, lo que hay que cambiar y lo que ya está descartado.

### 5.1. Setup base (repetir tal cual)

Todo el §0 y §1 de `docs/34` sigue vigente y está verificado. Lo que se confirma
después de un mes de datos:

- **Networks: solo YouTube.** Sin Display, sin video partners. ✓
- **Auto-apply: apagado.** Que Google no aplique recomendaciones solo. ✓
- **Puja: Target CPV.** Es la única sensata para una campaña de views.
- **Idiomas: English + Spanish.**
- **Un ad group, targeting contextual por keyword.**

### 5.2. Segmentación que funcionó (arrancar con esto)

**Geo, en dos tiers desde el día uno** en vez de un pool plano de 9 países:

| Tier | Países | Por qué |
|---|---|---|
| **Tier 1 (arrancar acá)** | **MX, CO, AR** | CPV 60-70, view rate 3,4-4,65%. Es donde el peso rinde. |
| **Tier 2 (sumar si sobra)** | **US, UK** | CPV más alto (85-111) pero view rate excelente (4,3-4,4%). El view vale más: es el mercado real de ambient (Bandcamp, playlists, prensa). |
| **No incluir** | **DE, AU, CA, NL** | DE es el peor en las dos dimensiones. AU y CA tienen CPV de 155-175 sin view rate que lo justifique. |

**Edad:** excluir **18-24** desde el arranque. El público está en **55-64,
35-44 y sobre todo en `Unknown`**. No excluir `Unknown` nunca.

**Género:** no segmentar, no hay señal.

**Dispositivos:** dejar todos, con bid adjustment negativo en computers si el
CPV se dispara. Saber de antemano que **TV screens va a dar 0 con in-feed**.

**Frequency capping:** ponerlo desde el día uno, 2-3 impresiones por usuario por
semana.

### 5.3. Keywords: la lección de escala

El aprendizaje más caro del mes: **los términos de nicho fino no tienen volumen
en YouTube**. `cryo chamber` (10 impresiones), `dungeon synth` (29), `dark
drone` (41) y `deep space ambient` (256) no sostienen una campaña ni con el
presupuesto liberado a su disposición.

La estructura que funciona es una pirámide:

1. **Base ancha y barata**: `ambient music`, `cosmic ambient`, `dark ambient`.
   Traen el volumen a CPV 56-79. **Van con las 29 negativas puestas** (§5.4), sin
   eso contaminan con sleep/baby/wellness.
2. **Medio por artista**: `steve roach`, `atrium carceri`, `lustmord`,
   `space ambient`. CPV 70-108. Traen público más afín pero más caro.
3. **Cola fina**: los cinco términos precisos. Dejarlos activos porque no
   cuestan nada, pero **no esperar volumen de ahí y no diseñar la campaña
   alrededor de ellos**.

Para TX02 la lista base sale de `docs/28_sonic_neighbors_aem.md`, con los
mismos tres niveles.

### 5.4. Las 29 negativas (copiar y pegar en cada transmission)

Bloquean el cluster sleep/wellness/baby que es lo que contamina los términos
anchos de ambient:

```
432 hz · 528 hz · anxiety relief · asmr · babies · baby · baby sleep ·
binaural beats · chakra · deep relaxation · focus music · guided meditation ·
healing frequency · lullaby · manifestation · massage · newborn · nursery ·
pink noise · reiki · sleep music · sleep sounds · solfeggio · spa ·
stress relief · study music · tinnitus · white noise · yoga
```

**Lo que a propósito NO se excluye: "sleep" y "meditation" pelados.** Mucha
gente que escucha dark ambient de verdad busca eso. Excluirlos corta público
real. (Criterio heredado de `docs/34 §6`, se mantiene.)

### 5.5. Anuncios: 3 desde el arranque, no 1

Cargar los tres visualizers como **tres anuncios** en el mismo ad group, no como
related videos de uno solo. Con ad rotation en "prefer best performing ads", el
sistema encuentra el mejor thumbnail en días. Es gratis y en in-feed el
thumbnail es el 90% del view rate.

### 5.6. Medición: encender antes de gastar el primer peso

**Dejar activas las conversiones de YouTube desde el minuto cero**: follow-on
views, channel subscriptions, engagements. Son las earned actions. Sin ellas la
campaña reporta 0 conversiones y todas las decisiones se toman mirando CPV, que
es media película.

Métricas a mirar, en orden:

1. **CPV** (la que manda con presupuesto fijo)
2. **Earned actions** (subs y views ganados por el canal)
3. **View rate** (benchmark real de in-feed: 0,5-3% es normal, >3% es bueno)
4. **Impresiones** por keyword y por geo, para detectar quién se come el budget
5. Los clics **no**. Con 23 clics en 27 días no hay nada que analizar ahí, y el
   asistente de Google va a insistir en analizarlos.

### 5.7. Descartado, no volver a intentarlo

- **Placements por canal a este presupuesto.** Un placement no agrega alcance,
  lo restringe: encierra el anuncio en esos canales y Google se niega a guardar
  si el inventario no alcanza para gastar el budget diario. Haría falta una
  lista de 20 a 40 canales. Detalle completo y handles verificados en
  `docs/34 §6`.
- **Subir el presupuesto porque lo pide el optimization score.** Los propios
  números de Google dan un costo marginal de ARS 358 por view (§3.1).
- **Analizar la campaña por clics.** Ver §5.6 punto 5.
- **Ampliar el público para levantar volumen.** Rompe el posicionamiento y, con
  presupuesto fijo, ni siquiera trae más views: trae impresiones más baratas y
  view rate peor.

### 5.8. Ritmo

`docs/31` manda: **una prueba por mes**, sin correr otros levers en paralelo
(dilución). Los cambios de §4 se aplican **de a uno o de a dos**, con 5 a 7 días
de lectura entre tandas. Si se aplican los siete juntos no se va a saber cuál
funcionó, que es exactamente lo que pasó con el ajuste del 06/08.

Orden sugerido:

| Tanda | Qué | Cuándo leer |
|---|---|---|
| 1 | Reactivar conversiones YouTube + frequency cap | inmediato, no esperar |
| 2 | Reactivar `ambient music` + excluir Alemania | 5-7 días |
| 3 | Excluir 18-24 + reactivar `cosmic ambient` | 5-7 días |
| 4 | Sumar 2 anuncios más | 7 días |
| 5 | Bid adj -50% computers (solo si las earned actions no lo justifican) | 7 días |

---

## 6. Qué NO se pudo ver (y por qué)

Para que nadie tome estos huecos por datos:

- **Alcance único y frecuencia.** Las columnas de unique reach / avg. impression
  frequency no estaban en la vista y no quise modificar la configuración de
  columnas de la cuenta (la auditoría era de solo lectura). **No lo vi.**
- **El importe del Target CPV.** La página de settings muestra la estrategia
  ("Target CPV") pero el número solo aparece al entrar en modo edición del
  campo. No entré para no arriesgar un cambio accidental. **No lo vi.**
- **Desglose por hora del día y día de la semana.** El botón `Segment` de la
  tabla no llegó a renderizar de forma estable en varios intentos. No hay ad
  schedule configurado (`All day`), así que tampoco había datos en esa pantalla.
  **No lo vi.**
- **Placements individuales** (canales y videos concretos donde apareció el ad).
  La sección Content solo devolvió filas de tipo `Keyword`, ninguna de tipo
  `Placement`. Con targeting contextual y formato in-feed, Google no reporta el
  detalle de emplazamientos acá. **No está disponible.**
- **Retención del video** (view-through a 25/50/75/100%). No estaba en las
  columnas de la vista. **No lo vi.**
- **Earned actions** (subs, likes, views ganados). No existen como dato: las
  conversiones de YouTube están desactivadas desde el 26/07 (§3.4). **No hay
  dato que ver.**
- **El copy exacto del anuncio.** La tabla de Ads no renderiza las filas en el
  navegador (mismo problema que reportó `docs/34 §6`). Solo pude confirmar que
  hay **1 anuncio** y que es un responsive video ad con 3 related videos.

---

## 7. Cambios aplicados en la cuenta (2026-08-22)

> A diferencia de todo lo anterior (que era diagnóstico de solo lectura), esta
> sección registra **escrituras reales** sobre la cuenta, hechas el 22/08/2026
> con autorización explícita del user sobre cuatro puntos y nada más.
>
> **No se tocó:** presupuesto (sigue ARS 2.500,00/día), estrategia de puja
> (sigue Target CPV), dispositivos (siguen todos habilitados, computers NO se
> excluyó a propósito, ver §4.7), anuncios ni creatividades. **No se aplicó
> ninguna recomendación del optimization score**, en particular "Optimize your
> budgets" (§3.1), que sigue pendiente y descartada.

### 7.1. Qué se aplicó y quedó verificado

| # | Cambio | Valor exacto | Verificación |
|---|---|---|---|
| 1 | Reactivar keywords pausadas el 06/08 | `ambient music` y `cosmic ambient` pasadas de `Paused` a `Eligible` | Recarga de la tabla Content: las 12 keywords en `Eligible`. Las 29 negativas intactas (`1 - 29 of 29`) |
| 2 | Excluir Alemania | `Germany (country)` agregada a Location exclusions a nivel campaña | Recarga: `Excluded location: Germany`, `1 - 1 of 1`. En Settings: `Locations: Targeted: Argentina (country) + 7 more · Excluded: Germany (country)` (antes era "+8 more") |
| 4a | Reactivar conversiones de YouTube | Los dos goals puestos como **account-default**: `Engagements` (contiene `YouTube channel subscriptions`) y `YouTube follow-on views` | Tabla de conversion actions: columna `Included in account-level goals` pasó de **No** a **Yes** en las dos acciones. Ambas siguen `Primary` + `Active`. Cada goal pasó de `Campaigns 0 of 1` a `1 of 1` |
| 4b | Frequency capping | **3 impresiones por usuario por semana** (`Cap impression frequency` = 3 per week). `Cap view frequency` quedó **sin tildar** | Recarga de Settings: `Frequency capping: 3 impressions per week` |

Sobre el punto 4a: el `docs/48 §3.4` hablaba de **tres** acciones removidas el
26/07. En la cuenta hoy existen **dos** conversion actions (`YouTube channel
subscriptions` y `YouTube follow-on views`); "Engagements" no es una tercera
acción sino el **grupo de goal** que contiene a channel subscriptions. Las dos
que existen quedaron reincorporadas, así que la reactivación está completa.

### 7.2. Qué NO se pudo aplicar

**Excluir el rango de edad 18-24: NO QUEDÓ APLICADO.**

Se intentó **dos veces** con el control correcto (tabla de Demographics > Age,
seleccionar solo la fila `18 - 24` > `Edit` > `Exclude from ad group`). Las dos
veces Google devolvió el mismo error de servidor:

```
Exclude age ranges from ad group
Status: Finished with errors
Changes 7 · Successful 0 · Errors 7
"An error occurred. Please try again later."
```

Detalle de lo que Google intentó hacer internamente: `1 negative age range
added` + `6 age ranges added`. Eso es coherente con excluir 18-24 (al excluir
un bucket, el sistema materializa los otros 6 como targeting positivo
explícito). Los 7 items fallaron y **Successful = 0**, o sea que **no quedó
nada a medio aplicar**.

Verificado después de los dos intentos: la tabla de Age sigue con los 7 buckets
en `Eligible` (`1 - 7 of 7`) y **`Unknown` intacto y Eligible**, que era la
condición dura del user (es el mejor segmento: 41% de los views, CPV 63,70).

> Nota de método: los labels del log de errores aparecen como "Unknown targeting
> value", pero eso es el placeholder de la UI cuando no puede resolver el nombre
> del criterio, **no** el bucket `Unknown`. Se confirmó mirando el estado real
> de la tabla después de cada intento.

No se buscó un camino alternativo para forzarlo. El único otro camino que
ofrece la UI (`Edit demographics`) abre el constructor de **New audience**, que
crearía un audience segment nuevo: fuera del alcance autorizado y contrario al
targeting 100% contextual de esta campaña (§1). Se canceló sin guardar.

**Queda pendiente:** reintentar la exclusión de 18-24 más adelante. Es un error
transitorio de Google, no un problema de permisos ni de configuración.

### 7.3. Por qué 3 impresiones por semana

El `§4.5` recomendaba "2-3 por usuario por semana" sin cerrar el número. Se
eligió **3 por semana** y se capó **impresiones**, no views:

1. **Se capan impresiones, no views.** El desperdicio está del lado de la
   impresión (el thumbnail que se muestra y no se clickea). Capar views
   limitaría justamente lo que estamos comprando.
2. **En in-feed el thumbnail se agota rápido.** El view es un clic deliberado.
   Si alguien no clickeó en las primeras 2 o 3 apariciones, la quinta no lo va a
   convencer. Cortar la cola larga de 5+ exposiciones libera inventario hacia
   usuarios nuevos sin gastar un peso más.
3. **Por qué no 2.** La campaña está `Limited by budget` con presupuesto fijo.
   Un cap de 2 corre el riesgo de estrangular el delivery y obligar al sistema a
   comprar inventario más caro para llegar a los ARS 2.500 diarios, que es
   exactamente el efecto que queremos evitar (es lo que pasó con el ajuste del
   06/08, §2). 3 por semana es el punto que poda sin ahogar.
4. **Público nicho.** Con ~779 impresiones/día sobre dark ambient, un poco de
   repetición ayuda al reconocimiento. 3 por semana (unas 12-13 por mes) deja
   espacio a eso sin caer en la saturación.

Si a las 2 semanas el volumen de impresiones cae mucho y el CPV no baja, el cap
es el primer sospechoso y se sube a 4 o 5 por semana.

### 7.4. Qué mirar en 2 semanas (lectura el 2026-09-05)

**Comparar contra el período 06/08 al 21/08**, que es el tramo post-ajuste del
06/08 y la línea de base contra la que se hicieron todos estos cambios:

| Métrica | Base (06/08-21/08) | Objetivo | Fracaso |
|---|---|---|---|
| **CPV** | **ARS 87,87** | **≤ ARS 78** (zona 72-78, §4.1) | > ARS 88 |
| **Views/día** | **29,0** | **≥ 33** | < 29 |

Las dos se miran juntas: el CPV es el que manda con presupuesto fijo, y
views/día es la traducción a resultado. Con el gasto diario constante en ~ARS
2.548 las dos se mueven en espejo, así que si una mejora y la otra no, hay que
revisar que el gasto diario no haya cambiado.

Secundarias, en este orden:

1. **Earned actions** (`Conversions` en la campaña). Hasta hoy reportaba
   **0,00** porque los goals no eran account-default. Con 4a aplicado tendría
   que empezar a reportar. **Si sigue en 0,00 a los 7 días, el punto 4a no
   funcionó** y hay que revisarlo. Es el dato que desbloquea la decisión de
   computers (§4.7).
2. **Impresiones/día**: base 779,1. Si se desploma, sospechar del frequency cap
   (§7.3 punto 4).
3. **CPV por keyword** de `ambient music` y `cosmic ambient`: la hipótesis de
   §4.1 es que con las 29 negativas puestas rinden como antes (55,97 y 77,77).
   Si `cosmic ambient` vuelve a subir, la contaminación sleep/baby no estaba
   del todo bloqueada y hay que ampliar las negativas.

**Caveat:** se aplicaron cuatro cambios juntos, lo cual viola el ritmo de una
prueba por vez de `§5.8`. Fue decisión explícita del user. Consecuencia asumida:
si el CPV mejora no vamos a saber cuánto aportó cada palanca. Lo que sí se puede
aislar es Alemania (mirando el desglose por país) y las dos keywords (mirando el
desglose por keyword). El frequency cap es el único que no se puede aislar sin
datos de frecuencia, que siguen sin estar en la vista (§6).

---

## 8. Segunda ronda de ajustes (2026-08-28)

Disparador: el user vio en YouTube Analytics que mobile es 69,6% del watch time
y México el 26,9% de las vistas, y propuso apuntar más a mobile y a México.

**La trampa de ese dato, y por qué no se siguió tal cual.** Esas métricas son del
CANAL, y la campaña es la que trae la mayoría del tráfico: si los ads se sirven en
México, las vistas vienen de México. Reforzar México sería reforzar dónde ya
compramos, no dónde hay interés. Y Google se fue a México solo porque es mercado
barato: la puja optimiza CPV y se va a donde el view sale menos.

### Los datos de la CAMPAÑA (29/07 al 27/08)

| País | Impr | Views | View rate | CPV | Costo | Conv |
|---|---|---|---|---|---|---|
| México | 9.912 | 333 | **3,36%** | 76,12 | **25.348** | 0 |
| Argentina | 3.985 | 143 | 3,59% | **67,85** | 9.703 | **1** |
| Estados Unidos | 3.189 | 138 | 4,33% | 87,75 | 12.110 | 0 |
| Reino Unido | 1.747 | 73 | 4,18% | 107,23 | 7.828 | 0 |
| **Colombia** | 1.601 | 71 | **4,43%** | **64,51** | 4.580 | 0 |
| Países Bajos | 979 | 28 | 2,86% | 93,49 | 2.618 | 0 |
| Canadá | 885 | 37 | 4,18% | **149,43** | 5.529 | 0 |
| Australia | 632 | 24 | 3,80% | **163,21** | 3.917 | 0 |

**México tiene el peor view rate de los mercados grandes y se lleva el 35% del
presupuesto.** Colombia tiene el mejor view rate Y el CPV más barato con el 7%.

| Dispositivo | Impr | Views | View rate | CPV | Costo |
|---|---|---|---|---|---|
| Mobile | 16.410 | 532 | 3,24% | 90,00 | 47.881 |
| Tablet | 6.707 | 317 | **4,73%** | **69,71** | 22.098 |
| Computer | 1.284 | 21 | **1,64%** | **195,24** | 4.100 |

**El cruce que importa:** tablet se lleva el 36% de los views pero sólo el 26,3%
del watch time; mobile es el 61% de los views y el 69,6% del watch time. Un view
de mobile rinde ~1,5 veces más minutos que uno de tablet. Costo por punto de watch
time: mobile 688, tablet 840, computer 1.281. **Mobile gana**, que era el instinto
del user. Tablet parece mejor sólo si se mira el CPV aislado.

### Aplicado y verificado

1. **Colombia bid adjustment +30%.** Mejor view rate y CPV más barato del tablero
   con apenas el 7% del gasto.
2. **Canadá y Australia excluidos.** CPV 149 y 163 (2 veces el promedio), 13% del
   gasto para el 7% de los views. Exclusiones totales ahora: Alemania, Canadá,
   Australia.
3. **Computadoras sacadas del targeting de dispositivos.** View rate 1,64%, CPV
   2,3 veces el promedio y el peor rendimiento por minuto. Cierra la decisión que
   había quedado pendiente en §5 esperando earned actions: ahora hay dato en los
   dos ejes. Quedan mobile, tablet y TV.
4. **México y Argentina sin tocar**, Estados Unidos y Reino Unido como testigo,
   que era lo que el user pidió dejar para comparar.

### Lo que NO se pudo hacer

**No hay ajuste de puja por dispositivo** en el panel de esta campaña: con Target
CPV en video sólo se ofrece prender o apagar cada dispositivo, no un multiplicador.
O sea que "mobile arriba" se logra de forma indirecta, sacando computadoras y
dejando que el presupuesto se reparta entre mobile y tablet.

### Qué mirar el 2026-09-11 (dos semanas)

Base contra la que comparar (29/07 al 27/08): CPV **ARS 84,57**, view rate
**3,69%**, 847 views en 30 días (28,2/día).

- Si el CPV **sube** pero el view rate sube más, va bien: se sacó inventario barato
  y desenganchado.
- Si Colombia no crece en impresiones, el +30% no alcanzó contra el CPV bajo de
  México y hay que subirlo más o bajar México.
- Chequear que `Conversions` deje de reportar 0,00. Los goals se reactivaron el
  22/08 y a esta fecha sigue habiendo una sola conversión, de Argentina.
- **Sigue pendiente la exclusión de 18-24**, que falló dos veces con error de
  servidor de Google el 22/08.

---

# Segunda revisión (2026-09-14)

> Se entró a la cuenta a verificar si los cambios del 22/08 funcionaron y si hacía
> falta ajustar algo más. **El ajuste del 22/08 funcionó.** Se aplicaron tres cambios
> nuevos, esta vez apuntados a conversión.

## 1. Qué se había aplicado del playbook

El 22/08 entre las 20:20 y las 20:37 se aplicaron, en este orden:

| Hora | Cambio | Sección |
|---|---|---|
| 20:20 | 2 broad match keywords enabled (`cosmic ambient`, `ambient music`) | §4.1 |
| 20:22 | 1 negative country changed (Alemania, más Canadá y Australia) | §4.2 |
| 20:31 | Campaign changed (entra el +30% de Colombia) | no estaba en el playbook |
| 20:36 | Engagements (YouTube hosted) added · channel subscriptions a "Yes" | §3.4 |
| 20:37 | YouTube follow-on views added · a "Yes" | §3.4 |

Y **no se tocó nada más** entre el 22/08 y el 14/09. O sea que la ventana posterior es
una medición limpia del efecto.

Quedaron sin aplicar: §3.2 (GA4), §4.3 (18-24), §4.5 (frequency capping), §4.6 (rotar
anuncios), §4.7 (computers -50%).

## 2. El resultado: el ajuste del 22/08 funcionó

Período 23/08 al 14/09 (23 días) contra el período anterior de igual largo:

| | 23/08 al 14/09 | Δ |
|---|---|---|
| Costo | ARS 56.987,84 | -1.297,68 (plano) |
| **TrueView CPV** | **ARS 68,66** | **-12,97 (-16%)** |
| **TrueView views** | **830** | **+116 (+16%)** |
| Impresiones | 28.436 | +8.639 |
| TrueView view rate (in-feed) | 2,92% | -0,69 pp |
| Clics | 27 · CTR 0,09% | +3 · -0,03 pp |
| **Conversiones** | **17** · conv. rate 2,02% · ARS 3.352/conv | antes no se medían |

A plata constante, **16% más views y 16% más baratas**. El view rate bajó, y está bien:
es el intercambio esperado de comprar más inventario a menor precio.

**Esto revierte el daño del 06/08**, que había subido el CPV un 28%. El CPV vuelve de
87,87 a 68,66, o sea por debajo incluso del 68,50 pre-ajuste.

## 3. Lo que habilitaron las conversiones

Por primera vez hay datos de conversión, y ordenan la decisión. Período 23/08 al 14/09:

| País | Impr | Views | View rate | CPV | Costo | Conv | Costo/conv |
|---|---|---|---|---|---|---|---|
| **Argentina** | 5.837 | 177 | 3,03% | 62,59 | 11.078,26 | **7** | **1.582,61** |
| México | 13.596 | 343 | 2,52% | 73,88 | 25.341,01 | 8 | 3.167,63 |
| Colombia | 4.130 | 151 | **3,66%** | **54,19** | 8.183,16 | 2 | **4.091,58** |
| Estados Unidos | 2.752 | 104 | **3,78%** | 71,92 | 7.479,35 | 0 | n/d |
| Reino Unido | 1.244 | 28 | 2,25% | 52,24 | 1.462,79 | 0 | n/d |
| **Países Bajos** | 671 | 20 | 2,98% | **140,82** | 2.816,38 | **0** | n/d |

**El hallazgo que cambia la lectura: el CPV y el view rate NO predicen la conversión.**
Colombia tiene el mejor CPV de la cuenta (54,19) y el mejor view rate (3,66%), y es el
PEOR costo por conversión de los tres países que convierten (4.091,58). Argentina tiene
peor view rate que Colombia y convierte a menos de la mitad de costo.

Hasta ahora la cuenta se venía optimizando por CPV porque era lo único que había. Con
conversiones prendidas, optimizar por CPV puede empujar plata exactamente al lugar
equivocado.

## 4. Los tres cambios aplicados el 14/09

### 4.1. Países Bajos excluido

CPV 140,82, más del doble del promedio de la cuenta (68,66), 20 views y cero
conversiones sobre ARS 2.816 gastados. Es el mismo perfil exacto que tenía Alemania
cuando se la excluyó: caro **y** sin resonancia.

Efecto inmediato medido sobre la misma ventana: el CPV del total baja de 68,66 a
**66,68** con solo sacarla del cálculo.

Exclusiones de la campaña ahora: Países Bajos, Alemania, Canadá, Australia.

### 4.2. Se le sacó el +30% a Colombia

Ese ajuste se había puesto el 22/08 y **no estaba en el playbook**. Con los datos de
hoy es contraproducente: está empujando presupuesto hacia el peor costo por conversión
de la cuenta. Queda en "—".

### 4.3. Argentina pasa a +30%

Mejor costo por conversión de la cuenta (1.582,61, la mitad que México), mejor tasa de
conversión (3,91%) y segundo mejor CPV (62,59). Era el único país bueno sin ajuste.

## 5. Lo que NO se tocó, y por qué

**Estados Unidos y Reino Unido**, cero conversiones sobre ARS 8.942. Tentador cortarlos
y sería un error de muestra: son 132 views entre los dos y, a la tasa de conversión
promedio de la cuenta (2,02%), lo esperado son 2 o 3 conversiones. Cero está dentro del
ruido. Además Estados Unidos tiene el mejor view rate de la cuenta (3,78%). **Se
revisan en dos semanas**, no ahora.

**El presupuesto**, que sigue en ARS 2.500/día. Google empuja el "Fix budget" en cada
pantalla. Sigue siendo mal negocio por lo de §3.1: sus propias proyecciones dan un
costo marginal de ARS 358 por view, cinco veces el CPV actual.

## 6. Advertencia sobre las 17 conversiones

Son **engagements de YouTube**: suscripciones al canal, follow-on views y engagements
del video. **No son ventas ni visitas al sitio.** Sirven para lo que se usaron acá, que
es comparar países entre sí con la misma vara, y no sirven para calcular retorno.

## 7. GA4: qué estaba y qué faltaba (corrección)

Este playbook decía en §3.2 que faltaba "vincular GA4", y la primera versión de esta
revisión lo repitió sin verificarlo. **Estaba a medias y conviene dejar la distinción
escrita, porque son dos cosas distintas que se confunden todo el tiempo:**

| | Estado al 14/09 |
|---|---|
| GA4 instalado en `spiralout.space` | **SÍ**, desde antes. Measurement ID `G-4VMFWJJE14` |
| Propiedad GA4 vinculada a Google Ads | **NO**. Property ID 538059451, marcada "unlinked" |

Lo primero mide el sitio. Lo segundo es lo que deja que Ads **vea** esas métricas y
pueda atribuir. Tener el tag puesto no vincula nada.

Detalle que también estaba mal contado: **no es Tag Manager.** Es el snippet directo de
GA4 (`gtag.js`). Confunde porque se sirve desde el dominio `googletagmanager.com`, pero
no hay contenedor GTM en el sitio. Importa a la hora de agregar eventos de conversión:
hay que tocar el HTML, no una interfaz de GTM.

**Aplicado el 14/09**: se vinculó la propiedad. La recomendación desapareció de la lista
y con ella la categoría "Measurement" del panel.

Lo que habilita, y que todavía no existe: eventos propios en el sitio (escuchar en
Bandcamp, ir a YouTube, etc.). Sin eventos definidos, el vínculo no trae nada por sí
solo. **Ese es el próximo paso real si se quiere medir algo más que engagement de
YouTube**, y está resuelto en §8.

## 8. Los eventos del sitio (agregados el 14/09)

El vínculo GA4 no trae nada sin eventos. Se agregaron cuatro, en las dos páginas
(`site/spiralout/index.html` y `site/spiralout/aem/index.html`), como **un solo
listener delegado en `document`**: no hay que tocar cada `<a>`, y si mañana se agrega
una plataforma queda medida sola.

| Evento | Cuándo | Parámetros | ¿Conversión? |
|---|---|---|---|
| `salida_plataforma` | Clic a Bandcamp, Spotify, Apple, Tidal, Qobuz, SoundCloud, YouTube Music, el canal | `plataforma`, `host` | **SÍ**, es el evento que importa |
| `ver_visualizer` | Clic a uno de los tres visualizers o a la playlist | `pieza` | **SÍ** |
| `ir_a_aem` | Clic de la home a `/aem/` | : | No, sirve de embudo |
| `contacto` | Clic al mail del pie | `metodo` | No |

**Por qué estos y no una conversión de "compró".** No hay checkout propio: la venta
pasa en Bandcamp y el play pasa en Spotify, o sea fuera del sitio y fuera del alcance
de la medición. Lo último que sí se puede ver es **la salida hacia la plataforma**, y
eso es lo que se mide. Es la mejor aproximación disponible de "el ad funcionó".

**Verificado antes de subir**: se sirvió el sitio local, se reemplazó `gtag` por un
espía y se dispararon los clics. Los cuatro eventos salen con los parámetros
correctos, los links internos no disparan nada, y un clic sobre la imagen de adentro
del link también cuenta (el listener sube por el DOM hasta el `<a>`).

### Lo que falta, y el orden importa

1. **Deployar** (`task site:deploy`). Sin eso no pasa nada.
2. **Esperar a que GA4 los vea.** Un evento nuevo no aparece en la lista hasta que
   llega al menos uno. En tiempo real se ve en minutos; en los informes normales tarda
   hasta 24 h.
3. **Marcarlos como key events** en GA4: Admin → Events → el toggle "Mark as key
   event" en `salida_plataforma` y `ver_visualizer`.
4. **Importarlos a Google Ads**: Goals → Conversions → New → Import → Google Analytics
   4. Recién ahí la campaña puede optimizar por ellos.
5. Cuando estén importados, **decidir si las 17 conversiones de engagement de YouTube
   siguen contando como conversión primaria**. Mezclar engagement de YouTube con
   salidas a plataforma en la misma columna hace que el número no signifique nada.

## 9. Qué mirar en la próxima revisión

- ¿Bajó el costo por conversión del total, ahora que la plata se corre hacia Argentina?
- ¿Estados Unidos y Reino Unido siguen en cero con más volumen acumulado?
- ¿México sostiene el volumen siendo el doble de caro por conversión que Argentina?
- ¿`salida_plataforma` y `ver_visualizer` están importados como conversión en Ads, y
  cuántas trae cada uno? Si en un mes no traen ninguna, el problema no es la campaña:
  es que la gente llega al sitio y no sale hacia ninguna plataforma.

