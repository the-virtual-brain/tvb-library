# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and 
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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
Perform Fragility Analysis on a TimeSeries Object and returns an
Fragility datatype.

.. moduleauthor:: Adam Li <adam2392@gmail.com>

"""

import numpy
import tvb.datatypes.time_series as time_series
import tvb.datatypes.arrays as arrays
import tvb.basic.traits.core as core
import tvb.basic.traits.types_basic as basic
import tvb.basic.traits.util as util
from tvb.basic.logger.builder import get_logger

from .fragility_lib.preprocess.filters import FilterLinearNoise
from .fragility_lib.execute.singlecore.singlemvar import SingleMvar
from .fragility_lib.execute.singlecore.singlepert import SinglePert
from .fragility_lib.execute.singlenode.parallelmvar import ParallelMvar
from .fragility_lib.execute.singlenode.parallelpert import ParallelPert

import psutil

LOG = get_logger(__name__)

class mvarwindowed(core.Type):
    """
    Takes a TimeSeries datatype(x) and returns a sequence of mvar models (A)

    :math: x(t+1) = A*x(t)

    MVAR takes time-points as observations and nodes as variables

    It uses a sliding window algorithm to estimate the mvar models
    """

    timeseries = .TimeSeries(
        label="Time Series",
        required=True,
        doc="The timeseries to which the fragility analysis is to be applied.")

    winsize = basic.Integer(
        label="Size of the windows to use in milliseconds.",
        required=False,
        default=250,
        doc="Size of the windows to use in milliseconds.")

    stepsize = basic.Integer(
        label="Size of the windows to use in milliseconds.",
        required=False,
        default=250,
        doc="Size of the windows to use in milliseconds.")

    samplerate = basic.Float(
        label="Sample rate of signal in Hz.",
        required=True,
        default=1000,
        doc="Sample rate of the signal in Hz")

    # whether or not to use multiprocessing
    parallelize = False
    numcores = psutil.cpu_count() / 2.

    def evaluate(self):
        rawdata = self.timeseries

        # first filter line noise
        noisemodel = FilterLinearNoise(samplerate=samplerate)
        rawdata = noisemodel.notchlinenoise(rawdata, freq=linefreq)

        # instantiate a mvarmodel object
        if parallelize:
            mvarmodel = ParallelMvar(self.winsize, self.stepsize, self.samplerate, numcores=numcores)
            
            # initialize model
            mvarmodel.runmvar(rawdata)
            adjmats = mvarmodel.mergemvarresults()
        else:
            # run serial mvar model computationa
            mvarmodel = SingleMvar(self.winsize, self.stepsize, self.samplerate)
            adjmats = mvarmodel.runmvar(rawdata, normalize=True)
        self.adjmats = adjmats


    def result_shape(self):
        "Returns the resulting model."
        n = self.adjmats.shape 
        return n
    def result_size(self):
        "Returns the storage size in bytes of the mixing matrix of the ICA analysis, assuming 64-bit float."
        return numpy.prod(self.result_shape()) * 8
    def _find_summary_info(self):
        """
        To be implemented in every subclass.
        """
        return None

class fragilitymodel(core.Type):
    adjmats = arrays.FloatArray(
        label="Time Series",
        required=True,
        doc="The timeseries to which the fragility analysis is to be applied.")

    radius = basic.Float(
        label="Radius of perturbation.",
        required=True,
        default=1000,
        doc="Radius of perturbation.")

    # whether or not to use multiprocessing
    parallelize = False
    numcores = psutil.cpu_count() / 2.

    def _compute_fragilitymetric(self, minnormpertmat):
        # get dimensions of the pert matrix
        N, T = minnormpertmat.shape
        # assert N < T
        fragilitymat = np.zeros((N, T))
        for icol in range(T):
            fragilitymat[:,icol] = (np.max(minnormpertmat[:,icol]) - minnormpertmat[:,icol]) /\
                                    np.max(minnormpertmat[:, icol])
        return fragilitymat

    def evaluate(self):
        adjmats = self.adjmats
        # instantiate a mvarmodel object
        if parallelize:
            # initialize model
            pertmodel = ParallelPert(winsize=self.winsize, stepsize=self.stepsize, radius=1.5, perturbtype='C', samplerate=self.samplerate, numcores=numcores)
            
            # create temp dir to save files
            tempdir = None
            assert tempdir is str
            pertmodel.settempdir(tempdir)

            # run parallel scheme
            pertmodel.runpert(adjmats)
            pertmats = mvarmodel.mergemvarresults()
        else:
            # run serial mvar model computationa
            pertmodel = SinglePert(winsize=self.winsize, stepsize=self.stepsize, radius=1.5, perturbtype='C', samplerate=self.samplerate)
            pertmats = pertmodel.runpert(adjmats)

        self.fragmats = self.fragilitymodel(pertmats)
        self.pertmats = pertmats

    def result_shape(self):
        "Returns the shape of the mixing matrix."
        return self.pertmats.shape
    
    def result_size(self):
        "Returns the storage size in bytes of the mixing matrix of the ICA analysis, assuming 64-bit float."
        return numpy.prod(self.result_shape()) * 8

    def _find_summary_info(self):
        """
        To be implemented in every subclass.
        """
        return None

