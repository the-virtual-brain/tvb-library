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
.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

Define what Analyzers classes will be included in the UI / Online help 
documentation. Python docstring from the classes listed below will be included.

"""

#import tvb.analyzers.auto_correlation as auto_correlation
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
                               #auto_correlation.AutoCorrelation: "Auto-correlation", 
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


