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
Demonstrate using the simulator for a surface simulation, deterministic 
intergation.

``Run time``: approximately 30 seconds (workstation circa 2010).

``Memory requirement``: < 1 GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy

"""
import tvb.basic.logger.logger as logger
LOG = logger.getLogger(__name__)

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.noise as noise
import tvb.simulator.monitors as monitors

import tvb.datatypes.connectivity as connectivity
import tvb.datatypes.surfaces as surfaces

from matplotlib.pyplot import *
from tvb.simulator.plot.tools import *
"""

from tvb.simulator.lab import *

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

#Initialise a Model, Coupling, and Connectivity.
rfhn = models.ReducedSetFitzHughNagumo()
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=0.0043) #0.0066

#Initialise an Integrator
hiss = noise.Additive(nsig = numpy.array([2**-16,]))
heunint = integrators.HeunStochastic(dt=2**-4, noise=hiss)

#Initialise some Monitors with period in physical time
mon_tavg = monitors.TemporalAverage(period=2**-2)
mon_savg = monitors.SpatialAverage(period=2**-2)
mon_eeg = monitors.EEG(period=2**-2)

#Bundle them
what_to_watch = (mon_tavg, mon_savg, mon_eeg)

#Initialise a surface
default_cortex = surfaces.Cortex()
default_cortex.coupling_strength = numpy.array([0.1835])

#Initialise Simulator -- Model, Connectivity, Integrator, Monitors, and surface.
sim = simulator.Simulator(model = rfhn, connectivity = white_matter, 
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch, 
                          surface = default_cortex)

sim.configure()

#Clear initial transient
LOG.info("Inital run to clear transient...")
for _, _, _ in sim(simulation_length=2**6):
    pass
LOG.info("Finished inital run to clear transient.")


#Perform the simulation
tavg_data = []
tavg_time = []
savg_data = []
savg_time = []
eeg_data = []
eeg_time = []
for tavg, savg, eeg in sim(simulation_length=2**6):
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])

    if not savg is None:
        savg_time.append(savg[0])
        savg_data.append(savg[1])
        
    if not eeg is None:
        eeg_time.append(eeg[0])
        eeg_data.append(eeg[1])

LOG.info("finished simulation")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##
    
#Make the lists numpy.arrays for easier use.
TAVG = numpy.array(tavg_data)
SAVG = numpy.array(savg_data)
EEG = numpy.array(eeg_data)

#Plot region averaged time series
figure(3)
plot(savg_time, SAVG[:, 0, :, 0])
title("Region average")

#Plot EEG time series
figure(4)
plot(eeg_time, EEG[:, 0, :, 0])
title("EEG")

show()

#Surface movie, requires mayavi.malb
if IMPORTED_MAYAVI:
    st = surface_timeseries(sim.surface, TAVG[:, 0, :, 0])

###EoF###