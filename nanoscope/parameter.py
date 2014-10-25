# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import datetime
import re


class CiaoParameter(object):
    """
    Parent class for generic values from the header.
    """
    type = 'P'

    def __init__(self, parameter, hard_value):
        self.parameter = parameter
        self.hard_value = self._parse_value(hard_value)

    def __str__(self):
        return '{0}: {1}'.format(self.parameter, self.hard_value)

    def _parse_value(self, value):
        """
        Try to parse and return the value as the following values:

        * ``datetime.datetime``
        * ``int``
        * ``float``
        * ``str``
        * ``None``

        Trailing whitespace is stripped and an empty string is returned
        as ``None``.
        """
        try:
            return datetime.datetime.strptime(value, '%I:%M:%S %p %a %b %d %Y')
        except:
            try:
                split_value = value.strip().split(' ')[0]
                if split_value == '' or split_value == 'None':
                    return None
            except AttributeError:
                return value
            try:
                return int(split_value)
            except ValueError:
                try:
                    return float(split_value)
                except ValueError:
                    return value


class CiaoValue(CiaoParameter):
    """
    Represents a Ciao value object.
    """
    type = 'V'

    def __init__(self, parameter, soft_scale, hard_scale, hard_value):
        self.parameter = parameter
        self.soft_scale = self._parse_value(soft_scale)
        self.hard_scale = self._parse_value(hard_scale)
        self.hard_value = self._parse_value(hard_value)

    def __str__(self):
        return '{0}: [{1}] ({2}) {3}'.format(self.parameter, self.soft_scale,
                                             self.hard_scale, self.hard_value)


class CiaoScale(CiaoParameter):
    """
    Represents a Ciao scale object.
    """
    type = 'C'

    def __init__(self, parameter, soft_scale, hard_value):
        self.parameter = parameter
        self.soft_scale = self._parse_value(soft_scale)
        self.hard_value = self._parse_value(hard_value)

    def __str__(self):
        return '{0}: [{1}] {2}'.format(self.parameter, self.soft_scale,
                                       self.hard_value)


class CiaoSelect(CiaoParameter):
    """
    Represents a Ciao select object.
    """
    type = 'S'

    def __init__(self, parameter, internal, external):
        self.parameter = parameter
        self.internal = internal
        self.external = external

    def __str__(self):
        return '{0}: [{1}] "{2}"'.format(self.parameter,
                                         self.internal,
                                         self.external)


class CiaoSectionHeader(CiaoParameter):
    """
    Represents a Ciao section header.
    """
    type = 'H'

    def __init__(self, header):
        self.header = header

    def __str__(self):
        return self.header


def parse_parameter(string):
    """
    Factory function that parses the parameter string and creates the
    appropriate CiaoParameter object.
    """
    header_match = re.match(r'\\\*(?P<header>.+)', string)
    if header_match is not None:
        return CiaoSectionHeader(header_match.group('header'))

    regex = re.compile(r'\\(?P<ciao>@?)(?:(?P<group>[0-9]+):)?'
                       r'(?P<parameter>[^:]+): '
                       r'(?:(?P<type>[VCS]) )?(?P<value>.*)')
    m = regex.match(string)
    if m is None:
        raise ValueError('"{0}" is not a valid Ciao Parameter'.format(string))

    parameter_type = m.group('type')
    value = m.group('value')
    if parameter_type == 'V':  # value
        value_regex = (r'(?:\[(?P<soft_scale>[^\[\]]*)\] )?'
                       r'(?:\((?P<hard_scale>[^\(\)]*)\) )?'
                       r'(?P<hard_value>[^\[\]\(\)]*)')
        vm = re.match(value_regex, value)
        return CiaoValue(m.group('parameter'), vm.group('soft_scale'),
                         vm.group('hard_scale'), vm.group('hard_value'))
    elif parameter_type == 'C':  # scale
        scale_regex = (r'(?:\[(?P<soft_scale>[^\[\]]*)\] )?'
                       r'(?P<hard_value>[^\[\]]*)')
        cm = re.match(scale_regex, value)
        return CiaoScale(m.group('parameter'), cm.group('soft_scale'),
                         cm.group('hard_value'))
    elif parameter_type == 'S':  # select
        select_regex = (r'(?:\[(?P<internal_designation>[^\[\]]*)\] )?'
                        r'(?:\"(?P<external_designation>[^\"]*)\")?')
        sm = re.match(select_regex, value)
        return CiaoSelect(m.group('parameter'),
                          sm.group('internal_designation'),
                          sm.group('external_designation'))
    else:  # simple value
        return CiaoParameter(m.group('parameter'), value)
