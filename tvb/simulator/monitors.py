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
Monitors record significant values from the simulation. In their simplest form
they return all the simulated data, Raw(), directly subsampled data, SubSample()
spatially averaged temporally subsampled, GlobalAverage(), or temporally
averaged subsamples, TemporalAverage(). The more elaborate monitors instantiate
a physically realistic measurement process on the simulation, such as EEG, MEG,
and fMRI (BOLD).

Conversion of power of 2 sample-rates(Hz) to Monitor periods(ms)
::

    4096 Hz => 0.244140625 ms
    2048 Hz => 0.48828125 ms
    1024 Hz => 0.9765625 ms
     512 Hz => 1.953125 ms
     256 Hz => 3.90625 ms
     128 Hz => 7.8125 ms


.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Noelia Montejo <Noelia@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Standard python libraries

# Third party python libraries
import numpy

#The Virtual Brain
from tvb.simulator.common import get_logger
LOG = get_logger(__name__)

import tvb.datatypes.sensors as sensors_module
import tvb.datatypes.arrays as arrays
import tvb.datatypes.projections as projections

import tvb.basic.traits.util as util
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.core as core

from tvb.simulator.common import iround



class Monitor(core.Type):
    """
    Base Monitor class, all Monitors inherit from this class.

    **private attribute:**
        ``_stock``: 
            A kind of internal memory of the monitor, used for when monitors
            are non-instantaneous, such as TemporalAverage or fMRI.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Monitor.__init__
    .. automethod:: Monitor.config_for_sim
    .. automethod:: Monitor.record

    """
    _base_classes = ['Monitor']

    period = basic.Float(
        label = "Sampling period (ms)",
        default = 0.9765625, #ms. 0.9765625 => 1024Hz #ms, 0.5 => 2000Hz
        doc = """Sampling period in milliseconds, must be an integral multiple
        of integration-step size. As a guide: 2048 Hz => 0.48828125 ms ;  
        1024 Hz => 0.9765625 ms ; 512 Hz => 1.953125 ms.""")

    variables_of_interest = arrays.IntegerArray(
        label = "Model variables to watch",
        doc = """This can be used to override, for each Monitor, the default 
        monitored state-variables. NOTE: Any specified indices must be consistent 
        with the Model being monitored. By default, if left unspecified, this will
        be set based on the variables_of_interest attribute on the Model.""",
        order = -1)
    

    def __init__(self,  **kwargs):
        """
        Initialise the place holder attributes that will be filled when the
        Monitor is configured for a given Simulation -- ie, for a specific
        Model, Connectivity, Integrator, etc.

        """
        super(Monitor, self).__init__(**kwargs) 
        LOG.debug(str(kwargs))

        self.istep = None #Monitor period in integration time-steps (integer).
        self.dt = None #Integration time-step in "physical" units.
        self.voi = None

        self._stock = numpy.array([], dtype=numpy.float64)


    def __repr__(self):
        """A formal, executable, representation of a Monitor object."""
        class_name = self.__class__.__name__
        traited_kwargs = self.trait.keys()
        formal = class_name + "(" + "=%s, ".join(traited_kwargs) + "=%s)"
        return formal % eval("(self." + ", self.".join(traited_kwargs) + ")")


    def __str__(self):
        """An informal, 'human readable', representation of a Monitor object."""
        class_name = self.__class__.__name__ 
        traited_kwargs = self.trait.keys()
        informal = class_name + "(" + ", ".join(traited_kwargs) + ")"
        return informal


    def config_for_sim(self, simulator):
        """
        Grab the Simulator's integration step size. Set the monitor's variables
        of interest based on the Monitor's 'variables_of_interest' attribute, if
        it was specified, otherwise use the 'variables_of_interest' specified 
        for the Model. Calculate the number of integration steps (isteps)
        between returns by the record method. This method is called from within
        the the Simulator's configure() method.

        Args:
            ``simulator`` (Simulator): a Simulator object.

        """
        # Simulation time step
        self.dt = simulator.integrator.dt

        # model state-variables to monitor
        if self.variables_of_interest.size == 0:
            self.voi = numpy.array([simulator.model.state_variables.index(var) for var in simulator.model.variables_of_interest])
        else:
            self.voi = self.variables_of_interest

        LOG.info("%s: variables of interest: %s" % (str(self), str(self.voi)))

        # monitor period in integration steps
        #TODO: Enforce period as integral multiple of dt elsewhere and remove 
        #      round from here, it's weird offset prone...
        self.istep = iround(self.period/ self.dt)
        LOG.info("%s: istep of monitor is %d" % (str(self), self.istep))


    def record(self, step, state):
        """
        This is the method where the specific Monitor's recording/monitoring
        function is defined, that is, it defines the return of a subset or
        projection of the state_variables of the Simulator's Model.

        """
        pass



class Raw(Monitor):
    """
    A monitor that records the output raw data from a tvb simulation:
    It collects:

        - all state variables and modes from class :Model:
        - all nodes of a region or surface based 
        - all the integration time steps 

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Raw.__init__
    .. automethod:: Raw.config_for_sim
    .. automethod:: Raw.record

    """
    _ui_name = "Raw recording"

    period = basic.Float(
        label = "Sampling period is ignored for Raw Monitor",
        order = -1)

    variables_of_interest = arrays.IntegerArray(
        label = "Raw Monitor sees all!!! Resistance is futile...",
        order = -1)
    
    def __init__(self, **kwargs):
        """Initialise the Raw monitor from the base Monitor class."""
        LOG.info("%s: initing..." % str(self))
        super(Raw, self).__init__(**kwargs)
        LOG.debug("%s: inited." % repr(self))


    def config_for_sim(self, simulator):
        """
        Initialise the istep to 1, regardless of any ``period`` provided. Also,
        sets the monitor's variables of interest to be all state variables, 
        regardless of any ``variables_of_interest`` provided.

        """
        # Simulation time step
        self.dt = simulator.integrator.dt

        if self.period is not None:
            LOG.warning("%s: Raw monitor ignores period argument." % repr(self))

        self.period = simulator.integrator.dt #Needed for Monitor consistency

        # state-variables to monitor
        self.voi = numpy.arange(simulator.model.nvar)
        LOG.info("%s: variable of interest is %s"%(str(self), str(self.voi)))

        # monitor period in integration steps
        self.istep = 1
        LOG.info("%s: istep of monitor is %d"%(str(self), self.istep))


    def record(self, step, state):
        """
        Records all state-variables, nodes and modes for every step of the
        integration.

        """
        time = step * self.dt
        return [time, state]



