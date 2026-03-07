import numpy as np
from scipy.interpolate import interp1d


def normalize_line(channel_data, nlength=101):
    """
    Interpolate a channel array to a target length.

    Parameters
    ----------
    channel_data : ndarray
        1-D or 2-D numpy array of shape (n,) or (n, k) to be resampled.
    nlength : int, optional
        Target number of samples. Default is 101.

    Returns
    -------
    channel_data_norm : ndarray
        Array resampled to shape (nlength,) or (nlength, k) using
        linear interpolation.
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




if __name__ == '__main__':
    # --- 1D TESTS ---
    data_1d = np.array([0, 1, 2, 3, 4])
    print("Original 1D shape:", data_1d.shape)

    # Case 1: same length
    same = normalize_line(data_1d, nlength=5)
    print("Same length test passed:", np.allclose(same, data_1d))

    # Case 2: upsample
    upsampled = normalize_line(data_1d, nlength=10)
    print("Upsampled 1D shape:", upsampled.shape)
    print("Upsampled 1D first/last values:", upsampled[0], upsampled[-1])

    # Case 3: downsample
    downsampled = normalize_line(data_1d, nlength=3)
    print("Downsampled 1D shape:", downsampled.shape)
    print("Downsampled 1D first/last values:", downsampled[0], downsampled[-1])

    print("\nAll tests completed.")