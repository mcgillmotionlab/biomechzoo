import numpy as np


def compute_sampling_rate_from_time(t, verbose=False):
    """ computes sampling rate from time column
    Arguments
    t, 1D numpy array, recorded times

    Returns
    fsamp, int: sampling rate of capture
    """
    # Calculate differences between consecutive time points
    dt = np.diff(t)

    # Average time difference (seconds)
    avg_dt = np.mean(dt)

    # Sampling frequency (Hz)
    # Sampling frequency (Hz)
    fsamp = int(np.round(1 / avg_dt))

    if verbose:
        print('Inferred sampling rate: {} Hz'.format(fsamp))

    return fsamp
