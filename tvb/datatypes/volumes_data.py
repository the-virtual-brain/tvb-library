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
The Data component of Volumes datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.traits.types_basic as basic
import tvb.datatypes.arrays as arrays


class VolumeData(MappedType):
    """
    Data having voxels as their elementary units.
    """
    origin = arrays.PositionArray(label = "Volume origin coordinates")
    voxel_size = arrays.FloatArray(label = "Voxel size") # need a triplet, xyz
    voxel_unit = basic.String(label = "Voxel Measure Unit", default = "mm")


class ParcellationMaskData(VolumeData):
    """
    This mask provides the information to perform a subdivision (parcellation) 
    of the brain `Volume` of the desired subject into spatially compacts 
    clusters or parcels. 
    This subdivision is based on spatial coordinates and functional information, 
    in order to grant spatially consistent and functionally homogeneous units.
    """
    data = arrays.IndexArray(label = "Parcellation mask")
    region_labels = arrays.StringArray(label = "Region labels")


class StructuralMRIData(VolumeData):
    """
    Quantitative volumetric data recorded by means of Magnetic Resonance Imaging 
    """
    #TODO: Need data defined ?data = arrays.FloatArray(label = "?Contrast?") ?
    weighting = basic.String(label = "MRI weighting") # eg, "T1", "T2", "T2*", "PD", ...
