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
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Demonstrate the effect of different normalisation ``modes`` on the connectivity
strength range. 

Current modes are re-scaling methods.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Third party python libraries

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

#Import from tvb.datatypes modules:
import tvb.datatypes.connectivity as connectivity

from matplotlib.pyplot import *
from tvb.simulator.plot.tools import *

LOG.info("Reading default connectivity...")

#Initialise a Connectivity object
white_matter = connectivity.Connectivity()
white_matter.configure()
con = connectivity.Connectivity()
con.configure()

#Normalise weights
con.weights = white_matter.normalised_weights(mode='tract')
plot_connectivity(con, num="tract_mode", plot_tracts=False)

#Undo normalisation
con.weights = white_matter.normalised_weights(mode='none')
plot_connectivity(con, num="default_mode", plot_tracts=False)

#Re-normalise using another `` mode``
con.weights = white_matter.normalised_weights(mode='region')
plot_connectivity(con, num="region_mode", plot_tracts=False)

pyplot.show()





