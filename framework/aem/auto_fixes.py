"""Auto-fixes structurales por-track aplicados pre-export.

Resuelve dos clases de problemas que aparecen en cualquier composicion ambient
del framework, sin tener que recordar agregar HPFs/tames track-por-track:

  1. Low-end stack (100-300 Hz) — drones + chants + voices_pad + pads + bells
     compiten por la misma banda. Mid_scoop del master no alcanza. Por-stem
     HPF en la fundamental util libera el rango.

  2. Sustain resonante (Fletcher-Munson 1.5-3 kHz) — bells y voyagers sostienen
     armonicos en banda donde el oido fatiga (cataratas/sinusitis perceptual).
     Single-band sustain compressor reduce solo el sustain, preserva ataques.

Uso:
    from aem.auto_fixes import apply_auto_fixes
    # ... construir comp con tracks ...
    apply_auto_fixes(comp)
    comp.export_wav(...)
"""

import numpy as np
from scipy.signal import lfilter

from .core import SR
from .effects import hpf, lpf


def tame_band_sustain(audio, lo_hz=450.0, hi_hz=1100.0,
                      threshold=0.012, smooth_ms=250.0, max_reduction_db=-10.0):
    """Single-band sustain compressor con bandpass zero-phase (filtfilt).

    Solo comprime energia SOSTENIDA en banda [lo_hz, hi_hz]. Ataques rapidos
    pasan limpios (envelope follower tarda smooth_ms en armarse).

    Funcionamiento:
      1. bandpass zero-phase de audio → "band"
      2. resto = audio - band
      3. envelope smoothed de band con TC=smooth_ms
      4. gain reduction proporcional cuando smoothed > threshold
      5. return rest + band * gain
    """
    if len(audio) == 0:
        return audio

    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, [lo_hz, hi_hz], btype='band', fs=SR, output='sos')
    band = sosfiltfilt(sos, audio)
    rest = audio - band

    env = np.abs(band)
    a = float(np.exp(-1.0 / (SR * smooth_ms / 1000.0)))
    smoothed = lfilter([1.0 - a], [1.0, -a], env)

    over = np.maximum(smoothed - threshold, 0.0)
    reduction_factor = np.clip(over / max(threshold, 1e-9), 0.0, 1.0)
    max_red_linear = 10.0 ** (max_reduction_db / 20.0)
    gain = 1.0 - (1.0 - max_red_linear) * reduction_factor

    return rest + band * gain


# --- Pattern matchers ---

def _is_bell_like(name):
    return any(k in name for k in [
        'bell', 'ping', 'magic', 'closure', 'ritual', 'chime',
    ])


def _is_sustained_pad(name):
    return any(k in name for k in [
        'intro_pad_high', 'voyager_swell', 'mellotron', 'departure',
        'tension_pad', 'peak_sustain', 'intro_pad',
    ])


def _is_voyager_like(name):
    return 'voyager' in name


def _is_sweep_track(name):
    return any(k in name for k in [
        'riser', 'downlifter', 'cue_release',
    ])


