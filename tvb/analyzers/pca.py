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
Perform Principal Component Analysis (PCA) on a TimeSeries datatype and return
a PrincipalComponents datatype.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

#TODO: Make an appropriate datatype for the output, include properties to
#      project source timesereis to component timeserries, etc

import numpy
import matplotlib.mlab as mlab
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.datatypes.mode_decompositions as mode_decompositions
import tvb.basic.traits.core as core
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class PCA(core.Type):
    """
    Return principal component weights and the fraction of the variance that 
    they explain. 
    
    PCA takes time-points as observations and nodes as variables.
    
    NOTE: The TimeSeries must be longer(more time-points) than the number of
          nodes -- Mostly a problem for TimeSeriesSurface datatypes, which, if 
          sampled at 1024Hz, would need to be greater than 16 seconds long.
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries to which the PCA is to be applied. NOTE: The 
            TimeSeries must be longer(more time-points) than the number of nodes
            -- Mostly a problem for surface times-series, which, if sampled at
            1024Hz, would need to be greater than 16 seconds long.""")
    
    #TODO: Maybe should support first N components or neccessary components to
    #      explain X% of the variance. NOTE: For default surface the weights
    #      matrix has a size ~ 2GB * modes * vars...
    
    def evaluate(self):
        """
        Compute the temporal covariance between nodes in the time_series. 
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        ts_shape = self.time_series.data.shape
        
        #Need more measurements than variables
        if ts_shape[0] < ts_shape[2]:
            msg = "PCA requires a longer timeseries (tpts > number of nodes)."
            LOG.error(msg)
            raise Exception, msg
        
        #(nodes, nodes, state-variables, modes)
        weights_shape = (ts_shape[2], ts_shape[2], ts_shape[1], ts_shape[3])
        LOG.info("weights shape will be: %s" % str(weights_shape))
        
        fractions_shape = (ts_shape[2], ts_shape[1], ts_shape[3])
        LOG.info("fractions shape will be: %s" % str(fractions_shape))
        
        weights = numpy.zeros(weights_shape)
        fractions = numpy.zeros(fractions_shape)
        
        #One inter-node temporal covariance matrix for each state-var & mode.
        for mode in range(ts_shape[3]):
            for var in range(ts_shape[1]):
                data = self.time_series.data[:, var, :, mode]
                data_pca = mlab.PCA(data)
                fractions[:, var, mode ] = data_pca.fracs
                weights[:, :, var, mode] = data_pca.Wt
        
        util.log_debug_array(LOG, fractions, "fractions")
        util.log_debug_array(LOG, weights, "weights")
        
        pca_result = mode_decompositions.PrincipalComponents(
            source = self.time_series,
            fractions = fractions,
            weights = weights,
            use_storage = False)
        
        return pca_result
    
    
    def result_shape(self, input_shape):
        """
        Returns the shape of the main result of the PCA analysis -- compnnent 
        weights matrix and a vector of fractions.
        """
        weights_shape = (input_shape[2], input_shape[2], input_shape[1],
                         input_shape[3])
        fractions_shape = (input_shape[2], input_shape[1], input_shape[3])
        return [weights_shape, fractions_shape]
    
    
    def result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the results of the PCA analysis.
        """
        result_size = numpy.sum(map(numpy.prod,
                                    self.result_shape(input_shape))) * 8.0 #Bytes
        return result_size
    
    
    def extended_result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the extended result of the PCA.
        That is, it includes storage of the evaluated PrincipleComponents
        attributes such as norm_source, component_time_series, etc.
        """
        result_size = self.result_size(input_shape)
        extend_size = result_size #Main arrays
        extend_size = extend_size + numpy.prod(input_shape) * 8.0 #norm_source
        extend_size = extend_size + numpy.prod(input_shape) * 8.0 #component_time_series
        extend_size = extend_size + numpy.prod(input_shape) * 8.0 #normalised_component_time_series
        return extend_size


