# Parallel Processing Functions
# Authors: Adam Li
# Edited by: Adam Li

# Imports necessary for this function
import numpy as np
from ...linearmodels.basemodel import PerturbationModel
from ...linearmodels.perturbationmodel import MinNormPerturbModel

# for multiprocessing on separate cpus
import multiprocessing as mp

# utility libraries
import os
import traceback
import natsort
import sys
import tempfile

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)


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
        newradius = np.max(evals) * 1.5
        # perform perturbation model computation
        # minperturbnorm, delvecs_list, delfreqs_list = shared_pertmodel.minnormperturbation(A, searchnum=shared_searchnum)
        # return minperturbnorm, delvecs_list, delfreqs_list
        pertmat, delvecs = shared_pertmodel.dcperturbation(A, radius=newradius)

        tempfilename = os.path.join(shared_tempdir, 'temp_{0}.npz'.format(win))
        try:
            np.savez(tempfilename, pertmat=pertmat, delvecs=delvecs)
        except BaseException:
            sys.stdout.write(traceback.format_exc())
            return 0
    return 1


class ParallelPert(PerturbationModel):
    def __init__(self, radius=1.5, perturbtype='C', numcores=None):
        super(ParallelPert, self).__init__(self,
                                           radius=1.5,
                                           perturbtype='C')
        self.pertmodel = MinNormPerturbModel(
            self.radius,
            self.perturbtype)
        if numcores is None:
            self.numcores = mp.cpu_count() - 1
        else:
            self.numcores = numcores

    def settempdir(self, tempdir=None):
        self.tempdir = tempdir
        if tempdir is None:
            # set temporary directory
            self.tempdir = tempfile.TemporaryDirectory()
        LOG.debug('created temporary directory %s', self.tempdir)

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

        LOG.debug(
            'Finished pert model computation for %d windows.',
            self.numwins)
        return 1

    def mergepertresults(self):
        tempfiles = natsort.natsort.natsorted(os.listdir(self.tempdir))

        # Loop through all temp files and merge them together
        for idx, tempfile in enumerate(tempfiles):
            tempdata = np.load(os.path.join(self.tempdir, tempfile))
            if idx == 0:
                pertmat = tempdata['pertmat']
                numchans = pertmat.shape[0]

                pertmats = np.zeros((numchans, self.numwins))
                delvecs_array = np.zeros(
                    (self.numwins, numchans, numchans), dtype='complex')
            else:
                pertmats[:, idx] = tempdata['pertmat'].ravel()
                delvecs_array[idx, :, :] = tempdata['delvecs']

        return pertmats, delvecs_array
