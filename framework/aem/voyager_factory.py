"""Voyager Factory — abstracción plug-and-play del voyager con presets.

Uso:
    from aem.voyager_factory import voyager_track

    voy = voyager_track(comp, 'voyager_left', preset='roach_octlow',
                         pan=+0.4, base_gain=0.55, events=[
        (90, {'amp': 0.35}),
        (115, {'amp': 0.30, 'variation': 'ascending'}),
    ])

Cambiar el preset = cambiar el sonido del voyager en TODO el album sin tocar las
composiciones. Cada preset es un perfil completo (instrumento, octave_shift,
notches, LPF, reverb, layers extras).

PRESETS DEFINIDOS:
  - roach_octlow   : main octava abajo + up octava normal (brillo) + dn 2 oct abajo
                     + drone + tremolo + reverb plate gigante. VALIDADO POR USER.
  - tool_classic   : main + 3 delays escalonados (250/500/750 ms) + bass + drone.
  - flute_warm     : flute_traversa con espectro calido + bass + drone.
  - safe_basic     : voyager_safe simple (triangle + 4 notches + LPF 2200 + reverb).
"""

import numpy as np

from .core import SR
from .effects import lpf, notch_eq, reverb, fade as _fade, lfo_amp, distort
from .instruments import melody, detuned_drone, flute_motif
from .motifs import (voyager_motif, voyager_safe_fx, VARIATIONS, VOYAGER_NOTES,
                       VOYAGER_NOTES_TIGHT, VOYAGER_NOTCH_FREQS)
from .composition import Composition, Track


# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------
#
# Cada preset es un dict que define como construir el voyager:
#   layers: lista de capas (cada una es un track con su instrumento, octave,
#           amp, fx). El primer layer es el "principal".
#   companion: dict opcional con bass + drone (formula anti-aturde TOOL)
#
# Las layers se construyen con _build_layer().

