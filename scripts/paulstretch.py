#!/usr/bin/env python3
"""Paulstretch: time-stretch extremo por randomización de fase.

El algoritmo canónico de Paul Nasca (el que usa PaulXStretch), en numpy. Estira
un sonido corto a minutos SIN el artefacto metálico del stretch clásico, porque
en vez de repetir granos randomiza la fase de cada ventana FFT y conserva solo
la magnitud. Resultado: el espectro se sostiene, el tiempo se disuelve.

Los dos parámetros que importan:

- **stretch**: cuánto se estira. 15 s x 20 = 5 minutos.
- **window**: el tamaño de la ventana FFT en segundos. **Es el que define el
  carácter.** Chica (0.1-0.2) deja el grano y algo del ritmo original; grande
  (1.0-3.0) lo funde en un pad sin ataque. No hay valor "correcto", hay dos
  sonidos distintos.

Uso:
    python3 scripts/paulstretch.py entrada.wav salida.wav --stretch 20 --window 0.5
    python3 scripts/paulstretch.py entrada.wav salida.wav --stretch 20 --window 1.5 --lowpass 800

`--lowpass` aplica el corte anti-fritura del proyecto (ver
`memory/pattern_noise_fritura.md`): arriba de ~1 kHz el material ruidoso
estirado suena a estática, no a espacio.
"""
import argparse
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, oaconvolve, sosfilt, sosfiltfilt


def paulstretch(samples, sr, stretch, window_sec):
    """Devuelve `samples` estirado `stretch` veces con ventana `window_sec`."""
    # ventana par, para que la mitad sea exacta
    win = int(window_sec * sr / 2) * 2
    half = win // 2
    # el envelope de Paulstretch: no es Hann, es (1 - x^2)^1.25, que solapa mejor
    x = np.linspace(-1.0, 1.0, win)
    envelope = (1.0 - x ** 2) ** 1.25

    # cuánto avanza el puntero de LECTURA por cada salto de half en la SALIDA
    displace = half / stretch

    out = np.zeros(int(len(samples) * stretch) + win, dtype=np.float64)
    old_windowed = np.zeros(half)
    pos = 0.0
    out_pos = 0

    while pos + win < len(samples):
        chunk = samples[int(pos):int(pos) + win] * envelope

        # magnitud del espectro, fase random: el corazón del algoritmo
        spec = np.fft.rfft(chunk)
        mag = np.abs(spec)
        phase = np.random.uniform(0, 2 * np.pi, len(spec))
        spec = mag * (np.cos(phase) + 1j * np.sin(phase))
        chunk = np.fft.irfft(spec) * envelope

        # overlap-add al 50%: la primera mitad se cruza con la anterior
        out[out_pos:out_pos + half] += old_windowed + chunk[:half]
        old_windowed = chunk[half:]

        pos += displace
        out_pos += half

    return out[:out_pos]


