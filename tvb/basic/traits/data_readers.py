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
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import os
import numpy
from scipy import io as scipy_io
from tvb.basic.logger.logger import getLogger
from tvb.core.utils import read_list_data
from tvb.config import TVBSettings



class File(object):
    """
    will be used for setting default values, when console-mode.
    """
    
    def __init__(self, path, name=None):
        import tvb.simulator
        root_path = os.path.dirname(tvb.simulator.__file__)
        self.path = os.path.join(root_path, 'files', path)
        self.name = name
        self.logger = getLogger(self.__class__.__module__)
    
    
    def read_data(self, name=None, matlab_data_name=None,
                  dtype=numpy.float64, skiprows=0, usecols=None):
        """
        Read from given file.
        """
        if TVBSettings.TRAITS_CONFIGURATION.use_storage:
            # We want to avoid reading files when no console-mode is used.
            return None
        if name is not None:
            self.name = name
        full_path = os.path.join(self.path, self.name)
        self.logger.debug("Starting to read from: " + str(full_path))
        # Try to read Numpy
        if full_path.endswith('.txt') or full_path.endswith('.txt.bz2'):
            return read_list_data(full_path, dtype=dtype, skiprows=skiprows, usecols=usecols)
        if full_path.endswith('.npz'):
            return self._read_npz(full_path)
        
        # Try to read Matlab format
        return self._read_matlab(full_path, matlab_data_name)
        
    
        
    def _read_npz(self, full_path):
        return numpy.load(full_path)
    
    
    def _read_matlab(self, path, matlab_data_name=None):
        """
        Read array from file.
        """
        if path.endswith(".mtx"):
            return scipy_io.mmread(path)
        
        if path.endswith(".mat"):
            try:
                matlab_data = scipy_io.matlab.loadmat(path)
            except NotImplementedError, exc:
                self.logger.error("Could not read Matlab content from: " + path)
                self.logger.error("Matlab files must be saved in a format <= -V7...")
                raise exc
            return matlab_data[matlab_data_name]


    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self
    
    
    
    
