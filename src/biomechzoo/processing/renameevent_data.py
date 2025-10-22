def renameevent_data(data, evt, nevt):
    """
    Rename events in the Zoo data structure.

    Parameters
    ----------
    data : dict
        The Zoo-formatted dictionary.
    evt : str or list of str
        Names of existing events to rename.
    nevt : str or list of str
        Names of new events to apply.

    Returns
    -------
    data : dict
        Updated Zoo data with renamed events.
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
