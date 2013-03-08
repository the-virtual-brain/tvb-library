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
The Data component of TimeSeries DataTypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.traits.types_basic as basic
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.traits.core as core
import tvb.datatypes.arrays as arrays
import tvb.datatypes.sensors as sensors_module
import tvb.datatypes.connectivity as connectivity_module
import tvb.datatypes.surfaces as surfaces
import tvb.datatypes.volumes as volumes


class TimeSeriesData(MappedType):
    """ Base time-series dataType. """
    
    title = basic.String
    
    data = arrays.FloatArray(
        label = "Time-series data",
        file_storage = core.FILE_STORAGE_EXPAND,
        doc = """An array of time-series data, with a shape of [tpts, :],
            where ':' represents 1 or more dimensions""")
    
    nr_dimensions = basic.Integer(
        label = "Number of dimension in timeseries",
        default = 4)
    
    length_1d, length_2d, length_3d, length_4d = [basic.Integer]*4
    
    labels_ordering = basic.List(
        default=["Time", "State Variable", "Space", "Mode"],
        label = "Dimension Names",
        doc = """List of strings representing names of each data dimension""")
    
    labels_dimensions = basic.Dict(
                                   label = "Specific labels for each dimension for the data stored in this timeseries.",
                                   doc = """ A dictionary containing mappings of the form {'dimension_name' : [labels for this dimension] }""")
    ## TODO (for Stuart) : remove TimeLine and make sure the correct Period/start time is returned by different monitors in the simulator
    time = arrays.FloatArray(
        file_storage = core.FILE_STORAGE_EXPAND,
        label = "Time-series time",
        required = False,
        doc = """An array of time values for the time-series, with a shape of
            [tpts,]. This is 'time' as returned by the simulator's monitors.""")
    
    start_time = basic.Float(label="Start Time:")
    
    sample_period = basic.Float(label = "Sample period", default = 1.0)
    
    # Specify the measure unit for sample period (e.g sec, msec, usec, ...)
    sample_period_unit = basic.String(
        label = "Sample Period Measure Unit",
        default = "ms")
    
    sample_rate = basic.Float(
        label = "Sample rate",
        doc = """The sample rate of the timeseries""")



class TimeSeriesEEGData(TimeSeriesData):
    """ A time series associated with a set of EEG sensors. """
    _ui_name = "EEG time-series"
    sensors = sensors_module.SensorsEEG
    labels_ordering = basic.List(default=["Time", "EEG Sensor"])


class TimeSeriesMEGData(TimeSeriesData):
    """ A time series associated with a set of MEG sensors. """
    _ui_name = "MEG time-series"
    sensors = sensors_module.SensorsMEG
    labels_ordering = basic.List(default=["Time", "MEG Sensor"])


class TimeSeriesRegionData(TimeSeriesData):
    """ A time-series associated with the regions of a connectivity. """
    _ui_name = "Region time-series"
    connectivity = connectivity_module.Connectivity
    labels_ordering = basic.List(default=["Time", "State Variable", "Region", "Mode"])


class TimeSeriesSurfaceData(TimeSeriesData):
    """ A time-series associated with a Surface. """
    _ui_name = "Surface time-series"
    surface = surfaces.CorticalSurface
    labels_ordering = basic.List(default=["Time", "State Variable", "Vertex", "Mode"])


class TimeSeriesVolumeData(TimeSeriesData):
    """ A time-series associated with a Volume. """
    _ui_name = "Volume time-series"
    volume = volumes.Volume
    labels_ordering = basic.List(default=["Time", "X", "Y", "Z"])


class PartialTimeSeriesSimulatorData(TimeSeriesData):
    """
    This DataType will be used the a simulation is on PAUSE.
    Currently not really used, it is just a future hook-point.
    """
    _ui_name = "Partial Simulation result"
    connectivity = connectivity_module.Connectivity
    surface = surfaces.CorticalSurface
    region_mapping = surfaces.RegionMapping
    labels_ordering = basic.List(default=["Time", "State Variable", "Space", "Mode"])



