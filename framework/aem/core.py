"""Constantes y helpers temporales del framework."""

import numpy as np

SR = 44100  # sample rate global — release standard (CD/streaming)


def t_arr(dur):
    """Vector de tiempo en segundos para `dur` segundos al sample rate global."""
    return np.linspace(0, dur, int(dur * SR), False)