class SubSample(Monitor):
    """
    Discretely sub-sample the simulation every `istep` integration steps. Time 
    steps that are not modulo `istep` are completely ignored.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: SubSample.__init__
    .. automethod:: SubSample.config_for_sim
    .. automethod:: SubSample.record

    """
    _ui_name = "Temporally sub-sample"

    def __init__(self, **kwargs):
        """Initialise a SubSample monitor from the base Monitor class."""
        LOG.info("%s: initing..." % str(self))
        super(SubSample, self).__init__(**kwargs)
        LOG.debug("%s: inited." % repr(self))


    def record(self, step, state):
        """Records if integration step corresponds to sampling period."""
        if step % self.istep == 0:
            time = step * self.dt
            return [time, state[self.voi, :]]



class SpatialAverage(Monitor):
    """
    Monitors the averaged value for the models variable of interest over sets of
    nodes -- defined by spatial_mask. This is primarily intended for use with
    surface simulations, with a default behaviour, when no spatial_mask is
    specified, of using surface.region_mapping in order to reduce a surface
    simulation back to a single average timeseries for each region in the
    associated Connectivity. However, any vector of length nodes containing
    integers, from a set contiguous from zero, specifying the new grouping to
    which each node belongs should work.

    Additionally, this monitor temporally sub-samples the simulation every `istep` 
    integration steps.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: SpatialAverage.__init__
    .. automethod:: SpatialAverage.config_for_sim
    .. automethod:: SpatialAverage.record

    """
    _ui_name = "Spatial average" #with temporal sub-sample
    #TODO: Consider modifying to "with temporal-average"
    spatial_mask = arrays.IntegerArray( #TODO: Check it's a vector of length Nodes (like region mapping for surface)
        label = "An index mask of nodes into areas",
        doc = """A vector of length==nodes that assigns an index to each node
            specifying the "region" to which it belongs. The default usage is
            for mapping a surface based simulation back to the regions used in 
            its `Long-range Connectivity.`""")
    
    default_mask = basic.Enumerate(
                              label = "Default Mask",
                              options = ["cortical", "hemispheres"],
                              default = ["cortical"],
                              doc = r"""Fallback in case spatial mask is none and no surface provided 
                              to use either connectivity hemispheres or cortical attributes.""",
                              order = 2)



    def __init__(self, **kwargs):
        """
        Initialise a SpatialAverage monitor from the base Monitor class. Add an
        additional place holder attribute, specific to this Monitor, for the
        array which averages nodes of the simulation to the new set of
        time-series specified by the spatial_mask.

        """
        LOG.info("%s: initing..." % str(self))
        super(SpatialAverage, self).__init__(**kwargs)

        self.spatial_mean = None
        LOG.debug("%s: inited." % repr(self))


    def config_for_sim(self, simulator):
        """
        Sets sampling period, variable/s of interest, and the array used to
        group nodes, by default the surface's region_mapping is used.

        """
        super(SpatialAverage, self).config_for_sim(simulator)

        if self.spatial_mask.size == 0:
            if not (simulator.surface is None):
                self.spatial_mask = simulator.surface.region_mapping
            else:
                conn = simulator.connectivity
                if self.default_mask[0] == 'cortical':
                    if conn is not None and conn.cortical is not None and conn.cortical.size > 0:
                        ## Use as spatial-mask cortical/non cortical areas
                        self.spatial_mask = [int(c) for c in conn.cortical]
                    else:
                        msg = "Must fill Spatial Mask parameter for non-surface simulations when using SpatioTemporal monitor!"
                        LOG.error(msg)
                        raise Exception(msg)
                if self.default_mask[0] == 'hemispheres':
                    if conn is not None and conn.hemispheres is not None and conn.hemispheres.size > 0:
                        ## Use as spatial-mask left/right hemisphere
                        self.spatial_mask = [int(h) for h in conn.hemispheres]
                    else:
                        msg = "Must fill Spatial Mask parameter for non-surface simulations when using SpatioTemporal monitor!"
                        LOG.error(msg)
                        raise Exception(msg)

        number_of_nodes = simulator.number_of_nodes
        LOG.debug("%s: number_of_nodes = %s" % (str(self), number_of_nodes))
        if self.spatial_mask.size != number_of_nodes:
            msg = "spatial_mask must be a vector of length number_of_nodes."
            LOG.error(msg)
            raise Exception(msg)

        areas = numpy.unique(self.spatial_mask)
        number_of_areas = len(areas)
        LOG.debug("%s: number_of_areas = %s" % (str(self), number_of_areas))
        if not numpy.all(areas == numpy.arange(number_of_areas)):
            msg = " ".join(("Areas in the spatial_mask must be specified as a",
                            "contiguous set of indices starting from zero."))
            LOG.error(msg)
            raise Exception(msg)

        util.log_debug_array(LOG, self.spatial_mask, "spatial_mask", owner=self.__class__.__name__)

        spatial_sum = numpy.zeros((number_of_nodes, number_of_areas))
        spatial_sum[numpy.arange(number_of_nodes), self.spatial_mask] = 1

        spatial_sum = spatial_sum.T

        util.log_debug_array(LOG, spatial_sum, "spatial_sum")

        nodes_per_area = numpy.sum(spatial_sum, axis=1)[:, numpy.newaxis]
        self.spatial_mean = spatial_sum / nodes_per_area

        util.log_debug_array(LOG, self.spatial_mean, "spatial_mean", owner=self.__class__.__name__)
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """
        This method records the state of the simulation if the integration step
        corresponds to the sampling period of this Monitor. The nodes of the
        simulation are effectively combined into groups, and then time-series
        representing the average activity within these groups is returned.

        """
        if step % self.istep == 0:
            time = step * self.dt
            monitored_state = numpy.dot(self.spatial_mean, state[self.voi, :])
            return [time, monitored_state.transpose((1, 0, 2))]



