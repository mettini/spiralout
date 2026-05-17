"""Outbound — TEMA COMPLETO (8:00), variante v0 BALANCED.

v6 — aplicacion de tecnicas nuevas (T10-T13) descubiertas armando
Crossing/Recursion. Mantiene la estructura narrativa de v5:

  1er minuto: capsula con fritura -> latido. Latido entra a 0:30 a 60 BPM
  CONSTANTE (no acelera) hasta 1:30 donde se VA con fade rapido.
  1:30: voyager entra y JUEGA durante 2 minutos (1:30-3:30) yendo y
  viniendo entre L y R, con fragmentos, ecos, distintas formas.
  3:30-4:30: in-pace. Voyager se va. Calma con voices_preview, drone Am,
  granular sparse, cosmos swell.
  4:30-5:30: voyager VUELVE en otra fase, OTRO PATRON.
  5:30-6:30: voices L+R full + desarrollo, voyager fragmentos sostenidos.
  6:00-7:00: climax. 6:30-7:00 voyager degraded.
  7:00-8:00: departure con downlifters.

CAMBIOS v6:
  - Capsula (0:00-0:30): agregada capa field_atmosphere (Lustmord-style)
  - Voyager dance (1:30-3:30): passing objects estereo (movement L<->R)
  - Embodiment build (5:00-5:30): voyager_swell con phasing leve
  - Climax (6:00-7:00): glitches sutiles (Burial-style) + bell de cierre
  - Departure (7:00-8:00): mellotron pad alto
  - voyager_degraded: aplicado radio_interference (T13)
  - Drones principales: tape_warm sutil para warmth analogica (T11)
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))            # transmissions/01
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))    # repo root
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.synth import sine, noise
from aem.instruments import (
    detuned_drone, voice_pad, kick, melody, riser,
    bell, whoosh, downlifter, reverse_swell, granular_pulse,
)
from aem.motifs import voyager_motif, voyager_safe, voyager_safe_fx, VOYAGER_NOTES_TIGHT
from aem.voyager_factory import voyager_track
from aem.effects import (
    fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp,
    tape_warm, radio_interference, notch_eq,
)


def voyager(amp, variation='main', subset=None, octave_shift=0):
    """Wrapper local: usa voyager_safe (benchmark TOOL).

    NO MODIFICAR sin confirmacion — el voyager es el alma del album.
    Los notches/LPF de proteccion los aplica voyager_safe_fx() al track.
    """
    return voyager_safe(amp=amp, variation=variation, subset=subset,
                        octave_shift=octave_shift)


def voyager_notch(track, include_c6=False):
    """DEPRECATED — usar voyager_safe_fx(track). Mantenido como alias."""
    voyager_safe_fx(track)
from aem.master import dirty_intro

DURATION = 480
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'outbound')
NAME = 'outbound_FULL'

comp = Composition(DURATION, name='Outbound (full) - v6 dark techniques')

# Voyager melody: D5-F5-A5-F5-D5-A4-D5
VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]
COUNTER_NOTES = [(f * 1.5, d) for f, d in VOYAGER_NOTES_TIGHT]  # 5ta arriba con duraciones TIGHT (patron validado)
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

# 01. SUB-BASS 42Hz — peak 0.75 (era 1.0), ramp más suave (12s en vez de 10).
# Razon: el sub sostenido a peak 1.0 durante 15s pelaba contra el limiter
# del master chain. Bajar el peak deja headroom y evita que el limiter
# trabaje constantemente en esa zona. El concepto "capsula" se mantiene.
sub = comp.add_track(Track('sub_42hz', gain=0.14, color='#3a4a5c'))   # 0.20→0.12 (user x0.6)
sub.add(0, sine(42, 35, 1.0))
# Envelope peak bajado 0.75→0.50 — sub presente pero no quema lo demas
sub.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (10, 0.20), (20, 0.50), (25, 0.50), (32, 0.0),
]))

# Sub_42hz IN-PACE — abismo cosmico sutil 3:30-4:30 (track separado, gain mas bajo)
sub_inpace = comp.add_track(Track('sub_42hz_in_pace', gain=0.07, color='#3a4a5c'))
sub_inpace.add(195, sine(42, 60, 1.0))   # 3:15 dur 60s — adelantado de 3:30
sub_inpace.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (195, 0.0), (205, 0.40), (245, 0.40), (255, 0.0),   # peak 0.30→0.40 (mas intensidad)
]))

# 02. CAPSULE SIGNALS — beeps radio. Empiezan a 0:10 (no a 0:02) para que
# el sub_42hz tenga unos segundos de respirar primero.
def beep(freq=800, dur=0.12, amp=0.5):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    env = np.sin(np.pi * ta / dur) ** 0.5
    return amp * env * np.sin(2 * np.pi * freq * ta)

signals = comp.add_track(Track('capsule_signals', gain=0.18, color='#4a8a9a'))   # 0.13→0.18
# Patron: grupo 1 (00:10) 4 notas, grupo 2 (00:20) repite las MISMAS 4 con la
# ultima SUBIDA (1500 → 1800) — frase + respuesta amplificada.
sig_times = [10, 12, 14, 16,    18, 20, 22, 24]
sig_freqs = [800, 1200, 600, 1500,    800, 1200, 600, 1800]
sig_amps  = [0.30, 0.35, 0.40, 0.50,    0.40, 0.45, 0.50, 0.60]   # grupo 2 mas presente (respuesta fuerte)
for t, f, a in zip(sig_times, sig_freqs, sig_amps):
    signals.add(t, beep(f, dur=0.10 + rng.random() * 0.08, amp=a))
signals.fx(lambda a: lpf(a, 2400))   # 1800→2400 (Lustmord open)
signals.fx(lambda a: amp_envelope(a, [(0, 1.0), (26, 1.0), (30, 0.0)]))
signals.fx(lambda a: reverb(a, decay=2.0, mix=0.4))

# 03. CAPSULE THUMP — empieza a 0:12 (no a 0:05). 4 thumps en lugar de 5.
thump = comp.add_track(Track('capsule_thump', gain=0.45, color='#3c2a2a'))
for t in [12, 17, 22, 27]:
    thump.add(t, kick(amp=0.55, dur=0.9, f0=60, fe=60, attack_ms=8, release_ms=200, pitch_sweep=False))   # sine pura (anti-fritura)
thump.fx(lambda a: lpf(a, 180))
thump.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 03b. CAPSULE FIELD ATMOSPHERE (v6) — Lustmord-style. Empieza a 0:08 con
# fade in (antes empezaba a 0:00 sumandose al sub abrupto).
field_capsule = comp.add_track(Track('capsule_field', gain=0.05, color='#3a3a3a'))
# Bajado gain 0.15→0.05 + amp interno 1.5→0.7. Era "estatica de cable de
# guitarra" (noise grave random + lpf 350) que sumaba buzz al inicio.
field_capsule.add(8, fade(lpf(noise(24, 0.7), 350), fi=6, fo=4))
field_capsule.fx(lambda a: lfo_amp(a, rate_hz=0.12, depth=0.5, offset=0.6))
field_capsule.fx(lambda a: reverb(a, decay=4.5, mix=0.5))


# ============================================================================
# LATIDO (0:30 - 1:30) — VELOCIDAD CONSTANTE 60 BPM. NO acelera.
# Fade out rapido a 1:30 cuando entra voyager.
# ============================================================================

# 04. HEART PULSE — la percusion del tema. Tres apariciones distintas:
#   (a) 0:30-1:30 LATIDO PRINCIPAL — constante 60 BPM (te lleva al voyager)
#   (b) 3:30-4:30 LATIDO IN-PACE — sparse (cada 2s) durante el respiro
#   (c) 5:50-6:30 LATIDO CLIMAX — full 60 BPM (embodiment), fade hasta 6:50
heart = comp.add_track(Track('heart_pulse', gain=0.09, color='#d04545'))   # user feedback 0:38 muy fuerte vs intro_pings — entre restore 0.12 y cut 0.06   # 0.12→0.06 (user x0.5)


def heart_kick(amp, dur):
    """Helper: kick MUY corto tipo heart beat real (thud-thud, no rebote, no echo).
    Curva natural: ataque suave 8ms, dur 0.4s con release 40ms cosine = corte rapido."""
    return kick(amp=amp, dur=0.4, f0=60,
                attack_ms=8.0, release_ms=40.0, pitch_sweep=False)
# (a) 0:30-1:10 latido principal — amp peak bajado a 0.65 (era 1.0, monopolizaba)
for i in range(40):
    t = 30 + i
    amp = 0.45 + (i / 5) * 0.20 if i < 5 else 0.65
    f0_var = 70 + (i % 3 - 1) * 2
    heart.add(t, heart_kick(amp=amp, dur=0.7))
# fade out 1:10-1:20 — peak 0.65 → 0
for i in range(10):
    t = 70 + i
    amp = 0.65 - (i / 10) * 0.65
    if amp > 0.05:
        heart.add(t, heart_kick(amp=amp, dur=0.6))

# 1 kick 1:36 — SACADO el de 1:38 (coincidia con entrada del bassline = TIC compuesto)
heart.add(96,  heart_kick(amp=0.45, dur=0.5))   # 1:36

# Reminiscencia 2:10-2:31 — 8 kicks amp 1.0 para que se escuchen claros
for t_kick in [130, 133, 136, 139, 142, 145, 148, 151]:
    heart.add(t_kick, heart_kick(amp=1.0, dur=0.5))

# (b) 3:30-4:30 latido in-pace sparse (cada 2s, amp medium) — percusion calmada
for i in range(15):
    t = 210 + i * 2
    amp = 0.5 + (i % 2) * 0.05  # variacion sutil
    heart.add(t, heart_kick(amp=amp, dur=0.6))

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
    heart.add(t, heart_kick(amp=amp, dur=0.7))
# fade out 6:30-6:50
for i in range(20):
    t = 390 + i
    amp = 0.5 - (i / 20) * 0.5
    if amp > 0.05:
        heart.add(t, heart_kick(amp=amp, dur=0.6))

heart.fx(lambda a: lpf(a, 200))                            # tapado sub-grave
# SACADO reverb — heart beat real no tiene rebote/echo, es thud seco


# ============================================================================
# INTRO COMPANION (0:35 - 1:30) — acompañan al latido para que no aburra
# durante el minuto que va solo hasta que entra voyager.
#  - pad agudo D5+A5 sostenido (continuidad armonica)
#  - bells/pings cortos puntuales (eventos sobre el latido)
# ============================================================================

# 05. INTRO PAD HIGH — pad alto D5+A5 que acompaña al latido. Entra a 0:25
# (10s antes que el latido full a 0:30 — los precede para preparar)
intro_pad = comp.add_track(Track('intro_pad_high', gain=0.20, pan=+0.2, color='#a0d0c0'))   # 0.20→0.12 (user x0.6)
intro_pad.add(25, drone_event([587.33, 880.00], 55, fi=12, fo=15, amp=0.35, n_voices=3))
intro_pad.add(118, drone_event([587.33, 880.00], 15, fi=4, fo=4, amp=0.22, n_voices=3))   # 1:58-2:13 (era 2:03)   # dur 70→55, fo 10→15: termina fade out a 1:20 (antes 1:35) — no se pisa con drone_shimmer 1:21
intro_pad.fx(lambda a: reverb(a, decay=5.0, mix=0.50))   # 0.6→0.50 (Lustmord less wet)

# 06. INTRO PINGS — bells cortos como "transmission signals". 6 pings sin gaps largos
intro_pings = comp.add_track(Track('intro_pings', gain=0.65, pan=-0.25, color='#c0e0d0'))   # 0.50→0.65 (mas presente sobre el heart beat)
# Bells anticipados -0.3s para entrar ENTRE beats del heart_pulse (kick por seg).
# Antes caian EXACTO en beat = competian con el ataque del kick.
intro_pings.add(39.7, bell(880.00, dur=5, amp=0.65, decay_rate=2.0))   # 0:40 A5
intro_pings.add(46.7, bell(587.33, dur=4, amp=0.55, decay_rate=2.5))   # 0:47 D5
intro_pings.add(51.7, bell(698.46, dur=5, amp=0.60, decay_rate=2.0))   # 0:52 F5
intro_pings.add(58.0, bell(587.33, dur=5, amp=0.55, decay_rate=2.3))   # 0:58 D5 — reemplaza al cosmos_swell sacado
intro_pings.add(64.7, bell(880.00, dur=5, amp=0.65, decay_rate=2.0))   # 1:05 A5
intro_pings.add(71.7, bell(587.33, dur=5, amp=0.55, decay_rate=2.2))   # 1:12 D5
# SACADO bell 1:22 A5 — el user no quiere ese ping ahi.
# intro_pings.add(82, bell(880.00, dur=6, amp=0.70, decay_rate=1.8))
intro_pings.fx(lambda a: lpf(a, 2000))                              # 1500→2000 (Lustmord open)
intro_pings.fx(lambda a: reverb(a, decay=5.5, mix=0.50))            # 0.65→0.50


# ============================================================================
# COSMOS — viento de fondo siempre presente. LFO breathing.
# ============================================================================

# 05. COSMOS
cosmos = comp.add_track(Track('cosmos', gain=0.05, color='#5a5a5a'))   # user x0.5 desde UI — se metia en todos lados   # 0.10→0.06 (user x0.6 todo)
cosmos.add(2, fade(lpf(noise(470, 1.0), 600), fi=10, fo=10))   # fade in 10s al evento (entraba abrupto)
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
# SACADO swell t=95 (1:35) — caia justo en el peak de density 1:30-1:42 (13 stems
# activos detectados por QA perceptual). El siguiente swell esta a t=130 (2:10).
for t in [165, 200, 235, 265, 295]:   # SACADO 330 (5:30) por user — SACADOS 130, 365, 405, 445 antes
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

cue_release = comp.add_track(Track('cue_release_1min', gain=0.28, color='#b09040'))   # 0.28→0.14 (user x0.5)
cue_release.add(70, fade(long_riser(dur=10, f_start=40, f_end=250), fi=0, fo=1.5))   # peak a 1:20 + fo 1.5s mas suave (era 0.3)
cue_release.fx(lambda a: lpf(a, 2000))
cue_release.fx(lambda a: reverb(a, decay=5.0, mix=0.5))   # decay 3→5, mix 0.4→0.5 — cola larga DESPUES del peak (lo que pidio el user)


# ============================================================================
# DRONES ARMONICOS — Dm -> Bb -> F -> Am -> Dm, crossfades de 25s
# ============================================================================

# 08. DRONE Dm (D-F-A) — establecimiento, 0:50 → 2:30
drone_dm = comp.add_track(Track('drone_Dm', gain=0.36, color='#7a5cb8'))   # 0.36→0.252 (user x0.7 densidad 02:24)
drone_dm.add(90, drone_event([146.83, 174.61, 220.00], 110, fi=15, fo=25))   # 50→90 (1:30) — entra DESPUES del voyager (1:21) como soporte armonico
drone_dm.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 09. DRONE Bb (Bb-D-F) — tension, 2:00 → 3:30
drone_bb = comp.add_track(Track('drone_Bb', gain=0.32, color='#9070a8'))
drone_bb.add(120, drone_event([116.54, 146.83, 174.61], 90, fi=25, fo=25))
drone_bb.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 10. DRONE F (F-A-C) — apertura, 2:50 → 4:30
drone_f = comp.add_track(Track('drone_F', gain=0.34, color='#a888a0'))   # 0.34→0.238 (user x0.7 densidad 02:24)
drone_f.add(170, drone_event([174.61, 220.00, 261.63], 100, fi=25, fo=25))
drone_f.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 11. DRONE Am (A-C-E) — in-pace + voyager fase 2, 3:50 → 5:30
drone_am = comp.add_track(Track('drone_Am', gain=0.32, color='#9080b0'))
drone_am.add(257, drone_event([110.00, 130.81, 164.81], 73, fi=25, fo=25))   # 3:50→4:17 (atrasado), dur 100→73 (mantiene end 5:30)
drone_am.fx(lambda a: reverb(a, decay=4.5, mix=0.5))

# 12. DRONE Dm climax/end — vuelta a casa, 4:55 → 8:00
drone_dm2 = comp.add_track(Track('drone_Dm_end', gain=0.42, color='#6a4ca8'))
drone_dm2.add(342, drone_event([146.83, 174.61, 220.00], 138, fi=25, fo=35))   # start 5:42 (era 5:16), dur 138 (mantiene end 8:00)
drone_dm2.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# BASSLINE — linea melodica grave que sigue los acordes
# ============================================================================

# 13. BASSLINE
bass = comp.add_track(Track('bassline', gain=0.38, color='#2c3a4c'))   # 0.38→0.266 (user x0.7 densidad 02:24)
# SACADA la primera nota a 0:50 — el bassline NO suena hasta 1:45.
# Amps internos bajados a la mitad (0.5 → 0.25) — "no rompe las pelotas".
bass_notes = [
    (98,  73.42, 17, 5, 5),      # 1:38 D2 — entrada del bassline (105→98, dur 12→17 para conectar con Bb1)
    (115, 58.27, 70, 5, 20),     # 1:55 Bb1
    (175, 87.31, 70, 20, 20),    # 2:55 F2
    (235, 110.00, 70, 20, 20),   # 3:55 A2
    (295, 73.42, 175, 20, 30),   # 4:55 D2 hasta final
]
for t, freq, dur, fi, fo in bass_notes:
    bass.add(t, drone_event([freq], dur, fi=fi, fo=fo, amp=0.25, n_voices=2))   # amp 0.5→0.25
bass.fx(lambda a: lpf(a, 220))
# Ducking multi-zona:
# 1. Drop a 1:44 (entrada voy_r) — bajar al 40% para que voy_r entre limpio
# 2. Bajar al 15% en 3:30-5:25 (sub + voices_preview + voyager_counter_2)
# 3. Durante voices_l/r (5:17-7:01): rampa progresiva 0.20 → 1.0
bass.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (100, 1.0), (104, 0.4), (118, 0.4), (125, 1.0),   # drop 1:44-1:58 voy_r
    (200, 1.0), (210, 0.15), (325, 0.15),
    (335, 0.20), (380, 0.50), (420, 1.0), (480, 1.0),
]))
bass.fx(lambda a: reverb(a, decay=4.5, mix=0.4))


# ============================================================================
# DRONE SHIMMER — capa aguda que da movimiento timbral
# ============================================================================

# 14. DRONE SHIMMER
shimmer = comp.add_track(Track('drone_shimmer', gain=0.22, pan=+0.2, color='#a8b0d8'))   # 0.22→0.11 (user x0.5)
# SACADO shimmer pre-voyager — el user no lo quiere antes del 1:30
# shimmer.add(85, drone_event([587.33, 698.46], 7, fi=5, fo=2))
# SACADO shimmer t=150 (2:30) — el voyager_swell ya hace "ola" en esa zona,
# no sumamos capa. Da mas espacio para volar al que escucha.
# shimmer.add(150, drone_event([293.66, 349.23, 440.00], 65, fi=15, fo=15))
shimmer.add(220, drone_event([523.25, 698.46], 43, fi=15, fo=11))             # C5+F5, dur 70→43, fo termina 4:23 (no jode con voices_preview peak)
shimmer.add(295, drone_event([587.33, 698.46], 110, fi=20, fo=25))            # D5+F5
# Cuando entra el voyager (1:30), bajamos shimmer a la mitad para que no joda.
# Sin amp_envelope inverso (la primer instancia 1:20-1:30 ya termina antes del voyager,
# las siguientes (150, 220, 295) tienen sus propios fades — no se solapan)
# Bajada y subida del shimmer entre 4:46 (286) y 5:20 (320) — el de 4:55-6:45
# pasa por silencio durante voy_counter_2 evento 2 (5:10-5:25)
shimmer.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (286, 1.0), (300, 0.0), (310, 0.0), (320, 1.0), (480, 1.0),
]))
shimmer.fx(lambda a: reverb(a, decay=5.0, mix=0.50))   # Lustmord less wet


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
# Anti-density 1:20-1:35 (voyager corrido a 1:20): bajar granular al 50%
granular.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (78, 1.0), (80, 0.5), (95, 0.5), (100, 1.0), (480, 1.0),
]))
granular.fx(lambda a: reverb(a, decay=3.5, mix=0.55))


# ============================================================================
# SUB PULSES — pulso lento intermitente. Solo durante latido (1:00-1:25)
# y despues sparse durante in-pace (3:50-4:25)
# ============================================================================

# 16. SUB PULSES
sub_pulses = comp.add_track(Track('sub_pulses', gain=0.50, color='#5c4a3c'))
# SACADOS sub_pulses 62 (1:02) y 78 (1:18) — el de 1:18 era el "kick de bombo
# de mas" antes de la entrada del voyager. Mantengo solo los del in-pace (3:50-4:25).
for t in [230, 250, 265]:
    sub_pulses.add(t, kick(amp=0.5, dur=1.2, f0=65, fe=65, attack_ms=8, release_ms=250, pitch_sweep=False))   # sine pura (anti-fritura)
sub_pulses.fx(lambda a: lpf(a, 220))
sub_pulses.fx(lambda a: reverb(a, decay=4.0, mix=0.3))


# ============================================================================
# VOYAGER FASE 1 (1:30-3:30) — JUEGA 2 MINUTOS yendo y viniendo entre L/R/C
# ============================================================================

# Tres tracks paneados distintos. Eventos repartidos.

# 17. VOYAGER LEFT (pan +0.4) — preset roach_octlow validado por user
voy_l = voyager_track(comp, 'voyager_left', preset='roach_octlow',
                       pan=+0.4, base_gain=0.55, color='#e6c34d',   # 0.55→0.33 (user x0.6 todos voyagers)
                       events=[(79.55, {'amp': 0.35, 'variation': 'main_tight'})],   # 1:19.55 (200ms antes de 1:19.75)
                       with_companion=False)

# 18. VOYAGER RIGHT (pan -0.4) — preset roach_octlow ascending
voy_r = voyager_track(comp, 'voyager_right', preset='roach_octlow',
                       pan=-0.4, base_gain=0.50, color='#c89b3a',   # 0.50→0.30 (user x0.6)
                       events=[(104, {'amp': 0.35, 'variation': 'ascending_tight'})],   # 1:44 (era 1:46) — 2s antes
                       with_companion=False)

# 19. VOYAGER CENTER — SACADO ENTERO (todos los add() comentados, era track vacio)
# Todos los voy_c.add() estaban comentados — el track quedaba vacio y el QA runtime
# lo flagueaba como inaudible.

# --- VOYAGER COMPANION (1:30 - 3:30) — sostiene la TENSION del dance ---

# VOYAGER SWELL — pad alto D5+A5 sostenido EN CRESCENDO durante todo el dance.
# Usa D y A (notas comunes a Dm, Bb, F → los 3 acordes del dance).
# Crescendo: 0.5 → 1.3x sobre 2 minutos. La tension crece hasta el in-pace.
voy_swell = comp.add_track(Track('voyager_swell', gain=0.192, pan=+0.3, color='#b0e0d0'))   # 0.192→0.1344 (user x0.7 densidad 02:24)
# Octava ABAJO (D4+A4 en vez de D5+A5): el swell ya no pisa el registro
# del motivo voyager — la armonia Dm se mantiene, pero en otro octave.
voy_swell.add(74.55, drone_event([293.66, 440.00], 120, fi=12, fo=15, amp=0.45, n_voices=3))   # 5s antes del voyager_left (1:19.55) — pre 1:14.55
voy_swell.fx(lambda a: amp_envelope(a, [
    (0, 0.5),
    (75, 0.5),      # 1:15 - inicio
    (80, 0.25),     # 1:20 — BAJAR al entrar voyager
    (95, 0.25),     # 1:35
    (105, 0.5),    # 1:45 — recupera
    (135, 0.7),    # 2:15
    (150, 0.7),    # 2:30
    (170, 0.5),    # 2:50
    (185, 0.8),    # 3:05 sube (patron onda)
    (190, 0.9),    # 3:10 culmen
    (195, 0.6),    # 3:15 baja pero NO a 0 — el fade out fo=15 del evento se hace cargo
    (480, 0.0),
]))
voy_swell.fx(lambda a: reverb(a, decay=6.0, mix=0.65))

# VOYAGER COMPANION PINGS — bells armonizados con cada seccion del dance
# Llenan gaps cada 12-18s entre los eventos voyager principales
voy_pings = comp.add_track(Track('voyager_pings', gain=0.55, pan=-0.3, color='#d8e0a0'))   # 0.55→0.33 (user x0.6)
# (sacamos el bell A5 de 1:48 — "sobraba" justo despues del fragment voyager_center)
# Voyager_pings — primer ping a 1:35 (entre voy_l 1:33 y voy_r 1:46)
voy_pings.add(93,  bell(587.33, dur=4, amp=0.50, decay_rate=2.5))   # 1:33 D5 — primer ping (era 1:32)
# SACADO ping 1:48 F5 — jodia con voyager_right (1:46)
# voy_pings.add(108, bell(698.46, dur=5, amp=0.50, decay_rate=2.2))
voy_pings.add(121, bell(587.33, dur=6, amp=0.55, decay_rate=2.0))   # 2:01 D5 (era 2:03)
voy_pings.add(140, bell(587.33, dur=5, amp=0.45, decay_rate=2.5))   # 2:20 D5 (era F5 — sonaba raro en el contexto)
voy_pings.add(152, bell(587.33, dur=5, amp=0.45, decay_rate=2.5))   # 2:32 D5
voy_pings.add(165, bell(880.00, dur=6, amp=0.50, decay_rate=2.2))   # 2:45 A5
voy_pings.add(197, bell(698.46, dur=4, amp=0.45, decay_rate=2.8))   # 3:17 F5 (era 3:25)
voy_pings.add(201, bell(587.33, dur=5, amp=0.40, decay_rate=2.5))   # 3:21 D5
voy_pings.add(287, bell(880.00, dur=5, amp=0.45, decay_rate=2.3))   # 4:47 A5 (drone_Am activo)
# SACADO ping A5 178 (2:58): se sumaba a la pelota — voyager_left + drone_bb +
# drone_F + bassline + granular + shimmer + swell. Demasiada densidad ahi.
# voy_pings.add(178, bell(880.00, dur=6, amp=0.60, decay_rate=1.8))
# SACADO ping C5 195 (3:15): coincidia exacto con voyager_right ascending
# entrando — la nota atras que se entremezclaba a 3:18.
# voy_pings.add(195, bell(523.25, dur=6, amp=0.55, decay_rate=2.0))
voy_pings.fx(lambda a: lpf(a, 1800))                          # corta armonicos altos del bell (sweet spot validado en fragment)
voy_pings.fx(lambda a: reverb(a, decay=5.5, mix=0.65))


# 20. VOYAGER ECHO — "voyager que vuelve distinto". LPF + reverb largo + lejos.
# Aparece en gaps para que no se pierda el hilo del tema.
voy_echo = comp.add_track(Track('voyager_echo', gain=0.20, pan=-0.5, color='#8a7030'))   # 0.20→0.12 (user x0.6)
# SACADO voy_echo a 1:38 — se mezclaba con voy_pings (1:42) + voy_r (1:45) = quilombo a 1:40
# voy_echo.add(98, voyager(amp=0.32))
# SACADOS post-2:08: el motivo se repetia mucho.
# voy_echo.add(199, voyager(amp=0.30, variation='ascending'))       # 3:19
# voy_echo.add(220, voyager(amp=0.30, subset=VOYAGER_NOTES[2:5]))   # 3:40 in-pace
voy_echo.add(172, voyager(amp=0.32, subset=VOYAGER_NOTES[:4]))      # 2:52 (era 3:00)
# SACADO voy_echo 4:44 — el user lo pidio sacar
# voy_echo.add(284, voyager(amp=0.30, subset=VOYAGER_NOTES[:4]))
voy_echo.add(340, voyager(amp=0.34))                                # 5:40
voy_echo.add(410, voyager(amp=0.192, subset=VOYAGER_INVERTED[:4]))   # 6:50 — amp 0.32→0.192 (user x0.6)
# LPF bajado 1800 → 900 (filtra C6=1046 del ascending: el echo del C6 queda
# velado/lejano, no compite con el voyager_right limpio).
voy_echo.fx(lambda a: lpf(a, 900))
voy_echo.fx(lambda a: reverb(a, decay=6.0, mix=0.7))


# ============================================================================
# IN-PACE (3:30-4:30) — voyager se va, calma. voices_preview entra.
# ============================================================================

# 21. VOICES preview — entra a 4:00 con fade largo (boosted, era inaudible)
# Fade aplicado al evento (no al track) — sino el fade no afecta porque el track
# es zeros hasta 4:00.
voices_preview = comp.add_track(Track('voices_preview', gain=0.55, color='#a89090'))   # 0.55→0.33 (user x0.6)
voices_preview.add(240, fade(voice_pad(293.66, 75, vibrato_rate=4.0, amp=0.42), fi=20, fo=15))
# Desaparecer (0.0) durante voyager_counter_2 (4:30-5:25), fade in 4:36→4:42 inverso
voices_preview.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (264, 1.0), (268, 0.4), (272, 0.0), (320, 0.0), (335, 1.0), (480, 1.0),
]))   # user: voices se pegaba con voy_counter en 4:33 — fade-out anticipado 268-272
voices_preview.fx(lambda a: reverb(a, decay=5.0, mix=0.55))


# ============================================================================
# VOYAGER FASE 2 (4:30-5:30) — VUELVE con OTRO PATRON
# Counter-voice (5ta arriba) + staccato + notas invertidas. NO el patron clasico.
# ============================================================================

# 22. VOYAGER COUNTER — la 5ta arriba protagonista, paneada izquierda
# preset roach_octlow con variation 'counter'
voy_counter = voyager_track(comp, 'voyager_counter_2', preset='roach_octlow',
                              pan=-0.5, base_gain=0.45, color='#d8a830',   # 0.45→0.27 (user x0.6)
                              events=[
                                  (270, {'amp': 0.35, 'variation': 'counter'}),
                                  (295, {'amp': 0.32, 'subset': COUNTER_NOTES[0:5]}),   # 4:55 (era 5:03)
                              ],
                              with_companion=False)

# ============================================================================
# VOYAGER RECALL (2:08 - 3:30) — bells tapados como "llamados" lejanos
# Reemplaza las multiples tocas del motivo en 2:08-3:30 que sonaban repetitivas.
# Notas del motivo (D5, F5, A5, D5) en bell con LPF agresivo + reverb gigante:
# memoria/llamado distante en lugar de melodia. Pan distintos para variedad.
# ============================================================================

# SACADO voyager_recall ENTERO — gain=0.0, no aporta nada


# WIND WAVE (2:20 - 3:20) — onda base de viento (sube y baja).
wind_wave = comp.add_track(Track('wind_wave_2_3', gain=0.30, pan=-0.2, color='#5a8a9a'))
wind_wave.add(140, fade(lpf(noise(60, 1.0), 500), fi=2.5, fo=3))   # fade al evento — anti-TIC entrada (mismo fix que wind_echo)
wind_wave.fx(lambda a: lfo_amp(a, rate_hz=0.15, depth=0.55, offset=0.5))
wind_wave.fx(lambda a: fade(a, fi=8, fo=12))
# Bajar wind_wave durante voy_echo (2:52-3:04) — para que se escuche el echo
wind_wave.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (170, 1.0), (172, 0.2), (185, 0.2), (190, 1.0), (480, 1.0),
]))
wind_wave.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# WIND TURBULENT (2:50 - 3:30) — viento DINAMICO con vibracion ("nave temblando").
# Doble LFO: uno rapido (6 Hz) para tremor/vibracion + uno lento (0.15 Hz)
# para sube/baja. amp_envelope con valles y picos asimetricos.
wind_turb = comp.add_track(Track('wind_turbulent', gain=0.35, pan=+0.3, color='#7a8aa0'))
wind_turb.add(188, fade(lpf(noise(40, 1.0), 800), fi=2.5, fo=3))   # fade al evento — anti-fritura entrada (mismo fix que wind_echo/wind_wave)
wind_turb.fx(lambda a: lfo_amp(a, rate_hz=6.0, depth=0.18, offset=1.0))   # vibracion rapida (tremor)
wind_turb.fx(lambda a: lfo_amp(a, rate_hz=0.15, depth=0.5, offset=0.5))    # sube/baja lento
wind_turb.fx(lambda a: amp_envelope(a, [
    (0, 0.0),
    (170, 0.0),
    (180, 0.7),    # 3:00 — primer peak
    (190, 0.3),    # 3:10 — valle
    (200, 0.9),    # 3:20 — segundo peak (mas alto)
    (208, 0.2),    # 3:28 — baja
    (210, 0.0),    # 3:30 — corte
]))
wind_turb.fx(lambda a: reverb(a, decay=6.0, mix=0.55, pre_delay_ms=50))

# WIND ECHO (3:05 - 3:25) — eco retardado del viento, reverb gigante con
# pre-delay grande = sensacion de "rebote distante".
wind_echo = comp.add_track(Track('wind_echo', gain=0.20, pan=-0.4, color='#5a7a8a'))
# SACADO wind_echo — se mezclaba con wind_wave + wind_turbulent en 3:05-3:25 = 3 capas de viento
# wind_echo.add(185, fade(lpf(noise(20, 1.0), 800), fi=2.5, fo=3))
wind_echo.fx(lambda a: lfo_amp(a, rate_hz=0.2, depth=0.6, offset=0.4))
wind_echo.fx(lambda a: fade(a, fi=4, fo=4))
wind_echo.fx(lambda a: reverb(a, decay=8.0, mix=0.55, pre_delay_ms=120))   # 0.7→0.55


# VOYAGER INVERTED — notas en otro orden, paneada C
# SACADO voyager_inverted ENTERO — todos los add() comentados, track vacio


# ============================================================================
# VOICES FULL (5:00-7:00) — humano que despierta
# ============================================================================

# 25. VOICES L (D4 -> Eb4 -> D4)
# Fade in/out aplicado a CADA evento (no al track, porque el track empieza en
# 0:00 con zeros y el fade de track no afecta los eventos posteriores).
# Ultimo evento ACORTADO de 50s a 28s (terminaba a 7:23, muy largo).
voices_l = comp.add_track(Track('voices_l_d4', gain=0.36, pan=-0.5, color='#c87a8c'))   # 0.36→0.216 (user x0.6)
voices_l.add(300, fade(voice_pad(293.66, 50, vibrato_rate=4.0, amp=0.45), fi=10, fo=8))  # 5:00 D4
voices_l.add(348, fade(voice_pad(311.13, 45, vibrato_rate=3.8, amp=0.45), fi=8, fo=6))   # 5:48 Eb4
voices_l.add(393, fade(voice_pad(293.66, 28, vibrato_rate=4.2, amp=0.45), fi=8, fo=10))  # 6:33 D4
# Silenciar hasta 5:17, fade in mas largo hasta 5:27 (10s) — entrada gradual
voices_l.fx(lambda a: amp_envelope(a, [(0, 0), (317, 0), (327, 1.0), (480, 1.0)]))
voices_l.fx(lambda a: reverb(a, decay=4.5, mix=0.55))

# 26. VOICES R (A4 -> Bb4 -> A4)
voices_r = comp.add_track(Track('voices_r_a4', gain=0.36, pan=+0.5, color='#c87a8c'))   # 0.36→0.216 (user x0.6)
voices_r.add(300, fade(voice_pad(440.00, 50, vibrato_rate=4.5, amp=0.45), fi=10, fo=8))  # 5:00 A4
voices_r.add(348, fade(voice_pad(466.16, 45, vibrato_rate=4.3, amp=0.45), fi=8, fo=6))   # 5:48 Bb4
voices_r.add(393, fade(voice_pad(440.00, 28, vibrato_rate=4.7, amp=0.45), fi=8, fo=10))  # 6:33 A4
# Silenciar hasta 5:17, fade in 10s hasta 5:27 (igual que voices_l)
voices_r.fx(lambda a: amp_envelope(a, [(0, 0), (317, 0), (327, 1.0), (480, 1.0)]))
voices_r.fx(lambda a: reverb(a, decay=4.5, mix=0.55))


# ============================================================================
# VOYAGER FASE 3 (6:30-7:00) — DEGRADED. Climax foreshadow.
# ============================================================================

# 27. VOYAGER DEGRADED — distort + lpf + radio_interference (T13).
# Mas vestigio que en v5: el voyager degraded ahora suena como una
# transmision deformada por interferencia cosmica.
def voyager_deg(notes_subset=None):
    # Octava abajo + waveform triangle (sonido validado Tool, no aturde)
    if notes_subset is None:
        raw = voyager(amp=0.5, octave_shift=-1)
    else:
        low_notes = [(f / 2, d) for f, d in notes_subset]
        raw = voyager(amp=0.5, subset=low_notes)
    raw = distort(lpf(raw, 1500), amount=2.5)
    raw = radio_interference(raw, noise_amount=0.10, lpf_cutoff=1300, saturation=1.3)
    return fade(raw, fi=2, fo=3)

voyager_alien = comp.add_track(Track('voyager_degraded', gain=0.18, pan=-0.3, color='#a04030'))   # 0.18→0.108 (user x0.6)
voyager_alien.add(360, voyager_deg())
voyager_alien.add(390, voyager_deg(VOYAGER_NOTES[2:6]))
voyager_alien.add(415, voyager_deg(VOYAGER_INVERTED))
# Bajar el primer evento (6:00) al 50% — quemaba la cabeza con voices
voyager_alien.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (358, 1.0), (360, 0.5), (372, 0.5), (375, 1.0), (480, 1.0),
]))
voyager_alien.fx(lambda a: reverb(a, decay=6.0, mix=0.55))


# ============================================================================
# GLUE PUNTUAL — bells, whooshes, reverse_swells, downlifters, risers
# ============================================================================

# 28. BELL MARKERS — campanas armonizadas con cada seccion
bells = comp.add_track(Track('bell_markers', gain=0.34, color='#d8c060'))
# SACADO bell D5 a 1:00 — no se notaba con el ruido del heart_pulse activo
# bells.add(59.7, bell(587.33, dur=10, amp=0.5))
# SACADO bell F5 a 1:30 — entraba JUSTO con la entrada del voyager y tapaba la melodia.
# El voyager tiene su propia presencia en F5 a 1:31.5 (segunda nota del motif).
# bells.add(90,  bell(698.46, dur=10, amp=0.50))
# SACADO bell F5 a 2:00 — voyager_right (1:55 ascending) toca hasta 2:07,
# la bell F5 se sumaba innecesariamente al motivo.
# bells.add(120, bell(698.46, dur=12, amp=0.5))    # 2:00 F5
# SACADO bell D6 a 3:00 — bells del 2:15 en adelante fuera, salvo la de 2:20.
# bells.add(180, bell(1174.66, dur=10, amp=0.25))
bells.add(239.7, bell(875.00, dur=12, amp=0.35)) # 4:00 A5 desafinado -10 cents (880→875) para no batir con D4.h3=882 del voices_preview + amp 0.55→0.35 (user: 4:00 quilombo "bell sobre algo resonando")
# SACADO bell 4:30 A5 — user: se mezclaba con todo lo demas, no iba
# bells.add(270, bell(880.00, dur=12, amp=0.5))
bells.add(330, bell(698.46, dur=10, amp=0.25, decay_rate=1.8))   # 5:30 F5: amp 0.55→0.25 + decay rapido (queda mas sutil sin voyager_inverted que sacamos)
bells.add(359.7, bell(880.00, dur=16, amp=0.55)) # 6:00 A5 climax — anticipado -0.3s (entre beats heart climax)
bells.add(426, bell(587.33, dur=14, amp=0.55))   # 7:06 D5 closure (era 7:00)
bells.fx(lambda a: lpf(a, 2000))                 # 1500→2000 (Lustmord open)
bells.fx(lambda a: reverb(a, decay=6.5, mix=0.50))   # 0.65→0.50

# 29. WHOOSHES — pre-evento
whooshes = comp.add_track(Track('whooshes', gain=0.40, color='#90a0b0'))
# PRUEBA: sacado whoosh 27 (pre-latido) — si sin esto no hay fritura sec 27, era el whoosh.
# whooshes.add(27,  whoosh(dur=3, direction='up'))
whooshes.add(77,  fade(whoosh(dur=3.5, direction='up'), fi=0, fo=0.8))    # pre 1:20 voyager (movido 87→77 con la fase 1)
# SACADO whoosh 177 (pre 3:00): se acumulaba con reverse 176 + riser 175 +
# ping A5 178 + voyager_left + drones = pelota a 2:58. Ya queda el riser.
# whooshes.add(177, whoosh(dur=3, direction='up'))
whooshes.add(207, fade(whoosh(dur=3, direction='down', amp=0.30), fi=0.8, fo=0))   # 3:27 down — fade in 0.8s + amp 0.4→0.30 anti-fritura inicial
# SACADO whoosh 4:27 — user: se mezclaba con todo lo demas en 4:30
# whooshes.add(267, fade(whoosh(dur=4, direction='up'), fi=0, fo=1.5))
whooshes.add(287, fade(whoosh(dur=4, direction='up'), fi=0, fo=0.8))   # 4:47 (peak ~4:51)
whooshes.add(355, fade(whoosh(dur=5, direction='up'), fi=0, fo=0.8))
whooshes.add(417, fade(whoosh(dur=4, direction='down', amp=0.30), fi=0.8, fo=0))   # 7:00 down — mismo tratamiento
whooshes.fx(lambda a: reverb(a, decay=3.5, mix=0.55))

# 30. REVERSE SWELLS — antes de eventos importantes
reverse = comp.add_track(Track('reverse_swells', gain=0.50, color='#7a90c0'))
# SACADO reverse_swell 86 (pre 1:30) — convergia con whoosh+riser+swell justo
# en la entrada del voyager → "volumen bestial" + mini-fritura.
# El whoosh 87 + riser 85 alcanzan como cues sin saturar.
# reverse.add(86,  reverse_swell(dur=4, freq=147))
# SACADO reverse_swell 176 (pre 3:00): se acumulaba con whoosh + riser + ping
# = pelota a 2:58. Ya queda el riser como unico cue pre-3:00.
# reverse.add(176, reverse_swell(dur=4, freq=174))
reverse.add(266, fade(reverse_swell(dur=4, freq=110), fi=0, fo=1.5))    # pre 4:30 fase 2 — fade out conecta con voy_counter
# SACADO reverse_swell 4:50
# reverse.add(290, reverse_swell(dur=4, freq=147))
reverse.add(354, reverse_swell(dur=6, freq=110))    # pre 6:00 climax
reverse.fx(lambda a: reverb(a, decay=4.0, mix=0.50))   # Lustmord less wet

# 31. DOWNLIFTERS — landings post-evento
downs = comp.add_track(Track('downlifters', gain=0.32, color='#9090a0'))
downs.add(208, downlifter(dur=8, f_start=350, f_end=80))    # 3:28 entra in-pace (relax)
downs.add(420, downlifter(dur=8, f_start=400, f_end=42))    # 7:00 entra departure
downs.add(465, downlifter(dur=12, f_start=300, f_end=42))   # 7:45 dive final
downs.fx(lambda a: reverb(a, decay=3.5, mix=0.5))

# 32. RISERS — cues de eventos
risers_track = comp.add_track(Track('risers', gain=0.32, color='#909090'))
# SACADO riser 85 (peak en 1:30) — convergia con la entrada del voyager y molestaba.
# El whoosh 87 alcanza como cue. Sin riser ni reverse_swell ahi: voyager entra limpio.
# risers_track.add(85,  riser(dur=5))
# SACADO riser 175 (cue pre-3:00). Ya saque whoosh y reverse, este es el ultimo
# cue de esa marca — ya no hace falta, ademas se acumulaba en la pelota a 2:58.
# risers_track.add(175, riser(dur=4))
# SACADO riser 4:30 — el reverse_swell + whoosh ya hacen el cue pre-voyager_counter
# risers_track.add(270, riser(dur=4))
risers_track.add(288, fade(riser(dur=8), fi=0, fo=2.5))   # 4:48 (era 4:50, 2s antes)
# SACADO riser t=355 (5:55, peak ~5:59) — user pidio sacar
# risers_track.add(355, riser(dur=6))
risers_track.fx(lambda a: lpf(a, 2000))
risers_track.fx(lambda a: reverb(a, decay=3.0, mix=0.4))


# ============================================================================
# v6 — TRACKS NUEVOS aplicando tecnicas de Crossing/Recursion
# ============================================================================

# 33. PASSING OBJECTS L (1:30 - 3:30) — durante voyager dance, movement L→R
pass_l = comp.add_track(Track('passing_objects_L', gain=0.22, pan=-0.6, color='#90a0b0'))
for t in [95, 130, 165, 200]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=500, direction='up')   # cutoff 500 (sweet spot validado en fragment)
    pass_l.add(t, fade(w, fi=0, fo=2.0))
pass_l.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 34. PASSING OBJECTS R (par de la L, desfasada 0.4s)
pass_r = comp.add_track(Track('passing_objects_R', gain=0.22, pan=+0.6, color='#90a0b0'))
for t in [95, 130, 165, 200]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=500, direction='up')   # cutoff 500 (sweet spot validado en fragment)
    pass_r.add(t + 0.4, fade(w, fi=2.0, fo=0.5))   # fo 0→0.5 — whoosh up tiene peak al final, sin fo cortaba CLICK 1:38, 2:13, 2:48, 3:23
pass_r.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 35. CLIMAX GLITCHES (6:00 - 7:00) — Burial-style sutiles durante el peak
from aem.instruments import glitch_burst as _gb
climax_glitches = comp.add_track(Track('climax_glitches', gain=0.55, pan=+0.3, color='#5a3a4a'))
for t in [365, 372, 380, 388, 395, 405, 413, 420]:
    f = rng.choice([400, 800, 1200, 600, 1800])
    climax_glitches.add(t, _gb(dur=0.08 + rng.random() * 0.06,
                                freq_center=f, bandwidth=0.5, amp=0.55))
climax_glitches.fx(lambda a: reverb(a, decay=3.0, mix=0.5))

# 36. CLIMAX CLOSURE BELL — bell A5 que marca el cierre del peak (a 7:00)
climax_bell = comp.add_track(Track('climax_closure_bell', gain=0.32, color='#d8c060'))
climax_bell.add(420, bell(880.00, dur=15, amp=0.55, decay_rate=0.8))  # 7:00 A5 sostenido
climax_bell.fx(lambda a: lpf(a, 2000))                                # 1500→2000 (Lustmord open)
climax_bell.fx(lambda a: reverb(a, decay=8.0, mix=0.55))   # 0.7→0.55

# 37. DEPARTURE MELLOTRON — pad alto D5+A5 que entra a 7:00 con fade muy
# largo (40s) — luz tenue en la salida del tema. Tomado del Crossing.
mellotron_dep = comp.add_track(Track('departure_mellotron', gain=0.28, pan=+0.3, color='#b0a0d0'))   # 0.28→0.168 (user x0.6)
mellotron_dep.add(420, fade(voice_pad(587.33, 55, vibrato_rate=2.5, amp=0.40),
                             fi=30, fo=15))   # dur 60→55 (termina 7:55, deja 5s silencio al final)
mellotron_dep.add(420, fade(voice_pad(880.00, 55, vibrato_rate=2.8, amp=0.35),
                             fi=30, fo=15))
mellotron_dep.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (420, 0.0), (425, 0.10), (440, 0.40),
    (460, 0.80), (475, 1.0), (480, 1.0),
]))
mellotron_dep.fx(lambda a: lpf(a, 2000))                  # 1500→2000 (Lustmord open) — notch ya filtra A5/A6
mellotron_dep.fx(lambda a: reverb(a, decay=8.0, mix=0.55))   # 0.7→0.55


# ============================================================================
# ANTI-PLANCHE 2:00-3:00 — user reporto que la zona se plancha. Agregamos
# riser sutil 2:24 + bell 2:35 + cosmos swell 2:00-2:55.
# ============================================================================

# Riser sutil a 2:24
out_riser = comp.add_track(Track('outbound_riser_2_24', gain=0.20, color='#909090'))
out_riser.add(143.5, fade(riser(dur=5, f_start=80, f_end=400, amp=0.45),
                           fi=0.5, fo=1.5))
out_riser.fx(lambda a: lpf(a, 1200))
out_riser.fx(lambda a: reverb(a, decay=3.5, mix=0.45))

# Bell marker 2:35 SACADO — el voy_pings ya tiene D5 a 2:32 (152s), poner otro
# D5 a 2:35 (155s) genera la sensacion de "ping repetido" 3 seg despues.

# Cosmos breath swell 2:00-2:55 — capa atmosferica de fondo
out_swell_2_3 = comp.add_track(Track('outbound_swell_2_3', gain=0.15, pan=-0.15,
                                      color='#5a6a8a'))
out_swell_2_3.add(120, fade(lpf(noise(55, amp=0.7), 400), fi=8, fo=12))
out_swell_2_3.fx(lambda a: reverb(a, decay=4.0, mix=0.55, pre_delay_ms=60))


if __name__ == '__main__':
    from aem.auto_fixes import apply_auto_fixes
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    apply_auto_fixes(comp, verbose=True)
    comp.list_tracks()
    print()
    # SACADO dirty_intro — el user no quiere la fritura al inicio (era el sonido
    # de "interferencia/estatica de cable de guitarra").
    master_fx = None
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'), master_fx=master_fx)
    comp.export_stems(os.path.join(OUT, 'stems', NAME), master_fx=master_fx)
