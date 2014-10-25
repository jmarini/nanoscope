# -*- coding: utf-8 -*-
import datetime
import unittest

from nanoscope.nanoscope import NanoscopeParser


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
        }
        p = NanoscopeParser('./tests/files/header_single_section.txt', 'utf-8')
        p.read_nanoscope()
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
        }
        p = NanoscopeParser('./tests/files/header_multiple_sections.txt', 'utf-8')
        p.read_nanoscope()
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
        }
        images = {
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
            }
        }
        p = NanoscopeParser('./tests/files/header_single_image.txt', 'utf-8')
        p.read_nanoscope()
        self.assertDictEqual(data, p.config)
        self.assertDictEqual(images, p.images)

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
        }
        images = {
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
            }
        }
        p = NanoscopeParser('./tests/files/header_multiple_images.txt', 'utf-8')
        p.read_nanoscope()
        self.assertDictEqual(data, p.config)
        self.assertDictEqual(images, p.images)
