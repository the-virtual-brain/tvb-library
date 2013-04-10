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
The ProjectionMatrices DataTypes. This brings together the scientific and framework 
methods that are associated with the surfaces data.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import tvb.datatypes.projections_scientific as scientific
import tvb.datatypes.projections_framework as framework



class ProjectionMatrix(framework.ProjectionMatrixFramework, scientific.ProjectionMatrixScientific):
    """
    This class brings together the scientific and framework methods that are
    associated with the ProjectionMatrix DataType.
    
    ::
        
                        ProjectionMatrixData
                                 |
                                / \\
        ProjectionMatrixFramework   ProjectionMatrixScientific
                                \ /
                                 |
                            ProjectionMatrix
        
    
    """
    pass


    
class ProjectionRegionEEG(framework.ProjectionRegionEEGFramework, 
                          scientific.ProjectionRegionEEGScientific, ProjectionMatrix):
    """
    This class brings together the scientific and framework methods that are
    associated with the ProjectionMatrix DataType.
    
    ::
        
                          ProjectionRegionEEGData
                                     |
                                    / \\
        ProjectionRegionEEGFramework   ProjectionRegionEEGScientific
                                    \ /
                                     |
                           ProjectionRegionEEG
        
    
    """
    pass



class ProjectionSurfaceEEG(framework.ProjectionSurfaceEEGFramework, 
                           scientific.ProjectionSurfaceEEGScientific, ProjectionMatrix):
    """
    This class brings together the scientific and framework methods that are
    associated with the ProjectionMatrix DataType.
    
    ::
        
                          ProjectionSurfaceEEGData
                                      |
                                     / \\
        ProjectionSurfaceEEGFramework   ProjectionSurfaceEEGScientific
                                     \ /
                                      |
                          ProjectionSurfaceEEG
        
    
    """
    pass
    
