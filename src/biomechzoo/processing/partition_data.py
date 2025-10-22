from biomechzoo.utils.findfield import findfield
import warnings
import copy
import numpy as np


def partition_data(data, evt_start, evt_end):
    """ partition data for all channels between events evt_start and evt_end"""

    # extract event values
    e1, _ = findfield(data, evt_start)
    e2, _ = findfield(data, evt_end)

    if e1 is None or e2 is None or len(e1) == 0 or len(e2) == 0:
        raise ValueError(f"Event not found: evt_start='{evt_start}' returned {e1}, evt_end='{evt_end}' returned {e2}")

    # convert to int and get first value
    e1 = int(e1[0])
    e2 = int(e2[0])

    data_new = copy.deepcopy(data)
    for ch_name, ch_data in sorted(data_new.items()):
        if ch_name != 'zoosystem':
            r = ch_data['line']
            try:
                if r.ndim == 1:
                    data_new[ch_name]['line'] = r[e1:e2]
                else:
                    data_new[ch_name]['line'] = r[e1:e2, :]
            except (IndexError, ValueError) as e:
                # IndexError: if e1[0]:e2[0] goes beyond the available indices
                # ValueError: less likely, but may arise with shape mismatches
                warnings.warn(f"Skipping {ch_name} due to error: {e}")

            # partition events
            events = ch_data['event']
            for event_name, value in events.items():
                original_frame = int(value[0])
                if original_frame == 999:
                    continue  # do not change outlier markers
                else:
                    arr = np.array(data_new[ch_name]['event'][event_name], dtype=np.int32)
                    arr[0] = original_frame - e1
                    data_new[ch_name]['event'][event_name] = arr

    return data_new
