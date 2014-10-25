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

    def test_read_height_data_multiple_images(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_header()
        height = p.read_image_data('Height')
        self.assertListEqual([-8417, -8416, -8414, -8413, -8411],
                              list(height.data[0, :5]))
        self.assertListEqual([-8417, -8411, -8404, -8396, -8387],
                             list(height.data[:5, 0]))


class TestNanoscopeImage(unittest.TestCase):

    def test_flatten_height_data(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_header()
        height = p.read_image_data('Height')
        flattened = [
            [-19, -18, -17, -16, -14],
            [-21, -20, -17, -16, -14],
            [-21, -20, -17, -15, -12],
            [-22, -18, -15, -13, -11],
            [-21, -17, -13, -12, -9],
        ]
        data = height.flatten(1)
        for line, flat in zip(data, flattened):
            self.assertListEqual(flat, list(np.round(line[:5], 0)))

    def test_convert_height_data(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_header()
        height = p.read_image_data('Height')
        height.flatten(1)
        converted = [
            [-1.64729, -1.56059, -1.47389, -1.38719, -1.21379],
            [-1.82069, -1.73399, -1.47389, -1.38719, -1.21379],
            [-1.82069, -1.73399, -1.47389, -1.30049, -1.04039],
            [-1.90749, -1.56059, -1.30049, -1.12709, -0.95369],
            [-1.82069, -1.47389, -1.12709, -1.04039, -0.78030],
        ]
        data = height.convert()
        for l, r in zip(np.array(converted).flatten(), data[:5, :5].flatten()):
            self.assertAlmostEqual(l, r, delta=0.01)

    def test_colors_height(self):
        p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
        p.read_header()
        p.read_image_data('Height')
        p.height.process(1)

    # def test_read_amplitude_data_multiple_images(self):
    #     p = NanoscopeParser('./tests/files/full_multiple_images.txt', 'cp1252')
    #     p.read_header()
    #     amplitude = p.read_image_data('Amplitude')
    #     self.assertListEqual([-2770, -3416, -2400, -3231, -4708],
    #                          list(amplitude.data[0, :5]))
    #     self.assertListEqual([-2770, -2585, -3877, -6462, -8677],
    #                          list(amplitude.data[:5, 0]))
