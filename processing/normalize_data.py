import warnings
from processing.normalize_line import normalize_line


def normalize_data(data, nlength=101):
    """File-level: normalize all channels in the loaded zoo dict to nlen."""

    data_new = data.copy()
    normalized_channels = {}
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            ch_data_line = ch_data['line']
            ch_data_event = ch_data['event']
            ch_data_normalized = normalize_line(ch_data_line, nlength)
    data_new[ch_name]['line'] = ch_data_normalized
    data_new[ch_name]['event'] = ch_data_event
    warnings.warn('event data have not been normalized')
    return data_new
