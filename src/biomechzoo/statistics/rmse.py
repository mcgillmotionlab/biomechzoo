import numpy as np


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute the root-mean-square error between two arrays.

    Parameters
    ----------
    a : ndarray
        First array of values.
    b : ndarray
        Second array of values, same shape as ``a``.

    Returns
    -------
    r : float
        Root-mean-square error between ``a`` and ``b``.
    """
    a = np.asarray(a)
    b = np.asarray(b)
    r = np.sqrt(np.mean((a - b) ** 2))

    return r
