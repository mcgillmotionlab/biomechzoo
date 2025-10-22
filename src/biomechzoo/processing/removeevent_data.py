import copy
import warnings
from biomechzoo.utils.findfield import findfield

def removeevent_data(data, events, mode='remove'):
    """
    Remove or keep specified events in all channels of a zoo dictionary.

    Parameters
    ----------
    data : dict
        Zoo data loaded from a file
    events : list of str
        Events to remove or keep
    mode : str
        'remove' or 'keep'

    Returns
    -------
    dict
        Modified zoo dictionary with events removed or kept
    """
    if mode not in ['remove', 'keep']:
        raise ValueError("mode must be 'remove' or 'keep'.")

    if isinstance(events, str):
        events = [events]

    # check if any events are not present
    valid_events = []
    for evt in events:
        e, _ = findfield(data, evt)
        if e is None:
            warnings.warn('Could not find event {} in zoo file, skipping'.format(evt))
        else:
            valid_events.append(evt)
    events = valid_events

    data_new = copy.deepcopy(data)
    channels = sorted([ch for ch in data_new if ch != 'zoosystem'])
    for ch in channels:
        event_dict = data_new[ch].get('event', {})
        events_to_remove = []

        for evt in list(event_dict.keys()):
            if mode == 'remove' and evt in events:
                events_to_remove.append(evt)
            elif mode == 'keep' and evt not in events:
                events_to_remove.append(evt)

        for evt in events_to_remove:
            event_dict.pop(evt, None)
            # print('Removed event "{}" from channel "{}"'.format(evt, ch))

        data_new[ch]['event'] = event_dict

    return data_new
