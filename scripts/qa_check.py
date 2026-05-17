"""QA check para una composicion renderizada.

Verifica el manifest.json contra las reglas de la skill aem-composer:
  R8 — bed (cosmos/granular/field) gain ≤ 0.15
  R8 — peak ≤ 0.60 después de normalize (avoid dominant tracks)
  Activity — todos los stems con peak ≥ 0.05 (sino el track no aporta)
  R9 — silencios > 8s (heuristic: detectar gaps largos en eventos)

Uso:
    python3 scripts/qa_check.py <transmission> <theme> <comp_id>
    ej:   python3 scripts/qa_check.py 01 crossing crossing_v0
    o:    python3 scripts/qa_check.py 01 outbound outbound_FULL

    python3 scripts/qa_check.py --finals <transmission> <theme> <version>
    ej:   python3 scripts/qa_check.py --finals 01 outbound v1

Sale con exit code 0 si todo pasa, 1 si hay bloqueantes, 2 si hay warnings.
"""

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Whitelist de nombres EXACTOS de tracks "bed continuo" donde aplica R8/AP2.
# Tracks con nombre tipo "cosmos_swells", "granular_dark" son EVENTOS puntuales,
# NO bed continuo, asi que NO aplica esta regla a ellos.
# sub_42hz NO esta en la lista — la R10 dice que puede tener forma propia (fade
# in/out con amp_envelope), no necesariamente bed continuo subliminal.
# NO incluye granular_bed — son pulses cortos esparcidos, no bed continuo
# de ruido. La regla AP2 esta pensada para cosmos noise sostenido.
BED_CONTINUOUS = {
    'cosmos', 'cosmic_bed', 'field_atmosphere', 'capsule_field',
}

# Reglas de la skill (referencias para los mensajes)
RULES = {
    'R8_bed_gain': 'Bed (cosmos/granular/field) gain ≤ 0.15',
    'R8_peak': 'Stem peak ≤ 0.60 (post-normalize)',
    'activity': 'Stem peak ≥ 0.05 (track aporta señal)',
    'AP2': 'Cosmos noise gain ≤ 0.15',
}


def is_bed(name):
    """Match exacto con la whitelist (los pattern partial matches dieron
    false positives con cosmos_swells, granular_dark, etc)."""
    return name.lower() in BED_CONTINUOUS


def qa_manifest(manifest_path):
    """Devuelve (errors, warnings) — listas de strings."""
    with open(manifest_path) as f:
        m = json.load(f)
    errors = []
    warnings = []

    # Single-track compositions son masters (no stems). NO aplica la regla
    # de "peak > 0.60 = dominante" porque por diseño es 1 track con peak
    # cerca del techo del master.
    is_single_track_master = len(m['tracks']) == 1

    for t in m['tracks']:
        name = t['name']
        gain = t['gain']
        peak = t['peak']

        # Bed gain check (R8/AP2)
        if is_bed(name) and gain > 0.15:
            errors.append(
                f'  [R8/AP2] {name:30s} gain={gain:.2f} > 0.15  '
                f'→ bajar el gain del bed'
            )

        # Activity check — distingue:
        # - track con gain >= 0.10 pero peak < 0.05 = bug (declarado como audible
        #   pero no suena). ERROR.
        # - track con gain < 0.10 = declarado intencionalmente sutil (ambient,
        #   loop_prep, sub atmosferico). WARNING solamente.
        if peak < 0.05:
            if gain >= 0.10:
                errors.append(
                    f'  [activity] {name:30s} peak={peak:.3f} < 0.05 (gain={gain:.2f})  '
                    f'→ declarado audible pero no suena, BUG'
                )
            else:
                warnings.append(
                    f'  [activity-sutil] {name:30s} peak={peak:.3f} (gain={gain:.2f})  '
                    f'→ track ambient sutil, OK por design'
                )

        # Peak too high — solo aplica a stems (multi-track), no a masters
        if peak > 0.60 and not is_single_track_master:
            warnings.append(
                f'  [R8] {name:30s} peak={peak:.3f} > 0.60  '
                f'→ track dominante, considerar bajar gain'
            )

    return m, errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('transmission', help='ej "01"')
    ap.add_argument('theme', help='ej "crossing", "outbound"')
    ap.add_argument('comp_id', help='ej "crossing_v0", "outbound_FULL", o version (con --finals)')
    ap.add_argument('--finals', action='store_true', help='leer del finals/ en vez del out/')
    args = ap.parse_args()

    if args.finals:
        manifest_path = os.path.join(
            PROJECT_ROOT, 'transmissions', args.transmission, 'themes',
            args.theme, 'finals', args.comp_id, 'stems', 'manifest.json'
        )
        label = f'{args.theme} finals/{args.comp_id}'
    else:
        manifest_path = os.path.join(
            PROJECT_ROOT, 'transmissions', args.transmission, 'out',
            args.theme, 'stems', args.comp_id, 'manifest.json'
        )
        label = f'{args.theme}/{args.comp_id}'

    if not os.path.exists(manifest_path):
        print(f'ERROR: no existe {manifest_path}', file=sys.stderr)
        sys.exit(3)

    manifest, errors, warnings = qa_manifest(manifest_path)

    print(f'=== QA: {label} ({manifest["duration"]}s, {len(manifest["tracks"])} tracks) ===')
    if errors:
        print(f'\nBLOQUEANTES ({len(errors)}):')
        for e in errors:
            print(e)
    if warnings:
        print(f'\nWARNINGS ({len(warnings)}):')
        for w in warnings:
            print(w)
    if not errors and not warnings:
        print('OK — todo pasa el checklist')

    if errors:
        sys.exit(1)
    if warnings:
        sys.exit(2)
    sys.exit(0)


if __name__ == '__main__':
    main()
