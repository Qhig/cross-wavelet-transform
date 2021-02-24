###########################################################################

## Plotting Example

###########################################################################


## Import modules

import numpy as np
import matplotlib.pyplot as plt

# Import the cross-wavelet transform function from the cwt.py file
from cwt import cfs

## Loading datas

time = np.load('time.npy')
ori_waveform = np.load('ori_waveform.npy')
new_waveform = np.load('new_waveform.npy')
fs = np.load('fs.npy')


## Usage of the cfs function
WXamp, WXspec, WXangle, Wcoh, WXdt, freqs, coi = cfs(ori_waveform, new_waveform, fs, 3, 0.25, 10, 0.5, 7, 100)


## Plotting

plt.figure(1)

plt.subplot(2, 2, 1)
plt.tight_layout()
plt.pcolormesh(time, freqs, WXdt, cmap='jet_r', edgecolors='none')
plt.clim([-0.02, 0.01])
plt.colorbar()
plt.plot(time, coi, 'w--', linewidth=5)
plt.ylim(freqs[-1], freqs[0])
plt.xlim(4, 25)
plt.title('Smoothed Time difference', fontsize=13)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')

plt.subplot(2, 2, 2)
plt.tight_layout()
plt.pcolormesh(time, freqs, Wcoh, cmap='jet', edgecolors='none')
plt.clim([0.985, 1])
plt.colorbar()
plt.plot(time, coi, 'w--', linewidth=5)
plt.ylim(freqs[-1], freqs[0])
plt.xlim(4, 25)
plt.title('Wavelet Coherence', fontsize=13)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')

plt.subplot(2, 2, 3)
plt.tight_layout()
plt.pcolormesh(time, freqs, np.log(WXamp), cmap='jet', edgecolors='none')
plt.clim([-50, 0])
plt.colorbar()
plt.plot(time, coi, 'w--', linewidth=5)
plt.ylim(freqs[-1], freqs[0])
plt.xlim(4, 25)
plt.title('(Logarithmic) Amplitude', fontsize=13)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')

plt.show()
