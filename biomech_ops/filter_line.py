import numpy as np
from scipy.signal import butter, filtfilt


def filter_line(signal_raw, filt):
    """ filter an array

    Arguments
    ----------
    signal_raw : n, or n x 3 array signal to be filtered
    filt : dict, optional
        Dictionary specifying filter parameters. Keys may include:
        - 'type': 'butter' (default)
        - 'order': filter order (default: 4)
        - 'cutoff': cutoff frequency or tuple (Hz)
        - 'btype': 'low', 'high', 'bandpass', 'bandstop' (default: 'low')
        - 'fs' frequency

    Returns
    -------
    signal_filtered: filtered version of signal_raw"""
    # todo allow for missing frequency to be obtained from zoosystem metadata
    if filt is None:
        filt = {}
    if filt['type'] is 'butterworth':
        filt['type'] = 'butter'
    # Set default filter parameters
    ftype = filt.get('type', 'butter')
    order = filt.get('order', 4)
    cutoff = filt.get('cutoff', None)
    btype = filt.get('btype', 'low')
    fs = filt.get('fs', None)

    if ftype != 'butter':
        raise NotImplementedError(f"Filter type '{ftype}' not implemented.")

    if fs is None:
        raise ValueError("Sampling frequency 'fs' must be specified in filt.")

    if cutoff is None:
        raise ValueError("Cutoff frequency 'cutoff' must be specified in filt.")

    nyq = 0.5 * fs
    norm_cutoff = np.array(cutoff) / nyq

    b, a = butter(order, norm_cutoff, btype=btype, analog=False)

    if signal_raw.ndim == 1:
        signal_filtered = filtfilt(b, a, signal_raw)
    else:
        # Apply filter to each column if multivariate
        signal_filtered = np.array([filtfilt(b, a, signal_raw[:, i]) for i in range(signal_raw.shape[1])]).T

    return signal_filtered


if __name__ == '__main__':
    """ -------TESTING--------"""
    import os
    import matplotlib.pyplot as plt
    from utils.zload import zload
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')
    data = zload(fl)
    data = data['data']
    signal_raw = data['ForceFz1']['line']
    filt = {'type': 'butterworth',
            'order': 3,
            'cutoff': 20,
            'btype': 'low',
            'fs': data['zoosystem']['Analog']['Freq']
            }
    signal_filtered = filter_line(signal_raw, filt)

    # now plot
    plt.figure(figsize=(10, 4))
    plt.plot(signal_raw, label='Raw', alpha=0.6)
    plt.plot(signal_filtered, label='Filtered', linewidth=2)
    plt.xlabel('Frame')
    plt.ylabel('Amplitude')
    plt.title('Testing filter_line')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


