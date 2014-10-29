#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='Nanoscope',
    version='0.8.0',
    url='',
    author='Jonathan Marini',
    author_email='jmarini@ieee.org',
    packages=['nanoscope'],
    install_requires=['numpy', 'six'],
    test_suite='tests',
)
