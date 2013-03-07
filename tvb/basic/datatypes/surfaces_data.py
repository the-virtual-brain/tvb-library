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

The Data component of Surfaces DataTypes.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""

import numpy
import scipy.sparse as sparse
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.traits.util as util
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.types_mapped as mapped
import tvb.basic.traits.data_readers as readers
import tvb.basic.traits.exceptions as exceptions
import tvb.basic.datatypes.arrays as arrays
import tvb.basic.datatypes.equations as equations
from tvb.basic.datatypes.connectivity import Connectivity

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

OUTER_SKIN = "Skin Air"
OUTER_SKULL = "Skull Skin"
INNER_SKULL = "Brain Skull"
CORTICAL = "Cortical Surface"
EEG_CAP = "EEG Cap"
FACE = "Face"


##--------------------- CLOSE SURFACES Start Here---------------------------------------##

class SurfaceData(MappedType):
    """
    This class primarily exists to bundle the structural Surface data into a 
    single object.
    """

    default = readers.File(path = "surfaces/cortex_reg13")

    vertices = arrays.PositionArray(
        label = "Vertex positions",
        order = -1,
        console_default = default.read_data(name="vertices.txt.bz2"),
        doc = """An array specifying coordinates for the surface vertices.""")

    triangles = arrays.IndexArray(
        label = "Triangles",
        order = -1, 
        target = util.Self.vertices,
        console_default = default.read_data(name="triangles.txt.bz2",
                                            dtype=numpy.int32),
        doc = """Array of indices into the vertices, specifying the triangles
        which define the surface.""")

    vertex_normals = arrays.OrientationArray(
        label = "Vertex normal vectors",
        order = -1,
        console_default = default.read_data(name="vertex_normals.txt.bz2"),
        doc = """An array of unit normal vectors for the surfaces vertices.""")

    triangle_normals = arrays.OrientationArray(
        label = "Triangle normal vectors",
        order = -1,
        doc = """An array of unit normal vectors for the surfaces triangles.""")

    geodesic_distance_matrix = mapped.SparseMatrix(
        label = "Geodesic distance matrix",
        order = -1,
        required = False,
        doc = """A sparse matrix of truncated geodesic distances""") #'CS'

    number_of_vertices = basic.Integer(
        label = "Number of vertices",
        order = -1,
        compute = util.Self.vertices.shape[0],
        doc = """The number of vertices making up this surface.""")

    number_of_triangles = basic.Integer(
        label = "Number of triangles",
        order = -1,
        compute = util.Self.triangles.shape[0],
        doc = """The number of triangles making up this surface.""")

    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##
    zero_based_triangles = basic.Bool(order = -1)

    split_triangles = arrays.IndexArray(order = -1, required = False)
    number_of_split_slices = basic.Integer(order = -1)
    split_triangles_indices = basic.List(order = -1)

    surface_type = basic.String
    __mapper_args__ = {'polymorphic_on': 'surface_type'}


class CorticalSurfaceData(SurfaceData):
    """
    A surface for describing the Brain Cortical area.
    """

    _ui_name = "A cortical surface"
    surface_type = basic.String(default = CORTICAL, order = -1)

    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': CORTICAL}

    default = readers.File(path = "surfaces/cortex_tvb_whitematter")


class SkinAirData(SurfaceData):
    """
    A surface defining the boundary between the skin and the air.
    """

    _ui_name = "Skin"

    default = readers.File(path = "surfaces/outer_skin_4096")

    surface_type = basic.String(default = OUTER_SKIN)

    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##
    __mapper_args__ = {'polymorphic_identity': OUTER_SKIN}
    __generate_table__ = True


class BrainSkullData(SurfaceData):
    """
    A surface defining the boundary between the brain and the skull.
    """

    _ui_name = "Inside of the skull"

    surface_type = basic.String(default = INNER_SKULL)
    default = readers.File(path = "surfaces/inner_skull_4096")

    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': INNER_SKULL}
    
    

class SkullSkinData(SurfaceData):
    """
    A surface defining the boundary between the skull and the skin.
    """

    _ui_name = "Outside of the skull"
    surface_type = basic.String(default = OUTER_SKULL)

    default = readers.File(path = "surfaces/outer_skull_4096")

    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': OUTER_SKULL}


##--------------------- CLOSE SURFACES End Here---------------------------------------##


##--------------------- OPEN SURFACES Start Here---------------------------------------##

