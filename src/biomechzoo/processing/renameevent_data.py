def renameevent_data(data, evt, nevt):
    """
    Rename events in the Zoo data structure.

    Parameters
    ----------
    data : dict
        The Zoo-formatted dictionary.
    evt : str or list of str
        Names of existing events to rename.
    nevt : str or list of str
        Names of new events to apply.

    Returns
    -------
    data : dict
        Updated Zoo data with renamed events.
    """
    # Convert to list if passed as single string
    if isinstance(evt, str):
        evt = [evt]
    if isinstance(nevt, str):
        nevt = [nevt]

    if len(evt) != len(nevt):
        raise ValueError("`evt` and `nevt` must have the same length.")

    # Get all data channels except 'zoosystem'
    channels = [ch for ch in data if ch != 'zoosystem']
    for old_name, new_name in zip(evt, nevt):
        eventsRenamed = False
        for ch in channels:
            events = data[ch].get('event', {})
            if old_name in events:
                print(f"Renaming event '{old_name}' in channel '{ch}' to '{new_name}'")
                data[ch]['event'][new_name] = events[old_name]
                del data[ch]['event'][old_name]
                eventsRenamed = True

        if not eventsRenamed:
            print('no event {} found in any channel'.format(evt))

    return data