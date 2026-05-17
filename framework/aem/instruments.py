"""Instrumentos compuestos. Combinan primitivas de sintesis para generar
sonidos mas reconocibles (drone, voz, kick, melodia, etc.).

Glosario por proposito:
  - estructura armonica: detuned_drone, voice_pad, chord
  - melodia: melody, bell
  - ritmo: kick, hihat
  - transiciones: riser, downlifter, reverse_swell, whoosh, granular_pulse
"""

import numpy as np

from .core import SR, t_arr
from .synth import sine
from .effects import lpf, hpf


def detuned_drone(freqs, dur, amp=0.3, n_voices=3, detune_cents=10, waveform='sine'):
    """Drone con voces ligeramente desafinadas — produce coro/grosor sin movimiento.

    waveform: 'sine' (legacy) o 'triangle'. Triangle distribuye energia en
    armonicos impares con amplitud 1/k^2 (mas suave, menos punzante en
    sostenidos sobre zona Fletcher-Munson). Igual que voyager_motif Tool.
    """
    n = int(dur * SR)
    out = np.zeros(n)
    voice_amp = amp / (len(freqs) * n_voices)
    for f in freqs:
        for i in range(n_voices):
            cents = (i - (n_voices - 1) / 2) * detune_cents
            f_d = f * 2 ** (cents / 1200)
            if waveform == 'sine':
                out += sine(f_d, dur, voice_amp)
            elif waveform == 'triangle':
                ta = np.linspace(0, dur, n, False)
                phase = 2 * np.pi * f_d * ta
                tri = np.zeros(n)
                for k in [1, 3, 5, 7, 9]:
                    sign = (-1) ** ((k - 1) // 2)
                    tri += sign * np.sin(k * phase) / (k ** 2)
                tri *= 8 / (np.pi ** 2)
                out += tri * voice_amp
            else:
                raise ValueError(f'waveform invalido: {waveform!r}')
    return out


def voice_pad(freq, dur, vibrato_rate=4.0, vibrato_depth=0.005, amp=0.3, n_harmonics=3):
    """Pad estilo voz: vibrato sutil + armonicos descendentes."""
    ta = t_arr(dur)
    vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * ta)
    f_mod = freq * vibrato
    phase = 2 * np.pi * np.cumsum(f_mod) / SR
    out = np.zeros_like(phase)
    for h in range(1, n_harmonics + 1):
        out += np.sin(h * phase) / h
    return (out / n_harmonics) * amp


def kick(amp=0.8, dur=0.6, f0=80, fe=35, attack_ms=0.0, release_ms=0.0,
         pitch_sweep=True):
    """Kick con pitch envelope (de f0 a fe) y envolvente de amplitud exponencial.

    Defaults restaurados al original (pitch_sweep=True, sin attack/release).
    Parametros opcionales:
        attack_ms: micro-attack lineal en los primeros ms (anti-click inicial)
        release_ms: micro-release exponencial al final (anti-cola sumandose
            con siguiente kick). Curva exp para no quebrar gradient.
    """
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    if pitch_sweep:
        fr = fe + (f0 - fe) * np.exp(-ta * 8)
        phase = 2 * np.pi * np.cumsum(fr) / SR
    else:
        phase = 2 * np.pi * f0 * ta
    env = np.exp(-ta * 4)
    a_n = int(attack_ms / 1000 * SR)
    if a_n > 0 and a_n < n:
        env[:a_n] *= np.linspace(0, 1, a_n)
    r_n = int(release_ms / 1000 * SR)
    if r_n > 0 and r_n < n:
        # Cosine smoothing 1→0 (sin quiebre de gradient — evita "tic" en cola)
        r_decay = (np.cos(np.linspace(0, np.pi, r_n)) + 1) / 2
        env[-r_n:] *= r_decay
    return amp * env * np.sin(phase)


def hihat(dur=0.04, amp=0.3):
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    env = np.exp(-ta * 80)
    return amp * env * np.random.randn(n)


