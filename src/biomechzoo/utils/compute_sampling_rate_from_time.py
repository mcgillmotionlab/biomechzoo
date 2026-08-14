import numpy as np
from numpy.typing import ArrayLike


def compute_sampling_rate_from_time(
        t: ArrayLike, verbose: bool = False,
) -> int:
    """
    Compute the sampling rate from a time column.

    Parameters
    ----------
    t : ndarray
        1-D array of recorded timestamps in seconds.
    verbose : bool, optional
        If True, print the computed sampling rate. Default is False.

    Returns
    -------
    fsamp : int
        Sampling rate in Hz, rounded to the nearest integer.
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
