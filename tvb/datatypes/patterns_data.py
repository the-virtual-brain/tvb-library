# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
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
import tvb.datatypes.arrays as arrays
import tvb.datatypes.surfaces as surfaces
import tvb.datatypes.volumes as volumes
import tvb.datatypes.connectivity as connectivity_module
import tvb.datatypes.equations as equations
from tvb.basic.traits.types_mapped import MappedType


class SpatialPatternData(MappedType):
    """
    Equation for space variation.
    """
    #NOTE; includes eqn, parameters, and pattern (i.e. discrete representation of equation on space)
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
        target = volume
        )


