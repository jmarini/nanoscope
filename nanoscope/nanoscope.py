# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import io
import struct

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
        self.read_header()
        if 'Height' in self.images:
            self.height['Raw data'] = self._read_image_data(self.height)
            self.height['Flattened data'] = np.array([])
            for line in self.height['Raw data']:
                self.height['Flattened data'].append(self._flatten_scanline(line))

    def read_header(self):
        with io.open(self.filename, 'r', encoding=self.encoding) as f:
            for line in f:
                parameter = parse_parameter(line.rstrip('\n'))
                if self._handle_parameter(parameter, f):
                    return

    def _handle_parameter(self, parameter, f):
        if parameter.type == 'H':  # header
            if parameter.header == 'File list end':
                return True
            if parameter.header == 'Ciao image list':
                return self._handle_parameter(self._read_image_header(f), f)
        elif parameter.type != 'S':
            self.config[parameter.parameter] = parameter.hard_value
        return False

    def _read_image_header(self, f):
        image_config = {}
        for line in f:
            parameter = parse_parameter(line.rstrip('\n'))
            if parameter.type == 'H':
                return parameter
            if parameter.type == 'S':
                if parameter.parameter == 'Image Data':
                    image_config['Image Data'] = parameter.internal_designation
                    self.images[parameter.internal_designation] = image_config
            else:
                image_config[parameter.parameter] = parameter.hard_value

    def _read_image_data(self, config):
        with io.open(self.filename, 'rb') as f:
            f.seek(config['Data offset'])
            num = int(config['Data length'] / config['Bytes/pixel'])
            raw_data = np.array(struct.unpack_from(
                '<{0}h'.format(num), f.read(config['Data length'])))
            raw_data = raw_data.reshape((config['Number of lines'],
                                         config['Samps/line']))
            return raw_data

    def _flatten_scanline(self, data, order=1):
        coefficients = np.polyfit(range(len(data)), data, order)
        correction = np.array(
            [sum([pow(i, n) * c
            for n, c in enumerate(reversed(coefficients))])
            for i in range(len(data))])
        return data - correction
