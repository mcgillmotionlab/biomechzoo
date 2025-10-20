import copy
from biomechzoo.utils.findfield import findfield


def split_trial(data, start_event, end_event):
    # todo check index problem compared to matlab start at 0 or 1
    data_new = copy.deepcopy(data)

    start_event_indx, _ = findfield(data_new, start_event)
    end_event_indx, _ = findfield(data_new, end_event)

    for key, value in data_new.items():
        if key == 'zoosystem':
            continue

        # Slice the line data
        trial_length = len(data_new[key]['line'])
        if trial_length > end_event_indx[0]:
            data_new[key]['line'] = value['line'][start_event_indx[0]:end_event_indx[0]]
        else:
            print('skipping split trial since event is outside range of data')
            return None

        # Update events if present
        # if 'event' in value:
        #     new_events = {}
        #     for evt_name, evt_val in value['event'].items():
        #         event_frame = evt_val[0]
        #         # Check if event falls within the new window
        #         if start_event_indx <= event_frame < end_event_indx:
        #             # Adjust index relative to new start
        #             new_events[evt_name] = [event_frame - start_event_indx, 0, 0]
        #     data_new[key]['event'] = new_events

    return data_new
