# 34 — Campaña YouTube ads (test mes 1) — listo para pegar

> El anuncio concreto para correr en Google Ads. Budget ≤ $50/mes (~$1.5/día).
> Objetivo: reach dirigido al nicho dark/space ambient con los visualizers.
> Estrategia → `docs/31 §5` · `docs/32 §B`. Claude arma, user corre.

## 0. Activación — la primera vez (donde se pierde el tiempo)

Hacer **en este orden**. Los dos primeros puntos son la trampa clásica: si los
saltás, no vas a encontrar las campañas de video en ningún menú.

1. **Entrá a `ads.google.com` con la cuenta de Google dueña del canal de
   YouTube.** Si usás otra, después no vas a poder ver earned actions (subs y
   views que gana el canal gracias al ad) ni armar remarketing.
2. **Salí del modo simplificado.** Google Ads abre las cuentas nuevas en *Smart
   mode*, que solo ofrece campañas automáticas y **no tiene campañas de Video**.
   Buscá **"Switch to Expert Mode"** (suele estar en el menú de tres puntos /
   Settings, o como link al pie del asistente de creación de campaña). Si el
   asistente te empuja a crear una campaña antes de dejarte entrar, buscá el
   link chico tipo *"Create an account without a campaign"* / *"Switch to Expert
   Mode"* y usalo. **Es un camino de ida en la práctica: hacelo antes de crear
   nada.**
3. **Método de pago.** Billing → agregar tarjeta. La campaña no sale al aire sin
   esto. Elegí país y moneda con cuidado: **la moneda no se puede cambiar
   después** (y afecta cómo lees el CPV).
4. **Vinculá el canal de YouTube.** Tools → *Linked accounts* (o *Data manager*)
   → YouTube → vincular `@aem.transmissions`. Sin esto las métricas de earned
   actions quedan vacías, que es justo lo que más importa medir acá.
5. **Recién ahora** creá la campaña con lo de §1.
6. **Poné un límite de gasto mensual** en Billing (account budget) además del
   budget diario. Cinturón y tiradores: el budget diario puede sobre-entregar
   hasta 2x en un día puntual.

> Los nombres exactos de los menús de Google Ads cambian seguido. Si un label no
> coincide, buscá el concepto (expert mode, linked accounts, account budget), no
> el texto literal.

## 1. Setup de la campaña (Google Ads)
- Cuenta: ads.google.com (crear si no hay; método de pago).
- **New campaign** → objetivo **"Awareness and consideration"** → tipo **Video**
  → subtype **"Video views"** → formato **In-feed** (aparece sugerido, el usuario
  elige clickear = lo más "orgánico").
- **Budget**: $1.5/día (≈ $45/mes). Bidding: **Maximum CPV** (dejá el sugerido, ~$0.03).
- **Networks**: solo **YouTube** (destildá Display/partners).
- **Geo**: Worldwide (o priorizar US, UK, DE, NL, CA, AU — mercados ambient fuertes).
- **Languages**: English + Spanish.
- **Video a promocionar**: **Outbound** (el más accesible/melódico, con el planeta
  y el óvulo). 1 solo video al arranque. Link: https://www.youtube.com/watch?v=Lbwz5F4xfrI

## 2. Targeting (lo importante — apilar estas capas)

### A. Custom segment — por keywords/búsquedas
Crear un "custom segment" con gente que **buscó o le interesa** estos términos:
```
dark ambient, space ambient, deep space ambient, drone music, lustmord,
cryo chamber, steve roach, atrium carceri, cosmic ambient, sleep ambient,
ambient music, dungeon synth, dark drone, meditation ambient
```

### B. Placements — canales concretos donde aparecer
Pegar estos canales como **placements** (o como custom segment "browses these channels"):
- **Cryo Chamber** (el label de dark ambient — mixes de 1h con millones de views, EL target)
- **Lustmord** · **Steve Roach** · **Atrium Carceri** · **Sabled Sun** (Cryo Chamber)
- **Kammarheit** · **Northaunt** · **Biosphere** · **Thomas Köner** · **Deathprod**
- **Stars of the Lid** · **Brian Eno** (ambient adyacente)
- Canales de mixes: buscar "dark ambient mix", "space ambient", "cosmic sleep" y
  sumar los que tengan volumen (ej. "Nightmares Portal", "Space Ambient Music").

