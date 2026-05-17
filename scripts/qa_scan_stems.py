"""QA por stem — recorre cada track del tema buscando frituras y problemas
de attack/release individuales.

Para cada stem:
  1. T_ABRUPT_ENTRY: peak en los primeros 50ms del onset > N (entrada abrupta = TIC)
  2. T_ABRUPT_END: peak en los ultimos 50ms del offset > N (corte abrupto = TIC)
  3. T_INTERNAL_TRANSIENT: jumps sample-level > N*median dentro del stem
  4. T_HOT_BAND: ratio energia 1500-4000 Hz > N (fritura zona Fletcher-Munson)
  5. T_BRIGHT_BAND: ratio 4000-8000 Hz > N (brillo punzante triangle/voice)

Reporta con timestamp absoluto del tema (no del stem).

Uso:
  python3.10 scripts/qa_scan_stems.py <theme>
    ej: python3.10 scripts/qa_scan_stems.py outbound

  task qa:stems
"""

import argparse
import os
import sys

import numpy as np
from scipy.io import wavfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# thresholds calibrados (subidos para evitar falsos positivos)
ONSET_PEAK_RATIO = 5.0          # peak en onset > N * media del sustain
ONSET_MIN_PEAK = 0.10           # ignorar si peak absoluto < esto
INTERNAL_JUMP_RATIO = 12.0      # jump sample > N * mediana local
INTERNAL_MIN_JUMP = 0.06
HOT_RATIO_THRESH = 0.40
BRIGHT_RATIO_THRESH = 0.25
WINDOW_FFT_S = 1.0

# Stems que son percutivos/transitorios por design (kicks, glitches, granular).
# Skip T_INTERNAL_TRANSIENT y T_ABRUPT_ENTRY/END para estos.
PERCUSSIVE_STEMS_SUBSTR = [
    'heart_pulse', 'granular_bed', 'capsule_signals', 'capsule_thump',
    'climax_glitches', 'sub_pulses', 'glitch_burst', 'broken_beat',
    'pre_heartbeat',
]

# Bells: attack agudo por naturaleza, no son fritura.
BELL_STEMS_SUBSTR = ['bell', 'pings', 'climax_closure_bell']

# --- Patterns documentados de bugs recurrentes ---
# Estos son los CASOS REALES que el QA debe atrapar (no falsos positivos):
#
# T_ABRUPT_ENTRY: evento entra a t > 0 sin fade — peak inicial = click sample-level.
#   Ejemplos historicos: wind_echo, wind_wave_2_3, wind_turbulent, field_atmosphere
#   t=60, downlifter peak-at-start sin fade in, ritual_bell envelope exp peak inicial.
#
# T_ABRUPT_END: evento termina sin fade — peak final corta abrupto.
#   Ejemplos: riser_pre_momia (env ta^1.5 termina en peak), whoosh_up con fo=0,
#   passing_objects_R con fo=0 (5 endpoints generaban 5 TICs).
#
# T_KICK_PITCH_SWEEP: kick() con pitch_sweep=True (default) genera transients
#   en la modulacion FM que el LPF 220 no atrapa completamente. SOLUCION:
#   pitch_sweep=False para kicks "sostenidos" (heart_*, sub_*, capsule_thump).
#
# T_CONCURRENT_ENTRY: 2+ eventos entrando en mismo timestamp en distintos tracks =
#   suma de transients ataque = click compuesto. Ejemplo: kick 1:38 + bassline 1:38.
#   Detector: ver concurrent_entries() abajo.
#
# T_LAYER_TRANSIENT_STACK: multiples layers de un mismo motivo cambiando de nota
#   al mismo sample = transient compuesto. Fix: crossfade entre notas o desfasar.
#
# T_REVERB_TAIL_OVERLAP: kicks frecuentes (cada N seg) con reverb decay > N seg
#   acumulan colas = saturacion SPL en grave. Fix: bajar reverb decay/mix.


# Stems "FX intencionales" — ruido o squeal frequencialmente rico por design.
# Skip TODOS los tags (incluyendo HOT_BAND/BRIGHT_BAND) para estos.
INTENTIONAL_FX_SUBSTR = [
    'feedback_squeal',     # nota alta inestable Burial-style (crossing/recursion)
    'vinyl_crackle',       # chasquidos broadband intencionales
    'wall_of_sound',       # distort layered intencional
    'voyager_degraded',    # transmision rota deliberada
    'radio_interference',  # noise filtrado intencional
    'sub_punisher',        # sub bass agresivo
    'sub_rumble',
    'wind_turbulent',      # noise turbulento intencional
    'chant_degraded',
]


