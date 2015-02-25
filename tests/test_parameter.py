# -*- coding: utf-8 -*-
import datetime
import unittest

import six

from nanoscope import parameter


class TestStringDecoding(unittest.TestCase):

    def test_unicode_string(self):
        string = six.u('testing')
        decoded = parameter.decode(string)
        self.assertTrue(isinstance(decoded, six.string_types))
        self.assertEqual(decoded, string)

    def test_string(self):
        string = 'testing'
        decoded = parameter.decode(string)
        self.assertEqual(decoded, string)

    def test_strip(self):
        string = six.u('testing\r\n')
        decoded = parameter.decode(string)
        self.assertEqual(decoded, string[:-2])

    def test_binary_string_ascii(self):
        string = six.b('testing')
        decoded = parameter.decode(string)
        self.assertEqual(six.u('testing'), decoded)

    def test_binary_string_utf8(self):
        string = six.b('\xd0\x98')
        decoded = parameter.decode(string, encoding='utf-8')
        self.assertEqual(six.u('\u0418'), decoded)

    def test_encoding_error(self):
        string = six.b('\xe0\x98')  # invalid continuation byte
        with self.assertRaises(UnicodeError):
            parameter.decode(string, encoding='utf-8')

class TestParameterParsing(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'')

    def test_empty_parameter_name(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'\ ')

    def test_empty_parameter_value_no_trailing_space(self):
        with self.assertRaises(ValueError):
            parameter.parse_parameter(r'\param:')

    def test_empty_value_trailing_space(self):
        p = parameter.parse_parameter(r'\param: ')
        self.assertIsNone(p.hard_value)

    def test_special_characters_parameter_name(self):
        name = r'.!#$%^&*-_,?/;"{}[]|=+`~<>'
        p = parameter.parse_parameter(r'\{0}: '.format(name))
        self.assertEqual(name, p.parameter)

    def test_parameter_with_at_symbol(self):
        name = 'param'
        p = parameter.parse_parameter(r'\@{0}: '.format(name))
        self.assertEqual(name, p.parameter)
        self.assertIsNone(p.hard_value)

    def test_parameter_with_group_number(self):
        name = 'param'
        group = 1
        p = parameter.parse_parameter(r'\@{0}:{1}: '.format(group, name))
        self.assertEqual(name, p.parameter)
        self.assertIsNone(p.hard_value)

    def test_detect_simple(self):
        p = parameter.parse_parameter(r'\param: ')
        self.assertIsInstance(p, parameter.CiaoParameter)
        self.assertEqual('P', p.type)
        self.assertIsNone(p.hard_value)

    def test_detect_value(self):
        p = parameter.parse_parameter(r'\param: V ')
        self.assertIsInstance(p, parameter.CiaoValue)
        self.assertEqual('V', p.type)
        self.assertIsNone(p.hard_value)

    def test_detect_scale(self):
        p = parameter.parse_parameter(r'\param: C ')
        self.assertIsInstance(p, parameter.CiaoScale)
        self.assertEqual('C', p.type)
        self.assertIsNone(p.hard_value)

    def test_detect_select(self):
        p = parameter.parse_parameter(r'\param: S ')
        self.assertIsInstance(p, parameter.CiaoSelect)
        self.assertEqual('S', p.type)

    def test_detect_header(self):
        p = parameter.parse_parameter(r'\*param')
        self.assertIsInstance(p, parameter.CiaoSectionHeader)
        self.assertEqual('H', p.type)
        self.assertEqual('param', p.header)


