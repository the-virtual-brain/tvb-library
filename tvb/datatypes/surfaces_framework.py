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
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (in press)
#
#
"""
Framework methods for the Surface DataTypes.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
"""

import numpy
import tvb.datatypes.surfaces_data as surfaces_data
import tvb.basic.traits.exceptions as exceptions
from tvb.basic.config.settings import TVBSettings as cfg
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



# TODO: This is just a temporary solution placed here to remove dependency from tvb.basic to tvb framework.
# As soon as we implement a better solution to the datatype framework diamond problem this should be removed.
def paths2url(datatype_entity, attribute_name, flatten=False, parameter=None):
    """
    Prepare a File System Path for passing into an URL.
    """
    if parameter is None:
        return cfg.WEB_VISUALIZERS_URL_PREFIX + datatype_entity.gid + '/'+ attribute_name + '/' + str(flatten)
    return (cfg.WEB_VISUALIZERS_URL_PREFIX + datatype_entity.gid + '/' + attribute_name + 
            '/' + str(flatten) + "?" + str(parameter))

##--------------------- CLOSE SURFACES Start Here---------------------------------------##

class SurfaceFramework(surfaces_data.SurfaceData):
    """ 
    This class exists to add framework methods to SurfacesData.
    """
    
    __tablename__ = None
    
    SPLIT_MAX_SIZE = 40000          #### Slices are for vertices [0.....SPLIT_MAX_SIZE + SPLIT_BUFFER_SIZE] 
    SPLIT_BUFFER_SIZE = 15000       #### [SPLIT_MAX_SIZE ..... 2 * SPLIT_BUFFER_SIZE + SPLIT_BUFFER_SIZE]
    
    SPLIT_PICK_MAX_TRIANGLE = 20000     #### Triangles [0, 1, 2], [3, 4, 5], [6, 7, 8].....
                                        #### Vertices -  no of triangles * 3
     
     
    def get_vertices_slice(self, slice_number= 0):
        """
        Read vertices slice, to be used by WebGL visualizer.
        """
        slice_number = int(slice_number)
        start_idx = slice_number * self.SPLIT_MAX_SIZE
        end_idx = (slice_number + 1) * self.SPLIT_MAX_SIZE + self.SPLIT_BUFFER_SIZE
        end_idx = min(end_idx, self.number_of_vertices)
        return self.get_data('vertices', slice(start_idx, end_idx, 1))
    
    
    def get_vertex_normals_slice(self, slice_number= 0):
        """
        Read vertex-normal slice, to be used by WebGL visualizer.
        """
        slice_number = int(slice_number)
        start_idx = slice_number * self.SPLIT_MAX_SIZE
        end_idx = (slice_number + 1) * self.SPLIT_MAX_SIZE + self.SPLIT_BUFFER_SIZE
        end_idx = min(end_idx, self.number_of_vertices)
        return self.get_data('vertex_normals', slice(start_idx, end_idx, 1))
    
    
    def get_triangles_slice(self, slice_number= 0):
        """
        Read split-triangles slice, to be used by WebGL visualizer.
        """
        if self.number_of_split_slices == 1:
            return self.triangles
        slice_number = int(slice_number)
        start_idx = self.split_triangles_indices[slice_number]
        end_idx = self.split_triangles_indices[slice_number + 1]
        return self.get_data('split_triangles', slice(start_idx, end_idx, 1))
    
    
    def get_flatten_triangles(self):
        """
        Return a flatten list of all the triangles to be used for stimulus view.
        """
        all_triangles = self.get_data('triangles')
        return all_triangles.flatten().tolist()
        
    
    def configure(self):
        """
        Before storing Surface in DB, make sure vertices/triangles are split in
        slices that are readable by WebGL.
        WebGL only supports triangle indices in interval [0.... 2^16] 
        """
        super(SurfaceFramework, self).configure()
        
        ### Don't split when size is convenient
        if self.number_of_vertices <= self.SPLIT_MAX_SIZE + self.SPLIT_BUFFER_SIZE:
            self.number_of_split_slices = 1
            return
        
        ### Compute the number of split slices.
        self.number_of_split_slices = self.number_of_vertices // self.SPLIT_MAX_SIZE
        if self.number_of_vertices % self.SPLIT_MAX_SIZE > self.SPLIT_BUFFER_SIZE:
            self.number_of_split_slices = self.number_of_split_slices + 1
        
        ### Do not split again, if split-data is already loaded:
        if (self.split_triangles is not None and self.split_triangles_indices is not None 
            and len(self.split_triangles_indices) == self.number_of_split_slices + 1):
            return
        
        LOG.debug("Start to compute surface split triangles and vertices")
        split_triangles = []
        for i in range(self.number_of_split_slices):
            split_triangles.append([])
        ### Iterate Triangles and find the slice where it fits, based on its vertices    
        for i in range(self.number_of_triangles):
            current_slice = 0
            transformed_triangle = [self.triangles[i][j] for j in range(3)]
            while min(transformed_triangle) > self.SPLIT_MAX_SIZE and current_slice < self.number_of_split_slices - 1:
                transformed_triangle = [transformed_triangle[j] - self.SPLIT_MAX_SIZE for j in range(3)]
                current_slice = current_slice + 1
            
            if max(transformed_triangle) > self.SPLIT_MAX_SIZE + self.SPLIT_BUFFER_SIZE:
                # triangle ignored, as it has vertices over multiple slices.
                continue
            else:
                split_triangles[current_slice].append(transformed_triangle)
         
        final_split_triangles = []
        triangles_split_indices = [0]
        ### Concatenate triangles, to be stored in a single HDF5 array.
        for split_ in split_triangles:
            triangles_split_indices.append(triangles_split_indices[-1] + len(split_))
            final_split_triangles.extend(split_)
        self.split_triangles = numpy.array(final_split_triangles, dtype=numpy.int32)
        self.split_triangles_indices = triangles_split_indices
       
        LOG.debug("End compute surface split triangles and vertices")
       
       
    def get_urls_for_rendering(self, include_alphas=False, region_mapping=None): 
        """
        Compose URLs for the JS code to retrieve a surface from the UI for
        rendering.
        """
        url_vertices = []
        url_triangles = []
        url_normals = []
        alphas = []
        alphas_indices = []
        for i in range(self.number_of_split_slices):
            param = "slice_number=" + str(i)
            url_vertices.append(paths2url(self, 'get_vertices_slice', parameter=param, flatten=True))
            url_triangles.append(paths2url(self, 'get_triangles_slice', parameter=param, flatten =True))
            url_normals.append(paths2url(self, 'get_vertex_normals_slice', parameter=param, flatten=True))
            if not include_alphas or region_mapping is None:
                continue
            alphas.append(paths2url(region_mapping, "get_alpha_array", flatten=True, 
                                                 parameter="size="+ str(self.number_of_vertices)))
            start_idx = self.SPLIT_MAX_SIZE * i 
            end_idx = self.SPLIT_MAX_SIZE * (i + 1) + self.SPLIT_BUFFER_SIZE
            end_idx = min(end_idx, self.number_of_vertices)
            alphas_indices.append(paths2url(region_mapping, "get_alpha_indices_array", 
                                                                      flatten=True, parameter="start_idx="+ 
                                                                      str(start_idx) +";end_idx="+ str(end_idx)))
          
        if include_alphas:  
            return url_vertices, url_normals, url_triangles, alphas, alphas_indices
        return url_vertices, url_normals, url_triangles


    ####################################### Split for Picking
    #######################################
    def get_pick_vertices_slice(self, slice_number= 0):
        """
        Read vertices slice, to be used by WebGL visualizer with pick.
        """
        slice_number = int(slice_number)
        slice_triangles = self.get_data('triangles', slice(slice_number * self.SPLIT_PICK_MAX_TRIANGLE, 
                                                           min(self.number_of_triangles, 
                                                               (slice_number+1) * self.SPLIT_PICK_MAX_TRIANGLE)))
        result_vertices = []
        for triang in slice_triangles:
            result_vertices.append(self.vertices[triang[0]])
            result_vertices.append(self.vertices[triang[1]])
            result_vertices.append(self.vertices[triang[2]])
        return numpy.array(result_vertices)
       
       
    def get_pick_vertex_normals_slice(self, slice_number= 0):
        """
        Read vertex-normals slice, to be used by WebGL visualizer with pick.
        """
        slice_number = int(slice_number)
        slice_triangles = self.get_data('triangles', slice(slice_number * self.SPLIT_PICK_MAX_TRIANGLE, 
                                                           min(self.number_of_triangles, 
                                                               (slice_number+1) * self.SPLIT_PICK_MAX_TRIANGLE)))
        result_normals = []
        for triang in slice_triangles:
            result_normals.append(self.vertex_normals[triang[0]])
            result_normals.append(self.vertex_normals[triang[1]])
            result_normals.append(self.vertex_normals[triang[2]])
        return numpy.array(result_normals) 
         
         
    def get_pick_triangles_slice(self, slice_number= 0):
        """
        Read triangles slice, to be used by WebGL visualizer with pick.
        """
        slice_number = int(slice_number)
        no_of_triangles = (min(self.number_of_triangles, (slice_number+1) * self.SPLIT_PICK_MAX_TRIANGLE) 
                           - slice_number * self.SPLIT_PICK_MAX_TRIANGLE)
        triangles_array = numpy.array(range(0, no_of_triangles * 3)).reshape((no_of_triangles, 3))
        return triangles_array
            
         
    def get_urls_for_pick_rendering(self):
        """
        Compose URLS for the JS code to retrieve a surface for picking.
        """
        vertices = []
        triangles = []
        normals = []
        number_of_split = self.number_of_triangles // self.SPLIT_PICK_MAX_TRIANGLE
        if self.number_of_triangles % self.SPLIT_PICK_MAX_TRIANGLE > 0:
            number_of_split = number_of_split + 1
            
        for i in range(number_of_split):
            param = "slice_number=" + str(i)
            vertices.append(paths2url(self, 'get_pick_vertices_slice', parameter=param, flatten=True))
            triangles.append(paths2url(self, 'get_pick_triangles_slice', parameter=param, flatten =True))
            normals.append(paths2url(self, 'get_pick_vertex_normals_slice', parameter=param, flatten=True))
            
        return vertices, normals, triangles
    
    def center(self):
        """
        Compute the center of the surface as the median spot on all the three axes.
        """
        return [float(numpy.mean(self.vertices[:, 0])), float(numpy.mean(self.vertices[:, 1])), float(numpy.mean(self.vertices[:, 2]))]
        

