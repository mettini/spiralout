---
name: aem-composer
description: Knowledge de composición ambient/cinematic para el proyecto ÆM (Spiral Out). Activar cuando se editen archivos en transmissions/<TX>/themes/, se compongan/iteren temas con el framework aem, o el usuario dé feedback musical/mezcla. Codifica técnicas de Brian Eno, Steve Roach, Stars of the Lid, Hans Zimmer + lessons learned del proyecto. Reglas concretas para que las composiciones no suenen "pegadas con cinta", tengan progresión, transiciones reales, y storytelling.
---

# ÆM Composer — knowledge para componer Outbound / Crossing / Recursion

Este es el skill que se aplica cuando trabajamos en composición de los temas
del EP. Codifica lo que sabemos de cómo se componen estas obras + lo que
aprendimos de los fallos previos.

## Filosofía

Ambient/cinematic no es "drones randoms con effects". Es **storytelling**:
una idea melódica/armónica que se desarrolla, una curva emocional que sube y
baja, transiciones reales (no cortes secos). El oyente tiene que **viajar**.

Tres frases rectoras:
1. **Progresión > Densidad.** Un tema con pocos elementos pero que va a algún
   lado le gana a uno con 30 capas que no se mueve.
2. **Crossfades > Cortes.** Cada cambio (de drone, de sección, de capa) tiene
   que solapar con lo anterior. El oyente no debe sentir cortes.
3. **El bed nunca está vacío.** Siempre algo de fondo (drone, pad, granular,
   reverb tail). Silencios > 5 segundos rompen la inmersión.

## Reglas de oro (no negociables)

### R1 — Progresión armónica obligatoria
Un tema de 8 minutos NO puede ser todo en D minor sostenido. Hay que cambiar
acordes cada 60-90 segundos. Patrón clásico Zimmer: **Dm → Bb → F → C** o
**Dm → Bb → F → Am → Dm** (vuelta a casa). Los drones tienen que MORPHEAR
de un acorde al siguiente con crossfade de 20-30s.

### R2 — Crossfades de 15-30s entre drones
Cuando el drone Dm termina y entra Bb, el Bb tiene que empezar 20s antes
de que el Dm termine. El overlap es la transición. Si los pones uno después
del otro suena cortado:
```python
# MAL — corte seco
drone_dm.add(60, drone_event([146.83, 174.61, 220.00], 60))     # 1:00 → 2:00
drone_bb.add(120, drone_event([116.54, 146.83, 174.61], 60))    # 2:00 → 3:00

# BIEN — crossfade 20s
drone_dm.add(60, drone_event([146.83, 174.61, 220.00], 80, fi=15, fo=20))   # 1:00 → 2:20
drone_bb.add(120, drone_event([116.54, 146.83, 174.61], 80, fi=20, fo=15))  # 2:00 → 3:20
```

### R3 — Una bassline melódica, no solo sub42 plano
El sub42 es la "columna del EP" pero no puede ser un sine fijo de 8 minutos.
Necesita una **bassline** que se mueva con los acordes (D2 → Bb1 → F2 → A2 → D2).
Esa es la línea melódica grave que da continuidad sin pelear con el drone.

### R4 — La melodía SE DESARROLLA, no se planta
La melodía principal (Voyager) tiene que crecer. Patrón: 1 nota → 2 notas →
fragmento → melodía completa → variación → eco. El oyente RECONOCE la idea
y la siente evolucionar. NO repetir la misma melodía igual cada vez.

### R5 — Densidad como CURVA, no plana
La cantidad de elementos audibles tiene forma:
```
densidad
  │           ╱╲
  │          ╱  ╲___
  │     ╱╲  ╱       ╲
  │ ╱╲ ╱  ╲╱         ╲
  └─────────────────────→ tiempo
   capsule  build  climax  fade
```
NO densidad plana = el oyente se aburre. Curva clara = viaje emocional.

### R6 — Reverbs largos (decay 4-6s) en pads/drones
El reverb tail llena los huecos entre eventos. Sin reverb los eventos suenan
sueltos. Con reverb decay 5s, el final de un evento se extiende y "alcanza"
al siguiente.

