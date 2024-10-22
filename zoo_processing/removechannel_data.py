import warnings

def removechannel_data(data, ch):

    """
    Removes channels from zoo files

    Parameters:
        data (dict): Loaded zoo data
        ch (str or list): Channels to remove. A single channel can be entered as a str

    Returns:
        data (dict): Updated zoo data with requested channels removed

    """
    for i, _ in enumerate(ch):
        value = data.pop(ch[i], None)
        if value is None:
            warnings.warn('channel {} not found'.format(ch[i]))

    return data

