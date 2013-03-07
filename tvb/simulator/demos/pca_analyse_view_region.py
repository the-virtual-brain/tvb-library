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
PCA analysis and visualisation demo.

``Run time``: approximately ? minutes (workstation circa 2010)

``Memory requirement``: ~ ?GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

import tvb.basic.logger.logger as logger
LOG = logger.getLogger(__name__)

import tvb.basic.datatypes.connectivity as connectivity
from tvb.basic.datatypes.time_series import TimeSeriesRegion

import tvb.analyzers.pca  as pca

from tvb.simulator.plot import timeseries_interactive as timeseries_interactive
from tvb.simulator.plot.tools import *

#Load the demo region timeseries dataset 
try:
    data = numpy.load("demo_data_region_16s_2048Hz.npy")
except IOError:
    LOG.error("Can't load demo data. Run demos/generate_region_demo_data.py")
    raise

period = 0.00048828125 #s

#Put the data into a TimeSeriesRegion datatype
white_matter = connectivity.Connectivity()
tsr = TimeSeriesRegion(connectivity = white_matter, 
                       data = data,
                       sample_period = period)
tsr.configure()

#Create and run the analyser
pca_analyser = pca.PCA(time_series = tsr)
pca_data = pca_analyser.evaluate()

#Generate derived data, such as, compnent time series, etc.
pca_data.configure()

#Put the data into a TimeSeriesSurface datatype
component_tsr = TimeSeriesRegion(connectivity = white_matter,
                                 data = pca_data.component_time_series,
                                 sample_period = period)
component_tsr.configure()

#Prutty puctures...
tsi = timeseries_interactive.TimeSeriesInteractive(time_series = component_tsr)
tsi.configure()
tsi.show()

if IMPORTED_MAYAVI:
    xmas_balls(tsr.connectivity, pca_data.weights[:, 0, 0, 0], edge_data=True)


