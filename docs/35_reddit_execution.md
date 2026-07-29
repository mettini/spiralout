# 35 — Reddit: ejecución sub por sub (reglas verificadas)

> **Reglas leídas de la fuente el 2026-07-26**, no de guías de terceros: se
> entró a `/r/<sub>/about/rules/` de cada uno. Las reglas cambian — si pasaron
> meses, releer antes de postear. Estrategia → `docs/31` · plan previo →
> `docs/32 §A` (queda desactualizado en dos puntos, ver abajo).

## Lo que cambia respecto de `docs/32`

Dos cosas que estaban planificadas **no se pueden hacer**:

1. **r/ifyoulikeblank está fuera de juego.** Regla 2, textual: *"Self-promotion
   (links to any media created by yourself **or someone you know**) is strictly
   prohibited. This is an instaban rule. No exceptions, no appeals."* El post
   "If you like Lustmord you'll like ÆM" es baneo inmediato. Y el "or someone
   you know" también mata usarlo **para Helen**. El sub solo sirve para
   responder pedidos de otros recomendando artistas ajenos.
2. **Los dos subs núcleo prohíben contenido de IA.** r/ambientmusic regla 4:
   *"No AI content"*. r/darkambient regla 5: *"AI-generated content is not
   allowed"*. Ver §"El problema de la IA".

## Tabla operativa

| Sub | ¿Puedo postear lo propio? | Cómo, exactamente | Links | La regla que mata |
|---|---|---|---|---|
| **r/drone** | **Sí** | Post directo. Título sin editorializar (regla 3): tal cual el release | Público sin cuenta (Bandcamp/YouTube). **No** Spotify-only | Regla 5: la música tiene que ser el centro, no el merch/venta |
| **r/SpaceMusic** | **Sí** | Post directo. Reglas mínimas: no spamear, on-topic | Bandcamp/YouTube | Regla 3: hay un dominio baneado por Reddit (no especifica cuál) — usar Bandcamp y listo |
| **r/ambientmusic** | Solo dos vías | (a) **Weekly Community Thread** (lo postea AutoModerator, está pinneado arriba) para self-promo casual · (b) post propio SOLO con **200 palabras mínimo** de técnica/motivación/inspiración | **Prohibido Spotify** (regla 5). Bandcamp o YouTube | Regla 4: **no AI content** · Regla 2: *"no ChatGPT"* en el texto |
| **r/listentothis** | **No, solo weekly** | Regla 3: self-promo y "personal association" **solo** en los *weekly music melting pot threads* | Canal oficial del artista (regla 5) | Regla 1: techo de popularidad (no nos afecta, estamos muy abajo) |
| **r/darkambient** | **Sí** (regla 3: *"original content is allowed"*) | Post directo, y las discusiones están bien vistas (regla 4) | Bandcamp/SoundCloud preferido; YouTube solo si no hay mejor | Regla 5: **no AI-generated content** |
| **r/ifyoulikeblank** | **NUNCA** | Solo responder pedidos ajenos recomendando a **otros** | — | Regla 2: instaban, incluye "someone you know" |

## El problema de la IA (leer antes de decidir)

ÆM es, literalmente, "AI + EM". El sitio dice *"the intersection of human
composition and artificial intelligence"*. Y los dos subs más grandes del nicho
tienen prohibición explícita de contenido de IA.

**El matiz técnico es real**: el audio de Heliopause es **código escrito a
mano** — el framework `aem` es DSP determinístico en Python, no hay ningún
modelo generativo en la cadena de audio. "Composición programática" no es
"AI-generated". Pero:

- Un mod que entra a `spiralout.space` lee "human composition and AI" y no va a
  investigar el matiz.
- El riesgo no es solo que borren el post: es que te acusen públicamente de IA
  **en la comunidad que estás tratando de ganar**. Ese costo no se revierte.

**Recomendación**: no ir a discutir la definición dentro de un sub. Concreto:

- En **r/drone** y **r/SpaceMusic** (sin regla de IA) se postea el release.
- En **r/ambientmusic** y **r/darkambient** se participa de verdad y **no se
  linkea nada propio**. Su valor pasa a ser credibilidad, no alcance.
- Si alguien pregunta, la respuesta honesta y corta: *"it's written in code —
  a Python DSP framework I wrote. No generative models in the audio."* Sin
  entrar en el resto. Nunca mentir: si te repreguntan por los visuales, ahí sí
  hubo modelos, y negarlo se paga peor.

## Paso 0 — la cuenta (antes de postear nada)

