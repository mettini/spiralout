"""Master FX: efectos que operan sobre el estereo final.

Master chain v2 (mayo 2026) — promovida del lab/clear_experiment despues de
iterar con feedback auditivo del user en el proyecto Heliopause.

Mejoras vs master chain original:
  - Mid scoop mas ancho (-2.5 dB @ 280 Q=0.8 vs -2 @ 300 Q=0.7)
  - Notch quirurgico en 1960 Hz (zona donde no hay fundamentales/armonicos
    musicales del album — saca chinchinante del voyager_swell/degraded sin
    tocar timbre de bells)
  - Exciter armonico TANH (no abs() rectifier — el abs en mixes complejos
    genera ~820 inter-modulations no-musicales que suenan a fritura)
  - Dual air shelf (+1.5 dB @ 5kHz + +2 dB @ 11kHz) — abre el espectro
    Lustmord-style sin sobre-saturar Fletcher-Munson
  - Glue tanh 0.08 (no 0.15) — menos armonicos pares acumulados
  - Soft limiter -0.5 dBTP (no -1) — mas headroom, menos saturacion
"""

import numpy as np

from .core import SR
from .effects import lpf, hpf, distort


def dirty_intro(stereo_audio, dirty_until=8, transition_dur=4,
                lpf_cutoff=700, distort_amount=1.8, n_crackles=25, seed=42,
                dirty_gain=0.85, transition_curve=2.5, start_offset=0.0):
    """Concept del Outbound: 'sonda encerrada' al inicio (LPF muy bajo,
    saturacion, crackles), despues se libera. Pasado el final de la transicion
    la senial queda 100% limpia.
    """
    out = stereo_audio.copy().astype(np.float64)
    n_offset = int(start_offset * SR)
    n_dirty = int(dirty_until * SR)
    n_trans = int(transition_dur * SR)
    n_total = n_dirty + n_trans
    if n_offset + n_total > out.shape[0]:
        n_total = out.shape[0] - n_offset
        n_dirty = max(0, n_total - n_trans)

    rng = np.random.default_rng(seed)

    for ch in range(out.shape[1]):
        clean_seg = stereo_audio[n_offset:n_offset + n_total, ch].astype(np.float64)
        seg = lpf(clean_seg, lpf_cutoff)
        seg = distort(seg, amount=distort_amount)

        for _ in range(n_crackles):
            p = int(rng.integers(0, max(1, n_dirty)))
            decay = 1.0 - (p / max(1, n_dirty))
            crackle = rng.standard_normal(80) * 0.18 * (0.4 + 0.6 * decay)
            end = min(p + 80, n_total)
            seg[p:end] += crackle[:end - p]

        if n_dirty > 0:
            out[n_offset:n_offset + n_dirty, ch] = (
                seg[:n_dirty] * dirty_gain
                + clean_seg[:n_dirty] * (1 - dirty_gain)
            )

        if n_trans > 0 and n_offset + n_dirty + n_trans <= out.shape[0]:
            t = np.linspace(0, 1, n_trans)
            dirty_amt = ((1 - t) ** transition_curve) * dirty_gain
            clean_amt = 1 - dirty_amt
            slc = slice(n_offset + n_dirty, n_offset + n_dirty + n_trans)
            out[slc, ch] = (
                seg[n_dirty:n_dirty + n_trans] * dirty_amt
                + clean_seg[n_dirty:n_dirty + n_trans] * clean_amt
            )
            end_idx = n_offset + n_dirty + n_trans - 1
            out[end_idx, ch] = stereo_audio[end_idx, ch]
    return out


# ============================================================
# MASTER CHAIN — para release final
# ============================================================

def soft_limit(stereo_audio, ceiling=0.89):
    """Limiter suave tanh-based.
    Para ambient: preferible a hard limiter, preserva mas dinamica.
    """
    drive = 1.0 / ceiling
    return np.tanh(stereo_audio * drive) * ceiling


def lufs_normalize(stereo_audio, target_lufs=-16.0):
    """Normaliza a target LUFS usando pyloudnorm (BS.1770)."""
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    loudness = meter.integrated_loudness(stereo_audio)
    if not np.isfinite(loudness):
        return stereo_audio
    delta_db = target_lufs - loudness
    gain = 10 ** (delta_db / 20)
    return stereo_audio * gain


# --- Helpers del master chain ---

def _high_shelf_boost(audio, gain_db, freq, sr=44100):
    """High-shelf boost via butter HPF + sumar al original."""
    from scipy.signal import iirfilter, sosfilt
    nyq = sr / 2
    sos = iirfilter(2, freq / nyq, btype='highpass', ftype='butter', output='sos')
    boost = sosfilt(sos, audio, axis=0)
    gain_linear = 10 ** (gain_db / 20) - 1.0
    return audio + boost * gain_linear


def _peak_eq(audio, gain_db, freq, q, sr=44100):
    """Peak/bell filter — boost (gain_db > 0) o cut/notch (gain_db < 0)."""
    from scipy.signal import iirpeak, sosfilt, tf2sos
    w0 = freq / (sr / 2)
    b, a = iirpeak(w0, q)
    sos = tf2sos(b, a)
    notch = sosfilt(sos, audio, axis=0)
    gain_linear = 10 ** (gain_db / 20) - 1.0
    return audio + notch * gain_linear


