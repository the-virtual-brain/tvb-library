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
TVB global configurations are predefined/read from here.
"""
import os
from tvb.basic.config.utils import ClassProperty, EnhancedDictionary
from tvb.basic.profile import TvbProfile as tvb_profile


class LibraryProfile():

    MAGIC_NUMBER = 9
    
    MAX_SURFACE_VERTICES_NUMBER = 300000
    
    TVB_STORAGE = os.path.expanduser(os.path.join("~", "TVB" + os.sep))
    
    @ClassProperty
    @staticmethod
    def TVB_LOG_FOLDER():
        """ 
        Represents a folder, where all log files are stored.
        """
        tmp_path = os.path.join(LibraryProfile.TVB_STORAGE, "logs")
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        return tmp_path
    
    LOGGER_CONFIG_FILE_NAME = "library_logger.conf"
    
    TRAITS_CONFIGURATION = EnhancedDictionary()
    TRAITS_CONFIGURATION.use_storage = False
    
    def initialize_profile(self):
        pass
    
if tvb_profile.CURRENT_SELECTED_PROFILE == tvb_profile.LIBRARY_PROFILE:
    TVBSettings = LibraryProfile
else:
    import tvb.config as cfg
    TVBSettings = cfg.FrameworkSettings
        
TVBSettings.initialize_profile()
