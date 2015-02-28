# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import unittest

import numpy as np

from nanoscope.nanoscope import read


class TestNanoscopeImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        p.height.process(order=1)
        cls.parser = p
        cls.height = p.height
        cls.get_loc = (lambda self, i, j:
            p.config['_Images']['Height']['Data offset'] +
            p.config['_Images']['Height']['Samps/line'] *
            p.config['_Images']['Height']['Bytes/pixel'] * j + i *
            p.config['_Images']['Height']['Bytes/pixel'])

    def test_flatten_height_data(self):
        expected = np.loadtxt('./tests/files/reference_flat.csv',
                              delimiter=',')
        actual = self.parser.height.flat_data

        for j, (l, r) in enumerate(zip(actual, expected)):
            for i, (ll, rr) in enumerate(zip(l, r)):
                self.assertEqual(ll, rr,
                    msg='@ ({0}, {1}) '
                        '0x{2:X}'.format(i, j, self.get_loc(i, j)))

    def test_convert_height_data(self):
        expected = np.loadtxt('./tests/files/reference_converted.csv',
                              delimiter=',')
        actual = np.round(self.height.converted_data, 2)

        for j, (l, r) in enumerate(zip(actual, expected)):
            for i, (ll, rr) in enumerate(zip(l, r)):
                self.assertAlmostEqual(ll, rr, delta=0.1,
                    msg='@ ({0}, {1}) '
                        '0x{2:X}'.format(i, j, self.get_loc(i, j)))

    def test_colorize_data(self):
        expected = np.loadtxt('./tests/files/reference_pixels.csv',
                              delimiter=',', dtype=np.uint8)
        num_lines = self.parser.config['_Images']['Height']['Number of lines']
        num_columns = self.parser.config['_Images']['Height']['Samps/line']
        expected = expected.reshape(num_lines, num_columns, 3)

        actual = self.height.colorize()

        for j, (l, r) in enumerate(zip(actual, expected)):
            for i, (ll, rr) in enumerate(zip(l, r)):
                for lll, rrr in zip(ll, rr):
                    self.assertAlmostEqual(int(lll), int(rrr), delta=4,
                        msg='@ ({0}, {1}) '
                            '0x{2:X}'.format(i, j, self.get_loc(i, j)))

    def test_zrange(self):
        expected = 27.397
        actual = self.height.zrange
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_rms(self):
        expected = 4.325
        actual = self.height.rms
        self.assertAlmostEqual(actual, expected, delta=0.001)
