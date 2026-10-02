from typing import Dict, List, Optional

from biomechzoo.utils.findfield import findfield


def get_split_events(data: Dict, first_event_name: str) -> Optional[List[str]]:
    """
    Split a lengthy trial containing multiple cycles into per-cycle
    event names.

    Searches ``data`` for events following the naming pattern
    ``name1``, ``name2``, etc., starting from ``first_event_name``.

    Parameters
    ----------
    data : dict
        Zoo file data dictionary.
    first_event_name : str
        Name of the first event in the numbered sequence
        (e.g. ``'RFS1'``).

    Returns
    -------
    split_events : list of str or None
        Names of the numbered events found in sequence, or None if
        the event channel could not be found or fewer than 2 events
        exist.
    """
    # find all events, events should follow style name1, name2, etc..
    split_events = []
    _, channel_name = findfield(data, first_event_name)
    if channel_name is None:
        return None

    event_name_root = first_event_name[0:-1]
    first_event_number = int(first_event_name[-1])
    i = 1
    if first_event_number > 1:
        i = first_event_number

    while True:
        key = f"{event_name_root}{i}"
        if key in data[channel_name]['event']:
            split_events.append(key)
            i += 1
        else:
            break

    n_segments = len(split_events) - 1
    if n_segments < 1:
        print("Not enough {} events to split.".format(event_name_root))
        return None

    return split_events

