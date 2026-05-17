"""Exporta los 3 temas del EP a MIDI (partes melódicas/armónicas/ritmicas).

Filosofia: el framework genera AUDIO sintetizado. Para colaboracion con
musicos/productores que usan DAWs (Logic, Ableton, etc.), exportamos las
partes "tocables" como MIDI:
  - Melodias (voyager y variantes)
  - Drones armonicos por seccion
  - Bassline melodica
  - Heart pulse / kicks
  - Voices (notas sostenidas)
  - Bells (notas puntuales)

NO se exporta a MIDI lo que es textura/synthesis no-melodica:
  - cosmos noise, granular, vinyl crackle, field recordings
  - wall_of_sound (drones detuned + distort masivo)
  - whooshes / risers / downlifters / reverse swells
  - glitches / bursts
  - sub_punisher / sub_rumble (sub-bass con LFO/distort)
  - chants (chant_drone formant synthesis — son notas pero los formantes
    no se traducen a MIDI; se incluyen como notas single basicas)
  - radio_interference, dirty_intro (efectos master)

Output:
  transmissions/01/release/distribution/midi/
    01 - Outbound.mid
    02 - Crossing.mid
    03 - Recursion.mid

Uso:
  python3 scripts/export_midi.py [--tx 01]
"""

import argparse
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'framework'))

from aem.midi_helpers import make_builder, GM_INSTRUMENTS  # noqa: E402

# Notas del proyecto (mismas constantes de los compose)
VOYAGER_NOTES = [
    (587.33, 1.5), (698.46, 1.0), (880.00, 1.5), (698.46, 1.0),
    (587.33, 2.0), (440.00, 2.0), (587.33, 3.0),
]
COUNTER_NOTES = [(f * 1.5, d) for f, d in VOYAGER_NOTES]
VOYAGER_INVERTED = [
    (587.33, 1.0), (440.00, 1.0), (698.46, 1.5), (440.00, 1.0),
    (587.33, 1.5), (698.46, 1.5), (880.00, 2.5),
]


# ============================================================================
# OUTBOUND — 8:00
# ============================================================================

