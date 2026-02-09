import copy
import warnings
from typing import Dict, List, Union, Any
from biomechzoo.utils.findfield import findfield

def removeevent_data(
    data: Dict[str, Any],
    events: Union[str, List[str]],
    mode: str = 'remove'
) -> Dict[str, Any]:
    """
    Remove or keep specified events in all channels of a biomechanical data structure.

    This function operates on all channels in the data dictionary, either removing
    specified events or keeping only the specified events (removing all others).
    Events not found in the data will generate a warning and be skipped.

    :param data: Biomechanical data dictionary loaded from a zoo file.
    :type data: Dict[str, Any]
    :param events: Event name or list of event names to remove or keep.
    :type events: Union[str, List[str]]
    :param mode: Operation mode - 'remove' to delete specified events, or 'keep' to
                 retain only specified events. Defaults to 'remove'.
    :type mode: str
    :return: Deep copy of input data with events removed or kept according to mode.
    :rtype: Dict[str, Any]
    :raises ValueError: If mode is not 'remove' or 'keep'.

    .. note::
       Events not found in the data will generate a warning but will not cause an error.

    .. note::
       The operation is applied to all channels in the data structure.
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
