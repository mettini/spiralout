"""Motifs: patrones musicales recurrentes del lore AEM (leitmotivs).

A diferencia de instruments.py (sound generators basicos: sine, melody,
drone) y de themes/ (composiciones completas), motifs.py contiene
PATRONES MUSICALES FIJOS reutilizables entre transmisiones. Cada motif
representa una idea del proyecto.

VOYAGER MOTIF: D5-F5-A5-F5-D5-A4-D5 (D menor pentatonica).
Representa "el primer mensaje humano enviado al cosmos" en el lore.
Es el sonido principal del proyecto.
"""

import numpy as np

from .core import SR
from .instruments import melody
from .effects import fade, lpf, notch_eq


# ---------------------------------------------------------------------------
# Voyager motif — notas y variantes
# ---------------------------------------------------------------------------

# Principal: D5-F5-A5-F5-D5-A4-D5 (12 segundos total)
VOYAGER_NOTES = [
    (587.33, 1.5),  # D5
    (698.46, 1.0),  # F5
    (880.00, 1.5),  # A5
    (698.46, 1.0),  # F5
    (587.33, 2.0),  # D5
    (440.00, 2.0),  # A4
    (587.33, 3.0),  # D5
]

# Inverted: D-A-F-A-D-F-A (re-ordenado, mismo set de notas)
VOYAGER_INVERTED = [
    (587.33, 1.0),
    (440.00, 1.0),
    (698.46, 1.5),
    (440.00, 1.0),
    (587.33, 1.5),
    (698.46, 1.5),
    (880.00, 2.5),
]

# Staccato: mismas notas, duraciones cortas (variante ritmica)
VOYAGER_STACCATO = [
    (587.33, 0.6), (698.46, 0.5), (880.00, 0.6), (698.46, 0.5),
    (587.33, 0.8), (440.00, 0.8), (587.33, 1.5),
]

# Ascending: la 4ta nota sube a C6, despues escalon intermedio en A5
# (parte de Dm7, no disona) y baja a D5. Duraciones homogeneas con el
# motivo principal: notas largas (1.5s) para las "cumbres" y notas
# medias (1.0s) para los pasos. Total 13s (1s mas que main).
VOYAGER_ASCENDING = [
    (587.33, 1.5),   # D5
    (698.46, 1.0),   # F5
    (880.00, 1.0),   # A5 (acortada para que la C6 entre antes)
    (1046.50, 1.5),  # C6 — cumbre del ascenso
    (880.00, 1.0),   # A5 — escalon intermedio
    (587.33, 1.5),   # D5
    (440.00, 1.5),   # A4 (acortada de 2.0 a 1.5 — D5 final entra antes)
    (587.33, 3.0),   # D5
]

# =====================================================================
# VOYAGER_NOTES_TIGHT — PATRON RITMICO FIJO (7 notas) — VALIDADO USER 2026-05-10
# =====================================================================
# DURACIONES LITERALES (no son espacios calculados): 1.7, 1.0, 1.7, 1.0, 1.7, 1.0, 1.7
# CRITICO: NO modificar sin confirmacion explicita del user.
# Es el unico motivo del voyager. ASCENDING_TIGHT fue removido (era 8 notas con C6).
VOYAGER_NOTES_TIGHT = [
    (587.33, 1.7),  # D5
    (698.46, 1.0),  # F5
    (880.00, 1.7),  # A5
    (698.46, 1.0),  # F5
    (587.33, 1.7),  # D5
    (440.00, 1.0),  # A4
    (587.33, 1.7),  # D5 final
]

# VOYAGER_ASCENDING_TIGHT REMOVIDO 2026-05-10 — el user pidio motivo de 7 notas
# (sin C6). Todos los voyagers (left, right, counter) usan VOYAGER_NOTES_TIGHT.

