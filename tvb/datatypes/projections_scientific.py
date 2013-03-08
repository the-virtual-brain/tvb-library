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

The Scientific component of ProjectionMatrices DataTypes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart Knock <stuart.knock@gmail.com>

"""
import tvb.datatypes.projections_data as data


class ProjectionMatrixScientific(data.ProjectionMatrixData):
    """ This class exists to add scientific methods to ProjectionMatrixData. """
    __tablename__ = None
   
    
    
class ProjectionRegionEEGScientific(data.ProjectionRegionEEGData):
    """ This class exists to add scientific methods to ProjectionRegionEEGData. """
    pass



class ProjectionSurfaceEEGScientific(data.ProjectionSurfaceEEGData):
    """ This class exists to add scientific methods to ProjectionSurfaceEEGData. """
    __tablename__ = None
    
        
        