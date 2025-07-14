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

    Returns
    -------
    signal_filtered: filtered version of signal_raw"""

    if filt is None:
        filt = {}

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




