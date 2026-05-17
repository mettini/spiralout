"""Outbound — TEMA COMPLETO (8:00), variante v0 BALANCED.

REWRITE v5 — narrativa explicita 2:

  1er minuto: capsula con fritura -> latido. Latido entra a 0:30 a 60 BPM
  CONSTANTE (no acelera) hasta 1:30 donde se VA con fade rapido.
  1:30: voyager entra y JUEGA durante 2 minutos (1:30-3:30) yendo y
  viniendo entre L y R, con fragmentos, ecos, distintas formas.
  3:30-4:30: in-pace. Voyager se va. Calma con voices_preview, drone Am,
  granular sparse, cosmos swell.
  4:30-5:30: voyager VUELVE en otra fase, OTRO PATRON (counter-voice
  protagonista, notas distintas, no la melodia clara).
  5:30-6:30: voices L+R full + desarrollo, voyager fragmentos sostenidos.
  6:30-7:00: voyager fase 3 — degraded/distorsion.
  6:00-7:00: climax.
  7:00-8:00: departure con downlifters.

Latido SOLO en 0:30-1:30 (no vuelve en climax).
Voyager con MULTIPLES tracks (L, R, C) para que pueda yendo/viniendo
sin tener que cambiar el pan del track entero.
"""

import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.synth import sine, noise
from aem.instruments import (
    detuned_drone, voice_pad, kick, melody, riser,
    bell, whoosh, downlifter, reverse_swell, granular_pulse,
)
from aem.effects import fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp
from aem.master import dirty_intro

DURATION = 480
OUT = os.path.join(ROOT, 'out', 'outbound')
NAME = 'outbound_FULL'

comp = Composition(DURATION, name='Outbound (full) - v5 voyager dance')

# Voyager melody: D5-F5-A5-F5-D5-A4-D5
VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]
COUNTER_NOTES = [(f * 1.5, d) for f, d in VOYAGER_NOTES]  # 5ta arriba
# Variante para fase 2: notas mas cortas (staccato), ritmo distinto
VOYAGER_STACCATO = [
    (587.33, 0.6), (698.46, 0.5), (880.00, 0.6), (698.46, 0.5),
    (587.33, 0.8), (440.00, 0.8), (587.33, 1.5),
]
# Variante alternativa: arpeggio invertido (D-A-F-A-D-F-A)
VOYAGER_INVERTED = [
    (587.33, 1.0), (440.00, 1.0), (698.46, 1.5), (440.00, 1.0),
    (587.33, 1.5), (698.46, 1.5), (880.00, 2.5),
]

rng = np.random.default_rng(7)


def drone_event(notes, dur, fi=10, fo=15, amp=0.4, n_voices=3, detune_cents=10):
    return fade(detuned_drone(notes, dur, amp=amp,
                              n_voices=n_voices, detune_cents=detune_cents),
                fi=fi, fo=fo)


# ============================================================================
# CAPSULA (0:00 - 0:30) — sub42 + fritura + signals densos
# ============================================================================

# 01. SUB-BASS 42Hz — fuerte al inicio. MUERE a 0:30.
sub = comp.add_track(Track('sub_42hz', gain=0.30, color='#3a4a5c'))
sub.add(0, sine(42, 35, 1.0))
sub.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (3, 1.0), (20, 1.0), (30, 0.0),
]))

# 02. CAPSULE SIGNALS — beeps radio densos durante la capsula
def beep(freq=800, dur=0.12, amp=0.5):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    env = np.sin(np.pi * ta / dur) ** 0.5
    return amp * env * np.sin(2 * np.pi * freq * ta)

signals = comp.add_track(Track('capsule_signals', gain=0.40, color='#4a8a9a'))
sig_times = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
sig_freqs = [800, 1200, 600, 1500, 800, 1200, 600, 1800, 800, 600, 1200, 800, 1500]
for t, f in zip(sig_times, sig_freqs):
    signals.add(t, beep(f, dur=0.10 + rng.random() * 0.08, amp=0.7))
