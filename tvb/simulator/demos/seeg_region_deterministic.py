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

Demonstrate using the simulator at the region level, deterministic interation.



``Run time``: approximately 2 seconds (workstation circa 2010)

``Memory requirement``: < 1GB



.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>



"""



# Third party python libraries

import numpy



"""

# Try and import from "The Virtual Brain"

from tvb.simulator.common import get_logger

LOG = get_logger(__name__)



#Import from tvb.simulator modules:

import tvb.simulator.simulator as simulator

import tvb.simulator.models as models

import tvb.simulator.coupling as coupling

import tvb.simulator.integrators as integrators

import tvb.simulator.monitors as monitors



import tvb.datatypes.connectivity as connectivity



from matplotlib.pyplot import *

"""



from tvb.simulator.lab import *

import tvb.datatypes.sensors as sensors
import tvb.basic.traits.data_readers as readers



##----------------------------------------------------------------------------##

##-                      Perform the simulation                              -##

##----------------------------------------------------------------------------##



LOG.info("Configuring...")

#Initialise a Model, Coupling, and Connectivity.


# TODO: ugly, move to default?
sensfile = readers.File(folder_path = "sensors", file_name = 'internal_39.txt.bz2')
sens = sensors.SensorsInternal()
sens.locations = sensfile.read_data(usecols = (1,2,3), field = "locations")
sens.labels = sensfile.read_data(usecols = (0,), dtype = "string", field = "labels")



oscilator = models.Generic2dOscillator()

white_matter = connectivity.Connectivity()

white_matter.speed = numpy.array([4.0])



white_matter_coupling = coupling.Linear(a=0.0154)



#Initialise an Integrator

heunint = integrators.HeunDeterministic(dt=2**-6)



#Initialise some Monitors with period in physical time

momo = monitors.Raw()

mama = monitors.TemporalAverage(period=2**-2)

mon_seeg = monitors.SEEG(sensors = sens,period=2**-2)



#Bundle them

what_to_watch = (momo, mama, mon_seeg)



#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.

sim = simulator.Simulator(model = oscilator, connectivity = white_matter,

                          coupling = white_matter_coupling, 

                          integrator = heunint, monitors = what_to_watch)



sim.configure()



LOG.info("Starting simulation...")

#Perform the simulation

raw_data = []

raw_time = []

tavg_data = []

tavg_time = []

seeg_data = []

seeg_time = []



for raw, tavg, seeg in sim(simulation_length=2**6):

    if not raw is None:

        raw_time.append(raw[0])

        raw_data.append(raw[1])

    

    if not tavg is None:

        tavg_time.append(tavg[0])

        tavg_data.append(tavg[1])

    if not seeg is None:

        print len(seeg[1])
        seeg_time.append(seeg[0])

        seeg_data.append(seeg[1])



LOG.info("Finished simulation.")



##----------------------------------------------------------------------------##

##-               Plot pretty pictures of what we just did                   -##

##----------------------------------------------------------------------------##



#Plot defaults in a few combinations



#Make the lists numpy.arrays for easier use.

RAW = numpy.array(raw_data)

TAVG = numpy.array(tavg_data)

SEEG = numpy.array(seeg_data)



#Plot raw time series

figure(1)

plot(raw_time, RAW[:, 0, :, 0])

title("Raw -- State variable 0")



figure(2)

plot(raw_time, RAW[:, 1, :, 0])

title("Raw -- State variable 1")



#Plot temporally averaged time series

figure(3)

plot(tavg_time, TAVG[:, 0, :, 0])

title("Temporal average")



figure(3)

plot(seeg_time, SEEG[:, 0, :, 0])

title("SEEG measurement")

#Show them

show()



###EoF###

