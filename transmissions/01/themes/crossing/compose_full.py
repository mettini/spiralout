"""Crossing — TEMA COMPLETO (13:00). El cruce. Centro del EP.

Storyboard:
  0:00 - 1:30   CONEXION         sub42 vuelve, vestigio voyager, drone Dm
  1:30 - 3:30   DESCENSO         sub baja 32Hz, field bed, drone con clusters
  3:30 - 6:00   OSCURIDAD        chant Dune (D2->A2->F2), heart 40bpm, passing objects
  6:00 - 7:30   MOMIA SE PUDRE   wall_of_sound, glitches, chant degraded — peak oscuro
  7:30 - 9:30   LA BAJADA        downlifter, mellotron alto, magia ocasional
  9:30 - 11:00  DERIVA           pad sostenido, objetos, heart suave intermitente
  11:00 - 13:00 VESTIGIO + CIERRE voyager echoes muy distorsionados (ultimo 20%)
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRANSMISSION_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(TRANSMISSION_ROOT, '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem import Composition, Track, SR
from aem.synth import sine, noise
from aem.instruments import (
    detuned_drone, voice_pad, kick, melody, bell,
    granular_pulse, sub_rumble, chant_drone, whoosh,
    wall_of_sound, feedback_squeal, downlifter, riser,
    glitch_burst, reverse_swell,
)
from aem.effects import (
    fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp,
    tape_warm, radio_interference, notch_eq,
)

DURATION = 780  # 13:00
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'crossing')
NAME = 'crossing_FULL'

comp = Composition(DURATION, name='Crossing (full) - 13min')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

rng = np.random.default_rng(13)


def drone_event(notes, dur, fi=10, fo=15, amp=0.4, n_voices=3, detune_cents=10):
    return fade(detuned_drone(notes, dur, amp=amp,
                              n_voices=n_voices, detune_cents=detune_cents),
                fi=fi, fo=fo)


# ============================================================================
# CONEXION (0:00 - 1:30) — sub42 vuelve, vestigio voyager, drone Dm
# ============================================================================

# 01. SUB 42Hz CONEXION — vuelve del outbound, fade out a 1:30
sub_conex = comp.add_track(Track('sub_42_conexion', gain=0.18, color='#3a4a5c'))   # 0.18→0.108 (user x0.6)
sub_conex.add(0, sine(42, 100, 0.4))
sub_conex.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (5, 1.0), (60, 1.0), (100, 0.0),
]))

# 02. VOYAGER VESTIGIO inicial — radio interference + reverb muy largo
# Antes arrancaba/cortaba de golpe. Ahora con notas alargadas + fade muy
# largo + radio_interference (T13) = "llega de pedo entre la interferencia"
def vestige_event(notes_subset, amp=0.32, fade_io=8):
    # Triangle + release 0.6 (sonido validado Tool, no aturde la A5)
    raw = melody(notes_subset, amp=amp, vibrato=True, waveform='triangle',
                 release=0.6, release_curve=1.0)
    # Pattern B fix: noise_amount 0.25→0.10 (menos wash de interferencia)
    raw = radio_interference(raw, noise_amount=0.10, lpf_cutoff=1300,
                             saturation=1.4, seed=None)
    return fade(raw, fi=fade_io, fo=fade_io)

vest_init = comp.add_track(Track('voyager_vestige_intro', gain=0.078, pan=-0.5, color='#7a6030'))   # 0.13→0.078 (user x0.6)
vest_init.add(15, vestige_event(VOYAGER_NOTES[:5], amp=0.22, fade_io=4))
vest_init.add(55, vestige_event(VOYAGER_NOTES[2:5], amp=0.20, fade_io=3))
# Pattern B fix: reverb decay 9→6 + mix 0.80→0.55 (menos wash sostenido)
vest_init.fx(lambda a: reverb(a, decay=6.0, mix=0.55))


# ============================================================================
# COSMOS BED — viento de fondo siempre presente con LFO breathing
# ============================================================================

# 03. COSMOS bed (gain 0.10 → 0.12 — apenas para pasar QA activity threshold)
cosmos = comp.add_track(Track('cosmos', gain=0.06, color='#5a5a5a'))   # user x0.5 desde UI — se metia en todos lados   # 0.12→0.048 (user x0.4)
cosmos.add(0, hpf(lpf(noise(DURATION, 1.0), 500), 100))   # HPF 100 (era HPF 60 del auto_fixes) — user feedback 20:30 "muy bajo, octavas demasiado abajo"; corta sub-bass del cosmos
cosmos.fx(lambda a: lfo_amp(a, rate_hz=0.06, depth=0.5, offset=0.7))
cosmos.fx(lambda a: fade(a, fi=15, fo=30))
# Duck a 0.5x durante zona chants (215-415s) — user pidio bajar cosmos cuando hay chants
cosmos.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (200, 1.0), (215, 0.5), (415, 0.5), (430, 1.0), (DURATION, 1.0),
]))


# ============================================================================
# SUB-BASS layers — 42Hz hasta 1:30, despues 32Hz oscuro hasta 9:30
# ============================================================================

# 04. SUB RUMBLE 32Hz — la presencia oscura
sub_dark = comp.add_track(Track('sub_rumble_32', gain=0.05, color='#1a1a2c'))   # 0.40→0.30→0.05 (user pidio bajar 0.25)
sub_dark.add(80, fade(sub_rumble(freq=32, dur=600, mod_rate=0.07, mod_depth=0.5), fi=4, fo=8))   # fade al evento — anti-TIC entrada
sub_dark.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (80, 0.0), (110, 1.0), (200, 1.0),
    (215, 0.25), (415, 0.25),                        # duck a 0.25x durante chants (user)
    (430, 1.0), (570, 1.0), (650, 0.4), (780, 0.0),
]))


# ============================================================================
# DRONES armonicos con CLUSTERS DISONANTES (DESCENSO 1:30 - 3:30)
# ============================================================================

# 05. DRONE Dm + cluster Bb (disonancia leve) — 1:30 a 4:00
drone_dm_cluster = comp.add_track(Track('drone_dm_cluster', gain=0.32, color='#7a5cb8'))   # 0.45→0.32 (user feedback 11:25 quilombo, muchas cosas sonando)
drone_dm_cluster.add(90, drone_event([146.83, 174.61, 220.00, 233.08],
                                      170, fi=15, fo=25, amp=0.45))
drone_dm_cluster.fx(lambda a: lpf(a, 1800))   # 1300→1800 (Lustmord: abrir presence, sacar 'abajo del agua')
drone_dm_cluster.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 06. DRONE Bb (Bb-D-F) — disonancia mayor, 3:00 a 5:30
drone_bb = comp.add_track(Track('drone_bb_dark', gain=0.22, color='#9070a8'))   # 0.32→0.22 — user feedback 11:25 quilombo (intermedio entre restored 0.32 y cut 0.192)
drone_bb.add(180, drone_event([116.54, 146.83, 174.61], 150, fi=25, fo=25))
drone_bb.fx(lambda a: lpf(a, 1800))   # 1400→1800 (Lustmord open)
drone_bb.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 07. FIELD ATMOSPHERE — bed continuo (R8 compliant gain 0.13)
field = comp.add_track(Track('field_atmosphere', gain=0.13, color='#3a3a3a'))
field.add(60, fade(lpf(noise(680, 1.0), 400), fi=4, fo=5))   # fade al evento — anti-TIC entrada
field.fx(lambda a: lfo_amp(a, rate_hz=0.06, depth=0.6, offset=0.6))
field.fx(lambda a: fade(a, fi=20, fo=30))


# ============================================================================
# OSCURIDAD COSMICA (3:30 - 6:00) — Chant Dune + heart suave + passing objects
# ============================================================================

# 08. CHANT D2 (Sardaukar entrada) — 3:30 a 4:30
chant_d2 = comp.add_track(Track('chant_D2', gain=0.14, pan=-0.15, color='#5a3a4a'))   # 0.20→0.12 (user x0.6)
chant_d2.add(210, fade(chant_drone(freq=73.42, dur=60, vibrato_rate=1.6,
                                    vibrato_depth=0.007, amp=0.50,
                                    n_harmonics=8, formant_emphasis=(2, 4, 7),
                                    fundamental_boost=4.0),
                       fi=15, fo=25))   # fi 10→25→15 (user: 25 era mucho)
chant_d2.fx(lambda a: lpf(a, 2400))   # 1800→2400 (Lustmord open)
chant_d2.fx(lambda a: reverb(a, decay=7.0, mix=0.50))   # mix 0.65→0.50 (menos wet)

# 08b. CHANT GLUE D→A — 5ta sostenida (D2+A2 detuned) que conecta chant_D2 con chant_A2
# sin discontinuidad. Cubre 245-280s (recortado: user dijo que corria mucho overlap con A2).
# Pan central. Mismo lpf+reverb que los chants.
chant_glue_da = comp.add_track(Track('chant_glue_DA', gain=0.06, pan=0.0, color='#5a4050'))   # 0.12→0.072 (user x0.6)
chant_glue_da.add(245, fade(detuned_drone([73.42, 110.00], 30, amp=0.40,
                                            n_voices=3, detune_cents=8),
                             fi=12, fo=15))   # dur 55→30, fi 18→12, fo 18→15 (recortado, sale antes que A2 este full)
chant_glue_da.fx(lambda a: lpf(a, 2400))   # Lustmord open
chant_glue_da.fx(lambda a: reverb(a, decay=7.0, mix=0.50))


# 09. CHANT A2 — 4:20 a 5:20
chant_a2 = comp.add_track(Track('chant_A2', gain=0.092, pan=+0.20, color='#6a4a5a'))   # 0.132→0.0792 (user x0.6)
chant_a2.add(260, fade(chant_drone(freq=110.00, dur=60, vibrato_rate=1.8,
                                     vibrato_depth=0.007, amp=0.50,
                                     n_harmonics=8, formant_emphasis=(2, 5, 7),
                                     fundamental_boost=4.0),
                       fi=20, fo=25))   # vibrato_depth 0.013→0.007 + fundamental_boost 4.0
chant_a2.fx(lambda a: lpf(a, 2400))   # Lustmord open
chant_a2.fx(lambda a: reverb(a, decay=7.0, mix=0.50))

# 09b. CHANT GLUE A→F — F2 + A2 detuned, suaviza transicion chant_A2 → chant_F2.
# A2 fade-out arranca ~315, F2 peak ~325 → glue cubre 290-325 (rellena el bache).
# Pan central. Mismo lpf+reverb que los chants.
chant_glue_af = comp.add_track(Track('chant_glue_AF', gain=0.06, pan=+0.05, color='#7050a0'))   # 0.12→0.072 (user x0.6)
chant_glue_af.add(290, fade(detuned_drone([110.00, 87.31], 35, amp=0.40,
                                            n_voices=3, detune_cents=8),
                             fi=12, fo=15))
chant_glue_af.fx(lambda a: lpf(a, 2400))   # Lustmord open
chant_glue_af.fx(lambda a: reverb(a, decay=7.0, mix=0.50))


# 10. CHANT F2 — 5:10 a 6:10
chant_f2 = comp.add_track(Track('chant_F2', gain=0.042, pan=0, color='#8a5a6a'))   # 0.06→0.036 (user x0.6)
# Entrada adelantada 310→305 + fade-in 12→18s: el cambio A2→F2 a 13:13 del
# continuous se sentia abrupto. Ahora el F2 arranca antes y crece mas lento,
# se cruza 15s con la cola del A2 — uno decanta en el otro sin hueco ni choque.
chant_f2.add(295, fade(chant_drone(freq=87.31, dur=90, vibrato_rate=1.5,
                                     vibrato_depth=0.007, amp=0.50,
                                     n_harmonics=8, formant_emphasis=(2, 4, 6),
                                     fundamental_boost=4.0),
                       fi=30, fo=35))   # vibrato_depth 0.015→0.007 + fundamental_boost 4.0
chant_f2.fx(lambda a: lpf(a, 2400))   # Lustmord open
chant_f2.fx(lambda a: reverb(a, decay=7.0, mix=0.50))

# 11. HEART BEAT SUAVE 40 BPM — 3:45 a 6:00 (60 kicks)
# Reverb mas larga (decay 5→8) y mas wet (mix 0.55→0.70) — el cola del kick
# se sentia que cortaba abrupto
heart_soft = comp.add_track(Track('heart_soft_40bpm', gain=0.20, color='#7c4040'))   # 0.42→0.20 (mitad)
# kicks cada 2s (era 1.5) — menos overlap entre colas. dur 0.6 (era 1.2) — cola corta.
for i in range(45):
    t = 225 + i * 2.0
    if t > 360:
        break
    heart_soft.add(t, kick(amp=0.30, dur=0.6, f0=55, fe=55, attack_ms=8, release_ms=200, pitch_sweep=False))
heart_soft.fx(lambda a: lpf(a, 200))
heart_soft.fx(lambda a: reverb(a, decay=2.5, mix=0.20))   # decay 8→2.5 mix 0.7→0.20 (sin cola larga acumulada)

# 12. PASSING OBJECTS L — whooshes paneados durante OSCURIDAD
pass_l = comp.add_track(Track('passing_objects_L', gain=0.32, pan=-0.6, color='#90a0b0'))
for t in [225, 260, 295, 330, 360]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=600, direction='up')   # T_NOISE_FRITURA: 2500→600
    pass_l.add(t, fade(w, fi=0, fo=2.0))
pass_l.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 13. PASSING OBJECTS R
pass_r = comp.add_track(Track('passing_objects_R', gain=0.32, pan=+0.6, color='#90a0b0'))
for t in [225, 260, 295, 330, 360]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=600, direction='up')
    pass_r.add(t + 0.4, fade(w, fi=2.0, fo=0.5))   # fo 0→0.5 (whoosh up tiene peak al final, sin fade out cortaba abrupto = CLICK 12:23)
pass_r.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 14. RITUAL BELL en mitad de OSCURIDAD
ritual = comp.add_track(Track('ritual_bell', gain=0.28, color='#d8c060'))
ritual.add(280, fade(bell(220.00, dur=15, amp=0.40, decay_rate=1.0), fi=0.08, fo=2.0))  # fade al evento + amp bajado (TIC al ataque del bell)
ritual.fx(lambda a: reverb(a, decay=8.0, mix=0.55))   # 0.7→0.55 (Lustmord less wet)

# 14b. REVERSE SWELL pre-F2 — el chant_F2 entra a 5:10. Antes habia un
# "increcento que terminaba en nada". Ahora un reverse_swell que CULMINA
# justo cuando entra el F2.
swell_pre_f2 = comp.add_track(Track('reverse_swell_pre_F2', gain=0.35, pan=+0.1, color='#7a90c0'))   # 0.65→0.35 (saturaba a 13:09)
from aem.instruments import reverse_swell
swell_pre_f2.add(304, fade(reverse_swell(dur=6, freq=220, amp=0.50), fi=0.5, fo=2.0))  # amp 0.70→0.50 + fo 0.5→2.0
swell_pre_f2.fx(lambda a: reverb(a, decay=5.0, mix=0.50))   # 0.6→0.50

# 14c. DRONE DISONANTE TENSION — capa adicional durante OSCURIDAD para
# mas caos. F + Bb (tritono respecto al D del bed) genera tension.
# Pattern C fix: saco C# (277.18) — eliminaba el tritono F-B disonante.
# Ahora F+Bb = 4ta perfecta, mucho mas limpio. + gain 0.30→0.22, distort 1.5→1.2
tension_pad = comp.add_track(Track('tension_pad', gain=0.14, pan=-0.3, color='#7a4060'))   # 0.14→0.084 (user x0.6)
tension_pad.add(220, fade(detuned_drone([174.61, 233.08], 150, amp=0.30,
                                          n_voices=3, detune_cents=15),
                           fi=15, fo=20))   # amp 0.40→0.30
tension_pad.fx(lambda a: lpf(a, 1800))   # Lustmord open
tension_pad.fx(lambda a: distort(a, amount=0.6))   # 1.2→0.6 (menos saturacion)
tension_pad.fx(lambda a: reverb(a, decay=6.5, mix=0.55))
# Boost a 2.0x durante chant_F2 (295-385) — user pidio mas tension cuando suena ese chant
tension_pad.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (290, 1.0), (300, 2.0), (380, 2.0), (390, 1.0), (DURATION, 1.0),
]))

# 14d. GLITCHES SUTILES durante OSCURIDAD — no solo en momia
oscuridad_glitches = comp.add_track(Track('oscuridad_glitches', gain=0.60, pan=+0.4, color='#5a4a4a'))
for t in [232, 248, 268, 290, 315, 335, 348]:
    f = rng.choice([300, 600, 900, 1200, 1500])
    oscuridad_glitches.add(t, glitch_burst(dur=0.08 + rng.random() * 0.08,
                                            freq_center=f, bandwidth=0.5, amp=0.60))
oscuridad_glitches.fx(lambda a: reverb(a, decay=3.5, mix=0.55))

# 14e. POST-F2 BRIDGE — el chant_F2 termina con fade a ~6:10. Para que la
# transicion al wall (6:00) no se sienta como hueco, agrego un sostenido
# disonante que cubre 5:50-6:15 (overlap con chant_F2 y entrada al wall).
post_f2_bridge = comp.add_track(Track('post_f2_bridge', gain=0.22, pan=0, color='#5a3060'))   # 0.32→0.22 (distort generaba fritura a 14:03)
post_f2_bridge.add(350, fade(detuned_drone([110.00, 138.59, 233.08], 30, amp=0.38,
                                             n_voices=4, detune_cents=20),
                              fi=10, fo=12))
post_f2_bridge.fx(lambda a: distort(a, amount=1.7))
post_f2_bridge.fx(lambda a: reverb(a, decay=5.5, mix=0.50))   # 0.6→0.50


# ============================================================================
# MOMIA SE PUDRE (6:00 - 7:30) — peak oscuro: wall + glitches + chant degraded
# ============================================================================

# 15. WALL OF SOUND — 6:00 a 7:30. Bajado fuerte 0.55→0.30 + distortion 4.0→2.5
# + n_layers 4→3 para reducir beating/vibration entre detunes
wall = comp.add_track(Track('wall_of_sound_climax', gain=0.06, color='#1a0a14'))   # 0.10→0.06 (pitido 14:25)
wall.add(360, wall_of_sound(root_freqs=[55.00, 73.42], dur=90,
                             distortion=1.5, n_layers=2, amp=0.40))
wall.fx(lambda a: amp_envelope(a, [
    (0, 0.0),
    (360, 0.0),     # arranca silencioso
    (380, 0.6),     # crece (6:20)
    (405, 1.0),     # peak (6:45)
    (430, 1.0),     # sostiene (7:10)
    (445, 0.5),     # baja (7:25)
    (450, 0.0),     # corte (7:30)
]))
wall.fx(lambda a: lpf(a, 2000))   # Lustmord open
wall.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 16. SUB PUNISHER 28Hz — bajado 0.38→0.20→0.13 (sumaba SPL al wall del 6:00-7:30)
sub_punish = comp.add_track(Track('sub_punisher_climax', gain=0.13, color='#2a0a14'))
sub_punish.add(360, sub_rumble(freq=28, dur=90, mod_rate=0.15, mod_depth=0.5))
sub_punish.fx(lambda a: distort(a, amount=1.0))
sub_punish.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (360, 0.0), (380, 0.8), (445, 1.0), (450, 0.0),
]))

# 17. FEEDBACK SQUEAL — bajado 0.22→0.14 (la nota alta agregaba vibración)
fb = comp.add_track(Track('feedback_squeal', gain=0.05, pan=+0.3, color='#5a3030'))   # 0.10→0.05 (user: friturita en 6:25)
fb.add(385, fade(feedback_squeal(freq=1480, dur=55, sweep_depth=0.025, sweep_rate=0.4,
                                  amp=0.45, decay_rate=0.10), fi=0.8, fo=2))   # fade in 0.8s — user feedback friturita a 14:25 (= 6:25 crossing), arranque sin fade del feedback_squeal
fb.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 18. GLITCH BURSTS — esparcidos durante el peak (Burial-style sobre el wall)
glitches = comp.add_track(Track('glitch_bursts_climax', gain=0.42, pan=-0.2, color='#5a3a4a'))
glitch_times = [365, 372, 380, 388, 395, 405, 413, 420, 428, 435, 443]
for t in glitch_times:
    f = rng.choice([400, 800, 1200, 2400, 600, 1800])
    glitches.add(t, glitch_burst(dur=0.10 + rng.random() * 0.08,
                                  freq_center=f, bandwidth=0.4, amp=0.70))
glitches.fx(lambda a: reverb(a, decay=2.5, mix=0.4))

# 19. CHANT DEGRADED — el canto se distorsiona en el peak
def chant_deg():
    raw = chant_drone(freq=73.42, dur=40, vibrato_rate=1.6, amp=0.5,
                      n_harmonics=8, formant_emphasis=(2, 4, 7))
    return distort(lpf(raw, 1500), amount=2.5)

chant_degraded = comp.add_track(Track('chant_degraded', gain=0.048, pan=-0.3, color='#a04030'))   # 0.08→0.048 (user x0.6)
chant_degraded.add(390, fade(chant_deg(), fi=10, fo=15))
chant_degraded.fx(lambda a: reverb(a, decay=5.5, mix=0.50))   # 0.65→0.50

# 20. RISER pre-momia (anuncia el peak)
riser_pre = comp.add_track(Track('riser_pre_momia', gain=0.40, color='#909090'))   # 0.40→0.24 (user x0.6)
riser_pre.add(355, fade(riser(dur=5, f_start=80, f_end=600, amp=0.55), fi=0, fo=1.5))   # fo 0.6→1.5 — user feedback mini TIC a 13:59 (= 5:59 crossing, final del riser)
riser_pre.fx(lambda a: lpf(a, 2000))
riser_pre.fx(lambda a: reverb(a, decay=3.0, mix=0.4))


# ============================================================================
# LA BAJADA (7:30 - 9:30) — downlifter, mellotron alto, magia ocasional
# ============================================================================

# 21. DOWNLIFTER post-peak — 7:30 (release del peak)
down1 = comp.add_track(Track('downlifter_release', gain=0.27, color='#7a5050'))   # 0.45→0.27 (user x0.6)
down1.add(450, fade(downlifter(dur=15, f_start=400, f_end=80, amp=0.6), fi=0.5, fo=0))   # fade in 0.5s — downlifter tiene peak al INICIO = TIC sin fade
down1.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 22. MELLOTRON PAD ALTO (D5+A5) — luz tenue. Fade in MUY LARGO y suave
# (40s) — empieza casi imperceptible y va creciendo de a poquito.
mellotron = comp.add_track(Track('mellotron_pad', gain=0.10, pan=+0.3, color='#b0a0d0'))
mellotron.add(450, fade(voice_pad(587.33, 130, vibrato_rate=2.5, amp=0.40),
                         fi=40, fo=20))
mellotron.add(450, fade(voice_pad(880.00, 130, vibrato_rate=2.8, amp=0.30),
                         fi=40, fo=20))
# amp_envelope adicional para curva exponencial (no lineal) en el fade in
mellotron.fx(lambda a: amp_envelope(a, [
    (0, 1.0), (450, 0.0), (455, 0.10), (470, 0.30),
    (485, 0.55), (500, 0.85), (520, 1.0), (780, 1.0),
]))
# Standard Tool: notch -12 dB en A5 (880 Hz) + 2do harm (1760) — el A5 sostenido
# del mellotron es lo que "pitaba" en minuto 16 del continuous.
mellotron.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
mellotron.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
mellotron.fx(lambda a: lpf(a, 2000))                  # 1500→2000 (Lustmord open) — notch -12 ya filtra A5/A6
mellotron.fx(lambda a: reverb(a, decay=8.0, mix=0.55))   # 0.7→0.55

# 23. DRONE Dm LIMPIO emerge — 7:35
# Standard Tool: triangle waveform + notch -12 en armonicos altos del A4 sostenido.
drone_clean = comp.add_track(Track('drone_dm_clean', gain=0.28, color='#7a5cb8'))
# SACADO A3 (220 Hz): su 4to armonico = A5 (880 Hz, zona Fletcher-Munson)
# era lo que aturdia. Drone queda D3-F3 (Dm sin quinta, mas abierto/misterioso).
drone_clean.add(455, fade(detuned_drone([146.83, 174.61], 200, amp=0.45,
                                          waveform='triangle'),
                          fi=15, fo=30))
drone_clean.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
drone_clean.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
drone_clean.fx(lambda a: reverb(a, decay=5.5, mix=0.55))

# 24. MAGIC PINGS — bells altos esparcidos durante BAJADA y DERIVA
# Bajado gain 0.46 → 0.25 + amps de bells reducidos (las freqs 1320/1760/2093
# caen en plena zona Fletcher-Munson y aturdían sumadas al mellotron A5).
magic = comp.add_track(Track('magic_pings', gain=0.375, pan=+0.3, color='#c0e0d0'))   # 0.15→0.375 (user x2.5) — REVERTIDO al backup, suena bien con reverb sin clamp
# Fix tonal v2: matcheamos outbound (D5/F5/A5 octava 5) — antes estaban en oct 6/7
# = "campanitas otra dimension". Ahora encajan con mellotron_pad D5+A5 + drone_dm_clean.
magic.add(470, bell(587.33,  dur=4, amp=0.45, decay_rate=2.5))   # D5 (igual outbound intro_pings)
magic.add(490, bell(880.00,  dur=4, amp=0.40, decay_rate=2.8))   # A5
magic.add(515, bell(698.46,  dur=5, amp=0.45, decay_rate=2.3))   # F5
magic.add(545, bell(587.33, dur=4, amp=0.40, decay_rate=3.0))   # D5 (era D6=1174.66 — user 17:05 "bajalo a la octava correcta")
magic.add(575, bell(880.00,  dur=5, amp=0.45, decay_rate=2.5))   # A5
magic.add(605, bell(698.46,  dur=4, amp=0.40, decay_rate=3.0))   # F5
# (SACADO magic ping 20:30 — colisionaba con closure_bell A4 que ataca a 750s = 2 notas superpuestas)
magic.fx(lambda a: lpf(a, 2000))                       # 1500→2000 (Lustmord open)
magic.fx(lambda a: reverb(a, decay=5.5, mix=0.50))    # 0.65→0.50


# ============================================================================
# DERIVA (9:30 - 11:00) — pad sostenido, objetos, heart suave intermitente
# ============================================================================

# 25. PASSING OBJECTS L (segundo set, durante deriva)
pass_l_2 = comp.add_track(Track('passing_objects_L_2', gain=0.30, pan=-0.6, color='#7090a0'))
for t in [575, 615, 650]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=600, direction='up')   # T_NOISE_FRITURA: 2500→600
    pass_l_2.add(t, fade(w, fi=0, fo=2.0))
pass_l_2.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 26. PASSING OBJECTS R
pass_r_2 = comp.add_track(Track('passing_objects_R_2', gain=0.30, pan=+0.6, color='#7090a0'))
for t in [575, 615, 650]:
    w = whoosh(dur=2.5, cutoff_start=300, cutoff_end=600, direction='up')   # T_NOISE_FRITURA: 2500→600
    pass_r_2.add(t + 0.4, fade(w, fi=2.0, fo=0.5))   # fo 0→0.5 — anti-CLICK whoosh up
pass_r_2.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 27. HEART SUAVE intermitente durante DERIVA
heart_drift = comp.add_track(Track('heart_drift', gain=0.38, color='#5c4040'))
for t in [580, 600, 620, 645, 660]:
    heart_drift.add(t, kick(amp=0.40, dur=0.9, f0=55, fe=55, attack_ms=8, release_ms=200, pitch_sweep=False))   # sine pura, sin pitch_sweep (anti-fritura)
heart_drift.fx(lambda a: lpf(a, 200))
heart_drift.fx(lambda a: reverb(a, decay=5.5, mix=0.55))


# ============================================================================
# VESTIGIO + CIERRE (11:00 - 13:00) — voyager echoes muy distorsionados
# ============================================================================

# 28. VOYAGER ECHO distante — Pattern B fix: noise + reverb más contenidos
def voyager_distant(notes_subset, amp=0.30, fade_io=5):
    # Triangle + release 0.6 (sonido validado Tool)
    raw = melody(notes_subset, amp=amp, vibrato=True, waveform='triangle',
                 release=0.6, release_curve=1.0)
    raw = radio_interference(raw, noise_amount=0.10, lpf_cutoff=1300,
                             saturation=1.4)
    return fade(raw, fi=fade_io, fo=fade_io)

vest_final = comp.add_track(Track('voyager_vestige_final', gain=0.036, pan=-0.4, color='#a08030'))   # 0.06→0.036 (user x0.6)
vest_final.add(655, voyager_distant(VOYAGER_NOTES, amp=0.32, fade_io=4))
vest_final.add(695, voyager_distant(VOYAGER_NOTES[2:5], amp=0.30, fade_io=3))
vest_final.add(738, voyager_distant(VOYAGER_NOTES[:3], amp=0.28, fade_io=2.0))   # amp bajado, fade_io 2.0 (audio dura ~4.5s)
vest_final.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 29. VOYAGER DEGRADED final — Pattern B fix: noise + reverb mas contenidos
def voyager_deg():
    low = [(f / 2, d) for f, d in VOYAGER_NOTES]
    # Triangle + release 0.6 (sonido validado Tool)
    raw = melody(low, amp=0.5, vibrato=True, waveform='triangle',
                 release=0.6, release_curve=1.0)
    raw = distort(lpf(raw, 1500), amount=2.5)
    raw = radio_interference(raw, noise_amount=0.10, lpf_cutoff=1200, saturation=1.3)
    return fade(raw, fi=4, fo=6)

voy_alien_final = comp.add_track(Track('voyager_degraded_final', gain=0.024, pan=+0.3, color='#a04030'))   # 0.04→0.024 (user x0.6)
voy_alien_final.add(720, voyager_deg())
voy_alien_final.fx(lambda a: reverb(a, decay=6.0, mix=0.55))

# 30. DRONE Dm fade final
drone_fade = comp.add_track(Track('drone_dm_fade_final', gain=0.252, color='#5a4a8a'))   # 0.42→0.252 (user x0.6)
drone_fade.add(660, fade(detuned_drone([146.83, 174.61, 220.00], 110, amp=0.50),
                          fi=15, fo=30))
drone_fade.fx(lambda a: reverb(a, decay=6.0, mix=0.6))

# 31. CLOSURE BELL D5
closure = comp.add_track(Track('closure_bell', gain=0.18, color='#d8c060'))   # 0.32→0.18 — REVERTIDO al backup, suena bien con reverb sin clamp
closure.add(720, fade(bell(587.33, dur=20, amp=0.40, decay_rate=0.6), fi=0.08, fo=2))   # D5
closure.add(750, fade(bell(440.00, dur=20, amp=0.55, decay_rate=0.7), fi=0.08, fo=2))   # A4 (octava original) amp 0.30→0.55 — user "no puede ser lo mismo que 17:05, suena muy arriba"
closure.fx(lambda a: lpf(a, 1500))                                # anti-fritura armonicos altos
closure.fx(lambda a: reverb(a, decay=8.0, mix=0.7))


# ============================================================================
# HEART pum-pum-pum acelerado (entre 4:00-4:25 y 4:45-5:15)
# Pum-pum-pum (3 beats cada 0.3s) + pausa 2.0s, ciclo 2.6s.
# Mismo kick que heart_pulse del outbound.
# ============================================================================

heart_acel = comp.add_track(Track('heart_acelerado_momia', gain=0.10, pan=0.0,
                                   color='#d04545'))

def _heart_kick_momia(amp):
    return kick(amp=amp, dur=0.4, f0=60,
                attack_ms=8.0, release_ms=40.0, pitch_sweep=False)

def _heart_cycle(t_start, amp):
    for off in [0.0, 0.3, 0.6]:
        heart_acel.add(t_start + off, _heart_kick_momia(amp=amp))

_HEART_CYCLE_DUR = 2.6   # 0.6s pum-pum-pum + 2.0s pausa

# Gap 1 (240-265s): amp 0.55
_t = 240.0
while _t + 0.6 < 265:
    _heart_cycle(_t, amp=0.55)
    _t += _HEART_CYCLE_DUR
# Gap 2 (285-315s): crescendo 0.58 → 0.65
_t = 285.0
_ciclos_g2 = 0
while _t + 0.6 < 315:
    _amp = min(0.58 + _ciclos_g2 * 0.005, 0.65)
    _heart_cycle(_t, amp=_amp)
    _t += _HEART_CYCLE_DUR
    _ciclos_g2 += 1

heart_acel.fx(lambda a: lpf(a, 250))   # sub-grave puro, sin contenido alto


# ============================================================================
# DUCKER CLIMAX 7:30-7:45 (= 15:30-15:45 en continuo)
# Bajar -9 dB en wall_of_sound + sub_punisher + glitches + feedback para
# evitar fritura por acumulacion de tracks distorsionados en climax.
# ============================================================================

_DUCK_TRACKS = {
    'wall_of_sound_climax', 'sub_punisher_climax',
    'glitch_bursts_climax', 'feedback_squeal',
}
_duck_env = [(0, 1.0), (445, 1.0), (450, 0.35), (465, 0.35), (470, 1.0), (DURATION, 1.0)]
for _tr in comp.tracks:
    if _tr.name in _DUCK_TRACKS:
        _tr.fx(lambda a, p=_duck_env: amp_envelope(a, p))


if __name__ == '__main__':
    from aem.auto_fixes import apply_auto_fixes
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    apply_auto_fixes(comp, verbose=True)
    comp.list_tracks()
    print()
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'))
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