signals.fx(lambda a: lpf(a, 1800))
signals.fx(lambda a: amp_envelope(a, [(0, 1.0), (24, 1.0), (30, 0.0)]))
signals.fx(lambda a: reverb(a, decay=2.0, mix=0.4))

# 03. CAPSULE THUMP — pulso filtrado dentro de la capsula
thump = comp.add_track(Track('capsule_thump', gain=0.45, color='#3c2a2a'))
for t in [5, 10, 15, 20, 25]:
    thump.add(t, kick(amp=0.7, dur=0.9, f0=70, fe=35))
thump.fx(lambda a: lpf(a, 180))
thump.fx(lambda a: reverb(a, decay=4.0, mix=0.5))


# ============================================================================
# LATIDO (0:30 - 1:30) — VELOCIDAD CONSTANTE 60 BPM. NO acelera.
# Fade out rapido a 1:30 cuando entra voyager.
# ============================================================================

# 04. HEART PULSE — la percusion del tema. Tres apariciones distintas:
#   (a) 0:30-1:30 LATIDO PRINCIPAL — constante 60 BPM (te lleva al voyager)
#   (b) 3:30-4:30 LATIDO IN-PACE — sparse (cada 2s) durante el respiro
#   (c) 5:50-6:30 LATIDO CLIMAX — full 60 BPM (embodiment), fade hasta 6:50
heart = comp.add_track(Track('heart_pulse', gain=0.55, color='#d04545'))
# (a) 0:30-1:30 latido principal
for i in range(60):
    t = 30 + i
    amp = 0.7 + (i / 5) * 0.3 if i < 5 else 1.0
    f0_var = 70 + (i % 3 - 1) * 2
    heart.add(t, kick(amp=amp, dur=0.7, f0=f0_var, fe=30))
# fade out rapido 1:30-1:42
for i in range(12):
    t = 90 + i
    amp = 1.0 - (i / 12) * 1.0
    if amp > 0.05:
        heart.add(t, kick(amp=amp, dur=0.6, f0=68, fe=30))

# (b) 3:30-4:30 latido in-pace sparse (cada 2s, amp medium) — percusion calmada
for i in range(15):
    t = 210 + i * 2
    amp = 0.5 + (i % 2) * 0.05  # variacion sutil
    heart.add(t, kick(amp=amp, dur=0.6, f0=68, fe=32))

# (c) 5:50-6:30 latido climax (full 60 BPM, embodiment)
for i in range(40):
    t = 350 + i
    if i < 5:
        amp = 0.7 + (i / 5) * 0.3
    elif i < 30:
        amp = 1.0
    else:
        amp = 1.0 - ((i - 30) / 10) * 0.6
    f0_var = 70 + (i % 3 - 1) * 2
    heart.add(t, kick(amp=amp, dur=0.7, f0=f0_var, fe=30))
# fade out 6:30-6:50
for i in range(20):
    t = 390 + i
    amp = 0.5 - (i / 20) * 0.5
    if amp > 0.05:
        heart.add(t, kick(amp=amp, dur=0.6, f0=68, fe=30))

heart.fx(lambda a: reverb(a, decay=2.5, mix=0.35))


# ============================================================================
# INTRO COMPANION (0:35 - 1:30) — acompañan al latido para que no aburra
# durante el minuto que va solo hasta que entra voyager.
#  - pad agudo D5+A5 sostenido (continuidad armonica)
#  - bells/pings cortos puntuales (eventos sobre el latido)
# ============================================================================

# 05. INTRO PAD HIGH — pad alto D5+A5 que acompaña al latido. Entra a 0:25
# (10s antes que el latido full a 0:30 — los precede para preparar)
intro_pad = comp.add_track(Track('intro_pad_high', gain=0.30, pan=+0.2, color='#a0d0c0'))
intro_pad.add(25, drone_event([587.33, 880.00], 70, fi=12, fo=10, amp=0.35, n_voices=3))
intro_pad.fx(lambda a: reverb(a, decay=5.0, mix=0.6))

