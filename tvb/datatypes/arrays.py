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

The Array datatypes. This brings together the scientific and framework 
methods that are associated with the Array datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.arrays_scientific as arrays_scientific
import tvb.datatypes.arrays_framework as arrays_framework
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class FloatArray(arrays_scientific.FloatArrayScientific, arrays_framework.FloatArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the FloatArray datatype.
    
    ::
        
                           FloatArrayData
                                 |
                                / \\
             FloatArrayFramework   FloatArrayScientific
                                \ /
                                 |
                             FloatArray
        
    
    """
    pass


class IntegerArray(arrays_scientific.IntegerArrayScientific,
                 arrays_framework.IntegerArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the IntegerArray datatype.
    
    ::
        
                          IntegerArrayData
                                 |
                                / \\
           IntegerArrayFramework   IntegerArrayScientific
                                \ /
                                 |
                            IntegerArray
        
    
    """
    pass


class ComplexArray(arrays_scientific.ComplexArrayScientific,
                 arrays_framework.ComplexArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the ComplexArray datatype.
    
    ::
        
                          ComplexArrayData
                                 |
                                / \\
           ComplexArrayFramework   ComplexArrayScientific
                                \ /
                                 |
                            ComplexArray
        
    
    """
    pass


class BoolArray(arrays_scientific.BoolArrayScientific,
                 arrays_framework.BoolArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the BoolArray datatype.
    
    ::
        
                           BoolArrayData
                                 |
                                / \\
              BoolArrayFramework   BoolArrayScientific
                                \ /
                                 |
                             BoolArray
        
    
    """
    pass


class StringArray(arrays_scientific.StringArrayScientific,
                 arrays_framework.StringArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the StringArray datatype.
    
    ::
        
                          StringArrayData
                                 |
                                / \\
            StringArrayFramework   StringArrayScientific
                                \ /
                                 |
                            StringArray
        
    
    """
    pass


class PositionArray(arrays_scientific.PositionArrayScientific,
                 arrays_framework.PositionArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the PositionArray datatype.
    
    ::
        
                          PositionArrayData
                                 |
                                / \\
          PositionArrayFramework   PositionArrayScientific
                                \ /
                                 |
                            PositionArray
        
    
    """
    pass


class OrientationArray(arrays_scientific.OrientationArrayScientific,
                       arrays_framework.OrientationArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the OrientationArray datatype.
    
    ::
        
                        OrientationArrayData
                                 |
                                / \\
       OrientationArrayFramework   OrientationArrayScientific
                                \ /
                                 |
                          OrientationArray
        
    
    """
    pass


class IndexArray(arrays_scientific.IndexArrayScientific,
                 arrays_framework.IndexArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the IndexArray datatype.
    
    ::
        
                           IndexArrayData
                                 |
                                / \\
             IndexArrayFramework   IndexArrayScientific
                                \ /
                                 |
                             IndexArray
        
    
    """
    pass


class MappedArray(arrays_scientific.MappedArrayScientific,
                  arrays_framework.MappedArrayFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the MappedArray datatype.
    
    ::
        
                           MappedArrayData
                                 |
                                / \\
             MappedArrayFramework   MappedArrayScientific
                                \ /
                                 |
                             MappedArray
        
    """
    pass


if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Array datatypes initializes without error.
    FLOAT_ARRAY = FloatArray()
    INTEGER_ARRAY = IntegerArray()
    COMPLEX_ARRAY = ComplexArray()
    BOOL_ARRAY = BoolArray()
    STRING_ARRAY = StringArray()
    POSITION_ARRAY = PositionArray()
    ORIENTATION_ARRAY = OrientationArray()
    INDEX_ARRAY = IndexArray()
    MAPPED_ARRAY = MappedArray()
    
    LOG.info("Default Array datatypes initialized without error...")

