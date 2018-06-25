import numpy as np
import colorednoise as cn


def fftnoise(f):
    '''
    Generates noise at the frequencies f.

    @parameters:
    - f         (np.ndarray) an array of frequencies

    @output:
    the inverse fft to get the new signal with phase shifts
    '''
    f = np.array(f, dtype='complex')
    Np = (len(f) - 1) // 2

    # generate random phases
    phases = np.random.rand(Np) * 2 * np.pi
    phases = np.cos(phases) + 1j * np.sin(phases)

    # multiply by phases
    f[1:Np + 1] *= phases
    f[-1:-1 - Np:-1] = np.conj(f[1:Np + 1])
    return np.fft.ifft(f).real


def band_limited_noise(min_freq, max_freq, samples, samplerate):
    '''
    @params:
    - samples        (int) the number of samples to generate
    - samplerate     (float) the samplerate of signal in Hz

    @output:
    the noise at frequencies between min_freq and max_freq
    '''
    freqs = np.abs(np.fft.fftfreq(samples, 1 / samplerate))
    f = np.zeros(samples)
    idx = np.where(np.logical_and(freqs >= min_freq, freqs <= max_freq))[0]
    f[idx] = 1
    return fftnoise(f)


class Noise(object):
    def __init__(self):
        pass

    @staticmethod
    def addcolorednoise(data, beta=2):
        samples = data.shape[1]  # number of samples to generate
        for ind in range(data.shape[0]):
            y = cn.powerlaw_psd_gaussian(beta, samples)
            data[ind, :] += y
        return data
    ''' Abstract methods for all noise objects to implement '''

    def configure(self):
        raise NotImplementedError(
            'Noise object does not have configure method.')

    def generate(self):
        raise NotImplementedError(
            'Noise object does not have generate method.')

    def _summary(self):
        pass


class LineNoise(Noise):
    def __init__(self, linefreq=60, bandwidth=4,
                 numharmonics=3, samplerate=1000.):
        self.linefreq = linefreq
        self.bandwidth = bandwidth
        self.numharmonics = numharmonics
        self.samplerate = samplerate

    def configure(self):
        pass

    def generate(self, numsamps, perturbfreq=True):
        '''
        Generates noise for a vector and adds to it

        @params:
        - numsamps      (int) the number of samples to generate
        '''

        linefreq = self.linefreq
        samplerate = self.samplerate

        # some factor wrt to the data scale
        multfactor = 2**10

        x_noise = np.zeros(numsamps)
        # loop through each harmonic and generate the randomized noise
        for iharm in range(self.numharmonics):
            lowfreq = linefreq - self.bandwidth // 2
            highfreq = linefreq + self.bandwidth // 2
            assert (highfreq - lowfreq) == 4.

            # generate a random perturbation on the frequency band noise
            if perturbfreq:
                randpert = np.random.normal(1, 0.01)
            else:
                randpert = 1.
            x_noise += band_limited_noise(lowfreq *
                                          randpert, highfreq *
                                          randpert, samples=numsamps, samplerate=samplerate)
            scaled_noise = np.float16(x_noise * multfactor)

        return scaled_noise

    def _summary(self):
        pass