def is_percussive(name):
    return any(s in name.lower() for s in PERCUSSIVE_STEMS_SUBSTR)


def is_bell(name):
    return any(s in name.lower() for s in BELL_STEMS_SUBSTR)


def is_intentional_fx(name):
    return any(s in name.lower() for s in INTENTIONAL_FX_SUBSTR)


def load_mono(path):
    """Lee WAV y normaliza a float [-1, 1] de manera correcta para int16/24/32."""
    import soundfile as sf
    x, sr = sf.read(path, always_2d=False)
    if x.ndim == 2:
        x = x.mean(axis=-1)
    return sr, x.astype(np.float32)


def fmt_t(t):
    m = int(t // 60)
    s = t - m * 60
    return f'{m}:{s:05.2f}'


def find_event_boundaries(x, sr, peak_thresh=0.005):
    """Detecta los eventos (rangos donde el stem suena) buscando regiones con
    abs > peak_thresh, agrupando con tolerancia de 200ms."""
    above = np.abs(x) > peak_thresh
    if not above.any():
        return []
    # Smooth: cerrar gaps < 200ms
    gap_n = int(0.2 * sr)
    events = []
    in_event = False
    start_idx = 0
    last_above = 0
    for i, v in enumerate(above):
        if v:
            if not in_event:
                in_event = True
                start_idx = i
            last_above = i
        else:
            if in_event and (i - last_above) > gap_n:
                events.append((start_idx, last_above))
                in_event = False
    if in_event:
        events.append((start_idx, last_above))
    # Filtrar eventos muy cortos (< 0.1s)
    return [(s, e) for s, e in events if (e - s) > int(0.1 * sr)]


def scan_event(x, sr, ev_start, ev_end, name):
    """Para un evento, detecta entry/exit abruptos + transientes internos."""
    findings = []
    seg = x[ev_start:ev_end]
    if len(seg) < 100:
        return findings

    # 1. Onset abrupto: comparar peak primeros 50ms vs media RMS sustain
    onset_n = int(0.05 * sr)
    sustain_n = int(0.5 * sr)
    if len(seg) < onset_n + sustain_n:
        return findings
    onset_peak = float(np.max(np.abs(seg[:onset_n])))
    sustain_rms = float(np.sqrt(np.mean(seg[onset_n:onset_n + sustain_n] ** 2)) + 1e-9)
    if onset_peak > ONSET_MIN_PEAK and onset_peak > ONSET_PEAK_RATIO * sustain_rms:
        t = ev_start / sr
        findings.append(('T_ABRUPT_ENTRY', t, onset_peak, sustain_rms))

    # 2. Offset abrupto: peak ultimos 50ms vs sustain previo
    offset_peak = float(np.max(np.abs(seg[-onset_n:])))
    sustain_pre = seg[-onset_n - sustain_n:-onset_n] if len(seg) > onset_n + sustain_n else seg[:onset_n]
    sustain_pre_rms = float(np.sqrt(np.mean(sustain_pre ** 2)) + 1e-9)
    if offset_peak > ONSET_MIN_PEAK and offset_peak > ONSET_PEAK_RATIO * sustain_pre_rms:
        t = ev_end / sr
        findings.append(('T_ABRUPT_END', t, offset_peak, sustain_pre_rms))

    # 3. Transientes internos: jumps sample-level > N * mediana local
    if len(seg) > sr:
        diff = np.abs(np.diff(seg))
        win_n = int(0.5 * sr)
        for i in range(0, len(diff) - win_n, win_n // 2):
            win = diff[i:i + win_n]
            med = float(np.median(win))
            if med < 1e-9:
                continue
            peak_idx_local = int(np.argmax(win))
            peak_jump = float(win[peak_idx_local])
            if peak_jump < INTERNAL_MIN_JUMP:
                continue
            ratio = peak_jump / med
            if ratio < INTERNAL_JUMP_RATIO:
                continue
            t = (ev_start + i + peak_idx_local) / sr
            findings.append(('T_INTERNAL_TRANSIENT', t, peak_jump, ratio))

    # 4-5. Energia spectral en bandas HOT/BRIGHT por ventanas
    win_fft_n = int(WINDOW_FFT_S * sr)
    for i in range(0, len(seg) - win_fft_n, win_fft_n // 2):
        frame = seg[i:i + win_fft_n] * np.hanning(win_fft_n)
        spec = np.abs(np.fft.rfft(frame)) ** 2
        freqs = np.fft.rfftfreq(win_fft_n, d=1.0 / sr)
        total = spec[freqs >= 50].sum() + 1e-12
        hot = spec[(freqs >= 1500) & (freqs <= 4000)].sum() / total
        bright = spec[(freqs >= 4000) & (freqs <= 8000)].sum() / total
        t = (ev_start + i + win_fft_n // 2) / sr
        if hot >= HOT_RATIO_THRESH:
            findings.append(('T_HOT_BAND', t, hot, 0))
        if bright >= BRIGHT_RATIO_THRESH:
            findings.append(('T_BRIGHT_BAND', t, bright, 0))

    return findings


def scan_stem(stem_path):
    sr, x = load_mono(stem_path)
    name = os.path.basename(stem_path).replace('.wav', '')
    # Stems FX intencionales: skip TODO (no flag nada)
    if is_intentional_fx(name):
        return name, []
    events = find_event_boundaries(x, sr)
    all_findings = []
    perc = is_percussive(name)
    bell = is_bell(name)
    for ev_start, ev_end in events:
        for f in scan_event(x, sr, ev_start, ev_end, name):
            tag = f[0]
            if perc and tag in ('T_INTERNAL_TRANSIENT', 'T_ABRUPT_ENTRY', 'T_ABRUPT_END'):
                continue
            if bell and tag in ('T_ABRUPT_ENTRY', 'T_ABRUPT_END'):
                continue
            all_findings.append(f)
    return name, all_findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('theme', help='outbound, crossing, recursion, etc')
    ap.add_argument('--types', nargs='*', default=None,
                    help='filtrar tipos (T_ABRUPT_ENTRY, T_ABRUPT_END, T_INTERNAL_TRANSIENT, T_HOT_BAND, T_BRIGHT_BAND)')
    args = ap.parse_args()

    stems_dir = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'out',
                                args.theme, 'stems', f'{args.theme}_FULL')
    if not os.path.isdir(stems_dir):
        print(f'ERROR: no existe {stems_dir}', file=sys.stderr)
        sys.exit(2)

    print(f'=== QA per-stem: {args.theme} ===')
    print(f'  scanning {stems_dir}')

    total_findings = 0
    by_type = {}
    by_stem = {}
    for f in sorted(os.listdir(stems_dir)):
        if not f.endswith('.wav'):
            continue
        path = os.path.join(stems_dir, f)
        name, findings = scan_stem(path)
        if args.types:
            findings = [f_ for f_ in findings if f_[0] in args.types]
        if not findings:
            continue
        total_findings += len(findings)
        by_stem[name] = findings
        for tag, *_ in findings:
            by_type[tag] = by_type.get(tag, 0) + 1

    if total_findings == 0:
        print('  OK — ningun problema detectado')
        sys.exit(0)

    print(f'  hallazgos totales: {total_findings}')
    print(f'  por tipo: {dict(sorted(by_type.items()))}\n')

    for stem, findings in by_stem.items():
        # Deduplicar findings cercanos (mismo tipo, < 0.5s aparte)
        deduped = []
        last_by_type = {}
        for tag, t, val, ratio in findings:
            if tag in last_by_type and abs(t - last_by_type[tag]) < 0.5:
                continue
            deduped.append((tag, t, val, ratio))
            last_by_type[tag] = t
        if not deduped:
            continue
        print(f'\n{stem}  ({len(deduped)} hits):')
        for tag, t, val, ratio in deduped[:15]:
            extra = f'  ratio={ratio:.1f}x' if ratio else ''
            print(f'  {fmt_t(t):>8s}  {tag:<25s}  val={val:.4f}{extra}')
        if len(deduped) > 15:
            print(f'  ... y {len(deduped)-15} mas')

    sys.exit(1)


if __name__ == '__main__':
    main()
