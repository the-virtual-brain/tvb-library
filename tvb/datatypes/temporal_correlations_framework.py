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
Framework methods for the Temporal Correlation datatypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.temporal_correlations_data as temporal_correlations_data


class CrossCorrelationFramework(temporal_correlations_data.CrossCorrelationData):
    """
    This class exists to add framework methods to CrossCorrelationData.
    """
    __tablename__ = None
    
    
    def configure(self):
        """After populating few fields, compute the rest of the fields"""
        # Do not call super, because that accesses data not-chunked
        self.nr_dimensions = len(self.read_data_shape())
        for i in range(self.nr_dimensions): 
            setattr(self, 'length_%dd' % (i+1), int(self.read_data_shape()[i]))
    
    
    def read_data_shape(self):
        """
        Expose shape read on field 'data'
        """
        return self.get_data_shape('array_data')
    
    
    def read_data_slice(self, data_slice):
        """
        Expose chunked-data access.
        """
        return self.get_data('array_data', data_slice)
    
    
    def write_data_slice(self, partial_result):
        """
        Append chunk.
        """
        self.store_data_chunk('array_data', partial_result.array_data,
                              grow_dimension=3, close_file=False)



