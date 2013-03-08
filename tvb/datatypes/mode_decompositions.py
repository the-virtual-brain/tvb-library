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
The Mode Decomposition datatypes. This brings together the scientific and 
framework methods that are associated with the Mode Decomposition datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import tvb.datatypes.mode_decompositions_scientific as mode_decompositions_scientific
import tvb.datatypes.mode_decompositions_framework as mode_decompositions_framework
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)


class PrincipalComponents(mode_decompositions_scientific.PrincipalComponentsScientific,
                          mode_decompositions_framework.PrincipalComponentsFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the PrincipalComponents datatype.
    
    ::
        
                            PrincipalComponentsData
                                     |
                                    / \\
        PrincipalComponentsFramework   PrincipalComponentsScientific
                                    \ /
                                     |
                              PrincipalComponents
        
    
    """
    pass


class IndependentComponents(mode_decompositions_scientific.IndependentComponentsScientific,
                            mode_decompositions_framework.IndependentComponentsFramework):
    """
    This class brings together the scientific and framework methods that are
    associated with the IndependentComponents datatype.
    
    ::
        
                            IndependentComponentsData
                                       |
                                      / \\
        IndependentComponentsFramework   IndependentComponentsScientific
                                      \ /
                                       |
                              IndependentComponents
        
    
    """
    pass



if __name__ == '__main__':
    # Do some stuff that tests or makes use of this module...
    LOG.info("Testing %s module..." % __file__)
    
    # Check that all default Mode Decomposition datatypes initialize without error.
    PRINCIPAL_COMPONENTS = PrincipalComponents()
    INDEPENDENT_COMPONENTS = IndependentComponents()
    
    LOG.info("Default Mode Decomposition datatypes initialized without error...")
