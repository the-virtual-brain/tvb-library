# Parallel Processing Functions
# Authors: Adam Li
# Edited by: Adam Li

# Imports necessary for this function 
import numpy as np 
from fragility.linearmodels.base.basemodel import PerturbationModel
from fragility.linearmodels.perturbationmodel import MinNormPerturbModel

# for multiprocessing on separate cpus
import psutil
import multiprocessing as mp

from contextlib import closing

# utility libraries
import os
import traceback
import natsort
import sys

def _initpert(adjmats, pertmodel, tempdir):
    global shared_adjmats
    global shared_pertmodel
    global shared_tempdir

    shared_adjmats = adjmats
    shared_pertmodel = pertmodel  
    shared_tempdir = tempdir     

def pertjob(icore):
    winstoanalyze = processlist[icore]
    for win in winstoanalyze:
        # get specific A matrix in this window
        A = np.squeeze(shared_adjmats[win, :, :])
        
        evals = np.abs(np.linalg.eigvals(A))
        newradius = np.max(evals) *1.5
        # perform perturbation model computation
        # minperturbnorm, delvecs_list, delfreqs_list = shared_pertmodel.minnormperturbation(A, searchnum=shared_searchnum)
        # return minperturbnorm, delvecs_list, delfreqs_list
        pertmat, delvecs = shared_pertmodel.dcperturbation(A, radius=newradius)
    
        tempfilename = os.path.join(shared_tempdir, 'temp_'+str(win)+'.npz')
        try:
            np.savez(tempfilename, pertmat=pertmat, delvecs=delvecs)
        except:
            sys.stdout.write(traceback.format_exc())
            return 0   
    return 1

class ParallelPert(PerturbationModel):
    def __init__(self, winsize=250, stepsize=125, radius=1.5, perturbtype='C', samplerate=1000., numcores=None):
        PerturbationModel.__init__(self, 
                            winsizems=winsize, 
                            stepsizems=stepsize, 
                            radius=1.5, 
                            perturbtype='C', 
                            samplerate=samplerate)
        self.pertmodel = MinNormPerturbModel(self.winsize, 
                                        self.stepsize, 
                                        self.radius, 
                                        self.perturbtype)
        if numcores is None:
            self.numcores = psutil.cpu_count() - 1 
        else:
            self.numcores = numcores

    def settempdir(self, tempdir):
        self.tempdir = tempdir

    def runpert(self, adjmats, listofwins=[]):
        # get the dimensions of adjmats
        self.numwins, numchans, _ = adjmats.shape

        global processlist
        global shared_adjmats
        global shared_pertmodel
        global shared_tempdir

        shared_adjmats = adjmats
        shared_pertmodel = self.pertmodel       
        shared_tempdir = self.tempdir

        # compute on different partitions at a time
        percentsplit = np.array_split(np.arange(0, self.numwins), 
                                    np.ceil(self.numwins / 1000.))
        for isplit in range(0, len(percentsplit)):
            processlist = np.array_split(percentsplit[isplit], self.numcores)

            # go through processes and analyze the partition on windows
            processes = []
            for icore in range(self.numcores):
                processes.append(mp.Process(target=pertjob, args=(icore,)))
            for p in processes:
                p.start()
            for p in processes:
                p.join()

        # create a multiprocessing pool with initializers to share memory arrays raweeg and timepoints
        # with closing(mp.Pool(initializer=_initpert, initargs=(adjmats, self.searchnum, self.tempdir))) as p:
        #     perturb_results = p.map_async(pertjob, range(0, self.numwins))
        # p.join()
        sys.stdout.write('Finished pert model computation for ' + str(self.numwins) + ' windows.')
        return 1
    def mergepertresults(self):
        tempfiles = natsort.natsort.natsorted(os.listdir(self.tempdir))

        # Loop through all temp files and merge them together
        for idx, tempfile in enumerate(tempfiles):
            tempdata = np.load(os.path.join(self.tempdir, tempfile))
            if idx==0:
                pertmat = tempdata['pertmat']
                numchans = pertmat.shape[0]

                pertmats = np.zeros((numchans, self.numwins))
                delvecs_array = np.zeros((self.numwins, numchans, numchans), dtype='complex')
            else:
                pertmats[:, idx] = tempdata['pertmat'].ravel()
                delvecs_array[idx, :, :] = tempdata['delvecs']

        return pertmats, delvecs_array