import numpy as np
from scipy.signal import butter, filtfilt
import warnings 

class FilterLinearNoise(object):
    def __init__(self, samplerate=None):
        '''
        @params
        freqrange       (list) of the lower and upper frequency value to filter at
        samplerate      (int) the sampling rate in Hz
        '''
        # self.freqrange = np.array(freqrange)
        self.samplerate = samplerate
        if not samplerate:
            warnings.warn("User needs to pass in sample rate in Hz!")

    def __buttfilt(self, rawdata, freqrange, btype, order):
        # Butterworth filter wrapper function with zero phase distortion.
        # FUNCTION:
        #   y = buttfilt(dat,freqrange,samplerate,filttype,order)
        #
        # INPUT ARGS: (defaults shown):
        #   raw_data = dat;           % data to be filtered (if data is a matrix, BUTTFILT filters across rows)
        #   freqrange = [58 62];      % filter range (depends on type)
        #   filttype = 'stop';        % type of filter ('bandpass','low','high','stop') 
        #   order = 4;                % order of the butterworth filter
        #   filters = {B,A};          % a set of filters to use on data (created by a previous buttfilt call)
        # OUTPUT ARGS::
        #   data = the filtered data
        # the Nyquist frequency
        nyq = self.samplerate/2. 
        
        # create a butterworth filter with specified order, freqs, type
        b, a = butter(N=order, Wn=freqrange/nyq, btype=btype)
        filters = np.array((b,a))
        # run filtfilt for zero phase distortion
        data = filtfilt(b, a, rawdata)
        return data, filters

    def filter_rawdata(self, rawdata, freqrange, btype='bandpass', order=4):
        freqrange = np.asarray(freqrange)

        rawdata, filters = self.__buttfilt(rawdata=rawdata, 
                                        freqrange=freqrange, 
                                        btype=btype, 
                                        order=order)
        return rawdata

    def notchlinenoise(self, rawdata, linefreq=60, order=3):
        '''
        To run filtering of raw data that comes in as [numchans, numtime], it will
        apply freqrange and it's corresponding harmonics up to nyquist with a notch filter.

        Example usage:
        filtereddata = filterrawdata([59.5,60.5], samplerate=1000, filtttype='notch')

        Parameters:
        freqrange = [58 62];      % filter range (depends on type)
        filttype        (str) notch for now
        order = 4;                % order of the butterworth filter
        '''
        ######################### FILTERING ################################
        # define lambda function that creates an array of the frequency harmonic +/- 0.5 Hz
        freqrange = lambda multfactor: np.array([linefreq*multfactor - 0.5, linefreq*multfactor + 0.5])

        i = 1
        while self.samplerate > freqrange(i)[0]*2.:
            rawdata, _ = self.__buttfilt(rawdata, freqrange(i), 'bandstop', order=order)
            print("filtered at: ", freqrange(i))
            i += 1

        return rawdata

if __name__ == '__main__':
    linefreq = 60
    samplerate = 1024.

    filtlinenoise = FilterLinearNoise(samplerate=samplerate)

    # example run through sample data
    data = np.random.random(size=(5,5000))
    print(data.shape)
    # to use a bandpass filter
    rawfiltrange = [0.1, 500]
    data = filtlinenoise.filter_rawdata(data, freqrange=rawfiltrange)

    # to notch at line noise
    data = filtlinenoise.notchlinenoise(data, freq=freqrange)

    print(data.shape)