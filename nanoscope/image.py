# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import numpy as np


class NanoscopeImage(object):
    """
    Holds the data associated with a Nanoscope image.
    """
    supported_colortables = {
        12: {
            'r': (lambda p: np.clip(np.round(
                  p * (10200 / 37) - (765 / 37)), 0, 255)),
            'g': (lambda p: np.clip(np.round(
                  p * (30600 / 73) - (11985 / 73)), 0, 255)),
            'b': (lambda p: np.clip(np.round(
                  p * (6800 / 9) - (4505 / 9)), 0, 255)),
        },
    }

    def __init__(self, image_type, raw_data, sensitivity, bytes_per_pixel,
                 magnify, scale, scan_area):
        self.sensitivity = sensitivity
        self.bytes_per_pixel = bytes_per_pixel
        self.magnify = magnify
        self.scale = scale
        self.raw_data = raw_data
        self.flat_data = None
        self.converted_data = None
        self.type = image_type
        self.height_scale = self.sensitivity * self.magnify * self.scale
        self.scan_area = scan_area

        self._cache = {}

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
        self._cache.clear()
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
        self._cache.clear()
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
        if colortable not in self.supported_colortables:
            raise ValueError('Colortable {} is not '
                             'currently supported'.format(colortable))

        colors = self.supported_colortables[colortable]
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
    def mean_height(self):
        """
        Returns the mean height of the data in nm. For a typical processed
        scan, this value should be about zero.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'mean_height' not in self._cache:
            self._cache['mean_height'] = np.mean(self.data)
        return self._cache['mean_height']

    @property
    def mean_roughness(self):
        """
        Returns the mean roughness of the data in nm.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'mean_roughness' not in self._cache:
            self._cache['mean_roughness'] = np.mean(np.abs(self.data - self.mean_height))
        return self._cache['mean_roughness']

    @property
    def rms_roughness(self):
        """
        Returns the root mean square roughness of the data in nm.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'rms_roughness' not in self._cache:
            self._cache['rms_roughness'] = (
                np.sqrt(np.sum(np.square(
                    self.data - self.mean_height)) / self.data.size))
        return self._cache['rms_roughness']

    @property
    def total_roughness(self):
        """
        Returns the total roughness of the data in nm. This is defined as the
        difference between the highest peak and the lowest valley.
        """
        return self.max_valley + self.max_peak

    @property
    def max_valley(self):
        """
        Returns the depth of the lowest valley in nm. A valley is defined
        relative to the mean height (typically 0nm).
        """
        return abs(self.min_height - self.mean_height)

    @property
    def max_peak(self):
        """
        Returns the height of the highest valley in nm. A peak is defined
        relative to the mean height (typically 0nm).
        """
        return self.max_height - self.mean_height

    @property
    def mean_valley(self):
        """
        Returns the depth of the average valley in nm. A valley is defined
        relative to the mean height (typically 0nm).

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'mean_valley' not in self._cache:
            valley_elems = self.data[self.data < self.mean_height]
            self._cache['mean_valley'] = (
                np.sum(np.abs(
                    valley_elems - self.mean_height)) / valley_elems.size)
        return self._cache['mean_valley']

    @property
    def mean_peak(self):
        """
        Returns the height of the average peak in nm. A peak is defined
        relative to the mean height (typically 0nm).

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'mean_peak' not in self._cache:
            peak_elems = self.data[self.data > self.mean_height]
            self._cache['mean_peak'] = (
                np.sum(peak_elems - self.mean_height) / peak_elems.size)
        return self._cache['mean_peak']

    @property
    def mean_total_roughness(self):
        """
        Returns the mean total roughness in nm. This is defined as the
        difference between the mean peak and valley.
        """
        return self.mean_peak + self.mean_valley

    @property
    def min_height(self):
        """
        Returns the minimum height in the image in nm.

        The value is calculated on first access and cached for later. Running
        convert or flatten will force a recalculation on the next access.
        """
        if 'min_height' not in self._cache:
            self._cache['min_height'] = np.min(self.data)
        return self._cache['min_height']

    @property
    def max_height(self):
        """
        Returns the maximum height in the image in nm.

        The value is calculated on first access and cached for later. Running
        conver or flatten will force a recalculation on the next access.
        """
        if 'max_height' not in self._cache:
            self._cache['max_height'] = np.max(self.data)
        return self._cache['max_height']

    def n_point_roughness(self, n=5):
        """
        Returns the average roughness in nm, defined as the mean of the n
        highest peaks and n lowest valleys.

        :param n: The number of points to take from both peaks and valleys.
        :returns: The average roughness of the n highest peaks and n lowest
                  valleys, in nm.
        """
        peak_elems = np.sort(self.data[self.data > self.mean_height])[-n:]
        valley_elems = np.sort(self.data[self.data < self.mean_height])[:n]
        return np.mean(peak_elems + valley_elems)

    def peak_count(self, threshold=None):
        """
        Calculates the total number of peaks and valleys in the image. A peak
        or valley is defined as any feature that exceeds the provided threshold.

        :param threshold: The threshold to use for defining a peak or valley.
                          Defaults to the mean roughness (Ra).
        :returns: The total number of peaks and valleys in the image.
        """
        threshold = threshold or self.mean_roughness
        return self.data[np.abs(self.data) >= abs(threshold)].size

    def peak_density(self, threshold=None):
        """
        Calclulates the number of peaks or valleys per unit area in the image,
        with units of peaks per square μm. A peak or valley is defined as any
        feature that exceeds the provided threshold.

        :param threshold: The threshold to use for defining a peak or valley.
                          Defaults to the mean roughness (Ra).
        :returns: The number of peaks and valleys in the image per square μm.
        """
        return self.peak_count(threshold) / self.scan_area

    def high_spot_count(self, threshold=None):
        threshold = threshold or self.mean_roughness
        return self.data[self.data >= threshold].size

    def low_spot_count(self, threshold=None):
        threshold = threshold or self.mean_roughness
        return self.data[self.data <= threshold].size

    def _flatten_scanline(self, data, order=1):
        coefficients = np.polyfit(range(len(data)), data, order)
        correction = np.array(
            [sum([pow(i, n) * c
            for n, c in enumerate(reversed(coefficients))])
            for i in range(len(data))])
        return data - correction

    Ra = mean_roughness
    Rq = rms_roughness
    rms = rms_roughness
    Rp = max_peak
    Rv = max_valley
    Rt = total_roughness
    zrange = total_roughness
    Rpm = mean_peak
    Rvm = mean_valley
    Rz = property(lambda self: self.n_point_roughness(n=5))
    Pc = property(lambda self: self.peak_count(self.mean_roughness))
    Pd = property(lambda self: self.peak_density(self.mean_roughness))
    HSC = property(lambda self: self.high_spot_count(self.mean_roughness))
    LSC = property(lambda self: self.low_spot_count(self.mean_roughness))
