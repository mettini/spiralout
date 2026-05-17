# Outbound v0 — arrangement (60s prototype)

## Concepto narrativo
Em deja el origen. El void → primera señal humana → el cuerpo despierta (pulso cardíaco) → la transmisión empieza a degradarse mientras se aleja.

Este es un prototipo de 1 minuto. La idea es que escuches la **estructura** — capas que entran, eventos en el tiempo, narrativa. La calidad sonora todavía es síntesis simple en Python; lo que importa es que entiendas cómo se construye el tema en pistas paralelas. Después esto se traduce a instrumentos reales en GarageBand manteniendo la misma arquitectura.

## Arquitectura del proyecto

```
maquetas/
├── engine.py                         framework reutilizable (Track, Composition, sintes, FX)
├── compose_outbound_v0.py            composición específica usando el engine
├── arrangement_outbound_v0.md        este documento (storyboard / score)
└── outbound_v0.wav                   audio renderizado (60s, estéreo)
```

Para iterar: editás `compose_outbound_v0.py` (cambiar gain, pan, tiempos de entrada, agregar tracks, etc.) y corrés `python3 compose_outbound_v0.py`. Genera el WAV nuevo en segundos.

## Estructura por secciones

### 0 → 12s — VOID
> El silencio antes del lanzamiento.

- **sub_42hz** entra desde 0s con fade-in de 8s. La columna vertebral. Casi imperceptible al inicio.
- **cosmos** (ruido CMB filtrado) entra desde 2s, fade-in 6s. El fondo del espacio.
- Sensación: estás en el vacío, todavía no pasa nada.

### 12 → 25s — PRIMERA SEÑAL
> La música nace. Aparece la armonía y la primera transmisión humana.

- **risers** (sweep ascendente) en 10s → cue que anuncia la entrada del drone.
- **drone_d_minor** entra a 12s — D-F-A en octava media. La estructura armónica se establece.
- **voyager_clear** entra a 18s — la melodía clara, la voz humana de la sonda dice "estoy acá". Paneada a la derecha. Dura 12s.

### 25 → 30s — PROFUNDIDAD
> La sonda gana cuerpo grave.

- **sub_drone** entra a 25s — D2 y F2, octava grave. Le da peso a la armonía.

### 30 → 45s — VOCES Y DEGRADACIÓN
> La sonda canta. La transmisión humana empieza a fallar.

- **risers** segundo sweep en 28s → cue para las voces.
- **voices_l_d4** (D4, vibrato 4 Hz) entra a 30s, paneada a la izquierda con fade-in 8s.
- **voices_r_a4** (A4, vibrato 4.5 Hz) entra a 30s, paneada a la derecha. Vibratos ligeramente distintos para que se sientan dos voces vivas.
- **voyager_degraded** entra a 35s — los mismos notes que voyager_clear pero una octava abajo, distorsionados y filtrados (lpf 1500 Hz + tanh distortion). La señal humana ya está degradada. Paneada a la izquierda (espejo del clear).

### 45 → 60s — PULSO Y CIERRE
> Em ya no es solo señal: tiene cuerpo. Pulso cardíaco. Cierre del primer movimiento.

- **risers** tercer sweep en 43s → cue para el pulso.
- **heart_pulse_60bpm** entra a 45s — kick a 60 BPM (1 pulso por segundo). 14 pulsos hasta el final.
- Todas las capas previas siguen sonando, fade-out gradual de las que se van apagando.

## Tabla de pistas vs tiempo

| Pista                | 0–12 | 12–25 | 25–30 | 30–45 | 45–60 |
|----------------------|------|-------|-------|-------|-------|
| sub_42hz             | ◐ in | ▓     | ▓     | ▓     | ▓◑    |
| cosmos (CMB)         | ◐ in | ▓     | ▓     | ▓     | ◑     |
| drone_d_minor        |      | ◐ in  | ▓     | ▓     | ▓     |
| voyager_clear (R)    |      | ◐ in  | ▓     | ◑     |       |
| sub_drone            |      |       | ◐ in  | ▓     | ▓     |
| voices_l_d4 (L)      |      |       |       | ◐ in  | ▓◑    |
| voices_r_a4 (R)      |      |       |       | ◐ in  | ▓◑    |
| voyager_degraded (L) |      |       |       | ◐ in  | ◑     |
| heart_pulse 60 BPM   |      |       |       |       | ◐ in  |
| risers (sweeps)      | ·    | spike | ·     | spike | spike |

(◐ = fade in, ◑ = fade out, ▓ = sostenido, · = ausente, spike = evento puntual)

## Qué escuchar específicamente
- **Estéreo:** voyager_clear va a la derecha, voyager_degraded a la izquierda. Las voces altas se abren L+R. Probá con auriculares.
- **El sub 42Hz** está siempre presente pero subliminal. Lo sentís más que lo escuchás.
- **Los risers** son los "anuncios" — pequeños sweeps que avisan que algo va a entrar. Como las pausas dramáticas en cine.
- **La degradación de la voyager** entre 35s y 47s: los mismos notes, una octava abajo, filtrados y distorsionados. Es la metáfora central — lo humano que se pierde en el cruce.
- **El pulso al final** entra solo cuando todo lo demás ya está en su lugar, como si Em finalmente cobrara cuerpo.

## Cómo iterar usando el framework

Tunear un parámetro existente:
```python
# Antes
pulse = comp.add_track(Track('heart_pulse_60bpm', gain=0.55, pan=0))

# Después (más fuerte, ligeramente a la izquierda)
pulse = comp.add_track(Track('heart_pulse_60bpm', gain=0.70, pan=-0.1))
```

Mover una pista en el tiempo:
```python
# Antes: voces entran a 30s
voices_l.add(30, voice_pad(293.66, 30, ...))

# Después: voces entran a 35s
voices_l.add(35, voice_pad(293.66, 25, ...))
```

Agregar una pista nueva (por ejemplo un swell de cuerdas a 40s):
```python
swell = comp.add_track(Track('strings_swell', gain=0.3, pan=0))
swell.add(40, voice_pad(220, 15, vibrato_rate=2, amp=0.5))
swell.fx(lambda a: fade(a, fi=5, fo=5))
swell.fx(lambda a: reverb(a, decay=4, mix=0.5))
```

Después corrés `python3 compose_outbound_v0.py` y escuchás el WAV nuevo.

## Próximos pasos
1. Escuchás `outbound_v0.wav` y me decís qué te tira y qué no.
2. Iteramos: agregar/sacar capas, cambiar tiempos, tunear gains/pans/reverbs.
3. Una vez Outbound nos cierra, repetimos para Crossing y Recursion (mismo engine, otras composiciones).
4. La estructura del engine (Track / events / effects) es exactamente la misma que vas a usar en GarageBand cuando reemplaces la síntesis Python por instrumentos reales — esto es el "mapa" del tema.
