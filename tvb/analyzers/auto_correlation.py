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

"""
Calculate a ... on a .. datatype and return a ...

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy
#TODO: Currently built around the Simulator's 4D timeseries -- generalise...
import tvb.datatypes.time_series as time_series
import tvb.basic.traits.core as core
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)



class AutoCorrelation(core.Type):
    """
    Compute the auto-correlation of the given input 4D TimeSeries datatype.
    
    Return a number_of_nodes-by-number_of_nodes auto-correlation matrix. 
    """
    
    time_series = time_series.TimeSeries(
        label = "Time Series",
        required = True,
        doc = """The timeseries on which the auto-correlation is calculated.""")
    
    
    def evaluate(self):
        """
        Auto-correlate two one-dimensional arrays.
        """
        
        self.time_series.trait["data"].log_debug(owner=self.__class__.__name__+".time_series")
    
        data_shape = self.time_series.data.shape
        result_shape = data_shape
        
        #Base-line correct the segmented time-series
        time_series = self.time_series.data
        time_series = time_series - time_series.mean(axis=0)[numpy.newaxis, :]
        util.log_debug_array(LOG, time_series, "time_series")
        
        result = numpy.zeros(result_shape)
        for var in range(data_shape[1]):
            for node in range(data_shape[2]):
                for mode in range(data_shape[3]):
                    x = time_series[:, var, node, mode]
                    #import pdb; pdb.set_trace()
                    result[:, var, node, mode] = numpy.correlate(x, x, mode="full")[(result_shape[0]-1):]
        
        util.log_debug_array(LOG, result, "result")
        
        return result
