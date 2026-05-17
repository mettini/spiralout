"""QA estatico del codigo fuente — detecta patterns anti-fritura.

Busca en los compose_full.py de cada tema el patron T_NOISE_FRITURA:
cualquier track de noise filtrado que deje pasar contenido > 1000 Hz
genera "fritura/estatica aguda" perceptual (Fletcher-Munson 1-4 kHz).

Patterns detectados:
  - whoosh(...) sin cutoff_end explicito (usa default — cutoff_end=800 desde
    el fix de mayo 2026, pero antes era 4000 — mantener verificacion)
  - whoosh(cutoff_end=N) con N > 1000
  - lpf(noise(...), N) con N > 1000
  - lpf(np.random.randn(...), N) con N > 1000
  - granular_pulse(freq=N) con N > 800
  - cosmos_swell(cutoff=N) con N > 1000
  - radio_interference(lpf_cutoff=N) con N > 1500 (un poco mas tolerante porque es intencional)
  - T_BELL_HARMONICS: bell(freq, ...) con freq >= 600 sin lpf(track, M<=2200) posterior
    (los bells generan armonicos hasta el 4to — A5=880 → 1760, 2640, 3520 Hz =
    fritura aguda Fletcher-Munson si no se filtran)
  - T_RISER_FRITURA: lpf(riser/cue, N) con N > 2200 (risers son sweeps frecuenciales,
    si pasan > 2200 generan fritura en el peak)

Salida: lista de hallazgos con archivo:linea + nivel (warning/error).
Exit code 1 si hay errores, 0 si todo OK o solo warnings.

Uso:
  python3.10 scripts/qa_scan_code.py
  task qa:scan
"""

import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Umbrales (Hz)
NOISE_CUTOFF_LIMIT = 1000      # > 1000 = fritura
GRANULAR_FREQ_LIMIT = 800      # granular_pulse pasa-banda
RADIO_INTERFERENCE_LIMIT = 1500  # un poco mas tolerante (efecto intencional)
BELL_FREQ_LIMIT = 600          # >= 600 Hz: armonicos > 1500 = fritura
BELL_LPF_MAX = 2200            # max cutoff aceptable para track con bells altos
RISER_LPF_LIMIT = 2200         # risers/cue_release con LPF > 2200 = fritura en peak


