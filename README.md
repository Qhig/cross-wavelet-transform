#### CODE for MEASURING SEISMIC TRAVEL-TIME CHANGES with the WAVELET METHOD
#### Contact: Shujuan Mao (maos@mit.edu) and Aurélien Mordret (aurelien.mordret@univ-grenoble-alpes.fr)

This package contains codes and test data for measuring seismic travel-time shifts in the time-frequency domain using the wavelet cross-spectrum analysis. 

Python 3 and the PyCWT packages from https://github.com/regeirk/pycwt are needed to run the codes

You can use pip to install this package :

    $ pip install pycwt

Contents in this package:

—— cwt.py
    The core function to calculate dt in the time-frequency domain by wavelet cross-spectrum analysis.

—— plotting_example.py 
    An example of using the cwt function on synthetic data. Plots come with one click.

—— time.npy
   fs.npy
   ori_waveform.npy
   new_waveform.npy
    Two synthetic waveforms for testing the codes, ori_waveform and new_waveform
    The synthetic seismograms are generated using velocity models by a homogeneous background superimposed with random heterogeneities. The perturbation between the current and reference velocity models is a 0.05% homogeneous dv/v throughout the medium. (If interested, see Section 3.1 in the following reference for more details.)

Reference: S.Mao, A.Mordret, M.Campillo, H.Fang, R.D.van der Hilst, (2019), On the Measurement of Seismic Travel-Time Changes in the Time-Frequency Domain with Wavelet Cross-Spectrum Analysis, GJI, In Review.
Torrence, C. and Compo, G. P.. A Practical Guide to Wavelet Analysis.


