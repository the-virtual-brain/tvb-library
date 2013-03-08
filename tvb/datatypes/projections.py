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
    



