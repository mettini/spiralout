"""Primitivas de sintesis. Devuelven arrays mono float."""

import numpy as np

from .core import SR, t_arr


def sine(freq, dur, amp=1.0):
    return amp * np.sin(2 * np.pi * freq * t_arr(dur))


def saw(freq, dur, amp=1.0):
    ta = t_arr(dur)
    return amp * (2 * (freq * ta - np.floor(0.5 + freq * ta)))


def noise(dur, amp=1.0):
    return amp * np.random.randn(int(dur * SR))


def silence(dur):
    return np.zeros(int(dur * SR))
