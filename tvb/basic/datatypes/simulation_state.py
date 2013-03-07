# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2013, all rights reserved.
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
DataType for storing a simulator's state in files and as DB reference.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""


import tvb.basic.traits.types_basic as basic
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.datatypes.arrays as arrays


class SimulationState(MappedType):
    """
    Simulation State, prepared for H5 file storage.
    """  
    
    # History Array
    history = arrays.FloatArray(required=False)
    # Simulator step number
    current_step = basic.Integer()
    # Array with _stock array for every monitor configured in current simulation.
    # As the monitors are dynamic, we prepare a bunch of arrays for storage in H5 file.
    monitor_stock_1 = arrays.FloatArray(required=False)
    monitor_stock_2 = arrays.FloatArray(required=False)
    monitor_stock_3 = arrays.FloatArray(required=False)
    monitor_stock_4 = arrays.FloatArray(required=False)
    monitor_stock_5 = arrays.FloatArray(required=False)
    monitor_stock_6 = arrays.FloatArray(required=False)
    monitor_stock_7 = arrays.FloatArray(required=False)
    monitor_stock_8 = arrays.FloatArray(required=False)
    monitor_stock_9 = arrays.FloatArray(required=False)
    monitor_stock_10 = arrays.FloatArray(required=False)
    monitor_stock_11 = arrays.FloatArray(required=False)
    monitor_stock_12 = arrays.FloatArray(required=False)
    monitor_stock_13 = arrays.FloatArray(required=False)
    monitor_stock_14 = arrays.FloatArray(required=False)
    monitor_stock_15 = arrays.FloatArray(required=False)
    
    
    def __init__(self, **kwargs):
        """ 
        Constructor for Simulator State
        """
        super(SimulationState, self).__init__(**kwargs)
        self.visible = False
    
    
    def populate_from(self, simulator_algorithm):
        """
        Prepare a state for storage from a Simulator object.
        """
        self.history = simulator_algorithm.history
        self.current_step = simulator_algorithm.current_step
        
        i = 1
        for monitor in simulator_algorithm.monitors:
            field_name = "monitor_stock_" + str(i)
            setattr(self, field_name, monitor._stock)
            if hasattr(monitor, "_ui_name"):
                self.set_metadata({'monitor_name': monitor._ui_name}, field_name)
            else:
                self.set_metadata({'monitor_name': monitor.__class__.__name__}, field_name)
            i = i + 1
        
    
    def fill_into(self, simulator_algorithm):
        """
        Populate a Simulator object from current stored-state.
        """
        simulator_algorithm.history = self.history 
        simulator_algorithm.current_step = self.current_step
        
        i = 1
        for monitor in simulator_algorithm.monitors:
            monitor._stock = getattr(self, "monitor_stock_" + str(i))
            i = i + 1
  
    
 