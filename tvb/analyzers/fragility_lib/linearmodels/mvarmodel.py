'''
Linearmodels.py
@By: Adam Li
@Date: 10/16/17

@Description: Classes designed for the implementation of linear models related to the work of analyzing data using linear models.

@Methods:
- setup_logging: For each children class of the linearmodel, one should create their own .yaml file for logging computations done by this model

'''
# Imports necessary for this function
import numpy as np
from scipy.sparse import csr_matrix, linalg, dok_matrix
from .basemodel import BaseWindowModel

class MvarModel(BaseWindowModel):
    def __init__(self, winsizems=250, stepsizems=125, samplerate=1000.):
        # super(MVARModel, self).__init__(winsize, stepsize)
        BaseWindowModel.__init__(self, 
                                winsizems=winsizems, 
                                stepsizems=stepsizems, 
                                samplerate=samplerate)

        # initialize logger configuration for Linear Model
        # if not logger:
        #     self._setup_logging(logfile=logfile)

        # create and initialize logger
        # self.logger = logger or logging.getLogger(__name__)
        # self.logger.info('Initialized MVAR model!')
    def mvaradjacencymatrix(self, eegwin):
        '''
        # Name:  mvaradjacencymatrix
        # Date Created: July 16, 2017
        # Data Modified: October  8, 2017
        # Description: Generates adjacency matrix for each window for a certain winsize/stepsize
        # 
        # Inputs: 
        # raweeg        (np.ndarray) the raw numpy array of data CxT, numchans by numsamps
        #
        # Outputs:
        # adjmat        (np.ndarray) the mvar model tensor CxC samples by chan by chan
        '''
        # 1. determine shape of the window of data
        numchans = eegwin.shape[0]
        # 2. compute functional connectivity
        # create observation vector (b) from vectorized data
        obvector = np.ndarray.flatten(eegwin[:, 1:], order='F')
        # 3. perform sparse least squares and reshape vector -> mat
        theta = self._computelstsq(eegwin, obvector)
        adjmat = theta.reshape((numchans, numchans))
        # return adjacency matrix to function call
        return adjmat

    def _computelstsq(self, eegwin, obvector):
        '''
        # Least Squares wrapper function .
        # FUNCTION:
        #   y = computelstsq(eegWin, obvector)
        #
        # INPUT ARGS: (defaults shown):
        #   eegWin = dat;           # CxT matrix with C chans and T samps, the A in Ax=b
        #   obvector = [58 62];     # Tx1 vector, the b in Ax=b
        # OUTPUT ARGS::
        #   theta = vector of weights in the x_ij in MVAR model 
        # Extract shape of window of eeg to get number of channels and samps
        '''
        numchans, numwinsamps = eegwin.shape
        
        # initialize H matrix as array filled with zeros
        if numchans > 100:
            H = np.zeros((numchans*(numwinsamps-1), numchans**2)) # N(T-1) x N^2
        else:
            H = dok_matrix((numchans*(numwinsamps-1), numchans**2))
        
        # 1: fill all columns in matrix H
        eegwin = eegwin.transpose()
        stepsize = np.arange(0,H.shape[0], numchans)
        H[stepsize, 0:numchans] = eegwin[0:numwinsamps-1,:]
        
        buff = eegwin[0:numwinsamps-1,:]
        for ichan in range(1, numchans):
            # indices to slice through H matrix by
            rowinds = stepsize+(ichan)
            colinds = np.arange((ichan)*numchans, (ichan+1)*numchans)
            # slice through H mat and build it
            H[np.ix_(rowinds, colinds)] = buff
        # 2: convert H mat into a sparse matrix to speed up computation
        if numchans > 100:
            H = csr_matrix(H)
        else:
            H = H.tocsr()
        # 3: compute sparse least squares
        theta = linalg.lsqr(H, obvector)[0]
        return theta



