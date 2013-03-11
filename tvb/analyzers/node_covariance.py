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
Calculate a ... on a .. datatype and return a ...

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.datatypes.graph as graph
import tvb.basic.traits.core as core
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)




class NodeCovariance(core.Type):
    """
    Compute the temporal covariance of nodes in a TimeSeries dataType.
    A nodes x nodes matrix is returned for each (state-variable, mode).
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries to which the NodeCovariance is to be applied.""")
    
    
    def evaluate(self):
        """
        Compute the temporal covariance between nodes in the time_series.
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        data_shape = self.time_series.data.shape
        
        #(nodes, nodes, state-variables, modes)
        result_shape = (data_shape[2], data_shape[2], data_shape[1], data_shape[3])
        LOG.info("result shape will be: %s" % str(result_shape))
        
        result = numpy.zeros(result_shape)
        
        #One inter-node temporal covariance matrix for each state-var & mode.
        for mode in range(data_shape[3]):
            for var in range(data_shape[1]):
                data = self.time_series.data[:, var, :, mode]
                data = data - data.mean(axis=0)[numpy.newaxis, 0]
                result[:, :, var, mode] = numpy.cov(data.T)
        
        util.log_debug_array(LOG, result, "result")
        
        covariance = graph.Covariance(source = self.time_series,
                                      array_data = result,
                                      use_storage = False)
        
        return covariance
    
    
    def result_shape(self, input_shape):
        """
        Returns the shape of the main result of the NodeCovariance analysis.
        """
        result_shape = (input_shape[2], input_shape[2], input_shape[1], input_shape[3])
        return result_shape
    
    
    def result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the NodeCovariance result.
        """
        result_size = numpy.prod(self.result_shape(input_shape)) * 8.0 #Bytes
        return result_size
    
    
    def extended_result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the NodeCovariance extended result.
        That is, it includes storage of the evaluated PrincipleComponents
        attributes such as norm_source, component_time_series, etc.
        """
        extend_size= self.result_size(input_shape)  #Currently no derived attributes.
        return extend_size


