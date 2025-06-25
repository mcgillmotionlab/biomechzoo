import numpy as np
from scipy.interpolate import interp1d
from biomechzoo.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave


def normalize(fld, num_frames=101):
    """
    Normalize the length of all channels in all zoo files in a folder.

    Parameters:
    - fld (str): Folder containing zoo files
    - num_frames (int): Number of frames to normalize to (default: 101)
    """
    files = engine(fld)
    for fl in files:
        zoo = zload(fl)
        new_zoo = normalize_data(zoo, num_frames)
        zsave(fl, new_zoo)


def normalize_data(data, num_frames=101):
    """
    Normalize all channels in a single zoo file to a fixed number of frames.

    Parameters:
    - zoo (dict): Loaded zoo dictionary
    - num_frames (int): Number of frames to normalize to

    Returns:
    - dict: Modified zoo dict with all channels resampled
    """
    for ch in data:
        if ch != 'zoosystem':
            data[ch] = normalize_line(data[ch], num_frames)

    # Record processing step
    data.setdefault('zoosystem', {}).setdefault('Processing', []).append('normalize')
    data['zoosystem']['NormFrames'] = num_frames

    return data

def normalize_line(channel, num_frames=101):
    """
    Resample a single channel's data to a fixed number of frames using linear interpolation.

    Parameters:
    - channel (dict): Channel dict with 'data' key
    - num_frames (int): Target number of frames

    Returns:
    - dict: Updated channel with resampled data
    """
    data = channel['data']
    old_len = data.shape[0]
    x_old = np.linspace(0, 1, old_len)
    x_new = np.linspace(0, 1, num_frames)

    if data.ndim == 1:
        f = interp1d(x_old, data, kind='linear')
        channel['data'] = f(x_new)
    else:
        f = interp1d(x_old, data, axis=0, kind='linear')
        channel['data'] = f(x_new)

    return channel
