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

Scientific methods for the Array datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
import tvb.datatypes.arrays_data as arrays_data
from tvb.basic.traits.types_mapped import MappedType


class FloatArrayScientific(arrays_data.FloatArrayData):
    """ This class exists to add scientific methods to FloatArrayData """
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Array type": self.__class__.__name__}
        summary["Shape"] = self.shape
        summary["Maximum"] = self.value.max()
        summary["Minimum"] = self.value.min()
        summary["Mean"] = self.value.mean()
        return summary


class IntegerArrayScientific(arrays_data.IntegerArrayData):
    """ This class exists to add scientific methods to IntegerArrayData """
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Array type": self.__class__.__name__}
        summary["Shape"] = self.shape
        summary["Maximum"] = self.value.max()
        summary["Minimum"] = self.value.min()
        summary["Mean"] = self.value.mean()
        summary["Median"] = numpy.median(self.value)
        return summary


class ComplexArrayScientific(arrays_data.ComplexArrayData):
    """ This class exists to add scientific methods to ComplexArrayData """
    
    _stored_metadata = [key for key in MappedType.ALL_METADATA_ARRAY.keys() 
                          if key != MappedType.METADATA_ARRAY_VAR]
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Array type": self.__class__.__name__}
        summary["Shape"] = self.shape
        summary["Maximum"] = self.value.max()
        summary["Minimum"] = self.value.min()
        summary["Mean"] = self.value.mean()
        return summary


class BoolArrayScientific(arrays_data.BoolArrayData):
    """ This class exists to add scientific methods to BoolArrayData """
    
    _stored_metadata = [MappedType.METADATA_ARRAY_SHAPE]
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Array type": self.__class__.__name__}
        summary["Shape"] = self.shape
        return summary


class StringArrayScientific(arrays_data.StringArrayData):
    """ This class exists to add scientific methods to StringArrayData """
    
    _stored_metadata = [MappedType.METADATA_ARRAY_SHAPE]
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Array type": self.__class__.__name__}
        summary["Shape"] = self.shape
        return summary


class PositionArrayScientific(arrays_data.PositionArrayData, FloatArrayScientific):
    """ This class exists to add scientific methods to PositionArrayData"""
    pass


class OrientationArrayScientific(arrays_data.OrientationArrayData, FloatArrayScientific):
    """ This class exists to add scientific methods to OrientationArrayData """
    pass


class IndexArrayScientific(arrays_data.IndexArrayData, IntegerArrayScientific):
    """ This class exists to add scientific methods to IndexArrayData """
    pass


class MappedArrayScientific(arrays_data.MappedArrayData):
    """This class exists to add scientific methods to MappedArrayData"""
    __tablename__ = None