PRESETS = {

    # === ROACH OCTAVE LOW (validado en lab por user) ===
    # main detuned octava abajo (-1) + up octava normal (capa de brillo, gain bajo,
    # pan -0.3) + dn dos octavas abajo (-2) + drone D2 detuned + tremolo lento +
    # reverb plate gigante (decay 7s pre-delay 100ms)
    'roach_octlow': {
        'description': 'Roach config con octava abajo — VALIDADO USER. Main -1.',
        'tempo_mult': 1.4,        # multiplica duraciones del motivo — mas espacio entre notas, "que suene cada nota"
        'event_fade_in': 0.5,
        'event_fade_out': 0.6,
        'layers': [
            {  # main: cuerpo principal
                'name_suffix': '',
                'instrument': 'triangle_detuned',
                'octave_shift': -1,
                'detune_cents': 0,
                'amp_default': 0.35,
                'pan_offset': 0.0,
                'gain_mult': 1.0,
                'attack': 0.2,
                'release': 0.6,
                'apply_4_notches': True,
                'extra_notches': [],
                'reverb': (4.5, 0.45, 0),    # SIN pre_delay (100ms generaba "doble" desfasado)
                # SIN tremolo: con 1 sola layer, modulacion lenta confunde
                # 'tremolo_rate': 0.15,
                # 'tremolo_depth': 0.15,
            },
            # SACADO brightness_up (oct 0) — generaba TIC en cambios de nota
            # (2 layers cambiando D5→F5 al mismo sample = transient compuesto).
            # Con time_offset 40ms se sentia "desincronizado" perceptualmente.
            # Volvemos a 1 sola layer (main octava abajo) — el v4 puro validado.
        ],
        'drone': {
            'freq': 73.42, 'amp': 0.35, 'n_voices': 3, 'detune_cents': 8,
            'gain': 0.20, 'reverb': (6.0, 0.4, 100),
        },
    },

    # === TOOL CLASSIC ===
    # main + 3 delays escalonados (estilo Adam Jones) + bass + drone D2
    'tool_classic': {
        'description': 'TOOL classic: main + 3 delays + bass + drone',
        'layers': [
            {
                'name_suffix': '',
                'instrument': 'triangle',
                'octave_shift': 0,
                'amp_default': 0.40,
                'pan_offset': 0.0,
                'gain_mult': 1.0,
                'attack': 0.05,
                'release': 0.6,
                'apply_4_notches': True,
                'reverb': (3.5, 0.40, 0),
            },
            {
                'name_suffix': '_delay_L_250',
                'instrument': 'triangle',
                'octave_shift': 0,
                'amp_default': 0.40,
                'pan_offset': -0.6,
                'gain_mult': 0.55,
                'time_offset': 0.250,
                'attack': 0.05, 'release': 0.6,
                'apply_4_notches': True,
                'reverb': (3.5, 0.40, 0),
            },
            {
                'name_suffix': '_delay_R_500',
                'instrument': 'triangle',
                'octave_shift': 0,
                'amp_default': 0.40,
                'pan_offset': +0.6,
                'gain_mult': 0.36,
                'time_offset': 0.500,
                'attack': 0.05, 'release': 0.6,
                'apply_4_notches': True,
                'reverb': (3.5, 0.40, 0),
            },
        ],
        'drone': {
            'freq': 73.42, 'amp': 0.40, 'n_voices': 1, 'detune_cents': 0,
            'gain': 0.10, 'reverb': (5.0, 0.4, 0),
        },
    },

    # === FLUTE WARM ===
    'flute_warm': {
        'description': 'Flauta traversa calida con bass + drone',
        'layers': [
            {
                'name_suffix': '',
                'instrument': 'flute_traversa',
                'octave_shift': 0,
                'amp_default': 0.40,
                'pan_offset': 0.0,
                'gain_mult': 1.0,
                'reverb': (3.5, 0.40, 0),
            },
        ],
        'bass_octave_shift': -1,
        'bass_gain': 0.45,
        'drone': {
            'freq': 73.42, 'amp': 0.40, 'n_voices': 1, 'detune_cents': 0,
            'gain': 0.10, 'reverb': (5.0, 0.4, 0),
        },
    },

    # === SAFE BASIC (el voyager_safe que ya teniamos) ===
    'safe_basic': {
        'description': 'voyager_safe simple (triangle + 4 notches + LPF 2200 + reverb)',
        'layers': [
            {
                'name_suffix': '',
                'instrument': 'triangle',
                'octave_shift': 0,
                'amp_default': 0.40,
                'pan_offset': 0.0,
                'gain_mult': 1.0,
                'attack': 0.05, 'release': 0.6,
                'apply_4_notches': True,
                'apply_lpf': 2200,
                'reverb': (4.5, 0.5, 0),
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def voyager_track(comp, name, preset='roach_octlow', pan=0.0, base_gain=0.55,
                   events=None, color=None, with_companion=True):
    """Crea un voyager con el preset especificado.

    Args:
      comp: Composition.
      name: nombre base. Los layers extras agregan sufijo.
      preset: clave en PRESETS.
      pan: paneo principal del voyager.
      base_gain: gain del track principal (los layers extras se escalan con gain_mult).
      events: lista de (t, params_dict). params puede tener 'amp', 'variation',
              'subset', 'octave_offset' (override del octave_shift del layer).
      color: color para Track().
      with_companion: si True, agrega bass + drone si el preset los define.

    Returns:
      el Track principal (primer layer).
    """
    if events is None:
        events = []
    if preset not in PRESETS:
        raise ValueError(f'preset desconocido: {preset!r}. Disponibles: {list(PRESETS.keys())}')
    cfg = PRESETS[preset]

    event_fade_in = cfg.get('event_fade_in', 0.0)
    event_fade_out = cfg.get('event_fade_out', 0.0)
    tempo_mult = cfg.get('tempo_mult', 1.0)
    main_track = None
    for i, layer_cfg in enumerate(cfg['layers']):
        layer_name = name + layer_cfg.get('name_suffix', '')
        layer_pan = max(-1.0, min(1.0, pan + layer_cfg.get('pan_offset', 0.0)))
        layer_gain = base_gain * layer_cfg.get('gain_mult', 1.0)
        track = _build_layer(comp, layer_name, layer_cfg, layer_pan, layer_gain,
                              events, color, event_fade_in, event_fade_out, tempo_mult)
        if i == 0:
            main_track = track

    # Companion: bass + drone (si aplica)
    if with_companion:
        if 'drone' in cfg:
            _add_drone(comp, cfg['drone'], comp.duration)
        if 'bass_octave_shift' in cfg and events:
            _add_bass(comp, cfg, events)

    return main_track


def list_presets():
    """Devuelve dict {nombre: descripcion} de presets disponibles."""
    return {k: v.get('description', '') for k, v in PRESETS.items()}


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _build_layer(comp, layer_name, layer_cfg, pan, gain, events, color,
                  event_fade_in=0.0, event_fade_out=0.0, tempo_mult=1.0):
    track_kwargs = {'gain': gain, 'pan': pan}
    if color:
        track_kwargs['color'] = color
    track = comp.add_track(Track(layer_name, **track_kwargs))

    instrument = layer_cfg.get('instrument', 'triangle')
    octave_shift_layer = layer_cfg.get('octave_shift', 0)
    detune_cents = layer_cfg.get('detune_cents', 0)
    attack = layer_cfg.get('attack', 0.05)
    release = layer_cfg.get('release', 0.6)
    time_offset = layer_cfg.get('time_offset', 0.0)

    for t, override in events:
        amp = override.get('amp', layer_cfg.get('amp_default', 0.40))
        variation = override.get('variation', 'main')
        subset = override.get('subset', None)
        oct_extra = override.get('octave_offset', 0)
        oct_total = octave_shift_layer + oct_extra
        # Override fade_in/out por evento si se especifica
        ev_fi = override.get('fade_in', event_fade_in)
        ev_fo = override.get('fade_out', event_fade_out)

        wave = _generate_wave(instrument, variation, subset, amp, oct_total,
                                attack, release, detune_cents, tempo_mult)
        # Anti-TIC: aplicar fade al wave (suaviza entrada/salida del evento)
        if ev_fi > 0 or ev_fo > 0:
            wave = _fade(wave, fi=ev_fi, fo=ev_fo)
        track.add(t + time_offset, wave)

    # Notches del voyager_safe (4 notches del benchmark TOOL)
    if layer_cfg.get('apply_4_notches'):
        for freq, _label in VOYAGER_NOTCH_FREQS:
            track.fx(lambda a, f=freq: notch_eq(a, freq_hz=f, q=10, gain_db=-12))
    # Notches extras (ej. 3520 para layers altos)
    for freq, gain_db in layer_cfg.get('extra_notches', []):
        track.fx(lambda a, f=freq, g=gain_db: notch_eq(a, freq_hz=f, q=10, gain_db=g))
    # LPF opcional
    apply_lpf = layer_cfg.get('apply_lpf')
    if apply_lpf:
        track.fx(lambda a, c=apply_lpf: lpf(a, c))
    # Distort opcional
    if layer_cfg.get('distort'):
        d_amount = layer_cfg['distort']
        track.fx(lambda a, am=d_amount: distort(a, amount=am))
    # Reverb
    if 'reverb' in layer_cfg:
        decay, mix, pre = layer_cfg['reverb']
        if pre > 0:
            track.fx(lambda a, d=decay, m=mix, p=pre: reverb(a, decay=d, mix=m, pre_delay_ms=p))
        else:
            track.fx(lambda a, d=decay, m=mix: reverb(a, decay=d, mix=m))
    # Tremolo (LFO amp)
    tremolo_rate = layer_cfg.get('tremolo_rate')
    if tremolo_rate:
        depth = layer_cfg.get('tremolo_depth', 0.15)
        track.fx(lambda a, r=tremolo_rate, d=depth: lfo_amp(a, rate_hz=r, depth=d))

    return track


def _generate_wave(instrument, variation, subset, amp, octave_shift, attack,
                    release, detune_cents, tempo_mult=1.0):
    """Genera el array audio segun el instrumento y la variacion.
    tempo_mult escala las duraciones de cada nota (>1 = mas lento, mas espacio)."""
    factor = (2 ** octave_shift) * (2 ** (detune_cents / 1200))

    # Determinar las notas (aplicando tempo_mult a las duraciones)
    if subset is not None:
        notes = [(f * factor, d * tempo_mult) for f, d in subset]
    elif variation == 'counter':
        # Counter usa VOYAGER_NOTES_TIGHT (no main) — las duraciones tight
        # mantienen espacios consistentes 1.7s en las ultimas notas (vs 2.4s
        # con main que se sentian espaciadas de mas).
        notes = [(f * 1.5 * factor, d * tempo_mult) for f, d in VOYAGER_NOTES_TIGHT]
    elif variation in VARIATIONS:
        notes = [(f * factor, d * tempo_mult) for f, d in VARIATIONS[variation]]
    else:
        raise ValueError(f'variation desconocida: {variation!r}')

    if instrument == 'flute_traversa':
        return flute_motif(notes, amp=amp, vibrato=True,
                              attack_ms=int(attack * 1000),
                              release_ms=int(release * 1000),
                              breath_amount=0.015, chiff_amount=0.04)

    # triangle / triangle_detuned: legato tipo "pedal de piano".
    # crossfade=0.4s + release_curve=1.5 = las notas se solapan generosamente
    # y la cola decae mas suave. El user reporto que sin esto las notas
    # "no estan interconectadas, como sin pedal del piano".
    return melody(notes, amp=amp, vibrato=True, waveform='triangle',
                    attack=attack, release=max(release, 0.9), release_curve=1.5,
                    crossfade=0.4)


def _add_drone(comp, drone_cfg, duration):
    """Agrega un track de drone segun el preset."""
    drone = comp.add_track(Track(f"_voyager_drone_{int(drone_cfg['freq'])}Hz",
                                    gain=drone_cfg['gain']))
    drone.add(0.5, detuned_drone([drone_cfg['freq']], duration - 1.0,
                                    amp=drone_cfg['amp'],
                                    n_voices=drone_cfg.get('n_voices', 1),
                                    detune_cents=drone_cfg.get('detune_cents', 0)))
    if 'reverb' in drone_cfg:
        decay, mix, pre = drone_cfg['reverb']
        if pre > 0:
            drone.fx(lambda a, d=decay, m=mix, p=pre: reverb(a, decay=d, mix=m, pre_delay_ms=p))
        else:
            drone.fx(lambda a, d=decay, m=mix: reverb(a, decay=d, mix=m))


def _add_bass(comp, cfg, events):
    """Agrega un bass que toca el motivo octava abajo (para presets que lo definen)."""
    octave_shift_bass = cfg.get('bass_octave_shift', -1)
    bass_gain = cfg.get('bass_gain', 0.45)
    bass = comp.add_track(Track('_voyager_bass', gain=bass_gain, pan=0.0))
    factor = 2 ** octave_shift_bass
    for t, override in events:
        amp = override.get('amp', 0.35)
        subset = override.get('subset', None)
        variation = override.get('variation', 'main')
        if subset:
            notes = [(f * factor, d) for f, d in subset]
        elif variation == 'counter':
            notes = [(f * 1.5 * factor, d) for f, d in VOYAGER_NOTES]
        else:
            notes = [(f * factor, d) for f, d in VARIATIONS.get(variation, VOYAGER_NOTES)]
        bass.add(t, melody(notes, amp=amp * 0.8, vibrato=False, waveform='sine',
                              release=0.8))
    bass.fx(lambda a: reverb(a, decay=2.5, mix=0.25))
