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
Scientific methods for the LookUpTables datatypes.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

#Third party modules
import numpy

#Modules from "The Virtual Brain"
import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.basic.datatypes.lookup_tables_data as lookup_tables_data


class LookUpTableScientific(lookup_tables_data.LookUpTableData):
    """
    This class primarily exists to add scientific methods to the 
    LookUpTablesData class, if any ...
    
    """
    __tablename__ = None
    


class PsiTableScientific(lookup_tables_data.PsiTableData, LookUpTableScientific):
    
    __tablename__ = None
    
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialization.
        """
        super(PsiTableScientific, self).configure()
        
        # Check if dx and invdx have been computed
        if self.number_of_values == 0:
            self.number_of_values = self.data.shape[0]

        if self.dx.size == 0:
            self.compute_search_indices()

        
        
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this dataType, if any ... 
        """
        summary = {"Number of values": self.number_of_values}
        return summary
        
    def compute_search_indices(self):
        """
        ...
        """
        self.dx = ((self.xmax - self.xmin) / (self.number_of_values) - 1)
        self.invdx = 1 / self.dx
        
        self.trait["dx"].log_debug(owner=self.__class__.__name__)
        self.trait["invdx"].log_debug(owner=self.__class__.__name__)
    
    def search_value(self, val):
        """ 
        Search a value in this look up table
        """
         
        if self.xmin: 
            y = val - self.xmin
        else: 
            y = val
            
        ind = numpy.array(y * self.invdx, dtype=int)
        try:
            return self.data[ind] + self.df[ind]*(y - ind * self.dx)
        except IndexError: # out of bounds
            return numpy.NaN 
            # NOTE: not sure if we should return a NaN or make val = self.max
            
    pass
    

class NerfTableScientific(lookup_tables_data.NerfTableData, LookUpTableScientific):
    __tablename__ = None
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialization.
        """
        super(NerfTableScientific, self).configure()
        

        if self.number_of_values == 0:
            self.number_of_values = self.data.shape[0]

        if self.dx.size == 0:
            self.compute_search_indices()
            
            
        
        
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this dataType, if any ... 
        """
        summary = {"Number of values": self.number_of_values}
        return summary
        
    def compute_search_indices(self):
        """
        ...
        """
        self.dx = ((self.xmax - self.xmin) / (self.number_of_values) - 1)
        self.invdx = 1 / self.dx
        
    
    def search_value(self, val):
        """ 
        Search a value in this look up table
        """ 
        
        if self.xmin: 
            y = val - self.xmin
        else: 
            y = val
            
        ind = numpy.array(y * self.invdx, dtype=int)
        
        try:
            return self.data[ind] + self.df[ind]*(y - ind * self.dx)
        except IndexError: # out of bounds
            return numpy.NaN 
            # NOTE: not sure if we should return a NaN or make val = self.max
            # At the moment, we force the input values to be within a known range
    pass