def _decide_hpf(name):
    """Devuelve HPF cutoff para el track segun pattern, o None si no aplica.

    Reglas (por pattern de track.name):
      sub_ / kick / heart / thump          → None (preservar rango sub)
      chant_d2 / chant_degraded            → 65   (fund D2=73)
      chant_a2                             → 90   (fund A2=110)
      chant_f2                             → 75   (fund F2=87)
      chant_glue                           → 65
      heart_soft_40bpm                     → 50
      voices_l_d4 / voices_preview         → 180  (fund D4=294)
      voices_r_a4                          → 220  (fund A4=440)
      reverse_voice                        → 180
      pads / swells (sin sub)              → 180
      bells / pings / magic / closure      → 250
      wall                                 → 90
      drones medios                        → 100
      voyager (no swell)                   → 200
      bassline                             → 45   (Bb1=58)
      wind / whoosh / passing / cues       → 100
      cosmos / field / atmosphere          → 60
      granular                             → 100
      glitches                             → 200
      vestige / distant / echo             → 150
    """
    if name.startswith('sub_'):
        return None
    if name in ('thump', 'capsule_thump', 'sub_pulses', 'broken_beat',
                'sub_punisher', 'sub_punisher_climax'):
        return None
    if 'heart' in name and 'soft' not in name:
        return None
    if 'kick' in name or 'thump' in name:
        return None

    if 'chant_d2' in name or name == 'chant_degraded':
        return 65
    if 'chant_a2' in name:
        return 90
    if 'chant_f2' in name:
        return 75
    if 'chant_glue' in name:
        return 65
    if name == 'heart_soft_40bpm':
        return 50

    if 'voices_l_d4' in name or 'voices_preview' in name:
        return 180
    if 'voices_r_a4' in name:
        return 220
    if 'reverse_voice' in name:
        return 180

    if any(k in name for k in [
        'intro_pad', 'voyager_swell', 'tension_pad', 'peak_sustain',
        'mellotron', 'departure', 'shimmer', 'drone_shimmer',
    ]):
        return 180

    if any(k in name for k in ['bell', 'ping', 'magic', 'closure', 'ritual']):
        return 250

    if 'wall' in name:
        return 90

    if name.startswith('drone_') and 'sub' not in name:
        return 100
    if 'drone_dm_cluster' in name or 'drone_bb_dark' in name:
        return 100
    if 'drone_dark' in name or 'drone_clean' in name:
        return 100

    if 'voyager' in name and 'swell' not in name:
        return 200

    if name == 'bassline':
        return 45

    if any(k in name for k in [
        'wind', 'whoosh', 'reverse_swell', 'riser', 'downlifter',
        'passing', 'cosmos_swell', 'cue_release', 'cosmic',
    ]):
        return 100

    if name == 'cosmos':
        return 60
    if 'field' in name or 'atmosphere' in name:
        return 60

    if 'granular' in name:
        return 100

    if 'glitch' in name:
        return 200

    if 'vestige' in name or 'distant' in name or 'echo' in name:
        return 150

    return None


def apply_auto_fixes(comp, verbose=False):
    """Aplica fixes structurales a un Composition:

      1. HPF por-track segun pattern (libera low-end stack).
      2. Bell-like tracks: tame_band_sustain en banda fundamentales (520-950)
         y 2dos armonicos (1100-1850). Muy sutil (-1.5 dB max) para preservar
         timbre de las notas. SOLO controla resonancias sostenidas.
      3. Pads sostenidos (mellotron, intro_pad, etc): tame mas firme (-12 dB).
      4. Voyagers: tame en banda 1500-2300 (peaks NO cubiertos por voyager_safe).
      5. Risers/downlifters/cue_release: LPF 800 (evita que el exciter del
         master genere armonicos sinteticos en Fletcher-Munson).

    Returns dict con conteo de aplicaciones.
    """
    n_hpf = 0
    n_bell_tame = 0
    n_pad_tame = 0
    n_voyager_tame = 0
    n_sweep_lpf = 0

    for tr in comp.tracks:
        name = tr.name.lower()

        cutoff = _decide_hpf(name)
        if cutoff is not None:
            tr.fx(lambda a, c=cutoff: hpf(a, c))
            n_hpf += 1

        if _is_bell_like(name):
            tr.fx(lambda a: tame_band_sustain(
                a, lo_hz=520, hi_hz=950,
                threshold=0.010, smooth_ms=180, max_reduction_db=0.0))
            tr.fx(lambda a: tame_band_sustain(
                a, lo_hz=1100, hi_hz=1850,
                threshold=0.012, smooth_ms=200, max_reduction_db=-1.5))
            n_bell_tame += 1
        elif _is_sustained_pad(name):
            tr.fx(lambda a: tame_band_sustain(
                a, lo_hz=520, hi_hz=950,
                threshold=0.005, smooth_ms=300, max_reduction_db=-12.0))
            n_pad_tame += 1

        if _is_voyager_like(name):
            tr.fx(lambda a: tame_band_sustain(
                a, lo_hz=1500, hi_hz=2300,
                threshold=0.008, smooth_ms=250, max_reduction_db=-15.0))
            n_voyager_tame += 1

        if _is_sweep_track(name):
            tr.fx(lambda a: lpf(a, 800))
            n_sweep_lpf += 1

    info = {
        'hpf': n_hpf,
        'bell_tame': n_bell_tame,
        'pad_tame': n_pad_tame,
        'voyager_tame': n_voyager_tame,
        'sweep_lpf': n_sweep_lpf,
    }
    if verbose:
        print(f'  auto_fixes: HPF={info["hpf"]} bell_tame={info["bell_tame"]} '
              f'pad_tame={info["pad_tame"]} voyager_tame={info["voyager_tame"]} '
              f'sweep_lpf={info["sweep_lpf"]}')
    return info