# 06. INTRO PINGS — bells cortos como "transmission signals". 6 pings sin gaps largos
intro_pings = comp.add_track(Track('intro_pings', gain=0.70, pan=-0.25, color='#c0e0d0'))
intro_pings.add(40, bell(880.00, dur=5, amp=0.65, decay_rate=2.0))   # 0:40 A5
intro_pings.add(47, bell(587.33, dur=4, amp=0.55, decay_rate=2.5))   # 0:47 D5 — llena gap
intro_pings.add(52, bell(698.46, dur=5, amp=0.60, decay_rate=2.0))   # 0:52 F5
intro_pings.add(65, bell(880.00, dur=5, amp=0.65, decay_rate=2.0))   # 1:05 A5
intro_pings.add(72, bell(587.33, dur=5, amp=0.55, decay_rate=2.2))   # 1:12 D5
intro_pings.add(82, bell(880.00, dur=6, amp=0.70, decay_rate=1.8))   # 1:22 A5 — culminacion
intro_pings.fx(lambda a: reverb(a, decay=5.5, mix=0.65))


# ============================================================================
# COSMOS — viento de fondo siempre presente. LFO breathing.
# ============================================================================

# 05. COSMOS
cosmos = comp.add_track(Track('cosmos', gain=0.10, color='#5a5a5a'))
cosmos.add(2, lpf(noise(470, 1.0), 600))
cosmos.fx(lambda a: lfo_amp(a, rate_hz=0.08, depth=0.5, offset=0.7))
cosmos.fx(lambda a: fade(a, fi=12, fo=20))

# 06. COSMOS swells — peaks puntuales
def cosmos_swell(dur=6.0, peak_amp=0.55, cutoff=900):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    raw = lpf(np.random.randn(n), cutoff)
    env = np.sin(np.pi * ta / dur) ** 2
    return raw * env * peak_amp

swells = comp.add_track(Track('cosmos_swells', gain=0.50, color='#7a7a90'))
for t in [60, 95, 130, 165, 200, 235, 265, 295, 330, 365, 405, 445]:
    swells.add(t, cosmos_swell(dur=5 + rng.random() * 5))
swells.fx(lambda a: reverb(a, decay=4.5, mix=0.55))


# ============================================================================
# CUE RELEASE — riser largo culminando a 1:00 (transicion fritura -> latido)
# ============================================================================

# 07. CUE RELEASE
def long_riser(dur=10, f_start=40, f_end=400):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    fr = f_start + (f_end - f_start) * (ta / dur) ** 2
    ph = 2 * np.pi * np.cumsum(fr) / SR
    env = np.linspace(0, 1, n) ** 1.5
    return np.sin(ph) * env

cue_release = comp.add_track(Track('cue_release_1min', gain=0.45, color='#b09040'))
cue_release.add(20, long_riser(dur=10, f_start=40, f_end=500))  # culmina a 0:30 con latido
cue_release.fx(lambda a: lpf(a, 2500))
cue_release.fx(lambda a: reverb(a, decay=3.0, mix=0.4))


# ============================================================================
# DRONES ARMONICOS — Dm -> Bb -> F -> Am -> Dm, crossfades de 25s
# ============================================================================