# =====================================================================
# VOYAGER_ASCENDING_TIGHT — 8 notas, C6 cumbre en pos 4 — VALIDADO USER 2026-05-10 v4
# =====================================================================
# DURACIONES LITERALES: 1.0, 1.7, 1.0, 1.7, 1.0, 1.7, 1.0, 1.7 (alternancia perfecta)
# Para voyager_right (diferencia melodica vs voyager_left que usa main_tight).
VOYAGER_ASCENDING_TIGHT = [
    (587.33, 1.0),   # D5
    (698.46, 1.7),   # F5
    (880.00, 1.0),   # A5
    (1046.50, 1.7),  # C6 cumbre (4ta — la que sube vs main_tight)
    (880.00, 1.0),   # A5
    (587.33, 1.7),   # D5
    (440.00, 1.0),   # A4
    (587.33, 1.7),   # D5 final
]

VARIATIONS = {
    'main': VOYAGER_NOTES,
    'main_tight': VOYAGER_NOTES_TIGHT,
    'inverted': VOYAGER_INVERTED,
    'staccato': VOYAGER_STACCATO,
    'ascending': VOYAGER_ASCENDING,
    'ascending_tight': VOYAGER_ASCENDING_TIGHT,   # 8 notas con C6, para voyager_right
    'fragment_open': VOYAGER_NOTES[:3],
    'fragment_close': VOYAGER_NOTES[-3:],
}


def voyager_motif(variation='main', amp=0.5, octave_shift=0,
                  vibrato=True, crossfade=0.0, waveform='sine',
                  attack=0.05, release=0.1, release_curve=1.0,
                  breath_amount=0.0,
                  fade_in=0.1, fade_out=0.5):
    """Genera el motivo Voyager.

    Args:
        variation: 'main' | 'inverted' | 'staccato' | 'counter' (5ta arriba) |
                   'fragment_open' (primeras 3 notas) | 'fragment_close' (ultimas 3)
        amp: amplitud (0.0 - 1.0). Empezar bajo (0.3-0.5) y subir.
        octave_shift: 1 = octava arriba, -1 = octava abajo, 0 = original.
        vibrato: aplicar vibrato suave 5 Hz.
        crossfade: segundos de overlap entre notas consecutivas (default 0).
            0.1-0.3 = legato natural, sin necesitar reverb para "respirar".
        fade_in: segundos de fade in (default 0.1, evita click al arranque).
        fade_out: segundos de fade out (default 0.5, evita corte abrupto).

    Returns:
        1D numpy array (mono). Para estereo paneado, envolver en Track(pan=...).
    """
    if variation == 'counter':
        # 5ta arriba (multiplicar freq por 1.5)
        notes = [(f * 1.5, d) for f, d in VOYAGER_NOTES]
    elif variation in VARIATIONS:
        notes = VARIATIONS[variation]
    else:
        valid = list(VARIATIONS.keys()) + ['counter']
        raise ValueError(f'variation must be one of {valid}, got {variation!r}')

    if octave_shift != 0:
        factor = 2 ** octave_shift
        notes = [(f * factor, d) for f, d in notes]

    audio = melody(notes, amp=amp, vibrato=vibrato, crossfade=crossfade,
                   waveform=waveform, attack=attack, release=release,
                   release_curve=release_curve, breath_amount=breath_amount)
    return fade(audio, fi=fade_in, fo=fade_out)


# ---------------------------------------------------------------------------
# VOYAGER SAFE — version protegida (benchmark = transmissions/01/themes/voyager_tool)
# ---------------------------------------------------------------------------
#
# IMPORTANTE: NO modificar estos defaults sin confirmacion explicita del user.
# El voyager es el alma del album. Cambios silenciosos lo aturden y rompen
# la identidad. Ver memory/voyager_protegido.md.
#
# Origen de los notches: triangle wave tiene SOLO armonicos impares. Las
# fundamentales del motif son D5 (587), F5 (698), A5 (880), C6 (1046).
# Sus 3er armonicos caen en zona Fletcher-Munson 1.5-3 kHz:
#   D5 * 3 = 1761 Hz   (notch 1760)
#   F5 * 3 = 2094 Hz   (notch 2093)
#   A5 fundamental     (notch 880)  — A5 fundamental tambien aturde si pasa libre
#   C6 fundamental     (notch 1046) — variation ascending tiene C6
# Sin estos 4 notches: punzante = "aturde" perceptual.
#
# LPF 2200: corta 5to+ armonicos triangle (D5 5th = 2935, F5 5th = 3490,
# A5 5th = 4400, etc) que tambien generan brillo punzante.

