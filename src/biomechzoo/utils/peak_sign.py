import numpy as np

def peak_sign(r):
    """
    Determine whether the largest absolute peak in the signal is positive or negative.

    Parameters
    ----------
    r : array-like
        Signal vector.

    Returns
    -------
    sign : int
        1 if the maximum peak is positive, -1 if negative.
    """
    r = np.asarray(r)
    max_val = np.max(r)
    min_val = np.min(r)

    if abs(max_val) > abs(min_val):
        return 1
    else:
        return -1
