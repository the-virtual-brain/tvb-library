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
Generate 16 seconds of 2048Hz data at the region level, stochastic integration.

``Run time``: approximately 4 minutes (workstation circa 2010)

``Memory requirement``: < 1GB
``Storage requirement``: ~ 19MB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy

"""
from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.noise as noise
import tvb.simulator.monitors as monitors

import tvb.datatypes.connectivity as connectivity
"""

from tvb.simulator.lab import *
##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator(a=1.42)
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=0.016)

#Initialise an Integrator
hiss = noise.Additive(nsig = numpy.array([2**-10,]))
heunint = integrators.HeunStochastic(dt=0.06103515625, noise=hiss) 

#Initialise a Monitor with period in physical time
what_to_watch = monitors.TemporalAverage(period=0.48828125) #2048Hz => period=1000.0/2048.0

#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
sim = simulator.Simulator(model = oscilator, connectivity = white_matter, 
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch)

sim.configure()

#Perform the simulation
tavg_data = []
tavg_time = []
LOG.info("Starting simulation...")
for tavg in sim(simulation_length=16000):
    if tavg is not None:
        tavg_time.append(tavg[0][0]) #TODO:The first [0] is a hack for single monitor
        tavg_data.append(tavg[0][1]) #TODO:The first [0] is a hack for single monitor

LOG.info("Finished simulation.")


##----------------------------------------------------------------------------##
##-                     Save the data to a file                              -##
##----------------------------------------------------------------------------##

#Make the list a numpy.array.
LOG.info("Converting result to array...")
TAVG = numpy.array(tavg_data)

#Save it
FILE_NAME = "demo_data_region_16s_2048Hz.npy"
LOG.info("Saving array to %s..." % FILE_NAME)
numpy.save(FILE_NAME, TAVG)

LOG.info("Done.")

###EoF###