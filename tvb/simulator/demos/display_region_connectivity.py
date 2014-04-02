# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.0O0010)
#
#

"""
Plot regions and connection edges.
Xmas balls scaled is in the range [0 - 1], representing
the cumulative input to each region.


.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

import tvb.datatypes.connectivity as connectivity
from tvb.simulator.plot.tools import *
import os

##----------------------------------------------------------------------------##
##-                      Load the object                                     -##
##----------------------------------------------------------------------------##

white_matter = connectivity.Connectivity()
white_matter.default.reload(white_matter, folder_path=os.path.join("connectivity", "hagmann_hemisphere_both_subcortical_false_998"))


#Compute cumulative input for each region
node_data = numpy.ones(998)#white_matter.weights.sum(axis=1)
node_size = node_data

labels_indices = numpy.loadtxt('../files/connectivity/hagmann_hemisphere_both_subcortical_false_998/raw_order_label_indices.txt')
lesion_centres = (numpy.array([57, 86, 138, 162, 194, 247, 308, 323, 360, 439, 472, 555, 584, 636, 662, 692, 746, 810, 821, 856, 938, 971]) -1).astype(int)
node_data[lesion_centres] = 5.


##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

if IMPORTED_MAYAVI:
    xmas_balls(white_matter, node_data= node_data, edge_data=False, labels=True, labels_indices=lesion_centres)
    
###EoF###