### C. Audiences (interests / affinity)
- Music lovers → **Ambient / Electronic music**
- **Science & astronomy enthusiasts** (encaja con Heliopause/Voyager)

> Empezar con A + B (lo más fino). Si el volumen es muy bajo, sumar C para ampliar.

## 3. El anuncio (copy)
- **Headline (corto):** `ÆM — Heliopause`
- **Descripción:** `Deep space ambient and drone. Three transmissions from the edge of the solar system.`
- **Thumbnail**: el del video (ya optimizado, `docs/24`).
- Sin hype, sin mencionar IA (`docs/29`). El thumbnail + el título hacen el trabajo.

## 4. Medir (a los 3-4 días) y podar
- **View rate** (>15-20% in-feed = bueno) · **CPV** (buscar $0.02-0.05) ·
  **watch-time/retención** (si miran >30s, el targeting está fino) ·
  **earned actions** (subs, likes, views a los otros videos).
- **La pregunta clave**: ¿movió el **streaming en Spotify** (Spotify for Artists,
  ventana del test)? Si no, cambiar targeting o probar otro lever el mes 2.
- Podar: bajar puja de segmentos caros, subir lo que trae views baratas + retención.

## 5. Recordatorio (docs/31)
Una prueba por mes. Este es el mes 1. NO correr IG boost / otros al mismo tiempo
(dilución). Medir → decidir mes 2.

---

## 6. Optimización del 2026-08-06 (lo que se hizo y lo que se aprendió)

### Los números al día 11 (26/07 → 05/08)

| | |
|---|---|
| Presupuesto | ARS 2.500/día · estado **Limited by budget** |
| Impresiones | 9.115 |
| TrueView views | 311 |
| CPV promedio | ARS 77,19 |
| Gasto | ARS 24.005,90 |
| Clics | 9 |
| Conversiones | 0 |

### El diagnóstico

El asistente de IA de Google analizó la campaña **entera por clics** (9 eventos) y
propuso cortar horario, dispositivo, edad y geo. En una campaña de *video views* los
clics son la métrica menos relevante, y con 9 eventos ninguno de esos cortes tiene
respaldo estadístico: en la franja de las 7-8 am se esperaban 1,8 clics y salieron 0,
lo cual pasa 1 de cada 6 veces por azar.

Mirando lo que sí tenía muestra, el problema real estaba en otro lado. Los 12
targetings eran **todos keywords** (los emplazamientos por canal de §2.B nunca se
habían cargado), y la reparación era ahí:

| Keyword | Impr | Views | View rate |
|---|---|---|---|
| **cosmic ambient** | **5.345** | 188 | 3,5% |
| ambient music | 1.386 | 48 | 3,5% |
| dark ambient | 698 | 21 | 3,0% |
| steve roach | 596 | 16 | 2,7% |
| atrium carceri | 537 | 20 | 3,7% |
| lustmord | 432 | 10 | 2,3% |
| **drone music** | 66 | 8 | **12,1%** |
| space ambient | 22 | 0 | 0% |
| dark drone | 13 | 0 | — |
| deep space ambient | 10 | 0 | — |
| dungeon synth | 9 | 0 | — |
| cryo chamber | **1** | 0 | — |

Dos cosas saltan: **"cosmic ambient" se comía el 59% de las impresiones** siendo el
término más vago de la lista (y es lo que ponía el anuncio en canales de dormir bebés
y relax profundo), y **los términos precisos estaban muertos de hambre** — `cryo
chamber` tuvo 1 impresión en once días, no por falta de público sino porque el
término ancho se llevaba el presupuesto.

La única señal real de todo el análisis: **`drone music` tiene 12,1% de view rate**
contra 3,4% del promedio.

### Lo que se aplicó

1. **Cuenta renombrada** de "Google Ads account" a **"Spiral Out"**.
2. **`cosmic ambient` y `ambient music` pausadas** (74% de las impresiones). No se
   subió el presupuesto: se liberó el que ya había para los términos finos.
