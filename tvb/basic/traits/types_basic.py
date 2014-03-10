# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
This module describes the simple of traited attributes one might needs on a class.

If your subclass should be mapped to a database table (true for most entities
that will be reused), use MappedType as superclass.

If you subclass is supported natively by SQLAlchemy, subclass Type, otherwise
subclass MappedType.

Important:
- Type - traited, possible mapped to db *col*
- MappedType - traited, mapped to db *table*


.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <duke@eml.cc>
.. moduleauthor:: Paula Sanz-Leon <paula.sanz-leon@univ-amu.fr>
"""

import numpy
import math
import json
import tvb.basic.traits.core as core
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class String(core.Type):
    """
    Traits type that wraps a Python string.
    """
    wraps = (str, unicode)



class Bool(core.Type):
    """
    Traits type wrapping Python boolean primitive. 
    The only instances of Python bool are True and False.
    """
    wraps = bool



class Integer(core.Type):
    """
    Traits type that wraps Numpy's int32.
    """
    wraps = (int, long)



class Float(core.Type):
    """
    Traits type that wraps Numpy's float64.
    """
    wraps = (float, numpy.float32, int)



class Complex(core.Type):
    """
    Traits type that wraps Numpy's complex64.
    """
    wraps = numpy.complex64



class MapAsJson():
    """Add functionality of converting from/to JSON"""


    def __get__(self, inst, cls):
        if inst is not None and self.trait.bound and hasattr(inst, '_' + self.trait.name):
            string = getattr(inst, '_' + self.trait.name)
            if string is None or (not isinstance(string, (str, unicode))):
                return string
            if len(string) < 1:
                return None
            json_value = self.from_json(string)
            setattr(inst, '_' + self.trait.name, json_value)
            return json_value
        return self


    @staticmethod
    def to_json(entity):
        return json.dumps(entity)


    @staticmethod
    def from_json(string):
        return json.loads(string)


    @staticmethod
    def decode_map_as_json(dct):
        """
        Used in the __convert_to_array to get an equation from the UI corresponding string.
        """
        for key, value in dct.items():
            if isinstance(value, unicode) and '__mapped_module' in value:
                dict_value = json.loads(value)
                if '__mapped_module' not in dict_value:
                    dct[key] = MapAsJson.decode_map_as_json(dict_value)
                else:
                    modulename = dict_value['__mapped_module']
                    classname = dict_value['__mapped_class']
                    module_entity = __import__(modulename, globals(), locals(), [classname])
                    class_entity = eval('module_entity.' + classname)
                    loaded_entity = class_entity.from_json(value)
                    dct[key] = loaded_entity
        return dct

    class MapAsJsonEncoder(json.JSONEncoder):
        """
        Used before any save to the database to encode Equation type objects.
        """


        def default(self, obj):
            if isinstance(obj, MapAsJson):
                return obj.to_json(obj)
            else:
                return json.JSONEncoder.default(self, obj)



class Sequence(MapAsJson, String):
    """
    Traits type base class that wraps python sequence 
    python types (containers)
    """
    wraps = (dict, list, tuple, set, slice, numpy.ndarray)



class Enumerate(Sequence):
    """
    Traits type that mimics an enumeration.
    """
    wraps = numpy.ndarray


    def __get__(self, inst, cls):
        if inst is None:
            return self
        if self.trait.bound:
            return numpy.array(super(Enumerate, self).__get__(inst, cls))
        return numpy.array(self.trait.value)


    def __set__(self, inst, value):
        if not isinstance(value, list):
            # So it works for simple selects aswell as multiple selects
            value = [value]
        if self.trait.select_multiple:
            super(Enumerate, self).__set__(inst, value)
        else:
            #Bypass default since that only accepts arrays for multiple selects
            setattr(inst, '_' + self.trait.name, self.to_json(value))
            self.trait.value = value



class Dict(Sequence):
    """
    Traits type that wraps a python dict.
    """
    wraps = dict



class Set(Sequence):
    """
    Traits type that wraps a python set.
    """
    wraps = set



class Tuple(Sequence):
    """
    Traits type that wraps a python tuple.
    """
    wraps = tuple


    def __get__(self, inst, cls):
        list_value = super(Tuple, self).__get__(inst, cls)

        if isinstance(list_value, list):
            return list_value[0], list_value[1]

        return list_value



class List(Sequence):
    """
    Traits type that wraps a Python list.
    """
    wraps = (list, numpy.ndarray)



class Slice(Sequence):
    """
    Useful of for specifying views or slices of containers.
    """
    wraps = slice



class Range(core.Type):
    """
    Range is a range that can have multiplicative or additive step sizes.
    Values generated by Range are in the interval [start, stop]

    Instances of Range will not generate their discrete values automatically,
    but these values can be obtained by converting to a list

    Multiplicative ranges are not yet supported by the web ui.

        >>> range_values = list(Range(lo=0.0, hi=1.0, step=0.1))

        [0.0,
         0.1,
         0.2,
         0.30000000000000004,
         0.4,
         0.5,
         0.6000000000000001,
         0.7000000000000001,
         0.8,
         0.9,
         1.0]

        or by direct iteration:

        >>> for val in Range(lo=0.0, hi=1.0, step=0.1):
                print val

        0.1
        0.2
        0.3
        0.4
        0.5
        0.6
        0.7
        0.8
        0.9
        1.0


        >>> for val in Range(lo=0.0, hi=2.0, step=1.0):
                print val
        0.0
        1.0
        2.0

        >>> for val in Range(lo=0.0, hi=3.0, step=1.0):
                print val
        0.0
        1.0
        2.0
        3.0

    using a fixed multiplier
        >>> for val in Range(lo=0.0, hi=5.0, base=2.0):
                print val
        0.0
        2.0
        4.0

        >>> for val in Range(lo=1.0, hi=8.O, base=2.0):
                print val
        1.0
        2.0
        4.0
        8.0

    """
    lo = Float(doc='start of range')
    hi = Float(doc='end of range')

    step = Float(default=None, doc='fixed step size between elements (for additive). It has priority over "base"')
    base = Float(default=2.0, doc='fixed multiplier between elements')


    def __iter__(self):
        """ Get valid values in interval"""

        def gen():
            if self.step:
                for i in xrange(self.number_of_additive_values()):
                    yield self.lo + self.step * i
            else:
                if self.base <= 1.0:
                    msg = "Invalid base value: %s"
                    LOG.error(msg % str(self.base))
                else:
                    val = self.lo
                    if val == 0:
                        yield val
                        val += self.base
                    # todo: check values produced by the multiplicative range
                    while val <= self.hi:
                        yield val
                        val *= self.base

        return gen()


    def number_of_additive_values(self):
        """
        :returns: integer specifying how many values are expected to be included in this additive range
        """
        approx_steps_numbers = (self.hi - self.lo) / self.step
        return_integer = int(approx_steps_numbers)
        if approx_steps_numbers - return_integer > 0.999:
            return return_integer + 1 + 1
        return return_integer + 1



class ValidationRange(core.Type):
    """
    ValidationRange represents a Range used only for validating a number.
    """



class JSONType(String):
    """
    Wrapper over a String which holds a serializable object.
    On set/get JSON load/dump will be called.
    """


    def __get__(self, inst, cls):
        if inst:
            string = super(JSONType, self).__get__(inst, cls)
            if string is None or (not isinstance(string, (str, unicode))):
                return string
            if len(string) < 1:
                return None
            return json.loads(string)
        return super(JSONType, self).__get__(inst, cls)


    def __set__(self, inst, value):
        if not isinstance(value, (str, unicode)):
            value = json.dumps(value)
        super(JSONType, self).__set__(inst, value)



class DType(String):
    """
    Traits type that wraps a Numpy dType specification.
    """

    wraps = (numpy.dtype, str)
    defaults = ((numpy.float64, ), {})


    def __get__(self, inst, cls):
        if inst:
            type_ = super(DType, self).__get__(inst, cls)
            return str(type_).replace("<type '", '').replace("'>", '')
        return super(DType, self).__get__(inst, cls)


    def __set__(self, inst, value):
        super(DType, self).__set__(inst, str(value))

   