### R7 — Cada evento importante tiene un cue de transición
Antes de cada entrada importante, poner un riser, whoosh, reverse_swell o
bell. Anuncia. El oyente preparado lo recibe; sin cue, suena que cae del cielo.

### R8 — Volúmenes con sentido
Eventos protagonistas (voyager, voices) con amp 0.45-0.55 y gain de track
0.55-0.60. Bed (cosmos) con gain 0.10-0.15. Eventos de glue (whooshes,
risers) con gain 0.30-0.40.

### R9 — Silencios SIEMPRE menores a 8s
Si entre eventos hay > 8 segundos de bed solo, METER ALGO: granular pulse,
swell, whoosh, mini-fragment. El oyente se desconecta a los 10s de drone solo.

### R10 — El sub42 no es siempre. Tiene forma propia.
Sub42 puede aparecer/desaparecer según la narrativa. Si el storyboard pide
"que muera al minuto", muere. No insistir con el "concepto de columna" si
contradice la narrativa.

### R11 — Noise filtrado: cutoff superior ≤ 1000 Hz (regla anti-fritura)

Cualquier track basado en `noise()`, `np.random.randn(...)`, `granular_pulse(freq=...)`, `whoosh(cutoff_end=...)`, `cosmos_swell(cutoff=...)` o `radio_interference(lpf_cutoff=...)` que deje pasar contenido **arriba de 1000 Hz** se percibe como **fritura/estática aguda**, aunque el SPL no clipee. Razón: la curva de Fletcher-Munson hace que la zona 1-4 kHz sea donde el oído más siente fatiga ante noise sostenido (a diferencia de tonos puros).

Sweet spot validado: **cutoff entre 500-800 Hz** para texturas de viento/atmósfera.

```python
# MAL — fritura aguda
whoosh(dur=2.5)                                    # default cutoff_end=4000 = catastrófico
lpf(noise(60, 1.0), 1500)                         # cualquier > 1000 = fritura
granular_pulse(freq=1100)                         # ES noise pasa-banda → fritura

# BIEN — texturas seguras
whoosh(dur=2.5, cutoff_end=600)                    # explícito, zona segura
lpf(noise(60, 1.0), 600)                          # ≤ 1000
granular_pulse(freq=380)                          # graves/medio-graves
```

Si necesitás brillo agudo, **NO usar noise** — usar tonos puros (`sine`, `bell` con notch en armónicos) que el oído procesa como información musical, no como estática.

### R11.1 — Bells y voice_pad: LPF al track obligatorio si freq >= 600 Hz

`bell(freq, ...)` y `voice_pad(freq, ...)` con freq alta generan armónicos que caen en zona Fletcher-Munson:
- A5 (880) → 1760, 2640, 3520 Hz
- D5 (587) triangle → 1761 (3rd), 2935 (5th)
- F5 (698) triangle → 2094 (3rd), 3490 (5th)

**SIEMPRE** aplicar `track.fx(lambda a: lpf(a, 1500))` (o 2200 si la fundamental es > 1500) a tracks de bells/voice_pad. Notches solos en 880/1760 NO alcanzan — el 3er/4to armónico pasan libres.

### R11.2 — `whoosh()` ya tiene LPF final defensivo (mayo 2026)

La implementación de `whoosh()` concatena chunks de noise filtrados a distintos cutoffs. Las junturas son discontinuidades = clicks broadband. Fix aplicado: LPF final al output con `cutoff = max(cutoff_start, cutoff_end)`. **No tocar `whoosh()` sin entender este fix.**

### R12 — Voyager protegido (el alma del álbum)

El voyager motif es la identidad sonora del álbum. **Cualquier modificación sin benchmark de regresión termina aturdiendo al user.**

**OBLIGATORIO** usar `voyager_safe()` + `voyager_safe_fx()` de `framework/aem/motifs.py`:

```python
from aem.motifs import voyager_safe, voyager_safe_fx

voy = comp.add_track(Track('voyager_x', gain=0.55, pan=0))
voy.add(t, voyager_safe(amp=0.40, variation='ascending'))   # amp <= 0.40 — no subir
voyager_safe_fx(voy)                                          # 4 notches + LPF 2200 OBLIGATORIO
voy.fx(lambda a: reverb(a, decay=4.5, mix=0.5))              # al gusto
```

