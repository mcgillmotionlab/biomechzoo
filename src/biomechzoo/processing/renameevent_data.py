from typing import Dict, List, Union, Any


def renameevent_data(
    data: Dict[str, Any],
    evt: Union[str, List[str]],
    nevt: Union[str, List[str]]
) -> Dict[str, Any]:
    """
    Rename events in all channels of a biomechanical data structure.

    This function searches all channels for specified event names and renames them
    to the new names. If an old event name is not found in a channel, it is skipped
    for that channel without error.

    :param data: Biomechanical data dictionary loaded from a zoo file.
    :type data: Dict[str, Any]
    :param evt: Existing event name(s) to rename.
    :type evt: Union[str, List[str]]
    :param nevt: New event name(s) to apply. Must be same length as evt.
    :type nevt: Union[str, List[str]]
    :return: Modified data dictionary with renamed events.
    :rtype: Dict[str, Any]
    :raises ValueError: If evt and nevt do not have the same length.

    .. note::
       Only events that exist in a channel will be renamed. Missing events are
       silently skipped for each channel.

    .. note::
       The function modifies the input data dictionary in place and also returns it.
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
        for ch in channels:
            events = data[ch].get('event', {})
            if old_name in events:
                data[ch]['event'][new_name] = events[old_name]
                del data[ch]['event'][old_name]

    return data


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from src.biomechzoo.utils.zload import zload
    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    evt = ['Left_FootStrike1', 'Left_FootStrike2', 'NonExistingEvent']

    # see existing keys
    missing = [k for k in evt if k not in data['SACR']['event']]
    print("Missing keys:", missing)   # expected behavior is missing 'NonExistingEvent'

    nevt = ['LFS_1', 'LFS2', 'NE_1']
    data = renameevent_data(data, evt=evt, nevt=nevt)

    # after applying renameevent_data
    missing = [k for k in nevt if k not in data['SACR']['event']]
    print("Missing keys:", missing)   # expected behavior is missing 'NE_1'