def export_outbound(output_path):
    mb = make_builder(bpm=120, ticks_per_beat=480)

    # 1. SUB 42Hz — solo durante capsule (0-30s, simbolico)
    # 42 Hz ≈ F1 — lo dejamos como nota sostenida
    mb.add_chord_track('Sub 42Hz (F1 sustained)',
                       [(0, [42.00], 30)],
                       program=GM_INSTRUMENTS['synth_bass'], channel=0,
                       velocity=60)

    # 2. HEART PULSE — 60 BPM constante 0:30-1:30 (60 kicks)
    heart_times = [30 + i for i in range(60)]
    # Fade out 1:30-1:42
    heart_times += [90 + i for i in range(12)]
    mb.add_kick_track('Heart Pulse 60 BPM', heart_times, channel=9, note=36)

    # 3. DRONE Dm armonico (D-F-A) — 0:50 → 7:50
    mb.add_chord_track('Drone Dm (D3-F3-A3) sustained',
                       [(50, [146.83, 174.61, 220.00], 415)],
                       program=GM_INSTRUMENTS['pad_warm'], channel=1,
                       velocity=60)

    # 4. SUB-DRONE D2-F2 — 1:45 → 7:50
    mb.add_chord_track('Sub Drone (D2-F2)',
                       [(105, [73.42, 87.31], 365)],
                       program=GM_INSTRUMENTS['synth_bass'], channel=2,
                       velocity=55)

    # 5. SUB PULSES — kicks lentos
    sub_pulse_times = [62, 78, 95, 112, 130, 148, 168, 188, 208, 228]
    mb.add_kick_track('Sub Pulses (kicks lentos)', sub_pulse_times,
                      channel=9, note=35, velocity=70)

    # 6. VOYAGER — todas las apariciones (melody completa + fragmentos)
    # vooyager_left, voyager_right, voyager_center fueron mergidos en Outbound v6.
    # En el Outbound actual (compose_full) tenemos:
    voyager_events = [
        (95,  VOYAGER_NOTES),                   # 1:35 main entry L
        (115, VOYAGER_NOTES),                   # 1:55 R
        (130, VOYAGER_NOTES[0:3]),              # 2:10 fragment L
        (145, VOYAGER_NOTES[5:7]),              # 2:25 final notes C
        (150, VOYAGER_NOTES[2:5]),              # 2:30 fragment R
        (165, VOYAGER_NOTES[0:4]),              # 2:45 C
        (175, VOYAGER_NOTES),                   # 2:55 L returns
        (195, VOYAGER_NOTES),                   # 3:15 R
        (210, [(587.33, 2.0), (440.00, 2.5)]),  # 3:30 last C before in-pace
    ]
    mb.add_melody_track('Voyager Melody', voyager_events,
                        program=GM_INSTRUMENTS['piano'], channel=3, velocity=85)

    # 7. VOYAGER COUNTER (5ta arriba)
    voyager_counter_events = [
        (135, COUNTER_NOTES[:5]),  # 2:15
        (210, COUNTER_NOTES),      # 3:30
        (295, COUNTER_NOTES[:5]),  # 4:55
    ]
    mb.add_melody_track('Voyager Counter (+5th)', voyager_counter_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=4, velocity=70)

    # 8. VOYAGER inverted (otra fase)
    mb.add_melody_track('Voyager Inverted',
                        [(330, VOYAGER_INVERTED)],
                        program=GM_INSTRUMENTS['pad_polysynth'], channel=5, velocity=70)

    # 9. VOICES preview — D4 sostenido
    mb.add_chord_track('Voices Preview (D4)',
                       [(240, [293.66], 75)],
                       program=GM_INSTRUMENTS['voice_aahs'], channel=6, velocity=60)

    # 10. VOICES L (D4 → Eb4 → D4)
    voices_l_events = [
        (300, [(293.66, 50)]),   # D4
        (348, [(311.13, 45)]),   # Eb4
        (393, [(293.66, 28)]),   # D4
    ]
    mb.add_melody_track('Voices L', voices_l_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=7, velocity=65)

    # 11. VOICES R (A4 → Bb4 → A4)
    voices_r_events = [
        (300, [(440.00, 50)]),
        (348, [(466.16, 45)]),
        (393, [(440.00, 28)]),
    ]
    mb.add_melody_track('Voices R', voices_r_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=8, velocity=65)

    # 12. BELL MARKERS
    bell_events = [
        (60, 587.33, 10), (90, 880.00, 10), (120, 698.46, 12),
        (180, 880.00, 14), (240, 659.25, 12), (270, 880.00, 12),
        (330, 880.00, 14), (360, 880.00, 16), (420, 587.33, 14),
    ]
    mb.add_note_events_track('Bell Markers', bell_events,
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=10, velocity=80)

    # 13. INTRO PINGS
    pings_events = [
        (40, 880.00, 5), (47, 587.33, 4), (52, 698.46, 5),
        (65, 880.00, 5), (72, 587.33, 5), (82, 880.00, 6),
    ]
    mb.add_note_events_track('Intro Pings', pings_events,
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=11, velocity=70)

    mb.save(output_path)
    print(f'  wrote {output_path}')


# ============================================================================
# CROSSING — 13:00
# ============================================================================

