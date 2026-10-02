import copy
import warnings
from typing import Dict

from biomechzoo.biomech_ops.normalize_line import normalize_line


def normalize_data(data: Dict, nlength: int = 101) -> Dict:
    """
    Normalize all channels in a zoo data dictionary to a target length.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    nlength : int, optional
        Target number of samples after normalization. Default is 101,
        which corresponds to 0-100% of a movement cycle.

    Returns
    -------
    data_new : dict
        Deep copy of the input data with all channel 'line' arrays
        resampled to ``nlength`` samples.

    Notes
    -----
    It is often necessary to partition data to a single cycle first
    (see :func:`partition_data`) before normalizing.

    Event data and zoosystem metadata are not fully updated in the
    current implementation; warnings are issued accordingly.
    """

    # normalize channel length
    data_new = copy.deepcopy(data)
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            ch_data_line = ch_data['line']
            # ch_data_event = ch_data['event']
            ch_data_event = ch_data.setdefault('event', {})
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
