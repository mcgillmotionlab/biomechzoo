import numpy as np
from scipy.interpolate import interp1d

def normalize_line(channel_data, target_length):
    '''
    Channel-level: interpolate channel data to target length.
    Assumes channel_data is a 1D or 2D numpy array.
    '''
    arr = np.asarray(channel_data)
    original_length = arr.shape[0]

    if original_length == target_length:
        return arr

    x_original = np.linspace(0, 1, original_length)
    x_target = np.linspace(0, 1, target_length)

    if arr.ndim == 1:
        f = interp1d(x_original, arr, kind='linear')
        arr_new = f(x_target)
    else:
        arr_new = np.zeros((target_length, arr.shape[1]))
        for i in range(arr.shape[1]):
            f = interp1d(x_original, arr[:, i], kind='linear')
            arr_new[:, i] = f(x_target)

    return arr_new
