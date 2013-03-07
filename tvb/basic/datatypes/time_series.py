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
The TimeSeries datatypes. This brings together the scientific and framework 
methods that are associated with the time-series data.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.basic.datatypes.time_series_scientific as time_series_scientific
import tvb.basic.datatypes.time_series_framework as time_series_framework


class TimeSeries(time_series_scientific.TimeSeriesScientific,
                 time_series_framework.TimeSeriesFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeries datatype.
    
    ::
        
                           TimeSeriesData
                                 |
                                / \\
             TimeSeriesFramework   TimeSeriesScientific
                                \ /
                                 |
                             TimeSeries
        
    
    """
    pass



class TimeSeriesEEG(time_series_scientific.TimeSeriesEEGScientific,
                    time_series_framework.TimeSeriesEEGFramework, TimeSeries):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeriesEEG datatype.
    
    ::
        
                         TimeSeriesEEGData
                                 |
                                / \\
          TimeSeriesEEGFramework   TimeSeriesEEGScientific
                                \ /
                                 |
                           TimeSeriesEEG
        
    
    """
    pass


class TimeSeriesMEG(time_series_scientific.TimeSeriesMEGScientific,
                    time_series_framework.TimeSeriesMEGFramework, TimeSeries):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeriesMEG datatype.
    
    ::
        
                         TimeSeriesMEGData
                                 |
                                / \\
          TimeSeriesMEGFramework   TimeSeriesMEGScientific
                                \ /
                                 |
                           TimeSeriesMEG
        
    
    """
    pass


class TimeSeriesRegion(time_series_scientific.TimeSeriesRegionScientific,
                       time_series_framework.TimeSeriesRegionFramework, TimeSeries):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeriesRegion dataType.
    
    ::
        
                         TimeSeriesRegionData
                                  |
                                 / \\
        TimeSeriesRegionFramework   TimeSeriesRegionScientific
                                 \ /
                                  |
                           TimeSeriesRegion
        
    
    """
    pass


class TimeSeriesSurface(time_series_scientific.TimeSeriesSurfaceScientific,
                        time_series_framework.TimeSeriesSurfaceFramework, TimeSeries):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeriesSurface dataType.
    
    ::
        
                         TimeSeriesSurfaceData
                                   |
                                  / \\
        TimeSeriesSurfaceFramework   TimeSeriesSurfaceScientific
                                  \ /
                                   |
                            TimeSeriesSurface
        
    
    """
    pass


class TimeSeriesVolume(time_series_scientific.TimeSeriesVolumeScientific,
                       time_series_framework.TimeSeriesVolumeFramework, TimeSeries):
    """
    This class brings together the scientific and framework methods that are
    associated with the TimeSeriesVolume dataType.
    
    ::
        
                         TimeSeriesVolumeData
                                  |
                                 / \\
        TimeSeriesVolumeFramework   TimeSeriesVolumeScientific
                                 \ /
                                  |
                           TimeSeriesVolume
        
    
    """
    pass



if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default TimeSeries datatypes initialize without error.
    TIME_SERIES = TimeSeries()
    TIME_SERIES_EEG = TimeSeriesEEG()
    TIME_SERIES_MEG = TimeSeriesMEG()
    TIME_SERIES_REGION = TimeSeriesRegion()
    TIME_SERIES_SURFACE = TimeSeriesSurface()
    TIME_SERIES_VOLUME = TimeSeriesVolume()
    
    LOG.info("Default TimeSeries datatypes initialized without error...")

