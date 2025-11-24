def update_channel_list(data, section='Video', ch_add=None, ch_remove=None):
    """
    Updates the channel list of a section by adding or removing channels.

    Args:
        data (dict): Zoo data dictionary.
        section (str): Section name ('Video', 'Analog', etc.).
        ch_add (str or list of str, optional): Channel(s) to add.
        ch_remove (str or list of str, optional): Channel(s) to remove.

    Returns:
        dict: The updated zoo dictionary (same object as input).
    """
    ch_list = data['zoosystem'][section]['Channels']

    # Normalize to list
    if isinstance(ch_add, str):
        ch_add = [ch_add]
    if isinstance(ch_remove, str):
        ch_remove = [ch_remove]

    # Add channels
    if ch_add is not None:
        for ch in ch_add:
            if ch not in ch_list:
                ch_list.append(ch)

    # Remove channels
    if ch_remove is not None:
        for ch in ch_remove:
            if ch in ch_list:
                ch_list.remove(ch)

    data['zoosystem'][section]['Channels'] = ch_list
    return data