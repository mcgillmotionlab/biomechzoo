import copy
from typing import Dict, Optional, Any
from biomechzoo.utils.findfield import findfield


def split_trial_data(
    data: Dict[str, Any],
    start_event: str,
    end_event: str
) -> Optional[Dict[str, Any]]:
    """
    Split trial data between two specified events, extracting a sub-trial.

    This function extracts a portion of trial data between a start event and an end
    event (inclusive), creating a new data structure with adjusted time indices.
    All channel data is sliced to this range, and event indices are recalculated
    relative to the new start position.

    :param data: Biomechanical data dictionary loaded from a zoo file.
    :type data: Dict[str, Any]
    :param start_event: Name of the event marking the beginning of the sub-trial.
    :type start_event: str
    :param end_event: Name of the event marking the end of the sub-trial.
    :type end_event: str
    :return: Deep copy of input data containing only the data between the two events,
             or None if the end event is outside the data range.
    :rtype: Optional[Dict[str, Any]]
    :raises ValueError: If either start_event or end_event is not found in the data.

    .. note::
       The end event index is inclusive in the slice (start:end+1).

    .. note::
       If the end event index exceeds the trial length, the function returns None
       and prints a warning message.

    .. note::
       Event indices are adjusted relative to the new start position in the split trial.
    """
    # todo check index problem compared to matlab start at 0 or 1
    data_new = copy.deepcopy(data)

    start_event_indx, _ = findfield(data_new, start_event)
    end_event_indx, _ = findfield(data_new, end_event)

    if start_event_indx is None:
        raise ValueError('start_event {} not found'.format(start_event))

    if end_event_indx is None:
        raise ValueError('event_event {} not found'.format(end_event))

    # hard fix integer
    start_event_indx = int(start_event_indx[0])
    end_event_indx = int(end_event_indx[0])

    for key, value in data_new.items():
        if key == 'zoosystem':
            continue

        # Slice the line data
        trial_length = len(data_new[key]['line'])
        if trial_length > end_event_indx:
            data_new[key]['line'] = value['line'][start_event_indx:end_event_indx+1]
        else:
            print('skipping split trial since event is outside range of data')
            return None

        # Update events if present
        if 'event' in value:
            new_events = {}
            for evt_name, evt_val in value['event'].items():
                event_frame = evt_val[0]
                # Adjust index relative to new start
                n = event_frame - start_event_indx
                new_events[evt_name] = [n, 0, 0]
            data_new[key]['event'] = new_events

    return data_new
