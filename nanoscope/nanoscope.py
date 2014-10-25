# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import io
import struct

import numpy as np

from .parameter import parse_parameter


class NanoscopeImage(object):
    """
    Holds the data associated with a Nanoscope image.
    """

    def __init__(self, config, raw_data):
        self.config = config
        self.raw_data = raw_data
        self.flat_data = None
        self.converted_data = None
        self.type = self.config.get('Image Data', 'Unknown')

    @property
    def data(self):
        if self.converted_data is None:
            if self.flat_data is None:
                return self.raw_data
            return self.flat_data
        return self.converted_data

    def flatten(self, order=1):
        self.flat_data = np.array([])
        for line in self.raw_data:
            self.flat_data.append(self._flatten_scanline(line, order))

    def convert(self):
        pass

    def process(self, order=1):
        self.flatten(order)
        self.convert()

    def _flatten_scanline(self, data, order=1):
        coefficients = np.polyfit(range(len(data)), data, order)
        correction = np.array(
            [sum([pow(i, n) * c
            for n, c in enumerate(reversed(coefficients))])
            for i in range(len(data))])
        return data - correction


class NanoscopeParser(object):
    """
    Handles reading and parsing Nanoscope files.
    """

    def __init__(self, filename, encoding='cp1252'):
        self.filename = filename
        self.encoding = encoding
        self.images = {}
        self.config = {'_Images': {}}

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

    def read_header(self):
        """
        Read the Nanoscope file header.
        """
        with io.open(self.filename, 'r', encoding=self.encoding) as f:
            for line in f:
                parameter = parse_parameter(line.rstrip('\n'))
                if parameter.type != 'H' and parameter.parameter == 'Version':
                    if parameter.hard_value not in ['0x05120130']:
                        raise ValueError('Unsupported file version {0}'.format(
                            parameter.hard_value))
                if self._handle_parameter(parameter, f):
                    return

    def read_image_data(self, image_type):
        if image_type not in ['Height', 'Amplitude', 'Phase']:
            raise ValueError('Unsupported image type {0}'.format(image_type))
        if image_type not in self.config['_Images']:
            raise ValueError('Image type {0} not in file.'.format(image_type))
        config = self.config['_Images'][image_type]
        with io.open(self.filename, 'rb') as f:
            f.seek(config['Data offset'])
            num = int(config['Data length'] / config['Bytes/pixel'])
            raw_data = np.array(struct.unpack_from(
                '<{0}h'.format(num), f.read(config['Data length'])))
            raw_data = raw_data.reshape((config['Number of lines'],
                                         config['Samps/line']))
        self.images[image_type] = NanoscopeImage(self.config['_Images'][image_type],
                                                 raw_data)
        return self.images[image_type]

    def flatten_image(self, raw_data, order=1):
        flat_data = []
        for line in raw_data:
            flat_data.append(self._flatten_scanline(line, order))
        return np.array(flat_data)

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
                    image_config['Image Data'] = parameter.internal
                    self.config['_Images'][parameter.internal] = image_config
            else:
                image_config[parameter.parameter] = parameter.hard_value

    def _flatten_scanline(self, data, order=1):
        coefficients = np.polyfit(range(len(data)), data, order)
        correction = np.array(
            [sum([pow(i, n) * c
            for n, c in enumerate(reversed(coefficients))])
            for i in range(len(data))])
        return data - correction