# 08. DRONE Dm (D-F-A) — establecimiento, 0:50 → 2:30
drone_dm = comp.add_track(Track('drone_Dm', gain=0.36, color='#7a5cb8'))
drone_dm.add(50, drone_event([146.83, 174.61, 220.00], 100, fi=15, fo=25))
drone_dm.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 09. DRONE Bb (Bb-D-F) — tension, 2:00 → 3:30
drone_bb = comp.add_track(Track('drone_Bb', gain=0.32, color='#9070a8'))
drone_bb.add(120, drone_event([116.54, 146.83, 174.61], 90, fi=25, fo=25))
drone_bb.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 10. DRONE F (F-A-C) — apertura, 2:50 → 4:30
drone_f = comp.add_track(Track('drone_F', gain=0.34, color='#a888a0'))
drone_f.add(170, drone_event([174.61, 220.00, 261.63], 100, fi=25, fo=25))
drone_f.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 11. DRONE Am (A-C-E) — in-pace + voyager fase 2, 3:50 → 5:30
drone_am = comp.add_track(Track('drone_Am', gain=0.32, color='#9080b0'))
drone_am.add(230, drone_event([110.00, 130.81, 164.81], 100, fi=25, fo=25))
drone_am.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 12. DRONE Dm climax/end — vuelta a casa, 4:55 → 8:00
drone_dm2 = comp.add_track(Track('drone_Dm_end', gain=0.42, color='#6a4ca8'))
drone_dm2.add(295, drone_event([146.83, 174.61, 220.00], 185, fi=25, fo=35))
drone_dm2.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# BASSLINE — linea melodica grave que sigue los acordes
# ============================================================================

# 13. BASSLINE
bass = comp.add_track(Track('bassline', gain=0.55, color='#2c3a4c'))
bass_notes = [
    (50,  73.42, 75, 8, 20),     # 0:50 D2
    (115, 58.27, 70, 20, 20),    # 1:55 Bb1
    (175, 87.31, 70, 20, 20),    # 2:55 F2
    (235, 110.00, 70, 20, 20),   # 3:55 A2
    (295, 73.42, 175, 20, 30),   # 4:55 D2 hasta final
]
for t, freq, dur, fi, fo in bass_notes:
    bass.add(t, drone_event([freq], dur, fi=fi, fo=fo, amp=0.5, n_voices=2))
bass.fx(lambda a: lpf(a, 220))
bass.fx(lambda a: reverb(a, decay=4.5, mix=0.4))


# ============================================================================
# DRONE SHIMMER — capa aguda que da movimiento timbral
# ============================================================================

# 14. DRONE SHIMMER
shimmer = comp.add_track(Track('drone_shimmer', gain=0.22, pan=+0.2, color='#a8b0d8'))
shimmer.add(75,  drone_event([587.33, 698.46], 60, fi=15, fo=15))
shimmer.add(150, drone_event([587.33, 698.46, 880.00], 65, fi=15, fo=15))
shimmer.add(220, drone_event([523.25, 698.46, 880.00], 70, fi=15, fo=15))
shimmer.add(295, drone_event([587.33, 698.46, 880.00], 110, fi=20, fo=25))
shimmer.fx(lambda a: reverb(a, decay=5.0, mix=0.6))


# ============================================================================
# GRANULAR BED — pulsos cortos. DENSO en primeros 2 min, sparse en in-pace.
# ============================================================================

# 15. GRANULAR BED — denso 0:50 a 3:30, sparse 3:30 a 4:30, denso 4:30 a 7:00
granular = comp.add_track(Track('granular_bed', gain=0.42, color='#6c8a7a'))
gr_freqs = [200, 280, 380, 500, 650, 850, 1100]
# Fase 1 densa: 0:50 a 3:30 cada 2-4s
t = 50
while t < 210:
    freq = rng.choice(gr_freqs)
    granular.add(t, granular_pulse(freq=freq, dur=0.4 + rng.random() * 0.4, amp=0.6))
    t += 2 + rng.random() * 2
# In-pace sparse: 3:30 a 4:30 cada 5-9s
while t < 270:
    freq = rng.choice(gr_freqs)
    granular.add(t, granular_pulse(freq=freq, dur=0.5 + rng.random() * 0.4, amp=0.4))
    t += 5 + rng.random() * 4
# Fase 2 + climax: 4:30 a 7:00 cada 2-4s
while t < 420:
    freq = rng.choice(gr_freqs)
    granular.add(t, granular_pulse(freq=freq, dur=0.4 + rng.random() * 0.4, amp=0.6))
    t += 2 + rng.random() * 2
granular.fx(lambda a: reverb(a, decay=3.5, mix=0.55))