**Defaults sagrados (validados en voyager_tool benchmark):**
- waveform = `triangle`, amp peak = `0.40`, release = `0.6`
- 4 notches: 880 (A5 fund), 1046 (C6 fund), 1760 (D5 3rd), 2093 (F5 3rd)
- LPF 2200 (corta 5to+ armónicos triangle)

**Si necesitás cambiar el voyager:**
1. Hacer el cambio
2. `task qa:voyager` → fallará (benchmark mismatch). Eso es esperado.
3. Pedir al user que valide auditivamente el nuevo sonido
4. Si confirma: `task voyager:benchmark` regenera el benchmark. Si no: revertir.

`task qa:all` corre la regresión automáticamente — no podés merger un cambio que rompa el voyager benchmark sin enterarte.

### R13 — QA spectral mide DOS bandas (HOT 1.5-4 kHz + BRIGHT 4-8 kHz)

`task qa:spectral` analiza ambas bandas porque:
- HOT 1.5-4 kHz = fritura Fletcher-Munson (detecta noise/whoosh problemáticos)
- BRIGHT 4-8 kHz = brillo punzante (detecta armónicos altos triangle/voice_pad que aturden sin disparar HOT)

Si solo medís HOT, te perdés los 5to+ armónicos del triangle del voyager — exactamente el bug que llevó a la creación de `voyager_safe()`. Workflow: `task qa:all` corre estático + spectral (ambas bandas) + regresión voyager + runtime.

## Estructura armónica recomendada

Para un tema en D dorian/minor de 8 minutos:

| Tiempo | Acorde | Notas raíz | Función |
|---|---|---|---|
| 0:00 - 1:00 | (capsule) | 42 Hz + filtered | preparación |
| 1:00 - 2:00 | Dm (D-F-A) | D2 | establecimiento |
| 2:00 - 3:00 | Bb (Bb-D-F) | Bb1 | tensión (relativo mayor de Gm) |
| 3:00 - 4:00 | F (F-A-C) | F2 | apertura (relativo mayor) |
| 4:00 - 5:00 | Am (A-C-E) | A2 | inquietud |
| 5:00 - 6:00 | Dm (D-F-A) | D2 | vuelta a casa |
| 6:00 - 7:00 | Dm climax | D2 | peak |
| 7:00 - 8:00 | Dm fade | D2 | resolución |

Hertz de las notas relevantes para el framework:
```
D2=73.42  D3=146.83  D4=293.66  D5=587.33
F2=87.31  F3=174.61  F4=349.23  F5=698.46
A2=110.00 A3=220.00  A4=440.00  A5=880.00
Bb1=58.27 Bb2=116.54 Bb3=233.08 Bb4=466.16
C3=130.81 C4=261.63  C5=523.25
E3=164.81 E4=329.63  E5=659.25
```

## Técnicas de transición (las 7 que importan)

### T1 — Riser (uplifter)
Sweep ascendente que culmina en el evento. **Usar antes** de entradas importantes
(2-5s de duración). En el framework: `riser(dur=4)`.

### T2 — Downlifter
Sweep descendente que aterriza tras un evento. **Usar después** de climaxes o al
inicio de un fade-out de sección. En el framework: `downlifter(dur=8)`.

### T3 — Reverse swell
Sonido que crece exponencialmente y corta abruptamente. Pre-drop. Marca
"algo importante viene en 0.5s". En el framework: `reverse_swell(dur=4, freq=174)`.

### T4 — Whoosh (filtered noise sweep)
Ruido pasa-bajo con cutoff que barre. Más sutil que un riser, no melódico.
Bueno para transiciones donde un riser sería demasiado evidente. En el framework:
`whoosh(dur=3, direction='up')` o `'down'`.

### T5 — Bell marker
Tono de campana en cambios de sección. Timbre metálico, no pelea con drones.
Cada bell debe armonizar con su sección (D5 sobre Dm, F5 sobre Bb, A5 sobre F, etc).
En el framework: `bell(880.00, dur=10)`.

### T6 — Reverse reverb
Reverb que crece hacia el evento (no después). Smooth swell que lleva. En el
framework, todavía no hay primitive — hacer manualmente: render evento, lo das
vuelta, aplicas reverb, lo das vuelta de nuevo, lo poneés ANTES del evento.

