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
#   The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Filler analyzer: Takes a TimeSeries object and returns two Floats.


These metrics are described and used in:

Hellyer et al. The Control of Global Brain Dynamics: Opposing Actions
of Frontoparietal Control and Default Mode Networks on Attention. 
The Journal of Neuroscience, January 8, 2014,  34(2):451– 461

Proxy metastability: the variability in spatial coherence of the signal
globally or locally (within a network) over time.

.. moduleauthor:: Paula Sanz Leon <paula.sanz-leon@univ-amu.fr>

"""

import tvb.analyzers.metrics_base as metrics_base
from tvb.basic.logger.builder import get_logger


LOG = get_logger(__name__)



class ProxyMetastabilitySynchrony(metrics_base.BaseTimeseriesMetricAlgorithm):
    """
    Subtract the mean time-series and compute. 

    Input:
    TimeSeries DataType
    
    Output: 
    Float, Float
    
    The two metrics given by this analyzers are a proxy for metastability and synchrony. 
    The underlying dynamical model used in the article was the Kuramoto model.

    .. math:
            V(t) = \frac{1}{N} \sum_{i=1}^{N} |S_i(t) - <S(t)>|


    """

    def evaluate(self):
        """
        Compute the zero centered variance of node variances for the time_series.
        """
        cls_attr_name = self.__class__.__name__ + ".time_series"
        self.time_series.trait["data"].log_debug(owner=cls_attr_name)
        
        shape = self.time_series.data.shape
        tpts  = shape[0]

        if self.start_point != 0.0:
            start_tpt = self.start_point / self.time_series.sample_period
            LOG.debug("Will discard: %s time points" % start_tpt)
        else: 
            start_tpt = 0

        if start_tpt > tpts:
            LOG.warning("The time-series is shorter than the starting point")
            LOG.debug("Will divide the time-series into %d segments." % self.segment)
            # Lazy strategy
            start_tpt = int((self.segment - 1) * (tpts//self.segment))

        av_mean_data = abs(self.time_series.data[start_tpt:, :] - self.time_series.data[start_tpt:, :].mean(axis=2, keepdims=True)).mean(axis=2)
        #std across time-points
        metastability = float(av_mean_data.std(axis=0).squeeze())
        synchrony     = 1./ av_mean_data.mean(axis=0).squeeze()
        return metastability, synchrony

