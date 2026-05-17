import numpy as np
from scipy.io import wavfile
from scipy import signal
import os

SR = 22050
DUR = 30
OUT = '/sessions/gracious-determined-faraday/mnt/My First Album/maquetas/'

def t(d): return np.linspace(0, d, int(d*SR), False)
def sine(f, d, a=0.3): return a*np.sin(2*np.pi*f*t(d))
def noise(d, a=0.1): return a*np.random.randn(int(d*SR))

def detuned(f, d, n=3, cents=10, a=0.3):
    out = np.zeros(int(d*SR))
    for i in range(n):
        df = f * 2**(((i-(n-1)/2)*cents)/1200)
        out += sine(df, d, a/n)
    return out

def lpf(audio, cutoff):
    nyq = SR/2
    b, a = signal.butter(2, cutoff/nyq, btype='low')
    return signal.filtfilt(b, a, audio)

def hpf(audio, cutoff):
    nyq = SR/2
    b, a = signal.butter(2, cutoff/nyq, btype='high')
    return signal.filtfilt(b, a, audio)

def fade(audio, fi=2, fo=2):
    out = audio.copy()
    fi_n, fo_n = int(fi*SR), int(fo*SR)
    if fi_n: out[:fi_n] *= np.linspace(0,1,fi_n)
    if fo_n: out[-fo_n:] *= np.linspace(1,0,fo_n)
    return out

def reverb(audio, decay=2.0, mix=0.3):
    out = audio * (1 - mix*0.5)
    delays_ms = [37, 53, 79, 113, 173, 251, 379]
    for dm in delays_ms:
        ds = int(dm/1000*SR)
        if ds >= len(audio): continue
        g = (decay/4)**(dm/200) * mix / len(delays_ms) * 1.5
        delayed = np.zeros_like(audio)
        delayed[ds:] = audio[:-ds] * g
        out += delayed
    return out

def kick(t_start, dur=0.5, f0=80, fe=40, sr=SR):
    n = int(dur*sr)
    ta = np.linspace(0, dur, n, False)
    fr = fe + (f0-fe)*np.exp(-ta*8)
    ph = 2*np.pi*np.cumsum(fr)/sr
    env = np.exp(-ta*6)
    return env*np.sin(ph)

def hihat(dur=0.04):
    n = int(dur*SR)
    ta = np.linspace(0, dur, n, False)
    return np.exp(-ta*80)*np.random.randn(n)*0.3

def add_at(audio, t_start, sample, gain=1.0):
    ns = int(t_start*SR)
    ne = min(ns+len(sample), len(audio))
    audio[ns:ne] += sample[:ne-ns]*gain
    return audio

def voice(f, d, vr=5, vd=0.005, a=0.25):
    ta = t(d)
    vib = 1 + vd*np.sin(2*np.pi*vr*ta)
    fm = f*vib
    ph = 2*np.pi*np.cumsum(fm)/SR
    return a*(np.sin(ph) + 0.5*np.sin(2*ph) + 0.3*np.sin(3*ph))/1.8

def norm(audio, peak=0.85):
    m = np.max(np.abs(audio))
    return audio*(peak/m) if m > 0 else audio

def save(name, audio):
    wavfile.write(OUT+name, SR, np.int16(norm(audio)*32767))

# --- 1. AMBIENT DRONE (Roach-style, F lydian)
def m1():
    o = np.zeros(int(DUR*SR))
    o += detuned(87.31, DUR, 3, 12, 0.12)
    o += detuned(174.61, DUR, 3, 8, 0.10)
    o += detuned(220.00, DUR, 3, 5, 0.08)
    o += detuned(246.94, DUR, 3, 5, 0.06)
    o += sine(42, DUR, 0.10)
    o += lpf(noise(DUR, 0.06), 800)
    o = lpf(o, 2500)
    o = reverb(o, 4.0, 0.45)
    return fade(o, 5, 5)

