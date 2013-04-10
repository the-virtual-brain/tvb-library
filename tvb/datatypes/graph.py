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

"""

The Graph datatypes. This brings together the scientific and framework methods
that are associated with the Graph datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.graph_scientific as graph_scientific
import tvb.datatypes.graph_framework as graph_framework
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class Covariance(graph_scientific.CovarianceScientific, graph_framework.CovarianceFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Covariance DataType.
    
    ::
        
                     CovarianceData
                            |
                           / \\
        CovarianceFramework   CovarianceScientific
                           \ /
                            |
                        Covariance
        
    
    """
    pass


class ConnectivityMeasure(graph_scientific.ConnectivityMeasureScientific,
                          graph_framework.ConnectivityMeasureFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the ConnectivityMeasure dataType.
    
    ::
        
                          ConnectivityMeasureData
                                     |
                                    / \\
         ConnectivityMeasureFramework   ConnectivityMeasureScientific
                                    \ /
                                     |
                          ConnectivityMeasure
        
    """
    pass

