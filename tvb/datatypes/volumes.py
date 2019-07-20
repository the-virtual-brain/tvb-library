# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
The Volume datatypes. This brings together the scientific and framework 
methods that are associated with the volume datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

from tvb.basic.logger.builder import get_logger
from tvb.basic.neotraits.api import HasTraits, Attr, NArray


LOG = get_logger(__name__)


class Volume(HasTraits):
    """
    Data defined on a regular grid in three dimensions.
    """
    origin = NArray(label="Volume origin coordinates")
    voxel_size = NArray(label="Voxel size") # need a triplet, xyz
    voxel_unit = Attr(str, label="Voxel Measure Unit", default="mm")

    def summary_info(self):
        return {
            "Volume type": self.__class__.__name__,
            "Origin": self.origin,
            "Voxel size": self.voxel_size,
            "Units": self.voxel_unit
        }

'''
Demonstrates plotting 3D volumetric objects with ``ax.voxels``
'''