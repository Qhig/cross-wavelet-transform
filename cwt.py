###########################################################################

## CFS Function:

# Using wavelet cross-spectrum to calculate the lapse-time and frequency-dependent
# travel-time changes between two time series.


## USAGE

#  WXamp, WXspec, WXangle, Wcoh, WXdt, freqs, coi = cfs(trace_ref,trace_current,fs,ns,nt,vpo,freqmin,freqmax,nptsfreq)


## Input

#    trace_ref,trace_current : Two vectors, reference and current time series.
#    fs : Sampling Frequency // Positive scalar, sampling frequency.
#    ns : NumScalesToSmooth // Positive integer, indicting the length of boxcar window.
#    nt : DegTimeToSmooth // Positive scalar, indicating the length of the Gaussian window.
#    vpo : VoicesPerOctave //  Even integer from 4 to 48, indicates how fine the frequency is discretized.
#                              Recommanded to be no less than 10.
#    freqmin : The ending value of the frequency vector, in Hz.
#    freqmax : The starting value of the frequency vector, in Hz.
#    nptsfreq : Number of frequency samples to generate between the starting and ending value.

## OUTPUT

#    WXamp : Matrix of amplitude product of two CWT in time-frequency domain
#    WXspec : Complex-valued matrix, the wavelet cross-spectrum
#    WXangle : Matrix of the angle of the complex argument in WXspec
#    Wcoh: Matrix of wavelet coherence
#    WXdt : Matrix of time difference and phase difference, respectively
#                  between the two input time series in time-frequency domain.
#                  !!!! This WXdt is obtained with wrapped phase difference.
#                  If needed, the user can also produce time difference with
#                  unwrapped phase from WXangle. !!!!
#    freqs : Vector of frequencies used in CWT, in Hz
#    coi: Cone of influence, indicating areas affected by edge effects.


## EXAMPLE:

#    WXamp, WXspec, WXangle, Wcoh, WXdt, freqs, coi = cfs(trace_ref,trace_current,fs,ns,nt,vpo,freqmin,freqmax,nptsfreq)


##    Authors: Shujuan Mao (maos@mit.edu) & Aurélien Mordret (mordret@mit.edu) & Higueret Quentin (quentin.higueret@univ-grenoble-alpes.fr)

#     Created: Feb., 2021


##    Reference:

#           S.Mao, A.Mordret, M.Campillo, H.Fang, R.D. van der Hilst,(2019),
#           On the Measurement of Seismic Travel-Time Changes in the
#           Time-Frequency Domain with Wavelet Cross-Spectrum Analysis,
#           GJI, In Review.
#           Torrence, C. and Compo, G. P.. A Practical Guide to Wavelet Analysis

##    Copyright (c) 2019, Shujuan Mao and Aurélien Mordret, covered by MIT License.

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.
#
###########################################################################


## Import modules
# The PyCWT package must be installed on the system

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot, transforms
from scipy.io import loadmat
import pycwt as wavelet
from pycwt.helpers import find
from scipy.signal import convolve2d
import warnings


## Disable Warnings

warnings.filterwarnings('ignore')


## conv2 function

# Returns the two-dimensional convolution of matrices x and y
def conv2(x, y, mode='same'):
    return np.rot90(convolve2d(np.rot90(x, 2), np.rot90(y, 2), mode=mode), 2)


## nextpow2 function

# Returns the exponents p for the smallest powers of two that satisfy the relation  : 2**p >= abs(x)
def nextpow2(x):
    res = np.ceil(np.log2(x))
    return res.astype('int')

## Smoothing function

# Smooth the dataset
def smoothCFS(cfs, scales, dt, ns, nt):
    N = cfs.shape[1]
    npad = 2 ** nextpow2(N)
    omega = np.arange(1, np.fix(npad / 2) + 1, 1).tolist()
    omega = np.array(omega) * ((2 * np.pi) / npad)
    omega_save = -omega[int(np.fix((npad - 1) / 2)) - 1:0:-1]
    omega_2 = np.concatenate((0., omega), axis=None)
    omega_2 = np.concatenate((omega_2, omega_save), axis=None)
    omega = np.concatenate((omega_2, -omega[0]), axis=None)
    # Normalize scales by DT because we are not including DT in the angular frequencies here.
    # The smoothing is done by multiplication in the Fourier domain.
    normscales = scales / dt

    for kk in range(0, cfs.shape[0]):
        F = np.exp(-nt * (normscales[kk] ** 2) * omega ** 2)
        smooth = np.fft.ifft(F * np.fft.fft(cfs[kk - 1], npad))
        cfs[kk - 1] = smooth[0:N]
    # Convolve the coefficients with a moving average smoothing filter across scales.
    H = 1 / ns * np.ones((ns, 1))

    cfs = conv2(cfs, H)
    return cfs


## cfs function

def cfs(trace_ref, trace_current, fs, ns, nt, vpo, freqmin, freqmax, nptsfreq):
    # Choosing a Morlet wavelet with a central frequency w0 = 6
    mother = wavelet.Morlet(6.)
    # nx represent the number of element in the trace_current array
    nx = np.size(trace_current)
    x_reference = np.transpose(trace_ref)
    x_current = np.transpose(trace_current)
    # Sampling interval
    dt = 1 / fs
    # Spacing between discrete scales, the default value is 1/12
    dj = 1 / vpo
    # Number of scales less one, -1 refers to the default value which is J = (log2(N * dt / so)) / dj.
    J = -1
    # Smallest scale of the wavelet, default value is 2*dt
    s0 = 2 * dt  # Smallest scale of the wavelet, default value is 2*dt

    # Creation of the frequency vector that we will use in the continuous wavelet transform
    freqlim = np.linspace(freqmax, freqmin, num=nptsfreq, endpoint=True, retstep=False, dtype=None, axis=0)

    # Calculation of the two wavelet transform independently
    # scales are calculated using the wavelet Fourier wavelength
    # coi : Cone of influence, indicating areas affected by edge effects
    # fft : Normalized fast Fourier transform of the input trace
    # fftfreqs : Fourier frequencies for the calculated FFT spectrum.
    cwt_reference, scales, freqs, coi, fft, fftfreqs = wavelet.cwt(x_reference, dt, dj, s0, J, mother, freqs=freqlim)
    cwt_current, _, _, _, _, _ = wavelet.cwt(x_current, dt, dj, s0, J, mother, freqs=freqlim)

    scales = np.array([[kk] for kk in scales])
    invscales = np.kron(np.ones((1, nx)), 1 / scales)
    cfs1 = smoothCFS(invscales * abs(cwt_reference) ** 2, scales, dt, ns, nt)
    cfs2 = smoothCFS(invscales * abs(cwt_current) ** 2, scales, dt, ns, nt)
    crossCFS = cwt_reference * np.conj(cwt_current)
    WXamp = abs(crossCFS)
    # cross-wavelet transform operation with smoothing
    crossCFS = smoothCFS(invscales * crossCFS, scales, dt, ns, nt)
    WXspec = crossCFS / (np.sqrt(cfs1) * np.sqrt(cfs2))
    WXangle = np.angle(WXspec)
    Wcoh = abs(crossCFS) ** 2 / (cfs1 * cfs2)
    pp = 2 * np.pi * freqs
    pp2 = np.array([[kk] for kk in pp])
    WXdt = WXangle / np.kron(np.ones((1, nx)), pp2)
    # Transformation of the coi vector for plotting purpose
    coi = [freqs[0] - ll if (ll < freqs[0]) else -1 for ll in coi]

    return WXamp, WXspec, WXangle, Wcoh, WXdt, freqs, coi


