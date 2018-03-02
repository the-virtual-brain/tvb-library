# Parallel Processing Functions
# Authors: Adam Li
# Edited by: Adam Li

# Imports necessary for this function 
import numpy as np 
from ...linearmodels.basemodel import BaseWindowModel
from ...linearmodels.mvarmodel import MvarModel

# for multiprocessing on separate cpus
import psutil
import multiprocessing as mp

import functools
from contextlib import closing

# utility libraries
import os
import traceback
import natsort
import sys
import warnings

def _initmvar(raweeg, timepoints, mvarmodel, tempdir):
    global shared_raweeg
    global shared_timepoints
    global shared_mvarmodel
    global shared_tempdir

    shared_timepoints = timepoints
    shared_raweeg = raweeg
    shared_mvarmodel = mvarmodel        
    shared_tempdir = tempdir

def mvarjob(icore):
    winstoanalyze = processlist[icore]
    for win in winstoanalyze:
        # 1: fill matrix of all channels' next EEG data over window
        eegwin = shared_raweeg[:, (shared_timepoints[win,0]) : (shared_timepoints[win,1]+1)]

        # 2: call the function to create the mvar model
        adjmat = shared_mvarmodel.mvaradjacencymatrix(eegwin)
        
        tempfilename = os.path.join(shared_tempdir, 'temp_'+str(win)+'.npz')
        try:
            np.savez_compressed(tempfilename, adjmat=adjmat)
        except:
            sys.stdout.write(traceback.format_exc())
            return 0
        # print("finished mvar job at ", win)
        # sys.stdout.flush()
    return 1

def mvarjobwin(win):
    # 1: fill matrix of all channels' next EEG data over window
    eegwin = shared_raweeg[:, (shared_timepoints[win,0]) : (shared_timepoints[win,1]+1)]
    # normalize eeg
    # eegwin = _normalizets(eegwin)
    # eegwin = (eegwin - np.mean(eegwin, axis=1)[:, np.newaxis]) / np.std(eegwin, axis=1)[:, np.newaxis]

    # 2: call the function to create the mvar model
    adjmat = shared_mvarmodel.mvaradjacencymatrix(eegwin)
        
    tempfilename = os.path.join(shared_tempdir, 'temp_'+str(win)+'.npz')
    try:
        np.savez_compressed(tempfilename, adjmat=adjmat)
    except:
        sys.stdout.write(traceback.format_exc())
        return 0
    return 1

class ParallelMvar(BaseWindowModel):
    def __init__(self, winsizems=250, stepsizems=125, samplerate=1000,numcores=None):
        BaseWindowModel.__init__(self, 
                                winsizems=winsizems, 
                                stepsizems=stepsizems, 
                                samplerate=samplerate)
        if numcores is None:
            self.numcores = psutil.cpu_count() - 1 
        else:
            self.numcores = numcores
        # instantiate the mvar model
        self.mvarmodel = MvarModel(self.winsize, self.stepsize)
        # initialize results queue to store all results
        # self.resultsqueue = mp.Queue()

    def settempdir(self, tempdir):
        self.tempdir = tempdir

    def runmvar(self, raweeg, listofwins=[]):
        # get number of channels and samples in the raw data
        numchans, numsignals  = raweeg.shape
        if numchans >= 200:
            warnings.warn("Whoa 200 channels to analyze? Could be too much to compute rn.")

        # compute time and sample windows array
        samplepoints = self.compute_samplepoints(numsignals, copy=False)
        self.numwins = samplepoints.shape[0]

        # Run multiprocessing pool over indices
        with closing(mp.Pool(initializer=_initmvar, 
                initargs=(raweeg, samplepoints, self.mvarmodel, self.tempdir))) as p:
            mvarresults = p.map(mvarjobwin, range(0, self.numwins))
        p.join()
        # mvarresults = [1]
        sys.stdout.write('Finished mvar model computation for ' +\
                        str(self.numwins) + ' windows.')
        return 1

    def mergemvarresults(self):
        tempfiles = natsort.natsort.natsorted(os.listdir(self.tempdir))

        if self.numwins != len(tempfiles):
           raise Exception('MVAR Model did not finish running for all necessary windows!')
           return 0

        # Loop through all temp files and merge them together
        for idx, tempfile in enumerate(tempfiles):
            tempdata = np.load(os.path.join(self.tempdir, tempfile))
            if idx==0:
                adjmat = tempdata['adjmat']
                numchans = adjmat.shape[0]
                adjmats = np.zeros((self.numwins, numchans, numchans))
            else:
                adjmats[idx, :, :] = tempdata['adjmat']
        return adjmats