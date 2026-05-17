"""Track + Composition: el modelo de dominio del framework.

Track  - una pista mono con gain, pan, eventos en el tiempo y cadena de fx.
Composition - el tema. Tiene duracion y una lista de tracks. Sabe renderizar
              estereo y exportar a WAV (master + stems individuales).
"""

import json
import os

import numpy as np
from scipy.io import wavfile

from .core import SR


class Track:
    def __init__(self, name, gain=1.0, pan=0.0, color=None):
        self.name = name
        self.gain = gain
        self.pan = pan
        self.color = color  # hint visual para la UI; opcional
        self.events = []
        self.effects = []

    def add(self, start_time, audio):
        self.events.append((start_time, audio))
        return self

    def fx(self, effect_fn):
        self.effects.append(effect_fn)
        return self

    def render_mono(self, total_dur):
        out = np.zeros(int(total_dur * SR))
        for start, audio in self.events:
            ns = int(start * SR)
            ne = min(ns + len(audio), len(out))
            out[ns:ne] += audio[:ne - ns]
        out *= self.gain
        for fn in self.effects:
            out = fn(out)
        return out


class Composition:
    def __init__(self, duration, name='untitled'):
        self.duration = duration
        self.name = name
        self.tracks = []

    def add_track(self, track):
        self.tracks.append(track)
        return track

    # ------------------------------------------------------------------
    # render
    # ------------------------------------------------------------------

    def _pan_stereo(self, mono, pan):
        """Aplica equal-power panning a un mono. Devuelve (L, R)."""
        angle = (pan + 1) * np.pi / 4
        return mono * np.cos(angle), mono * np.sin(angle)

    def render_stereo(self):
        n = int(self.duration * SR)
        master_l = np.zeros(n)
        master_r = np.zeros(n)
        for tr in self.tracks:
            mono = tr.render_mono(self.duration)
            l, r = self._pan_stereo(mono, tr.pan)
            master_l += l
            master_r += r
        return np.stack([master_l, master_r], axis=-1)

    # ------------------------------------------------------------------
    # export
    # ------------------------------------------------------------------

    def export_wav(self, filename, peak=0.85, master_fx=None):
        """Render full + export master a WAV."""
        audio = self.render_stereo()
        if master_fx is not None:
            audio = master_fx(audio)
        m = np.max(np.abs(audio))
        if m > 0:
            audio *= peak / m
        _ensure_parent(filename)
        wavfile.write(filename, SR, np.int16(audio * 32767))
        print(f'  master  -> {filename} ({self.duration}s)')
        return audio

    def export_stems(self, output_dir, master_fx=None, peak=0.85, write_manifest=True):
        """Renderiza cada track como WAV estereo en `output_dir`. Aplica el mismo
        factor de normalizacion del master (calculado a partir del mix completo)
        para que los stems suenen al mismo nivel relativo que en el master.

        El master_fx NO se aplica a los stems individuales (es un efecto sobre
        la suma — aplicarlo por stem produciria resultado distinto). Por eso
        sumar stems en la UI suena MUY similar al master pero NO identico.

        Devuelve dict con metadata de los stems exportados.
        """
        os.makedirs(output_dir, exist_ok=True)

        # paso 1 — render completo para calcular factor de normalizacion
        master = self.render_stereo()
        if master_fx is not None:
            master = master_fx(master)
        m = np.max(np.abs(master))
        norm = (peak / m) if m > 0 else 1.0

        # paso 2 — render por track con el mismo factor
        manifest_tracks = []
        for tr in self.tracks:
            mono = tr.render_mono(self.duration)
            l, r = self._pan_stereo(mono, tr.pan)
            stem = np.stack([l, r], axis=-1) * norm
            stem = np.clip(stem, -1.0, 1.0)
            filename = f'{tr.name}.wav'
            path = os.path.join(output_dir, filename)
            wavfile.write(path, SR, np.int16(stem * 32767))
            print(f'  stem    -> {path}')
            manifest_tracks.append({
                'name': tr.name,
                'file': filename,
                'gain': tr.gain,
                'pan': tr.pan,
                'color': tr.color,
                'peak': float(np.max(np.abs(stem))),
                'rms': float(np.sqrt(np.mean(stem ** 2))),
            })

        if write_manifest:
            manifest = {
                'name': self.name,
                'duration': self.duration,
                'sample_rate': SR,
                'norm_factor': float(norm),
                'tracks': manifest_tracks,
            }
            with open(os.path.join(output_dir, 'manifest.json'), 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f'  manifest-> {os.path.join(output_dir, "manifest.json")}')

        return manifest_tracks

    # ------------------------------------------------------------------
    # debug
    # ------------------------------------------------------------------

    def list_tracks(self):
        for tr in self.tracks:
            print(f'  {tr.name:25s} gain={tr.gain:.2f} pan={tr.pan:+.2f} '
                  f'events={len(tr.events)} fx={len(tr.effects)}')


def _ensure_parent(path):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
