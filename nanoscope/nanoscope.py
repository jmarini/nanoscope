# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import io

import numpy as np
import six

from .image import NanoscopeImage
from .parameter import parse_parameter


def read(f, encoding='utf-8', header_only=False):
    """
    Reads the specified file, given as either a filename or an already opened
    file object. Passed file objects must be opened in binary mode. Meant as the
    typical entry point for loading in afm data.

    :param f: Filename of the file to read or an opened file object. File
              objects must be opened in binary mode.
    :param encoding: The encoding to use when reading the file header. Defaults
                     to utf-8.
    :param header_only: Whether to read only the header of the file. Defaults to
                        False.
    :returns: A NanoscopeFile object containing the image data.
    :raises OSError: If a passed file object is not opened in binary mode.
    """
    try:
        with io.open(f, 'rb') as file_obj:
            images = NanoscopeFile(file_obj, encoding, header_only)
    except TypeError:
        if 'b' not in f.mode:
            raise OSError('File must be opened in binary mode.')
        images = NanoscopeFile(f, encoding, header_only)
    return images


class NanoscopeFile(object):
    """
    Handles reading and parsing Nanoscope files.
    """
    supported_versions = ['0x05120130']

    def __init__(self, file_object, encoding='utf-8', header_only=False):
        self.images = {}
        self.config = {'_Images': {}}
        self.encoding = encoding

        self._read_header(file_object)
        if not header_only:
            for image_type in six.iterkeys(self.config['_Images']):
                self._read_image_data(file_object, image_type)

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

    def _read_header(self, file_object):
        """
        Read the Nanoscope file header.
        """
        file_object.seek(0)
        for line in file_object:
            parameter = parse_parameter(line, self.encoding)
            if not self._validate_version(parameter):
                raise ValueError(
                    'Unsupported file version {0}'.format(parameter.hard_value))
            if self._handle_parameter(parameter, file_object):
                return

    def _read_image_data(self, file_object, image_type):
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
        data_offset = config['Data offset']
        data_size = config['Bytes/pixel']
        number_lines = config['Number of lines']
        samples_per_line = config['Samps/line']

        file_object.seek(data_offset)
        number_points = number_lines * samples_per_line
        raw_data = (np.frombuffer(file_object.read(data_size * number_points),
                                  dtype='<i{}'.format(data_size),
                                  count=number_points)
                   .reshape((number_lines, samples_per_line)))

        self.images[image_type] = NanoscopeImage(
            image_type,
            raw_data,
            self.config['Sens. Zscan'],
            config['Bytes/pixel'],
            config['Z magnify'],
            config['Z scale']
        )
        return self.images[image_type]

    def _validate_version(self, parameter):
        if parameter.type == 'H' or parameter.parameter != 'Version':
            return True
        return parameter.hard_value in self.supported_versions

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
            parameter = parse_parameter(line, self.encoding)
            if parameter.type == 'H':
                return parameter
            if parameter.type == 'S':
                if parameter.parameter == 'Image Data':
                    image_config['Image Data'] = parameter.internal
                    self.config['_Images'][parameter.internal] = image_config
            else:
                image_config[parameter.parameter] = parameter.hard_value
