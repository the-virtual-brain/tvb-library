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
This modeule contains different file handlers used to log messages
in different context and for different parts of application.
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler, MemoryHandler
from tvb.basic.config.config import TVBSettings as cfg

class SimpleTimedRotatingFileHandler(TimedRotatingFileHandler):  
    """
    This is a custom rotating file handler which computes the full path for log file 
    depending on the TVB configuration.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0):
        log_file =  os.path.join(cfg.TVB_LOG_FOLDER, filename)            
        TimedRotatingFileHandler.__init__(self, log_file, when, interval, backupCount)
        

class ClusterTimedRotatingFileHandler(MemoryHandler):
    # Name of the log file where code from Web application will be stored
    WEB_LOG_FILE = "web_application.log"
    
    # Name of the file where to write logs from the code executed on cluster nodes
    CLUSTER_NODES_LOG_FILE = "operations_executions.log"
    
    # Size of the buffer which store log entries in memory
    BUFFER_CAPACITY = 200 # log entries
    
    """
    This is a custom rotating file handler which computes the name of the file depending on the 
    execution environment (web node or cluster node)
    """
    def __init__(self, when='h', interval=1, backupCount=0):
        log_file = None
        # Formatter string
        format_str = '%(asctime)s - %(levelname)s'
        if cfg.OPERATION_EXECUTION_PROCESS:
            log_file =  os.path.join(cfg.TVB_LOG_FOLDER, self.CLUSTER_NODES_LOG_FILE)
            if cfg.RUNNING_ON_CLUSTER_NODE:
                node_name = cfg.CLUSTER_NODE_NAME
                if node_name is not None:
                    format_str += ' [node:' + node_name + '] '
            else:
                format_str += ' [proc:' + str(os.getpid()) + '] '
        else:
            log_file =  os.path.join(cfg.TVB_LOG_FOLDER, self.WEB_LOG_FILE)

        format_str += ' - %(name)s - %(message)s'
            
        rotating_file_handler = SimpleTimedRotatingFileHandler(log_file, when, interval, backupCount)
        rotating_file_handler.setFormatter(logging.Formatter(format_str))
        
        MemoryHandler.__init__(self, capacity = self.BUFFER_CAPACITY, target = rotating_file_handler)
        
        
        