import numpy as np 
import colorednoise as cn

class Noise(object):
    def __init__(self):
        pass

    @staticmethod
    def addnoise(data, beta=2):
        samples = data.shape[1] # number of samples to generate
        for ind in range(data.shape[0]):
            y = cn.powerlaw_psd_gaussian(beta, samples)
            data[ind,:] += y
        return data