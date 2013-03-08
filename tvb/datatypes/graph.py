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

The Graph datatypes. This brings together the scientific and framework methods
that are associated with the Graph datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(parent_module=__name__)

import tvb.datatypes.graph_scientific as graph_scientific
import tvb.datatypes.graph_framework as graph_framework


class Covariance(graph_scientific.CovarianceScientific,
                 graph_framework.CovarianceFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the Covariance datatype.
    
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



if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Graph datatypes initialize without error.
    COVARIANCE = Covariance()
    
    LOG.info("Default Graph datatypes initialized without error...")
