# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import numpy as np


class NanoscopeParser(object):
    """
    Handles reading and parsing Nanoscope files.
    """

    def __init__(self, filename):
        self.filename = filename

    def _split_data(self, data, stride):
        """
        Split a 1d array into a 2d array
        """
        out = []
        for n, value in enumerate(data):
            if n % 512 == 0:
                out.append([])
            out[-1].append(value)
        return out

    def _flatten_scanline(self, data):
        a, b = np.polyfit(range(len(data)), data, 1)
        out = []
        for i, value in enumerate(data):
            out.append(value - (i * a + b))
        return out
