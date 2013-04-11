# -*- coding: utf-8 -*-

"""
Demonstrate using a 'contributed' model at the region level, deterministic
integration scheme.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy


# Try and import from "The Virtual Brain"
try:
    from tvb.basic.logger.builder import get_logger
    LOG = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)
    LOG.warning("Failed to import TVB logger, using Python logging directly...")

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.monitors as monitors
import tvb.datatypes.connectivity as connectivity


# Import the contributed model
# NOTE: the 'externals/contrib/simulator/models' folder should be added to the pythonpath
# >> export PYTHONPATH=/Users/paupau/trunk/externals/contrib/simulator/models:$PYTHONPATH


import BrunelWang as MODEL

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
bw = MODEL.BrunelWang()

white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=0.09)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=2**-5)

#Initialise some Monitors with period in physical time
momo = monitors.Raw()
mama = monitors.TemporalAverage(period=2**-2)

#Bundle them
what_to_watch = (momo, mama)

#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
sim = simulator.Simulator(model = bw, connectivity = white_matter,
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch)

sim.configure()

LOG.info("Starting simulation...")
#Perform the simulation
raw_data = []
raw_time = []
tavg_data = []
tavg_time = []
for raw, tavg in sim(simulation_length=2**8):
    if not raw is None:
        raw_time.append(raw[0])
        raw_data.append(raw[1])
    
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])

LOG.info("Finished simulation.")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

#Plot defaults in a few combinations
import matplotlib.pyplot as pyplot

#Make the lists numpy.arrays for easier use.
RAW = numpy.array(raw_data)
TAVG = numpy.array(tavg_data)

#Plot raw time series
pyplot.figure(1)
pyplot.plot(raw_time, RAW[:, 0, :, 0])
pyplot.title("Raw -- State variable 0")

pyplot.figure(2)
pyplot.plot(raw_time, RAW[:, 1, :, 0])
pyplot.title("Raw -- State variable 1")

#Plot temporally averaged time series
pyplot.figure(3)
pyplot.plot(tavg_time, TAVG[:, 0, :, 0])
pyplot.title("Temporal average")

#Show them
pyplot.show()

###EoF###
