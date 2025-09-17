import numpy as np


def addchannel_data(data, ch_new_name, ch_new_data, section='Video'):
    """
    Add a new channel to zoo data.

    Parameters
    ----------
    data : dict
        Zoo file data.
    ch_new_name : str
        Name of the new channel.
    ch_new_data : array-like
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
    if ch_new_name in data:
        print('Warning: channel {} already exists, overwriting...'.format(ch_new_name))

# Assign channel data
    data[ch_new_name] = {
        'line': ch_new_data,
        'event': {}
    }

    # Update channel list
    ch_list = data['zoosystem'][section].get('Channels', [])

    # If the channel list is a NumPy array, convert it to a list
    if isinstance(ch_list, np.ndarray):
        ch_list = ch_list.tolist()

    # Ensure it's a flat list of strings
    if isinstance(ch_list, list) and ch_new_name not in ch_list:
        ch_list.append(ch_new_name)
        data['zoosystem'][section]['Channels'] = ch_list

    return data


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from src.biomechzoo.utils.zload import zload
    from src.biomechzoo.utils.zplot import zplot
    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    data = data['data']
    r = data['RKneeAngles']['line']*3
    data= addchannel_data(data, ch_new_name='blah', ch_new_data=r)
    zplot(data, 'blah')

