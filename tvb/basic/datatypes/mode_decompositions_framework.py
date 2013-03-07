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
Framework methods for the Mode Decomposition datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import tvb.basic.datatypes.mode_decompositions_data as mode_decompositions_data


class PrincipalComponentsFramework(mode_decompositions_data.PrincipalComponentsData):
    """
    This class exists to add framework methods to PrincipalComponentsData.
    """
    __tablename__ = None
    
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.store_data_chunk('weights', partial_result.weights,
                              grow_dimension=2, close_file=False)
        
        self.store_data_chunk('fractions', partial_result.fractions,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_norm_source()
        self.store_data_chunk('norm_source', partial_result.norm_source,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_component_time_series()
        self.store_data_chunk('component_time_series', 
                              partial_result.component_time_series,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_normalised_component_time_series()
        self.store_data_chunk('normalised_component_time_series',
                              partial_result.normalised_component_time_series,
                              grow_dimension=1, close_file=False)



class IndependentComponentsFramework(mode_decompositions_data.IndependentComponentsData):
    """
    This class exists to add framework methods to IndependentComponentsData.
    """
    __tablename__ = None
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        
        self.store_data_chunk('unmixing_matrix', partial_result.unmixing_matrix,
                              grow_dimension=2, close_file=False)
                              
        self.store_data_chunk('prewhitening_matrix', partial_result.prewhitening_matrix,
                              grow_dimension=2, close_file=False)
                              
        
        partial_result.compute_norm_source()
        self.store_data_chunk('norm_source', partial_result.norm_source,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_component_time_series()
        self.store_data_chunk('component_time_series', 
                              partial_result.component_time_series,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_normalised_component_time_series()
        self.store_data_chunk('normalised_component_time_series',
                              partial_result.normalised_component_time_series,
                              grow_dimension=1, close_file=False)
        
        partial_result.compute_mixing_matrix()
        self.store_data_chunk('mixing_matrix', partial_result.mixing_matrix,
                              grow_dimension=2, close_file=False)


