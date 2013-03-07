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

Scientific methods for the Pattern datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""
#TODO: Need configure methods for space and time...

import numpy

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.basic.datatypes.patterns_data as patterns_data
import tvb.basic.traits.util as util


#TODO: UGLY, figure out a better way...
class SpatioTemporalCall(object):
    """
    A call method to be added to Spatiotemporal classes
    """
    
    
    def __call__(self, temporal_indices=None, spatial_indices=None):
        """
        The temporal pattern vector, set by the configure_time method, is 
        combined with the spatial pattern vector, set by the configure_space 
        method, to form a spatiotemporal pattern.
        
        Called with a single time index as an argument, the spatial pattern at 
        that point in time is returned. This is the standard usage within a 
        simulation where the current simulation time point is retrieved.
        
        Called without any arguments, by default a big array representing the 
        entire spatiotemporal pattern is returned. While this may be useful for
        visualisation, say of region level spatiotemporal patterns, care should
        be taken as when surfaces are considered the returned array can be
        potentially quite large.
        
        """
        #NOTE: Ugly, should be a better way...
        if ((temporal_indices is not None) and (spatial_indices is None)):
            pattern = (self.spatial_pattern *
                       self.temporal_pattern[0, temporal_indices])
        
        elif ((temporal_indices is None) and (spatial_indices is None)):
            pattern = self.spatial_pattern * self.temporal_pattern
        
        elif ((temporal_indices is not None) and (spatial_indices is not None)):
            pattern = (self.spatial_pattern[spatial_indices, 0] *
                       self.temporal_pattern[0, temporal_indices])
        
        elif ((temporal_indices is None) and (spatial_indices is not None)):
            pattern = (self.spatial_pattern[spatial_indices, 0] *
                       self.temporal_pattern)
        
        else:
            LOG.error("%s: Well, that shouldn't be possible..." % repr(self))
        
        return pattern



class SpatialPatternScientific(patterns_data.SpatialPatternData):
    """ This class exists to add scientific methods to SpatialPatternData. """
    space = None
    _spatial_pattern = None
    __tablename__ = None

    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Type": self.__class__.__name__}
        summary["Spatial equation"] = self.spatial.__class__.__name__ #TODO: SHould probably grab doc from equation, ie the mathematical representation.
        summary["Spatial parameters"] = self.spatial.parameters
        return summary
    
    #--------------------------- spatial_pattern ------------------------------#
    def _get_spatial_pattern(self):
        """
        Return a discrete representation of the spatial pattern.
        """
        return self._spatial_pattern
        
    def _set_spatial_pattern(self, x):
        """ 
        Generate a discrete representation of the spatial pattern.
        
        The argument x represents a distance, or effective distance, for each 
        node in the space.
        
        """
        
        self.spatial.pattern = x
        
        self._spatial_pattern = numpy.sum(self.spatial.pattern,
                                          axis=1)[:, numpy.newaxis]
    
    spatial_pattern = property(fget=_get_spatial_pattern,
                               fset=_set_spatial_pattern)
    #--------------------------------------------------------------------------#


    def configure_space(self, distance):
        """
        Stores the distance vector as an attribute of the spatiotemporal pattern
        and uses it to generate the spatial pattern vector.
        
        Depending on equations used and interpretation distance can be an actual
        physical distance, on a surface,  geodesic distance (along the surface) 
        away for some focal point, or a per node weighting...
        
        """
        util.log_debug_array(LOG, distance, "distance")
        #Set the discrete representation of space.
        self.space = distance
        #
        self.spatial_pattern = self.space


class SpatioTemporalPatternScientific(patterns_data.SpatioTemporalPatternData,
                                      SpatialPatternScientific,
                                      SpatioTemporalCall):
    """
    This class exists to add scientific methods to SpatioTemporalPatternData.
    """
    time = None
    _temporal_pattern = None
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """ Extend the base class's summary dictionary. """
        summary = super(SpatioTemporalPatternScientific, self)._find_summary_info()
        summary["Temporal equation"] = self.temporal.__class__.__name__ #TODO: SHould probably grab doc from equation, ie the mathematical representation.
        summary["Temporal parameters"] = self.temporal.parameters
        return summary


    #--------------------------- temporal_pattern -----------------------------#
    def _get_temporal_pattern(self):
        """
        Return a discrete representation of the temporal pattern.
        """
        return self._temporal_pattern


    def _set_temporal_pattern(self, t):
        """
        Generate a discrete representation of the temporal pattern.

        """

        self.temporal.pattern = t
        self._temporal_pattern = numpy.reshape(self.temporal.pattern, (1, -1))

    temporal_pattern = property(fget=_get_temporal_pattern,
                                fset=_set_temporal_pattern)
    #--------------------------------------------------------------------------#


    def configure_time(self, time):
        """
        Stores the time vector, physical units (ms), as an attribute of the
        spatiotemporal pattern and uses it to generate the temporal pattern
        vector.

        """
        #Set the discrete representation of time.
        self.time = time

        self.temporal_pattern = self.time
    
    
