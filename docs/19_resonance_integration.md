# 19 — Resonance × Spiral Out integration

[`~/git/resonance`](file:///Users/emilianomettini/git/resonance) es un
**evidence-based artistic discovery engine** que vos estás construyendo.
Encuentra artistas vía señales públicas (no nombres, no algoritmos
opacos, no hype). Stack: Kotlin / Spring Boot / Aurora pgvector / Claude
API / AWS.

**Tesis**: Resonance es la herramienta perfecta para el frente de difusión
de Spiral Out, porque convierte "a quién pitcheo este disco" — la pregunta
más cara y opinada del release marketing — en una query basada en
evidencia.

---

## Por qué este proyecto le sirve a Spiral Out (y vice versa)

### Lo que Resonance ofrece a Spiral Out

Para cada release (ÆM Heliopause, Helen agosto, futuro), Resonance puede
contestar preguntas como:

1. **"¿Qué artistas son adyacentes en compositional depth y ecosystem
   resonance al perfil de ÆM Heliopause?"**
   → Lista de 20-50 artistas similares con score + evidencia
2. **"¿Qué playlists / curadores / blogs cubren a esos artistas?"**
   → Mapa de canales de difusión adyacentes (no obvios)
3. **"¿Qué label / community ecosystem rodea a artistas con esos rasgos?"**
   → Identifica scenes (kranky, Hyperdub-like, indie ambient AR/LatAm)
4. **"Dado el catalog viejo de Helen, ¿cuáles son los artistas con
   trayectoria similar (long-form + technical mastery) y qué hicieron
   bien en distribución?"**
   → Benchmarks reales, no copy from random Medium articles

### Lo que Spiral Out le da a Resonance

- **Casos reales** para iterar el modelo: ÆM y Helen son ejemplos
  concretos de artistas con scores específicos. Probar el motor contra
  perfiles que vos conocés de adentro es 100x más útil que probarlo
  contra Nils Frahm.
- **Feedback loop**: cuando recomienda playlists / curadores y vos
  pitcheás → los hits y misses alimentan el modelo de scoring (variable
  V9 — ecosystem resonance).
- **Demo public-facing**: cuando lance Heliopause, podés mostrar
  Resonance en acción con un caso real de release marketing.

---

## Cómo usarlo en cada fase del release

### Fase 1 — pre-pitch (T-60 a T-30)

**Query**: dame 30 artistas adyacentes a ÆM Heliopause (deep space ambient,
Python composition, conceptual long-form, AI-collaborative).

**Output esperado** (formato sugerido):

```
Score  Coverage  Artist               Why                          Adjacent labels
15/18  9/9       Tim Hecker           V1+V3+V6 strong              Kranky
14/18  8/9       Lustmord             V1+V5+V6                     Soleilmoon
13/18  8/9       Christina Vantzou    V6 + AI-curious              Kranky
13/18  7/9       Lawrence English     V1+V8+V9                     Room40
...
```

Con eso tenés el "vecindario". Después:

**Query 2**: para esos 30 artistas, dame los playlists, blogs y curadores
que los cubren (con tracking de cuáles overlap).

**Output esperado**:

```
Channel              Type        Artists covered    Reach    Pitch URL/contact
"deep space ambient" playlist    18/30              45k      https://open.spotify.com/playlist/...
Stationary Travels    blog        12/30              -        https://stationarytravels.wordpress.com/contact
Headphone Commute     blog        21/30              -        https://www.headphonecommute.com/submit
Kranky bandcamp tag  community   8/30               -        ...
```

Eso es **la lista de pitching de Tier 1** sin tener que adivinar.

### Fase 2 — pitch execution (T-30 a T-0)

Mantener un spreadsheet por release con:
- channel
- pitch sent date
- response date (yes/no/no-reply)
- outcome (review posted / playlist add / declined / no reply)

Después del release, dump del spreadsheet → Resonance como feedback de qué
recomendaciones funcionaron (positive examples para entrenar V9).

### Fase 3 — post-release (T+30+)

Resonance puede analizar:
- "¿Qué artistas terminaron co-apareciendo en playlists con ÆM Heliopause?"
- "¿Apareció en algún 'related artists' de Spotify? De cuáles?"
- Esto valida (o invalida) los matches que predijo en Fase 1

---

## Estado actual de Resonance

De su `CLAUDE.md` (read 2026-05-16):

- **Status**: early development
- Stack: Kotlin 2.2.20, Spring Boot 3.5.6, JDK 21
- Plan: MusicBrainz crawler → Bandcamp crawler → Claude evidence extraction
  → scoring aggregation
- 9 variables del scoring model
- Próximos pasos en el README: seed benchmarks, MB crawler, Bandcamp
  crawler, Claude extraction, scoring

**Para Spiral Out**, lo que falta en Resonance para que sea útil:
- [ ] Crawler de MusicBrainz funcionando — produce el grafo de artistas
- [ ] Crawler de Bandcamp — para encontrar releases adyacentes + labels
- [ ] Claude extraction de evidence — saca traits del texto
- [ ] Scoring + similarity search (pgvector) — devuelve top-N adyacentes
- [ ] API endpoint `/similar?artist_id=<ÆM>&top=30`
- [ ] (Opcional) Playlist/curator overlay — para fase 2 del release

Para Heliopause **agosto**, no llega a estar listo end-to-end. Para Helen
**agosto** tampoco. Pero un MVP que devuelva los 20-30 vecinos para ÆM
podría estar listo en 4-6 semanas de trabajo dedicado, lo cual es
**altamente útil para los próximos releases** y para Helen retroactivo.

---

## Orden de prioridad sugerido (Resonance específico)

Si Spiral Out → Resonance es la motivación, el MVP de Resonance se
prioriza:

1. **MB crawler + seed con benchmarks ambient/experimental** (no Nils Frahm
   solo — agregar Lustmord, Steve Roach, Stars of the Lid, Tim Hecker,
   Christina Vantzou, Lawrence English, Burial, Demdike Stare, Caterina
   Barbieri, Loraine James)
2. **Claude extraction prompt** específico para los 9 variables, con
   atención especial a V3 (tool obsession — captura "composes in Python",
   "uses modular synths", etc.) y V6 (compositional depth — captura
   "long-form pieces", "drone-based", "AI-collaborative")
3. **Endpoint de similarity search** que tome un artist y devuelva
   top-N por score + coverage
4. **Output exportable** a CSV / markdown para usar en pitch planning
5. **Capa de playlists / curators** (V9 dimension) — más adelante

---

## Conexión operacional

**No fusionar los repos**. Spiral Out y Resonance son proyectos distintos.
Pero:

- En Spiral Out (`docs/17_release_playbook.md` Sección PR) — referenciar
  Resonance como discovery tool una vez que esté usable
- En Resonance — tener un "case study" doc que cuente cómo se usó para
  Heliopause / Helen. Sirve para divulgar la idea y para iterar
- Cuando llegue el momento de pitch round, dump output de Resonance →
  pegarlo en `transmissions/01/release/pitch_plan.md`

---

## Riesgo / tradeoff

**Riesgo**: posponer release marketing porque "estoy esperando que
Resonance esté listo".

**Mitigación**: para Heliopause (release imminent), pitchear con lo que
tenés a mano (lista manual de blogs en
[`docs/17_release_playbook.md`](17_release_playbook.md) sección PR). Para
Helen agosto y releases futuros, Resonance vale la pena esperar.

**No** condicionar el release de Heliopause al MVP de Resonance.
