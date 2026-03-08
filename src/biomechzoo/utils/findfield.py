def findfield(data, target_event):
    """
    Search zoo data for the value and channel associated with a target event.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    target_event : str
        Name of the event to search for.

    Returns
    -------
    events : list or None
        Event data as ``[frame_index, value, 0]``, or None if not found.
    channel : str or None
        Name of the channel containing the event, or None if not found.
    """
    for channel, content in data.items():
        if channel == 'zoosystem':
            continue
        events = content.get('event', {})
        if target_event in events:
            val = events[target_event]
            return val, channel

    return None, None


