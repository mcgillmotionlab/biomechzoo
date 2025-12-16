def findfield(data, target_event):
    """ searches in zoo data for the event value and channel name associated with target_event

    Arguments:
        data. dict. zoo data
        target_event, str. Name of event to search for
    Returns:
        events, list of len 2. First is index (exd) and second is value (eyd)
        channel, str. Name of channel associated with event
    """
    for channel, content in data.items():
        if channel == 'zoosystem':
            continue
        events = content.get('event', {})
        if target_event in events:
            val = events[target_event]
            return val, channel

    return None, None


