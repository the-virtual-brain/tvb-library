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
The Volume datatypes. This brings together the scientific and framework 
methods that are associated with the volume datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.basic.datatypes.volumes_scientific as volumes_scientific
import tvb.basic.datatypes.volumes_framework as volumes_framework


class Volume(volumes_scientific.VolumeScientific, 
             volumes_framework.VolumeFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Volume datatype.
    
    ::
        
                             VolumeData
                                 |
                                / \\
                 VolumeFramework   VolumeScientific
                                \ /
                                 |
                              Volume
        
    
    """
    pass


class ParcellationMask(volumes_scientific.ParcellationMaskScientific, 
                       volumes_framework.ParcellationMaskFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the ParcellationMask datatype.
    
    ::
        
                         ParcellationMaskData
                                  |
                                 / \\
        ParcellationMaskFramework   ParcellationMaskScientific
                                 \ /
                                  |
                           ParcellationMask
        
    
    """
    pass


class StructuralMRI(volumes_scientific.StructuralMRIScientific, 
                    volumes_framework.StructuralMRIFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the StructuralMRI datatype.
    
    ::
        
                         StructuralMRIData
                                 |
                                / \\
          StructuralMRIFramework   StructuralMRIScientific
                                \ /
                                 |
                           StructuralMRI
        
    
    """
    pass



if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Volume datatypes initialize without error.
    VOLUME = Volume()
    PARCELLATION_MASK = ParcellationMask()
    STRUCTURAL_MRI = StructuralMRI()
    
    LOG.info("Default Volume datatypes initialized without error...")

