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
Explore LarterBreakspear model.

``Run time``: 20 min (workstation circa 2012 Intel Xeon W3520@2.67Ghz)

``Memory requirement``: ~300 MB
``Storage requirement``: ~150MB

NOTE: stats were made for a simulation using the 998 region Hagmann
connectivity matrix.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Third party python libraries
import numpy

# Try and import from "The Virtual Brain"
from tvb.simulator.lab import *
from tvb.datatypes.time_series import TimeSeriesRegion
import tvb.analyzers.fmri_balloon as bold
from tvb.simulator.plot import timeseries_interactive as timeseries_interactive

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
lb = models.LarterBreakspear(QV_max=1.0, QZ_max=1.0, 
                             d_V=0.6, C=0.1, 
                             aee=0.5, aie=0.5, ani=0.1, 
                             VT=0.5,  gNa=0.0, Iext=0.165)

lb.variables_of_interest = ["V", "W", "Z"]

white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([7.0])

white_matter_coupling = coupling.HyperbolicTangent(a=0.5*lb.QV_max, 
                                                   midpoint=lb.VT, 
                                                   sigma=lb.d_V, 
                                                   normalise=True)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=0.2)

#Initialise some Monitors with period in physical time
mon_tavg =  monitors.TemporalAverage(period=2.)
mon_bold  = monitors.Bold(period=2000.)

#Bundle them
what_to_watch = (mon_bold, mon_tavg)

#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
sim = simulator.Simulator(model = lb, 
                          connectivity = white_matter,
                          coupling = white_matter_coupling, 
                          integrator = heunint, 
                          monitors = what_to_watch)

sim.configure()

LOG.info("Starting simulation...")
#Perform the simulation
bold_data, bold_time = [], []
tavg_data, tavg_time = [], []

for raw, tavg in sim(simulation_length=10000):
    if not raw is None:
        bold_time.append(raw[0])
        bold_data.append(raw[1])
    
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])

LOG.info("Finished simulation.")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

#Make the lists numpy.arrays for easier use.
BOLD = numpy.array(bold_data)
TAVG = numpy.array(tavg_data)

#Plot raw time series
figure(1)
plot(tavg_time, TAVG[:, 0, :, 0], 'k', alpha=0.1)
title("Raw -- State variable 0")

figure(2)
plot(tavg_time, TAVG[:, 1, :, 0], 'b', alpha=0.1)
title("Raw -- State variable 1")

figure(3)
plot(tavg_time, TAVG[:, 2, :, 0], 'r', alpha=0.1)
title("Raw -- State variable 2")

#Plot 3D trajectories
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(4)
ax = fig.gca(projection='3d')

for node in range(white_matter.number_of_regions):
  ax.plot(TAVG[:, 0, node, 0],  TAVG[:, 1, node, 0], TAVG[:, 2, node, 0], alpha=0.1)
ax.set_xlabel('V')
ax.set_ylabel('W')
ax.set_zlabel('Z')
plt.show()



#Make the list a numpy.array.
LOG.info("Converting result to array...")
TAVG_TIME = numpy.array(tavg_time)
BOLD_TIME = numpy.array(bold_time)

#Save tavg output
FILE_NAME = "demo_data_region_tavg_10s_500Hz_larterbreakspear"
LOG.info("Saving array to %s..." % FILE_NAME)
TAVG=numpy.load(FILE_NAME + '.npy')
TAVG_TIME=numpy.load(FILE_NAME+'_time.npy')

#Save bold output
FILE_NAME = "demo_data_region_bold_10s_500Hz_larterbreakspear"
LOG.info("Saving array to %s..." % FILE_NAME)
numpy.save(FILE_NAME + '.npy', BOLD)
numpy.save(FILE_NAME+'_time.npy', BOLD_TIME)


#Create TimeSeries instance
tsr = TimeSeriesRegion(data = TAVG,
                       time = TAVG_TIME,
                       sample_period = 2.)
tsr.configure()

#Create and run the monitor/analyser
bold_model = bold.BalloonModel(time_series = tsr)
bold_data  = bold_model.evaluate()

#Put the data into a TimeSeriesSurface datatype
bold_tsr = TimeSeriesRegion(connectivity = white_matter,
                            data = bold_data.data, 
                            time = bold_data.time)

#Prutty puctures...
tsi = timeseries_interactive.TimeSeriesInteractive(time_series = bold_tsr)
tsi.configure()
tsi.show()

#Save bold-balloon output
FILE_NAME = "demo_data_region_balloon_10s_500Hz_larterbreakspear"
LOG.info("Saving array to %s..." % FILE_NAME)
numpy.save(FILE_NAME + '.npy', bold_data.data)
numpy.save(FILE_NAME+'_time.npy', bold_data.time)

###EoF###