- **Username neutro.** Nada de `AEM_official` ni `spiralout`: grita promo y
  rompe el faceless. Un nombre cualquiera de fan del género.
- **Historial.** Una cuenta de 0 días con un link propio se filtra sola. Si la
  cuenta es nueva: 2-4 semanas participando antes de compartir algo.
- La regla 9:1 no es superstición: es lo que hace que tu perfil, cuando alguien
  lo mira, parezca un fan y no un vendedor.

### Dónde aportar en serio (tipos de hilo que aparecen todas las semanas)

En r/ambientmusic, al 2026-07-26, estaban activos justo estos: *"What are your
favorite 'soft noise' albums?"*, *"Anyone have any recommendations similar to
these?"*, *"What would you recommend me as a starter"*, *"What separates great
ambient from background music?"*. Ese es el material: recomendar **otros**
(Lustmord, Köner, Deathprod, Biosphere, Northaunt, Stars of the Lid), aportar
data técnica o histórica, opinar en serio. Cero mención propia.

## Los mensajes

Links a usar: Bandcamp `https://aemtransmissions.bandcamp.com` ·
YouTube `@aem.transmissions`. **Nunca Spotify** en estos subs.

### A · r/drone y r/SpaceMusic — post directo

Título (r/drone exige no editorializar, así que va plano):

```
ÆM — Heliopause [dark ambient / drone] (2026)
```

Cuerpo (post de texto, no link post):

```
Three long-form pieces recorded as a single passage: Outbound (8:00),
Crossing (13:00), Recursion (3:00). The heliopause is where the solar wind
stops pushing and interstellar space begins — the record sits on that
boundary and never quite crosses it.

Sub-heavy, slow, no beats. A recurring melodic motif drifts across all
three tracks, degrading a little each time it returns.

Bandcamp: https://aemtransmissions.bandcamp.com
Full visualizers (4K): youtube.com/@aem.transmissions
```

Sin "out now", sin hype, sin pedir nada. Cumple las dos reglas que importan:
la música es el centro y el link es accesible sin cuenta.

### B · Weekly thread de r/ambientmusic y melting pot de r/listentothis

Un comentario corto, no un ensayo. Es un hilo de self-promo casual, se entiende
qué es:

```
ÆM — Heliopause (dark ambient / drone, 2026). Three pieces on the edge of
the solar system, sub-heavy and slow. Bandcamp:
https://aemtransmissions.bandcamp.com
```

En r/listentothis, si en algún momento se postea fuera del weekly (solo lo
puede hacer **otra persona**, no vos), el formato obligatorio es:

```
ÆM -- Outbound [Dark Ambient / Drone] (2026)
```

### C · Si decidís ir al post de 200 palabras en r/ambientmusic

**Esto no te lo puedo escribir yo**: la regla 2 dice *"no ChatGPT"*, y un texto
generado en un sub que además prohíbe IA es exactamente la forma de quemarlo.
Te dejo el esqueleto de puntos y lo escribís vos, en tu voz de compositor
(firmado como Emiliano, no como ÆM — este es el único contexto donde conviene
romper el faceless, porque la regla pide hablar de técnica):

- Los temas no se grabaron: se **escribieron en código**. Framework propio en
  Python, síntesis y FX a mano, sin DAW en la cadena de composición.
- Qué implica componer así: no hay "tocar hasta que salga", hay leer el
  espectro y ajustar parámetros. Lo que ganás es control absoluto del tiempo
  largo; lo que perdés es el accidente feliz.
- El motivo recurrente (Voyager) y la decisión de **degradarlo** en cada
  reaparición en vez de repetirlo igual.
- Un problema concreto y cómo se resolvió: el ruido filtrado arriba de 1 kHz
  sonaba a fritura, y usar `abs()` como exciter generaba cientos de
  intermodulaciones. Se resolvió con `tanh` y bajando el corte a 800 Hz.
- El concepto de la heliopausa como frontera que no se cruza.
- **Decisión previa**: cómo respondés si preguntan por la IA (ver arriba).

## Reglas duras (de `docs/32`, siguen valiendo)

- Nunca el mismo día en varios subs — crosspost-spam = shadowban.
- No responder a la defensiva. Si no engancha, dejar pasar.
- Nada de DMs promocionales, votos comprados ni cuentas múltiples.
- Un toque, con dignidad.

## Pendiente

- **Discord** (Modular Grid, Ambient Music, Latin Electronic): sin investigar
  todavía. Los servidores no tienen reglas públicas indexables — hay que
  entrar y leer `#rules`.
