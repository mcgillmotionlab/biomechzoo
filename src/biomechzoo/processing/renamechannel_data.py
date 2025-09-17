import numpy as np


def renamechannel_data(data, ch_old_names, ch_new_names, section='Video'):
    """
    Rename channels in a zoo data.

    Parameters
    ----------
    data : dict
        Zoo file data.
    ch_old_names : str or list
        Name of the old channels.
    ch_new_names : str or list
        Name of the new channels.

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

    for i, ch_old_name in enumerate(ch_old_names):
        ch_new_name = ch_new_names[i]
        # Warn if overwriting
        if ch_new_name in data:
            print('Warning: channel {} already exists, overwriting...'.format(ch_new_name))

        # Assign new channel
        data[ch_new_name] = {
            'line': data[ch_old_name]['line'],
            'event': data[ch_old_name]['event']
        }

        # remove old channel
        data.pop(ch_old_name)

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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    ch_old_name = 'RKneeAngles'
    ch_new_name = 'RightKneeAngles'
    data = renamechannel_data(data, ch_old_name=ch_old_name, ch_new_name=ch_new_name)

    if ch_old_name not in data:
        print('RkneeAngles removed')
    if ch_new_name in data:
        print('RightKneeAngles added')

