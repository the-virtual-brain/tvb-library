# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the ptroject, you need to sign a contributor's license. 
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

The Data component of the LookUpTables datatypes. These are intended to be 
tables containing the values of computationally expensive functions used
within the tvb.simulator.models.

At present, we only make use of these in the Brunel and Wang model.

.. moduleauthor:: Paula Sanz Leon <paula@tvb.invalid>

"""



import numpy
import tvb.datatypes.arrays as arrays
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.data_readers as readers
from tvb.basic.logger.builder import get_logger
from tvb.basic.traits.types_mapped import MappedType


LOG = get_logger(__name__)

# NOTE: For the time being, we make use of the precalculated tables we already have.
# however, we LookUpTables datatypes could have a compute() method to 
# calculate a given function (using Equation datatypes? ). 


class LookUpTableData(MappedType):
    """
    Lookup Tables for storing pre-computed functions.
    Specific table subclasses are implemented below.
    
    """
    
    _base_classes = ['LookUpTables']

    table = readers.Table(folder_path = "tables")
    
    equation = basic.String(
        label = "String representation of the precalculated function",
        doc = """A latex representation of the function whose values are stored 
            in the table, with the extra escaping needed for interpretation via sphinx.""")
    
    xmin = arrays.FloatArray(
        label = "x-min",
        console_default = table.read_dimension('min_max', 0, field = "xmin"), 
        doc = """Minimum value""")
        
    xmax = arrays.FloatArray(
        label = "x-max",
        console_default = table.read_dimension('min_max', 1, field = "xmax"), 
        doc = """Maximum value""")
    
    data = arrays.FloatArray(
        label = "data",
        console_default = table.read_dimension('f', field = "data"), 
        doc = """Tabulated values""")
    
    number_of_values = basic.Integer(
        label = "Number of values",
        default = 0,
        doc = """The number of values in the table """)
        
    df = arrays.FloatArray(
        label = "df",
        console_default = table.read_dimension('df', field = "df"), 
        doc = """.""")
     
    dx = arrays.FloatArray(
        label = "dx",
        default = numpy.array([]), 
        doc = """Tabulation step""")    
    
    invdx = arrays.FloatArray(
       label = "invdx",
       default = numpy.array([]),
       doc = """.""")
            
    

class PsiTableData(LookUpTableData):
    """
    Look up table containing the values of a function representing the time-averaged gating variable
    :math:`\\psi(\\nu)` as a function of the presynaptic rates :math:`\\nu` 
    
    """
    
    def __init__(self, **kwargs):
        super(PsiTableData, self).__init__(**kwargs)
        self.table.reload(self.__class__, folder_path = "tables", file_name = "psi.npz")
    
    

class NerfTableData(LookUpTableData):
    """
    Look up table containing the values of Nerf integral within the :math:`\\phi`
    function that describes how the discharge rate vary as a function of parameters
    defining the statistical properties of the membrane potential in presence of synaptic inputs.
    
    """
    
    def __init__(self, **kwargs):
        super(NerfTableData, self).__init__(**kwargs)
        self.table.reload(self.__class__, folder_path = "tables", file_name = "nerf_int.npz")
        
    
    

