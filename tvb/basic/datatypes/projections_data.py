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
The Data component of ProjectionMatrices DataTypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart Knock <stuart.knock@gmail.com>
"""

import tvb.basic.traits.types_basic as basic
from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.datatypes.arrays as arrays
import tvb.basic.datatypes.surfaces as surfaces_module
import tvb.basic.datatypes.sensors as sensors_module
import tvb.basic.datatypes.connectivity as connectivity_module



class ProjectionMatrixData(MappedType):
    """
    Base DataType for representing a ProjectionMatrix.
    The projection is between a source of type Connectivity regions or Surface and a set of Sensors.
    """
    
    sources = MappedType(label = "surface or region",
                                default = None, required = True)
    
    
    ## We can not use base class sensors here due to polymorphic selection
    sensors = MappedType(label = "Sensors", default = None, required = False,
                                doc = """ A set of sensors to compute projection matrix for them. """)
    
    projection_data = arrays.FloatArray(label = "Projection Matrix Data",
                                        default = None, required = True)
     
     
    #size = basic.Integer(label = "dummy", default = int(1))
    
    

class ProjectionRegionEEGData(ProjectionMatrixData):
    """
    Specific projection, from a Connectivity Regions to EEG Sensors,
    """
    sensors = sensors_module.SensorsEEG
    
    sources = connectivity_module.Connectivity
    
    __tablename__ = None
    

class ProjectionSurfaceEEGData(ProjectionMatrixData):
    """
    Specific projection, from a CorticalSurface to EEG sensors.
    """

    brain_skull = surfaces_module.BrainSkull(label = "Brain Skull", default = None, required = False,
                                             doc = """Boundary between skull and cortex domains.""")
        
    skull_skin = surfaces_module.SkullSkin(label = "Skull Skin", default = None, required = False,
                                           doc = """Boundary between skull and skin domains.""")
        
    skin_air = surfaces_module.SkinAir( label = "Skin Air", default = None, required = False,
                                        doc = """Boundary between skin and air domains.""")
    
    conductances = basic.Dict(label = "Domain conductances", required = False,
                              default = {'air': 0.0, 'skin': 1.0, 'skull': 0.01, 'brain': 1.0},
                              doc = """ A dictionary representing the conductances of ... """)    
    
    sensors = sensors_module.SensorsEEG
    
    sources = surfaces_module.CorticalSurface
    
    
class ProjectionRegionMEGData(ProjectionMatrixData):
    """
    Specific projection, from a Connectivity datatype to a MEGSensors datatype,
    .. warning :: PLACEHOLDER
    
    """
    sensors = sensors_module.SensorsMEG
    
    sources = connectivity_module.Connectivity
    
    __tablename__ = None
    
    
class ProjectionSurfaceMEGData(ProjectionMatrixData):
    """
    Specific projection, from a CorticalSurface to MEG sensors.
    ... warning :: PLACEHOLDER
    """

    brain_skull = surfaces_module.BrainSkull(label = "Brain Skull", default = None, required = False,
                                             doc = """Boundary between skull and cortex domains.""")
        
    skull_skin = surfaces_module.SkullSkin(label = "Skull Skin", default = None, required = False,
                                           doc = """Boundary between skull and skin domains.""")
        
    skin_air = surfaces_module.SkinAir( label = "Skin Air", default = None, required = False,
                                        doc = """Boundary between skin and air domains.""")
    
    conductances = basic.Dict(label = "Domain conductances", required = False,
                              default = {'air': 0.0, 'skin': 1.0, 'skull': 0.01, 'brain': 1.0},
                              doc = """ A dictionary representing the conductances of ... """)    
    
    sensors = sensors_module.SensorsMEG
    
    sources = surfaces_module.CorticalSurface
    
    
    
    
    
    