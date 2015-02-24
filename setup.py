#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from io import open
from os import path

import nanoscope


base_dir = path.abspath(path.dirname(__file__))

with open(path.join(base_dir, 'README.rst'), 'r', encoding='utf-8') as f:
    readme = f.read()


setup(
    name='nanoscope',
    version=nanoscope.__version__,
    description='Library to parse and process of Nanoscope Dimension AFM files',
    long_description=readme,
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
