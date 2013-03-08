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
Demonstrate using the simulator at the region level with a stimulus.

``Run time``: approximately 7 min (workstation circa 2010).

``Memory requirement``: < 1GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy

# Try and import from "The Virtual Brain"
try:
    import tvb.basic.logger.logger as logger
    LOG = logger.getLogger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)
    LOG.warning("Failed to import TVB logger, using Python logging directly...")

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.monitors as monitors

import tvb.datatypes.connectivity as connectivity

import tvb.datatypes.equations as equations
import tvb.datatypes.patterns as patterns

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator() #ReducedSetHindmarshRose() #
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=0.0126)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=2**-4)

#Initialise some Monitors with period in physical time
momo = monitors.TemporalAverage(period=1.0) #1000Hz
mama = monitors.Bold(period=500) #defaults to one data point every 2s

#Bundle them
what_to_watch = (momo, mama)

#Define the stimulus
#Specify a weighting for regions to receive stimuli... 
white_matter.configure() # Because we want access to number_of_regions
nodes = [0, 7, 13, 33, 42]
weighting = numpy.zeros((white_matter.number_of_regions, )) #1
weighting[nodes] = numpy.array([2.0**-2, 2.0**-3, 2.0**-4, 2.0**-5, 2.0**-6]) # [:, numpy.newaxis]

eqn_t = equations.Gaussian()
eqn_t.parameters["midpoint"] = 15000.0
eqn_t.parameters["sigma"] = 4.0

stimulus = patterns.StimuliRegion(temporal = eqn_t,
                                  connectivity = white_matter, 
                                  weight = weighting)

#Initialise Simulator -- Model, Connectivity, Integrator, Monitors, and stimulus.
sim = simulator.Simulator(model = oscilator, connectivity = white_matter, 
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch, 
                          stimulus = stimulus) # surface=default_cortex, 

sim.configure()


LOG.info("Starting simulation...")
#Perform the simulation
tavg_time = []
tavg_data = []
bold_time = []
bold_data = []
for tavg, bold in sim(simulation_length=30000):
    
    if not tavg is None:
       tavg_time.append(tavg[0])
       tavg_data.append(tavg[1])
    
    if not bold is None:
        bold_time.append(bold[0])
        bold_data.append(bold[1])

LOG.info("Finished simulation.")

###EoF###
