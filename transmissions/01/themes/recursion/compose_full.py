"""Recursion — TEMA COMPLETO (3:00). Hibrido A+B.

Storyboard:
  0:00 - 0:30  PERTURBACION   crackle + glitches + drone dark + voces invertidas
  0:30 - 1:15  WALL ESCALA    wall_of_sound entra, sub_punisher, feedback squeal
  1:15 - 1:35  PEAK           todo al maximo
  1:35 - 2:00  DESPEJE        downlifter, wall fade, glitches espacian, drone limpio emerge
  2:00 - 2:35  VOYAGER        melodia completa, brillante
  2:35 - 3:00  CIERRE/LOOP    voyager echo, bell D5, drone Dm fade — prepara loop al outbound
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
    detuned_drone, voice_pad, kick, melody, bell, sub_rumble,
    wall_of_sound, feedback_squeal, downlifter, riser,
    vinyl_crackle, glitch_burst, pitch_jitter_melody,
)
from aem.effects import fade, lpf, hpf, reverb, distort, amp_envelope, lfo_amp, notch_eq

DURATION = 180  # 3:00
OUT = os.path.join(TRANSMISSION_ROOT, 'out', 'recursion')
NAME = 'recursion_FULL'

comp = Composition(DURATION, name='Recursion (full) - hybrid A+B')

VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]

rng = np.random.default_rng(42)


# ============================================================================
# PERTURBACION (0:00 - 0:30) — Burial-style glitch + crackle + drone dark
# ============================================================================

# 00. SUB CONTINUITY — sub_42 que conecta con el final del Crossing.
# Arranca a 0:00 con fade in suave para que la entrada no sea abrupta.
sub_continuity = comp.add_track(Track('sub_continuity', gain=0.18, color='#3a4a5c'))   # 0.18→0.09 (user x0.5)
sub_continuity.add(0, sine(42, 25, 0.4))
# Fade in 8s desde 0 — antes arrancaba a 0.6 abrupto.
sub_continuity.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (8, 0.6), (15, 0.4), (25, 0.0),
]))

# 01. VINYL CRACKLE — bed (BAJADO 0.40 → 0.20: tapaba todo)
# Fade in suave (5s) para que no entre abrupto del silencio del Crossing
crackle = comp.add_track(Track('vinyl_crackle', gain=0.025, color='#3a3030'))   # 0.04→0.025 (sigue muy presente)
crackle.add(0, vinyl_crackle(dur=DURATION, density=0.25, amp=0.22, base_hiss=0.02, seed=42))
crackle.fx(lambda a: hpf(a, 400))    # antes 800: dejaba solo agudos brillantes. 400 da cuerpo.
crackle.fx(lambda a: lpf(a, 4500))   # corta el techo mas estridente
crackle.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (5, 1.0), (90, 1.0), (110, 0.5), (180, 0.0),
]))
crackle.fx(lambda a: reverb(a, decay=2.0, mix=0.3))

# 02. DRONE Dm dark — bed armonico oscuro
drone_dark = comp.add_track(Track('drone_dm_dark', gain=0.14, color='#3a2a4c'))
drone_dark.add(0, fade(detuned_drone([146.83, 174.61, 220.00], 100, amp=0.45),
                        fi=20, fo=20))                       # fi 10→20s (entrada mas larga, "entra todo" no era abrupto)
drone_dark.fx(lambda a: lpf(a, 1800))   # 1200→1800 (Lustmord open)
drone_dark.fx(lambda a: reverb(a, decay=5.0, mix=0.55))

# 03. GLITCH BURSTS — esparcidos en perturbacion + peak
glitches = comp.add_track(Track('glitch_bursts', gain=0.16, pan=-0.2, color='#5a3a4a'))   # 0.24→0.16
glitch_times = [3, 7, 11, 14, 18, 23, 27,  # perturbacion dense
                40, 50, 60, 65, 75, 80, 90, 95]  # tambien sobre el wall
for t in glitch_times:
    f = rng.choice([400, 800, 1200, 2400, 600, 1800, 350])
    glitches.add(t, glitch_burst(dur=0.10 + rng.random() * 0.08,
                                  freq_center=f, bandwidth=0.4, amp=0.55))
glitches.fx(lambda a: amp_envelope(a, [(0, 1.0), (95, 1.0), (100, 0.0)]))
glitches.fx(lambda a: reverb(a, decay=2.5, mix=0.4))

# 04. REVERSE-LIKE VOICES (voice_pad con fade reverso)
def reverse_voice_event(freq, dur, amp=0.40):
    raw = voice_pad(freq, dur, vibrato_rate=3.0, amp=amp, n_harmonics=4)
    return fade(raw[::-1], fi=dur * 0.6, fo=dur * 0.05)

reverse_voice = comp.add_track(Track('reverse_voice', gain=0.20, pan=+0.3, color='#5a4070'))
reverse_voice.add(8, reverse_voice_event(440.00, 6))   # 0:08
reverse_voice.add(20, reverse_voice_event(587.33, 6))  # 0:20
reverse_voice.fx(lambda a: lpf(a, 2000))   # 1500→2000 (Lustmord open)
reverse_voice.fx(lambda a: reverb(a, decay=5.0, mix=0.50))   # 0.6→0.50

# 05. BROKEN BEAT — kicks fragmentados sin patron en perturbacion
broken = comp.add_track(Track('broken_beat', gain=0.09, color='#5c2a2a'))   # 0.13→0.09
for t in [5, 13, 24]:
    broken.add(t, kick(amp=0.7, dur=0.6, f0=70, fe=32))
broken.fx(lambda a: lpf(a, 200))
broken.fx(lambda a: reverb(a, decay=3.5, mix=0.45))


# ============================================================================
# WALL ESCALA + PEAK (0:30 - 1:35) — Sunn O))) catedral
# ============================================================================

# 06. WALL OF SOUND principal (D2 + A1) — entra a 0:30, peak 1:15-1:35
# 06. WALL OF SOUND — SACADO. Saturaba/se quebraba cuando subia (1:30-1:35).
# Reemplazado por un drone D2 sostenido simple con leve distort = masa
# armonica sin el wall masivo que rompia el sonido.
wall = comp.add_track(Track('wall_replacement_drone', gain=0.18, color='#1a0a14'))
wall.add(30, fade(detuned_drone([55.00, 73.42], 70, amp=0.40,
                                  n_voices=2, detune_cents=6,
                                  waveform='triangle'),
                   fi=15, fo=8))
wall.fx(lambda a: amp_envelope(a, [
    (0, 0.0), (30, 0.0), (45, 0.5), (75, 0.8), (80, 0.8), (95, 0.0),   # user: fade out 1:20→1:35
]))
wall.fx(lambda a: distort(a, amount=0.6))
wall.fx(lambda a: lpf(a, 2000))   # 1500→2000 (Lustmord open)
wall.fx(lambda a: reverb(a, decay=5.0, mix=0.5))

# 07. SUB PUNISHER 28Hz — bajado 0.50→0.20→0.10 (28 Hz tiembla fisicamente).
# Comparado a 12:30 del continuous (chant a 73 Hz audible pero no tiembla),
# 28 Hz es casi infrasonido y se siente en el cuerpo.
sub = comp.add_track(Track('sub_punisher', gain=0.05, color='#2a0a14'))
sub.add(28, fade(sub_rumble(freq=28, dur=72, mod_rate=0.2, mod_depth=0.5), fi=3, fo=5))   # fade al evento
sub.fx(lambda a: distort(a, amount=0.8))
sub.fx(lambda a: amp_envelope(a, [
    (0, 0.0),
    (28, 0.0),
    (45, 0.7),
    (80, 0.7),   # user: fade out 1:20→1:35
    (95, 0.0),
]))

# 08. FEEDBACK SQUEAL — nota alta inestable, MUY sutil (perforaba el timpano)
fb = comp.add_track(Track('feedback_squeal', gain=0.07, pan=+0.3, color='#5a3030'))   # gain 0.14→0.07
fb.add(50, feedback_squeal(freq=1480, dur=45, sweep_depth=0.025, sweep_rate=0.4,
                           amp=0.30, decay_rate=0.10))   # amp 0.5→0.30
fb.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 09. RISER pre-peak — anuncia el peak a 1:15. Fade out mas suave.
riser_pre_peak = comp.add_track(Track('riser_pre_peak', gain=0.28, color='#909090'))   # 0.28→0.168 (user x0.6)
riser_pre_peak.add(70, fade(riser(dur=8, f_start=80, f_end=600, amp=0.40), fi=0, fo=2.5))   # amp 0.55→0.40
riser_pre_peak.fx(lambda a: lpf(a, 2000))
riser_pre_peak.fx(lambda a: reverb(a, decay=4.5, mix=0.5))  # decay mas largo

# 09b. PEAK SUSTAIN — drone alto que cubre el hueco entre el peak (1:35) y
# el downlifter_release (1:40). Antes habia silencio; ahora un sustain con
# distortion que mantiene la presencia.
peak_sustain = comp.add_track(Track('peak_sustain', gain=0.12, pan=+0.2, color='#7a3030'))   # 0.12→0.06 (user x0.5)
# Standard Tool: triangle + n_voices/detune reducido + distort suave + notch
# Sin A2 (110): su 4to harm = A4 (440) que con distort generaba A5/A6 punzantes.
peak_sustain.add(85, fade(detuned_drone([55.00, 73.42], 18, amp=0.30,
                                          n_voices=2, detune_cents=8,
                                          waveform='triangle'),
                           fi=2, fo=8))
peak_sustain.fx(lambda a: distort(a, amount=1.5))
peak_sustain.fx(lambda a: lpf(a, 1800))   # 1200→1800 (Lustmord open)
peak_sustain.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
peak_sustain.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
peak_sustain.fx(lambda a: reverb(a, decay=3.5, mix=0.45))    # decay 5→3.5 (cola termina antes)


# ============================================================================
# DESPEJE (1:35 - 2:00) — downlifter, drone limpio emerge
# ============================================================================

# 10. DOWNLIFTER de release a 1:40 (post-peak)
# Bajado gain 0.45→0.20 + fade in 1.5s al evento (sin fade el attack era abrupto
# y se sentia como CLICK/POP a 1:41 = 22:25 del continuous, "parlante desconado").
down = comp.add_track(Track('downlifter_release', gain=0.20, color='#7a5050'))   # 0.20→0.10 (user x0.5)
down.add(100, fade(downlifter(dur=10, f_start=400, f_end=80, amp=0.6),
                    fi=1.5, fo=2.0))
down.fx(lambda a: reverb(a, decay=4.0, mix=0.5))

# 11. DRONE Dm limpio que emerge — a 1:40, dura hasta el final
drone_clean = comp.add_track(Track('drone_dm_clean', gain=0.25, color='#7a5cb8'))   # 0.25→0.175 (user x0.7)
# SACADO A3 (220 Hz): su 4to armonico = A5 (880 Hz, zona Fletcher-Munson) era
# lo que aturdia a 22:40 incluso con notch. Drone queda D3-F3 (Dm sin quinta).
# Subo gain ligeramente (0.20 → 0.25) porque al sacar la nota perdimos energia.
drone_clean.add(100, fade(detuned_drone([146.83, 174.61], 80, amp=0.40,
                                          n_voices=2, detune_cents=4,
                                          waveform='triangle'),
                          fi=12, fo=20))
drone_clean.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
drone_clean.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
drone_clean.fx(lambda a: reverb(a, decay=5.5, mix=0.55))


# ============================================================================
# VOYAGER REGRESA (2:00 - 2:35)
# ============================================================================

# 12. VOYAGER limpio — el regreso, brillante
# Sweet spot FANTASMAL: audible pero escondido + LPF corta brillo + mas reverb wet.
# Iteracion: 0.55 inaudible, 0.75 demasiado, 0.65 todavia fuerte, 0.45 + lpf
# + reverb wet = fantasmal real (presencia espectral, no protagonica).
voyager = comp.add_track(Track('voyager_return', gain=0.06, pan=+0.2, color='#e6c34d'))   # 0.06→0.036 (user x0.6)
# Motivo original (con A5). Volumen bajo (fantasmal de fondo, sweet spot 22:50)
voyager.add(120, melody(VOYAGER_NOTES, amp=0.22, vibrato=True,
                          waveform='triangle', release=0.6, release_curve=1.0))
voyager.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voyager.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voyager.fx(lambda a: lpf(a, 1500))                   # 2200 → 1500 (corta A6 tambien)
voyager.fx(lambda a: reverb(a, decay=4.0, mix=0.55))  # 7/0.7 → 4/0.55 (cola mas corta, menos acumulacion)

# 13. VOYAGER ECHO — eco del fantasma. Tambien volumen MUY bajo.
voyager_echo = comp.add_track(Track('voyager_echo', gain=0.05, pan=-0.4, color='#8a7030'))   # 0.05→0.030 (user x0.6)
voyager_echo.add(134, melody(VOYAGER_NOTES, amp=0.20, vibrato=True,
                               waveform='triangle', release=0.6, release_curve=1.0))   # 2:14 (era 2:04) — entra cuando voyager_return termina, no se pisan
voyager_echo.fx(lambda a: notch_eq(a, freq_hz=880.00, q=10, gain_db=-12))
voyager_echo.fx(lambda a: notch_eq(a, freq_hz=1760.00, q=10, gain_db=-12))
voyager_echo.fx(lambda a: lpf(a, 1800))
voyager_echo.fx(lambda a: reverb(a, decay=6.0, mix=0.7))


# ============================================================================
# CIERRE / LOOP (2:35 - 3:00)
# ============================================================================

# 14. BELL D5 final — closure marker
bells = comp.add_track(Track('closure_bell', gain=0.10, color='#d8c060'))   # 0.08→0.10 (subido apenas — el A5 quedo muy bajito)
bells.add(155, bell(587.33, dur=20, amp=0.18, decay_rate=0.8))   # amp 0.15→0.18 (subido un pelin)
bells.add(165, bell(880.00, dur=15, amp=0.13, decay_rate=1.0))   # amp 0.08→0.13 (subido)
bells.fx(lambda a: lpf(a, 2000))   # 1500→2000 (Lustmord open)
bells.fx(lambda a: reverb(a, decay=8.0, mix=0.55))   # 0.7→0.55

# 15. SUB CIERRE — sub_42hz vuelve sutilmente para preparar el loop al outbound
# Gain 0.40 → 0.30: matchea con el sub_42hz del inicio del outbound (gain 0.30)
# para que el loop continuous sea continuo, sin saltos.
sub_loop = comp.add_track(Track('sub_42_loop_prep', gain=0.05, color='#3a4a5c'))   # 0.05→0.03 (user x0.6)
sub_loop.add(160, sine(42, 20, 0.4))
# El user no quiere "lo que levanta a 23:24". Volumen casi imperceptible para
# mantener la conexion del loop con el outbound (sub_42 al inicio) sin que
# se sienta como un elemento que "levanta" al final.
sub_loop.fx(lambda a: amp_envelope(a, [
    (0, 0), (160, 0), (170, 0.3), (175, 0.4), (180, 0.0),
]))


def _global_fadeout(audio, fadeout_s=8.0):
    """Fade out global en los ultimos N segundos del recursion master.
    Garantiza que NADA termine abrupto al cierre (3:00) — conecta limpio
    con el inicio del outbound en el continuous EP loop."""
    n_fade = int(fadeout_s * SR)
    if len(audio) > n_fade:
        ramp = np.linspace(1, 0, n_fade) ** 1.5
        if audio.ndim == 2:
            audio[-n_fade:] *= ramp[:, None]
        else:
            audio[-n_fade:] *= ramp
    return audio


if __name__ == '__main__':
    from aem.auto_fixes import apply_auto_fixes
    print(f'\n{comp.name}  {DURATION}s  {len(comp.tracks)} tracks')
    apply_auto_fixes(comp, verbose=True)
    comp.list_tracks()
    print()
    # Aplica fade out global en los ultimos 8s — conexion limpia con outbound
    comp.export_wav(os.path.join(OUT, 'master', f'{NAME}.wav'),
                    master_fx=_global_fadeout)
    comp.export_stems(os.path.join(OUT, 'stems', NAME))
