import numpy as np
from filter_line import filter_line


def filter_data(data, ch, filt=None):
    """
    Filter one or more channels from a zoo data dictionary using specified filter parameters.

    Arguments
    ----------
    data : dict
        The zoo data dictionary containing signal channels.
    ch : str or list of str
        The name(s) of the channel(s) to filter.
    filt : dict, optional
        Dictionary specifying filter parameters. Keys may include:
        - 'type': 'butter' (default)
        - 'order': filter order (default: 4)
        - 'cutoff': cutoff frequency or tuple (Hz)
        - 'btype': 'low', 'high', 'bandpass', 'bandstop' (default: 'low')

    Returns
    -------
    dict
        The updated data dictionary with filtered channels.
    """

    if filt is None:
        filt = {}

    if isinstance(ch, str):
        ch = [ch]

    for c in ch:
        if c not in data:
            raise KeyError('Channel {} not found in data'.format(c))

        signal_raw = data[c]['line']
        signal_filtered = filter_line(signal_raw, filt)
        data[c]['line'] = signal_filtered

    return data
