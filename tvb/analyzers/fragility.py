# -*- coding: utf-8 -*-
#
#
#  Fragility-Algorithm Package. 
#
#   CITATION:
# When using for scientific publications, please cite it as follows:
#
#   <INCLUDE CITATION>
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

    timeseries = time_series.TimeSeries(
        label="Time Series",
        required=True,
        doc="The timeseries to which the fragility analysis is to be applied.")

    winsize = basic.Integer(
        label="Size of the windows to use in milliseconds.",
        required=True,
        default=250,
        doc="Size of the windows to use in milliseconds.")

    stepsize = basic.Integer(
        label="Size of the windows to use in milliseconds.",
        required=True,
        default=125,
        doc="Size of the windows to use in milliseconds.")

    samplerate = basic.Float(
        label="Sample rate of signal in Hz.",
        required=True,
        default=1000,
        doc="Sample rate of the signal in Hz")

    # whether or not to use multiprocessing
    parallelize = False
    numcores = psutil.cpu_count() / 2.

    def evaluate(self, linefreq=60):
        rawdata = self.timeseries.data

        # first filter line noise
        noisemodel = FilterLinearNoise(samplerate=self.samplerate)
        rawdata = noisemodel.notchlinenoise(rawdata, linefreq=linefreq)

        # instantiate a mvarmodel object
        if self.parallelize:
            mvarmodel = ParallelMvar(self.winsize, self.stepsize, self.samplerate, numcores=numcores)
            
            # initialize model
            mvarmodel.runmvar(rawdata)
            adjmats = mvarmodel.mergemvarresults()
        else:
            # run serial mvar model computationa
            mvarmodel = SingleMvar(self.winsize, self.stepsize, self.samplerate)
            adjmats = mvarmodel.runmvar(rawdata, normalize=True)
        self.adjmats = adjmats
        return adjmats

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
        fragilitymat = numpy.zeros((N, T))
        for icol in range(T):
            fragilitymat[:,icol] = (numpy.max(minnormpertmat[:,icol]) - minnormpertmat[:,icol]) /\
                                    numpy.max(minnormpertmat[:, icol])
        return fragilitymat

    def evaluate(self):
        adjmats = self.adjmats
        # instantiate a mvarmodel object
        if self.parallelize:
            # initialize model
            pertmodel = ParallelPert(radius=1.5, perturbtype='C', numcores=numcores)
            
            # create temp dir to save files
            tempdir = None
            assert tempdir is str
            pertmodel.settempdir(tempdir)

            # run parallel scheme
            pertmodel.runpert(adjmats)
            pertmats = mvarmodel.mergemvarresults()
        else:
            # run serial mvar model computationa
            pertmodel = SinglePert(radius=1.5, perturbtype='C')
            pertmats = pertmodel.runpert(adjmats)

        self.fragmats = self._compute_fragilitymetric(pertmats)
        self.pertmats = pertmats
        return self.fragmats

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