class CorticalSurfaceFramework(surfaces_data.CorticalSurfaceData, SurfaceFramework):
    """ This class exists to add framework methods to CorticalSurfaceData """
    pass


class SkinAirFramework(surfaces_data.SkinAirData, SurfaceFramework):
    """ This class exists to add framework methods to SkinAirData """
    __tablename__ = None


class BrainSkullFramework(surfaces_data.BrainSkullData, SurfaceFramework):
    """ This class exists to add framework methods to BrainSkullData """
    pass

class SkullSkinFramework(surfaces_data.SkullSkinData, SurfaceFramework):
    """ This class exists to add framework methods to SkullSkinData """
    pass

##--------------------- CLOSE SURFACES End Here---------------------------------------##

##--------------------- OPEN SURFACES Start Here---------------------------------------##

class OpenSurfaceFramework(surfaces_data.OpenSurfaceData, SurfaceFramework):
    """ This class exists to add framework methods to OpenSurfaceData """
    
    def validate(self):
        """
        This method checks if the data stored into this entity is valid, and is ready to be stored in DB.
        Method automatically called just before saving entity in DB.
        In case data is not valid a ValidationException is thrown.
        """
        # Check if the surface has a valid number of vertices (not more than the configured maximum).
        if self.number_of_vertices > cfg.MAX_SURFACE_VERTICES_NUMBER:
            msg = "This surface has too many vertices (max allowed: %d)."%cfg.MAX_SURFACE_VERTICES_NUMBER
            msg += " Please upload a new surface or change max number in application settings."
            raise exceptions.ValidationException(msg)


