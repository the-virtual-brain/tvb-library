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
Filler analyzer: Takes a TimeSeries object and returns a Float.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.analyzers.metrics_base as metrics_base
import tvb.datatypes.time_series as time_series_module
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class GlobalVariance(metrics_base.BaseTimeseriesMetricAlgorithm):
    """
    Zero-centres all the time-series and then calculates the variance over all 
    data points.
    
    Input:
    TimeSeries datatype 
    
    Output: 
    Float
    
    This is a crude indicator of "excitability" or oscillation amplitude of the
    models over the entire network.
    """
    
    time_series = time_series_module.TimeSeries(
        label = "Time Series", 
        required = True,
        doc="""The TimeSeries for which the zero centered Global Variance is to
            be computed.""")
    
    def evaluate(self):
        """
        Compute the zero centered global variance of the time_series. 
        """
        cls_attr_name = self.__class__.__name__+".time_series"
        self.time_series.trait["data"].log_debug(owner = cls_attr_name)
        
        zero_mean_data = (self.time_series.data - self.time_series.data.mean(axis=0))
        global_variance = zero_mean_data.var()
        return global_variance  
    
    
    def result_shape(self):
        """
        Returns the shape of the main result of the ... 
        """
        return (1,)
    
    
    def result_size(self):
        """
        Returns the storage size in Bytes of the results of the ... .
        """
        return 8.0 #Bytes
    
    
    def extended_result_size(self):
        """
        Returns the storage size in Bytes of the extended result of the ....
        That is, it includes storage of the evaluated ...
        """
        return 8.0 #Bytes