def export_crossing(output_path):
    mb = make_builder(bpm=120, ticks_per_beat=480)

    # 1. SUB 42 conexion (0-100s)
    mb.add_chord_track('Sub 42Hz Conexion',
                       [(0, [42.00], 100)],
                       program=GM_INSTRUMENTS['synth_bass'], channel=0, velocity=55)

    # 2. DRONES armonicos (Dm → Bb → F → Am → Dm)
    drone_events = [
        (50,  [146.83, 174.61, 220.00], 100),  # Dm
        (120, [116.54, 146.83, 174.61], 90),   # Bb
        (170, [174.61, 220.00, 261.63], 100),  # F
        (230, [110.00, 130.81, 164.81], 100),  # Am
        (295, [146.83, 174.61, 220.00], 185),  # Dm climax/end
    ]
    mb.add_chord_track('Drones Armonicos', drone_events,
                       program=GM_INSTRUMENTS['pad_warm'], channel=1, velocity=60)

    # 3. BASSLINE (sigue la armonia)
    bass_events = [
        (50,  [73.42], 75),    # D2
        (115, [58.27], 70),    # Bb1
        (175, [87.31], 70),    # F2
        (235, [110.00], 70),   # A2
        (295, [73.42], 175),   # D2 hasta final
    ]
    mb.add_chord_track('Bassline (D2-Bb1-F2-A2-D2)', bass_events,
                       program=GM_INSTRUMENTS['fingered_bass'], channel=2, velocity=70)

    # 4. CHANTS (D2 → A2 → F2)
    chant_events = [
        (210, [73.42], 60),   # D2 — chant 3:30-4:30
        (260, [110.00], 60),  # A2 — chant 4:20-5:20
        (310, [87.31], 60),   # F2 — chant 5:10-6:10
    ]
    mb.add_chord_track('Chant Sardaukar', chant_events,
                       program=GM_INSTRUMENTS['voice_oohs'], channel=3, velocity=70)

    # 5. HEART beat soft (40 BPM = cada 1.5s)
    heart_times = [225 + i * 1.5 for i in range(60) if 225 + i * 1.5 <= 360]
    mb.add_kick_track('Heart Soft 40 BPM', heart_times,
                      channel=9, note=36, velocity=60)

    # 6. VOYAGER — left, right, center (concept del Crossing)
    voy_l_events = [(90, VOYAGER_NOTES), (130, VOYAGER_NOTES[0:3]),
                    (175, VOYAGER_NOTES)]
    voy_r_events = [(115, VOYAGER_NOTES), (150, VOYAGER_NOTES[2:5]),
                    (195, VOYAGER_NOTES)]
    voy_c_events = [(105, VOYAGER_NOTES[0:2]), (145, VOYAGER_NOTES[5:7]),
                    (165, VOYAGER_NOTES[0:4]),
                    (210, [(587.33, 2.0), (440.00, 2.5)])]
    mb.add_melody_track('Voyager L', voy_l_events,
                        program=GM_INSTRUMENTS['piano'], channel=4, velocity=80)
    mb.add_melody_track('Voyager R', voy_r_events,
                        program=GM_INSTRUMENTS['piano'], channel=5, velocity=80)
    mb.add_melody_track('Voyager C', voy_c_events,
                        program=GM_INSTRUMENTS['piano'], channel=6, velocity=70)

    # 7. VOYAGER counter (fase 2: 4:30, 4:55)
    counter_2_events = [(270, COUNTER_NOTES), (310, COUNTER_NOTES[0:5])]
    mb.add_melody_track('Voyager Counter F2', counter_2_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=7, velocity=70)

    # 8. VOYAGER inverted (5:30 bridge a fase 3)
    mb.add_melody_track('Voyager Inverted', [(330, VOYAGER_INVERTED)],
                        program=GM_INSTRUMENTS['pad_polysynth'], channel=8, velocity=70)

    # 9. VOICES preview (4:00-5:15)
    mb.add_chord_track('Voices Preview', [(240, [293.66], 75)],
                       program=GM_INSTRUMENTS['voice_aahs'], channel=10, velocity=55)

    # 10. VOICES L (D4 → Eb4 → D4) — entran 5:00
    voices_l_events = [
        (300, [(293.66, 50)]), (348, [(311.13, 45)]), (393, [(293.66, 28)]),
    ]
    voices_r_events = [
        (300, [(440.00, 50)]), (348, [(466.16, 45)]), (393, [(440.00, 28)]),
    ]
    mb.add_melody_track('Voices L', voices_l_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=11, velocity=65)
    mb.add_melody_track('Voices R', voices_r_events,
                        program=GM_INSTRUMENTS['voice_aahs'], channel=12, velocity=65)

    # 11. BELL MARKERS armonizados
    bell_events = [
        (60,  587.33, 10), (90,  880.00, 10), (120, 698.46, 12),
        (180, 880.00, 14), (240, 659.25, 12), (270, 880.00, 12),
        (330, 880.00, 14), (360, 880.00, 16), (420, 587.33, 14),
    ]
    mb.add_note_events_track('Bell Markers', bell_events,
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=13, velocity=75)

    # 12. RITUAL BELL (4:40)
    mb.add_note_events_track('Ritual Bell A3', [(280, 220.00, 15)],
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=14, velocity=80)

    # 13. CLOSURE BELL (12:00, 12:30)
    closure_events = [(720, 587.33, 20), (750, 440.00, 20)]
    mb.add_note_events_track('Closure Bells', closure_events,
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=15, velocity=70)

    mb.save(output_path)
    print(f'  wrote {output_path}')


