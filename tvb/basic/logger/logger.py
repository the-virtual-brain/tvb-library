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
This is the code used for displaying logging messages in an uniform way, from
the entire application.

Example usage::
    
    #At the top of a module:
    import tvb.basic.logger.logger as logger
    LOG = logger.getLogger(parent_module=__name__, config_root='tvb')
    
    #Then simply use it with:
    LOG.info('a meaningful message')
        
    #Or to achieve class level labelling (assuming Class.__str__ is defined):
    LOG.info('%s: a meaningful message' % str(self))

.. moduleauthor:: Calin Pavel <calin.pavel@codemart.ro>
.. moduleauthor:: Bogdan Neacsa <bogdan.neacsa@codemart.ro>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Marmaduke Woodman <mw@eml.cc>

"""

import os
import logging.config
from tvb.config import TVBSettings as cfg
    
#Currently for backward compatibility config_root defaults to 'tvb' and 
#comes as the second argument, this should probably be changed to config_root 
#as a non-optional first arg, then parent_module as an optional kwarg.
def getLogger(parent_module = '', config_root='tvb'):
    """
    Parent module is optional to specify and describes the module the logger was
    called from.
    :param parent_module: module for which to create logger.
    :param config_root: Deprecated - !!! THIS IS NOT USED ANYMORE !!!
    """
    return LOGGER_BUIDER.build_logger(parent_module)


class LoggerBuilder(object):
    """
    Class taking care of uniform Python logger initialization. It uses the 
    Python logging package. It's purpose is just to offer a common mechanism for 
    initializing all modules in a package.
    """

    def __init__(self, config_root):
        """
        Prepare Python logging, by specifying a configuration file for current
        package (config_root param).
        """
        
        config_file_name = cfg.LOGGER_CONFIG_FILE_NAME
        package = __import__(config_root, globals(), locals(), ['__init__'], 0)
        package_path = package.__path__[0]
        
        #Specify logging configuration file for current package. 
        logging.config.fileConfig(os.path.join(package_path, config_file_name), 
                                  disable_existing_loggers = True)


    def build_logger(self, parent_module):
        """ Build a logger instance and return it"""
        return logging.getLogger(parent_module)


if "LOGGER_BUIDER" not in globals():
    if cfg.TRAITS_CONFIGURATION.use_storage:
        LOGGER_BUIDER = LoggerBuilder('tvb.logger_config')
    else:
        LOGGER_BUILDER = LoggerBuilder('tvb.basic.logger.logger')
    
    
