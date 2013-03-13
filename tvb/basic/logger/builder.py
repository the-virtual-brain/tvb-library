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
Singleton logging builder.


.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import os
import logging.config 
from tvb.basic.profile import TvbProfile
from tvb.basic.config.settings import TVBSettings  


class LoggerBuilder(object):
    """
    Class taking care of uniform Python logger initialization. 
    It uses the Python native logging package. 
    It's purpose is just to offer a common mechanism for initializing all modules in a package.
    """

    def __init__(self, config_root):
        """
        Prepare Python logger based on a configuration file.
        :param: config_root - current package to configure logger for it.
        """
        
        config_file_name = TVBSettings.LOGGER_CONFIG_FILE_NAME
        package = __import__(config_root, globals(), locals(), ['__init__'], 0)
        package_path = package.__path__[0]
        
        #Specify logging configuration file for current package. 
        logging.config.fileConfig(os.path.join(package_path, config_file_name), 
                                  disable_existing_loggers = True)

    @staticmethod
    def build_logger(parent_module):
        """
        Build a logger instance and return it
        """
        return logging.getLogger(parent_module)



### We make sure a single instance of logger-builder is created.
if "GLOBAL_LOGGER_BUILDER" not in globals():
    
    if TvbProfile.is_library_mode():
        GLOBAL_LOGGER_BUILDER = LoggerBuilder('tvb.basic.logger')
    else:
        GLOBAL_LOGGER_BUILDER = LoggerBuilder('tvb.config.logger')

 
 
def get_logger(parent_module = ''):
    """
    Function to retrieve a new Python logger instance for current module.
    
    :param parent_module: module for which to create logger.
    """
    return GLOBAL_LOGGER_BUILDER.build_logger(parent_module)
   
    
