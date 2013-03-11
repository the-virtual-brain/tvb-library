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
Calculate temporal cross correlation on a TimeSeries datatype and return a 
temporal_correlations.CrossCorrelation dataype.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
from scipy.signal.signaltools import correlate
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.datatypes.temporal_correlations as temporal_correlations
import tvb.basic.traits.core as core
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)




class CrossCorrelate(core.Type):
    """
    Compute the node-pairwise cross-correlation of the given input 4D TimeSeries 
    datatype.
    
    Return a CrossCorrelation datatype. It contains the cross-correlation 
    sequences for all possible combinations of the nodes.
    
    See: http://www.scipy.org/doc/api_docs/SciPy.signal.signaltools.html#correlate
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The time-series for which the cross correlation sequences are 
        calculated.""")
    
    
    def evaluate(self):
        """
        Cross-correlate two one-dimensional arrays.
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        #(tpts, nodes, nodes, state-variables, modes)
        result_shape = self.result_shape(self.time_series.data.shape)
        LOG.info("result shape will be: %s" % str(result_shape))
        
        result = numpy.zeros(result_shape)
        
        #TODO: For region level, 4s, 2000Hz, this takes ~3hours... (which makes node_coherence seem positively speedy...)
        #TODO: Probably best to add a keyword for offsets, so we just compute +- some "small" range...
        #One inter-node correllation, across offsets, for each state-var & mode.
        for mode in range(result_shape[4]):
            for var in range(result_shape[3]):
                data = self.time_series.data[:, var, :, mode]
                data = data - data.mean(axis=0)[numpy.newaxis, :]
                #TODO: Work out a way around the 4 level loop,
                for n1 in range(result_shape[1]):
                    for n2 in range(result_shape[2]):
                        result[:, n1, n2, var, mode] = correlate(data[:, n1],
                                                                 data[:, n2],
                                                                 mode="same")
        
        util.log_debug_array(LOG, result, "result")
        
        offset = (self.time_series.sample_period *
                  numpy.arange(-(numpy.floor(result_shape[0] / 2.0)),
                               numpy.ceil(result_shape[0] / 2.0)))
        
        cross_corr = temporal_correlations.CrossCorrelation(
            source = self.time_series,
            array_data = result,
            time = offset,
            use_storage = False)
        
        return cross_corr
    
    
    def result_shape(self, input_shape):
        """Returns the shape of the main result of ...."""
        result_shape = (input_shape[0], input_shape[2], input_shape[2],
                        input_shape[1], input_shape[3])
        return result_shape
    
    
    def result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the main result of .
        """
        result_size = numpy.sum(map(numpy.prod,
                                    self.result_shape(input_shape))) * 8.0 #Bytes
        return result_size
    
    
    def extended_result_size(self, input_shape):
        """
        Returns the storage size in Bytes of the extended result of the ....
        That is, it includes storage of the evaluated ... attributes
        such as ..., etc.
        """
        extend_size = self.result_size(input_shape) #Currently no derived attributes.
        return extend_size