### T7 — Crossfade de drone
Dos drones overlappean 20-30s con fade out + fade in cruzados. La forma más
natural de cambiar armonía sin que se sienta el corte. Es la R2.

### T8 — Passing object (whoosh con pan movement)
Un sonido que va de L a R (o viceversa) crea sensación de "objeto pasando
cerca". En el framework actual el pan es por track, así que se hace con
DOS tracks: uno pan=-0.6 con el evento entrando, otro pan=+0.6 con el
mismo evento desfasado 0.3-0.5s. La transición auditiva da el movimiento.
También funciona: una pista con un evento corto fade in/out donde el sonido
es ya intrínsecamente direccional (whoosh con cutoff sweep).

### T9 — Resynthesis voice (vocal grave Dune-style)
Para el "canto grave Dune-style" no hace falta una voz real: un drone
sintético con formantes en frecuencias bajas (200-400 Hz) y armónicos
acentuados en sus picos suena vocal. En el framework: voice_pad con
freq baja (60-100 Hz para "Sardaukar chant") + n_harmonics=5-8 + vibrato
muy lento (rate 1.5-2 Hz). Para más oscuridad: distort suave + lpf en
1500-2000 Hz.

### T10 — Reverse reverb (pre-event swell)
Reverb tail reproducido al revés que LLEVA al evento (en lugar de fadear
DESPUÉS). Crea swell otherworldly. En el framework:
```python
# tomar el evento, aplicar reverb generosa, dar vuelta, posicionar ANTES
event = melody([(587.33, 1)], amp=0.4)
reverb_tail = reverb(event, decay=4.0, mix=1.0)[::-1]
swell_in = fade(reverb_tail, fi=0.6 * len(reverb_tail) / SR, fo=0.05)
track.add(t_evento - dur_swell, swell_in)
track.add(t_evento, event)
```
Esencial para que entradas importantes "vengan desde antes" (no caigan
del cielo).

### T11 — Tape saturation (warmth analógica)
Saturación SUAVE (drive 1.3-2.0) con tanh — agrega harmónicos pares,
suaviza transients, redondea low end. Diferente del `distort` que se usa
para wall of sound (drive 3-5). Para warmth en pads/drones:
```python
def tape_warm(audio, drive=1.6):
    return np.tanh(audio * drive) / np.tanh(drive)
```
Aplicar en mix bus o por track. Recomendado para drones que se sienten
"digitales/fríos".

### T12 — Granular processing (Tim Hecker style)
Cortar audio en grains pequeños (0.05-0.5s), randomizar offset/pitch/
amplitude, reproducir overlapping. En el framework actual `granular_pulse`
es solo un pulse corto pasa-banda. Para granular real:
```python
def granular_process(source, dur, grain_dur=0.1, overlap=0.5,
                     pitch_jitter_cents=10, amp_jitter=0.3):
    # toma source audio, devuelve textura granular
    ...
```
Útil para texturas evolucionantes que parecen "vivas".

### T13 — Radio interference (vestigio que llega "de pedo")
Para algo que suena como una transmisión radial casi perdida en el
ruido cósmico:
```python
def radio_interference(signal, noise_amount=0.4, lpf_cutoff=1500,
                       saturation=1.3, dropout_density=0.3):
    sig = lpf(signal, lpf_cutoff)               # mids only
    sig = tanh(sig * saturation) / tanh(saturation)  # warmth
    sig = sig + noise(len(sig)/SR) * noise_amount   # static
    # opcional: mute random pequeños (dropouts)
    return sig
```
Esencial para el voyager vestige del Crossing — algo que "llega de
pedo a escucharse debido a la interferencia".

### T15 — Ghost layer treatment (presencia espectral, no protagónica)
Para elementos que el usuario quiere "fantasmal pero audible" — presentes
sin ser protagónicos. Combinación que funciona empíricamente (sweet spot
encontrado iterativamente):

```python
ghost = comp.add_track(Track('ghost_voyager', gain=0.10, pan=+0.2))
ghost.add(t, melody(NOTES, amp=0.40))
ghost.fx(lambda a: lpf(a, 2200))                    # cortar brillo
ghost.fx(lambda a: reverb(a, decay=7.0, mix=0.70))  # mas wet, mas largo
```

