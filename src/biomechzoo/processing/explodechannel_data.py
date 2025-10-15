import copy
import numpy as np

def explodechannel_data(data, channels=None):
    """ Explodes 3D channels (n x 3 arrays) into separate X, Y, Z channels.

    Arguments:
        data (dict): Zoo data loaded from a file
        channels (list of str or None): Channels to explode.
            If None, explode all channels with 'line' shaped (n x 3).

    Returns:
        data_new (dict): Modified zoo dictionary with exploded channels.
    """
    data_new = copy.deepcopy(data)

    # Ensure zoosystem channel lists are Python lists
    for sys in ['Video', 'Analog']:
        if sys in data_new.get('zoosystem', {}):
            ch_list = data_new['zoosystem'][sys].get('Channels', [])
            if isinstance(ch_list, np.ndarray):
                ch_list = ch_list.tolist()
            # strip whitespace
            ch_list = [str(ch).strip() for ch in ch_list]
            data_new['zoosystem'][sys]['Channels'] = ch_list

    # Find default channels if none provided
    if channels is None:
        channels = []
        for ch in data_new:
            if ch == 'zoosystem':
                continue
            ch_data = data_new[ch]['line']
            if ch_data.ndim == 2 and ch_data.shape[1] == 3:
                channels.append(ch)

    # Explode each channel
    for ch in channels:
        if ch not in data_new:
            print('Warning: channel {} not found, skipping.'.format(ch))
            continue

        ch_data = data_new[ch]['line']
        if ch_data.ndim != 2 or ch_data.shape[1] != 3:
            print(f"Warning: channel '{ch}' 'line' is not n x 3 shape, skipping.")
            continue

        x, y, z = ch_data[:, 0], ch_data[:, 1], ch_data[:, 2]
        for axis, line in zip(['_x', '_y', '_z'], [x, y, z]):
            key = ch + axis
            data_new[key] = {
                'line': line,
                'event': data_new[ch]['event']}

        # Remove original channel
        del data_new[ch]

        # --- Update zoosystem lists ---
        for sys in ['Video', 'Analog']:
            if sys in data_new['zoosystem']:
                ch_list = data_new['zoosystem'][sys]['Channels']
                if ch in ch_list:
                    # Remove original channel
                    ch_list = [c for c in ch_list if c != ch]
                    # Add exploded channels
                    ch_list.extend([ch + '_x', ch + '_y', ch + '_z'])
                    data_new['zoosystem'][sys]['Channels'] = ch_list

    return data_new
