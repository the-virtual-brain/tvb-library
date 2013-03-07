# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the project, you need to sign a contributor's license. 
# Please contact info@thevirtualbrain.org for further details.
# Neither the name of Baycrest nor the names of any TVB contributors may be used to endorse or 
# promote products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#
#

"""
This module describes the simple of traited attributes one needs in a class.

If your subclass should be mapped to a database table (true for most entities
that will be reused), use MappedType.

If you subclass is supported natively by SQLAlchemy, subclass Type, otherwise
subclass MappedType.

Important:
- Type - traited, possible mapped to db *col*
- MappedType - traited, mapped to db *table*


.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: marmaduke <duke@eml.cc>
"""

import numpy
import math
import json
import sqlalchemy
import tvb.basic.traits.core as core
import tvb.basic.logger.logger as logger

LOG = logger.getLogger(__name__)

class String(core.Type):
    """
    Traits type that wraps a python string.
    """
    wraps = (str, unicode)


class Bool(core.Type):
    """
    Traits type wrapping Python bool. 
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
    #TODO: Probably should be complex128, as 
    #      we would generally want equivalence with float64
    wraps = numpy.complex64


class MapAsJson():
    """Add functionality of converting from/to JSON"""

    def __get__(self, inst, cls):
        if (inst is not None and self.trait.bound and hasattr(inst, '_' + self.trait.name)):
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
        Used before any save to the database to encode Equation type opjects.
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
            return (list_value[0], list_value[1])
        
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
    Range is like Python range() except that it will accept ranges with
    multiplicative or additive step sizes.

    Instances of Range will not generate their discete values automatically,
    but these values can be obtained by converting to a list

        >>> range_values = list(Range(hi=1.0, step=0.1))

    or direct iteration

        >>> for val in Range(lo=0.0, hi=3.0):
                print val
        0.0
        1.0
        2.0

    """
    #TODO: May need a dtype, for when we want a range of integers -- indexes, for example. 

    lo = Float(doc='start of range')
    hi = Float(doc='end of range')

    step = Float(default=1.0,
                 doc='fixed step size between elements')

    base = Float(default=math.e,
                 doc='fixed multiplier between elements')

    def __iter__(self):
        """ Get valid values in interval"""
        def gen():
            val = self.lo
            while val < self.hi:
                if self.step:
                    val += self.step
                    yield val
                else:
                    val *= self.base
                    yield val
        return gen()


class ValidationRange(core.Type):
    """
    ValidationRange represents a Range used only for validating a number.
    """


class JSONType(String):
    """
    Wrapper over a String which holds a serializable object.
    On set/get Json loand/dump will be called.
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
    Traits type that wraps a numpy dtype specification.
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

   
