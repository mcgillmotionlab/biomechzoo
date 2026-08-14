from typing import Dict, List, Optional, Union


def update_channel_list(
        data: Dict, section: str = 'Video',
        ch_add: Optional[Union[str, List[str]]] = None,
        ch_remove: Optional[Union[str, List[str]]] = None,
) -> Dict:
    """
    Update the channel list of a zoosystem section by adding or removing channels.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing a 'zoosystem' key.
    section : str, optional
        Section name to update (e.g., 'Video' or 'Analog'). Default is 'Video'.
    ch_add : str or list of str, optional
        Channel name(s) to add to the section's channel list.
    ch_remove : str or list of str, optional
        Channel name(s) to remove from the section's channel list.

    Returns
    -------
    data : dict
        The updated zoo dictionary (modified in place).
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