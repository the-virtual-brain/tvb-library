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
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
The Data component of Connectivity datatype.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""

import numpy
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.core as core
import tvb.basic.traits.data_readers as readers
import tvb.datatypes.volumes as volumes
import tvb.datatypes.arrays as arrays
from tvb.basic.traits.types_mapped import MappedType


class ConnectivityData(MappedType):
    """
    This class primarily exists to bundle the long range structural connectivity
    data into a single object. 
    """

#    default = readers.File(folder_path="connectivity/o52r00_irp2008")
#    parcellation_mask =0
#    region_labels=0
#    weights=0
#    unidirectional = 0
#    tract_lengths = 0
#    speed = 0
#    centres = 0
#    cortical = 0
#    hemispheres = 0
#    orientations = 0
#    areas = 0
#    idelays = 0
#    delays = 0
#    number_of_regions = 0
#    nose_correction = 0
#    parent_connectivity=0
#    saved_selection=0
#
#    def __init__(self, folder_path="connectivity/o52r00_irp2008"):
#            
#        self.__class__.default = readers.File(folder_path)
#
#
#        self.__class__.parcellation_mask = volumes.ParcellationMask(
#            label="Parcellation mask (volume)",
#            required=False,
#            doc="""A 3D volume mask defining the parcellation of the brain into distinct regions.""")
#    
#        self.__class__.region_labels = arrays.StringArray(
#            label="Region labels",
#            console_default=self.__class__.default.read_data(file_name="centres.txt.bz2", usecols=(0,),
#                                              dtype="string", field="region_labels"),
#            doc="""Short strings, 'labels', for the regions represented by the connectivity matrix.""")
#    
#        self.__class__.weights = arrays.FloatArray(
#            label="Connection strengths",
#            console_default=self.__class__.default.read_data(file_name="weights.txt.bz2", field="weights"),
#            doc="""Matrix of values representing the strength of connections between regions, arbitrary units.""")
#    
#        self.__class__.unidirectional = basic.Integer(
#            default=0, required=False,
#            doc="1, when the weights matrix is square and symmetric over the main diagonal, 0 when bi-directional matrix.")
#    
#        self.__class__.tract_lengths = arrays.FloatArray(
#            label="Tract lengths",
#            console_default=self.__class__.default.read_data(file_name="tract_lengths.txt.bz2", field="tract_lengths"),
#            doc="""The length of myelinated fibre tracts between regions.
#            If not provided Euclidean distance between region centres is used.""")
#    
#        self.__class__.speed = arrays.FloatArray(
#            label="Conduction speed",
#            default=numpy.array([3.0]), file_storage=core.FILE_STORAGE_NONE,
#            doc="""A single number or matrix of conduction speeds for the myelinated fibre tracts between regions.""")
#    
#        self.__class__.centres = arrays.PositionArray(
#            label="Region centres",
#            console_default=self.__class__.default.read_data(file_name="centres.txt.bz2", usecols=(1, 2, 3), field="centres"),
#            doc="An array specifying the location of the centre of each region.")
#    
#        self.__class__.cortical = arrays.BoolArray(
#            label="Cortical",
#            console_default=self.__class__.default.read_data(file_name="cortical.txt.bz2", dtype=numpy.bool, field="cortical"),
#            required=False,
#            doc="""A boolean vector specifying whether or not a region is part of the cortex.""")
#    
#        self.__class__.hemispheres = arrays.BoolArray(
#            label="Hemispheres (True for Right and False for Left Hemisphere",
#            required=False,
#            doc="""A boolean vector specifying whether or not a region is part of the right hemisphere""")
#    
#        self.__class__.orientations = arrays.OrientationArray(
#            label="Average region orientation",
#            console_default=self.__class__.default.read_data(file_name="average_orientations.txt.bz2", field="orientations"),
#            required=False,
#            doc="""Unit vectors of the average orientation of the regions represented in the connectivity matrix.
#            NOTE: Unknown data should be zeros.""")
#    
#        self.__class__.areas = arrays.FloatArray(
#            label="Area of regions",
#            console_default=self.__class__.default.read_data(file_name="areas.txt.bz2", field="areas"),
#            required=False,
#            doc="""Estimated area represented by the regions in the connectivity matrix.
#            NOTE: Unknown data should be zeros.""")
#    
#        self.__class__.idelays = arrays.IndexArray(
#            label="Conduction delay indices",
#            required=False, file_storage=core.FILE_STORAGE_NONE,
#            doc="An array of time delays between regions in integration steps.")
#    
#        self.__class__.delays = arrays.FloatArray(
#            label="Conduction delay",
#            file_storage=core.FILE_STORAGE_NONE, required=False,
#            doc="""Matrix of time delays between regions in physical units, setting conduction speed automatically
#            combines with tract lengths to update this matrix, i.e. don't try and change it manually.""")
#    
#        self.__class__.number_of_regions = basic.Integer(
#            label="Number of regions",
#            doc="""The number of regions represented in this Connectivity """)
#    
#        # ------------- FRAMEWORK ATTRIBUTES -----------------------------
#    
#        # Rotation if positions are not normalized.
#        self.__class__.nose_correction = basic.JSONType(required=False)
#    
#        # Original Connectivity, from which current connectivity was edited.
#        self.__class__.parent_connectivity = basic.String(required=False)
#    
#        # In case of edited Connectivity, this are the nodes left in interest area,
#        # the rest were part of a lesion, so they were removed.
#        self.__class__.saved_selection = basic.JSONType(required=False)

    default = readers.File(folder_path="connectivity/o52r00_irp2008")


    parcellation_mask = volumes.ParcellationMask(
        label="Parcellation mask (volume)",
        required=False,
        doc="""A 3D volume mask defining the parcellation of the brain into distinct regions.""")

    region_labels = arrays.StringArray(
        label="Region labels",
        console_default=default.read_data(file_name="centres.txt.bz2", usecols=(0,),
                                          dtype="string", field="region_labels"),
        doc="""Short strings, 'labels', for the regions represented by the connectivity matrix.""")

    weights = arrays.FloatArray(
        label="Connection strengths",
        console_default=default.read_data(file_name="weights.txt.bz2", field="weights"),
        doc="""Matrix of values representing the strength of connections between regions, arbitrary units.""")

    unidirectional = basic.Integer(
        default=0, required=False,
        doc="1, when the weights matrix is square and symmetric over the main diagonal, 0 when bi-directional matrix.")

    tract_lengths = arrays.FloatArray(
        label="Tract lengths",
        console_default=default.read_data(file_name="tract_lengths.txt.bz2", field="tract_lengths"),
        doc="""The length of myelinated fibre tracts between regions.
        If not provided Euclidean distance between region centres is used.""")

    speed = arrays.FloatArray(
        label="Conduction speed",
        default=numpy.array([3.0]), file_storage=core.FILE_STORAGE_NONE,
        doc="""A single number or matrix of conduction speeds for the myelinated fibre tracts between regions.""")

    centres = arrays.PositionArray(
        label="Region centres",
        console_default=default.read_data(file_name="centres.txt.bz2", usecols=(1, 2, 3), field="centres"),
        doc="An array specifying the location of the centre of each region.")

    cortical = arrays.BoolArray(
        label="Cortical",
        console_default=default.read_data(file_name="cortical.txt.bz2", dtype=numpy.bool, field="cortical"),
        required=False,
        doc="""A boolean vector specifying whether or not a region is part of the cortex.""")

    hemispheres = arrays.BoolArray(
        label="Hemispheres (True for Right and False for Left Hemisphere",
        required=False,
        doc="""A boolean vector specifying whether or not a region is part of the right hemisphere""")

    orientations = arrays.OrientationArray(
        label="Average region orientation",
        console_default=default.read_data(file_name="average_orientations.txt.bz2", field="orientations"),
        required=False,
        doc="""Unit vectors of the average orientation of the regions represented in the connectivity matrix.
        NOTE: Unknown data should be zeros.""")

    areas = arrays.FloatArray(
        label="Area of regions",
        console_default=default.read_data(file_name="areas.txt.bz2", field="areas"),
        required=False,
        doc="""Estimated area represented by the regions in the connectivity matrix.
        NOTE: Unknown data should be zeros.""")

    idelays = arrays.IndexArray(
        label="Conduction delay indices",
        required=False, file_storage=core.FILE_STORAGE_NONE,
        doc="An array of time delays between regions in integration steps.")

    delays = arrays.FloatArray(
        label="Conduction delay",
        file_storage=core.FILE_STORAGE_NONE, required=False,
        doc="""Matrix of time delays between regions in physical units, setting conduction speed automatically
        combines with tract lengths to update this matrix, i.e. don't try and change it manually.""")

    number_of_regions = basic.Integer(
        label="Number of regions",
        doc="""The number of regions represented in this Connectivity """)

    # ------------- FRAMEWORK ATTRIBUTES -----------------------------

    # Rotation if positions are not normalized.
    nose_correction = basic.JSONType(required=False)

    # Original Connectivity, from which current connectivity was edited.
    parent_connectivity = basic.String(required=False)

    # In case of edited Connectivity, this are the nodes left in interest area,
    # the rest were part of a lesion, so they were removed.
    saved_selection = basic.JSONType(required=False)

