import copy
import numpy as np
from biomechzoo.utils.update_channel_list import update_channel_list

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

        # find section
        if ch in data_new['zoosystem']['Video']['Channels']:
            section = 'Video'
        elif ch in data_new['zoosystem']['Analog']['Channels']:
            section = 'Analog'
        else:
            raise ValueError('Unknown section for channel {}'.format(ch))

        ch_data = data_new[ch]['line']
        if ch_data.ndim != 2 or ch_data.shape[1] != 3:
            print(f"Warning: channel '{ch}' 'line' is not n x 3 shape, skipping.")
            continue

        # Add exploded channels
        x, y, z = ch_data[:, 0], ch_data[:, 1], ch_data[:, 2]
        for axis, line in zip(['_x', '_y', '_z'], [x, y, z]):
            key = ch + axis

            # Bring the old events to _x only
            if axis == '_x':
                edata = data_new[ch]['event']
            else:
                edata = {}

            data_new[key] = {
                'line': line,
                'event': edata
            }

            # Update channel list and assign back
            data_new = update_channel_list(data_new, section=section, ch_add=key)

        # Remove original channel from list and dict
        data_new = update_channel_list(data_new, section=section, ch_remove=ch)
        data_new.pop(ch)


    return data_new


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    ch_old_name = 'RKneeAngles'
    ch_new_name = 'RightKneeAngles'
    data = explodechannel_data(data)

