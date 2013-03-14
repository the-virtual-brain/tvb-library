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
The Data component of Sensors datatypes, for the moment just EEG and MEG,
however, ECoG, depth electrodes, etc should be supported...

Sensors uses:
    locations and labels for visualisation
    combined with source and head surfaces to generate projection matrices used
    in monitors such as EEG, MEG...

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

from tvb.basic.traits.types_mapped import MappedType
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.data_readers as readers
import tvb.datatypes.arrays as arrays


EEG_POLYMORPHIC_IDENTITY = "EEG"
MEG_POLYMORPHIC_IDENTITY = "MEG"
INTERNAL_POLYMORPHIC_IDENTITY = "Internal"



class SensorsData(MappedType):
    """
    Base Sensors class.
    All sensors have locations. 
    Some will have orientations, e.g. MEG.
    
    """
    _ui_name = "Unknown sensors" 
    
    sensors_type = basic.String
    
    __mapper_args__ = {'polymorphic_on': 'sensors_type'}
    
    default = readers.File(folder_path = "sensors", file_name = 'EEG_unit_vectors_BrainProducts_62.txt.bz2')
    
    labels = arrays.StringArray(
        label = "Sensor labels",
        console_default = default.read_data(usecols = (0,), dtype = "string", field = "labels"))
    
    locations = arrays.PositionArray(
        label = "Sensor locations",
        console_default = default.read_data(usecols = (1,2,3), field = "locations"))
    
    has_orientation = basic.Bool(default = False)
    
    orientations = arrays.OrientationArray(required = False)
    
    number_of_sensors = basic.Integer(
        label = "Number of sensors",
        doc = """The number of sensors described by these Sensors.""")



class SensorsEEGData(SensorsData):
    """
    EEG sensor locations are represented as unit vectors, these need to be
    combined with a head(outer-skin) surface to obtain actual sensor locations
    ::
        
                              position
                                 |
                                / \\
                               /   \\
        file columns: labels, x, y, z
        
    """
    _ui_name = "EEG Sensors"
    
    __tablename__ = None
    
    __mapper_args__ = {'polymorphic_identity': EEG_POLYMORPHIC_IDENTITY}
    
    sensors_type = basic.String(default = EEG_POLYMORPHIC_IDENTITY)
    
    has_orientation = basic.Bool(default = False, order = -1)


    def __init__(self, **kwargs):
        super(SensorsEEGData, self).__init__(**kwargs)
        self.default.reload(self.__class__, folder_path = "sensors", 
                            file_name = "EEG_unit_vectors_BrainProducts_62.txt.bz2")



class SensorsMEGData(SensorsData):
    """
    These are actually just SQUIDS. Axial or planar gradiometers are achieved
    by calculating lead fields for two sets of sensors and then subtracting...
    ::
        
                              position  orientation
                                 |           |
                                / \         / \\
                               /   \       /   \\
        file columns: labels, x, y, z,   dx, dy, dz
        
    """
    _ui_name = "MEG sensors"
    
    __tablename__ = None
    
    __mapper_args__ = {'polymorphic_identity': MEG_POLYMORPHIC_IDENTITY}
    
    sensors_type = basic.String(default = MEG_POLYMORPHIC_IDENTITY)
    
    orientations = arrays.OrientationArray(
        label = "Sensor orientations",
        console_default = SensorsData.default.read_data(usecols = (4,5,6), field = "orientations", lazy_load = True),
        doc = "An array representing the orientation of the MEG SQUIDs")
    
    has_orientation = basic.Bool(default = True, order = -1)

    def __init__(self, **kwargs):
        super(SensorsMEGData, self).__init__(**kwargs)
        self.default.reload(self.__class__, folder_path = "sensors", file_name = "meg_channels_reg13.txt.bz2")



class SensorsInternalData(SensorsData):
    """
    Sensors inside the brain...
    """
    _ui_name = "Internal Sensors"
    
    __tablename__ = None
    
    __mapper_args__ = {'polymorphic_identity': INTERNAL_POLYMORPHIC_IDENTITY}
    
    sensors_type = basic.String(default = INTERNAL_POLYMORPHIC_IDENTITY)