def new_connectivity(filename):
    class ConnectivityData(MappedType):
        """
        This class primarily exists to bundle the long range structural connectivity
        data into a single object. 
        """


        default = readers.File(folder_path=filename)


        parcellation_mask = volumes.ParcellationMask(
            label="Parcellation mask (volume)",
            required=False,
            doc="""A 3D volume mask defining the parcellation of the brain into distinct regions.""")

        region_labels = arrays.StringArray(
            label="Region labels",
            console_default=default.read_data(file_name="centres.txt.bz2", usecols=(0,),
                                              dtype="string", field="region_labels"),
            doc="""Short strings, 'labels', for the regions represented by the connectivity matrix.""")

        weights = arrays.FloatArray(
            label="Connection strengths",
            console_default=default.read_data(file_name="weights.txt.bz2", field="weights"),
            doc="""Matrix of values representing the strength of connections between regions, arbitrary units.""")

        unidirectional = basic.Integer(
            default=0, required=False,
            doc="1, when the weights matrix is square and symmetric over the main diagonal, 0 when bi-directional matrix.")

        tract_lengths = arrays.FloatArray(
            label="Tract lengths",
            console_default=default.read_data(file_name="tract_lengths.txt.bz2", field="tract_lengths"),
            doc="""The length of myelinated fibre tracts between regions.
            If not provided Euclidean distance between region centres is used.""")

        speed = arrays.FloatArray(
            label="Conduction speed",
            default=numpy.array([3.0]), file_storage=core.FILE_STORAGE_NONE,
            doc="""A single number or matrix of conduction speeds for the myelinated fibre tracts between regions.""")

        centres = arrays.PositionArray(
            label="Region centres",
            console_default=default.read_data(file_name="centres.txt.bz2", usecols=(1, 2, 3), field="centres"),
            doc="An array specifying the location of the centre of each region.")

        cortical = arrays.BoolArray(
            label="Cortical",
            console_default=default.read_data(file_name="cortical.txt.bz2", dtype=numpy.bool, field="cortical"),
            required=False,
            doc="""A boolean vector specifying whether or not a region is part of the cortex.""")

        hemispheres = arrays.BoolArray(
            label="Hemispheres (True for Right and False for Left Hemisphere",
            required=False,
            doc="""A boolean vector specifying whether or not a region is part of the right hemisphere""")

        orientations = arrays.OrientationArray(
            label="Average region orientation",
            console_default=default.read_data(file_name="average_orientations.txt.bz2", field="orientations"),
            required=False,
            doc="""Unit vectors of the average orientation of the regions represented in the connectivity matrix.
            NOTE: Unknown data should be zeros.""")

        areas = arrays.FloatArray(
            label="Area of regions",
            console_default=default.read_data(file_name="areas.txt.bz2", field="areas"),
            required=False,
            doc="""Estimated area represented by the regions in the connectivity matrix.
            NOTE: Unknown data should be zeros.""")

        idelays = arrays.IndexArray(
            label="Conduction delay indices",
            required=False, file_storage=core.FILE_STORAGE_NONE,
            doc="An array of time delays between regions in integration steps.")

        delays = arrays.FloatArray(
            label="Conduction delay",
            file_storage=core.FILE_STORAGE_NONE, required=False,
            doc="""Matrix of time delays between regions in physical units, setting conduction speed automatically
            combines with tract lengths to update this matrix, i.e. don't try and change it manually.""")

        number_of_regions = basic.Integer(
            label="Number of regions",
            doc="""The number of regions represented in this Connectivity """)

        # ------------- FRAMEWORK ATTRIBUTES -----------------------------

        # Rotation if positions are not normalized.
        nose_correction = basic.JSONType(required=False)

        # Original Connectivity, from which current connectivity was edited.
        parent_connectivity = basic.String(required=False)

        # In case of edited Connectivity, this are the nodes left in interest area,
        # the rest were part of a lesion, so they were removed.
        saved_selection = basic.JSONType(required=False)




    class ConnectivityScientific(ConnectivityData):
        """
        This class primarily exists to add scientific methods to the 
        ConnectivityData class.
        
        """
        __tablename__ = None
        
        
        
        def configure(self):
            """
            Invoke the compute methods for computable attributes that haven't been
            set during initialization.
            """
            super(ConnectivityScientific, self).configure()
            
            self.number_of_regions = self.weights.shape[0]
            
            self.trait["weights"].log_debug(owner=self.__class__.__name__)
            self.trait["tract_lengths"].log_debug(owner=self.__class__.__name__)
            self.trait["speed"].log_debug(owner=self.__class__.__name__)
            self.trait["centres"].log_debug(owner=self.__class__.__name__)
            self.trait["orientations"].log_debug(owner=self.__class__.__name__)
            self.trait["areas"].log_debug(owner=self.__class__.__name__)
            
            if self.tract_lengths.size == 0:
                self.compute_tract_lengths()
            
            if self.region_labels.size == 0:
                self.compute_region_labels()
                
            if self.hemispheres is None or self.hemispheres.size == 0:
                self.try_compute_hemispheres()
            
            #This can not go into compute, as it is too complex reference
            #if self.delays.size == 0:
            #TODO: Because delays are stored and loaded the size was never 0.0 and
            #      so this wasn't being run, making the conduction_speed hack on the
            #      simulator non-functional. Inn the longer run it'll probably be
            #      necessary for delays to never be stored but always calculated 
            #      from tract-lengths and speed...
            if self.speed is None: #TODO: this is a hack fix...
                LOG.warning("Connectivity.speed attribute not initialized properly, setting it to 3.0...")
                self.speed = numpy.array([3.0]) #F£$%^&*!!!#self.trait["speed"].value
            
            #NOTE: Because of the conduction_speed hack for UI this must be evaluated here, even if delays 
            #already has a value, otherwise setting speed in the UI has no effect...
            self.delays = self.tract_lengths / self.speed
            self.trait["delays"].log_debug(owner=self.__class__.__name__)
            
            if (self.weights.transpose() == self.weights).all():
                self.unidirectional = 1 
        
        
        def _find_summary_info(self):
            """
            Gather scientifically interesting summary information from an instance
            of this dataType.
            """
            summary = {"Number of regions": self.number_of_regions}
            summary.update(self.get_info_about_array('areas',
                                                     [self.METADATA_ARRAY_MAX,
                                                      self.METADATA_ARRAY_MIN, 
                                                      self.METADATA_ARRAY_MEAN]))
            summary.update(self.get_info_about_array('weights',
                                                     [self.METADATA_ARRAY_MAX,
                                                      self.METADATA_ARRAY_MIN, 
                                                      self.METADATA_ARRAY_MEAN,
                                                      self.METADATA_ARRAY_VAR]))
            summary.update(self.get_info_about_array('tract_lengths',
                                                     [self.METADATA_ARRAY_MAX,
                                                      self.METADATA_ARRAY_MIN, #TODO: Here, the min of only non-zero elements would be more informative.
                                                      self.METADATA_ARRAY_MEAN,
                                                      self.METADATA_ARRAY_VAR]))
            return summary
        
        
        def set_idelays(self, dt):
            """
            Convert the time delays between regions in physical units into an array
            of linear indices into the simulator's history attribute.   
            
            args:
                ``dt (float64)``: Length of integration time step...
            
            Updates attribute:
                ``idelays (numpy.array)``: Transmission delay between brain regions
                in integration steps.
            """
            # Express delays in integration steps
            self.idelays = numpy.rint(self.delays / dt).astype(numpy.int32)
            self.trait["idelays"].log_debug(owner=self.__class__.__name__)
        
        
        def compute_tract_lengths(self):
            """
            If no tract lengths data are available, this can be used to calculate
            the Euclidean distance between region centres to use as a proxy.
            
            """
            nor = self.number_of_regions
            tract_lengths = numpy.zeros((nor, nor))
            #TODO: redundant by half, do half triangle then flip...
            for region in range(nor):
                temp = self.centres - self.centres[region, :][numpy.newaxis, :]
                tract_lengths[region, :] = numpy.sqrt(numpy.sum(temp**2, axis=1))
            
            self.tract_lengths = tract_lengths
            self.trait["tract_lengths"].log_debug(owner=self.__class__.__name__)
        
        
        def compute_region_labels(self):
            """ """
            labels = ["region_%03d" % n for n in range(self.number_of_regions)]
            self.region_labels = numpy.array(labels, dtype = "128a")
        
        def try_compute_hemispheres(self):
            """
            If all region labels are prefixed with L or R, then compute hemisphere side with that.
            """
            if self.region_labels is not None and self.region_labels.size > 0:
                hemispheres = []
                ## Check if all labels are prefixed with R / L
                for label in self.region_labels:
                    if label is not None and label.lower().startswith('r'):
                        hemispheres.append(True)
                    elif label is not None and label.lower().startswith('l'):
                        hemispheres.append(False)
                    else:
                        hemispheres = None
                        break
                ## Check if all labels are sufixed with R / L
                if hemispheres is None:
                    hemispheres = []
                    for label in self.region_labels:
                        if label is not None and label.lower().endswith('r'):
                            hemispheres.append(True)
                        elif label is not None and label.lower().endswith('l'):
                            hemispheres.append(False)
                        else:
                            hemispheres = None
                            break
                if hemispheres is not None:
                    self.hemispheres = numpy.array(hemispheres, dtype=numpy.bool)
         
         
        def normalised_weights(self, mode='tract'):
            """
            Normalise the connection strengths (weights) and return normalized matrix. 
            Three simple types of normalisation are supported. 
            The ``normalisation_mode`` of normalisation is one of the following:
                
                'tract': Normalise such that the maximum abssolute value of a single
                    connection is 1.0.
                
                'region': Normalise such that the maximum abssolute value of the
                    cumulative input to any region is 1.0.
                
                None: does nothing.
                
            NOTE: Currently multiple 'tract' and/or 'region' normalisations without
                intermediate 'none' normalisations destroy the ability to recover
                the original un-normalised weights matrix.
            
            """
            #NOTE: It is not yet clear how or if we will integrate this functinality
            #      into the UI. Currently the same effect can be achieved manually
            #      by using the coupling functions, it is just that, in certain
            #      situations, things are simplified by starting from a normalised
            #      weights matrix. However, in other situations it is not desirable
            #      to have a simple normalisation of this sort.
            
            LOG.info("Starting to normalize to mode: %s" % str(mode))
            
            normalisation_factor = None
            if mode in ("tract", "edge"):
                normalisation_factor = numpy.abs(self.weights).max()
            elif mode in ("region", "node"):
                normalisation_factor = numpy.max(numpy.abs(self.weights.sum(axis=1)))
            elif mode in (None, "none"):
                normalisation_factor = 1.0
            else:
                LOG.error("Bad weights normalisation mode, must be one of:")
                LOG.error("('tract', 'edge', 'region', 'node', 'none')")
                raise Exception("Bad weights normalisation mode")
                
            LOG.debug("Normalization factor is: %s" % str(normalisation_factor))
            mask = self.weights != 0.0
            result = copy(self.weights)
            result[mask] = self.weights[mask] / normalisation_factor
            return result

        def compute_adjacency_matrix(self):
            """
            Transforms the weights matrix into the binary (adjaceny) matrix 
            """
            LOG.info("Transforming weighted matrix into binary matrix")
            
            result = copy(self.weights)
            result = numpy.where(results > 0, 1, result)
            
            
        def switch_distribution(self, matrix='tract_lengths', mode='none'):
            """
            Permutation and resampling methods for the weights and distance 
            (tract_lengths) matrices.
            'normal'    : leaves the matrix unchanged
            'shuffle'   : randomize the elements of the 'matrix' matrix. Fisher-Yates 
                          algorithm.
                          
                          for i from n - 1 downto 1 do
                              j <- random integer with 0 :math:`\leq` j :math:`\leq` i
                              exchange a[j] and a[i]
                        
            'mean'      : sets all the values to the sample mean value. 
            'empirical' : uses the gaussian_kde to estimate the underlying pdf of the 
                          values and randomly samples a new matrix. 
            
            'analytical': defined pdf. Fits the data to the distribution to get the 
                          corresponding parameters and then randomly samples a new 
                          matrix. 
            """
            # Empirical seems to fail on some scipy installations. Error is not pinned down
            # so far, it seems to only happen on some machines. Most relevant related to this:
            #
            # http://projects.scipy.org/scipy/ticket/1735
            # http://comments.gmane.org/gmane.comp.python.scientific.devel/14816
            # http://permalink.gmane.org/gmane.comp.python.numeric.general/42082
            D = eval("self." + matrix)
            
            msg = "The distribution of the %s matrix will be changed" % matrix
            LOG.info(msg)
            
            if mode == 'none':
                LOG.info("Maybe not ... Doing nothing")
                
            elif mode == 'shuffle':
                for i in reversed(xrange(1, D.shape[0])):
                    j = int(numpy.random.rand() * (i + 1))
                    D[:, i], D[:, j] = D[:, j].copy(), D[:, i].copy()
                    D[i, :], D[j, :] = D[j, :].copy(), D[i, :].copy()

            elif mode == 'mean':
                D = D.mean()
                
            elif mode == 'empirical':
                # NOTE: the seed should be fixed to get reproducible results if 
                # we run the same simulation
                
                from scipy import stats
                kernel = stats.gaussian_kde(D.flatten())
                D = kernel.resample(size=(D.shape))
                
                if numpy.any(D < 0) :
                    # NOTE: The KDE method is not perfect, there are still very 
                    #       small probabilities for negative values around 0.
                    # TODO: change the kde bandwidth method 
                    LOG.warning("Found negative values. Setting them to 0.0")
                    D = numpy.where(D < 0.0, 0.0, D)
                    
                # NOTE: if we need the cdf: kernel.integrate_box_1d(lo, hi)
                # TODO: make a subclass using rv_continous, might be more accurate
                            
            elif mode == 'analytical': 
                LOG.warning("Analytical mode has not been implemented yet.")
                #NOTE: pdf name could be an argument.
                
            
            
            

    return ConnectivityScientific