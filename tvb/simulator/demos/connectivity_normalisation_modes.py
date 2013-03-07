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
Demonstrate the effect of different normalisation ``modes`` on the connectivity
strength range. 

Current modes are re-scaling methods.

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Third party python libraries

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(__name__)

#Import from tvb.basic.datatypes modules:
import tvb.basic.datatypes.connectivity as connectivity

from matplotlib.pyplot import *
from tvb.simulator.plot.tools import *

LOG.info("Reading default connectivity...")

#Initialise a Connectivity object
white_matter = connectivity.Connectivity()
white_matter.configure()
con = connectivity.Connectivity()
con.configure()

#Normalise weights
con.weights = white_matter.normalised_weights(mode='tract')
plot_connectivity(con, num="tract_mode", plot_tracts=False)

#Undo normalisation
con.weights = white_matter.normalised_weights(mode='none')
plot_connectivity(con, num="default_mode", plot_tracts=False)

#Re-normalise using another `` mode``
con.weights = white_matter.normalised_weights(mode='region')
plot_connectivity(con, num="region_mode", plot_tracts=False)

pyplot.show()





