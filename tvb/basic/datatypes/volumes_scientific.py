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
Scientific methods for the Volume datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.datatypes.volumes_data as volumes_data


class VolumeScientific(volumes_data.VolumeData):
    """ This class exists to add scientific methods to VolumeData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Volume type": self.__class__.__name__}
        summary["Origin"] = self.origin
        summary["Voxel size"] = self.voxel_size
        summary["Units"] = self.voxel_unit
        return summary


class ParcellationMaskScientific(volumes_data.ParcellationMaskData,
                                 VolumeScientific):
    """ This class exists to add scientific methods to ParcellationMaskData. """
    
    
    def _find_summary_info(self):
        """ Extend the base class's summary dictionary. """
        summary = super(ParcellationMaskScientific, self)._find_summary_info()
        summary["Volume shape"] = self.get_data_shape('data')
        summary["Number of regions"] = self.get_data_shape('region_labels')[0]
        return summary


class StructuralMRIScientific(volumes_data.StructuralMRIData,
                              VolumeScientific):
    """ This class exists to add scientific methods to StructuralMRIData. """
    pass

