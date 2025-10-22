import warnings
import copy
from biomechzoo.biomech_ops.normalize_line import normalize_line


def normalize_data(data, nlength=101):
    """normalize all channels in the loaded zoo dict to nlen.
    Arguments
        data: dict, loaded zoo file
        nlength: int: new length of data. Default = 101, usually a movement cycle
    Returns:
        None
    Notes:
        -It is often needed to partition data to a single cycle first (see partition_data)
    """

    # normalize channel length
    data_new = copy.deepcopy(data)
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            ch_data_line = ch_data['line']
            ch_data_event = ch_data['event']
            ch_data_normalized = normalize_line(ch_data_line, nlength)
            data_new[ch_name]['line'] = ch_data_normalized
            data_new[ch_name]['event'] = ch_data_event
    warnings.warn('event data have not been normalized')

    # update zoosystem
    # todo: update all relevant zoosystem meta data related to data lengths
    warnings.warn('zoosystem data have not been fully updated')
    if 'Video' in data['zoosystem']:
        data['zoosystem']['Video']['CURRENT_END_FRAME'] = nlength
    if 'Analog' in data['zoosystem']:
        data['zoosystem']['Analog']['CURRENT_END_FRAME'] = nlength

    return data_new