Reglas:
- gain de track muy bajo (0.10-0.18 — suficiente para QA activity check)
- amp interno medio (0.35-0.45 — la fuente es audible internamente)
- LPF en 2000-2400 Hz (corta brillo definicional)
- reverb decay 6-8s + mix 0.60-0.75 (cola larga, muy wet → "espectral")

Cuidado con tener DOS ghost layers similares al mismo tiempo: ambos a 0.20
suenan como UN sonido a 0.40. Bajar AMBOS proporcionalmente si es el caso.

### T14 — Disintegration loop (Basinski style)
Loop que se va degradando en cada repetición — pierde brillo, agrega
crackle, baja amp:
```python
def disintegration_loop(loop_audio, n_repeats, decay_per_loop=0.05,
                        crackle_growth=0.02, lpf_close_per_loop=200):
    out = np.zeros(len(loop_audio) * n_repeats)
    for i in range(n_repeats):
        amp = max(0, 1 - i * decay_per_loop)
        cutoff = max(200, 8000 - i * lpf_close_per_loop)
        seg = lpf(loop_audio, cutoff) * amp
        # agregar crackle creciente
        crackle_amount = i * crackle_growth
        seg += vinyl_crackle(len(seg)/SR, density=crackle_amount, amp=0.2)
        out[i*len(loop_audio):(i+1)*len(loop_audio)] = seg
    return out
```
Para conceptos donde la melodía SE PIERDE con el tiempo.

## Patrón de tensión (Hans Zimmer minimalismo + Eno layering)

Build-up por addition de capas, no por intensidad de un solo elemento:

```
0:00  capa A solo
0:30  capa A + capa B (entra B con fade 8s)
1:00  A + B + capa C
1:30  A + B + C + capa D
2:00  CLIMAX = todas las capas juntas
2:15  empiezan a salir capas (D primero, luego C, B...)
2:45  solo A queda
```

Cada capa nueva = más densidad = más tensión. Cada capa que se va = release.
**El espectador sigue las capas inconscientemente.** Por eso funciona.

Variante Zimmer: la melodía permanece igual pero las **CAPAS** debajo cambian.
La melodía es ancla, las capas son el viaje.

## Pad continuo / glue layer

Para que NUNCA suene "pegado con cinta", siempre debe haber al menos UNA capa
sosteniendo:

- `cosmos` (noise filtrado con LFO breathing) → fondo desde 0:00 hasta 7:30
- `granular_bed` (pulses cortos pasa-banda cada 3-7s) → glue desde 0:50
- Drones armónicos overlapeados → bed armónico siempre presente
- Reverb tails de 4-6s → llenan los huecos entre eventos

Si un solo de estas falta, los eventos puntuales suenan flotando.

## Anti-patterns (lo que NO funcionó)

### AP1 — "Voy a meter el voyager con UNA NOTA SOLA y crece"
El usuario quiere RECONOCER la melodía. Una nota sola no es "el motivo
desarrollándose", es "no pasa nada". Mejor: voyager aparece con la melodía
COMPLETA la primera vez, y después se repite con variaciones.

### AP2 — "El cosmos noise puede ser más fuerte porque es atmósfera"
El cosmos con gain > 0.15 satura la cabeza del oyente y opaca todo lo demás.
Si va con LFO breathing (modulación de amp), bajar gain a 0.10.

### AP3 — "Voy a hacer dirty intro de 1 minuto entero"
Más de 30 segundos de fritura/distorsión = el oyente se va. Dirty puro 0-8s,
clearing 8-30s, clean total a partir de 30s.

### AP4 — "Heart pulse al final del tema (5:00)"
El usuario explícitamente quiere los latidos al PRINCIPIO (0:30-3:00) como
guía narrativa. Llevan al oyente. NO al climax.

### AP5 — "Sub42 sostenido durante los 8 minutos como columna"
Sub42 es opcional según la narrativa. Si la narrativa pide que muera, muere.
La continuidad la da la bassline melódica, no el sub fijo.

