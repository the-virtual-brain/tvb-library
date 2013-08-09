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

The Connectivity datatype. This brings together the scientific and framework 
methods that are associated with the connectivity data.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.connectivity_scientific as connectivity_scientific
import tvb.datatypes.connectivity_framework as connectivity_framework
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class Connectivity(connectivity_scientific.ConnectivityScientific, connectivity_framework.ConnectivityFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Connectivity dataType.
    
    ::
        
                          ConnectivityData
                                 |
                                / \\
          ConnectivityFramework     ConnectivityScientific
                                \ /
                                 |
                            Connectivity
        
    
    """
    #TODO: Do we want to do something like the following here???
    #ui_label = "Long-range structural connectivity"
    #ui_doc = """ The long range structural connectivity represents the a 
    #    particular parcellation of the brain into regions. For this parcellation
    #    a set of properties are then defined. These are typically extracted, via
    #    methods such as DSI, for individual subjects. They include things such 
    #    as the strenth of connection between regions, the length of white matter
    #    tracts connecting reions ... ete,etc, blah, blah"""
    pass

