import numpy as np

def make_unit(v: np.ndarray) -> np.ndarray:
    """
    Creates a unit vector (a vector of length '1') from a vector 'v'
    """
    return v / np.linalg.norm(v, axis=-1, keepdims=True)
