import copy
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
        resampled to ``nlength`` samples and event frame indices scaled
        to the new length.

    Notes
    -----
    It is often necessary to partition data to a single cycle first
    (see: func:`partition_data`) before normalizing.

    Event values and placeholders are preserved. Current end-frame
    metadata are updated; acquisition and source metadata are unchanged.
    """

    # normalize channel length
    data_new = copy.deepcopy(data)
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            ch_data_line = ch_data['line']
            ch_data_event = ch_data.setdefault('event', {})
            if ch_data_line is int:
                raise ValueError('Channel line must be a numpy array.')
            original_length = ch_data_line.shape[0]
            ch_data_normalized = normalize_line(ch_data_line, nlength)
            data_new[ch_name]['line'] = ch_data_normalized
            for event in ch_data_event.values():
                event_frame = event[0]
                if event_frame == 999:
                    continue
                if original_length == 1 or nlength == 1:
                    event[0] = 0
                else:
                    event[0] = round(
                        event_frame * (nlength - 1) / (original_length - 1)
                    )
            data_new[ch_name]['event'] = ch_data_event

    # Acquisition metadata such as sampling frequency and source frame
    # counts describe the original recording and remain unchanged.
    if 'Video' in data_new['zoosystem']:
        data_new['zoosystem']['Video']['CURRENT_END_FRAME'] = nlength
    if 'Analog' in data_new['zoosystem']:
        data_new['zoosystem']['Analog']['CURRENT_END_FRAME'] = nlength

    return data_new
