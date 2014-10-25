# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import io

import numpy as np

from .parameter import parse_parameter


class NanoscopeParser(object):
    """
    Handles reading and parsing Nanoscope files.
    """

    def __init__(self, filename, encoding='cp1252'):
        self.filename = filename
        self.encoding = encoding
        self.images = {}
        self.config = {}

    @property
    def height(self):
        """
        Return the height image if it exists, else ``None``.
        """
        return self.images.get('Height', None)

    @property
    def amplitude(self):
        """
        Return the amplitude image if it exists, else ``None``.
        """
        return self.images.get('Amplitude', None)

    @property
    def phase(self):
        """
        Return the phase image if it exists, else ``None``.
        """
        return self.images.get('Phase', None)

    def read_nanoscope(self):
        """
        Read in the nanoscope file and convert the raw data.
        """
        self._read_header()
        for image in self.images:
            self._read_image_data(image)

    def _read_header(self):
        with io.open(self.filename, 'r', encoding=self.encoding) as f:
            for line in f:
                parameter = parse_parameter(line.rstrip('\n'))
                self._handle_parameter(parameter, f)

    def _handle_parameter(self, parameter, f):
        if parameter.type == 'H':  # header
            if parameter.header == 'File list end':
                return
            elif parameter.header == 'Ciao image list':
                self._handle_parameter(self._read_image_header(f), f)
        elif parameter.type != 'S':
            self.config[parameter.parameter] = parameter.hard_value

    def _read_image_header(self, f):
        image_config = {}
        for line in f:
            parameter = parse_parameter(line.rstrip('\n'))
            if parameter.type == 'H':
                return parameter
            if parameter.type == 'S':
                if parameter.parameter == 'Image Data':
                    self.images[parameter.internal_designation] = image_config
            else:
                image_config[parameter.parameter] = parameter.hard_value

    def _read_image_data(self, config):
        pass

    def _flatten_scanline(self, data):
        a, b = np.polyfit(range(len(data)), data, 1)
        out = []
        for i, value in enumerate(data):
            out.append(value - (i * a + b))
        return out
