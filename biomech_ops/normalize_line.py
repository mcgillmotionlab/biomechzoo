import numpy as np
from scipy.interpolate import interp1d


def normalize_line(channel_data, nlength=101):
    """
    Channel-level: interpolate channel data to target length.
    Assumes channel_data is a 1D or 2D numpy array.
    """
    original_length = channel_data.shape[0]

    if original_length == nlength:
        return channel_data

    x_original = np.linspace(0, 1, original_length)
    x_target = np.linspace(0, 1, nlength)

    if channel_data.ndim == 1:
        f = interp1d(x_original, channel_data, kind='linear')
        channel_data_norm = f(x_target)
    else:
        channel_data_norm = np.zeros((nlength, channel_data.shape[1]))
        for i in range(channel_data.shape[1]):
            f = interp1d(x_original, channel_data[:, i], kind='linear')
            channel_data_norm[:, i] = f(x_target)

    return channel_data_norm