#    def __call__(self, temporal_indices=None, spatial_indices=None):
#        """
#        The temporal pattern vector, set by the configure_time method, is 
#        combined with the spatial pattern vector, set by the configure_space 
#        method, to form a spatiotemporal pattern.
#        
#        Called with a single time index as an argument, the spatial pattern at 
#        that point in time is returned. This is the standard usage within a 
#        simulation where the current simulation time point is retrieved.
#        
#        Called without any arguments, by default a big array representing the 
#        entire spatiotemporal pattern is returned. While this may be useful for
#        visualisation, say of region level spatiotemporal patterns, care should
#        be taken as when surfaces are considered the returned array can be
#        potentially quite large.
#        
#        """
#        #NOTE: Ugly, should be a better way...
#        if ((temporal_indices is not None) and (spatial_indices is None)):
#            pattern = (self.spatial_pattern *
#                       self.temporal_pattern[0, temporal_indices])
#        
#        elif ((temporal_indices is None) and (spatial_indices is None)):
#            pattern = self.spatial_pattern * self.temporal_pattern
#        
#        elif ((temporal_indices is not None) and (spatial_indices is not None)):
#            pattern = (self.spatial_pattern[spatial_indices, 0] *
#                       self.temporal_pattern[0, temporal_indices])
#        
#        elif ((temporal_indices is None) and (spatial_indices is not None)):
#            pattern = (self.spatial_pattern[spatial_indices, 0] *
#                       self.temporal_pattern)
#        
#        else:
#            LOG.error("%s: Well, that shouldn't be possible..." % repr(self))
#        
#        return pattern


class StimuliRegionScientific(patterns_data.StimuliRegionData,
                              SpatioTemporalPatternScientific):
    """ This class exists to add scientific methods to StimuliRegionData. """
    
    @property
    def weight_array(self):
        """
        Wrap weight List into a Numpy array, as it is requested by the simulator.
        """
        return numpy.array(self.weight)[:, numpy.newaxis]
    
    def configure_space(self, region_mapping = None):
        """
        Do necessary preparations in order to use this stimulus. 
        NOTE: this was previously done in simulator configure_stimuli() method.
        It no needs to be used in stimulus viewer also.
        """
        if (region_mapping is not None):
            #TODO: smooth at surface region boundaries
            #import pdb; pdb.set_trace()
            distance = self.weight_array[region_mapping, :]
        else:
            distance = self.weight_array
        super(StimuliRegionScientific, self).configure_space(distance)


class StimuliSurfaceScientific(patterns_data.StimuliSurfaceData,
                                SpatioTemporalPatternScientific):
    """ This class exists to add scientific methods to StimuliSurfaceData. """

    def configure_space(self, region_mapping = None):
        """
        Do necessary preparations in order to use this stimulus. 
        NOTE: this was previously done in simulator configure_stimuli() method.
        It no needs to be used in stimulus viewer also.
        """
        dis_shp = (self.surface.number_of_vertices, #TODO: When this was in Simulator it was number of nodes, using surface vertices breaks surface simulations which include non-cortical regions.
                   numpy.size(self.focal_points_surface))
        distance = numpy.zeros(dis_shp)
        k = -1
        for focal_point in self.focal_points_surface:
            k += 1
            foci = numpy.array([focal_point], dtype=numpy.int32)
            distance[:, k] = self.surface.geodesic_distance(foci)
        super(StimuliSurfaceScientific, self).configure_space(distance)


class SpatialPatternVolumeScientific(patterns_data.SpatialPatternVolumeData,
                                     SpatialPatternScientific):
    """
    This class exists to add scientific methods to SpatialPatternVolumeData.
    """
    pass


#class ParameterVariationRegionScientific(
#    patterns_data.ParameterVariationRegionData,
#    SpatialPatternRegionScientific):
#    """
#    This class exists to add scientific methods to ParameterVariationRegionData.
#    """
#
#
#    def __call__(self, parameter_value=1.0): #distance,
#        """
#        Override the __call__ in SpatiotemporalPatterns to, for the time being,
#        restrict paramter variations to being spatial.
#
#        """
#
#        spatialised_parameter = parameter_value * (1.0 + self.spatial_pattern)
#
#        return spatialised_parameter


#class ParameterVariationSurfaceScientific(
#    patterns_data.ParameterVariationSurfaceData,
#    SpatialPatternSurfaceScientific):
#    """
#    This class exists to add scientific methods to ParameterVariationSurfaceData.
#    """
#
#
#    def __call__(self, parameter_value=1.0): #distance,
#        """
#        Override the __call__ in SpatiotemporalPatterns to, for the time being,
#        restrict paramter variations to being spatial.
#
#        """
#
#        spatialised_parameter = parameter_value * (1.0 + self.spatial_pattern)
#
#        return spatialised_parameter