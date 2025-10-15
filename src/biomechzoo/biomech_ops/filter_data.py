from biomechzoo.biomech_ops.filter_line import filter_line


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
        - 'ftype': 'butter' (default)
        - 'order': filter order (default: 4)
        - 'cutoff': cutoff frequency or tuple (Hz)
        - 'btype': 'low', 'high', 'bandpass', 'bandstop' (default: 'lowpass')

    Returns
    -------
    dict
        The updated data dictionary with filtered channels.
    """

    if filt is None:
        filt = {'ftype': 'butter',
                'order': 4,
                'cutoff': 10,
                'btype': 'lowpass',
                'filtfilt': True}

    if isinstance(ch, str):
        ch = [ch]

    # loop through all channels and filter
    for c in ch:
        if c not in data:
            raise KeyError('Channel {} not found in data'.format(c))

        if 'fs' not in filt:

            video_channels = data['zoosystem']['Video']['Channels']
            analog_channels = data['zoosystem']['Analog']['Channels']

            if c in analog_channels:
                filt['fs'] = data['zoosystem']['Analog']['Freq']
            elif c in video_channels:
                filt['fs'] =  data['zoosystem']['Video']['Freq']
            else:
                raise ValueError('Channel not analog or video')

        signal_raw = data[c]['line']
        signal_filtered = filter_line(signal_raw=signal_raw, filt=filt)
        data[c]['line'] = signal_filtered

    return data
