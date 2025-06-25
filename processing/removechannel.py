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
    zoosystem = data.get('zoosystem', {})
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

    # Build new zoo dictionary
    data_new = {'zoosystem': zoosystem}
    for ch in keep_channels:
        data_new[ch] = data[ch]

    return data_new
