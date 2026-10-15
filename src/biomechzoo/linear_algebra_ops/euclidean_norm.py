import numpy as np


def euclidean_norm(
    x: np.ndarray, y: np.ndarray, z: np.ndarray | None = None
) -> np.ndarray:
    """Compute the Euclidean norm of paired 2D or 3D vectors.

    Each input array contains one coordinate for each vector. When ``z`` is
    omitted, the norm is computed in 2D; otherwise it is computed in 3D.

    Parameters
    ----------
    x : np.ndarray
        One-dimensional array of x-coordinates.
    y : np.ndarray
        One-dimensional array of y-coordinates. Must have the same length as
        ``x``.
    z : np.ndarray, optional
        One-dimensional array of z-coordinates. If provided, must have the
        same length as ``x`` and ``y``. If omitted, computes 2D norms.

    Returns
    -------
    np.ndarray
        One-dimensional array containing the norm of each paired vector. Its
        length is the number of coordinate values in each input array.

    Raises
    ------
    ValueError
        If the coordinate arrays do not all have the same length.
    """

    # allow for 2D (only via missing z) or 3D vectors
    if z is None:
        vectors = [x, y]
    else:
        vectors = [x, y, z]

    # check lengths of vectors
    if any(len(vector) != len(vectors[0]) for vector in vectors[1:]):
        raise ValueError("All vectors must have the same length.")

    matrix = np.column_stack(vectors)
    norm = np.linalg.norm(matrix, axis=1)
    return norm