# ============================================================================
# RECURSION — 3:00
# ============================================================================

def export_recursion(output_path):
    mb = make_builder(bpm=120, ticks_per_beat=480)

    # 1. SUB CONTINUITY (0-25s) — sub42 conecta con final del Crossing
    mb.add_chord_track('Sub Continuity 42Hz', [(0, [42.00], 25)],
                       program=GM_INSTRUMENTS['synth_bass'], channel=0, velocity=50)

    # 2. DRONE Dm dark (todo el tema)
    mb.add_chord_track('Drone Dm Dark', [(0, [146.83, 174.61, 220.00], 100)],
                       program=GM_INSTRUMENTS['pad_warm'], channel=1, velocity=55)

    # 3. DRONE Dm clean (despues del peak, 1:40-3:00)
    mb.add_chord_track('Drone Dm Clean', [(100, [146.83, 174.61, 220.00], 80)],
                       program=GM_INSTRUMENTS['pad_warm'], channel=2, velocity=70)

    # 4. BROKEN BEAT (kicks fragmentados durante perturbacion)
    broken_times = [5, 13, 24]
    mb.add_kick_track('Broken Beat', broken_times,
                      channel=9, note=36, velocity=80)

    # 5. REVERSE VOICES (notas inquietantes)
    reverse_events = [(8, 440.00, 6), (20, 587.33, 6)]
    mb.add_note_events_track('Reverse Voices', reverse_events,
                             program=GM_INSTRUMENTS['voice_oohs'],
                             channel=3, velocity=55)

    # 6. PEAK SUSTAIN (drone bajo distortioned 1:25-1:45)
    mb.add_chord_track('Peak Sustain (A1-D2-A2)',
                       [(85, [55.00, 73.42, 110.00], 18)],
                       program=GM_INSTRUMENTS['pad_polysynth'],
                       channel=4, velocity=85)

    # 7. VOYAGER RETURN (2:00 — limpio, fantasmal)
    mb.add_melody_track('Voyager Return', [(120, VOYAGER_NOTES)],
                        program=GM_INSTRUMENTS['piano'], channel=5, velocity=60)

    # 8. VOYAGER ECHO (2:04 — mismo, eco)
    mb.add_melody_track('Voyager Echo', [(124, VOYAGER_NOTES)],
                        program=GM_INSTRUMENTS['piano'], channel=6, velocity=45)

    # 9. CLOSURE BELLS (2:35, 2:45)
    closure_events = [(155, 587.33, 20), (165, 880.00, 15)]
    mb.add_note_events_track('Closure Bells', closure_events,
                             program=GM_INSTRUMENTS['tubular_bells'],
                             channel=10, velocity=75)

    # 10. SUB 42 LOOP PREP (2:40-3:00) — para preparar loop al outbound
    mb.add_chord_track('Sub 42Hz Loop Prep', [(160, [42.00], 20)],
                       program=GM_INSTRUMENTS['synth_bass'], channel=11, velocity=55)

    mb.save(output_path)
    print(f'  wrote {output_path}')


# ============================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tx', default='01')
    args = ap.parse_args()

    tx_dir = os.path.join(PROJECT_ROOT, 'transmissions', args.tx)
    out_dir = os.path.join(tx_dir, 'release', 'distribution', 'midi')
    os.makedirs(out_dir, exist_ok=True)

    print(f'\n=== export:midi (transmission {args.tx}) ===')
    export_outbound(os.path.join(out_dir, '01 - Outbound.mid'))
    export_crossing(os.path.join(out_dir, '02 - Crossing.mid'))
    export_recursion(os.path.join(out_dir, '03 - Recursion.mid'))

    print(f'\nMIDI files en: {out_dir}')


if __name__ == '__main__':
    main()
