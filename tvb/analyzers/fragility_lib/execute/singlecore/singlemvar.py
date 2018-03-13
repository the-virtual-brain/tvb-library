import numpy as np 
import sys
import os
sys.path.append('../../')
from ...linearmodels.basemodel import BaseWindowModel
from ...linearmodels.mvarmodel import MvarModel
import warnings

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)

class SingleMvar(BaseWindowModel):
    '''
    These following functions are locally run on 1 CPU

    @Input:
    - passes in a single instance of the Patient IEEG object
    '''
    def __init__(self, winsizems=250, stepsizems=125, samplerate=1000):
        BaseWindowModel.__init__(self, winsizems=winsizems, 
                                stepsizems=stepsizems, 
                                samplerate=samplerate)
        # instantiate the mvar model
        self.mvarmodel = MvarModel(self.winsize, self.stepsize)
        self.winscomputed = False
    def settempdir(self, tempdir):
        self.tempdir = tempdir

    def runmvarsingle(self, raweeg, iwin, normalize=False):
        # get number of channels and samples in the raw data
        numchans, numsignals  = raweeg.shape

        assert numchans <= numsignals
        if numchans >= 200:
            warnings.warn("Whoa 200 channels to analyze? Could be too much to compute rn.")

        # compute time and sample windows array
        if self.winscomputed == False:
            self.compute_timepoints(numsignals)
            self.compute_samplepoints(numsignals)
            self.winscomputed = True

        # 1: fill matrix of all channels' next EEG data over window
        eegwin = raweeg[:, (self.samplepoints[iwin,0]):(self.samplepoints[iwin,1]+1)]

        if normalize:
            eegwin = (eegwin - np.mean(eegwin, axis=1)[:, np.newaxis]) / np.std(eegwin, axis=1)[:, np.newaxis]

        # 2. Compute the mvar-1 model
        adjmat = self.mvarmodel.mvaradjacencymatrix(eegwin)
        return adjmat

    def runmvar(self, raweeg, normalize=False):
        # get number of channels and samples in the raw data
        numchans, numsignals  = raweeg.shape

        assert numchans <= numsignals
        if numchans >= 200:
            warnings.warn("Whoa 200 channels to analyze? Could be too much to compute rn.")

        # compute time and sample windows array
        if self.winscomputed == False:
            self.compute_timepoints(numsignals)
            self.compute_samplepoints(numsignals)
            self.winscomputed = True

        adjmats = np.zeros((len(self.samplepoints), numchans, numchans), dtype=np.float32)
        for iwin in range(len(self.samplepoints)):
            # 1: fill matrix of all channels' next EEG data over window
            eegwin = raweeg[:, (self.samplepoints[iwin,0]):(self.samplepoints[iwin,1]+1)]

            if normalize:
                eegwin = (eegwin - np.mean(eegwin, axis=1)[:, np.newaxis]) / np.std(eegwin, axis=1)[:, np.newaxis]
            # 2. Compute the mvar-1 model
            adjmats[iwin,...] = self.mvarmodel.mvaradjacencymatrix(eegwin)

            LOG.debug('Finished running %s window out of %s', (iwin, len(self.samplepoints)))
            
        return adjmats

if __name__ == '__main__':
    winsizems = 250
    stepsizems = 125
    samplerate = 1024

    # initialize the base model for testing
    mvarmodel = SingleMvar(winsizems, stepsizems, samplerate)
    numsignals = 5000
    mvarmodel.compute_samplepoints(numsignals)
    mvarmodel.compute_timepoints(numsignals)

    # example run through sample data
    data = np.random.random(size=(5,5000))
    for iwin in range(len(mvarmodel.samplepoints)):
        adjmat = mvarmodel.runmvarsingle(data, iwin)
