# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import io

import numpy as np
import six

from .parameter import parse_parameter


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
        """
        if self._zrange is None:
            self._zrange = self.data.ptp()
        return self._zrange

    @property
    def rms(self):
        """
        Returns the root mean square roughness of the data.
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
        """
        Read the raw data for the specified image type if it is in the file.

        :param image_type: String indicating which image type to read.
                           Only accepts 'Height', 'Amplitude', and 'Phase'
        :returns: A NanoscopeImage instance of the specified type
        :raises ValueError: If image_type is a nonsupported type
        :raises ValueError: If the image_type indicated is not in the file
        """
        if image_type not in ['Height', 'Amplitude', 'Phase']:
            raise ValueError('Unsupported image type {0}'.format(image_type))
        if image_type not in self.config['_Images']:
            raise ValueError('Image type {0} not in file.'.format(image_type))
        config = self.config['_Images'][image_type]
        with io.open(self.filename, 'rb') as f:
            f.seek(config['Data offset'])
            num = int(config['Data length'] / config['Bytes/pixel'])
            raw_data = np.fromstring(f.read(config['Data length']),
                                     dtype='<{0}h'.format(num))
            raw_data = raw_data.reshape((config['Number of lines'],
                                         config['Samps/line']))
        self.images[image_type] = NanoscopeImage(
            image_type,
            raw_data,
            self.config['Sens. Zscan'],
            self.config['_Images'][image_type]['Bytes/pixel'],
            self.config['_Images'][image_type]['Z magnify'],
            self.config['_Images'][image_type]['Z scale']
        )
        return self.images[image_type]

    def read_file(self):
        """
        Read the header and raw data for all images.
        """
        self.read_header()
        for image_type in six.iterkeys(self.config['_Images']):
            self.read_image_data(image_type)

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