def _ms_width(audio, side_gain=1.25):
    """Mid/Side stereo widening — boost del Side para sensacion de ancho."""
    if audio.ndim != 2 or audio.shape[1] != 2:
        return audio
    L = audio[:, 0]
    R = audio[:, 1]
    M = (L + R) * 0.5
    S = (L - R) * 0.5 * side_gain
    out = np.empty_like(audio)
    out[:, 0] = M + S
    out[:, 1] = M - S
    return out


def _harmonic_exciter(audio, src_lo=1200.0, src_hi=3500.0,
                      drive=2.0, mix=0.20, sr=44100):
    """Harmonic exciter — tanh saturation (NO abs() rectifier).

    Por que tanh y no abs():
      El abs() rectifier crea inter-modulation BRUTAL entre cada par de
      frecuencias presentes — para un mix con 40+ freqs activas, genera
      ~820 frecuencias suma/diferencia NO-musicales que suenan a fritura.

      tanh es soft saturation analog-like: cada frecuencia genera sus propios
      armonicos (mayormente impares — 3er, 5to, 7mo) con MUY POCAS
      inter-modulations.
    """
    from scipy.signal import butter, sosfiltfilt

    # 1. Bandpass del source
    sos_bp = butter(4, [src_lo, src_hi], btype='band', fs=sr, output='sos')
    if audio.ndim == 2:
        src = np.empty_like(audio)
        for ch in range(audio.shape[1]):
            src[:, ch] = sosfiltfilt(sos_bp, audio[:, ch])
    else:
        src = sosfiltfilt(sos_bp, audio)

    # 2. tanh saturation
    saturated = np.tanh(src * drive) / max(np.tanh(drive), 1e-9)

    # 3. HPF para quedarse solo con armonicos nuevos arriba del source
    sos_hp = butter(4, src_hi, btype='highpass', fs=sr, output='sos')
    if saturated.ndim == 2:
        excite = np.empty_like(saturated)
        for ch in range(saturated.shape[1]):
            excite[:, ch] = sosfiltfilt(sos_hp, saturated[:, ch])
    else:
        excite = sosfiltfilt(sos_hp, saturated)

    # 4. Mezclar back
    return audio + excite * mix


# --- Master chain principal ---

def master_chain(stereo_audio,
                 lufs_target=-16.0,
                 true_peak_db=-0.5,
                 hpf_freq=30,
                 mid_scoop_db=-2.5,
                 mid_scoop_freq=280.0,
                 mid_scoop_q=0.8,
                 notch_freqs=(1960.0,),
                 notch_db=-2.5,
                 notch_q=3.0,
                 exciter_enabled=True,
                 exciter_src_lo=1200.0,
                 exciter_src_hi=3500.0,
                 exciter_drive=2.0,
                 exciter_mix=0.20,
                 air_low_db=1.5,
                 air_low_freq=5000.0,
                 air_high_db=2.0,
                 air_high_freq=11000.0,
                 ms_width=1.25,
                 glue_amount=0.08):
    """Master chain v2 para ambient — Lustmord-style.

    Orden:
      1. HPF (30 Hz)
      2. Mid scoop (-2.5 dB @ 280 Hz Q=0.8)
      3. Notch en 1960 Hz Q=3 -2.5 dB (zona sin nota musical critica)
      4. Exciter armonico TANH (1.2-3.5 kHz source → armonicos en 3-14 kHz)
      5. Dual air shelf (+1.5 @ 5kHz, +2 @ 11kHz)
      6. M/S width 1.25
      7. Glue compression tanh 0.08
      8. Soft limiter -0.5 dBTP
      9. LUFS normalize -16 LUFS
    """
    out = stereo_audio.astype(np.float64).copy()

    # 1. HPF por canal
    for ch in range(out.shape[1]):
        out[:, ch] = hpf(out[:, ch], hpf_freq)

    # 2. Mid scoop — saca mud 200-400 Hz
    if mid_scoop_db < 0:
        out = _peak_eq(out, gain_db=mid_scoop_db,
                       freq=mid_scoop_freq, q=mid_scoop_q)

    # 3. Notches quirurgicos
    for f in notch_freqs:
        out = _peak_eq(out, gain_db=notch_db, freq=f, q=notch_q)

    # 4. EXCITER ARMONICO
    if exciter_enabled:
        out = _harmonic_exciter(
            out,
            src_lo=exciter_src_lo, src_hi=exciter_src_hi,
            drive=exciter_drive, mix=exciter_mix)

    # 5. Dual air shelf
    if air_low_db > 0:
        out = _high_shelf_boost(out, gain_db=air_low_db, freq=air_low_freq)
    if air_high_db > 0:
        out = _high_shelf_boost(out, gain_db=air_high_db, freq=air_high_freq)

    # 6. M/S width
    if ms_width != 1.0:
        out = _ms_width(out, side_gain=ms_width)

    # 7. Glue compression
    drive = 1.0 + glue_amount
    out = np.tanh(out * drive) / np.tanh(drive)

    # 8. Soft limiter
    ceiling = 10 ** (true_peak_db / 20)
    out = soft_limit(out, ceiling=ceiling)

    # 9. LUFS normalize
    out = lufs_normalize(out, target_lufs=lufs_target)

    # Safety clip
    out = np.clip(out, -ceiling, ceiling)

    return out
