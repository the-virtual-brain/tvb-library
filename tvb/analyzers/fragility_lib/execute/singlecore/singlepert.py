import numpy as np
from ...linearmodels.basemodel import PerturbationModel
from ...linearmodels.perturbationmodel import MinNormPerturbModel

from tvb.basic.logger.builder import get_logger
LOG = get_logger(__name__)


class SinglePert(PerturbationModel):
    '''
    These following functions are locally run on 1 CPU

    @Input:
    - passes in a single instance of the Patient IEEG object
    '''

    def __init__(self, radius=1.5, perturbtype='C'):
        super(SinglePert, self).__init__(self,
                                         radius=radius,
                                         perturbtype=perturbtype)
        self.pertmodel = MinNormPerturbModel(
            self.radius,
            self.perturbtype)

    def settempdir(self, tempdir):
        self.tempdir = tempdir

    def runpertsingle(self, adjmat, iwin, fast=True):
        adjmat = adjmat.squeeze()
        assert adjmat.ndim == 2
        assert adjmat.shape[0] == adjmat.shape[1]
        # get shape of the adjmats
        numchans = adjmat.shape[0]
        searchnum = 51
        # initialize dict
        perturbation_dict = dict()

        # perform perturbation model computation
        if not fast:
            self.pertmat, self.delvecs, self.delfreqs = \
                self.pertmodel.gridsearchperturbation(
                    adjmat, searchnum=searchnum)
            # save the corresponding arrays
            perturbation_dict['pertmat'] = self.pertmat
            perturbation_dict['delvecs'] = self.delvecs
            perturbation_dict['delfreqs'] = self.delfreqs
        else:
            self.pertmat, self.delvecs = self.pertmodel.dcperturbation(adjmat)
            # save the corresponding arrays
            perturbation_dict['pertmat'] = self.pertmat
            perturbation_dict['delvecs'] = self.delvecs
        return perturbation_dict

    def runpert(self, adjmats):
        assert adjmats.ndim == 3
        assert adjmats.shape[1] == adjmats.shape[2]
        # get shape of the adjmats
        numchans = adjmats.shape[1]

        pertmats = np.zeros((numchans, adjmats.shape[0]), dtype=np.float32)
        for iwin in range(adjmats.shape[0]):
            adjmat = adjmats[iwin, :, :].squeeze()
            # perform perturbation model computation
            pertmat, delvecs = self.pertmodel.dcperturbation(adjmat)

            pertmats[:, iwin] = pertmat.ravel()

            LOG.debug('Finished running %s window out of %s',
                      (iwin, adjmats.shape[0]))
        return pertmats