# ============================================================================
# SUB PULSES — pulso lento intermitente. Solo durante latido (1:00-1:25)
# y despues sparse durante in-pace (3:50-4:25)
# ============================================================================

# 16. SUB PULSES
sub_pulses = comp.add_track(Track('sub_pulses', gain=0.50, color='#5c4a3c'))
for t in [62, 78, 230, 250, 265]:
    sub_pulses.add(t, kick(amp=0.6, dur=1.2, f0=80, fe=42))
sub_pulses.fx(lambda a: lpf(a, 220))
sub_pulses.fx(lambda a: reverb(a, decay=4.0, mix=0.3))


# ============================================================================
# VOYAGER FASE 1 (1:30-3:30) — JUEGA 2 MINUTOS yendo y viniendo entre L/R/C
# ============================================================================

# Tres tracks paneados distintos. Eventos repartidos.

# 17. VOYAGER LEFT (pan +0.4)
voy_l = comp.add_track(Track('voyager_left', gain=0.55, pan=+0.4, color='#e6c34d'))
voy_l.add(90,  melody(VOYAGER_NOTES, amp=0.55))                 # 1:30 entrada principal L
voy_l.add(130, melody(VOYAGER_NOTES[0:3], amp=0.45))            # 2:10 fragmento corto L
voy_l.add(175, melody(VOYAGER_NOTES, amp=0.50))                 # 2:55 vuelve completo L
voy_l.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 18. VOYAGER RIGHT (pan -0.4)
voy_r = comp.add_track(Track('voyager_right', gain=0.50, pan=-0.4, color='#c89b3a'))
voy_r.add(115, melody(VOYAGER_NOTES, amp=0.50))                 # 1:55 responde R
voy_r.add(150, melody(VOYAGER_NOTES[2:5], amp=0.45))            # 2:30 fragmento medio R
voy_r.add(195, melody(VOYAGER_NOTES, amp=0.50))                 # 3:15 R
voy_r.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 19. VOYAGER CENTER (pan 0) — fragmentos cortos y ecos
voy_c = comp.add_track(Track('voyager_center', gain=0.45, pan=0, color='#f0d060'))
voy_c.add(105, melody(VOYAGER_NOTES[0:2], amp=0.40))            # 1:45 fragmento C
voy_c.add(145, melody(VOYAGER_NOTES[5:7], amp=0.40))            # 2:25 final notas C
voy_c.add(165, melody(VOYAGER_NOTES[0:4], amp=0.45))            # 2:45 C
voy_c.add(210, melody([(587.33, 2.0), (440.00, 2.5)], amp=0.40))  # 3:30 ultima nota antes del in-pace
voy_c.fx(lambda a: reverb(a, decay=5.0, mix=0.55))

# --- VOYAGER COMPANION (1:30 - 3:30) — sostiene la TENSION del dance ---

# VOYAGER SWELL — pad alto D5+A5 sostenido EN CRESCENDO durante todo el dance.
# Usa D y A (notas comunes a Dm, Bb, F → los 3 acordes del dance).
# Crescendo: 0.5 → 1.3x sobre 2 minutos. La tension crece hasta el in-pace.
voy_swell = comp.add_track(Track('voyager_swell', gain=0.32, pan=+0.3, color='#b0e0d0'))
voy_swell.add(85, drone_event([587.33, 880.00], 130, fi=12, fo=15, amp=0.45, n_voices=3))
voy_swell.fx(lambda a: amp_envelope(a, [
    (0, 0.5),       # antes del evento (zeros, no afecta)
    (85, 0.5),      # 1:25 - inicio
    (115, 0.7),     # 1:55 - sube
    (145, 0.9),     # 2:25 - mas
    (175, 1.1),     # 2:55 - peak crescendo
    (210, 1.3),     # 3:30 - culmen
    (215, 0.0),     # 3:35 - corte para in-pace
    (480, 0.0),
]))
voy_swell.fx(lambda a: reverb(a, decay=6.0, mix=0.65))

