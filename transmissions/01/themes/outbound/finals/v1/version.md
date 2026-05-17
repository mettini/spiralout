# Outbound — versión final v1

Snapshot del outbound aprobado como v1. Render del 2026-05-03.

## Estructura

```
0:00 - 0:30   CAPSULA       sub_42hz + fritura + signals + thump
0:30 - 1:30   LATIDO        heart_pulse 60 BPM constante (con intro_pad + pings)
1:30 - 3:30   VOYAGER DANCE voyager L/R/C alternando + voyager_swell crescendo + pings
3:30 - 4:30   IN-PACE       latido sparse + voyager echoes + voices_preview
4:30 - 5:30   VOYAGER F2    counter (5ta arriba) + inverted (otro patron)
5:30 - 6:30   EMBODIMENT    voices L+R + heart_pulse climax (60 BPM)
6:00 - 7:00   CLIMAX        todas las capas + voyager degraded
7:00 - 8:00   DEPARTURE     downlifters + fade
```

## Tracks (35 totales)

Foundation: sub_42hz, capsule_signals, capsule_thump, heart_pulse,
intro_pad_high, intro_pings, cosmos, cosmos_swells, cue_release_1min.

Drones armónicos (Dm → Bb → F → Am → Dm): drone_Dm, drone_Bb, drone_F,
drone_Am, drone_Dm_end.

Bassline + glue: bassline, drone_shimmer, granular_bed, sub_pulses.

Voyager (multiples versiones): voyager_left, voyager_right, voyager_center,
voyager_swell, voyager_pings, voyager_echo, voyager_counter_2,
voyager_inverted, voyager_degraded.

Voces: voices_preview, voices_l_d4, voices_r_a4.

Glue puntual: bell_markers, whooshes, reverse_swells, downlifters, risers.

## Master FX

dirty_intro: dirty_until=8, transition_dur=22, n_crackles=70,
dirty_gain=0.80, transition_curve=2.5. Clean total a 0:30.

## Cómo se generó

Snapshot del compose en `compose_snapshot.py` — equivalente a haber corrido
`python3.10 tracks/outbound/compose_full.py` el 2026-05-03 con el código en
ese momento.

Master + stems renderizados en este directorio. Para escuchar via player,
re-rendear con el snapshot o copiarlos temporalmente a
`out/outbound/master/` y `out/outbound/stems/outbound_FULL/`.
