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
The Data component of Spectral datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.datatypes.arrays as arrays
import tvb.datatypes.time_series as time_series
from tvb.basic.traits.types_mapped import MappedType


class PrincipalComponentsData(MappedType):
    """
    Result of a Principal Component Analysis (PCA).
    """
    
    source = time_series.TimeSeries(
        label = "Source time-series",
        doc = "Links to the time-series on which the PCA is applied.")
    
    weights = arrays.FloatArray(
        label = "Principal vectors",
        doc = """The vectors of the 'weights' with which each time-series is
            represented in each component.""",
        file_storage = core.FILE_STORAGE_EXPAND)
    
    fractions = arrays.FloatArray(
        label = "Fraction explained",
        doc = """A vector or collection of vectors representin the fraction of
            the variance explained by each principal component.""",
        file_storage = core.FILE_STORAGE_EXPAND)
    
    norm_source = arrays.FloatArray(
        label = "Normalised source time series",
        file_storage = core.FILE_STORAGE_EXPAND)
    
    component_time_series = arrays.FloatArray(
        label = "Component time series",
        file_storage = core.FILE_STORAGE_EXPAND)
    
    normalised_component_time_series = arrays.FloatArray(
        label = "Normalised component time series",
        file_storage = core.FILE_STORAGE_EXPAND)
    
    __generate_table__ = True


class IndependentComponentsData(MappedType):
    """
    Result of TEMPORAL (Fast) Independent Component Analysis
    """
    
    source = time_series.TimeSeries(
        label = "Source time-series",
        doc = "Links to the time-series on which the ICA is applied.")
    
    mixing_matrix = arrays.FloatArray(
        label = "Mixing matrix - Spatial Maps",
        doc = """The linear mixing matrix (Mixing matrix) """)
            
    unmixing_matrix = arrays.FloatArray(
        label = "Unmixing matrix - Spatial maps",
        doc = """The estimated unmixing matrix used to obtain the unmixed 
            sources from the data""")
    
    prewhitening_matrix = arrays.FloatArray(
        label = "Pre-whitening matrix",
        doc = """ """)
            
    n_components = basic.Integer(
        label = "Number of independent components",
        doc = """ Observed data matrix is considered to be a linear combination 
        of :math:`n` non-Gaussian independent components""")
            
    norm_source = arrays.FloatArray(
        label = "Normalised source time series. Zero centered and whitened.",
        file_storage=core.FILE_STORAGE_EXPAND)
    
    component_time_series = arrays.FloatArray(
        label = "Component time series. Unmixed sources.",
        file_storage=core.FILE_STORAGE_EXPAND)
    
    normalised_component_time_series = arrays.FloatArray(
        label = "Normalised component time series",
        file_storage=core.FILE_STORAGE_EXPAND)
    
    __generate_table__ = True

