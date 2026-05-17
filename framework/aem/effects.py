"""Efectos por pista. Todos son funciones puras (audio -> audio)."""

import numpy as np
from scipy import signal

from .core import SR


def fade(audio, fi=0, fo=0):
    """Fade in (fi seg) y/o fade out (fo seg) lineal."""
    out = audio.copy()
    fi_n = int(fi * SR)
    fo_n = int(fo * SR)
    if fi_n > 0:
        out[:fi_n] *= np.linspace(0, 1, fi_n)
    if fo_n > 0:
        out[-fo_n:] *= np.linspace(1, 0, fo_n)
    return out


def lpf(audio, cutoff, order=2):
    """Low-pass Butterworth via filtfilt (zero phase)."""
    nyq = SR / 2
    b, a = signal.butter(order, cutoff / nyq, btype='low')
    return signal.filtfilt(b, a, audio)


def hpf(audio, cutoff, order=2):
    """High-pass Butterworth via filtfilt."""
    nyq = SR / 2
    b, a = signal.butter(order, cutoff / nyq, btype='high')
    return signal.filtfilt(b, a, audio)


def notch_eq(audio, freq_hz, q=10.0, gain_db=-6.0):
    """Peaking EQ biquad (RBJ Audio EQ Cookbook).

    gain_db negativo = NOTCH (sustractivo). Atenua una banda estrecha
    sin tocar el resto del espectro.

    Q alto (8-12) = notch quirurgico. Q bajo (1-3) = afecta vecinas.
    """
    A = 10 ** (gain_db / 40)
    omega = 2 * np.pi * freq_hz / SR
    alpha = np.sin(omega) / (2 * q)
    cos_omega = np.cos(omega)
    b0 = 1 + alpha * A
    b1 = -2 * cos_omega
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * cos_omega
    a2 = 1 - alpha / A
    b = np.array([b0, b1, b2]) / a0
    a = np.array([1.0, a1 / a0, a2 / a0])
    return signal.lfilter(b, a, audio)


def reverb(audio, decay=2.0, mix=0.3, pre_delay_ms=0):
    """Multi-tap delay con decaimiento exponencial.

    NOTA tecnica: la formula `(decay/4)^(dm/200)` genera gains de tap > 1
    cuando decay > 4. Eso NO es bug — el "shimmer/tilin tilin" de los bells
    del album depende de esa amplificacion sutil en taps de cola larga.
    Si se usa como CATHEDRAL MASTER reverb (sobre el mix completo), genera
    wow/flutter audible. Para uso master, mantener decay <= 4.

    Args:
        decay: largo de la cola (~segundos para silenciar).
        mix: cantidad de wet (0-1).
        pre_delay_ms: silencio entre la nota seca y el inicio del reverb (ms).
    """
    out = audio * (1 - mix * 0.5)
    pd_n = int(pre_delay_ms / 1000 * SR)
    delays_ms = [37, 53, 79, 113, 173, 251, 379, 547, 743]
    for dm in delays_ms:
        ds = int(dm / 1000 * SR) + pd_n
        if ds >= len(audio):
            continue
        g = (decay / 4) ** (dm / 200) * mix / len(delays_ms) * 1.5
        delayed = np.zeros_like(audio)
        delayed[ds:] = audio[:-ds] * g
        out += delayed
    return out


def distort(audio, amount=2.0):
    """Saturacion tanh. amount controla cuanto comprime."""
    return np.tanh(audio * amount) / np.tanh(amount)


def amp_envelope(audio, points):
    """Aplica una envolvente piecewise-linear de amplitud al audio.

    points: lista de (t_segundos, gain). Interpolacion lineal entre puntos.
    Antes del primer punto y despues del ultimo se sostiene el valor extremo.

    Ejemplo:
        # full hasta 0:50, baja a 0.25 entre 0:50 y 1:30, sostiene
        amp_envelope(audio, [(0, 1.0), (50, 1.0), (90, 0.25), (480, 0.25)])
    """
    if not points:
        return audio
    out = audio.copy()
    n = len(out)
    times = np.array([p[0] for p in points], dtype=np.float64)
    gains = np.array([p[1] for p in points], dtype=np.float64)
    sample_t = np.linspace(0, n / SR, n, False)
    env = np.interp(sample_t, times, gains)
    return out * env


def lfo_amp(audio, rate_hz=0.2, depth=0.3, offset=1.0):
    """Modulacion de amplitud por LFO sinusoidal lento.

    out = audio * (offset + depth * sin(2π * rate * t))

    Default crea un 'breathing' a 0.2 Hz (un ciclo cada 5s) variando
    amplitud entre 0.7 y 1.3 (offset 1.0, depth 0.3).
    """
    n = len(audio)
    ta = np.linspace(0, n / SR, n, False)
    mod = offset + depth * np.sin(2 * np.pi * rate_hz * ta)
    return audio * mod


def tape_warm(audio, drive=1.6):
    """Tape saturation suave (warmth analogica). Diferente del distort:
    drive bajo (1.3-2.0) agrega harmonicos pares, suaviza transients.
    Para drones/pads que se sienten frios."""
    return np.tanh(audio * drive) / np.tanh(drive)


def radio_interference(signal, noise_amount=0.4, lpf_cutoff=1500,
                       saturation=1.3, seed=None):
    """Procesa una senial como una transmision radial con interferencia.
    Para vestigios del voyager que llegan "de pedo" entre el ruido cosmico.

    Args:
        signal: array de audio
        noise_amount: amplitud del noise overlay (0.2-0.6)
        lpf_cutoff: corte del LPF (1000-2000 Hz tipico — solo mids)
        saturation: warmth (1.2-1.5)
    """
    rng = np.random.default_rng(seed)
    sig = lpf(signal, lpf_cutoff)
    sig = np.tanh(sig * saturation) / np.tanh(saturation)
    n = len(sig)
    static = rng.standard_normal(n) * noise_amount * 0.4
    static = lpf(static, 3000)
    return sig + static


def reverse_reverb_swell(event_audio, decay=4.0, mix=1.0, swell_dur=None):
    """Crea un swell que entra ANTES del evento (reverse reverb).
    Devuelve el swell para posicionar antes del evento original.

    Si swell_dur es None, usa la longitud completa del reverb tail.
    """
    tail = reverb(event_audio, decay=decay, mix=mix)
    reversed_tail = tail[::-1]
    if swell_dur is not None:
        n = int(swell_dur * SR)
        if n < len(reversed_tail):
            reversed_tail = reversed_tail[-n:]
    # fade in largo, salida brusca para llevar al evento
    n = len(reversed_tail)
    fi_n = int(n * 0.7)
    out = reversed_tail.copy()
    out[:fi_n] *= np.linspace(0, 1, fi_n) ** 1.5
    return out
