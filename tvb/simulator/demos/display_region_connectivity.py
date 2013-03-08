# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution or commercial re-sale is permitted.
# Neither the name of Baycrest nor the names of its contributors may be used to endorse or promote
# products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.”
#
#
"""
Plot regions and connection edges.
Xmas balls scaled is in the range [0 - 1], representing
the cumulative input to each region.


.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

import tvb.datatypes.connectivity as connectivity
from tvb.simulator.plot.tools import *


##----------------------------------------------------------------------------##
##-                      Load the object                                     -##
##----------------------------------------------------------------------------##

white_matter = connectivity.Connectivity()

#Compute cumulative input for each region
node_data = white_matter.weights.sum(axis=1)
scaling_factor = node_data.max()

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

if IMPORTED_MAYAVI:
    xmas_balls(white_matter, node_data / scaling_factor,  edge_data=True)
    
###EoF###