# -*- coding: utf-8 -*-
import datetime
import unittest

import numpy as np

from nanoscope import NanoscopeParser


class TestNanoscopeParser(unittest.TestCase):

    def test_read_header_single_section(self):
        data = {
            'Version': '0x05120130',
            'Date': datetime.datetime(2014, 10, 17, 10, 27, 26),
            'Start context': 'OL2',
            'Data length': 40960,
            'Text': None,
            'History': None,
            'Navigator note': None,
            'Engage X Pos': -19783.4,
            'Engage Y Pos': -42151.3,
            '_Images': {},
        }
        p = NanoscopeParser('./tests/files/header_single_section.txt', 'utf-8')
        p.read_header()
        self.assertDictEqual(data, p.config)

    def test_read_header_multiple_sections(self):
        data = {
            'Version': '0x05120130',
            'Date': datetime.datetime(2014, 10, 17, 10, 27, 26),
            'Start context': 'OL2',
            'Data length': 40960,
            'Text': None,
            'History': None,
            'Navigator note': None,
            'Engage X Pos': -19783.4,
            'Engage Y Pos': -42151.3,
            'Description': 'D3100 NSIV',
            'Controller': 'IV',
            'Microscope': 'D3100',
            'Extender': 'Quadrex',
            'Tip Exchange': None,
            'Vision': 'FrameGrabber',
            'Zoom System': 'Motorized',
            'Scanner file': '1965g.scn',
            'Profile name': 'default',
            '_Images': {},
        }
        p = NanoscopeParser('./tests/files/header_multiple_sections.txt', 'utf-8')
        p.read_header()
        self.assertDictEqual(data, p.config)

    def test_read_header_single_image(self):
        data = {
            'Version': '0x05120130',
            'Date': datetime.datetime(2014, 10, 17, 10, 27, 26),
            'Start context': 'OL2',
            'Data length': 40960,
            'Text': None,
            'History': None,
            'Navigator note': None,
            'Engage X Pos': -19783.4,
            'Engage Y Pos': -42151.3,
            '_Images': {
                'Height': {
                    'Data offset': 40960,
                    'Data length': 524288,
                    'Bytes/pixel': 2,
                    'Start context': 'OL',
                    'Data type': 'AFM',
                    'Note': None,
                    'Samps/line': 512,
                    'Number of lines': 512,
                    'Aspect ratio': '1:1',
                    'Line direction': 'Retrace',
                    'Highpass': 0,
                    'Lowpass': 0,
                    'Realtime planefit': 'Line',
                    'Offline planefit': None,
                    'Valid data start X': 0,
                    'Valid data start Y': 0,
                    'Valid data len X': 512,
                    'Valid data len Y': 512,
                    'Tip x width correction factor': 1,
                    'Tip y width correction factor': 1,
                    'Tip x width correction factor sigma': 1,
                    'Tip y width correction factor sigma': 1,
                    'Z magnify': 0.002639945,
                    'Z scale': 438.6572,
                    'Z offset': 0,
                    'Image Data': 'Height',
                },
            },
        }
        p = NanoscopeParser('./tests/files/header_single_image.txt', 'utf-8')
        p.read_header()
        self.assertDictEqual(data, p.config)

    def test_read_header_multiple_images(self):
        data = {
            'Version': '0x05120130',
            'Date': datetime.datetime(2014, 10, 17, 10, 27, 26),
            'Start context': 'OL2',
            'Data length': 40960,
            'Text': None,
            'History': None,
            'Navigator note': None,
            'Engage X Pos': -19783.4,
            'Engage Y Pos': -42151.3,
            '_Images': {
                'Height': {
                    'Data offset': 40960,
                    'Data length': 524288,
                    'Bytes/pixel': 2,
                    'Start context': 'OL',
                    'Data type': 'AFM',
                    'Note': None,
                    'Samps/line': 512,
                    'Number of lines': 512,
                    'Aspect ratio': '1:1',
                    'Line direction': 'Retrace',
                    'Highpass': 0,
                    'Lowpass': 0,
                    'Realtime planefit': 'Line',
                    'Offline planefit': None,
                    'Valid data start X': 0,
                    'Valid data start Y': 0,
                    'Valid data len X': 512,
                    'Valid data len Y': 512,
                    'Tip x width correction factor': 1,
                    'Tip y width correction factor': 1,
                    'Tip x width correction factor sigma': 1,
                    'Tip y width correction factor sigma': 1,
                    'Z magnify': 0.002639945,
                    'Z scale': 438.6572,
                    'Z offset': 0,
                    'Image Data': 'Height'
                },
                'Amplitude': {
                    'Data offset': 565248,
                    'Data length': 524288,
                    'Bytes/pixel': 2,
                    'Start context': 'OL',
                    'Data type': 'AFM',
                    'Note': None,
                    'Samps/line': 512,
                    'Number of lines': 512,
                    'Aspect ratio': '1:1',
                    'Line direction': 'Retrace',
                    'Highpass': 0,
                    'Lowpass': 0,
                    'Realtime planefit': 'Line',
                    'Offline planefit': 'Full',
                    'Valid data start X': 0,
                    'Valid data start Y': 0,
                    'Valid data len X': 512,
                    'Valid data len Y': 512,
                    'Tip x width correction factor': 1,
                    'Tip y width correction factor': 1,
                    'Tip x width correction factor sigma': 1,
                    'Tip y width correction factor sigma': 1,
                    'Z magnify': 0.4615211,
                    'Z scale': 0.2166748,
                    'Z offset': 0,
                    'Image Data': 'Amplitude',
                },
            },
        }
        p = NanoscopeParser('./tests/files/header_multiple_images.txt', 'utf-8')
        p.read_header()
        self.assertDictEqual(data, p.config)

    def test_property(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_file()
        self.assertIsNotNone(p.height)
        self.assertIsNotNone(p.amplitude)
        self.assertIsNone(p.phase)

    def test_height_scale(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt')
        p.read_header()
        sensitivity = p.config['Sens. Zscan']
        magnify = p.config['_Images']['Height']['Z magnify']
        scale = p.config['_Images']['Height']['Z scale']
        self.assertAlmostEqual(15.0, sensitivity * magnify * scale, delta=0.01)

    def test_read_height_data_multiple_images(self):
        csv_data = np.loadtxt('./tests/files/reference_raw.csv',
                              delimiter=',')
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_header()
        height = p.read_image_data('Height')
        get_loc = (lambda i, j:
            p.config['_Images']['Height']['Data offset'] +
            p.config['_Images']['Height']['Samps/line'] *
            p.config['_Images']['Height']['Bytes/pixel'] * j + i *
            p.config['_Images']['Height']['Bytes/pixel'])
        for j, (l, r) in enumerate(zip(height.data, csv_data)):
            for i, (ll, rr) in enumerate(zip(l, r)):
                self.assertEqual(ll, rr,
                    msg='@ ({0}, {1}) '
                        '0x{2:X}'.format(i, j, get_loc(i, j)))

    def test_read_unsupported_image_type(self):
        p = NanoscopeParser('./tests/files/header_single_section.txt', 'utf-8')
        p.read_header()
        with self.assertRaises(ValueError, msg='Unsupported image type test'):
            p.read_image_data('test')

    def test_read_nonexistant_image_type(self):
        p = NanoscopeParser('./tests/files/header_single_image.txt', 'utf-8')
        p.read_header()
        with self.assertRaises(ValueError, msg='Image type Phase not in file'):
            p.read_image_data('Phase')


class TestNanoscopeImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_file()
        p.height.flatten(1).convert()
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
        actual = self.height.zrange()
        self.assertAlmostEqual(actual, expected, delta=0.001)

    def test_rms(self):
        expected = 4.325
        actual = self.height.rms()
        self.assertAlmostEqual(actual, expected, delta=0.001)