3. **29 keywords negativas** a nivel campaña: `baby · babies · baby sleep · lullaby ·
   newborn · nursery · spa · massage · yoga · reiki · chakra · manifestation ·
   healing frequency · solfeggio · 432 hz · 528 hz · binaural beats · guided
   meditation · asmr · white noise · pink noise · tinnitus · study music · focus
   music · sleep music · sleep sounds · deep relaxation · stress relief · anxiety
   relief`.
   **Ojo con lo que NO se excluyó y es a propósito**: "sleep" y "meditation" pelados.
   Mucha gente que escucha dark ambient de verdad busca eso, excluirlos corta público
   real. Los términos targeteados hacen el trabajo sin ese daño.
4. **No se tocó** dispositivo, horario, edad ni geo. Lo de desktop además estaba mal
   medido: en ambient la tele y la compu es donde se escucha largo, no donde se
   clickea.

### Lo que se descartó y por qué (para no volver a intentarlo)

**Los emplazamientos por canal quedan DESCARTADOS a este presupuesto.**

El aprendizaje que costó la tarde: **un emplazamiento no agrega alcance, lo
restringe.** El propio panel lo dice: *"Your ad can appear on any eligible Google
Display Network placement **and only on the following YouTube placements**"*. Cargar
4 canales saca el anuncio de todo YouTube y lo encierra en esos 4. Google calcula el
inventario, ve que no alcanza para gastar ARS 2.500/día y **se niega a guardar**:

> "You need more placements for your ads to show on. Add more channels and videos or
> remove the ones you have already added."

Para que sea viable haría falta una lista de **20 a 40 canales**, y ahí los
emplazamientos pasan a ser toda la estrategia del ad group (las keywords dejan de
importar). Eso es una tarea de research —los "- Topic" de cada artista necesitan el
ID del canal, más los canales de mixes con volumen— y no se justifica para un test de
USD 1,5/día. Se revisa si algún día el presupuesto sube en serio.

**Handles verificados uno por uno en YouTube**, para cuando haga falta:

```
youtube.com/@cryochamberlabel      Cryo Chamber, 428K subs  ← el ancla
youtube.com/@BLustmord             Lustmord (Official), 35,2K
youtube.com/@SteveRoachOfficial    Steve Roach, 12,5K
youtube.com/@biophonrecords        Biophon, el sello de Biosphere
```

**No adivinar handles.** `@CryoChamber` es un canal llamado "mercury" y `@northaunt`
es uno llamado "mountsun". Se cargaron los dos por adivinanza y hubo que descartarlos.

Kammarheit, Northaunt, Atrium Carceri, Biosphere y Thomas Köner **no tienen canal
propio**, solo los "- Topic" que genera YouTube. Se pueden targetear pero requieren el
ID. Dato: Steve Roach - Topic tiene más subs (15,7K) que su canal oficial (12,5K).

### Chequeos de configuración (verificados el 06/08)

- **Networks: solo YouTube.** No hay fuga a Display ni a video partners. ✓
- **Auto-apply: apagado.** Google no aplica recomendaciones solo. ✓
- **La UI empuja "Raise limited budget" constantemente. NO se aplica** — decisión
  explícita del user.
- **"Ads funded by EMILIANO JORGE METTINI"** aparece público en el Ads Transparency
  Center. Es el requisito legal de Google: si el que paga es una persona y no una
  entidad, va su nombre legal. **Se deja así** (decisión del user, 06/08). Tensión
  menor con que ÆM es faceless, asumida a conciencia.
- **Copy del anuncio**: la tabla de Ads no renderiza las filas en el navegador, así
  que no se pudo leer desde ahí. La descripción pública del video de Outbound arranca
  con el texto cifrado del cuento ("To leave was, in truth, the verb that invented
  it"), sin mención de IA. La frase "proyecto de IA" que usó el asistente de Google
  salió con toda probabilidad de la conversación del user con él, no del copy.

### Qué mirar en 5-7 días

La pregunta única: **¿se movieron los términos precisos?** `deep space ambient`,
`dark drone`, `dungeon synth`, `space ambient` y `cryo chamber` estaban en 0-22
impresiones porque no les llegaba presupuesto. Ahora sí les llega.

- Si empiezan a moverse con view rate decente → el problema era la distribución del
  presupuesto y está resuelto.
- Si siguen muertos → no hay volumen en esos términos, y ahí sí la única salida es la
  lista grande de emplazamientos o cambiar de palanca (`docs/32 §C`).

Y seguir mirando **view rate, CPV y earned actions**, no clics.
