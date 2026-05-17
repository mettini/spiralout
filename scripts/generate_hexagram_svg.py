"""Genera el SVG del hexagrama 24 (Fù / Return / 復) en pixel art real
para el proyecto ÆM.

Diferencias con la version anterior:
- Pixels VISIBLES con mini gap entre cada uno (1px de gap entre celdas
  de 8px) — se ve la trama pixelada como en el arte de tapa.
- Proporciones del hexagrama mas compactas — gap entre lineas mas chico
  que en la version previa (2 grid units en vez de 1:1 con la altura).
- SIN texto en el SVG. Solo el simbolo. El texto va en HTML aparte
  (con la font VT323 — ver html/hexagram_lockup.html).
- Variantes: logo (transparente) + logo dark (con bg).

El hexagrama 24 se LEE DE ABAJO HACIA ARRIBA en el I Ching:
  6 ┃ ┃   yin
  5 ┃ ┃   yin
  4 ┃ ┃   yin
  3 ┃ ┃   yin
  2 ┃ ┃   yin
  1 ━━━   yang  ← la linea que vuelve

Salida en transmissions/01/artwork/hexagram/:
  hexagram_24_logo.svg          simbolo solo (transparente, 1024x1024)
  hexagram_24_logo_dark.svg     simbolo + fondo dark
"""

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(PROJECT_ROOT, 'transmissions', '01', 'artwork', 'hexagram')
os.makedirs(OUT_DIR, exist_ok=True)

PHOSPHOR = '#a6d65f'
BG_DARK = '#0d1014'

# ============================================================================
# Grid setup — todo se calcula en "celdas" (unidades de pixel en el grid)
# y despues se mapea a pixeles SVG.
# ============================================================================

PX = 8                  # tamano del cuadradito pixel (px en SVG)
GAP = 1                 # mini margen entre cuadraditos (px en SVG)
CELL = PX + GAP         # tamano efectivo de cada celda

# Hexagrama: 6 lineas. Cada linea ocupa GRID_LINE_H celdas verticales,
# separadas por GRID_GAP celdas verticales.
GRID_LINE_H = 3         # altura de cada linea = 3 celdas (3 pixels)
GRID_GAP = 2            # gap vertical entre lineas = 2 celdas
GRID_LINE_W = 32        # ancho de cada linea entera (yang) = 32 celdas
GRID_YIN_GAP = 6        # gap del medio en lineas yin = 6 celdas
GRID_YIN_HALF = (GRID_LINE_W - GRID_YIN_GAP) // 2  # 13 celdas por mitad


def cell_to_px(c):
    return c * CELL


def line_yin(x0, y0):
    """Devuelve lista de cuadraditos para una linea yin (rota)."""
    rects = []
    for cy in range(GRID_LINE_H):
        for cx in range(GRID_YIN_HALF):
            rects.append((x0 + cell_to_px(cx), y0 + cell_to_px(cy)))
        x_right = x0 + cell_to_px(GRID_YIN_HALF + GRID_YIN_GAP)
        for cx in range(GRID_YIN_HALF):
            rects.append((x_right + cell_to_px(cx), y0 + cell_to_px(cy)))
    return rects


def line_yang(x0, y0):
    """Devuelve lista de cuadraditos para una linea yang (entera)."""
    rects = []
    for cy in range(GRID_LINE_H):
        for cx in range(GRID_LINE_W):
            rects.append((x0 + cell_to_px(cx), y0 + cell_to_px(cy)))
    return rects


def build_hexagram(cx_px, cy_px):
    """Construye los 6 lineas del hexagrama 24 centradas en (cx_px, cy_px).
    5 yin arriba, 1 yang abajo. Devuelve lista de (x, y) de cuadraditos."""
    # Tamano total del hexagrama en celdas
    total_w_cells = GRID_LINE_W
    total_h_cells = 6 * GRID_LINE_H + 5 * GRID_GAP

    # Origen (top-left) del hexagrama en pixeles
    x0 = cx_px - cell_to_px(total_w_cells) / 2
    y0 = cy_px - cell_to_px(total_h_cells) / 2

    rects = []
    # 5 lineas yin (arriba)
    for i in range(5):
        y = y0 + cell_to_px(i * (GRID_LINE_H + GRID_GAP))
        rects.extend(line_yin(x0, y))
    # 1 linea yang (abajo)
    y_yang = y0 + cell_to_px(5 * (GRID_LINE_H + GRID_GAP))
    rects.extend(line_yang(x0, y_yang))

    return rects


def rects_to_svg(rects, color):
    return '\n'.join(
        f'  <rect x="{x}" y="{y}" width="{PX}" height="{PX}" fill="{color}"/>'
        for (x, y) in rects
    )


def write_svg(filename, content, viewbox, bg=None):
    bg_rect = f'  <rect width="100%" height="100%" fill="{bg}"/>\n' if bg else ''
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" '
        f'shape-rendering="crispEdges">\n'
        f'{bg_rect}'
        f'{content}\n'
        f'</svg>\n'
    )
    path = os.path.join(OUT_DIR, filename)
    with open(path, 'w') as f:
        f.write(svg)
    print(f'  wrote {path}')


# ============================================================================
# Genera SVGs (1024x1024 viewBox cuadrado para que sea fácil escalable)
# ============================================================================

VIEW = 1024
content = rects_to_svg(build_hexagram(VIEW / 2, VIEW / 2), PHOSPHOR)

write_svg('hexagram_24_logo.svg', content,
          viewbox=f'0 0 {VIEW} {VIEW}')

write_svg('hexagram_24_logo_dark.svg', content,
          viewbox=f'0 0 {VIEW} {VIEW}', bg=BG_DARK)

# Tambien una version mas chica (256x256) para favicons / icons
content_small = rects_to_svg(build_hexagram(256 / 2, 256 / 2), PHOSPHOR)
# Reescalando: para 256 necesito redefinir PX y GAP — pero simplificar
# usando preserveAspectRatio. Mejor: dejar el viewBox de 1024 y que
# el browser/usuario escale via width/height.

# El SVG es vectorial — escala a cualquier tamano. No hace falta version
# small. Usar el mismo logo.svg y setear width/height.

print('\nGenerado en', OUT_DIR)
print(f'Pixels: {PX}x{PX} px, gap {GAP} px entre cuadraditos')
print(f'Hexagrama: {6 * GRID_LINE_H + 5 * GRID_GAP} celdas alto x '
      f'{GRID_LINE_W} celdas ancho')
