import numpy as np

def make_unit(v: np.ndarray) -> np.ndarray:
    """
    Normalise a vector or array of vectors to unit length.

    Parameters
    ----------
    v : ndarray
        Input vector or array of vectors. The last axis is treated as the
        vector dimension.

    Returns
    -------
    ndarray
        Array of the same shape as ``v`` where each vector has been divided
        by its L2 norm, resulting in unit length along the last axis.
    """
    return v / np.linalg.norm(v, axis=-1, keepdims=True)