# VOYAGER COMPANION PINGS — bells armonizados con cada seccion del dance
# Llenan gaps cada 12-18s entre los eventos voyager principales
voy_pings = comp.add_track(Track('voyager_pings', gain=0.55, pan=-0.3, color='#d8e0a0'))
# (sacamos el bell A5 de 1:48 — "sobraba" justo despues del fragment voyager_center)
voy_pings.add(112, bell(587.33, dur=4, amp=0.50, decay_rate=2.5))   # 1:52 D5 — llena silencio
voy_pings.add(125, bell(698.46, dur=5, amp=0.50, decay_rate=2.2))   # 2:05 F5 (transicion Bb)
voy_pings.add(140, bell(587.33, dur=6, amp=0.55, decay_rate=2.0))   # 2:20 D5 (Bb)
voy_pings.add(160, bell(698.46, dur=6, amp=0.55, decay_rate=2.0))   # 2:40 F5 (Bb→F)
voy_pings.add(178, bell(880.00, dur=6, amp=0.60, decay_rate=1.8))   # 2:58 A5 (F)
voy_pings.add(195, bell(523.25, dur=6, amp=0.55, decay_rate=2.0))   # 3:15 C5 (F)
voy_pings.fx(lambda a: reverb(a, decay=5.5, mix=0.65))


# 20. VOYAGER ECHO — "voyager que vuelve distinto". LPF + reverb largo + lejos.
# Aparece en gaps para que no se pierda el hilo del tema.
voy_echo = comp.add_track(Track('voyager_echo', gain=0.32, pan=-0.5, color='#8a7030'))
voy_echo.add(94,  melody(VOYAGER_NOTES, amp=0.32))                  # eco del 1:30
voy_echo.add(199, melody(VOYAGER_NOTES, amp=0.30))                  # eco del 3:15
voy_echo.add(220, melody(VOYAGER_NOTES[2:5], amp=0.30))             # 3:40 in-pace eco
voy_echo.add(255, melody(VOYAGER_NOTES[:4], amp=0.32))              # 4:15 in-pace eco
voy_echo.add(340, melody(VOYAGER_NOTES, amp=0.34))                  # 5:40 entre fase 2 y voices full
voy_echo.add(410, melody(VOYAGER_INVERTED[:4], amp=0.32))           # 6:50 climax eco distante
voy_echo.fx(lambda a: lpf(a, 1800))
voy_echo.fx(lambda a: reverb(a, decay=6.0, mix=0.7))


# ============================================================================
# IN-PACE (3:30-4:30) — voyager se va, calma. voices_preview entra.
# ============================================================================

# 21. VOICES preview — entra a 4:00 con fade largo (boosted, era inaudible)
# Fade aplicado al evento (no al track) — sino el fade no afecta porque el track
# es zeros hasta 4:00.
voices_preview = comp.add_track(Track('voices_preview', gain=0.45, color='#a89090'))
voices_preview.add(240, fade(voice_pad(293.66, 75, vibrato_rate=4.0, amp=0.42), fi=20, fo=15))
voices_preview.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# VOYAGER FASE 2 (4:30-5:30) — VUELVE con OTRO PATRON
# Counter-voice (5ta arriba) + staccato + notas invertidas. NO el patron clasico.
# ============================================================================

# 22. VOYAGER COUNTER — la 5ta arriba protagonista, paneada izquierda
voy_counter = comp.add_track(Track('voyager_counter_2', gain=0.45, pan=-0.5, color='#d8a830'))
voy_counter.add(270, melody(COUNTER_NOTES, amp=0.45))           # 4:30 counter L
voy_counter.add(310, melody(COUNTER_NOTES[0:5], amp=0.40))      # 5:10 counter L fragmento
voy_counter.fx(lambda a: reverb(a, decay=5.5, mix=0.6))

