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
TVB-Simulator-Library global configurations are defined here.

Also the generic TVB-Configuration gets set from this point 
(dependent on the previously user-specified profile).
"""

import os
import sys
from sys import platform
from tvb.basic.config.utils import ClassProperty, EnhancedDictionary
from tvb.basic.profile import TvbProfile as tvb_profile


class LibraryProfile():
    """
    Profile needed at the level of TVB Simulator Library.
    It needs to respect a minimal pattern, common to all TVB available profiles.
    """
    
    ## Number used for estimation of TVB used storage space
    MAGIC_NUMBER = 9
    
    ## Maximum number of vertices accepted on a Surface object.
    ## Used for validation purposes.
    MAX_SURFACE_VERTICES_NUMBER = 300000
    
    ## Default value of folder where to store logging files.
    TVB_STORAGE = os.path.expanduser(os.path.join("~", "TVB" + os.sep))
    
    ## Temporary add-on used in DataTypes_Framework.
    ## When DataType_Framework classes will get moved, this should be removed.
    WEB_VISUALIZERS_URL_PREFIX = ""
    
    ## Way of functioning traits is different when using storage or not.
    ## Storage set to false is valid when using TVB_Simulator_Library stand-alone.
    TRAITS_CONFIGURATION = EnhancedDictionary()
    TRAITS_CONFIGURATION.interface_method_name = 'interface'
    TRAITS_CONFIGURATION.use_storage = False
    
    ## Name of file where logging configuration is stored.
    LOGGER_CONFIG_FILE_NAME = "library_logger.conf"
    
    
    @ClassProperty
    @staticmethod
    def TVB_LOG_FOLDER():
        """ Return a folder, where all log files are to be stored. """
        tmp_path = os.path.join(LibraryProfile.TVB_STORAGE, "logs")
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        return tmp_path
    
   
    
    @staticmethod
    def is_development():
        """Return True when TVB  is used with Python installed natively."""
        import tvb
        tvb_root = os.path.dirname(os.path.abspath(tvb.__file__))
        return (os.path.exists(os.path.join(tvb_root, 'demoData'))
                and os.path.exists(os.path.join(tvb_root, 'ui_test'))
                and os.path.exists(os.path.join(tvb_root, 'tvb_test')))

    
    @classmethod
    def initialize_profile(cls):
        """No initialization needed for this particular profile. But usefull in general"""
        pass
    
FRAMEWORK_PRESENT = True
try:
    import tvb.config as cfg
except ImportError:
    FRAMEWORK_PRESENT = False
###
###  Dependent of the selected profile. Load the correct configuration.
###    
if tvb_profile.CURRENT_SELECTED_PROFILE == tvb_profile.LIBRARY_PROFILE or FRAMEWORK_PRESENT == False:
    ## TVB-Simulator-Library is used stand-alone.
    ## Fallback to LibraryProfile either if this was the profile passed as argument or if TVB Framework is not present.
    TVBSettings = LibraryProfile
    
else:
    ## Initialization based on profile is further done in Framework.
    TVBSettings = cfg.FrameworkSettings
        
TVBSettings.initialize_profile()


