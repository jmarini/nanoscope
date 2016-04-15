# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import datetime
import io
import unittest

import numpy as np
import six

from nanoscope.nanoscope import NanoscopeFile, read


class TestNanoscopeFile(unittest.TestCase):

    def test_read_header_invalid_version(self):
        file_data = ('\\*File list\n'
                     '\\Version: 0x00000000\n'
                     '\\*File list end\n')
        f = six.StringIO(file_data)
        with self.assertRaises(ValueError,
                               msg='Unsupported file version 0x00000000'):
            p = NanoscopeFile(f)
        f.close()

    def test_read_header_single_section(self):
        parsed_data = {
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
        file_data = ('\\*File list\n'
                     '\\Version: 0x05120130\n'
                     '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
                     '\\Start context: OL2\n'
                     '\\Data length: 40960\n'
                     '\\Text: \n'
                     '\\History: \n'
                     '\\Navigator note: \n'
                     '\\Engage X Pos: -19783.4 um\n'
                     '\\Engage Y Pos: -42151.3 um\n'
                     '\\*File list end\n')
        f = six.StringIO(file_data)
        p = NanoscopeFile(f)
        f.close()
        self.assertDictEqual(parsed_data, p.config)

    def test_read_header_multiple_sections(self):
        parsed_data = {
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
        file_data = ('\\*File list\n'
                     '\\Version: 0x05120130\n'
                     '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
                     '\\Start context: OL2\n'
                     '\\Data length: 40960\n'
                     '\\Text: \n'
                     '\\History: \n'
                     '\\Navigator note: \n'
                     '\\Engage X Pos: -19783.4 um\n'
                     '\\Engage Y Pos: -42151.3 um\n'
                     '\\*Equipment list\n'
                     '\\Description: D3100 NSIV\n'
                     '\\Controller: IV\n'
                     '\\Microscope: D3100\n'
                     '\\Extender: Quadrex\n'
                     '\\Tip Exchange: None\n'
                     '\\Vision: FrameGrabber\n'
                     '\\Zoom System: Motorized\n'
                     '\\Scanner file: 1965g.scn\n'
                     '\\Profile name: default\n'
                     '\\*File list end\n')
        f = six.StringIO(file_data)
        p = NanoscopeFile(f)
        f.close()
        self.assertDictEqual(parsed_data, p.config)

    def test_read_header_single_image(self):
        parsed_data = {
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
        file_data = (
            '\\*File list\n'
            '\\Version: 0x05120130\n'
            '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
            '\\Start context: OL2\n'
            '\\Data length: 40960\n'
            '\\Text: \n'
            '\\History: \n'
            '\\Navigator note: \n'
            '\\Engage X Pos: -19783.4 um\n'
            '\\Engage Y Pos: -42151.3 um\n'
            '\\*Ciao image list\n'
            '\\Data offset: 40960\n'
            '\\Data length: 524288\n'
            '\\Bytes/pixel: 2\n'
            '\\Start context: OL\n'
            '\\Data type: AFM\n'
            '\\Note: \n'
            '\\Samps/line: 512\n'
            '\\Number of lines: 512\n'
            '\\Aspect ratio: 1:1\n'
            '\\Line direction: Retrace\n'
            '\\Highpass: 0\n'
            '\\Lowpass: 0\n'
            '\\Realtime planefit: Line\n'
            '\\Offline planefit: None\n'
            '\\Valid data start X: 0\n'
            '\\Valid data start Y: 0\n'
            '\\Valid data len X: 512\n'
            '\\Valid data len Y: 512\n'
            '\\Tip x width correction factor: 1\n'
            '\\Tip y width correction factor: 1\n'
            '\\Tip x width correction factor sigma: 1\n'
            '\\Tip y width correction factor sigma: 1\n'
            '\\@2:Image Data: S [Height] "Height"\n'
            '\\@Z magnify: C [2:Z scale] 0.002639945 \n'
            '\\@2:Z scale: V [Sens. Zscan] (0.006693481 V/LSB) 438.6572 V\n'
            '\\@2:Z offset: V [Sens. Zscan] (0.006693481 V/LSB)       0 V\n'
            '\\*File list end\n'
        )
        f = six.StringIO(file_data)
        p = NanoscopeFile(f, header_only=True)
        f.close()
        self.assertDictEqual(parsed_data, p.config)

    def test_read_header_multiple_images(self):
        parsed_data = {
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
        file_data = (
            '\\*File list\n'
            '\\Version: 0x05120130\n'
            '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
            '\\Start context: OL2\n'
            '\\Data length: 40960\n'
            '\\Text: \n'
            '\\History: \n'
            '\\Navigator note: \n'
            '\\Engage X Pos: -19783.4 um\n'
            '\\Engage Y Pos: -42151.3 um\n'
            '\\*Ciao image list\n'
            '\\Data offset: 40960\n'
            '\\Data length: 524288\n'
            '\\Bytes/pixel: 2\n'
            '\\Start context: OL\n'
            '\\Data type: AFM\n'
            '\\Note: \n'
            '\\Samps/line: 512\n'
            '\\Number of lines: 512\n'
            '\\Aspect ratio: 1:1\n'
            '\\Line direction: Retrace\n'
            '\\Highpass: 0\n'
            '\\Lowpass: 0\n'
            '\\Realtime planefit: Line\n'
            '\\Offline planefit: None\n'
            '\\Valid data start X: 0\n'
            '\\Valid data start Y: 0\n'
            '\\Valid data len X: 512\n'
            '\\Valid data len Y: 512\n'
            '\\Tip x width correction factor: 1\n'
            '\\Tip y width correction factor: 1\n'
            '\\Tip x width correction factor sigma: 1\n'
            '\\Tip y width correction factor sigma: 1\n'
            '\\@2:Image Data: S [Height] "Height"\n'
            '\\@Z magnify: C [2:Z scale] 0.002639945 \n'
            '\\@2:Z scale: V [Sens. Zscan] (0.006693481 V/LSB) 438.6572 V\n'
            '\\@2:Z offset: V [Sens. Zscan] (0.006693481 V/LSB)       0 V\n'
            '\\*Ciao image list\n'
            '\\Data offset: 565248\n'
            '\\Data length: 524288\n'
            '\\Bytes/pixel: 2\n'
            '\\Start context: OL\n'
            '\\Data type: AFM\n'
            '\\Note: \n'
            '\\Samps/line: 512\n'
            '\\Number of lines: 512\n'
            '\\Aspect ratio: 1:1\n'
            '\\Line direction: Retrace\n'
            '\\Highpass: 0\n'
            '\\Lowpass: 0\n'
            '\\Realtime planefit: Line\n'
            '\\Offline planefit: Full\n'
            '\\Valid data start X: 0\n'
            '\\Valid data start Y: 0\n'
            '\\Valid data len X: 512\n'
            '\\Valid data len Y: 512\n'
            '\\Tip x width correction factor: 1\n'
            '\\Tip y width correction factor: 1\n'
            '\\Tip x width correction factor sigma: 1\n'
            '\\Tip y width correction factor sigma: 1\n'
            '\\@2:Image Data: S [Amplitude] "Amplitude"\n'
            '\\@Z magnify: C [2:Z scale] 0.4615211 \n'
            '\\@2:Z scale: V [Sens. Amplitude] (0.0003051758 V/LSB) 0.2166748 V\n'
            '\\@2:Z offset: V [Sens. Amplitude] (0.0003051758 V/LSB)       0 V\n'
            '\\*File list end\n'
        )
        f = six.StringIO(file_data)
        p = NanoscopeFile(f, header_only=True)
        f.close()
        self.assertDictEqual(parsed_data, p.config)

    def test_read_filename(self):
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        self.assertIsNotNone(p.height)

    def test_read_file_object_binary_mode(self):
        with io.open('./tests/files/full_multiple_images.txt', 'rb') as f:
            p = read(f, encoding='cp1252')
        self.assertIsNotNone(p.height)

    def test_read_file_object_text_mode(self):
        with io.open('./tests/files/full_multiple_images.txt', 'r') as f:
            with self.assertRaises(OSError):
                read(f, encoding='cp1252')

    def test_property(self):
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        self.assertIsNotNone(p.height)
        self.assertIsNotNone(p.amplitude)
        self.assertIsNone(p.phase)

    def test_height_scale(self):
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        sensitivity = p.config['Sens. Zscan']
        magnify = p.config['_Images']['Height']['Z magnify']
        scale = p.config['_Images']['Height']['Z scale']
        self.assertAlmostEqual(15.0, sensitivity * magnify * scale, delta=0.01)

    def test_read_height_data_multiple_images(self):
        csv_data = np.loadtxt('./tests/files/reference_raw.csv',
                              delimiter=',')
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        height = p.height
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

    def test_iterate_images(self):
        p = read('./tests/files/full_multiple_images.txt', encoding='cp1252')
        images = [image for image in p]
        self.assertIn(p.height, images)
        self.assertIn(p.amplitude, images)

    def test_read_invalid_image(self):
        file_data = (
            '\\*File list\n'
            '\\Version: 0x05120130\n'
            '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
            '\\Data length: 40960\n'
            '\\*Ciao image list\n'
            '\\Data offset: 40960\n'
            '\\Data length: 524288\n'
            '\\Bytes/pixel: 2\n'
            '\\Samps/line: 512\n'
            '\\Number of lines: 512\n'
            '\\Aspect ratio: 1:1\n'
            '\\Valid data start X: 0\n'
            '\\Valid data start Y: 0\n'
            '\\Valid data len X: 512\n'
            '\\Valid data len Y: 512\n'
            '\\@2:Image Data: S [Invalid] "Invalid"\n'
            '\\@Z magnify: C [2:Z scale] 0.002639945 \n'
            '\\@2:Z scale: V [Sens. Zscan] (0.006693481 V/LSB) 438.6572 V\n'
            '\\@2:Z offset: V [Sens. Zscan] (0.006693481 V/LSB)       0 V\n'
            '\\*File list end\n'
        )
        f = six.StringIO(file_data)
        with self.assertRaises(ValueError,
                               msg='Unsupported image type Invalid'):
            p = NanoscopeFile(f)
        f.close()

    def test_read_image_not_in_file(self):
        file_data = (
            '\\*File list\n'
            '\\Version: 0x05120130\n'
            '\\Date: 10:27:26 AM Fri Oct 17 2014\n'
            '\\Data length: 40960\n'
            '\\*Ciao image list\n'
            '\\Data offset: 40960\n'
            '\\Data length: 524288\n'
            '\\Bytes/pixel: 2\n'
            '\\Samps/line: 512\n'
            '\\Number of lines: 512\n'
            '\\Aspect ratio: 1:1\n'
            '\\Valid data start X: 0\n'
            '\\Valid data start Y: 0\n'
            '\\Valid data len X: 512\n'
            '\\Valid data len Y: 512\n'
            '\\@2:Image Data: S [Height] "Height"\n'
            '\\@Z magnify: C [2:Z scale] 0.002639945 \n'
            '\\@2:Z scale: V [Sens. Zscan] (0.006693481 V/LSB) 438.6572 V\n'
            '\\@2:Z offset: V [Sens. Zscan] (0.006693481 V/LSB)       0 V\n'
            '\\*File list end\n'
        )
        f = six.StringIO(file_data)
        with self.assertRaises(ValueError,
                               msg='Image type Amplitude not in file'):
            p = NanoscopeFile(f, header_only=True)
            p._read_image_data(f, 'Amplitude')
        f.close()
