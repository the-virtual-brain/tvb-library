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

The Data component of traited array datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""

import numpy
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.traits.util as util
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.types_mapped as mapped


class FloatArrayData(mapped.Array):
    """ A numpy.ndarray of dtype numpy.float64 """
    _ui_name = "Floating-point array"
    dtype = basic.DType(default=numpy.float64)


class IntegerArrayData(mapped.Array):
    """ A numpy.ndarray of dtype numpy.int32 """
    _ui_name = "Array of integers"
    dtype = basic.DType(default=numpy.int32)


class ComplexArrayData(mapped.Array):
    """ A numpy.ndarray of dtype numpy.complex128 """
    _ui_name = "Array of complex numbers"
    dtype = basic.DType(default=numpy.complex128)


class BoolArrayData(mapped.Array):
    """ A numpy.ndarray of dtype numpy.bool """
    _ui_name = "Boolean array"
    dtype = basic.DType(default=numpy.bool)


# if you want variable length strings, you must use dtype=object
# otherwise, must specify max lenth as 'na' where n is integer,
# e.g. dtype='100a' for a string w/ max len 100 characters.
class StringArrayData(mapped.Array):
    """ A numpy.ndarray of dtype str """
    _ui_name = "Array of strings"
    dtype = "128a" # "42a"


class PositionArrayData(FloatArrayData):
    """ An array specifying position. """
    _ui_name = "Array of positions"
    
    coordinate_system = basic.String(
        label = "Coordinate system",
        default = "cartesian", 
        doc = """The coordinate system used to specify the positions.
            Eg: 'spherical', 'polar'""")

    coordinate_space = basic.String( # ?Make this only an extension where needed?
        label = "Coordinate space",
        default = "None",
        doc = "The standard space the positions are in, eg, 'MNI', 'colin27'")


class OrientationArrayData(FloatArrayData):
    """ An array specifying orientations. """
    _ui_name = "Array of orientations"

    coordinate_system_or = basic.String(
        label = "Coordinate system",
        default = "cartesian")


class IndexArrayData(IntegerArrayData):
    """ An array that indexes another array. """
    _ui_name = "Index array"
 
    target = mapped.Array(
        label = "Indexed array",
        doc = "A link to the array that the indices index.")


class MappedArrayData(MappedType):
    """ Array that will be Mapped as a table in DB"""
    
    title = basic.String
    label_x, label_y = basic.String, basic.String
    aggregation_functions = basic.JSONType(required = False)
    dimensions_labels = basic.JSONType(required = False)
    
    nr_dimensions, length_1d, length_2d, length_3d, length_4d = [basic.Integer]*5
    array_data = mapped.Array()  
    
    __generate_table__ = True

    @property
    def display_name(self):
        """
        Overwrite from superclass and add title field
        """
        previous = super(MappedArrayData, self).display_name
        if previous is None:
            return str(self.title)
        return str(self.title) +  " " + previous
       
       
    @property
    def shape(self):
        """
        Shape for current wrapped numpy array.
        """
        return self.aggregation_functions.shape
    
     
