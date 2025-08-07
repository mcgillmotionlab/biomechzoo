from biomechzoo.utils.findfield import findfield


def get_split_events(data, first_event_name):
    """ splits lengthy trials containing n cycles into n trials based on side"""

    # find all events, events should follow style name1, name2, etc..
    split_events = []
    i = 1
    _, channel_name = findfield(data, first_event_name)
    if channel_name is None:
        return None

    event_name_root = first_event_name[0:-1]
    while True:
        key = f"{event_name_root}{i}"
        if key in data[channel_name]['event']:
            split_events.append(data[channel_name]['event'][key][0])
            i += 1
        else:
            break

    n_segments = len(split_events) - 1
    if n_segments < 1:
        print("Not enough {} events to split.".format(event_name_root))
        return

    return split_events