def make_ir(sr, seconds, lowpass_hz, seed):
    """IR sintetica: ruido que decae, filtrado. Una camara grande y oscura.

    El filtro no es decorativo: ruido con contenido arriba de ~1-2 kHz suena a
    fritura, no a espacio (`memory/pattern_noise_fritura.md`).
    """
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    t = np.arange(n) / sr
    ir = rng.standard_normal(n) * np.exp(-t / (seconds / 5.0))
    sos = butter(4, lowpass_hz / (sr / 2), btype="low", output="sos")
    ir = sosfilt(sos, ir)
    pre = int(0.03 * sr)                     # pre-delay corto: da tamano
    ir[:pre] *= np.linspace(0, 1, pre)
    return ir / np.abs(ir).max()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--stretch", type=float, default=20.0)
    p.add_argument("--window", type=float, default=0.5, help="ventana FFT en segundos")
    p.add_argument("--lowpass", type=float, default=0.0, help="Hz; 0 = sin filtro")
    p.add_argument("--octaves-down", type=float, default=0.0,
                   help="baja la afinacion por velocidad de reproduccion; cada octava duplica el largo")
    p.add_argument("--gain", type=float, default=0.9, help="pico de salida")
    p.add_argument("--stereo", action="store_true",
                   help="dos pasadas independientes L/R. Paulstretch randomiza la fase, asi que "
                        "dos corridas dan el mismo espectro con fase distinta = estereo real")
    p.add_argument("--space", type=float, default=0.0,
                   help="segundos de cola de reverb por convolucion; 0 = seco")
    p.add_argument("--space-lowpass", type=float, default=2000.0, help="Hz de la IR")
    p.add_argument("--wet", type=float, default=0.8, help="0-1")
    # cadena de acabado
    p.add_argument("--hp", type=float, default=0.0,
                   help="Hz de high-pass. 28 saca el subsonico que se come headroom")
    p.add_argument("--mono-below", type=float, default=0.0,
                   help="Hz debajo de los cuales el material va a mono. 120 es lo estandar: "
                        "sub decorrelado se cancela al sumar a mono")
    p.add_argument("--drive", type=float, default=0.0,
                   help="0-1, saturacion tanh EN PARALELO. Genera armonicos desde los "
                        "fundamentales para que el sub se oiga en parlantes chicos. "
                        "tanh, nunca abs (ver memory/abs_rectifier_exciter_antipattern.md)")
    p.add_argument("--seconds", type=float, default=0.0,
                   help="recorta la salida a N segundos, tomados del MEDIO, con fades de 2s")
    p.add_argument("--peak-db", type=float, default=None,
                   help="pico de salida en dBFS. -6 para un stem que despues se mezcla")
    a = p.parse_args()

    sr, data = wavfile.read(a.entrada)
    data = data.astype(np.float64)
    if data.ndim > 1:                       # a mono, es material de textura
        data = data.mean(axis=1)
    if np.abs(data).max() > 0:
        data /= np.abs(data).max()

    if a.stereo:
        chans = [paulstretch(data, sr, a.stretch, a.window),
                 paulstretch(data, sr, a.stretch, a.window)]
        n = min(len(c) for c in chans)
        out = np.stack([c[:n] for c in chans], axis=1)
    else:
        out = paulstretch(data, sr, a.stretch, a.window)[:, None]

    if a.octaves_down > 0:
        # bajar por velocidad, como una cinta lenta: pitchea Y alarga.
        # Es el gesto de Lustmord, no un pitch-shift que preserva duracion.
        factor = 2.0 ** a.octaves_down
        idx = np.arange(0, len(out) - 1, 1.0 / factor)
        src = np.arange(len(out))
        out = np.stack([np.interp(idx, src, out[:, c]) for c in range(out.shape[1])], axis=1)

    if a.lowpass > 0:
        sos = butter(4, a.lowpass / (sr / 2), btype="low", output="sos")
        out = np.stack([sosfilt(sos, out[:, c]) for c in range(out.shape[1])], axis=1)

    if a.space > 0:
        # una IR distinta por canal: ensancha todavia mas, porque las colas
        # no estan correlacionadas entre si.
        # float32 a proposito: en renders de 40+ min, float64 se come varios GB
        out = out.astype(np.float32)
        wet = np.zeros_like(out)
        for c in range(out.shape[1]):
            ir = make_ir(sr, a.space, a.space_lowpass, seed=1000 + c).astype(np.float32)
            w = oaconvolve(out[:, c], ir)[:len(out)]
            wet[:, c] = w / (np.abs(w).max() or 1.0)
        out = (1 - a.wet) * out / (np.abs(out).max() or 1.0) + a.wet * wet

    out = out - out.mean(axis=0, keepdims=True)          # DC offset fuera

    if a.hp > 0:
        sos = butter(2, a.hp / (sr / 2), btype="high", output="sos")
        out = np.stack([sosfilt(sos, out[:, c]) for c in range(out.shape[1])], axis=1)

    if a.drive > 0:
        norm = np.abs(out).max() or 1.0
        sat = np.tanh(out / norm * 3.0) * norm            # tanh: armonicos sin intermodulaciones
        out = (1 - a.drive) * out + a.drive * sat

    if a.drive > 0:
        norm = np.abs(out).max() or 1.0
        out = (1 - a.drive) * out + a.drive * (np.tanh(out / norm * 3.0) * norm)

    if a.mono_below > 0 and out.shape[1] == 2:
        # sosfiltfilt (fase cero) a proposito: con un IIR causal, "senal - lowpass"
        # NO es un complemento porque el lowpass sale desfasado, y deja residuo
        # decorrelacionado en los graves. Con fase cero la resta es exacta.
        # Y va DESPUES del drive: saturar decorrelaciona, asi que la imagen se
        # arregla al final.
        sos = butter(4, a.mono_below / (sr / 2), btype="low", output="sos")
        low = np.stack([sosfiltfilt(sos, out[:, c]) for c in range(2)], axis=1)
        out = (out - low) + low.mean(axis=1, keepdims=True)

    if a.seconds > 0:
        need = int(a.seconds * sr)
        if len(out) > need:
            off = (len(out) - need) // 2      # del medio: el arranque de un stretch es lo mas pobre
            out = out[off:off + need]
        f = int(min(2.0, a.seconds / 6) * sr)
        ramp = np.linspace(0, 1, f)[:, None] if out.ndim > 1 else np.linspace(0, 1, f)
        out[:f] *= ramp
        out[-f:] *= ramp[::-1]

    peak = np.abs(out).max()
    if peak > 0:
        target = a.gain if a.peak_db is None else 10 ** (a.peak_db / 20)
        out = out / peak * target

    if out.shape[1] == 1:
        out = out[:, 0]
    wavfile.write(a.salida, sr, (out * 32767).astype(np.int16))
    print(f"-> {a.salida}  {len(out) / sr / 60:.1f} min  "
          f"(x{a.stretch:g}, ventana {a.window:g}s"
          f"{f', -{a.octaves_down:g} oct' if a.octaves_down else ''}"
          f"{f', LP {a.lowpass:g} Hz' if a.lowpass else ''}"
          f"{f', camara {a.space:g}s wet {a.wet:g}' if a.space else ''}"
          f"{', estereo' if a.stereo else ''})")


if __name__ == "__main__":
    sys.exit(main())