def scan_concurrent_entries(path, lines):
    """T_CONCURRENT_ENTRY: detecta 2+ eventos entrando en mismo timestamp en
    distintos tracks = posible TIC compuesto al ataque.

    Casos historicos: kick heart_pulse 1:38 + bassline 1:38, voyager_left 1:30 +
    voyager_swell 1:30, etc. La suma de attacks simultaneos genera click.

    Detecta patrones `<track>.add(<t>, ...)` con mismo `<t>` en distintos tracks.
    """
    errors = []
    # Captura (line_no, track_name, t)
    re_add = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\.add\(\s*([0-9]+(?:\.[0-9]+)?)\s*,')
    entries_by_t = {}  # t -> [(line, track), ...]
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith('#'):
            continue
        m = re_add.match(line)
        if m:
            track = m.group(1)
            t = float(m.group(2))
            entries_by_t.setdefault(t, []).append((i, track))

    for t, entries in entries_by_t.items():
        # Filtrar entradas en mismo track (multiples eventos de heart_pulse en
        # un loop son OK — el problema es que sean DISTINTOS tracks).
        tracks = set(track for _, track in entries)
        if len(tracks) >= 2:
            # Sospechoso solo si t > 0 (t=0 todos arrancan = no es problema)
            if t > 1.0:
                lines_str = ', '.join(f'L{ln}({tr})' for ln, tr in entries)
                errors.append(
                    f'  [T_CONCURRENT_ENTRY] {os.path.relpath(path, PROJECT_ROOT)}\n'
                    f'    {len(tracks)} tracks entran en t={t} (riesgo TIC compuesto):\n'
                    f'    {lines_str}\n'
                    f'    Fix: desfasar uno de los tracks 0.5-2s, o asegurar fade in suficiente'
                )
    return errors


def scan_bells_and_risers(path, lines):
    """Pasa cruzada: detecta bells/risers con cutoff problematico.

    Para cada track, registra:
      - bells_max_freq: frecuencia mas alta del bell agregado al track
      - has_lpf: True si el track tiene `.fx(lambda a: lpf(a, M))` con M aceptable
      - lpf_cutoff: el cutoff aplicado (si existe)
      - bell_lines: lineas donde se agregaron los bells

    Devuelve lista de errores.
    """
    errors = []
    track_bells = {}  # track_name -> [(line, freq), ...]
    track_lpf = {}    # track_name -> [(line, cutoff), ...]

    # Pattern: <track>.add(t, bell(N, ...))
    re_bell_add = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\.add\([^,]+,\s*bell\(\s*([0-9.]+)')
    # Pattern: <track>.fx(lambda a: lpf(a, N))
    re_track_lpf = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\.fx\(\s*lambda\s+\w+\s*:\s*lpf\([^,]+,\s*(\d+(?:\.\d+)?)\s*\)')

    for i, line in enumerate(lines, 1):
        m = re_bell_add.match(line)
        if m:
            tname = m.group(1)
            freq = float(m.group(2))
            track_bells.setdefault(tname, []).append((i, freq))
            continue
        m = re_track_lpf.match(line)
        if m:
            tname = m.group(1)
            cutoff = float(m.group(2))
            track_lpf.setdefault(tname, []).append((i, cutoff))

    # Verificar: cada track con bells de freq alta debe tener LPF aceptable
    for tname, bell_events in track_bells.items():
        max_freq = max(f for _, f in bell_events)
        if max_freq < BELL_FREQ_LIMIT:
            continue
        lpfs = track_lpf.get(tname, [])
        # Aceptable: existe al menos un LPF con cutoff <= BELL_LPF_MAX
        valid = [c for _, c in lpfs if c <= BELL_LPF_MAX]
        if not valid:
            first_line, first_freq = bell_events[0]
            lpf_info = (
                f'sin lpf en track' if not lpfs
                else f'lpf cutoff(s) demasiado alto: {[c for _, c in lpfs]}'
            )
            errors.append(
                f'  [T_BELL_HARMONICS] {os.path.relpath(path, PROJECT_ROOT)}:{first_line}\n'
                f'    track "{tname}" tiene bell(freq={max_freq:.0f}) >= {BELL_FREQ_LIMIT} Hz, {lpf_info}\n'
                f'    armonicos del bell > 1500 Hz = fritura Fletcher-Munson\n'
                f'    fix: agregar `{tname}.fx(lambda a: lpf(a, 1500))` antes del reverb'
            )

    # Pattern: lpf en risers/cue_release con cutoff > RISER_LPF_LIMIT
    re_riser_lpf = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\.fx\(\s*lambda\s+\w+\s*:\s*lpf\([^,]+,\s*(\d+(?:\.\d+)?)\s*\)')
    for i, line in enumerate(lines, 1):
        m = re_riser_lpf.match(line)
        if m:
            tname = m.group(1).lower()
            if 'riser' in tname or 'cue' in tname:
                cutoff = float(m.group(2))
                if cutoff > RISER_LPF_LIMIT:
                    errors.append(
                        f'  [T_RISER_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                        f'    {tname} con lpf cutoff {cutoff:.0f} > {RISER_LPF_LIMIT} Hz — fritura en peak del sweep\n'
                        f'    > {line.strip()}'
                    )

    return errors


def scan_file(path):
    """Devuelve (errors, warnings) — listas de strings con hallazgos."""
    errors = []
    warnings = []
    with open(path) as f:
        lines = f.readlines()

    # Pasa cruzada (bells/risers)
    errors.extend(scan_bells_and_risers(path, lines))
    # Pasa cruzada (concurrent entries en distintos tracks)
    errors.extend(scan_concurrent_entries(path, lines))

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Saltar comentarios y lineas vacias
        if not stripped or stripped.startswith('#'):
            continue

        # Pattern 1: lpf(noise(...) o lpf(np.random.randn(...))
        m = re.search(r'lpf\(\s*(?:noise|np\.random\.randn)\([^)]*\)\s*,\s*(\d+(?:\.\d+)?)', line)
        if m:
            cutoff = float(m.group(1))
            if cutoff > NOISE_CUTOFF_LIMIT:
                errors.append(
                    f'  [T_NOISE_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    lpf(noise, {cutoff:.0f}) > {NOISE_CUTOFF_LIMIT} Hz — fritura aguda esperada\n'
                    f'    > {stripped}'
                )

        # Pattern 2: whoosh(cutoff_end=N) con N alto
        m = re.search(r'whoosh\([^)]*cutoff_end\s*=\s*(\d+(?:\.\d+)?)', line)
        if m:
            cutoff = float(m.group(1))
            if cutoff > NOISE_CUTOFF_LIMIT:
                errors.append(
                    f'  [T_NOISE_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    whoosh(cutoff_end={cutoff:.0f}) > {NOISE_CUTOFF_LIMIT} Hz — fritura aguda\n'
                    f'    > {stripped}'
                )

        # Pattern 3: granular_pulse(freq=N)
        m = re.search(r'granular_pulse\([^)]*freq\s*=\s*(\d+(?:\.\d+)?)', line)
        if m:
            freq = float(m.group(1))
            if freq > GRANULAR_FREQ_LIMIT:
                errors.append(
                    f'  [T_NOISE_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    granular_pulse(freq={freq:.0f}) > {GRANULAR_FREQ_LIMIT} Hz — pasa-banda agudo = fritura\n'
                    f'    > {stripped}'
                )

        # Pattern 4: cosmos_swell(cutoff=N) o cosmos_swell(..., cutoff=N)
        m = re.search(r'cosmos_swell\([^)]*cutoff\s*=\s*(\d+(?:\.\d+)?)', line)
        if m:
            cutoff = float(m.group(1))
            if cutoff > NOISE_CUTOFF_LIMIT:
                warnings.append(
                    f'  [T_NOISE_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    cosmos_swell(cutoff={cutoff:.0f}) > {NOISE_CUTOFF_LIMIT} Hz — posible fritura\n'
                    f'    > {stripped}'
                )

        # Pattern 5: radio_interference(lpf_cutoff=N) — intencional pero alto = exceso
        m = re.search(r'radio_interference\([^)]*lpf_cutoff\s*=\s*(\d+(?:\.\d+)?)', line)
        if m:
            cutoff = float(m.group(1))
            if cutoff > RADIO_INTERFERENCE_LIMIT:
                warnings.append(
                    f'  [T_NOISE_FRITURA] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    radio_interference(lpf_cutoff={cutoff:.0f}) > {RADIO_INTERFERENCE_LIMIT} Hz — efecto agresivo\n'
                    f'    > {stripped}'
                )

        # Pattern 6 (mayo 2026): T_REVERB_DECAY_BUG — la formula del reverb()
        # del framework genera gains de tap > 1 con decay > 4 (ej decay=10,
        # tap 743ms → gain 6.05x = wow/flutter audible). Fix aplicado en
        # framework/aem/effects.py mayo 2026 (clamp del termino base a 1.0).
        # Aun asi, warn si vemos reverb(decay > 6) — comportamiento original
        # tipico es decay 2-4s.
        m = re.search(r'reverb\([^)]*decay\s*=\s*(\d+(?:\.\d+)?)', line)
        if m:
            decay = float(m.group(1))
            if decay > 6.0:
                warnings.append(
                    f'  [T_REVERB_DECAY] {os.path.relpath(path, PROJECT_ROOT)}:{i}\n'
                    f'    reverb(decay={decay}) > 6 — verificar que no produzca smearing/wow\n'
                    f'    (fix aplicado en effects.py para decay > 4, pero decay > 6 sigue siendo cola larga)\n'
                    f'    > {stripped}'
                )

    return errors, warnings


def main():
    themes_root = os.path.join(PROJECT_ROOT, 'transmissions')
    if not os.path.exists(themes_root):
        print(f'ERROR: no existe {themes_root}', file=sys.stderr)
        sys.exit(3)

    all_errors = []
    all_warnings = []
    files_scanned = 0

    for tx in sorted(os.listdir(themes_root)):
        themes_dir = os.path.join(themes_root, tx, 'themes')
        if not os.path.isdir(themes_dir):
            continue
        for theme in sorted(os.listdir(themes_dir)):
            compose = os.path.join(themes_dir, theme, 'compose_full.py')
            if not os.path.exists(compose):
                # Intentar compose.py (otros nombres)
                alt = os.path.join(themes_dir, theme, 'compose.py')
                if os.path.exists(alt):
                    compose = alt
                else:
                    continue
            files_scanned += 1
            errors, warnings = scan_file(compose)
            all_errors.extend(errors)
            all_warnings.extend(warnings)

    print(f'=== QA scan code (T_NOISE_FRITURA) — {files_scanned} archivos ===')
    if all_errors:
        print(f'\nBLOQUEANTES ({len(all_errors)}):')
        for e in all_errors:
            print(e)
    if all_warnings:
        print(f'\nWARNINGS ({len(all_warnings)}):')
        for w in all_warnings:
            print(w)
    if not all_errors and not all_warnings:
        print('OK — ningun pattern T_NOISE_FRITURA detectado')

    if all_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