class OpenSurfaceData(SurfaceData):
    """
    A base class for all surfaces that are open (eg. CapEEG or Face Surface).
    """
    __tablename__ = None
    

class EEGCapData(OpenSurfaceData):
    """
    A surface defining the EEG Cap.
    """
    _ui_name = "EEG Cap"
    
    surface_type = basic.String(default = EEG_CAP)
    
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity' : EEG_CAP}
    
    
class FaceSurfaceData(OpenSurfaceData):
    """
    A surface defining the face of a human.
    """
    _ui_name = "Face Surface"
    
    surface_type = basic.String(default = FACE)
    
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity' : FACE}


##--------------------- OPEN SURFACES End Here---------------------------------------##

##--------------------- SURFACES ADJIACENT classes start Here---------------------------------------##

class RegionMappingData(arrays.MappedArray):
    """
    An array representing a measure of a Connectivity dataType.
    """
    default = readers.File(path = "surfaces/cortex_reg13")

    #TODO: this is consistent with default Connectivity, but needs reconsidering...
    array_data = arrays.IndexArray(console_default =
                            default.read_data(name="o52r00_irp2008.txt.bz2",
                                              dtype=numpy.int32))

    connectivity = Connectivity

    surface = SurfaceData

    __generate_table__ = True
    ##--------------------- FRAMEWORK ATTRIBUTES -----------------------------##


class LocalConnectivityData(MappedType):
    """
    A sparse matrix for representing the local connectivity within the Cortex.
    """
    _ui_name = "Local connectivity"

    surface = CorticalSurfaceData(label = "Surface", order=1)

    matrix = mapped.SparseMatrix(order = -1)

    equation = equations.FiniteSupportEquation(
        label = "Spatial",
        required = False,
        default = equations.Gaussian,
        order = 2)

    cutoff = basic.Float(
        label = "Cutoff distance (mm)",
        default = 40.0,
        doc = "Distance at which to truncate the evaluation in mm.",
        order = 3)


    def compute(self):
        """
        Compute current Matrix.
        """
        LOG.info("Mapping geodesic distance through the LocalConnectivity.")

        #Start with data being geodesic_distance_matrix, then map it through equation
        self.equation.pattern = self.matrix.data

        #Then replace original data with result...
        self.matrix.data = self.equation.pattern

        #Homogenise spatial discretisation effects across the surface
        nv = self.matrix.shape[0]
        ind = numpy.arange(nv, dtype=int)
        pos_mask = self.matrix.data > 0.0
        neg_mask = self.matrix.data < 0.0
        pos_con = self.matrix.copy()
        neg_con = self.matrix.copy()
        pos_con.data[neg_mask] = 0.0
        neg_con.data[pos_mask] = 0.0
        pos_contrib = pos_con.sum(axis=1)
        pos_contrib = numpy.array(pos_contrib).squeeze()
        neg_contrib = neg_con.sum(axis=1)
        neg_contrib = numpy.array(neg_contrib).squeeze()
        pos_mean = pos_contrib.mean()
        neg_mean = neg_contrib.mean()
        if ((pos_mean != 0.0 and any(pos_contrib == 0.0)) or
            (neg_mean != 0.0 and any(neg_contrib == 0.0))):
            msg = "Cortical mesh is too coarse for requested LocalConnectivity."
            LOG.warning(msg)
            bad_verts = ()
            if pos_mean != 0.0:
                bad_verts = bad_verts + numpy.nonzero(pos_contrib == 0.0)
            if neg_mean != 0.0:
                bad_verts = bad_verts + numpy.nonzero(neg_contrib == 0.0)
            LOG.debug("Problem vertices are: %s" % str(bad_verts))
        pos_hf = numpy.zeros(shape=pos_contrib.shape)
        pos_hf[pos_contrib != 0] = pos_mean / pos_contrib[pos_contrib != 0]
        neg_hf = numpy.zeros(shape=neg_contrib.shape)
        neg_hf[neg_contrib != 0] = neg_mean / neg_contrib[neg_contrib != 0]
        pos_hf_diag = sparse.csc_matrix((pos_hf, (ind, ind)), shape=(nv, nv))
        neg_hf_diag = sparse.csc_matrix((neg_hf, (ind, ind)), shape=(nv, nv))
        homogenious_conn = (pos_hf_diag * pos_con) + (neg_hf_diag * neg_con)

        #Then replace unhomogenised result with the spatially homogenious one...
        if not homogenious_conn.has_sorted_indices:
            homogenious_conn.sort_indices()

        self.matrix = homogenious_conn


    def validate(self, ignore_list = None):
        """
        This method checks if the data stored into this entity is valid, and 
        ready to be stored in DB.
        Method automatically called just before saving entity in DB.
        In case data is not valid an Exception should be thrown.
        :param ignore_list: list of strings representing names of the attributes
                            to not be validated.
        """
        super(LocalConnectivityData, self).validate(ignore_list = ["matrix"])

        # Sparse Matrix is required so we should check if there is any data stored for it
        if self.matrix is None:
            msg = " ".join(("LocalConnectivity can not be stored because it",
                            "has no SparseMatrix attached."))
            raise exceptions.ValidationException(msg)