### AP6 — "Eventos sueltos cada 30s con drone constante de fondo"
"Pegados con cinta". Cada evento sin glue suena flotando. Hay que CONECTAR:
crossfades, bells armonizadas, granular continuo, reverb tails largos.

### AP7 — "Una sola tonalidad (D minor) durante todo el tema"
Aburrimiento garantizado. Cambiar acordes cada 60-90s. Ver R1.

### AP8 — "Risers y bells en cada cosa (cargado de cues)"
Los cues son útiles ANTES de eventos importantes, no antes de cada cosa.
Si todo tiene riser, ninguno cuesta. Reservar para entradas clave.

### AP9 — "track.fx(fade(fi=N))" cuando el primer evento NO arranca en t=0
El `fade()` se aplica al array completo del track (zeros hasta el primer
evento, luego el evento). Si el primer evento empieza en t=240s, el fade
in de 20s afecta los samples 0-20s (zeros) → no hace nada. El evento
entra abruptamente en 4:00 con su atack natural.

**Fix**: aplicar fade DENTRO del evento individual:
```python
# MAL — fade de track no afecta evento que entra a 4:00
voices.add(240, voice_pad(293.66, 75, amp=0.42))
voices.fx(lambda a: fade(a, fi=20, fo=15))

# BIEN — fade aplicado al evento mismo
voices.add(240, fade(voice_pad(293.66, 75, amp=0.42), fi=20, fo=15))
```

### AP10 — "Notas staccato/aceleradas pegadas a un voyager normal"
Cambiar el ritmo de la melodía protagonista a notas mucho más cortas
(staccato) suena como "play to fast forward" — el oyente percibe que la
melodía aceleró sin razón. Si querés variación: cambiar pan, octava,
agregar counter-voice, o usar VOYAGER_INVERTED. NO cambiar tempo de las
notas drásticamente.

### AP12 — "Bajo el voyager_return pero el voyager_echo lo tapa igual"
Lección iterativa del Recursion: cuando hay dos elementos similares
(misma melodía, misma frecuencia central, mismo tiempo) el oído los suma
como uno. Bajar UNO solo no afecta la percepción global. Solución: bajar
AMBOS proporcionalmente cuando el feedback es "todavía suena fuerte".

Iteración real: voyager_return 0.55→0.75→0.65→0.45→0.22→0.10 (cada uno
"sigue fuerte") hasta darse cuenta que voyager_echo en 0.32 también
contribuía. Bajar ambos juntos resolvió.

### AP11 — "Sostenidos largos (>30s) en el cierre del tema"
Un voice_pad de 50s al final que llega hasta el 7:23 en un tema de 8:00
hace que el último minuto se sienta plantado. Cortar a max 25-30s y
permitir que entren los downlifters/fade naturalmente.

## Workflow recomendado (para iterar un tema)

1. **Storyboard primero** — escribir en arrangement_*.md la narrativa por
   minuto. Qué pasa, qué siente el oyente, qué entra/sale.
2. **Esqueleto armónico** — drones de cada sección con sus crossfades.
   Renderear y escuchar con todo silenciado excepto drones + bassline.
3. **Sumar la melodía** — voyager (o equivalente) con su desarrollo.
   Renderear y escuchar.
4. **Sumar el ritmo** — heart_pulse / sub_pulses si aplica.
5. **Sumar voces / capas** — voices L/R, drone_shimmer, voyager_counter.
6. **Glue puntual** — bells, whooshes, reverse_swells, downlifters, risers.
7. **Glue continuo** — granular_bed, cosmos breathing.
8. **Master FX** — dirty_intro u otros.

En cada paso: render, escuchar en player, iterar. NO escribir todo de una y
asumir que va a sonar.

## Cuando el usuario dice...

| Feedback | Qué significa | Qué hacer |
|---|---|---|
| "no pasa una mierda" | huecos > 8s sin eventos | densificar bed: granular, swells, mini-fragments |
| "pegado con cinta" | eventos no conectan | crossfades grandes, reverb largos, glue continuo |
| "no tiene progresión" | una sola tonalidad/idea | cambios armónicos, melodía que se desarrolla |
| "satura" | algo con gain > 0.5 dominando | bajar gain del culpable a la mitad |
| "fritura demasiado" | dirty_intro muy largo o fuerte | dirty_until corto, dirty_gain bajo |
| "no se escucha X" | gain o reverb mix mal | subir gain del track, bajar reverb mix, dar protagonismo |
| "más onda" | poca densidad o variación | sumar capas, granular más denso, pre-events más frecuentes |
| "no me lleva" | falta narrativa clara | redefinir storyboard, ordenar entradas/salidas con sentido |
| "me aburro a los 2 minutos" | establishment muy largo | acelerar entrada de elementos, climax antes |

