# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import numpy as np


class NanoscopeImage(object):
    """
    Holds the data associated with a Nanoscope image.
    """

    def __init__(self, image_type, raw_data, sensitivity, bytes_per_pixel,
                 magnify, scale):
        self.sensitivity = sensitivity
        self.bytes_per_pixel = bytes_per_pixel
        self.magnify = magnify
        self.scale = scale
        self.raw_data = raw_data
        self.flat_data = None
        self.converted_data = None
        self.type = image_type
        self.height_scale = self.sensitivity * self.magnify * self.scale
        self._rms = None
        self._zrange = None

    @property
    def data(self):
        """
        Returns the most processed form of the data.
        """
        if self.converted_data is None:
            if self.flat_data is None:
                return self.raw_data
            return self.flat_data
        return self.converted_data

    def process(self, order=1):
        """
        Flattens and converts the raw data. Convenience function that reduces
        the manual steps needed.

        :param order: The order of the polynomial to use when flattening.
                      Defaults to 1 (linear), which should give good results
                      for most images.
        :returns: The image with flattened and converted data for chaining
                  commands.
        """
        return self.flatten(order).convert()

    def flatten(self, order=1):
        """
        Flattens the raw data, by fitting each scanline to a polynomial with
        the order specified and subtracting that fit from the raw data.

        Typically happens prior to converting from raw data.

        :param order: The order of the polynomial to use when flattening.
                      Defaults to 1 (linear).
        :returns: The image with flattened data for chaining commands.
        """
        self.flat_data = np.round([self._flatten_scanline(line, order)
                                   for line in self.raw_data])
        self._reset_cached()
        return self

    def convert(self):
        """
        Converts the raw data into data with the proper units for that image
        type (i.e. nm for Height, V for Amplitude).

        Typically happens after flattening the data.

        :returns: The image with converted data for chaining commands.
        """
        if self.flat_data is None:
            self.flat_data = self.raw_data
        value = self.sensitivity * self.scale / pow(2, 8 * self.bytes_per_pixel)
        self.converted_data = self.flat_data * value
        self._reset_cached()
        return self

    def colorize(self, colortable=12):
        """
        Colorizes the data according to the specified height scale. Currently
        uses colorscale #12 from Nanoscope as hardcoded behavior.

        :param colortable: The Nanoscope colortable to use.
                           Only 12 is supported, and is the default.
        :returns: The pixels of the image ready for use with
                  ``Pillow.Image.fromarray``.
        :raises ValueError: If the colortable is not supported.
        """
        if colortable != 12:
            raise ValueError('Only colortable #12 is currently supported')

        colors = {
            'r': (lambda p: np.clip(np.round(
                p * (10200 / 37) - (765 / 37)), 0, 255)),
            'g': (lambda p: np.clip(np.round(
                p * (30600 / 73) - (11985 / 73)), 0, 255)),
            'b': (lambda p: np.clip(np.round(
                p * (6800 / 9) - (4505 / 9)), 0, 255)),
        }
        get_color = (lambda v:
            np.array([colors[c]((v + (self.height_scale / 2)) /
                                self.height_scale) for c in 'rgb']))
        if self.converted_data is None:
            self.converted_data = self.data

        data = []
        for row in reversed(self.converted_data):
            data.append([])
            for col in row:
                data[-1].append(get_color(col))
        return np.array(data, dtype=np.uint8)

    def reset_height_scale(self):
        """
        Resets the height scale to the original value from the file.
        """
        self.height_scale = self.sensitivity * self.magnify * self.scale

    @property
    def zrange(self):
        """
        Returns the z-range of the data, the difference between the maximum and
        minimum values.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if self._zrange is None:
            self._zrange = self.data.ptp()
        return self._zrange

    @property
    def rms(self):
        """
        Returns the root mean square roughness of the data.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if self._rms is None:
            self._rms = np.sqrt(np.sum(np.square(self.data)) / self.data.size)
        return self._rms

    def _flatten_scanline(self, data, order=1):
        coefficients = np.polyfit(range(len(data)), data, order)
        correction = np.array(
            [sum([pow(i, n) * c
            for n, c in enumerate(reversed(coefficients))])
            for i in range(len(data))])
        return data - correction

    def _reset_cached(self):
        self._rms = self._zrange = None
