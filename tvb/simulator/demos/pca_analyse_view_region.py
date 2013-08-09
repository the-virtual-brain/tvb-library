# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
PCA analysis and visualisation demo.

``Run time``: approximately ? minutes (workstation circa 2010)

``Memory requirement``: ~ ?GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

import tvb.datatypes.connectivity as connectivity
from tvb.datatypes.time_series import TimeSeriesRegion

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


