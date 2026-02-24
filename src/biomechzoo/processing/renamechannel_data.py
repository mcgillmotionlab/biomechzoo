import numpy as np
from typing import Dict, List, Union, Any
from biomechzoo.utils.update_channel_list import update_channel_list


def renamechannel_data(
    data: Dict[str, Any],
    ch_old_names: Union[str, List[str]],
    ch_new_names: Union[str, List[str]],
    section: str = 'Video'
) -> Dict[str, Any]:
    """
    Rename channels in a biomechanical data structure.

    This function renames one or more channels by creating new channel entries with
    the new names, copying the line data and events from the old channels, and then
    removing the old channel entries. The channel list in zoosystem metadata is
    updated accordingly.

    Parameters
    ----------
    data : dict of str to Any
        Biomechanical data dictionary loaded from a zoo file.
    ch_old_names : str or list of str
        Current name(s) of channel(s) to rename.
    ch_new_names : str or list of str
        New name(s) for the channel(s). Must be same length as ch_old_names.
    section : {'Video', 'Analog'}, optional
        Section of zoo data where channels belong. Default is 'Video'.

    Returns
    -------
    dict of str to Any
        Modified data dictionary with renamed channels.

    Notes
    -----
    If a new channel name already exists in the data, it will be overwritten
    with a warning message.

    The function modifies the input data dictionary in place and also returns it.
    """

    # check if string (single input)
    if isinstance(ch_old_names, str):
        ch_old_names = [ch_old_names]
    if isinstance(ch_new_names, str):
        ch_new_names = [ch_new_names]

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
    data = update_channel_list(data, section=section, ch_remove=ch_old_names)
    data = update_channel_list(data, section=section, ch_add=ch_new_names)

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

