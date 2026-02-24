from typing import Dict, List, Any
from biomechzoo.utils.update_channel_list import update_channel_list

def removechannel_data(
    data: Dict[str, Any],
    channels: List[str],
    mode: str = 'remove'
) -> Dict[str, Any]:
    """
    Remove or keep specified channels in a biomechanical data structure.

    This function provides two modes of operation: 'remove' mode deletes the specified
    channels from the data, while 'keep' mode retains only the specified channels and
    removes all others. The function updates both the main data dictionary and the
    channel lists in the zoosystem metadata.

    Parameters
    ----------
    data : dict of str to Any
        Biomechanical data dictionary loaded from a zoo file.
    channels : list of str
        List of channel names to remove or keep, depending on mode.
    mode : {'remove', 'keep'}, optional
        Operation mode. If 'remove', specified channels are deleted.
        If 'keep', only specified channels are retained. Default is 'remove'.

    Returns
    -------
    dict of str to Any
        Modified data dictionary with channels removed or kept according to mode.

    Raises
    ------
    ValueError
        If mode is not 'remove' or 'keep', or if channel section cannot
        be determined.

    Notes
    -----
    Channels not found in the data will generate a warning but will not cause an error.

    The function modifies the input data dictionary in place and also returns it.
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
            data = update_channel_list(data, section='Video', ch_remove=ch)
        elif ch in data['zoosystem']['Analog']['Channels']:
            data = update_channel_list(data, section='Analog', ch_remove=ch)
        else:
            raise ValueError('Unknown section for channel: {}'.format(ch))

    return data
