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
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

Define what Analyzers classes will be included in the UI / Online help 
documentation. Python docstring from the classes listed below will be included.

"""

import tvb.analyzers.cross_correlation as cross_correlation
import tvb.analyzers.fft as fft
import tvb.analyzers.ica as ica
import tvb.analyzers.pca as pca
import tvb.analyzers.node_coherence as node_coherence
import tvb.analyzers.node_complex_coherence as node_complex_coherence
import tvb.analyzers.node_covariance as node_covariance
import tvb.analyzers.metric_kuramoto_index as metric_kuramoto_index
import tvb.analyzers.metric_variance_global as metric_variance_global
import tvb.analyzers.metric_variance_of_node_variance as metric_variance_of_node_variance
import tvb.analyzers.wavelet as wavelet



### Dictionary {Analyzer Class : Title to appear in final documentation}

ANALYZERS_FOR_DOCUMENTATION = {
    cross_correlation.CrossCorrelate: "Cross-correlation",
    fft.FFT: "Fast Fourier Transform (FFT)",
    ica.fastICA: "Independent Component Analysis",
    pca.PCA: "Principal Components Analysis",
    node_coherence.NodeCoherence: "Node Coherence",
    node_complex_coherence.NodeComplexCoherence: "Node Complex Coherence",
    node_covariance.NodeCovariance: "Node Covariance",
    wavelet.ContinuousWaveletTransform: "Wavelet",
    metric_variance_global.GlobalVariance: "Global Variance",
    metric_variance_of_node_variance.VarianceNodeVariance: "Variance of Node Variance",
    metric_kuramoto_index.KuramotoIndex: "Kuramoto Index"
}


