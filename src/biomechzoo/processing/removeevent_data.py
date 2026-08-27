import copy
import warnings
from typing import Dict, List, Union, Any
from biomechzoo.utils.findfield import findfield

def removeevent_data(
        data: Dict[str, Any], events: Union[str, List[str]],
        mode: str = 'remove',
) -> Dict[str, Any]:
    """
    Remove or retain specified events across all channels in a biomechanical
    data structure.

    This function operates on every channel in the input data dictionary,
    either removing the specified events or keeping only the specified
    events (removing all others). Events not found in the data generate
    a warning and are skipped.

    Parameters
    ----------
    data : dict of str to Any
        Biomechanical data dictionary loaded from a .zoo file.
    events : str or list of str
        Event name or list of event names to remove or retain.
    mode : {'remove', 'keep'}, optional
        Operation mode. If 'remove', specified events are deleted.
        If 'keep', only the specified events are retained and all
        others are removed. Default is 'remove'.

    Returns
    -------
    data_new : dict of str to Any
        Deep copy of the input data with events modified according
        to the selected mode.

    Raises
    ------
    ValueError
        If `mode` is not 'remove' or 'keep'.

    Notes
    -----
    Events not found in the data generate a warning but do not
    raise an error.

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
