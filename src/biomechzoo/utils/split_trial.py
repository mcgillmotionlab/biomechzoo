def split_trial(data, start_event_indx, end_event_indx):
    # todo check index problem compared to matlab start at 0 or 1
    data_new = data.copy()

    for key, value in data_new.items():
        if key == 'zoosystem':
            continue

        # Slice the line data
        data_new[key]['line'] = value['line'][start_event_indx:end_event_indx]

        # Update events if present
        if 'event' in value:
            new_events = {}
            for evt_name, evt_val in value['event'].items():
                event_frame = evt_val[0]
                # Check if event falls within the new window
                if start_event_indx <= event_frame < end_event_indx:
                    # Adjust index relative to new start
                    new_events[evt_name] = [event_frame - start_event_indx, 0, 0]
            data_new[key]['event'] = new_events

    return data_new