# VOYAGER INVERTED — notas en otro orden, paneada C
# (eliminado voyager_staccato — el ritmo acelerado no encajaba)
voy_inv = comp.add_track(Track('voyager_inverted', gain=0.40, pan=0, color='#f0c050'))
voy_inv.add(330, melody(VOYAGER_INVERTED, amp=0.45))            # 5:30 inverted C — bridge a fase 3
voy_inv.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# VOICES FULL (5:00-7:00) — humano que despierta
# ============================================================================

# 25. VOICES L (D4 -> Eb4 -> D4)
# Fade in/out aplicado a CADA evento (no al track, porque el track empieza en
# 0:00 con zeros y el fade de track no afecta los eventos posteriores).
# Ultimo evento ACORTADO de 50s a 28s (terminaba a 7:23, muy largo).
voices_l = comp.add_track(Track('voices_l_d4', gain=0.36, pan=-0.5, color='#c87a8c'))
voices_l.add(300, fade(voice_pad(293.66, 50, vibrato_rate=4.0, amp=0.45), fi=10, fo=8))  # 5:00 D4
voices_l.add(348, fade(voice_pad(311.13, 45, vibrato_rate=3.8, amp=0.45), fi=8, fo=6))   # 5:48 Eb4
voices_l.add(393, fade(voice_pad(293.66, 28, vibrato_rate=4.2, amp=0.45), fi=8, fo=10))  # 6:33 D4 → 7:01
voices_l.fx(lambda a: reverb(a, decay=4.5, mix=0.55))

# 26. VOICES R (A4 -> Bb4 -> A4)
voices_r = comp.add_track(Track('voices_r_a4', gain=0.36, pan=+0.5, color='#c87a8c'))
voices_r.add(300, fade(voice_pad(440.00, 50, vibrato_rate=4.5, amp=0.45), fi=10, fo=8))  # 5:00 A4
voices_r.add(348, fade(voice_pad(466.16, 45, vibrato_rate=4.3, amp=0.45), fi=8, fo=6))   # 5:48 Bb4
voices_r.add(393, fade(voice_pad(440.00, 28, vibrato_rate=4.7, amp=0.45), fi=8, fo=10))  # 6:33 A4 → 7:01
voices_r.fx(lambda a: reverb(a, decay=4.5, mix=0.55))


# ============================================================================
# VOYAGER FASE 3 (6:30-7:00) — DEGRADED. Climax foreshadow.
# ============================================================================

# 27. VOYAGER DEGRADED — distorsion + lpf + octava abajo
def voyager_deg(notes_subset=None):
    notes = notes_subset or VOYAGER_NOTES
    low_notes = [(f / 2, d) for f, d in notes]
    raw = melody(low_notes, amp=0.5)
    return distort(lpf(raw, 1500), amount=2.5)

voyager_alien = comp.add_track(Track('voyager_degraded', gain=0.36, pan=-0.3, color='#a04030'))
voyager_alien.add(360, voyager_deg())                           # 6:00 entra
voyager_alien.add(390, voyager_deg(VOYAGER_NOTES[2:6]))         # 6:30 fragmento degraded
voyager_alien.add(415, voyager_deg(VOYAGER_INVERTED))           # 6:55 inverted degraded
voyager_alien.fx(lambda a: reverb(a, decay=5.5, mix=0.65))


# ============================================================================
# GLUE PUNTUAL — bells, whooshes, reverse_swells, downlifters, risers
# ============================================================================

# 28. BELL MARKERS — campanas armonizadas con cada seccion
bells = comp.add_track(Track('bell_markers', gain=0.48, color='#d8c060'))
bells.add(60,  bell(587.33, dur=10, amp=0.5))    # 1:00 D5 (Dm)
bells.add(90,  bell(880.00, dur=10, amp=0.55))   # 1:30 A5 — coincide con voyager entrada
bells.add(120, bell(698.46, dur=12, amp=0.5))    # 2:00 F5 (Bb)
bells.add(180, bell(880.00, dur=14, amp=0.55))   # 3:00 A5 (F)
bells.add(240, bell(659.25, dur=12, amp=0.55))   # 4:00 E5 (Am, in-pace)
bells.add(270, bell(880.00, dur=12, amp=0.5))    # 4:30 A5 — voyager fase 2
bells.add(330, bell(880.00, dur=14, amp=0.6))    # 5:30 A5 — bridge
bells.add(360, bell(880.00, dur=16, amp=0.7))    # 6:00 A5 climax
bells.add(420, bell(587.33, dur=14, amp=0.55))   # 7:00 D5 closure
bells.fx(lambda a: reverb(a, decay=6.5, mix=0.65))

