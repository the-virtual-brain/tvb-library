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
Scientific methods for the TimeSeries dataTypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.datatypes.time_series_data as time_series_data


class TimeSeriesScientific(time_series_data.TimeSeriesData):
    """ This class exists to add scientific methods to TimeSeriesData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Time-series type": self.__class__.__name__}
        summary["Time-series name"] = self.title
        summary["Dimensions"] = self.labels_ordering
        summary["Time units"] = self.sample_period_unit
        summary["Sample period"] = self.sample_period
        summary["Length"] = self.sample_period * self.get_data_shape('data')[0]
        summary.update(self.get_info_about_array('data'))
        return summary



class TimeSeriesEEGScientific(time_series_data.TimeSeriesEEGData, 
                              TimeSeriesScientific):
    """ This class exists to add scientific methods to TimeSeriesEEGData. """
    pass
    
#    #NOTE: Explicitly adding number_of_sensors is sort of redundant given
#    #      "Shape" and "Dimensions", however, maybe worthwhile as convinience?
#    def _find_summary_info(self):
#        """ Extend the base class's summary dictionary. """
#        summary = super(TimeSeriesEEGScientific, self)._find_summary_info()
#        summary["Number of EEG sensors"] = self.sensors.number_of_sensors
#        return summary


class TimeSeriesMEGScientific(time_series_data.TimeSeriesMEGData, 
                              TimeSeriesScientific):
    """ This class exists to add scientific methods to TimeSeriesMEGData. """
    pass


class TimeSeriesRegionScientific(time_series_data.TimeSeriesRegionData, 
                                 TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesRegionData.
    """
    pass


class TimeSeriesSurfaceScientific(time_series_data.TimeSeriesSurfaceData, 
                                  TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesSurfaceData.
    """
    pass


class TimeSeriesVolumeScientific(time_series_data.TimeSeriesVolumeData,
                                 TimeSeriesScientific):
    """
    This class exists to add scientific methods to TimeSeriesVolumeData.
    """
    pass