class GlobalAverage(Monitor):
    """
    Monitors the averaged value for the model's variables of interest over all
    the nodes at each sampling period. This mainly exists as a "convenience"
    monitor for quickly checking the "global" state of a simulation.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: GlobalAverage.__init__
    .. automethod:: GlobalAverage.config_for_sim
    .. automethod:: GlobalAverage.record

    """
    _ui_name = "Global average"


    def __init__(self, **kwargs):
        """Initialise a GlobalAverage monitor from the base Monitor class."""
        LOG.info("%s: initing..." % str(self))
        super(GlobalAverage, self).__init__(**kwargs)
        LOG.debug("%s: inited." % repr(self))


    def record(self, step, state):
        """Records if integration step corresponds to sampling period."""
        if step % self.istep == 0:
            time = step * self.dt
            data = numpy.mean(state[self.voi, :], axis=1)[:, numpy.newaxis, :]
            return [time, data]



class TemporalAverage(Monitor):
    """
    Monitors the averaged value for the model's variable/s of interest over all
    the nodes at each sampling period. Time steps that are not modulo ``istep``
    are stored temporarily in the ``_stock`` attribute and then that temporary
    store is averaged and returned when time step is modulo ``istep``.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: TemporalAverage.__init__
    .. automethod:: TemporalAverage.config_for_sim
    .. automethod:: TemporalAverage.record

    """
    _ui_name = "Temporal average"


    def __init__(self, **kwargs):
        """Initialise a TemporalAverage monitor from the base Monitor class."""
        LOG.info("%s: initing..." % str(self))
        super(TemporalAverage, self).__init__(**kwargs)
        LOG.debug("%s: inited." % repr(self))


    def config_for_sim(self, simulator):
        """
        Set the monitor's variables of interest based on the model
        specification. Calculates the number of integration steps (isteps)
        between returns by the record method. And initialises the stock array
        over which the temporal averaging will be performed.

        """
        super(TemporalAverage, self).config_for_sim(simulator)

        stock_size = (self.istep, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        self._stock = numpy.zeros(stock_size)


    def record(self, step, state):
        """
        Records if integration step corresponds to sampling period, Otherwise
        just update the monitor's stock. When the step corresponds to the sample
        period, the ``_stock`` is averaged over time for return. 

        """
        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
        if step % self.istep == 0:
            avg_stock = numpy.mean(self._stock, axis=0)
            time = (step - self.istep / 2.0) * self.dt
            return [time, avg_stock]



class EEG(Monitor):
    """
    Monitors the temporally averaged value for the models variable of interest
    projected to sensors on the head surface at each sampling period.

    .. note:: For the moment, this returns idealised (reference free) EEG.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: EEG.__init__
    .. automethod:: EEG.config_for_sim
    .. automethod:: EEG.record

    """
    #_ui_name = "EEG (ONLY FOR reg13 SURFACE + o52r00_irp2008 CORTEX-ONLY CONNECTIVITY (74))"

    #TODO: Currently all monitors return a 3D state [variables of interest, nodes, modes],
    #      resulting in a 4D TimeSeries with time as the zeroth dim, however,
    #      TimeSeriesEEG is really intended to only be 2D [time, channels]. So,
    #      we should be summing over variables of interest and Modes, however,
    #      this will require across the board changes to Analysers their adapters
    #      and some visualisers so that everything works... In other words, this
    #      will need to be done in one big step, otherwise it'll break everthing. 

    #TODO: add reference electrode capability, support single point through to 
    #      grand average -- Should be done offline as an "analyser" or better 
    #      built into the visualiser...

    #TODO: ?Maybe easier from UI perspective to frame this in terms of sources,
    #       head geometry, and sensors...?

    #TODO: Probably going to need to make ProjectionMatrix a datatype and then
    #      use it for projection_matrix in order to be able to access this 
    #      sensibly via the UI... May need to explicitly define subtypes, ie,
    #      SurfaceToEEG, SurfaceToMEG, RegionToEEG,  RegionToMEG, etc
    projection_matrix_data = projections.ProjectionMatrix(required = True, default = None, 
                                                label = "EEG Projection Matrix",
                                                doc = """An array that is used to 
                                                map activity from nodes of the 
                                                simulation to a set of EEG 
                                                sensors.""")


    def __init__(self, **kwargs):
        """Initialise EEG monitor from the base Monitor class."""
        LOG.info("%s: initing..." % str(self))
        super(EEG, self).__init__(**kwargs)
        LOG.debug("%s: inited." % repr(self))

    @property
    def projection_matrix(self):
        """
        Define shortcut for retrieving ProjectionMatrix array.
        """
        if self.projection_matrix_data is None:
            return None
        return self.projection_matrix_data.projection_data


    @property
    def sensors(self):
        if self.projection_matrix_data is not None:
            return self.projection_matrix_data.sensors
        return None


    def config_for_sim(self, simulator):
        """
        Set the monitor's variables of interest based on the model
        specification. Calculates the number of integration steps (isteps)
        between returns by the record method. And initialises the stock array
        over which the simulation state will be temporally averaged before the 
        projection_matrix is applied.

        """
        super(EEG, self).config_for_sim(simulator)

        if self.projection_matrix is None or self.projection_matrix.size == 0:
            self.projection_matrix_data = projections.ProjectionSurfaceEEG()
            self.projection_matrix_data.projection_data = simulator.surface.eeg_projection
            simulator.surface.trait['eeg_projection'].log_debug(owner=self.__class__.__name__)
        else:
            self.projection_matrix_data.trait['projection_data'].log_debug(owner=self.__class__.__name__)

        if (self.projection_matrix is None or simulator.number_of_nodes != self.projection_matrix.shape[1]):
            raise Exception("Incompatible Monitor EEG Projection Matrix with simulation nodes!! Expected length:" 
                            + str(simulator.number_of_nodes))
        stock_size = (self.istep, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        self._stock = numpy.zeros(stock_size)
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """ 
        Records if integration step corresponds to sampling period. Otherwise
        just update the monitor's stock.

        """
        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
        if step % self.istep == 0:
            time = (step - self.istep / 2.0) * self.dt
            avg_stock = numpy.mean(self._stock, axis=0)
            #If there are multiple variables or modes we assume they can be 
            #sensibly summed to form a single source...
            avg_stock = avg_stock.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            avg_stock = avg_stock.sum(axis=2)[:,:,numpy.newaxis] #modes
            eeg = numpy.dot(self.projection_matrix, avg_stock)
            return [time, eeg.transpose((1, 0, 2))]



#class MEG(Monitor):
#    """
#    Monitors the temporally averaged value for the models variable of interest
#    projected to sensors on the head surface at each sampling period.
#    
#    .. note:: For the moment, this returns single squid MEG.
#    
#    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
#    .. #can't find the methods of the class, the class specific names below get
#    .. #us around this...
#    .. automethod:: MEG.__init__
#    .. automethod:: MEG.config_for_sim
#    .. automethod:: MEG.record
#    
#    """
#    #_ui_name = "MEG (ONLY FOR reg13 SURFACE + o52r00_irp2008 CORTEX-ONLY CONNECTIVITY (74))"
#    
#    #TODO: Currently all monitors return a 3D state [variables of interest, nodes, modes],
#    #      resulting in a 4D TimeSeries with time as the zeroth dim, however,
#    #      TimeSeriesMEG is really intended to only be 2D [time, channels]. So,
#    #      we should be summing over variables of interest and Modes, however,
#    #      this will require across the board changes to Analysers their adapters
#    #      and some visualisers so that everything works... In other words, this
#    #      will need to be done in one big step, otherwise it'll break everthing. 
#    
#    #TODO: add reference electrode capability, support single point through to 
#    #      grand average
#    
#    #TODO: ?Maybe easier from UI perspective to frame this in terms of sources,
#    #       head geometry, and sensors...?
#    
#    #TODO: Probably going to need to make ProjectionMatrix a datatype and then
#    #      use it for projection_matrix in order to be able to access this 
#    #      sensibly via the UI... May need to explicitly define subtypes, ie,
#    #      SurfaceToEEG, SurfaceToMEG, RegionToEEG,  RegionToMEG, etc
#    projection_matrix = arrays.FloatArray(
#        label = "Projection matrix",
#        required = True,
#        doc = """An array that is used to map activity from nodes of the 
#        simulation to a set of MEG sensors.""")
#    
#    
#    def __init__(self, **kwargs):
#        """Initialise MEG monitor from the base Monitor class."""
#        LOG.info("%s: initing..." % str(self))
#        super(MEG, self).__init__(**kwargs)
#        LOG.debug("%s: inited." % repr(self))
#    
#    
#    def config_for_sim(self, simulator):
#        """
#        Set the monitor's variables of interest based on the model
#        specification. Calculates the number of integration steps (isteps)
#        between returns by the record method. And initialises the stock array
#        over which the simulation state will be temporally averaged before the 
#        projection_matrix is applied.
#        
#        """
#        super(MEG, self).config_for_sim(simulator)
#        
#        if self.projection_matrix.size == 0:
#            self.projection_matrix = simulator.surface.meg_projection
#        
#        self.trait["projection_matrix"].log_debug(owner=self.__class__.__name__)
#        
#        stock_size = (self.istep, self.voi.shape[0],
#                      simulator.number_of_nodes,
#                      simulator.model.number_of_modes)
#        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))
#        
#        self._stock = numpy.zeros(stock_size)
#        #import pdb; pdb.set_trace()
#    
#    
#    def record(self, step, state):
#        """ 
#        Records if integration step corresponds to sampling period. Otherwise
#        just update the monitor's stock.
#        
#        """
#        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
#        if step % self.istep == 0:
#            time = (step - self.istep / 2.0) * self.dt
#            avg_stock = numpy.mean(self._stock, axis=0)
#            #If there are multiple variables or modes we assume they can be 
#            #sensibly summed to form a single source...
#            avg_stock = avg_stock.sum(axis=0)[numpy.newaxis,:,:] #state-variables
#            avg_stock = avg_stock.sum(axis=2)[:,:,numpy.newaxis] #modes
#            meg = numpy.dot(self.projection_matrix, avg_stock)
#            return [time, meg.transpose((1, 0, 2))]
#


#TODO: Once OpenMEEG is operational, dump the sphericals they're a hacky mess...

class SphericalEEG(Monitor):
    """
    Monitors the temporally averaged value for the models variable of interest 
    projected to sensors on the head surface at each sampling period.  

    .. [Sarvas_1987] Sarvas, J., *Basic mathematical and electromagnetic
        concepts of the biomagnetic inverse problem*, Physics in Medicine and
        Biology, 1987.

    .. note:: For the moment, this returns idealised (reference free) EEG.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: SphericalEEG.__init__
    .. automethod:: SphericalEEG.config_for_sim
    .. automethod:: SphericalEEG.record

    """
    _ui_name = "Spherical EEG"

    #TODO: Currently all monitors return a 3D state [variables of interest, nodes, modes],
    #      resulting in a 4D TimeSeries with time as the zeroth dim, however,
    #      TimeSeriesEEG is really intended to only be 2D [time, channels]. So,
    #      we should be summing over variables of interest and Modes, however,
    #      this will require across the board changes to Analysers their adapters
    #      and some visualisers so that everything works... In other words, this
    #      will need to be done in one big step, otherwise it'll break everthing. 

    #TODO: add reference electrode capability, support single point through to 
    #      grand average

    #TODO: Remove the default load, require sensors to be specified else error.

    sigma = basic.Float(label = "conductivity",
                  default = 1.0)

    sensors = sensors_module.SensorsEEG(
        label = "EEG Sensors",
        default = None,
        required = True,
        doc = """The set of EEG sensors for which the forward solution will be
        calculated.""")


    def __init__(self, **kwargs):
        """
        Initialise from the base Monitor class. Setting sampling period.

        """
        LOG.info("%s: initing..." % str(self))
        super(SphericalEEG, self).__init__(**kwargs)

        self.projection_matrix = None
        LOG.debug("%s: inited." % repr(self))


    def config_for_sim(self, simulator):
        """
        Equation 12 of [Sarvas_1987]_

        TODO: add equations...

        """
        super(SphericalEEG, self).config_for_sim(simulator)

        #parameter to
        sigma = self.sigma # 1.0

        #r => sensor positions
        #r_0 => source positions
        #a => vector from sources_to_sensor
        #Q => source unit vectors
        if simulator.surface is None:
            r_0 = simulator.connectivity.centres
            Q = simulator.connectivity.orientations # * simulator.connectivity.areas
        else:
            r_0 = simulator.surface.vertices
            Q = simulator.surface.vertex_normals

        centre = numpy.mean(r_0, axis=0)[numpy.newaxis, ]
        radius = 1.05125 * max(numpy.sqrt(numpy.sum((r_0 - centre)**2, axis=1)))

        #Stick sensors on a sphere enclosing the sources...
        # use local to avoid modifying H5 data file
        sensor_locations = self.sensors.locations.copy()
        sen_dis = numpy.sqrt(numpy.sum((sensor_locations)**2, axis=1))
        sensor_locations = sensor_locations / sen_dis[:, numpy.newaxis]
        sensor_locations = sensor_locations * radius
        sensor_locations = sensor_locations + centre

        #should check all sensors positions are > r_0, and that sensors positions lie on sphere...
        #import pdb; pdb.set_trace()
        #a = sensor_locations - r_0
        #na = numpy.sqrt(numpy.sum(a**2, axis=1))[:, numpy.newaxis]
        #nr = numpy.sqrt(numpy.sum(sensor_locations**2, axis=1))[:, numpy.newaxis]
        #Shouldn't have to loop, but I'm tired...
        V_r = numpy.zeros((sensor_locations.shape[0], r_0.shape[0]))
        for sensor_k in numpy.arange(sensor_locations.shape[0]):
            a = sensor_locations[sensor_k, :] - r_0
            na = numpy.sqrt(numpy.sum(a**2, axis=1))[:, numpy.newaxis]
            #import pdb; pdb.set_trace()
            V_r[sensor_k, :] = numpy.sum(Q * (a / na**3), axis=1 ) / (4.0 * numpy.pi * sigma)

        self.projection_matrix = V_r

        util.log_debug_array(LOG, self.projection_matrix, "projection_matrix", 
                             owner=self.__class__.__name__)

        stock_size = (self.istep, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        self._stock = numpy.zeros(stock_size)
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """ Records if integration step corresponds to sampling period. """
        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
        if step % self.istep == 0:
            time = (step - self.istep / 2.0) * self.dt
            avg_stock = numpy.mean(self._stock, axis=0)
            #If there are multiple variables or modes we assume they can be 
            #sensibly summed to form a single source...
            avg_stock = avg_stock.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            avg_stock = avg_stock.sum(axis=2)[:,:,numpy.newaxis] #modes
            eeg = numpy.dot(self.projection_matrix, avg_stock)
            return [time, eeg.transpose((1, 0, 2))]




class SphericalMEG(Monitor):
    """
    Monitors the temporally averaged value for the models variable of interest 
    projected to sensors on the head surface at each sampling period.

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: SphericalMEG.__init__
    .. automethod:: SphericalMEG.config_for_sim
    .. automethod:: SphericalMEG.record

    """
    _ui_name = "Spherical MEG"

    #TODO: Currently all monitors return a 3D state [variables of interest, nodes, modes],
    #      resulting in a 4D TimeSeries with time as the zeroth dim, however,
    #      TimeSeriesMEG is really intended to only be 2D [time, channels]. So,
    #      we should be summing over variables of interest and Modes, however,
    #      this will require across the board changes to Analysers their adapters
    #      and some visualisers so that everything works... In other words, this
    #      will need to be done in one big step, otherwise it'll break everthing. 

    #TODO: add reference electrode capability, support single point through to 
    #      grand average

    sensors = sensors_module.SensorsMEG(
        label = "MEG Sensors",
        default = None,
        required = True,
        doc = """The set of MEG sensors for which the forward solution will be
        calculated.""")


    def __init__(self, **kwargs):
        """
        Initialise from the base Monitor class. Add a placeholder attribute for
        the projectin matrix.
        """
        LOG.info("%s: initing..." % str(self))
        super(SphericalMEG, self).__init__(**kwargs)
        self.projection_matrix = None
        LOG.debug("%s: inited." % repr(self))


    def config_for_sim(self, simulator):
        """
        Equation 25 of [Sarvas_1987]_

        TODO: add equation...

        """
        super(SphericalMEG, self).config_for_sim(simulator)

        #the magnetic constant = 1.25663706 × 10-6 m kg s-2 A-2  (H/m)
        mu_0 = 1.25663706 #mH/mm #TODO: Think units are wrong, should still be × 10-6

        #parameter to
        #sigma = 1.0

        #r => sensor positions
        #r_0 => source positions
        #a => vector from sources_to_sensor
        #Q => source unit vectors
        if simulator.surface is None:
            r_0 = simulator.connectivity.centres
            Q = simulator.connectivity.orientations
        else:
            r_0 = simulator.surface.vertices
            Q = simulator.surface.vertex_normals

        centre = numpy.mean(r_0, axis=0)[numpy.newaxis, :]
        radius = 1.25 * max(numpy.sqrt(numpy.sum((r_0 - centre)**2, axis=1)))

        #Stick sensors on a sphere enclosing the sources...
        # use local to avoid modifying H5 data file
        sensor_locations = self.sensors.locations.copy()
        sen_dis = numpy.sqrt(numpy.sum((sensor_locations)**2, axis=1))
        sensor_locations = sensor_locations / sen_dis[:, numpy.newaxis]
        sensor_locations = sensor_locations * radius
        sensor_locations = sensor_locations + centre

        #should check all sensor_locations are > r_0
        #import pdb; pdb.set_trace()
        #a = sensor_locations - r_0
        #na = numpy.sqrt(numpy.sum(a**2, axis=1))[:, numpy.newaxis]
        #nr = numpy.sqrt(numpy.sum(sensor_locations**2, axis=1))[:, numpy.newaxis]
        #Shouldn't have to loop, but I'm tired...

        #import pdb; pdb.set_trace()

        B_r = numpy.zeros((sensor_locations.shape[0], r_0.shape[0], 3))
        for sensor_k in numpy.arange(sensor_locations.shape[0]):
            a = sensor_locations[sensor_k,:] - r_0
            na = numpy.sqrt(numpy.sum(a**2, axis=1))[:, numpy.newaxis]
            rsk = sensor_locations[sensor_k,:][numpy.newaxis, :]
            nr = numpy.sqrt(numpy.sum(rsk**2, axis=1))[:, numpy.newaxis]

            F = a * (nr * a + nr**2 - numpy.sum(r_0 * rsk, axis=1)[:, numpy.newaxis])
            adotr = numpy.sum((a / na) * rsk, axis=1)[:, numpy.newaxis]
            delF = ((na**2 / nr + adotr + 2.0 * na + 2.0 * nr) * rsk - 
                    (a + 2.0 * nr + adotr * r_0))

            B_r[sensor_k, :] = ((mu_0 / (4.0 * numpy.pi * F**2)) * 
                (numpy.cross(F * Q, r_0) - numpy.sum(numpy.cross(Q, r_0) *
                (rsk * delF), axis=1)[:, numpy.newaxis]))

        self.projection_matrix = numpy.sqrt(numpy.sum(B_r**2, axis=2))

        util.log_debug_array(LOG, self.projection_matrix, "projection_matrix",
                             owner=self.__class__.__name__)

        stock_size = (self.istep, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        self._stock = numpy.zeros(stock_size)
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """
        Records if integration step corresponds to sampling period. The 
        projection_matrix generated by the config_for_sim method is used to map
        activity at nodes of the simulation to a set of MEG sensors.

        """
        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
        if step % self.istep == 0:
            time = (step - self.istep / 2.0) * self.dt
            avg_stock = numpy.mean(self._stock, axis=0)
            #If there are multiple variables or modes we assume they can be 
            #sensibly summed to form a single source...
            avg_stock = avg_stock.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            avg_stock = avg_stock.sum(axis=2)[:,:,numpy.newaxis] #modes
            meg = numpy.dot(self.projection_matrix, avg_stock)
            return [time, meg.transpose((1, 0, 2))]



#NOTE: It's probably best to do voxelisation as an offline "analysis" style
#      process, returning region or surface timeseries for BOLD based on the
#      simulation. The voxelisation only really makes sense for surface anyway,
#      and it should be interesting/benificial to be able to compare the effect
#      of different voxelisations on the same underlying surface.
class Bold(Monitor):
    """

    A Ballon-Windkessel like model  

    .. [B_1997] Buxton, R. and Frank, L., *A Model for the Coupling between 
        Cerebral Blood Flow and Oxygen Metabolism During Neural Stimulation*,
        17:64-72, 1997.

    .. [F_2000] Friston, K., Mechelli, A., Turner, R., and Price, C., *Nonlinear 
        Responses in fMRI: The Balloon Model, Volterra Kernels, and Other 
        Hemodynamics*, NeuroImage, 12, 466 - 477, 2000.

    .. VJ derivation...

    .. note:: LIMITATIONS: sampling period must be integer multiple of 500ms

    .. note:: CONSIDERATIONS: It is  sensible to use this monitor if your 
              simulation length is > 30s (30000ms)

    .. warning:: Not yet tested, debugged, generalised etc...
    .. wisdom and plagiarism

    .. #Currently there seems to be a clash betwen traits and autodoc, autodoc
    .. #can't find the methods of the class, the class specific names below get
    .. #us around this...
    .. automethod:: Bold.__init__
    .. automethod:: Bold.config_for_sim
    .. automethod:: Bold.record

    """
    _ui_name = "BOLD"

    #Over-ride the Monitor baseclass period...
    period = basic.Float(
        label = "Sampling period (ms)",
        default = 2000.0,
        doc = """For the BOLD monitor, sampling period in milliseconds must be
            an integral multiple of 500""")

    tau_s = basic.Float(
        label = "Dimensionless? exponential decay parameter",
        default = 0.8)

    tau_f = basic.Float(
        label = "Dimensionless? oscillatory parameter",
        default = 0.4)
        
    k1 = basic.Float(
        label = "First Volterra kernel coefficient",
        default = 5.6,
        order = -1)
        
    V0 = basic.Float(
        label = "resting blood volume fraction ",
        default = 0.02,
        order = -1)



    def __init__(self, **kwargs):
        """
        Initialise from the base Monitor class.

        """
        LOG.info("%s: initing..." % str(self))
        super(Bold, self).__init__(**kwargs)
        LOG.warning("%s: Needs testing, debugging, etc..." % repr(self))

        #Bold measurement period is much larger than our simulation's dt, so we
        #need an interim downsampling to support it. 
        #TODO: adapt monitors to support chaining, so we can just stick a 
        #      temporal average followed by the bold response convolution and
        #      then a spatial average (node to voxel, only really relevant for 
        #      surface simulations).
        self._interim_period = None
        self._interim_istep = None
        self._interim_stock = None #I hate bold.
        self._stock_steps = None

        self.hemodynamic_response_function = None

        LOG.debug("%s: inited." % repr(self))

    def compute_hrf(self):
        r"""
        Compute the heamodynamic response function.

        .. math::
            G(t - t^{\prime}) &= 
             e^{\frac{1}{2} \left(\frac{t - t^{\prime}}{\tau_s} \right)}
             \frac{\sin\left((t - t^{\prime})
             \sqrt{\frac{1}{\tau_f} - \frac{1}{4 \tau_s^2}}\right)} 
             {\sqrt{\frac{1}{\tau_f} - \frac{1}{4 \tau_s^2}}}
             \; \; \; \; \; \;  for \; \; \; t \geq t^{\prime} \\
             &= 0 \; \; \; \; \; \;  for \; \; \;  t < t^{\prime}


        """

        #TODO: Current traits limitations require this moved to config_for_sim()
        if numpy.mod(self.period, 500.0): #TODO: This is a temporary limit, need to fix configure...
            msg = "%s: BOLD.period must be a multiple of 500.0, period = %s"
            LOG.error(msg % (str(self), str(self.period)))

        #Typical scanner TR is 2s, means Bold period 2000ms

        #downsample avereage over simulator steps to give fixed sr (256Hz)
           #then (18.75 * tau_s) * 256  ==> 3840 required length of _stock

         # simulation in ms therefore 1000.0/256.0 ==> 3.90625 _interim_period in ms
        LOG.warning("%s: Needs testing, debugging, etc..." % repr(self))

        magic_sample_rate = 2.0**-2 #/ms #NOTE: An integral multiple of dt
        magic_number = 19200.0 * self.tau_s #truncates G, see below, once ~zero 

        #Length of history needed for convolution in ms
        required_history_length = magic_sample_rate * magic_number 
        self._stock_steps = numpy.ceil(required_history_length).astype(int)
        stock_time = numpy.arange(0.0, magic_number/1000.0, magic_number/1000.0/self._stock_steps) #TODO: neaten

        # The Heamodynamic response function.
        sqrt_tfts = numpy.sqrt(1.0/self.tau_f - 1.0/(4.0*self.tau_s**2))
        exp_ts = numpy.exp(-0.5*(stock_time/self.tau_s))
        G = exp_ts * (numpy.sin(sqrt_tfts * stock_time) / sqrt_tfts)

        #Reverse it, need it into the past for matrix-multiply of stock
        G = G[::-1]
        self.hemodynamic_response_function = G[numpy.newaxis, :]

        util.log_debug_array(LOG, self.hemodynamic_response_function,
                             "hemodynamic_response_function",
                             owner=self.__class__.__name__)

        #Interim stock configuration
        self._interim_period = 1.0 / magic_sample_rate #period in ms
        self._interim_istep = int(round(self._interim_period / self.dt))



    def config_for_sim(self, simulator):
        """
        Set up stock arrays
       
        """
        super(Bold, self).config_for_sim(simulator)

        self.compute_hrf() # now we have self.hemodynamic_response_function

        interim_stock_size = (self._interim_istep, self.voi.shape[0],
                              simulator.number_of_nodes,
                              simulator.model.number_of_modes) 
        LOG.debug("%s: interim_stock_size is %s" % (str(self), str(interim_stock_size)))

        self._interim_stock = numpy.zeros(interim_stock_size)

        #Stock configuration
        stock_size = (self._stock_steps, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        #Set the inital _stock based on simulator.history
        mean_history = numpy.mean(simulator.history[:, self.voi, :, :], axis=0)
        self._stock = mean_history[numpy.newaxis,:] * numpy.ones(stock_size)
        #NOTE: BOLD can have a long (~15s) transient that is mainly due to the
        #      initial dynamic transient from simulations that are started with 
        #      imperfect initlial conditions.
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """
        Returns a result if integration step corresponds to sampling period.
        Updates the interim-stock on every step and updates the stock if the 
        step corresponds to the interim period.

        """
        #Update the interim-stock at every step
        self._interim_stock[((step % self._interim_istep) - 1), :] = state[self.voi, :]

        #At stock's period update it with the temporal average of interim-stock
        if step % self._interim_istep == 0:
            #import pdb; pdb.set_trace()
            avg_interim_stock = numpy.mean(self._interim_stock, axis=0)
            self._stock[((step/self._interim_istep % self._stock_steps) - 1), :] = avg_interim_stock

        #At the monitor's period, apply the heamodynamic response function to
        #the stock and return the resulting BOLD signal.
        if step % self.istep == 0:
            time = step * self.dt
            hrf = numpy.roll(self.hemodynamic_response_function,
                             ((step/self._interim_istep % self._stock_steps) - 1),
                             axis=1)
            bold = (numpy.dot(hrf, self._stock.transpose((1, 2, 0, 3))) - 1.0) * (self.k1 * self.V0 / 3.0)
            bold = bold.reshape(self._stock.shape[1:])
            bold = bold.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            bold = bold.sum(axis=2)[:,:,numpy.newaxis] #modes
            return [time, bold]


class BoldRegionROI(Bold):
    """
    The BoldRegionROI monitor assumes that it is being used on a surface and 
    uses the region mapping of the surface to generate regional signals which
    are the spatial average of all vertices in the region. 

    This was originated to compare the results of a Bold monitor with a 
    region level simulation with that of an otherwise identical surface
    simulation.

    """
    _ui_name = "BOLD Region ROI"

    def config_for_sim(self, simulator):
        super(BoldRegionROI, self).config_for_sim(simulator)
        self.region_mapping = simulator.surface.region_mapping

    def record(self, step, state, array=numpy.array):
        result = super(BoldRegionROI, self).record(step, state)
        if result:
            t, data = result
            return [t, array([data.flat[self.region_mapping==i].mean()
                              for i in xrange(self.region_mapping.max())])]
        else:
            return None

class BoldMultithreaded(Bold):
    """
    This is another Bold clone built to work with the GPU parameter sweep
    simulator. Design criteria

    - we're doing a temporal downsampling before passing into this monitor
      so we need to specify the internal sampling rate using in the stock.
      We assume for now that the downsampled signal's Nyquist frequency is 
      outside the range of significant response of the HRF.

      As a quick workaround, just set Bold.dt to the temporal averaged sampling
      frequency.

    - we'll be passing state to this monitor where there's an additional 
      index for the GPU thread, i.e.

        stock.shape == (n_stock, nodes, vars, modes, threads)

      where threads is a multiple of 32, up to even 2**15 (in extreme
      cases), so algorithm etc needs to handle this extra 
      dimension.

    PS After rewriting a few lines from the Bold class, it seems that
       taking advantage of NumPy style indexing, the array handling can
       be general to whether we're using the threads dimension or not; it
       simply doesn't touch it, but operations automatically work correctly.

    """

    def config_for_sim(self, simulator, n_thr=1):
        """
        Set up stock arrays
       
        """
        super(BoldMultithreaded, self).config_for_sim(simulator)
        self.compute_hrf()

        interim_stock_size = (self._interim_istep, self.voi.shape[0],
                              simulator.number_of_nodes,
                              simulator.model.number_of_modes,
                              n_thr) 
        LOG.debug("%s: interim_stock_size is %s" % (str(self), str(interim_stock_size)))

        self._interim_stock = numpy.zeros(interim_stock_size)

        #Stock configuration
        stock_size = (self._stock_steps, ) + self._interim_stock.shape[1:]
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        #Set the inital _stock based on simulator.history
        mean_history = numpy.mean(simulator.history[:, self.voi], axis=0)
        self._stock = mean_history[numpy.newaxis,:] * numpy.ones(stock_size)
        #NOTE: BOLD can have a long (~15s) transient that is mainly due to the
        #      initial dynamic transient from simulations that are started with 
        #      imperfect initlial conditions.
        #import pdb; pdb.set_trace()


    def record(self, step, state):
        """
        Returns a result if integration step corresponds to sampling period.
        Updates the interim-stock on every step and updates the stock if the 
        step corresponds to the interim period.

        """
        #Update the interim-stock at every step
        self._interim_stock[((step % self._interim_istep) - 1), ...] = state[self.voi]

        #At stock's period update it with the temporal average of interim-stock
        if step % self._interim_istep == 0:
            #import pdb; pdb.set_trace()
            avg_interim_stock = numpy.mean(self._interim_stock, axis=0)
            i_stock = ((step/self._interim_istep % self._stock_steps) - 1)
            self._stock[i_stock, ...] = avg_interim_stock

        #At the monitor's period, apply the heamodynamic response function to
        #the stock and return the resulting BOLD signal.
        if step % self.istep == 0:

            # convenient locals
            time = step * self.dt
            kernel = self.hemodynamic_response_function
            stock = self._stock
            shape = self._stock.shape # (time, voi, node, mode, thr)

            # compute "full" response, then average across voi & modes
            response = (stock  .reshape((shape[0], -1)).T*kernel).sum(1)
            averaged = response.reshape (shape[1:]).sum(0).sum(1)
            
            # return with fully general shape
            return [time, averaged.reshape((1, shape[2], 1) + shape[4:])]


class BalloonWindkesselAccordingToKJFristonEtAl2003NeuroImage(Monitor):
    """

    The full Balloon-Windkessel model, following Friston et al's paper
    detailing the equations describing hemodynamic state. 

    Currently, this monitor models the BOLD activity of the nodes of the
    simulation, not voxels. 

    .. [F_2003] Friston, K., Harrison, L., and Penny, W., *Dynamic causal
        modeling*, NeuroImage, 19, 1273 - 1302, 2003.

    """
    _ui_name = "Balloon-Windkessel"

    class config:

        period = basic.Float(
            label = "Sampling period (ms)",
            default = 1000.0,
            doc = """Sampling period of the Balloon""")

        nvcvar = basic.Integer(
            label = "Neurovascular coupling variable index",
            default = 0,
            doc = ""
            )

        #                                   prior mean          prior variance

        kappa = basic.Float(
            label="",
            default=                        0.65, # per/s       0.015
            doc="Rate of signal decay"
            )

        gamma = basic.Float(
            label="",
            default=                        0.41, # per/s       0.002
            doc="Rate of flow-dependent elimination"
            )

        tau = basic.Float(
            label="",
            default=                        0.98, # s           0.0568
            doc="Haemodynamic transit time"
            )

        alpha = basic.Float(
            label="",
            default=                        0.32, #             0.0015
            doc="Grubb's exponent"
            )

        rho = basic.Float(
            label="",
            default=                        0.34, #             0.0024
            doc="Resting oxygen extraction fraction"
            )

    """
    class state:

        z_i = FloatArray()
        s_i = FloatArray()
        f_i = FloatArray()
        v_i = FloatArray()
        q_i = FloatArray()
        y_i = FloatArray()

    class ddt:
        pass

    """
        
    def __init__(self, *args, **kwds):
        raise NotImplementedError
    
    def record(self, step, state):
        """
        Returns a result if integration step corresponds to sampling period.
        Updates the interim-stock on every step and updates the stock if the 
        step corresponds to the interim period.

        """
        #Update the interim-stock at every step
        self._interim_stock[((step % self._interim_istep) - 1), :] = state[self.voi, :]

        #At stock's period update it with the temporal average of interim-stock
        if step % self._interim_istep == 0:
            #import pdb; pdb.set_trace()
            avg_interim_stock = numpy.mean(self._interim_stock, axis=0)
            self._stock[((step/self._interim_istep % self._stock_steps) - 1), :] = avg_interim_stock

        #At the monitor's period, apply the heamodynamic response function to
        #the stock and return the resulting BOLD signal.
        if step % self.istep == 0:
            time = step * self.dt
            hrf = numpy.roll(self.hemodynamic_response_function,
                             ((step/self._interim_istep % self._stock_steps) - 1),
                             axis=1)
            bold = numpy.dot(hrf, self._stock.transpose((1, 2, 0, 3)))
            bold = bold.reshape(self._stock.shape[1:])
            bold = bold.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            bold = bold.sum(axis=2)[:,:,numpy.newaxis] #modes
            return [time, bold]


class SEEG(Monitor):
    """
    Monitors electrophysiological signals from depth electrodes (intended for stereo-EEG).
    """
    _ui_name = "stereo-EEG"

    sigma = basic.Float(label = "conductivity",
                  default = 1.0)

    sensors = sensors_module.SensorsInternal(
        label = "Internal brain sensors",
        default = None,
        required = True,
        doc = """The set of SEEG sensors for which the forward solution will be
        calculated.""")

    def __init__(self, **kwargs):
        """
        Initialise from the base Monitor class. Setting sampling period.

        """
        LOG.info("%s: initing..." % str(self))
        super(SEEG, self).__init__(**kwargs)

        self.projection_matrix = None
        LOG.debug("%s: inited." % repr(self))

    def config_for_sim(self, simulator):
        """
        Compute the projection matrix -- simple distance weight for now.
        Equation 12 from sarvas1987basic (point dipole in homogeneous space): 
          V(r) = 1/(4*pi*\sigma)*Q*(r-r_0)/|r-r_0|^3
        """
        super(SEEG, self).config_for_sim(simulator)

        if self.sensors is None:
            self.sensors = sensors_module.SensorsInternal(
                label = "Internal brain sensors",
                default = None,
                required = True,
                doc = """The set of SEEG sensors for which the forward solution will be
                calculated.""")

        
        if simulator.surface is None:
            r_0 = simulator.connectivity.centres
            Q = simulator.connectivity.orientations # * simulator.connectivity.areas
        else:
            r_0 = simulator.surface.vertices
            Q = simulator.surface.vertex_normals

        V_r = numpy.zeros((self.sensors.locations.shape[0], r_0.shape[0]))
        for sensor_k in numpy.arange(self.sensors.locations.shape[0]):
            a = self.sensors.locations[sensor_k, :] - r_0
            na = numpy.sqrt(numpy.sum(a**2, axis=1))[:, numpy.newaxis]
            V_r[sensor_k, :] = numpy.sum(Q * (a / na**3), axis=1 ) / (4.0 * numpy.pi * self.sigma)

        self.projection_matrix = V_r

        util.log_debug_array(LOG, self.projection_matrix, "projection_matrix",
                             owner=self.__class__.__name__)

        stock_size = (self.istep, self.voi.shape[0],
                      simulator.number_of_nodes,
                      simulator.model.number_of_modes)
        LOG.debug("%s: stock_size is %s" % (str(self), str(stock_size)))

        self._stock = numpy.zeros(stock_size)


    def record(self, step, state):
        """
        Same as the EEG monitor:
        """
        self._stock[((step % self.istep) - 1), :] = state[self.voi, :]
        if step % self.istep == 0:
            time = (step - self.istep / 2.0) * self.dt
            avg_stock = numpy.mean(self._stock, axis=0)
            #If there are multiple variables or modes we assume they can be 
            #sensibly summed to form a single source...
            avg_stock = avg_stock.sum(axis=0)[numpy.newaxis,:,:] #state-variables
            avg_stock = avg_stock.sum(axis=2)[:,:,numpy.newaxis] #modes
            eeg = numpy.dot(self.projection_matrix, avg_stock)
            return [time, eeg.transpose((1, 0, 2))]

