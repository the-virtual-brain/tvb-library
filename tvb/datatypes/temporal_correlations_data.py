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

The Data component of Temporal Correlation datatypes.

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>
.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>

"""

from tvb.basic.traits import get_mapped_type
MappedType = get_mapped_type()
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.datatypes.arrays as arrays
import tvb.datatypes.time_series as time_series


class CrossCorrelationData(MappedType):
    """
    Result of a CrossCorrelation Analysis.
    """
    #Overwrite attribute from superclass
    array_data = arrays.FloatArray(file_storage = core.FILE_STORAGE_EXPAND)
    
    source = time_series.TimeSeries(
        label = "Source time-series",
        doc = """Links to the time-series on which the cross_correlation is
            applied.""")
    
    time = arrays.FloatArray(label = "Temporal Offsets")
    
    
    labels_ordering = basic.List(
        label = "Dimension Names",
        default = ["Offsets", "Node", "Node", "State Variable", "Mode"],
        doc = """List of strings representing names of each data dimension""")
    
    __generate_table__ = True