## Referencias del proyecto

- `framework/aem/` — el framework. Ver `framework/README.md` para API.
- `framework/aem/instruments.py` — primitivas: drone, voice, kick, bell,
  whoosh, riser, downlifter, reverse_swell, granular_pulse, melody.
- `framework/aem/effects.py` — fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp.
- `framework/aem/master.py` — dirty_intro y otros master FX.
- `tracks/outbound/arrangement_full.md` — storyboard del tema.
- `player/` — UI para escuchar stems individuales.

## Inspiración / referencias

- **Brian Eno — Music for Airports**: tape loops de distintos largos
  superpuestos, pads de attack/decay suaves.
- **Steve Roach — Structures from Silence**: chord progressions sostenidas
  por minutos, modulación de timbre (no pitch).
- **Stars of the Lid — Tired Sounds**: orquestación con strings + drones,
  evolución gradual, capas que cambian de color sin cambiar de armonía.
- **Hans Zimmer — Time (Inception)**: build-up minimalista por adición de
  capas. Patrón D minor → Bb → F → C.
- **Hans Zimmer — Dune (2021/2024)**: voces aumentadas para sonar
  "other-worldly". Sardaukar chant (voz masculina + compresión). Hybrid
  instruments (chelo como Tibetan warhorn). Resynthesis (recrear voces
  con bank de sine oscillators).
- **Lustmord — Heresy / Dark Matter**: dark ambient profundo. Sub-bass
  rumbles + field recordings de criptas/cuevas/sitios de tests nucleares.
  Cosmic scale + existential unease + ritualistic soundscapes.
- **Burial**: dark ambient con sub-bass + field recording urbano.

## Por tema / paleta sonora

Diferentes temas piden diferente paleta. La skill de composición se aplica
con **estética distinta** según el tema:

### Outbound (cinematic + emergent dub)
Inspiración: Zimmer + Donato Dozzy. Clima: salir, despegue, transmisión.
Paleta: D minor diatónico, voyager melody (humano), heart_pulse rítmico,
voices etéreas, cosmos noise sutil. Brillo medio-alto. Reverbs medios.
Crackles iniciales acotados.

### Crossing (Lustmord + Dune)
Inspiración: Lustmord + Hans Zimmer Dune. Clima: cruce, oscuridad
profunda, cosmic scale. Paleta:
- **Sub-bass más bajo** que outbound (28-35 Hz, no solo 42)
- **Vocal drone grave Dune-style** (60-100 Hz, formantes acentuados)
- **Field-recording-style atmospheres** (granular noise modulated)
- **Heart beat MUY suave y lento** (40 BPM, no 60) tipo respiración
- **Passing objects** con pan movement (algo que "pasa cerca")
- **Mellotron/synth** sostenido como "luz tenue" cuando baja la oscuridad
- **Vestigio de voyager** SOLO en el último 20% del tema (no abusar — la
  melodía humana ya quedó atrás, salvo el eco final)
- Acordes: D minor + cluster bajos disonantes para tensión cósmica
- Reverbs MUY largos (6-10s decay)
- Distortion sutil en los drones graves (saturación cosmic)

### Recursion (a definir)
Será corto (3 min). Cierre del EP. Probablemente devuelve a algún elemento
del Outbound como "vuelta a casa" en clave distinta.

Fuentes detalladas + URLs en `docs/11_research_composition.md`.

Fuentes detalladas + URLs en `docs/11_research_composition.md`.

## ✅ CHECKLIST DE QA (pasar antes de declarar "listo")

Pasá un compose por este checklist mentalmente. Si alguno falla → arreglar
antes de re-renderizar.

