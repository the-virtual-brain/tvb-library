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

The Framework component of ProjectionMatrices DataTypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import tvb.datatypes.projections_data as data


class ProjectionMatrixFramework(data.ProjectionMatrixData):
    """ This class exists to add framework methods to ProjectionMatrixData. """
    __tablename__ = None
    

    
class ProjectionRegionEEGFramework(data.ProjectionRegionEEGData):
    """ This class exists to add framework methods to ProjectionRegionEEGData. """
    __tablename__ = None
    
    def generate_new_projection(self, connectivity_gid, storage_path):
        """
        Generate a new projection matrix with the given connectivity gid from an 
        existing Region Projection corresponding to the parent connectivity.
        """
        new_projection = self.__class__()
        new_projection.storage_path = storage_path
        new_projection._sources = connectivity_gid
        new_projection._sensors = self._sensors
        new_projection.projection_data = self.projection_data
        return new_projection



class ProjectionSurfaceEEGFramework(data.ProjectionSurfaceEEGData):
    """ This class exists to add framework methods to ProjectionSurfaceEEGData. """
    __tablename__ = None