def removechannel_data(data, channels, mode='remove'):
    """
    File-level processing: Remove or keep specified channels in a single zoo dictionary.

    Parameters:
    - data (dict): Zoo data loaded from a file
    - channels (list of str): List of channels to remove or keep
    - mode (str): 'remove' or 'keep'

    Returns:
    - dict: Modified zoo dictionary with updated channels
    """
    if mode not in ['remove', 'keep']:
        raise ValueError("mode must be 'remove' or 'keep'.")

    all_channels = [ch for ch in data if ch != 'zoosystem']

    # Check for missing channels
    missing = [ch for ch in channels if ch not in all_channels]
    if missing:
        print('Warning: the following channels were not found {}'.format(missing))

    if mode == 'remove':
        keep_channels = [ch for ch in all_channels if ch not in channels]
    elif mode == 'keep':
        keep_channels = [ch for ch in all_channels if ch in channels]
    else:
        raise ValueError("Mode must be 'remove' or 'keep'.")

    # --- Compute channels to remove ---
    remove_channels = [ch for ch in all_channels if ch not in keep_channels]

    if remove_channels:
        print('Removing channels: {}'.format(remove_channels))
    else:
        print('No channels to remove')

    # Remove from main data dict ---
    for ch in remove_channels:
        data.pop(ch, None)
        if ch in data['zoosystem']['Video']['Channels']:
            data['zoosystem']['Video']['Channels'] = [c for c in data['zoosystem']['Video']['Channels'] if c != ch]
        if ch in data['zoosystem']['Analog']['Channels']:
            data['zoosystem']['Analog']['Channels'] = [c for c in data['zoosystem']['Analog']['Channels'] if c != ch]

    return data
