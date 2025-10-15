import numpy as np
import scipy.signal as sgl


def filter_line(signal_raw, filt=None, fs=None):
    """Filter an array using a Butterworth filter."""
    #todo: verify that filter is working correctly
    #todo add more filters
    #todo: consider using kineticstoolkit

    if filt is None:
        filt = {'ftype': 'butter',
                'order': 4,
                'cutoff': 10,
                'btype': 'lowpass',
                'filtfilt': True}
        if fs is None:
            raise ValueError('fs is required if no filt is specified')

    else:
        if 'fs' not in filt:
            raise ValueError('fs is a required key of filt')

    # Normalize filter type strings
    if filt['ftype'] == 'butterworth':
        filt['ftype'] = 'butter'
    if filt['btype'] is 'low':
        filt['btype'] = 'lowpass'
    if filt['btype'] is 'high':
        filt['btype'] = 'highpass'

    # Extract parameters
    ftype = filt['ftype']
    order = filt['order']
    cutoff = filt['cutoff']
    btype = filt['btype']
    filtfilt = filt['filtfilt']
    fs = filt['fs']

    # prepare normalized cutoff(s)
    nyq = 0.5 * fs
    norm_cutoff = np.atleast_1d(np.array(cutoff) / nyq)

    if ftype is 'butter':
        signal_filtered = kt_butter(ts=signal_raw, fc=norm_cutoff, fs=fs, order=order, btype=btype, filtfilt=filtfilt)
    else:
        raise NotImplementedError(f"Filter type '{ftype}' not implemented.")

    return signal_filtered


def kt_butter(ts, fc, fs, order=2, btype='lowpass', filtfilt=True):
    """
    Apply a Butterworth filter to data.

    Parameters
    ----------
    ts, ndarray, 1d.
    fc, Cut-off frequency in Hz. This is a float for single-frequency filters
        (lowpass, highpass), or a tuple of two floats (e.g., (10., 13.)
        for two-frequency filters (bandpass, bandstop)).
    order, Optional. Order of the filter. Default is 2.
    btype, Optional. Can be either "lowpass", "highpass", "bandpass" or
        "bandstop". Default is "lowpass".
    filtfilt, Optional. If True, the filter is applied two times in reverse direction
        to eliminate time lag. If False, the filter is applied only in forward
        direction. Default is True.

    Returns
    -------
    ts_f,  A copy of the input data which each data being filtered.
    
    Notes: 
    - This code was adapted from kineticstoolkit Thanks @felxi
    """

    sos = sgl.butter(order, fc, btype, analog=False, output="sos", fs=fs)

    # Filter
    if filtfilt:
        ts_f = sgl.sosfiltfilt(sos, ts, axis=0)
    else:
        ts_f = sgl.sosfilt(sos,ts, axis=0)

    return ts_f