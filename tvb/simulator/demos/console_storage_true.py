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
Demo using console mode with storage.Note that consolde profile must have TRAITS_CONFIGURATION.use_storage = true before launching this.

.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
"""
import tvb.basic.config.settings as cfg
cfg.TVBSettings.TRAITS_CONFIGURATION.use_storage = True

# Need to atach db events so storage paths and traited attributes work properly
from tvb.core.traits import db_events
db_events.attach_db_events()

from tvb.core.entities.storage import dao
from tvb.core.services.operationservice import OperationService
from tvb.core.adapters.abcadapter import ABCAdapter
from tvb.core.entities.transient.filtering import FilterChain

import numpy
from tvb.simulator.lab import *

# We need a user and a project in order to run operations and store results
user = dao.get_user_by_name('admin')
project = dao.get_projects_for_user(user.id)[0]

# Here is an example of how one would launch a TVB adapter (in this case an uploader)
launcher = OperationService()
tmp_storage = "/home/bogdan.neacsa/TVB"
algo_group = dao.find_group('tvb.adapters.uploaders.zip_connectivity_importer', 'ZIPConnectivityImporter')
adapter = ABCAdapter.build_adapter(algo_group)
launch_args = {'uploaded' : '/home/bogdan.neacsa/Work/TVB/svn/tvb/trunk/demoData/connectivity/connectivity_regions_96.zip'}
launcher.initiate_operation(user, project.id, adapter, tmp_storage, **launch_args)
# Should get output: "Operation X has finished"  You can later on use X to get resulted datatypes if you want.

# Lets retrieve the connectivity based on the operation id (in this case 11) and change the subject on this connectivity
conn_result = dao.get_results_for_operation(11)[0]
conn_result.subject = "My fancy subject"
dao.store_entity(conn_result)

# Now let's get all the connectivities for our custom subject
from tvb.basic.datatypes.connectivity import Connectivity
dt_filter = FilterChain(fields = [FilterChain.datatype + '.subject'], operations = ["=="], values = ['My fancy subject'])
returned_values = dao.get_values_of_datatype(project.id, Connectivity, dt_filter)
LOG.info("Got from database values: %s" %(returned_values,))


# An example from the simulator demos run now with our connectivity we got above
# ----------------- ---------------------------------- -----------------
# ----------------- From generate region data demo below -----------------
# ----------------- ---------------------------------- -----------------
##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator(a=1.42)
white_matter = ABCAdapter.load_entity_by_gid(returned_values[0][2])   # You can also load a datatype if you have the gid or id of it.
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
for tavg in sim(simulation_length=1600):
    if tavg is not None:
        tavg_time.append(tavg[0][0]) #TODO:The first [0] is a hack for single monitor
        tavg_data.append(tavg[0][1]) #TODO:The first [0] is a hack for single monitor
        
# ----------------- ---------------------------------- -----------------
# ----------------- From generate region data demo ends ----------------
# ----------------- ---------------------------------- -----------------

# We have the data but it's still transient unless we store it in a timeseries
import tvb.basic.datatypes.time_series as time_series
# Using TimeSeriesRegion since that is what we got here
data_result = time_series.TimeSeriesRegion()
data_result.set_operation_id(1) # Need an operation. Maybe create a dummy one special for console mode?
data_result.connectivity = white_matter
data_result.write_data_slice(tavg_data)
data_result.write_time_slice(tavg_time)
data_result.close_file()
LOG.info("Saving simulator result to db.")
dao.store_entity(data_result)
LOG.info("Loading from db to check results are properly stored")
loaded_dt = ABCAdapter.load_entity_by_gid(data_result.gid)
LOG.info("Time shape is %s"%(loaded_dt.get_data_shape('time'),))
LOG.info("Data shape is %s"%(loaded_dt.get_data_shape('data'),))
LOG.info(loaded_dt.get_data('time'))
LOG.info(loaded_dt.get_data('data'))