# --- 2. CINEMATIC EMOTIONAL (Zimmer-style D minor, build)
def m2():
    o = np.zeros(int(DUR*SR))
    full_t = t(DUR)
    o += sine(73.42, DUR, 0.15)
    o += voice(146.83, DUR, 4, 0.005, 0.10)
    o += voice(174.61, DUR, 4, 0.005, 0.08)
    o += voice(220.00, DUR, 4, 0.005, 0.06)
    env = np.linspace(0.3, 1.0, len(full_t))
    o *= env
    v4 = voice(293.66, DUR, 4, 0.005, 0.10)
    e4 = np.zeros(len(full_t))
    half = len(full_t)//2
    e4[half:] = np.linspace(0, 1, len(full_t)-half)
    o += v4 * e4
    o += sine(42, DUR, 0.08)
    o = reverb(o, 3.0, 0.40)
    return fade(o, 2, 4)

# --- 3. VOCAL SACRED (Lisa Gerrard, D minor parallel fifths)
def m3():
    o = np.zeros(int(DUR*SR))
    v1 = voice(293.66, DUR, 5, 0.008, 0.15)
    v2 = voice(440.00, DUR, 4.5, 0.007, 0.12)
    v3 = voice(587.33, DUR, 4.8, 0.009, 0.08)
    breath = 0.7 + 0.3*np.sin(2*np.pi*0.1*t(DUR))
    o += (v1+v2+v3) * breath
    o += sine(146.83, DUR, 0.10) + sine(220.00, DUR, 0.08)
    o += sine(42, DUR, 0.06)
    o = reverb(o, 5.0, 0.55)
    return fade(o, 3, 4)

# --- 4. DUB-TECHNO EMERGENT (Donato Dozzy, C minor)
def m4():
    o = np.zeros(int(DUR*SR))
    o += sine(65.41, DUR, 0.10)
    o += detuned(130.81, DUR, 3, 8, 0.08)
    o += detuned(155.56, DUR, 3, 8, 0.06)
    o += detuned(196.00, DUR, 3, 8, 0.04)
    o += sine(42, DUR, 0.08)
    bpm = 65
    iv = 60/bpm
    nk = int((DUR-8)/iv)
    for i in range(nk):
        ts = 8 + i*iv
        ks = kick(ts, 0.6, 80, 40)
        o = add_at(o, ts, ks, 0.4)
    nh = int((DUR-12)/iv*2)
    for i in range(nh):
        ts = 12 + i*iv/2 + iv/2
        if ts < DUR-0.1:
            hh = hpf(hihat(0.05), 6000)
            o = add_at(o, ts, hh, 0.15)
    o = reverb(o, 3.0, 0.30)
    return fade(o, 2, 4)

# --- 5. TECTONIC PULSE (Lustmord 30 BPM ritual)
def m5():
    o = np.zeros(int(DUR*SR))
    o += sine(43.65, DUR, 0.10)
    o += detuned(87.31, DUR, 3, 10, 0.10)
    o += detuned(110.00, DUR, 3, 8, 0.06)
    o += sine(42, DUR, 0.10)
    iv = 2.0
    np_ = int(DUR/iv)
    for i in range(np_):
        ts = i*iv
        p = kick(ts, 1.0, 60, 28)
        o = add_at(o, ts, p, 0.40)
    o += voice(174.61, DUR, 3, 0.005, 0.06)
    o = reverb(o, 4.0, 0.40)
    return fade(o, 3, 4)