class TestSimpleParameter(unittest.TestCase):

    def test_empty_value(self):
        p = parameter.parse_parameter(r'\param:  ')
        self.assertIsNone(p.hard_value)

    def test_none(self):
        p = parameter.parse_parameter(r'\param: None')
        self.assertIsNone(p.hard_value)

    def test_datetime(self):
        time = datetime.datetime.utcnow().replace(microsecond=0)
        p = parameter.parse_parameter(r'\param: ' +
                                      time.strftime('%I:%M:%S %p %a %b %d %Y'))
        self.assertEqual(time, p.hard_value)

    def test_float_unambiguous(self):
        value = 1.2345
        p = parameter.parse_parameter(r'\param: {0}'.format(value))
        self.assertAlmostEqual(value, p.hard_value)
        self.assertIs(type(p.hard_value), float)

    def test_float_ambiguous(self):
        value = 1.0
        p = parameter.parse_parameter(r'\param: {0}'.format(value))
        self.assertAlmostEqual(value, p.hard_value)
        self.assertIs(type(p.hard_value), float)

    def test_integer(self):
        value = 12345
        p = parameter.parse_parameter(r'\param: {0}'.format(value))
        self.assertEqual(value, p.hard_value)
        self.assertIn(type(p.hard_value), six.integer_types)

    def test_string(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: ' + value)
        self.assertAlmostEqual(value, p.hard_value)

    def test_value_with_unit(self):
        number = 1.0
        value = '{0} unit'.format(number)
        p = parameter.parse_parameter(r'\param: {0}'.format(value))
        self.assertAlmostEqual(number, p.hard_value)
        self.assertIs(type(p.hard_value), float)

    def test_negative(self):
        value = -10
        p = parameter.parse_parameter(r'\param: {0}'.format(value))
        self.assertEqual(value, p.hard_value)


class TestValueParameter(unittest.TestCase):

    def test_only_soft_scale(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: V [{0}] '.format(value))
        self.assertEqual(value, p.soft_scale)
        self.assertIsNone(p.hard_scale)
        self.assertIsNone(p.hard_value)

    def test_only_hard_scale(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: V ({0}) '.format(value))
        self.assertIsNone(p.soft_scale)
        self.assertEqual(value, p.hard_scale)
        self.assertIsNone(p.hard_value)

    def test_only_hard_value(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: V {0}'.format(value))
        self.assertIsNone(p.soft_scale)
        self.assertIsNone(p.hard_scale)
        self.assertEqual(value, p.hard_value)

    def test_no_soft_scale(self):
        hard_scale = 'hard_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: V ({0}) {1}'.format(hard_scale, value))
        self.assertIsNone(p.soft_scale)
        self.assertEqual(hard_scale, p.hard_scale)
        self.assertEqual(value, p.hard_value)

    def test_no_hard_scale(self):
        soft_scale = 'soft_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: V [{0}] {1}'.format(soft_scale, value))
        self.assertEqual(soft_scale, p.soft_scale)
        self.assertIsNone(p.hard_scale)
        self.assertEqual(value, p.hard_value)

    def test_no_hard_value(self):
        soft_scale = 'soft_scale'
        hard_scale = 'hard_scale'
        p = parameter.parse_parameter(
            r'\param: V [{0}] ({1}) '.format(soft_scale, hard_scale))
        self.assertEqual(soft_scale, p.soft_scale)
        self.assertEqual(hard_scale, p.hard_scale)
        self.assertIsNone(p.hard_value)

    def test_all(self):
        soft_scale = 'soft_scale'
        hard_scale = 'hard_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: V [{0}] ({1}) {2}'.format(soft_scale, hard_scale, value))
        self.assertEqual(soft_scale, p.soft_scale)
        self.assertEqual(hard_scale, p.hard_scale)
        self.assertEqual(value, p.hard_value)

    def test_str(self):
        soft_scale = 'soft_scale'
        hard_scale = 'hard_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: V [{0}] ({1}) {2}'.format(soft_scale, hard_scale, value))
        self.assertEqual(p.__str__(), 'param: [soft_scale] (hard_scale) value')


class TestScaleParameter(unittest.TestCase):

    def test_only_soft_scale(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: C [{0}] '.format(value))
        self.assertEqual(value, p.soft_scale)
        self.assertIsNone(p.hard_value)

    def test_only_hard_value(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: C {0}'.format(value))
        self.assertIsNone(p.soft_scale)
        self.assertEqual(value, p.hard_value)

    def test_all(self):
        soft_scale = 'soft_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: C [{0}] {1}'.format(soft_scale, value))
        self.assertEqual(soft_scale, p.soft_scale)
        self.assertEqual(value, p.hard_value)

    def test_str(self):
        soft_scale = 'soft_scale'
        value = 'value'
        p = parameter.parse_parameter(
            r'\param: C [{0}] {1}'.format(soft_scale, value))
        self.assertEqual(p.__str__(), 'param: [soft_scale] value')


class TestSelectParameter(unittest.TestCase):

    def test_only_internal(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: S [{0}] '.format(value))
        self.assertEqual(value, p.internal)
        self.assertIsNone(p.external)

    def test_only_external(self):
        value = 'value'
        p = parameter.parse_parameter(r'\param: S "{0}"'.format(value))
        self.assertIsNone(p.internal)
        self.assertEqual(value, p.external)

    def test_all(self):
        internal = 'internal'
        external = 'external'
        p = parameter.parse_parameter(
            r'\param: S [{0}] "{1}"'.format(internal, external))
        self.assertEqual(internal, p.internal)
        self.assertEqual(external, p.external)

    def test_str(self):
        internal = 'internal'
        external = 'external'
        p = parameter.parse_parameter(
            r'\param: S [{0}] "{1}"'.format(internal, external))
        self.assertEqual(p.__str__(), 'param: [internal] "external"')
