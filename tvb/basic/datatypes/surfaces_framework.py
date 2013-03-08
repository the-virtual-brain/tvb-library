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
Framework methods for the Surface DataTypes.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
"""

import numpy
import tvb.basic.datatypes.surfaces_data as surfaces_data
import tvb.core.adapters.abcdisplayer as abcdisplayer
import tvb.basic.logger.logger as logger
import tvb.basic.traits.exceptions as exceptions
LOG = logger.getLogger(parent_module=__name__)

from tvb.basic.config.settings import TVBSettings as cfg

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
            url_vertices.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_vertices_slice', parameter=param, flatten=True))
            url_triangles.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_triangles_slice', parameter=param, flatten =True))
            url_normals.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_vertex_normals_slice', parameter=param, flatten=True))
            if not include_alphas or region_mapping is None:
                continue
            alphas.append(abcdisplayer.ABCDisplayer.paths2url(region_mapping, "get_alpha_array", flatten=True, 
                                                 parameter="size="+ str(self.number_of_vertices)))
            start_idx = self.SPLIT_MAX_SIZE * i 
            end_idx = self.SPLIT_MAX_SIZE * (i + 1) + self.SPLIT_BUFFER_SIZE
            end_idx = min(end_idx, self.number_of_vertices)
            alphas_indices.append(abcdisplayer.ABCDisplayer.paths2url(region_mapping, "get_alpha_indices_array", 
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
            vertices.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_pick_vertices_slice', parameter=param, flatten=True))
            triangles.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_pick_triangles_slice', parameter=param, flatten =True))
            normals.append(abcdisplayer.ABCDisplayer.paths2url(self, 'get_pick_vertex_normals_slice', parameter=param, flatten=True))
            
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
        :return NumPy array with [[1, 0], [1, 0] ....] of length :param size
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
        :return NumPy array with [[colosest_reg_idx, 0, 0] ....]
        :param start_idx vertex index on the surface
        :param end_idx vertex index on the surface
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
    
    
