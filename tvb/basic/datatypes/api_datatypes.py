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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

Define what DataType classes are to be included in the Online-Help documentation.
Python doc from the classes listed bellow will be included.

"""

from tvb.basic.datatypes.volumes_data import VolumeData
from tvb.basic.datatypes.arrays_data import MappedArrayData
from tvb.basic.datatypes.connectivity_data import ConnectivityData
from tvb.basic.datatypes.graph_data import ConnectivityMeasureData, CovarianceData
from tvb.basic.datatypes.mapped_values import DatatypeMeasure, ValueWrapper
from tvb.basic.datatypes.mode_decompositions_data import IndependentComponentsData, PrincipalComponentsData
from tvb.basic.datatypes.patterns_data import StimuliRegionData, StimuliSurfaceData
from tvb.basic.datatypes.projections_data import ProjectionRegionEEGData, ProjectionSurfaceEEGData
from tvb.basic.datatypes.simulation_state import SimulationState
from tvb.basic.datatypes.temporal_correlations_data import CrossCorrelationData
import tvb.basic.datatypes.sensors_data as sensors
import tvb.basic.datatypes.spectral_data as spectral
import tvb.basic.datatypes.surfaces_data as surfaces 
import tvb.basic.datatypes.time_series_data as timeseries
import tvb.basic.datatypes.lookup_tables as lookup_tables
    

### Dictionary {DataType Class : Title to appear in final documentation}
### We need to define this dictionary, because not all DataTypea are ready to be exposed in documentation.

DATATYPES_FOR_DOCUMENTATION = {
                               ## Category 2: Raw Entities - GREEN colored
                               ConnectivityData: "Connectivity", 
                               VolumeData: "Volume",
                               surfaces.BrainSkullData: "Brain Skull", 
                               surfaces.CortexData: "Cortex",
                               surfaces.CorticalSurfaceData: "Cortical Surface", 
                               surfaces.SurfaceData: "Surface",
                               surfaces.SkinAirData: "Skin Air", 
                               surfaces.SkullSkinData: "Skull Skin", 
                               
                               ## Category 3: Adjacent Entities (Raw or pre-computed by Creators) - YELLOW color
                               sensors.SensorsEEGData: "Sensors EEG", 
                               sensors.SensorsMEGData: "Sensors MEG",
                               sensors.SensorsInternalData: "Sensors Internal", 
                               StimuliRegionData: "Stimuli Region", 
                               StimuliSurfaceData: "Stimuli Surface",
                               ProjectionRegionEEGData: "Projection Region to EEG", 
                               ProjectionSurfaceEEGData: "Projection Surface to EEG",
                               surfaces.LocalConnectivityData: "Local Connectivity", 
                               surfaces.RegionMappingData: "Region Mapping",
                               lookup_tables.PsiTable: "Psi Lookup Table",
                               lookup_tables.NerfTable: "Nerf Lookup Table",
                               SimulationState: "Simulation State",
                               
                               ## Category 1: Array-like entities (mainly computed by Simulator) - RED color
                               timeseries.TimeSeriesData: "Time Series", 
                               timeseries.TimeSeriesEEGData: "Time Series EEG", 
                               timeseries.TimeSeriesMEGData: "Time Series MEG", 
                               timeseries.TimeSeriesRegionData: "Time Series Region", 
                               timeseries.TimeSeriesSurfaceData: "Time Series Surface", 
                               timeseries.TimeSeriesVolumeData: "Time Series Volume",
                               ValueWrapper: "Single Value", 
                               MappedArrayData: "MappedArray", 
                               DatatypeMeasure: "DataType Measure", 
                               ConnectivityMeasureData: "Connectivity Measure",
                               
                               ## Category 4: Analyzers Results - BLUE color
                               CrossCorrelationData: "Cross Correlation", 
                               CovarianceData: "Covariance",
                               spectral.CoherenceSpectrumData: "Coherence Spectrum", 
                               spectral.FourierSpectrumData: "Fourier Spectrum", 
                               spectral.WaveletCoefficientsData: "Wavelet Coefficient",
                               IndependentComponentsData: "Independent Components",
                               PrincipalComponentsData: "Principal Components"
                               }


