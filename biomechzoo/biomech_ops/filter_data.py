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

    analog_channels = data['zoosystem']['Analog']['Channels']
    if analog_channels:
        analog_freq = data['zoosystem']['Analog']['Freq']
    video_channels = data['zoosystem']['Video']['Channels']
    if video_channels:
        video_freq = data['zoosystem']['Video']['Freq']

    for c in ch:
        if c not in data:
            raise KeyError('Channel {} not found in data'.format(c))

        if 'fs' not in filt:
            if c in analog_channels:
                filt['fs'] = analog_freq
            elif c in video_freq:
                filt['fs'] = video_freq
            else:
                raise ValueError('frequency not provided and cannot be inferred from zoosystem for channel'.format(c))

        signal_raw = data[c]['line']
        signal_filtered = filter_line(signal_raw, filt)
        data[c]['line'] = signal_filtered

    return data