def melody(notes, amp=0.3, vibrato=True, crossfade=0.0, waveform='sine',
           attack=0.05, release=0.1, release_curve=1.0, breath_amount=0.0):
    """Secuencia de notas (freq, dur) con vibrato opcional.

    Args:
        notes: lista de (freq_hz, dur_sec)
        amp: amplitud
        vibrato: aplicar vibrato 5 Hz
        crossfade: overlap entre notas en segundos
        waveform: 'sine' (legacy, sine + 15% 2do harm),
                  'triangle' (1/k^2 sum de armonicos impares — suave),
                  'square' (1/k sum de armonicos impares — brillante),
                  'flute' (sine + noise filtrado mezclado, simula soplo de quena)
        attack: segundos de attack lineal (default 0.05)
        release: segundos de release lineal (default 0.1). Subir a 0.5-1.5
            para que la cola se sostenga y solape con la siguiente nota
            (efecto "pedal del piano").
        breath_amount: cantidad de noise filtrado mezclado para simular soplo.
            Solo aplica si waveform='flute' (default 0.15).
    """
    crossfade_n = int(crossfade * SR)
    release_n = int(release * SR)
    out_parts = []
    note_step_samples = []  # cuanto avanza el "pos" por nota (= note_dur sin cola)
    for freq, note_dur in notes:
        n_nominal = int(note_dur * SR)
        # n incluye nominal + cola release (asi la cola se extiende mas alla)
        n = n_nominal + release_n
        note_step_samples.append(n_nominal)
        ta = np.linspace(0, n / SR, n, False)
        if vibrato:
            vib = 1 + 0.008 * np.sin(2 * np.pi * 5 * ta)
            f_mod = freq * vib
        else:
            f_mod = np.full(n, freq)
        phase = 2 * np.pi * np.cumsum(f_mod) / SR
        if waveform == 'sine':
            sample = np.sin(phase) + 0.15 * np.sin(2 * phase)
        elif waveform == 'triangle':
            sample = np.zeros_like(phase)
            for k in [1, 3, 5, 7, 9]:
                sign = (-1) ** ((k - 1) // 2)
                sample += sign * np.sin(k * phase) / (k ** 2)
            sample *= 8 / (np.pi ** 2)
        elif waveform == 'square':
            sample = np.zeros_like(phase)
            for k in [1, 3, 5, 7, 9, 11, 13]:
                sample += np.sin(k * phase) / k
            sample *= 4 / np.pi
        elif waveform == 'flute':
            # Sine + 0.05 del 2do harm + noise filtrado banda alrededor de freq
            from scipy import signal as sps
            sample = np.sin(phase) + 0.05 * np.sin(2 * phase)
            # Noise filtrado bandpass alrededor de freq (simula aire / soplo)
            noise_raw = np.random.randn(n)
            low = max(50, freq * 0.5) / (SR / 2)
            high = min(0.95, freq * 4 / (SR / 2))
            if low < high:
                b, a = sps.butter(2, [low, high], btype='band')
                noise_filt = sps.filtfilt(b, a, noise_raw)
                noise_filt /= max(np.max(np.abs(noise_filt)), 1e-9)
                breath = breath_amount if breath_amount > 0 else 0.15
                sample = sample * (1 - breath * 0.5) + noise_filt * breath
        else:
            raise ValueError(f'waveform invalido: {waveform!r}')
        # Envelope: attack rampa, sustain hasta n_nominal, release lineal hasta n.
        # release_n puede ser MAYOR que note_dur (cola se extiende, "pedal piano").
        a_n = max(int(attack * SR), crossfade_n)
        a_n = min(a_n, n_nominal // 2 if n_nominal > 0 else a_n)
        s_n = max(0, n_nominal - a_n)
        r_n = release_n if release_n > 0 else 0
        # release_curve: 1.0 = lineal, >1 = decae rapido al inicio (mas natural).
        if r_n > 0:
            release_env = (1 - np.linspace(0, 1, r_n)) ** release_curve
        else:
            release_env = np.array([])
        env = np.concatenate([
            np.linspace(0, 1, a_n),
            np.full(s_n, 1.0),
            release_env,
        ])
        # Asegurar mismo length que sample
        if len(env) < n:
            env = np.concatenate([env, np.zeros(n - len(env))])
        env = env[:n]
        out_parts.append(sample * env * amp)

    # Mix con offsets = note_dur (cada nota arranca al final del nominal de la
    # anterior; la cola de release se SUMA con el inicio de la siguiente).
    # crossfade adicional resta del step si > 0 (legacy).
    total_samples = sum(note_step_samples[:-1]) - crossfade_n * (len(out_parts) - 1) \
                    + len(out_parts[-1])
    out = np.zeros(max(total_samples, len(out_parts[-1])))
    pos = 0
    for i, p in enumerate(out_parts):
        end = min(pos + len(p), len(out))
        out[pos:end] += p[:end - pos]
        if i < len(out_parts) - 1:
            pos += note_step_samples[i] - crossfade_n
    return out


def riser(dur=4.0, f_start=50, f_end=300, amp=0.5):
    """Sweep ascendente — cue de transicion entre secciones."""
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    fr = f_start + (f_end - f_start) * (ta / dur) ** 2
    ph = 2 * np.pi * np.cumsum(fr) / SR
    env = np.linspace(0, 1, n) ** 1.5
    return np.sin(ph) * env * amp


def downlifter(dur=4.0, f_start=400, f_end=40, amp=0.5):
    """Sweep descendente — landing despues de una seccion."""
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    fr = f_end + (f_start - f_end) * (1 - ta / dur) ** 2
    ph = 2 * np.pi * np.cumsum(fr) / SR
    env = np.linspace(1, 0, n) ** 1.5
    return np.sin(ph) * env * amp


def reverse_swell(dur=3.0, freq=200, amp=0.4, n_harmonics=3):
    """Sonido que crece y corta abruptamente — marker pre-evento.

    Tipico antes de un drop o entrada importante: la audiencia siente que
    'algo se viene'. Pareja al downlifter (que limpia despues del evento).
    """
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    out = np.zeros(n)
    for h in range(1, n_harmonics + 1):
        out += np.sin(2 * np.pi * freq * h * ta) / h
    env = np.linspace(0, 1, n) ** 2
    return amp * env * out / n_harmonics


def bell(freq, dur=4.0, amp=0.4, n_harmonics=4, decay_rate=1.5):
    """Tono de campana: fundamental + armonicos con decay exponencial.

    Sirve como marcador de momentos clave (cambios de seccion). El timbre
    metalico es muy distinto del bed armonico, asi corta sin pelear con
    los drones.
    """
    n = int(dur * SR)
    ta = np.linspace(0, dur, n, False)
    out = np.zeros(n)
    for h in range(1, n_harmonics + 1):
        out += np.sin(2 * np.pi * freq * h * ta) / (h ** 1.5)
    env = np.exp(-ta * decay_rate)
    return amp * env * out / n_harmonics


def whoosh(dur=2.5, cutoff_start=200, cutoff_end=800, amp=0.4, direction='up'):
    """Ruido filtrado con barrido de cutoff — para transiciones (panneable).

    direction='up': sweep abre el filtro (sensacion de apertura/expansion)
    direction='down': sweep cierra el filtro (sensacion de cierre/recogida)

    Mas sutil que un riser: aporta movimiento sin ser melodico.
    """
    n = int(dur * SR)
    raw = np.random.randn(n)
    n_chunks = 24
    chunk_len = max(1, n // n_chunks)
    if direction == 'down':
        cutoffs = np.linspace(cutoff_end, cutoff_start, n_chunks)
    else:
        cutoffs = np.linspace(cutoff_start, cutoff_end, n_chunks)
    chunks = []
    for i, cutoff in enumerate(cutoffs):
        seg = raw[i * chunk_len:(i + 1) * chunk_len]
        if len(seg) > 4:
            chunks.append(lpf(seg, max(80, cutoff)))
    out = np.concatenate(chunks) if chunks else raw
    if len(out) < n:
        out = np.pad(out, (0, n - len(out)))
    else:
        out = out[:n]
    # FIX anti-fritura: las junturas entre chunks de distintos cutoffs son
    # discontinuidades = clicks = energia broadband (> 1500 Hz). Aplicar LPF
    # final con cutoff = max(cutoff_start, cutoff_end) garantiza que no quede
    # contenido arriba de eso, eliminando los clicks de juntura.
    final_cutoff = max(cutoff_start, cutoff_end)
    out = lpf(out, final_cutoff)
    ta = np.linspace(0, 1, n)
    if direction == 'up':
        env = np.power(ta, 0.7)
    else:
        env = np.power(1 - ta, 0.7)
    return amp * env * out


def granular_pulse(freq=400, dur=0.3, amp=0.5, bandwidth_ratio=0.4):
    """Pulso corto de ruido pasa-banda — textura granular.

    Aporta micro-eventos en el bed que rompen la sensacion de drone constante.
    Sembrar varios a tiempos randomicos crea movimiento sin melodia.
    """
    n = int(dur * SR)
    raw = np.random.randn(n)
    raw = hpf(raw, freq * (1 - bandwidth_ratio))
    raw = lpf(raw, freq * (1 + bandwidth_ratio))
    ta = np.linspace(0, 1, n)
    env = np.sin(np.pi * ta) ** 2
    return amp * env * raw


def chord(freqs, dur, amp=0.3, vibrato_rate=3.5, vibrato_depth=0.004, n_harmonics=2):
    """Acorde sostenido (multiples voice_pad superpuestas).

    Usar para cambios armonicos: detuned_drone es un sostenido estable; chord
    permite hacer una progresion (Dm -> F -> Am, etc) usando un evento por
    acorde y crossfadeandolos.
    """
    out = np.zeros(int(dur * SR))
    for f in freqs:
        out += voice_pad(f, dur,
                         vibrato_rate=vibrato_rate,
                         vibrato_depth=vibrato_depth,
                         amp=amp / len(freqs),
                         n_harmonics=n_harmonics)
    return out


def chant_drone(freq, dur, vibrato_rate=1.8, vibrato_depth=0.012,
                amp=0.4, n_harmonics=8, formant_emphasis=(2, 4, 7),
                fundamental_boost=1.0):
    """Vocal drone grave estilo Sardaukar/Dune.

    Fundamental baja (60-150 Hz tipico) + armonicos. Algunos armonicos
    se enfatizan (multiplicados por ~2.5) emulando los formantes que dan
    "color vocal" — sin ser una voz real, suena vocal por la distribucion
    de energia espectral.

    Args:
        freq: fundamental en Hz (60-150 para canto grave)
        dur: duracion en segundos
        vibrato_rate: vibrato lento (1-2.5 Hz para canto sostenido)
        vibrato_depth: profundidad del vibrato
        n_harmonics: cuantos armonicos sumar
        formant_emphasis: tupla de armonicos a enfatizar (vocal-like)
        fundamental_boost: multiplicador extra del armonico 1 (la nota).
            Default 1.0 = sin cambio (retrocompat). Subir a 3-5 hace que
            la nota tonal domine sobre los formantes (que naturalmente
            tienden a opacarla por el x2.5 weight).
    """
    ta = t_arr(dur)
    vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * ta)
    f_mod = freq * vibrato
    phase = 2 * np.pi * np.cumsum(f_mod) / SR
    out = np.zeros_like(phase)
    for h in range(1, n_harmonics + 1):
        if h == 1:
            weight = fundamental_boost
        else:
            weight = 2.5 if h in formant_emphasis else 1.0
        out += np.sin(h * phase) * weight / h
    return (out / n_harmonics) * amp


def sub_rumble(freq=32, dur=10, mod_rate=0.15, mod_depth=0.4, amp=0.5):
    """Sub-bass profundo (28-40 Hz) con modulacion lenta de amplitud.
    Cosmic rumble — la presencia grave de fondo en dark ambient (Lustmord).

    A 28-32 Hz esta en el limite de audicion humana (~20 Hz) — se siente
    mas que se escucha. Buen bed para tema oscuro.
    """
    ta = t_arr(dur)
    mod = 1 + mod_depth * np.sin(2 * np.pi * mod_rate * ta)
    return amp * mod * np.sin(2 * np.pi * freq * ta)


# ============================================================
# RECURSION instruments — drone metal, glitch, phase music
# ============================================================

def wall_of_sound(root_freqs, dur, distortion=4.0, n_layers=4, amp=0.5):
    """Wall of sound estilo Sunn O))) — masa de drones desafinados con
    distortion heavy. Suena como una catedral oscura colapsando.

    Args:
        root_freqs: lista de frecuencias raíz (ej [55.0, 73.42] = A1, D2)
        dur: duracion en segundos
        distortion: cantidad de saturacion tanh (3-6 para wall metal)
        n_layers: cuantas capas desafinadas por root (4-6)
    """
    from .effects import distort
    out = np.zeros(int(dur * SR))
    cents_offsets = [-30, -10, 10, 30, 50, -50][:n_layers]
    for f in root_freqs:
        for cents in cents_offsets:
            f_d = f * 2 ** (cents / 1200)
            out += sine(f_d, dur, amp / (len(root_freqs) * n_layers))
    return distort(out, amount=distortion)


def feedback_squeal(freq, dur, sweep_depth=0.02, sweep_rate=0.3, amp=0.4, decay_rate=0.5):
    """Nota alta sostenida con sweep sutil — simula feedback de amplificador.

    Decay exponencial lento. Pitch oscila levemente (sweep_depth en cents
    relativos) creando inestabilidad realista de feedback acoplado.
    """
    ta = t_arr(dur)
    sweep = 1 + sweep_depth * np.sin(2 * np.pi * sweep_rate * ta)
    f_mod = freq * sweep
    phase = 2 * np.pi * np.cumsum(f_mod) / SR
    env = np.exp(-ta * decay_rate)
    return amp * env * np.sin(phase)


def vinyl_crackle(dur, density=0.3, amp=0.25, base_hiss=0.05, seed=None):
    """Capa constante de vinyl crackle — clicks aleatorios + base hiss.
    Estilo Burial: textura de fondo que llena el espacio.

    Args:
        dur: duracion en segundos
        density: probabilidad de click por sample (0.0001 - 0.001 típico)
        amp: amplitud de los clicks
        base_hiss: amplitud del ruido continuo de fondo
    """
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    # base hiss
    out = rng.standard_normal(n) * base_hiss
    # clicks aleatorios
    n_clicks = int(dur * density * 100)
    for _ in range(n_clicks):
        p = int(rng.integers(0, max(1, n - 50)))
        click_len = int(rng.integers(2, 30))
        click = rng.standard_normal(click_len) * amp * (0.5 + rng.random() * 0.5)
        out[p:p + click_len] += click
    return out


def glitch_burst(dur=0.12, freq_center=800, bandwidth=0.5, amp=0.4):
    """Burst corto de noise filtrado a una freq central. Tipo malfunction
    de radio / glitch digital. Inspirado en sound design de Burial."""
    from .effects import lpf, hpf
    n = int(dur * SR)
    raw = np.random.randn(n)
    raw = hpf(raw, freq_center * (1 - bandwidth))
    raw = lpf(raw, freq_center * (1 + bandwidth))
    # envelope sharp: ataque rapido, decay rapido
    ta = np.linspace(0, 1, n)
    env = np.exp(-ta * 12) * (1 - np.exp(-ta * 40))
    return amp * env * raw


def pitch_jitter_melody(notes, amp=0.3, jitter_cents=5, seed=None):
    """Melodia con shift random de cents en cada nota — "memoria distorsionada".
    Estilo Caretaker / Burial."""
    rng = np.random.default_rng(seed)
    jittered = []
    for f, d in notes:
        shift = (rng.random() * 2 - 1) * jitter_cents  # ±jitter_cents
        f_new = f * 2 ** (shift / 1200)
        jittered.append((f_new, d))
    return melody(jittered, amp=amp, vibrato=True)


def phased_loop(notes, dur_total, loop_dur, phase_shift_ms=5,
                amp=0.35, vibrato=True):
    """Loop de melodia que se desfasa progresivamente — Steve Reich style.

    Devuelve dos arrays paralelos (synced, phased):
      - synced: el loop repetido sincronizado
      - phased: el loop repetido pero con desplazamiento creciente de
                phase_shift_ms milisegundos por loop

    Para usar: meter ambos en tracks paneados L/R. Los loops empiezan
    sincronizados, gradualmente se desfasan creando ringing/echo, y al
    final convergen otra vez (cuando el desplazamiento acumulado completa
    un loop_dur).
    """
    loop_audio = melody(notes, amp=amp, vibrato=vibrato)
    n_loop = len(loop_audio)
    n_total = int(dur_total * SR)
    phase_shift_samples = int(phase_shift_ms / 1000 * SR)

    synced = np.zeros(n_total)
    phased = np.zeros(n_total)

    # synced: simple repetición
    pos = 0
    while pos < n_total:
        end = min(pos + n_loop, n_total)
        synced[pos:end] += loop_audio[:end - pos]
        pos += n_loop

    # phased: cada repetición desplazada un poco más
    pos = 0
    loop_idx = 0
    while pos < n_total:
        offset = loop_idx * phase_shift_samples
        actual_pos = pos + offset
        if actual_pos >= n_total:
            break
        end = min(actual_pos + n_loop, n_total)
        phased[actual_pos:end] += loop_audio[:end - actual_pos]
        pos += n_loop
        loop_idx += 1

    return synced, phased


# ---------------------------------------------------------------------------
# FLUTE TRAVERSA — flauta traversa sintetica
# ---------------------------------------------------------------------------
#
# Espectro armonico basado en literatura de acustica musical (Fletcher &
# Rossing, "The Physics of Musical Instruments") + analisis FFT de samples
# de referencia (transverse flute C4 tenuto + A4):
#
#   armonico  ratio    nivel  notas
#       1     fund     0 dB   fundamental dominante
#       2     2x      -3 dB   muy presente (caracter "hueco" de la flauta)
#       3     3x     -12 dB
#       4     4x     -18 dB
#       5     5x     -22 dB
#       6+    fade rapido — atenuacion progresiva para evitar fritura
#
# Componentes adicionales que dan REALISMO:
#   - breath_noise: ruido pasa-banda 1.5-3 kHz, sutil (lo que diferencia
#     una flauta sintetica "fria" de una "viva")
#   - chiff: burst breve de aire al ataque (50ms), filtrado 800-2500 Hz
#   - vibrato: 5 Hz, depth 2.5% del freq (vibrato natural de soplo)
#   - ADSR: attack 80ms (no percutivo), release 250ms suave
#
# Lo IMPORTANTE para no aturdir (anti-fritura):
#   - los armonicos > 5to estan muy atenuados o eliminados
#   - LPF defensivo 4500 Hz al final corta cualquier brillo restante
#   - el breath noise ESTA en 1.5-3 kHz pero su nivel es muy bajo (0.04)

def flute_traversa(freq, dur, amp=0.5, vibrato=True, vibrato_rate=5.0,
                   vibrato_depth=0.025, breath_amount=0.015,
                   chiff_amount=0.04, attack_ms=80, release_ms=250,
                   warm=True):
    """Flauta traversa sintetica.

    Args:
      freq: frecuencia fundamental (Hz)
      dur: duracion total de la nota (segundos)
      amp: amplitud peak (0-1)
      vibrato: aplicar vibrato natural
      vibrato_rate: frecuencia del vibrato (Hz). Default 5 Hz (humano)
      vibrato_depth: profundidad relativa del vibrato (0.025 = 2.5%)
      breath_amount: cantidad de breath noise filtrado (0.04 sutil, 0.10 evidente)
      chiff_amount: cantidad de aire en el ataque (0.06 sutil)
      attack_ms: ataque en milisegundos (80 = no percutivo)
      release_ms: release en milisegundos (250 = suave)

    Returns:
      1D numpy array (mono).
    """
    from scipy.signal import butter, filtfilt
    n = int(dur * SR)
    t = np.linspace(0, dur, n, False)

    # Vibrato natural: modulacion de frecuencia 5 Hz, depth 2.5%
    if vibrato:
        vib_mod = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    else:
        vib_mod = np.ones(n)

    # Espectro armonico de la flauta (ratio, nivel relativo).
    # warm=True (default): bajamos 2do armonico (caia en zona HOT 1500-4000 con A5
    # — su 2do esta en 1760, dentro de la zona Fletcher-Munson) y bajamos 3ro/4to
    # tambien. Resultado: timbre mas "calido" tipo aulos griego, menos "moderno
    # piccolo". Anti-fritura por design.
    if warm:
        harmonics = [
            (1.0, 1.00),    # fundamental dominante
            (2.0, 0.40),    # 2do bajado (era 0.70 = -8 dB) — corta brillo HOT
            (3.0, 0.12),    # 3ro suave (-18 dB)
            (4.0, 0.05),    # 4to muy bajo
            (5.0, 0.02),    # 5to casi inaudible
        ]
    else:
        harmonics = [
            (1.0, 1.00),
            (2.0, 0.70),    # version "bright" (mas piccolo)
            (3.0, 0.25),
            (4.0, 0.13),
            (5.0, 0.08),
            (6.0, 0.04),
        ]
    # Suma de armonicos con vibrato aplicado en la fase
    wave = np.zeros(n)
    phase_base = 2 * np.pi * np.cumsum(freq * vib_mod) / SR
    for ratio, level in harmonics:
        # Cada armonico atenua un poco mas en agudos (anti-fritura zona Fletcher)
        if freq * ratio > 4500:
            continue   # corta armonicos arriba de 4.5 kHz directamente
        wave += level * np.sin(ratio * phase_base)
    wave /= sum(level for r, level in harmonics if freq * r <= 4500)

    # Breath noise: ruido pasa-banda 1.5-3 kHz, sutil. Da "vida"
    if breath_amount > 0:
        breath = np.random.randn(n)
        nyq = SR / 2
        b, a = butter(4, [1500 / nyq, 3000 / nyq], btype='band')
        breath = filtfilt(b, a, breath)
        m = float(np.abs(breath).max())
        if m > 0:
            breath /= m
        # Modular el breath con el envelope general (mas notable en sustain)
        wave += breath_amount * breath

    # Chiff de ataque: burst de aire breve filtrado pasa-banda 800-2500 Hz
    if chiff_amount > 0:
        chiff_n = min(int(0.05 * SR), n)
        if chiff_n > 32:
            chiff = np.random.randn(chiff_n)
            nyq = SR / 2
            b, a = butter(4, [800 / nyq, 2500 / nyq], btype='band')
            chiff = filtfilt(b, a, chiff)
            chiff_env = np.exp(-np.linspace(0, 6, chiff_n))
            m = float(np.abs(chiff).max())
            if m > 0:
                chiff /= m
            wave[:chiff_n] += chiff_amount * chiff * chiff_env

    # ADSR — attack suave (no percutivo), release suave
    attack_n = min(int(attack_ms / 1000 * SR), n // 2)
    release_n = min(int(release_ms / 1000 * SR), n // 2)
    env = np.ones(n)
    if attack_n > 0:
        # Curva sqrt para ataque smooth (mas natural que linear)
        env[:attack_n] = np.linspace(0, 1, attack_n) ** 0.5
    if release_n > 0:
        # Curva potencia 0.7 para release suave
        env[-release_n:] = np.linspace(1, 0, release_n) ** 0.7
    wave *= env

    # LPF defensivo — corta cualquier contenido > 4500 Hz que haya quedado
    # (chiff/breath pueden tener tail leakage)
    wave = lpf(wave, 4500)

    return amp * wave


def flute_motif(notes, amp=0.45, vibrato=True, attack_ms=80, release_ms=250,
                breath_amount=0.04, chiff_amount=0.06):
    """Toca una secuencia de notas (freq_hz, dur_sec) con flute_traversa.
    Equivalente a melody() pero usando el sintetizador de flauta.
    """
    chunks = []
    for freq, dur in notes:
        chunks.append(flute_traversa(freq, dur, amp=amp, vibrato=vibrato,
                                       attack_ms=attack_ms, release_ms=release_ms,
                                       breath_amount=breath_amount,
                                       chiff_amount=chiff_amount))
    return np.concatenate(chunks)
