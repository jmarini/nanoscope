# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Error(Exception):
    """Base exception for nanoscope errors."""
    pass


class UnsupportedVersion(Error):
    """Error for unsupported SPM file version."""

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return 'Unsupported file version {}'.format(self.version)


class MissingImageData(Error):
    """Error for missing data for defined image in header."""

    def __init__(self, image):
        self.image = image

    def __str__(self):
        return ('Image type {} found in header '
                'but is missing data'.format(self.image))


class InvalidParameter(Error):
    """Error for incorrectly formatted Ciao parameter."""

    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return '"{}" is not a valid Ciao parameter'.format(self.parameter)