# 29. WHOOSHES — pre-evento
whooshes = comp.add_track(Track('whooshes', gain=0.40, color='#90a0b0'))
whooshes.add(27,  whoosh(dur=3, direction='up'))      # pre 0:30 latido
whooshes.add(87,  whoosh(dur=3.5, direction='up'))    # pre 1:30 voyager entrada
whooshes.add(177, whoosh(dur=3, direction='up'))      # pre 3:00
whooshes.add(207, whoosh(dur=3, direction='down'))    # pre 3:30 in-pace (down — relax)
whooshes.add(267, whoosh(dur=4, direction='up'))      # pre 4:30 voyager fase 2
whooshes.add(295, whoosh(dur=4, direction='up'))      # pre 5:00 voices
whooshes.add(355, whoosh(dur=5, direction='up'))      # pre 6:00 climax
whooshes.add(417, whoosh(dur=4, direction='down'))    # pre 7:00 departure
whooshes.fx(lambda a: reverb(a, decay=3.5, mix=0.55))

# 30. REVERSE SWELLS — antes de eventos importantes
reverse = comp.add_track(Track('reverse_swells', gain=0.50, color='#7a90c0'))
reverse.add(86,  reverse_swell(dur=4, freq=147))    # pre 1:30 voyager entrada
reverse.add(176, reverse_swell(dur=4, freq=174))    # pre 3:00
reverse.add(266, reverse_swell(dur=4, freq=110))    # pre 4:30 fase 2
reverse.add(296, reverse_swell(dur=4, freq=147))    # pre 5:00 voices
reverse.add(354, reverse_swell(dur=6, freq=110))    # pre 6:00 climax
reverse.fx(lambda a: reverb(a, decay=4.0, mix=0.6))

# 31. DOWNLIFTERS — landings post-evento
downs = comp.add_track(Track('downlifters', gain=0.32, color='#9090a0'))
downs.add(208, downlifter(dur=8, f_start=350, f_end=80))    # 3:28 entra in-pace (relax)
downs.add(420, downlifter(dur=8, f_start=400, f_end=42))    # 7:00 entra departure
downs.add(465, downlifter(dur=12, f_start=300, f_end=42))   # 7:45 dive final
downs.fx(lambda a: reverb(a, decay=3.5, mix=0.5))

# 32. RISERS — cues de eventos
risers_track = comp.add_track(Track('risers', gain=0.32, color='#909090'))
risers_track.add(85,  riser(dur=5))   # cue voyager entrada 1:30 (mas largo, importante)
risers_track.add(175, riser(dur=4))   # cue 3:00
risers_track.add(265, riser(dur=4))   # cue voyager fase 2 4:30
risers_track.add(295, riser(dur=5))   # cue voices 5:00
risers_track.add(355, riser(dur=6))   # cue climax 6:00
risers_track.fx(lambda a: lpf(a, 2000))
risers_track.fx(lambda a: reverb(a, decay=3.0, mix=0.4))


if __name__ == '__main__':
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    comp.list_tracks()
    print()
    master_fx = lambda a: dirty_intro(
        a,
        dirty_until=8,
        transition_dur=22,       # clean total a 0:30 (cuando entra el latido)
        n_crackles=70,
        dirty_gain=0.80,
        transition_curve=2.5,
    )
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'), master_fx=master_fx)
    comp.export_stems(os.path.join(OUT, 'stems', NAME), master_fx=master_fx)
