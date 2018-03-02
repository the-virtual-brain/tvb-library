import numpy as np
import sys

from .basemodel import PerturbationModel

class MinNormPerturbModel(PerturbationModel):
    def __init__(self, radius=1.5, perturbtype='C'):
        PerturbationModel.__init__(self, 
                                radius=1.5, 
                                perturbtype='C')

    def _computeperturbation(self, A, w, pert_eig, ek):
        '''
        # Name: computeperturbation
        # 
        # Description: This is the computation and setup of the least squares soln. given
        # an A matrix, |lambda| value, and unit vector ek.
        @ params
        A           (np.ndarray) the raw numpy array of data CxC, numchans by numchans
        pert_eig    (np.complex) a complex number the represents where the
                    eigenvalue perturbation wants to go
        ek          (np.ndarray) the unit vector with 0's and then 1 at the
                    index of the channel we want to apply perturbation at
        @ returns
        delvec      (np.ndarray) the perturbation vector used to perturb A
                    to eigensystem with pert_eig at one.
        '''
        b = np.array((0, 1))
        numchans, _ = A.shape

        perturbA = A - pert_eig*np.eye((numchans))
        # determine if to compute row, or column perturbation
        if self.perturbtype == 'R': # C = inv(A)*ek
            Cmat = np.linalg.lstsq(perturbA, ek, rcond=-1)[0]
        elif self.perturbtype == 'C': # C = ek.T * inv(A)
            Cmat = np.linalg.lstsq(perturbA.T, ek, rcond=-1)[0].T

        # extract real and imaginary components to create vector of constraints
        Crmat = np.real(Cmat)
        Cimat = np.imag(Cmat)
        if self.perturbtype == 'R':
            Bmat = np.append(Cimat, Crmat, axis=1)
        elif self.perturbtype == 'C':
            Bmat = np.append(Cimat, Crmat, axis=0)    

        # compute perturbation to solve least squares
        if w != 0:
            delvec = Bmat.T.dot( np.linalg.inv(Bmat.dot(Bmat.T)) ).dot(b)
        else:
            delvec = -Cmat / np.linalg.norm(Cmat, ord='fro')**2
        return delvec

    def dcperturbation(self, A, radius=None):
        '''
        # Name: minnormperturbation
        # Description: Generates the minimum norm perturbation model described in Fragility in Epileptic Networks by Sritharan
        # 
        # Inputs: 
        # A        (np.ndarray) the raw numpy array of data CxC, numchans by numchans
        # l1       (float) the l1 regularization term for computing 'sparse minimum norm perturbation'
        #
        # Outputs:
        # minperturbnorm    (float) the l2 norm of the perturbation vector
        # delvecs_node      (np.ndarray) [n, n'] is an array of perturbation vectors
                            that achieve minimum norm at each row
        '''
        # initialize function paramters
        if radius is None:
            sigma = self.radius
        else:
            sigma = radius
        omega = 0
        numchans = A.shape[0]
        # initialize vector to desired eigenvalue
        pert_eig = sigma + 1j*omega
        # initialize array to store all the minimum euclidean norms, vecs and freqs
        minperturbnorm = np.zeros((numchans, 1))
        delvecs_node = np.zeros((numchans, numchans), dtype='complex')
        
        # apply perturbation model to each channel within network
        for inode in range(0, numchans):
            # set the unit column vector
            ek = np.concatenate((np.zeros((inode,1)), 
                                np.ones((1,1)), 
                                np.zeros((numchans-inode-1,1))), axis=0)
            delvec = self._computeperturbation(A, omega, pert_eig, ek)
            # store the l2 norm of the perturbation vector
            min_norm = np.linalg.norm(delvec)
            # store the minimum norm perturbation achievable, vector and frequency
            minperturbnorm[inode] = min_norm
            # store the vector corresponding to minimum norm perturbation
            delvecs_node[inode, :] = delvec
                
        return minperturbnorm, delvecs_node

    def gridsearchperturbation(self, A, searchnum=51):
        '''
        # Name: minnormperturbation
        # 
        # Description: Generates the minimum norm perturbation model described in Fragility in Epileptic Networks by Sritharan
        # 
        # Inputs: 
        # A: the raw numpy array of data CxT, numchans by numsamps
        # 3. l1: the l1 regularization term for computing 'sparse minimum norm perturbation'
        # searchnum: the amount of searches around the circle with radius to search for the min norm
        #
        # Outputs:
        # pertmat:              (np.ndarray)
        delvecs_list            (list)
        delfreqs_list           (list)
        '''
        # initialize search paramters to compute minimum norm perturbation
        top_wspace = np.linspace(-self.radius, self.radius, num=searchnum)
        wspace = np.append(top_wspace, op_wspace[1:len(top_wspace)-1], axis=0)
        sigma = np.sqrt(self.radius**2 - top_wspace**2)
        sigma = np.append(-sigma, sigma[1:len(top_wspace)-1], axis=0)
        b = np.array((0, 1))

        numchans, _ = A.shape

        # to store all the euclidean norms of the perturbation vectors
        delnorm_mat = np.zeros((numchans, wspace.size))
        delvecs_node = np.zeros((numchans, numchans))
        
        # initialize array to store all the minimum euclidean norms, vecs and freqs
        minperturbnorm = np.zeros((numchans, 1))
        delvecs_list = []
        delfreqs_list = []
        
        # apply perturbation model to each channel within network
        for inode in range(0, numchans):
            # set the unit column vector
            ek = np.concatenate((np.zeros((inode,1)), 
                                np.ones((1,1)), 
                                np.zeros((numchans-inode-1,1))), axis=0)
            delvecs_wspace = np.zeros((wspace.size, numchans), dtype='complex')
            
            # begin search over each w in wspace
            for iw in range(0, wspace.size):
                pert_eig = sigma[iw] + 1j*wspace[iw]
                delvec = self._computeperturbation(A, wspace[iw], pert_eig, ek)
                
                # store the l2 norm of the perturbation vector
                delnorm_mat[inode, iw] = np.linalg.norm(delvec)
                # store the perturbation vector at this specified radii point
                delvecs_wspace[iw,:] = delvec
                
            ########## Process Results from Grid Search In Eigenspace ##########        
            # find index of minimum norm perturbation for channel
            min_norm = delnorm_mat[inode, :].min()
            min_indices = np.where(min_norm == delnorm_mat[inode,:])[0]
            
            # store the minimum norm perturbation achievable, vector and frequency
            minperturbnorm[inode] = min_norm

            # store the perturbation vector(s)/frequency(s) that produces minimum euclidean norm for this inode (channel)
            if len(min_indices) == 1:
                min_index = min_indices[0]
                
                # get the min vector and the min freq to store
                vec = delvecs_wspace[min_index, :]
                freq = sigma[min_index] + 1j*wspace[min_index]

                # store the vector corresponding to minimum norm perturbation
                delvecs_list.append(vec)
                # store the position on instability circle that the minimum norm perturbation occurs
                delfreqs_list.append(freq)
                
            else:
                # initialize frequencies to insert for this node as a list
                to_insert_freqs = []

                # loop through each index where minimum euclidean norm occured
                for idx, min_index in enumerate(min_indices):
                    vec = delvecs_wspace[min_index, :].squeeze().reshape(numchans, 1)
                    freq = sigma[min_index] + 1j*wspace[min_index]
                
                    to_insert_freqs.append(freq)
                    if idx == 0:
                        to_insert_vec = np.array(vec)
                    else:
                        to_insert_vec = np.concatenate((to_insert_vec, vec), axis=1)
                 
                # convert the list to a np array 
                to_insert_freqs = np.array(to_insert_freqs)       

                # store all the perturbation vectors
                delvecs_list.append(to_insert_vec)
                # store the position on instability circle that the minimum norm perturbation occurs
                delfreqs_list.append(np.array(to_insert_freqs))
                
        return minperturbnorm, delvecs_list, delfreqs_list


