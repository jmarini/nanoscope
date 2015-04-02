#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from io import open
from os import path
from re import search, MULTILINE


def read(filename, encoding='utf-8'):
    base_dir = path.abspath(path.dirname(__file__))
    with open(path.join(base_dir, filename), 'r', encoding=encoding) as f:
        return f.read()


def find_version(filename, encoding='utf-8'):
    """
    Reads the version string from the specified file. It should be in the
    format:

    .. code-block:: python

        __version__ = 'version-string'

    Where version-string should be the version number.

    Adapted from packaging.python.org
    """
    version_file = read(filename, encoding)
    version_match = search(
        r'^__version__\s+=\s+[\'"](?P<version>[^\'"]+)[\'"]',
        version_file,
        MULTILINE)
    if version_match:
        return version_match.group('version')
    raise RuntimeError('Unable to find version string.')


setup(
    name='nanoscope',
    version=find_version('nanoscope/__init__.py'),
    description='Library to parse and process of Nanoscope Dimension AFM files',
    long_description=read('README.rst'),
    url='https://github.com/jmarini/nanoscope',
    author='Jonathan Marini',
    author_email='j.marini@ieee.org',
    packages=['nanoscope'],
    install_requires=['numpy', 'six'],
    test_suite='tests',
    classifiers=(
        'Development Status :: 5 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering',
    ),
)
