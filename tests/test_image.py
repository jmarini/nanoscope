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

    def test_mean_height(self):
        expected = 0.00
        actual = self.height.mean_height
        self.assertAlmostEqual(actual, expected, delta=1e-4)

    def test_mean_roughness(self):
        expected = 3.433
        actual = self.height.mean_roughness
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_rms_roughness(self):
        expected = 4.325
        actual = self.height.rms_roughness
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_max_peak(self):
        expected = 14.478
        actual = self.height.max_peak
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_max_valley(self):
        expected = 12.918
        actual = self.height.max_valley
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_total_roughness(self):
        expected = self.height.max_peak + self.height.max_valley
        actual = self.height.total_roughness
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_mean_peak(self):
        expected = 3.346
        actual = self.height.mean_peak
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_mean_valley(self):
        expected = 3.525
        actual = self.height.mean_valley
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_min_height(self):
        expected = -self.height.max_valley
        actual = self.height.min_height
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_max_height(self):
        expected = self.height.max_peak
        actual = self.height.max_height
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_mean_total_roughness(self):
        expected = self.height.mean_peak + self.height.mean_valley
        actual = self.height.mean_total_roughness
        self.assertAlmostEqual(actual, expected, delta=0.001)
