import numpy as np


def add_channel_data(data, ch, ndata, section='Video'):
    """
    Add a new channel to zoo data.

    Parameters
    ----------
    data : dict
        Zoo file data.
    ch : str
        Name of the new channel.
    ndata : array-like
        New data to be added to the channel (should be n x 1 or n x 3).
    section : str
        Section of zoo data ('Video' or 'Analog').

    Returns
    -------
    dict
        Updated zoo data with new channel added.

    Notes
    -----
    - If the channel already exists, it will be overwritten.
    - Adds channel name to the list in data['zoosystem'][section]['Channels'].
    """

    # Warn if overwriting
    if ch in data:
        print(f"Warning: channel '{ch}' already exists, overwriting...")

# Assign channel data
    data[ch] = {
        'line': ndata,
        'event': {}
    }

    # Update channel list
    ch_list = data['zoosystem'][section].get('Channels', [])

    # If the channel list is a NumPy array, convert it to a list
    if isinstance(ch_list, np.ndarray):
        ch_list = ch_list.tolist()

    # Ensure it's a flat list of strings
    if isinstance(ch_list, list) and ch not in ch_list:
        ch_list.append(ch)
        data['zoosystem'][section]['Channels'] = ch_list

    return data


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from utils.zload import zload
    from utils.zplot import zplot
    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    data = data['data']
    r = data['RKneeAngles']['line']*3
    data=add_channel_data(data, ch='blah', ndata=r)
    zplot(data, 'blah')