VOYAGER_NOTCH_FREQS = [
    (880.00,  'A5 fundamental'),
    (1046.50, 'C6 fundamental (variation ascending)'),
    (1760.00, '3rd harmonic of D5 (587 * 3)'),
    (2093.00, '3rd harmonic of F5 (698 * 3)'),
]
VOYAGER_LPF_CUTOFF = 2200            # corta 5to+ armonicos triangle
VOYAGER_DEFAULT_AMP = 0.40           # validado en voyager_tool (NO subir sin user)
VOYAGER_DEFAULT_RELEASE = 0.6        # validado en voyager_tool
VOYAGER_DEFAULT_WAVEFORM = 'triangle' # identidad sonora del album


def voyager_safe(amp=VOYAGER_DEFAULT_AMP, variation='main', subset=None,
                 octave_shift=0, vibrato=True,
                 release=VOYAGER_DEFAULT_RELEASE, waveform=VOYAGER_DEFAULT_WAVEFORM):
    """Genera el wave del voyager con params VALIDADOS del benchmark TOOL.

    Para que suene "safe" (no aturda), DEBE combinarse con voyager_safe_fx()
    aplicado al track despues de agregar todos los eventos:

        voy = comp.add_track(Track('voyager_x', gain=0.55, pan=0))
        voy.add(t, voyager_safe(amp=0.40, variation='ascending'))
        voyager_safe_fx(voy)                                  # <-- OBLIGATORIO
        voy.fx(lambda a: reverb(a, decay=4.5, mix=0.5))       # <-- al gusto

    Args:
      amp: amplitud (default 0.40 — validado TOOL, NO subir sin confirmacion user)
      variation: 'main' | 'inverted' | 'staccato' | 'counter' | 'ascending' |
                 'fragment_open' | 'fragment_close'
      subset: lista de (freq_hz, dur_sec) para fragmentos custom
      octave_shift: 1 = octava arriba, -1 = octava abajo
      vibrato: vibrato 5 Hz (default True)
      release: cola de cada nota (default 0.6 — validado TOOL)
      waveform: triangle por default (identidad del album)

    Returns:
      1D numpy array (mono).
    """
    if subset is not None:
        # Subset: usa melody directo con waveform y release del TOOL
        return melody(subset, amp=amp, vibrato=vibrato, waveform=waveform,
                      release=release, release_curve=1.0)
    return voyager_motif(variation=variation, amp=amp, waveform=waveform,
                          release=release, release_curve=1.0,
                          octave_shift=octave_shift, vibrato=vibrato)


def voyager_safe_fx(track):
    """Aplica al track los 4 notches + LPF 2200 del benchmark TOOL.

    Llamar DESPUES de agregar todos los eventos del voyager y ANTES del
    reverb/efectos finales. Garantiza que el track no aturda por armonicos
    altos del triangle wave.

    Sirve para CUALQUIER track que use voyager_safe(), independientemente de
    la variation: los 4 notches + LPF cubren D5/F5/A5/C6 y sus 3er-5to
    armonicos.

    NO modificar las freqs sin user — son las del Voyager TOOL benchmark.
    """
    for freq, _label in VOYAGER_NOTCH_FREQS:
        track.fx(lambda a, f=freq: notch_eq(a, freq_hz=f, q=10, gain_db=-12))
    track.fx(lambda a: lpf(a, VOYAGER_LPF_CUTOFF))


def voyager_duration(variation='main'):
    """Devuelve la duracion en segundos del motif sin fades."""
    if variation == 'counter':
        notes = VOYAGER_NOTES
    elif variation in VARIATIONS:
        notes = VARIATIONS[variation]
    else:
        raise ValueError(f'variation invalida: {variation!r}')
    return sum(d for _, d in notes)
