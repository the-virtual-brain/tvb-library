# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import butter, filtfilt, welch, periodogram, spectrogram
from scipy.interpolate import interp1d, griddata


# x is assumed to be data (real numbers) arranged along the first dimension of an ndarray
# this factory makes use of the numpy array properties


# Pointwise analyzers:

def interval_scaling(x, min_targ=0.0, max_targ=1.0, min_orig=None, max_orig=None):
    if min_orig is None:
        min_orig = np.min(x, axis=0)
    if max_orig is None:
        max_orig = np.max(x, axis=0)
    scale_factor = (max_targ - min_targ) / (max_orig - min_orig)
    return min_targ + (x - min_orig) * scale_factor


def abs_envelope(x):
    x_mean = x.mean(axis=0) * np.ones(x.shape[1:])
    # Mean center each signal
    x -= x_mean
    # Compute the absolute value and add back the mean
    return np.abs(x) + x_mean


def spectrogram_envelope(x, fs, lpf=None, hpf=None, nperseg=None):
    envelope = []
    for xx in x.T:
        F, T, C = spectrogram(xx, fs, nperseg=nperseg)
        fmask = np.ones(F.shape, 'bool')
        if hpf:
            fmask *= F > hpf
        if lpf:
            fmask *= F < lpf
        envelope.append(C[fmask].sum(axis=0))
    return np.array(envelope).T, T


# Across points analyzers:

# Univariate:

# Time domain:


# Frequency domain:

def _butterworth_bandpass(fs, mode, lowcut, highcut, order=3):
    """
    Build a diggital Butterworth filter
    """
    nyq = 0.5 * fs
    freqs = []
    if lowcut is not None:
        freqs.append(lowcut / nyq)  # normalize frequency
    if highcut is not None:
        freqs.append(highcut / nyq)  # normalize frequency
    b, a = butter(order, freqs, btype=mode)  # btype : {'lowpass', 'highpass', 'bandpass', 'bandstop}, optional
    return b, a


def filter_data(data, fs, lowcut=None, highcut=None, mode='bandpass', order=3, axis=0):
    # get filter coefficients
    b, a = _butterworth_bandpass(fs, mode, lowcut, highcut, order)
    # filter data
    y = filtfilt(b, a, data, axis=axis)
    # y = lfilter(b, a, data, axis=axis)
    return y


def spectral_analysis(x, fs, freq=None, method="periodogram", output="spectrum", nfft=None, window='hanning',
                      nperseg=256, detrend='constant', noverlap=None, f_low=10.0, log_scale=False):
    if freq is None:
        freq = np.linspace(f_low, nperseg, nperseg - f_low - 1)
        df = freq[1] - freq[0]
    psd = []
    for iS in range(x.shape[1]):
        if method is welch:
            f, temp_psd = welch(x[:, iS],
                                fs=fs,  # sample rate
                                nfft=nfft,
                                window=window,  # apply a Hanning window before taking the DFT
                                nperseg=nperseg,  # compute periodograms of 256-long segments of x
                                detrend=detrend,
                                scaling="spectrum",
                                noverlap=noverlap,
                                return_onesided=True,
                                axis=0)
        else:
            f, temp_psd = periodogram(x[:, iS],
                                      fs=fs,  # sample rate
                                      nfft=nfft,
                                      window=window,  # apply a Hanning window before taking the DFT
                                      detrend=detrend,
                                      scaling="spectrum",
                                      return_onesided=True,
                                      axis=0)
        f = interp1d(f, temp_psd)
        temp_psd = f(freq)
        if output == "density":
            temp_psd /= (np.sum(temp_psd) * df)
        psd.append(temp_psd)
    # Stack them to a ndarray
    psd = np.stack(psd, axis=1)
    if output == "energy":
        return np.sum(psd, axis=0)
    else:
        if log_scale:
            psd = np.log(psd)
        return psd, freq


def time_spectral_analysis(x, fs, freq=None, mode="psd", nfft=None, window='hanning', nperseg=256, detrend='constant',
                           noverlap=None, f_low=10.0, calculate_psd=True, log_scale=False):
    # TODO: add a Continuous Wavelet Transform implementation
    if freq is None:
        freq = np.linspace(f_low, nperseg, nperseg - f_low - 1)
    stf = []
    for iS in range(x.shape[1]):
        f, t, temp_s = spectrogram(x[:, iS], fs=fs, nperseg=nperseg, nfft=nfft, window=window, mode=mode,
                                   noverlap=noverlap, detrend=detrend, return_onesided=True, scaling='spectrum', axis=0)
        t_mesh, f_mesh = np.meshgrid(t, f, indexing="ij")
        temp_s = griddata((t_mesh.flatten(), f_mesh.flatten()), temp_s.T.flatten(),
                          tuple(np.meshgrid(t, freq, indexing="ij")), method='linear')
        stf.append(temp_s)
    # Stack them to a ndarray
    stf = np.stack(stf, axis=2)
    if log_scale:
        stf = np.log(stf)
    if calculate_psd:
        psd, _ = spectral_analysis(x, fs, freq=freq, method="periodogram", output="spectrum", nfft=nfft, window=window,
                                   nperseg=nperseg, detrend=detrend, noverlap=noverlap, log_scale=log_scale)
        return stf, t, freq, psd
    else:
        return stf, t, freq
