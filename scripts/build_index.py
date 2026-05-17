"""Reconstruye <transmission>/out/index.json escaneando los stems disponibles.

Uso:
    python3 scripts/build_index.py [<transmission_dir>]

Default: transmissions/01
"""

import glob
import json
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def label_for(comp_id, manifest):
    name = manifest.get('name') or comp_id
    dur = manifest.get('duration', 0)
    mins = int(dur // 60)
    secs = int(dur % 60)
    return f'{name}  ({mins}:{secs:02d})'


def main():
    tx_dir = sys.argv[1] if len(sys.argv) > 1 else 'transmissions/01'
    tx_path = os.path.join(PROJECT_ROOT, tx_dir)
    out_dir = os.path.join(tx_path, 'out')
    index_path = os.path.join(out_dir, 'index.json')

    if not os.path.isdir(out_dir):
        print(f'ERROR: {out_dir} no existe', file=sys.stderr)
        sys.exit(1)

    pattern = os.path.join(out_dir, '*', 'stems', '*', 'manifest.json')
    entries = []
    for manifest_path in sorted(glob.glob(pattern)):
        rel = os.path.relpath(manifest_path, out_dir)
        # rel = 'outbound/stems/outbound_FULL/manifest.json'
        parts = rel.split(os.sep)
        if len(parts) < 4:
            continue
        tema, _stems, comp_id, _manifest = parts[0], parts[1], parts[2], parts[3]
        with open(manifest_path) as f:
            manifest = json.load(f)
        master_rel = os.path.join(tema, 'master', f'{comp_id}.wav')
        master_exists = os.path.exists(os.path.join(out_dir, master_rel))
        entries.append({
            'id': comp_id,
            'label': label_for(comp_id, manifest),
            'manifest': os.path.join(tema, 'stems', comp_id, 'manifest.json'),
            'stems_dir': os.path.join(tema, 'stems', comp_id),
            'master': master_rel if master_exists else None,
        })

    # ordenar por tema en orden NARRATIVO del EP (no alfabetico),
    # luego dentro del tema: full primero, despues v0..vN, despues otros
    THEME_ORDER = {'outbound': 0, 'crossing': 1, 'recursion': 2, 'maquetas': 9}

    def sort_key(e):
        eid = e['id']
        tema = e['stems_dir'].split(os.sep)[0]
        tema_order = THEME_ORDER.get(tema, 5)
        # Master arriba, despues continuous, despues full, despues prototypes
        if eid.endswith('_MASTER') or eid.endswith('_CONTINUOUS'):
            sub = (0, eid)
        elif eid.endswith('_FULL'):
            sub = (1, eid)
        else:
            m = re.search(r'_v(\d+)$', eid)
            sub = (2, int(m.group(1))) if m else (3, eid)
        return (tema_order, sub)
    entries.sort(key=sort_key)

    out = {
        'transmission': os.path.basename(tx_path),
        'compositions': entries,
    }
    with open(index_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'wrote {index_path} with {len(entries)} composition(s):')
    for e in entries:
        print(f'  {e["id"]:30s} {e["label"]}')


if __name__ == '__main__':
    main()
