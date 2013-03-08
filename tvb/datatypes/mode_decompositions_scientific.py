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
Scientific methods for the Spectral datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import numpy
import tvb.datatypes.mode_decompositions_data as mode_decompositions_data
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class PrincipalComponentsScientific(mode_decompositions_data.PrincipalComponentsData):
    """
    This class exists to add scientific methods to PrincipalComponentsData.
    """
    __tablename__ = None
    
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialization.
        """
        if self.state is not None:
            super(PrincipalComponentsScientific, self).configure()
        
        LOG.debug("Instance state: %s" % str(self.state))
        if self.state is None and self.weights.size != 0:
            if self.norm_source.size == 0:
                self.compute_norm_source()
            
            if self.component_time_series.size == 0:
                self.compute_component_time_series()
            
            if self.normalised_component_time_series.size == 0:
                self.compute_normalised_component_time_series()
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Mode decomposition type": self.__class__.__name__}
        summary["Source"] = self.source.title
        #summary["Number of variables"] = self...
        #summary["Number of mewasurements"] = self...
        #summary["Number of components"] = self...
        #summary["Number required for 95%"] = self...
        return summary
    
    
    def compute_norm_source(self):
        """Normalised source time-series."""
        self.norm_source = ((self.source.data - self.source.data.mean(axis=0)) /
                            self.source.data.std(axis=0))
        self.trait["norm_source"].log_debug(owner=self.__class__.__name__)
    
    
    #TODO: ??? Any value in making this a TimeSeries datatypes ???
    def compute_component_time_series(self):
        """Compnent time-series."""
        #TODO: Generalise -- it currently assumes 4D TimeSeriesSimulator...
        ts_shape = self.source.data.shape
        component_ts = numpy.zeros(ts_shape)
        for var in range(ts_shape[1]):
            for mode in range(ts_shape[3]):
                w = self.weights[:, :, var, mode]
                ts = self.source.data[:, var, :, mode]
                component_ts[:, var, :, mode] = numpy.dot(w, ts.T).T
        
        self.component_time_series = component_ts
        self.trait["component_time_series"].log_debug(owner=self.__class__.__name__)
    
    
    #TODO: ??? Any value in making this a TimeSeries datatypes ???
    def compute_normalised_component_time_series(self):
        """normalised_Compnent time-series."""
        #TODO: Generalise -- it currently assumes 4D TimeSeriesSimulator...
        ts_shape = self.source.data.shape
        component_ts = numpy.zeros(ts_shape)
        for var in range(ts_shape[1]):
            for mode in range(ts_shape[3]):
                w = self.weights[:, :, var, mode]
                nts = self.norm_source[:, var, :, mode]
                component_ts[:, var, :, mode] = numpy.dot(w, nts.T).T
        
        self.normalised_component_time_series = component_ts
        self.trait["normalised_component_time_series"].log_debug(owner=self.__class__.__name__)



class IndependentComponentsScientific(mode_decompositions_data.IndependentComponentsData):
    """
    This class exists to add scientific methods to IndependentComponentsData.
    
    """
    __tablename__ = None
    
    def configure(self):
        """
        Invoke the compute methods for computable attributes that haven't been
        set during initialisation.
        """
        if self.state is not None:
            super(IndependentComponentsScientific, self).configure()
        
        LOG.debug("Instance state: %s" % str(self.state))
        if self.state is None and self.unmixing_matrix.size != 0:
            if self.norm_source.size == 0:
                self.compute_norm_source()
            
            if self.component_time_series.size == 0:
                self.compute_component_time_series()
            
            if self.normalised_component_time_series.size == 0:
                self.compute_normalised_component_time_series()
                
                
    def compute_norm_source(self):
        """Normalised source time-series."""
        self.norm_source = ((self.source.data - self.source.data.mean(axis=0)) /
                            self.source.data.std(axis=0))
        self.trait["norm_source"].log_debug(owner=self.__class__.__name__)
        
    #TODO: ??? Any value in making this a TimeSeries datatypes ??? -- 
    # (PAULA) >> a component time-series datatype?
    def compute_component_time_series(self):
        """Component time-series."""
        #TODO: Generalise -- it currently assumes 4D TimeSeriesSimulator...
        ts_shape = self.source.data.shape
        component_ts_shape = (ts_shape[0], ts_shape[1], self.n_components, ts_shape[3])
        component_ts = numpy.zeros(component_ts_shape)
        for var in range(ts_shape[1]):
            for mode in range(ts_shape[3]):
                w = self.unmixing_matrix[:, :, var, mode]
                k = self.prewhitening_matrix[:, :, var, mode]
                ts = self.source.data[:, var, :, mode]
                component_ts[:, var, : , mode] = numpy.dot(w, numpy.dot(k, ts.T)).T         
        
        self.component_time_series = component_ts
        self.trait["component_time_series"].log_debug(owner=self.__class__.__name__)
        
        
    #TODO: ??? Any value in making this a TimeSeries datatypes ???
    def compute_normalised_component_time_series(self):
        """normalised_component time-series."""
        #TODO: Generalise -- it currently assumes 4D TimeSeriesSimulator...
        ts_shape = self.source.data.shape
        component_ts_shape = (ts_shape[0], ts_shape[1], self.n_components, ts_shape[3])
        component_nts = numpy.zeros(component_ts_shape)
        for var in range(ts_shape[1]):
            for mode in range(ts_shape[3]):
                w = self.unmixing_matrix[:, :, var, mode]
                k = self.prewhitening_matrix[:, :, var, mode]
                nts = self.norm_source[:, var, :, mode]
                component_nts[:, var, :, mode] = numpy.dot(w, numpy.dot(k, nts.T)).T              
        self.normalised_component_time_series = component_nts
        self.trait["normalised_component_time_series"].log_debug(owner=self.__class__.__name__)
        
    def compute_mixing_matrix(self):
        """ 
        Compute the linear mixing matrix A, so X = A * S , 
        where X is the observed data and S contain the independent components 
            """
        ts_shape = self.source.data.shape
        mixing_matrix_shape = (ts_shape[2], self.n_components, ts_shape[1], ts_shape[3])
        mixing_matrix = numpy.zeros(mixing_matrix_shape)
        for var in range(ts_shape[1]):
            for mode in range(ts_shape[3]):
                w = self.unmixing_matrix[:, :, var, mode]
                k = self.prewhitening_matrix[:, :, var, mode]
                temp = numpy.matrix(numpy.dot(w, k))
                mixing_matrix[:, :, var, mode] = numpy.array(numpy.dot(temp.T ,(numpy.dot(temp, temp.T)).I))
        self.mixing_matrix = mixing_matrix
        self.trait["mixing_matrix"].log_debug(owner=self.__class__.__name__)
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Mode decomposition type": self.__class__.__name__}
        summary["Source"] = self.source.title
        #summary["Number of variables"] = str(self.source.read_data_shape()[2])
        #summary["Number of measurements"] = str(self.source.read_data_shape()[0])
        #summary["Number of components"] = str(self.n_components)
        #summary.update(self.get_info_about_array('array_data'))
        return summary


