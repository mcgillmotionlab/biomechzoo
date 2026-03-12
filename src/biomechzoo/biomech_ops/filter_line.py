import numpy as np
import scipy.signal as sgl


def filter_line(signal_raw, filt=None, fs=None):
    """
    Filter a 1-D signal array using a Butterworth filter.

    Parameters
    ----------
    signal_raw : ndarray
        Raw 1-D signal to be filtered.
    filt : dict, optional
        Filter parameter dictionary with keys:
        - 'ftype' : str — filter type, e.g. 'butter' (default)
        - 'order' : int — filter order (default: 4)
        - 'cutoff' : float or tuple — cutoff frequency in Hz
        - 'btype' : str — 'lowpass', 'highpass', 'bandpass', or 'bandstop'
        - 'filtfilt' : bool — zero-phase filtering if True
        - 'fs' : float — sampling frequency in Hz (required)
    fs : float, optional
        Sampling frequency in Hz. Only used when filt is not provided.

    Returns
    -------
    signal_filtered : ndarray
        Filtered signal array.

    Raises
    ------
    ValueError
        If 'fs' is not provided when filt is None, or if 'fs' key is
        missing from the filt dictionary.
    NotImplementedError
        If a filter type other than 'butter' is specified.
    """
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
        [b, a] = sgl.butter(N=order, Wn=norm_cutoff, btype=btype, )
        signal_filtered = sgl.filtfilt(b, a, signal_raw)
    else:
        raise NotImplementedError(f"Filter type '{ftype}' not implemented.")

    return signal_filtered


def kt_butter(ts, fc, fs, order=2, btype='lowpass', filtfilt=True):
    """
    Apply a Butterworth filter to a time series.

    Parameters
    ----------
    ts : ndarray
        1-D input time series to filter.
    fc : float or tuple of float
        Cut-off frequency in Hz. Use a float for lowpass/highpass filters,
        or a tuple of two floats (e.g., ``(10., 13.)``) for bandpass/bandstop.
    fs : float
        Sampling frequency in Hz.
    order : int, optional
        Order of the Butterworth filter. Default is 2.
    btype : {'lowpass', 'highpass', 'bandpass', 'bandstop'}, optional
        Type of filter. Default is 'lowpass'.
    filtfilt : bool, optional
        If True, the filter is applied twice (forward and backward) to
        eliminate phase lag. If False, only a forward pass is applied.
        Default is True.

    Returns
    -------
    ts_f : ndarray
        Filtered copy of the input time series.

    Notes
    -----
    This function was adapted from kineticstoolkit. Thanks @felxi.
    """

    sos = sgl.butter(order, fc, btype, analog=False, output="sos", fs=fs)

    # Filter
    if filtfilt:
        ts_f = sgl.sosfiltfilt(sos, ts, axis=0)
    else:
        ts_f = sgl.sosfilt(sos,ts, axis=0)

    return ts_f