class EEGCapFramework(surfaces_data.EEGCapData, OpenSurfaceFramework):
    """ This class exists to add framework methods to EEGCapData """
    pass

class FaceSurfaceFramework(surfaces_data.FaceSurfaceData, OpenSurfaceFramework):
    """ This class exists to add framework methods to FaceSurface """
    pass

##--------------------- OPEN SURFACES End Here---------------------------------------##

##--------------------- SURFACES ADJIACENT classes start Here---------------------------------------##

class RegionMappingFramework(surfaces_data.RegionMappingData):
    """ 
    Framework methods regarding RegionMapping DataType.
    """
    __tablename__ = None
    
       
    @staticmethod
    def get_alpha_array(size):
        """
        Compute alpha weights.
        When displaying region-based results, we need to compute color for each
        surface vertex based on a gradient of the neighbor region(s).
        Currently only one vertex is used for determining color (the one 
        indicated by the RegionMapping).
        :return: NumPy array with [[1, 0], [1, 0] ....] of length :param size
        """
        if isinstance(size, (str, unicode)):
            size = int(size)
        return numpy.ones((size, 1)) * numpy.array([1.0, 0.0])
    
    
    def get_alpha_indices_array(self, start_idx, end_idx):
        """
        Compute alpha indices.
        When displaying region-based results, we need to compute color for each
        surface vertex based on a gradient of the neighbor region(s).
        For each vertex on the surface, alpha-indices will be the closest
        region-indices

        :param start_idx: vertex index on the surface
        :param end_idx: vertex index on the surface
        :return: NumPy array with [[colosest_reg_idx, 0, 0] ....]

        """
        if isinstance(start_idx, (str, unicode)):
            start_idx = int(start_idx)
        if isinstance(end_idx, (str, unicode)):
            end_idx = int(end_idx)
        size = end_idx - start_idx
        result = numpy.transpose(self.array_data[start_idx: end_idx]).reshape(size, 1) * numpy.array([1.0, 0.0, 0.0])
        result = result + numpy.ones((size, 1)) * numpy.array([0.0, 1.0, 1.0])
        return result
    
    
    def generate_new_region_mapping(self, connectivity_gid, storage_path):
        """
        Generate a new region mapping with the given connectivity gid from an 
        existing mapping corresponding to the parent connectivity.
        """
        new_region_map = self.__class__()
        new_region_map.storage_path = storage_path
        new_region_map._connectivity = connectivity_gid
        new_region_map._surface = self._surface
        new_region_map.array_data = self.array_data
        new_region_map.default = self.default
        return new_region_map
    
    
class LocalConnectivityFramework(surfaces_data.LocalConnectivityData):
    """ This class exists to add framework methods to LocalConnectivityData """
    __tablename__ = None
    
    
class CortexFramework(surfaces_data.CortexData, CorticalSurfaceFramework):
    """ This class exists to add framework methods to CortexData """
    __tablename__ = None
    
    