# --- 6. BROKEN TECHNO (Burial-style 90 BPM irregular)
def m6():
    o = np.zeros(int(DUR*SR))
    o += sine(98.00, DUR, 0.07)
    o += sine(196.00, DUR, 0.05)
    o += sine(233.08, DUR, 0.04)
    o += sine(42, DUR, 0.08)
    bpm = 90
    iv = 60/bpm
    pat = [1,0,0,1,0,1,0,0]
    ns = int(DUR/iv)
    for i in range(ns):
        if pat[i % len(pat)]:
            ts = i*iv
            ks = kick(ts, 0.4, 70, 35)
            o = add_at(o, ts, ks, 0.45)
    for i in range(ns):
        if i % 4 == 2:
            ts = i*iv
            sn_n = int(0.1*SR)
            sn = hpf(np.random.randn(sn_n)*np.exp(-np.linspace(0,30,sn_n)), 1500)
            o = add_at(o, ts, sn, 0.30)
    rng = np.random.default_rng(7)
    for i in range(ns*2):
        if rng.random() > 0.5:
            ts = i*iv/2
            if ts < DUR-0.1:
                o = add_at(o, ts, hihat(0.05), 0.2)
    o = reverb(o, 2.5, 0.30)
    return fade(o, 1, 4)

# --- 7. HYPNOTIC ACID TECHNO (Donato Dozzy K, 90 BPM steady)
def m7():
    o = np.zeros(int(DUR*SR))
    o += sine(73.42, DUR, 0.06)
    o += sine(146.83, DUR, 0.05)
    o += sine(42, DUR, 0.08)
    bpm = 90
    iv = 60/bpm
    ns = int(DUR/iv)
    for i in range(ns):
        ts = i*iv
        ks = kick(ts, 0.4, 70, 35)
        o = add_at(o, ts, ks, 0.5)
    bass_seq = [73.42, 73.42, 87.31, 73.42, 110.00, 73.42, 87.31, 110.00]
    bass_o = np.zeros(int(DUR*SR))
    for i in range(ns):
        note = bass_seq[i % len(bass_seq)]
        ts = i*iv
        nd = iv*0.85
        n_ = int(nd*SR)
        ta = np.linspace(0, nd, n_, False)
        sample = 2*(note*ta - np.floor(0.5+note*ta))
        env = np.exp(-ta*1.8)
        sample = sample*env*0.3
        bass_o = add_at(bass_o, ts, sample, 1.0)
    bass_o = lpf(bass_o, 700)
    o += bass_o*0.4
    for i in range(ns*2):
        ts = i*iv/2 + iv/2
        if ts < DUR-0.1:
            o = add_at(o, ts, hihat(0.04), 0.15)
    o = reverb(o, 2.0, 0.25)
    return fade(o, 1, 4)

# --- 8. INDUSTRIAL DARK (Annihilation, dissonant low drones + clanks)
def m8():
    o = np.zeros(int(DUR*SR))
    o += sine(36.71, DUR, 0.10)
    o += detuned(73.42, DUR, 3, 15, 0.08)
    o += detuned(110.00, DUR, 3, 10, 0.05)
    o += sine(85, DUR, 0.04)
    o += sine(42, DUR, 0.10)
    rng = np.random.default_rng(42)
    times = sorted(rng.uniform(2, DUR-2, 10))
    for ts in times:
        n_ = int(0.3*SR)
        ta = np.linspace(0, 0.3, n_, False)
        cl = (np.sin(2*np.pi*1300*ta) + 0.5*np.sin(2*np.pi*1850*ta) + 0.3*np.sin(2*np.pi*2400*ta))
        cl *= np.exp(-ta*4)
        o = add_at(o, ts, cl, 0.18)
    o = np.tanh(o*1.5)*0.7
    o = reverb(o, 3.0, 0.40)
    return fade(o, 2, 4)

maquetas = [
    ('m1_ambient_drone.wav', m1),
    ('m2_cinematic.wav', m2),
    ('m3_vocal_sacred.wav', m3),
    ('m4_dub_techno.wav', m4),
    ('m5_tectonic.wav', m5),
    ('m6_broken_techno.wav', m6),
    ('m7_acid_techno.wav', m7),
    ('m8_industrial.wav', m8),
]
for name, fn in maquetas:
    save(name, fn())
    print(f'OK {name}')
print('done')
