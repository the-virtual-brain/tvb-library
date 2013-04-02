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
Demonstrate using the simulator for a surface simulation, deterministic 
integration.

``Run time``: approximately 27 seconds (workstation circa 2010).
``Memory requirement``: ~ 1 GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

#import os #For eeg_projection hack...

# Third party python libraries
import numpy
#from scipy import io as scipy_io #For eeg_projection hack...
"""
from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

#Import from tvb.simulator modules
#import tvb.simulator #For eeg_projection hack...
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.monitors as monitors

import tvb.datatypes.connectivity as connectivity
import tvb.datatypes.surfaces as surfaces

from matplotlib.pyplot import *
from tvb.simulator.plot.tools import *
"""

from tvb.simulator.lab import *
import tvb.datatypes.sensors as sensors
import tvb.basic.traits.data_readers as readers


##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.

sensfile = readers.File(folder_path = "sensors", file_name = 'internal_39.txt.bz2')
sens = sensors.SensorsInternal()
sens.locations = sensfile.read_data(usecols = (1,2,3), field = "locations")
sens.labels = sensfile.read_data(usecols = (0,), dtype = "string", field = "labels")

oscilator = models.Generic2dOscillator()
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=0.014)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=2**-4)

#Initialise some Monitors with period in physical time
mon_tavg = monitors.TemporalAverage(period=2**-2)
mon_savg = monitors.SpatialAverage(period=2**-2)
mon_eeg = monitors.EEG(period=2**-2)
mon_seeg = monitors.SEEG(period=2**-2)

#Bundle them
what_to_watch = (mon_tavg, mon_savg, mon_eeg, mon_seeg)

##TODO: UGLY, FIXME        
#root_path = os.path.dirname(tvb.simulator.__file__)
#proj_mat_path = os.path.join(root_path, 'files', "surfaces", "cortex_reg13", "projection_outer_skin_4096_eeg_1020_62.mat")
#matlab_data = scipy_io.matlab.loadmat(proj_mat_path)
#eeg_projection = matlab_data["ProjectionMatrix"]

#Initialise a surface
local_coupling_strength = numpy.array([2**-10])
default_cortex = surfaces.Cortex(coupling_strength=local_coupling_strength) #,
                                 #eeg_projection=eeg_projection)

#Initialise Simulator -- Model, Connectivity, Integrator, Monitors, and surface.
sim = simulator.Simulator(model = oscilator, connectivity = white_matter,
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch,
                          surface = default_cortex)

sim.configure()

LOG.info("Starting simulation...")
#Perform the simulation
tavg_data = []
tavg_time = []
savg_data = []
savg_time = []
eeg_data = []
eeg_time = []
seeg_data = []
seeg_time = []
for tavg, savg, eeg, seeg in sim(simulation_length=2**2):
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])
    
    if not savg is None:
        savg_time.append(savg[0])
        savg_data.append(savg[1])
    
    if not eeg is None:
        eeg_time.append(eeg[0])
        eeg_data.append(eeg[1])
    if not seeg is None:
        seeg_time.append(seeg[0])
        seeg_data.append(seeg[1])

LOG.info("finished simulation.")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

#Make the lists numpy.arrays for easier use.
TAVG = numpy.array(tavg_data)
SAVG = numpy.array(savg_data)
EEG = numpy.array(eeg_data)
SEEG = numpy.array(seeg_data)

#Plot region averaged time series
figure(3)
plot(savg_time, SAVG[:, 0, :, 0])
title("Region average")

#Plot EEG time series
figure(4)

color_idx = numpy.linspace(0, 1, EEG.shape[2])
for i in color_idx:
    plot(eeg_time, EEG[:, 0, :, 0], color=cm.cool(i), lw=3, alpha=0.2)
title("EEG")
color_idx = numpy.linspace(0, 1, SEEG.shape[2])
for i in color_idx:
    plot(seeg_time, SEEG[:, 0, :, 0], color=cm.cool(i), lw=3, alpha=0.2)
title("EEG")

#Show them
show()

#Surface movie, requires mayavi.malb
if IMPORTED_MAYAVI:
    st = surface_timeseries(sim.surface, TAVG[:, 0, :, 0])

###EoF###
