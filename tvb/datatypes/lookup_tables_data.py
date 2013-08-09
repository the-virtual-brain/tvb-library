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
    __tablename__ = None
    
    
    def __init__(self, **kwargs):
        super(PsiTableData, self).__init__(**kwargs)
        self.table.reload(self.__class__, folder_path = "tables", file_name = "psi.npz")
    
    

class NerfTableData(LookUpTableData):
    """
    Look up table containing the values of Nerf integral within the :math:`\\phi`
    function that describes how the discharge rate vary as a function of parameters
    defining the statistical properties of the membrane potential in presence of synaptic inputs.
    
    """
    __tablename__ = None
    
    
    def __init__(self, **kwargs):
        super(NerfTableData, self).__init__(**kwargs)
        self.table.reload(self.__class__, folder_path = "tables", file_name = "nerf_int.npz")
        
    
    