### Estructura armónica
- [ ] **R1** Hay al menos 3 acordes distintos a lo largo del tema (no todo Dm).
- [ ] **R2** Cada cambio de drone tiene crossfade ≥ 15s (overlap entre el
  fade-out del que sale y el fade-in del que entra).
- [ ] **R3** Hay una bassline melódica (no solo sub42 plano), con notas que
  siguen los acordes.

### Desarrollo melódico
- [ ] **R4** La melodía protagonista (voyager) aparece varias veces con
  variaciones distintas (no copy-paste). Patrones diferentes en cada vuelta.
- [ ] La melodía cuando aparece dura > 8s (no fragmentos sueltos cortos).
- [ ] Hay al menos un "voyager echo / vuelve distinto" (LPF + reverb largo).

### Densidad y curva emocional
- [ ] **R5** Densidad como curva (no plana): build-up → climax → release.
- [ ] **R9** Sin silencios > 8s en ninguna sección. Si hay un "in-pace"
  (calma intencional), tiene al menos 1 elemento sosteniendo (granular,
  swells, latido sparse, voyager echo).
- [ ] El climax tiene al menos 4 capas activas simultáneas.

### Glue (que no suene "pegado con cinta")
- [ ] **R6** Drones/pads tienen reverb decay ≥ 4s.
- [ ] **R7** Cada evento importante (voyager, voices full, climax) tiene
  cue de transición (riser, whoosh, reverse_swell o bell ANTES).
- [ ] Hay glue continuo: granular_bed sembrado en gaps, cosmos breathing,
  reverb tails largos.

### Volúmenes / mezcla
- [ ] **R8** Bed (cosmos, granular) gain ≤ 0.15. Eventos protagonistas
  (voyager, voices) gain 0.45-0.60. Cues (whoosh, riser) 0.30-0.40.
- [ ] El track más fuerte (peak en manifest.json) no supera 0.6 después
  de la normalización (sino algo está dominando demasiado).

### Narrativa / story
- [ ] El tema tiene un arc claro: principio (set-up) → desarrollo → clímax
  → cierre. Se puede explicar la historia en una frase.
- [ ] Los elementos rítmicos (heart_pulse) tienen propósito narrativo: si
  están "te llevan", si se van "te dejan flotar", si vuelven "embodiment".
- [ ] El sub42 (si existe) tiene forma propia (no constante 8 minutos).

### Anti-patterns (chequear que NO se cumplan)
- [ ] AP1 — voyager NO arranca con una sola nota como "tease" lento.
- [ ] AP2 — cosmos noise NO supera gain 0.15.
- [ ] AP3 — dirty_intro NO dura > 30s en total (dirty + transition).
- [ ] AP4 — heart_pulse NO está solo al final (tiene que aparecer temprano
  o estructurado por la narrativa).
- [ ] AP5 — sub42 NO está constante los 8 minutos.
- [ ] AP6 — eventos NO están sueltos sin glue (siempre algo bridging).
- [ ] AP7 — NO toda la pieza en una sola tonalidad sin cambios.
- [ ] AP8 — risers/cues NO en cada cosita (reservados para entradas clave).
- [ ] AP9 — para tracks cuyo primer evento NO empieza en t=0, el `fade()`
  está aplicado al EVENTO (no al track). Verificar `track.fx(lambda a: fade(...))`
  cuando hay events posteriores: probable bug.
- [ ] AP10 — la melodía protagonista NO tiene una versión "staccato acelerada"
  pegada a una versión normal (suena fast-forward).
- [ ] AP11 — sostenidos finales (último evento de voices, drone, etc.) NO duran
  > 30s. Cortar para permitir el fade natural del cierre.

### Render técnico
- [ ] El render compila sin warnings.
- [ ] El master peak es razonable (no clipping).
- [ ] El manifest.json se generó OK.
- [ ] Los stems individuales tienen peak > 0.05 (sino el track no aporta).

### Cierre del checklist
- Antes de decirle al usuario "listo", repasar este checklist.
- Si > 2 ítems fallan → no decir listo, iterar primero.
- Si 1-2 ítems fallan pero son menores (ej. cosmos a 0.16 vs 0.15) → mencionar
  al usuario que se podría afinar.
- Si todos pasan → señalar al usuario los puntos clave del cambio.
