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
The Sensors datatype. This brings together the scientific and framework 
methods that are associated with the sensor datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.datatypes.sensors_data as sensors_data
import tvb.datatypes.sensors_scientific as sensors_scientific
import tvb.datatypes.sensors_framework as sensors_framework


class Sensors(sensors_scientific.SensorsScientific,
              sensors_framework.SensorsFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Sensors datatype.
    
    ::
        
                            SensorsData
                                 |
                                / \\
                SensorsFramework   SensorsScientific
                                \ /
                                 |
                              Sensors
        
    
    """
    pass


class SensorsEEG(sensors_scientific.SensorsEEGScientific,
                 sensors_framework.SensorsEEGFramework, Sensors):
    """
    This class brings together the scientific and framework methods that are
    associated with the SensorsEEG datatype.
    
    ::
        
                           SensorsEEGData
                                 |
                                / \\
             SensorsEEGFramework   SensorsEEGScientific
                                \ /
                                 |
                             SensorsEEG
        
    
    """
    ## TODO try to make this happen behind the scene through Traits.core
    __mapper_args__ = {'polymorphic_identity': sensors_data.EEG_POLYMORPHIC_IDENTITY}


class SensorsMEG(sensors_scientific.SensorsMEGScientific,
                 sensors_framework.SensorsMEGFramework, Sensors):
    """
    This class brings together the scientific and framework methods that are
    associated with the SensorsMEG datatype.
    
    ::
        
                           SensorsMEGData
                                 |
                                / \\
             SensorsMEGFramework   SensorsMEGScientific
                                \ /
                                 |
                             SensorsMEG
        
    
    """
    ## TODO try to make this happen behind the scene through Traits.core
    __mapper_args__ = {'polymorphic_identity': sensors_data.MEG_POLYMORPHIC_IDENTITY}


class SensorsInternal(sensors_scientific.SensorsInternalScientific,
                      sensors_framework.SensorsInternalFramework, Sensors):
    """
    This class brings together the scientific and framework methods that are
    associated with the SensorsInternal datatype.
    
    ::
        
                        SensorsInternalData
                                 |
                                / \\
        SensorsInternalFramework   SensorsInternalScientific
                                \ /
                                 |
                          SensorsInternal
        
    
    """
    ## TODO try to make this happen behind the scene through Traits.core
    __mapper_args__ = {'polymorphic_identity': sensors_data.INTERNAL_POLYMORPHIC_IDENTITY}




if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Sensor datatypes initialize without error.
    SENSORS = Sensors()
    EEG_SENSORS = SensorsEEG()
    MEG_SENSORS = SensorsMEG()
    SENSORS_INTERNAL = SensorsInternal()
    
    LOG.info("Default Sensor datatypes initialized without error...")