class CortexData(CorticalSurfaceData):
    """
    Extends the CorticalSurface class to add specific attributes of the cortex,
    such as, local connectivity...
    """
    _ui_complex_datatype = CorticalSurfaceData

    _ui_name = "A cortex..."

    default = readers.File(path = "surfaces/cortex_reg13")

    local_connectivity = LocalConnectivityData(label = "Local Connectivity",
                                               required = False,
                                               doc = """Define the interaction 
                                               between neighboring network nodes. 
                                               This is implicitly integrated in 
                                               the definition of a given surface 
                                               as an excitatory mean coupling of 
                                               directly adjacent neighbors to 
                                               the first state variable of each 
                                               population model (since these 
                                               typically represent the mean-neural 
                                               membrane voltage). 
                                               This coupling is instantaneous 
                                               (no time delays).""")

    region_mapping_data = RegionMappingData(
        label = "region mapping",
        console_default = RegionMappingData(),
        doc = """An index vector of length equal to the number_of_vertices + the
            number of non-cortical regions, with values that index into an
            associated connectivity matrix.""") # 'CS'

    coupling_strength = arrays.FloatArray(
        label = "Local coupling strength", 
        range= basic.Range(lo=0.0, hi=20.0, step=1.0),
        default = numpy.array([1.0]), 
        file_storage = core.FILE_STORAGE_NONE,
        doc = """A factor that rescales local connectivity strengths.""")

    eeg_projection = arrays.FloatArray(
        label = "EEG projection", order = -1,
        console_default = default.read_data(name="projection_outer_skin_4096_eeg_1020_62.mat",
                                            matlab_data_name="ProjectionMatrix"), 
        #NOTE: This is redundant if the EEG monitor isn't used, but it makes life simpler.
        required = False,
        #linked = ?sensors, skull, skin, etc?
        doc = """A 2-D array which projects the neural activity on the cortical
            surface to a set of EEG sensors.""") 
        #  requires linked sensors.SensorsEEG and Skull/Skin/Air

    meg_projection = arrays.FloatArray(
        label = "MEG projection",
        required = False, order = -1,
        #linked = ?sensors, skull, skin, etc?
        doc = """A 2-D array which projects the neural activity on the cortical
            surface to a set of MEG sensors.""") 
        #  requires linked SensorsMEG and Skull/Skin/Air

    internal_projection = arrays.FloatArray(
        label = "Internal projection",
        required = False, order = -1,
        #linked = ?sensors, skull, skin, etc?
        doc = """A 2-D array which projects the neural activity on the 
            cortical surface to a set of embeded sensors.""") 
        #  requires linked SensorsInternal

    __generate_table__ = True

    def populate_cortex(self, cortex_surface, cortex_parameters=None):
        """
        Populate 'self' from a CorticalSurfaceData instance with additional 
        CortexData specific attributes.

        :param cortex_surface:  CorticalSurfaceData instance
        :param cortex_parameters: dictionary key:value, where key is attribute on CortexData 
        """
        for name in cortex_surface.trait:
            try:
                setattr(self, name, getattr(cortex_surface, name))
            except Exception, exc:
                self.logger.exception(exc)
                self.logger.error("Could not set attribute '" + name +"' on Cortex")
        for key, value in cortex_parameters.iteritems():
            setattr(self, key, value)
        return self


    @property
    def region_mapping(self):
        """
        Define shortcut for retrieving RegionMapping map array.
        """
        if self.region_mapping_data is None:
            return None
        return self.region_mapping_data.array_data



