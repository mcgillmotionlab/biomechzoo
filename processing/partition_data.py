def partition_data(data, evt_start, evt_end):
    data_new = data.copy()
    for ch_name, ch_data in data_new.items():
        if ch_name != 'zoosystem':
            ch_data_line = _partition_line(ch_data['line'], evt_start, evt_end)
            ch_data_events = _partition_event(ch_data['event'], evt_start, evt_end)
            ch_data_normalized = normalize_line(ch_data_line, nlength)
    data_new[ch_name]['line'] = ch_data_normalized
    data_new[ch_name]['event'] = ch_data_event
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
