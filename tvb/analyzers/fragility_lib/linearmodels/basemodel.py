'''
Base Models for the Fragility Module
# Authors: Adam Li
# Edited by: Adam Li
'''
# Imports necessary for this function 
import numpy as np
import warnings 

class BaseWindowModel(object):
    '''
    This is a base class wrapper for any type of window model that we use. 
    For example, we use a sliding window to compute a MVAR-1 model, or to compute
    FFT models.

    @params:
    - model         (object)
    - winsize       (int) an int of the window size to use in milliseconds
    - stepsize      (int) an int of the window step size to use in milliseconds
    - samplerate    (float) the samplerate in Hz
    '''
    def __init__(self, winsizems=None, stepsizems=None, samplerate=None):
        # if not model:
        #     warnings.warn("Model was not set! Please initialize a model and pass it in as model=")
        if not winsizems:
            warnings.warn("Window size was not set for sliding window model. Set a winsize in ms!")
        if not stepsizems:
            warnings.warn("Step size was not set for sliding window model. Set a stepsize in ms!")
        if not samplerate:
            warnings.warn("User needs to pass in sample rate in Hz!")

        assert isinstance(winsizems, int)
        assert isinstance(stepsizems, int)

        # self.model = model
        self.winsize = winsizems
        self.stepsize = stepsizems
        self.samplerate = samplerate

        # compute the number of samples in window and step
        self._setsampsinwin()
        self._setsampsinstep()
    def _setsampsinwin(self):
        # onesamp_ms = 1. * 1000./self.samplerate
        # numsampsinwin = self.winsize / onesamp_ms
        self.winsamps = self.winsize * self.samplerate / 1000.
        if self.winsamps % 1 != 0:
            warnings.warn("The number of samples within your window size is not an even integer.\
                          Consider increasing/changing the window size.")
    def _setsampsinstep(self):
        self.stepsamps = self.stepsize * self.samplerate / 1000.
        if self.stepsamps % 1 != 0:
            warnings.warn("The number of samples within your step size is not an even integer.\
                          Consider increasing/changing the step size.")
    def get_timepoints(self):
        return self.timepoints
    def get_samplepoints(self):
        return self.samplepoints
    def compute_timepoints(self, numtimepoints, copy=True):
        # Creates a [n,2] array that holds the time range of each window 
        # in the analysis over sliding windows.

        # trim signal and then convert into milliseconds
        # numtimepoints = numtimepoints - numtimepoints%(self.samplerate/6)
        timepoints_ms = numtimepoints * 1000. / self.samplerate

        # create array of indices of window start and end times
        timestarts = np.arange(0, timepoints_ms - self.winsize+1, self.stepsize)
        timeends = np.arange(self.winsize-1, timepoints_ms, self.stepsize)
        # create the timepoints array for entire data array
        timepoints = np.append(timestarts[:, np.newaxis], 
                               timeends[:, np.newaxis], axis=1)
        if copy:
            self.timepoints = timepoints
        else:
            return timepoints
    def compute_samplepoints(self, numtimepoints, copy=True):
        # Creates a [n,2] array that holds the sample range of each window that 
        # is used to index the raw data for a sliding window analysis
        samplestarts = np.arange(0, numtimepoints - self.winsamps+1., self.stepsamps).astype(int)
        sampleends = np.arange(self.winsamps-1., numtimepoints, self.stepsamps).astype(int)
        samplepoints = np.append(samplestarts[:, np.newaxis],
                                 sampleends[:, np.newaxis], axis=1)
        if copy:
            self.samplepoints = samplepoints
        else:
            return samplepoints

class PerturbationModel(BaseWindowModel):
    def __init__(self, winsizems=250, stepsizems=125, radius=1.5, perturbtype='C', samplerate=1000.):
        BaseWindowModel.__init__(self, winsizems=winsizems, stepsizems=stepsizems, samplerate=samplerate)
        self.radius = radius
        self.perturbtype = perturbtype

if __name__ == '__main__':
    # test parameters
    winsizems = 250
    stepsizems = 125
    samplerate = 1024
    model = None
    radius = 1.5
    perturbtype = 'C'

    # initialize the base model for testing
    initmodel = BaseWindowModel(winsizems, stepsizems, samplerate)
    numsignals = 5000
    initmodel.compute_samplepoints(numsignals)
    initmodel.compute_timepoints(numsignals)

    print("Sample points through raw data: ", initmodel.samplepoints)
    print("Time points through raw data in ms: ", initmodel.timepoints)

    initmodel = PerturbationModel(winsize, stepsize, radius, perturbtype, samplerate)
    

