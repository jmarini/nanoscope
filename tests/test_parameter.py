# -*- coding: utf-8 -*-
import datetime
import unittest

import six

from nanoscope import parameter


class TestParameterParsing(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'')

    def test_empty_parameter_name(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'\ ')

    def test_empty_parameter_value_no_trailing_space(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'\name:')

    def test_empty_value_trailing_space(self):
        p = parameter.parse_parameter(r'\name: ')
        self.assertIsNone(p.hard_value)

    def test_special_characters_parameter_name(self):
        name = r'.!#$%^&*-_,?/;"{}[]|=+`~<>'
        p = parameter.parse_parameter('\\' + name + ': ')
        self.assertEqual(name, p.parameter)


class TestSimpleParameter(unittest.TestCase):

    def test_empty_value(self):
        p = parameter.parse_parameter(r'\name:  ')
        self.assertIsNone(p.hard_value)

    def test_none(self):
        p = parameter.parse_parameter(r'\name: None')
        self.assertIsNone(p.hard_value)

    def test_datetime(self):
        time = datetime.datetime.utcnow().replace(microsecond=0)
        p = parameter.parse_parameter('\\date: ' +
                                      time.strftime('%I:%M:%S %p %a %b %d %Y'))
        self.assertEqual(time, p.hard_value)

    def test_float_unambiguous(self):
        value = 1.2345
        p = parameter.parse_parameter('\\float: {0}'.format(value))
        self.assertAlmostEqual(value, p.hard_value)
        self.assertIs(type(p.hard_value), float)

    def test_float_ambiguous(self):
        value = 1.0
        p = parameter.parse_parameter('\\float: {0}'.format(value))
        self.assertAlmostEqual(value, p.hard_value)
        self.assertIs(type(p.hard_value), float)

    def test_integer(self):
        value = 12345
        p = parameter.parse_parameter('\\integer: {0}'.format(value))
        self.assertEqual(value, p.hard_value)
        self.assertIn(type(p.hard_value), six.integer_types)

    def test_string(self):
        value = 'abcd'
        p = parameter.parse_parameter('\\string: ' + value)
        self.assertAlmostEqual(value, p.hard_value)
