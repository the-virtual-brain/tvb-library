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

The Data component of Spatiotemporal pattern datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""
#TODO: Reconsider the class hierarchy... Seems it could be more efficient.
#NOTE: Definetely we need to change the hierarchy, it's a pain this way...
#      For example, we need a base Stimulus class...

import tvb.basic.traits.types_basic as basic
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.datatypes.arrays as arrays
import tvb.datatypes.surfaces as surfaces
import tvb.datatypes.volumes as volumes
import tvb.datatypes.connectivity as connectivity_module
import tvb.datatypes.equations as equations


class SpatialPatternData(MappedType):
    """
    Equation for space variation.
    """
    #NOTE; includes eqn, params, and pattern (ie descrete rep of eqn on space)
    spatial = equations.FiniteSupportEquation(
        label = "Spatial Equation",
        order = 2)
    
    #NOTE: the specifics depend on region vs surface...
    #space = FloatArray() #+ {numpy.ndarray(shape=(x, 1))} # column vector


class SpatioTemporalPatternData(SpatialPatternData):
    """
    Combine space and time equations.
    """
    temporal = equations.Equation(label = "Temporal Equation", order=3)
    #space must be shape (x, 1); time must be shape (1, t)
    #pattern = self.spatial.pattern * self.temporal.pattern # FloatArray() #{numpy.ndarray(shape=(x, t))}


class StimuliRegionData(SpatioTemporalPatternData):
    """ 
    A class that bundles the temporal profile of the stimulus, together with the 
    list of scaling weights of the regions where it will applied.
    """
    # when applied to a simulation we need to specify which state-variable it
    # applies to, and possibly how (multiplicative|additive)... but maybe this
    # should live with the model???
    connectivity = connectivity_module.Connectivity(label = "Connectivity", order=1)
    
    spatial = equations.Discrete(
        label = "Spatial Equation", 
        default = equations.Discrete,
        fixed_type = True,
        order = -1)
    
    weight = basic.List(label = "scaling", locked = True, order=4) #,
                        #default = numpy.zeros((util.Self.connectivity.number_of_regions, 1))) #?ones?


class StimuliSurfaceData(SpatioTemporalPatternData):
    """
    A spatiotemporal pattern defined in a surface datatype. It includes the list 
    of focal points. 
    """
    # when applied to a simulation we need to specify which state-variable it
    # applies to, and possibly how (multiplicative|additive)... but maybe this
    # should live with the model???
    surface = surfaces.CorticalSurface(label = "Surface", order=1)
    
    focal_points_surface = basic.List(
        label = "Focal points",
        locked = True,
        order = 4)
        
    focal_points_triangles = basic.List(
        label = "Focal points triangles",
        locked = True,
        order = 4)


class SpatialPatternVolumeData(SpatialPatternData):
    """ A spatiotemporal pattern defined in a volume. """
    volume = volumes.Volume(label = "Volume")
    
    focal_points_volume = arrays.IndexArray(
        label = "Focal points",
        #target = util.Self.volume.data
        )


