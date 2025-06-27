from utils.findfield import findfield
import warnings

def partition_data(data, evt_start, evt_end):
    """ partition data for all channels between events evt_start and evt_end"""

    # extract event values
    e1, _ = findfield(data,evt_start)
    e2, _ = findfield(data,evt_end)

    data_new = data.copy()
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            try:
                data_new[ch_name]['line'] = ch_data[e1[0]:e2[0], :]
            except (IndexError, ValueError) as e:
                # IndexError: if e1[0]:e2[0] goes beyond the available indices
                # ValueError: less likely, but may arise with shape mismatches
                warnings.warn(f"Skipping {ch_name} due to error: {e}")

            # partition events
            events = ch_data['event']
            for event_name, value in events.items():
                original_frame = value[0]
                if original_frame == 1:
                    continue  # leave index 1 as is (per MATLAB version)
                elif original_frame == 999:
                    continue  # do not change outlier markers
                else:
                    new_frame = original_frame - e1[0] + 1
                    data_new[ch_name]['event'][event_name][0] = new_frame

    return data_new


def _partition_line(arr, evt_start, evt_end):
    arr_new = arr[evt_start:evt_end, :]
    return arr_new

def _partition_event(event_dict, evt_start, evt_end, arr_len):

    event_dict_new = {}
    for event, event_val in event_dict:
        event_val_new =
        event_dict_new[event] =



    return event_dict_new
