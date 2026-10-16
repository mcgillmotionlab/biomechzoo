from typing import Dict, Any
from biomechzoo.utils.findfield import findfield
import warnings
import copy
import numpy as np


def partition_data(
        data: Dict[str, Any], evt_start: str, evt_end: str,
) -> Dict[str, Any]:
    """
    Partition data for all channels between two specified events.

    This function extracts a subset of data between a start event and an end event,
    trimming all channel data to this time range. Event indices within channels are
    adjusted relative to the new partitioned start position.

    Parameters
    ----------
    data : dict of str to Any
        Biomechanical data dictionary containing channels and events.
    evt_start : str
        Name of the starting event for partitioning.
    evt_end : str
        Name of the ending event for partitioning.

    Returns
    -------
    data_new : dict of str to Any
        Deep copy of input data with channels partitioned between the two events.

    Raises
    ------
    ValueError
        If either start or end event is not found in the data.

    Notes
    -----
    Event indices are automatically adjusted relative to the new partition start.
    Events marked with index 999 (outlier markers) are preserved unchanged.

    Channels that cause IndexError or ValueError during partitioning will be
    skipped with a warning message.
    """

    # extract event values
    e1, start_channel = findfield(data, evt_start)
    e2, end_channel = findfield(data, evt_end)

    if e1 is None or e2 is None or len(e1) == 0 or len(e2) == 0:
        raise ValueError("Event not found: evt_start='{0}' returned {1}, evt_end='{2}' returned {3}".format(evt_start, e1, evt_end, e2))

    start_frame = int(e1[0])
    end_frame = int(e2[0])
    if (
        start_frame < 0
        or end_frame > len(data[start_channel]['line'])
        or end_frame > len(data[end_channel]['line'])
    ):
        raise ValueError('Partition event indices are outside the data range.')
    if start_frame >= end_frame:
        raise ValueError('Start event must occur before end event.')

    data_new = copy.deepcopy(data)
    for ch_name, ch_data in sorted(data_new.items()):
        if ch_name != 'zoosystem':
            r = ch_data['line']
            try:
                if r.ndim == 1:
                    data_new[ch_name]['line'] = r[start_frame:end_frame]
                else:
                    data_new[ch_name]['line'] = r[start_frame:end_frame, :]
            except (IndexError, ValueError) as e:
                # IndexError: if e1[0]:e2[0] goes beyond the available indices
                # ValueError: less likely, but may arise with shape mismatches
                warnings.warn('Skipping {0} due to error: {1}'.format(ch_name, e))

            # partition events
            events = ch_data['event']
            if len(events)>0:
                for event_name, value in events.items():
                    original_frame = int(value[0])
                    if original_frame == 999:
                        continue  # do not change outlier markers
                    else:
                        arr = np.array(data_new[ch_name]['event'][event_name], dtype=np.int32)
                        arr[0] = original_frame - start_frame
                        data_new[ch_name]['event'][event_name] = arr

    return data_new
