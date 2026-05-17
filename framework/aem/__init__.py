"""ÆM composition framework — multi-pista declarativo, render offline a WAV.

Modulos:
    core         - constantes (SR) y helpers temporales
    synth        - primitivas de sintesis (sine, saw, noise, silence)
    instruments  - composites (drone, voice_pad, kick, hihat, melody, riser)
    effects      - efectos por pista (fade, lpf, hpf, reverb, distort)
    master       - efectos de master sobre el estereo final (dirty_intro)
    composition  - Track + Composition (render, stems, export)

Uso tipico:
    from aem import Composition, Track
    from aem.synth import sine
    from aem.instruments import detuned_drone
    from aem.effects import fade, reverb
    from aem.master import dirty_intro

    comp = Composition(60, name='ejemplo')
    drone = comp.add_track(Track('drone', gain=0.4))
    drone.add(0, detuned_drone([220, 277], 60))
    drone.fx(lambda a: fade(a, fi=4, fo=4))
    drone.fx(lambda a: reverb(a, decay=3, mix=0.4))
    comp.export_wav('out.wav', master_fx=lambda a: dirty_intro(a, 8, 4))
"""

from .core import SR, t_arr
from .composition import Track, Composition

__all__ = ['SR', 't_arr', 'Track', 'Composition']
