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
Scientific methods for the Temporal Correlation datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(__name__)

import tvb.datatypes.temporal_correlations_data as temporal_correlations_data



class CrossCorrelationScientific(temporal_correlations_data.CrossCorrelationData):
    """ This class exists to add scientific methods to CrossCorrelationData. """
    __tablename__ = None
    
    
    def _find_summary_info(self):
        """
        Gather scientifically interesting summary information from an instance
        of this datatype.
        """
        summary = {"Temporal correlation type": self.__class__.__name__}
        summary["Source"] = self.source.title
        summary["Dimensions"] = self.labels_ordering
        #summary["Dimensions"] = ["Offsets", "Node", "Node","State Variable", "Mode"]
        summary.update(self.get_info_about_array('array_data'))
        return summary



