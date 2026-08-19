from typing import Dict, List, Union

import numpy as np
from numpy.typing import ArrayLike

from biomechzoo.processing.addchannel_data import addchannel_data


def compute_magnitude_line(
        x: ArrayLike, y: ArrayLike, z: ArrayLike,
) -> np.ndarray:
    """
    Compute the Euclidean magnitude of a 3-component signal.

    Parameters
    ----------
    x : array_like
        X component.
    y : array_like
        Y component.
    z : array_like
        Z component.

    Returns
    -------
    magnitude : ndarray
        Vector magnitude ``sqrt(x**2 + y**2 + z**2)``.
    """
    magnitude = np.sqrt((x**2) + (y**2) + (z **2))

    return magnitude


def rectify_data(data: Dict, chs: Union[str, List[str]]) -> Dict:
    """
    Take the absolute value of one or more channels and store the
    result as new channels.

    Parameters
    ----------
    data : dict
        Zoo data dictionary.
    chs : str or list of str
        Channel name(s) to rectify.

    Returns
    -------
    data : dict
        The input ``data`` dictionary updated with one new
        ``'<ch>_rectified'`` channel per entry in ``chs``.
    """
    if type(chs) is str:
        chs = [chs]

    # extract channels from data
    for ch in chs:
        yd = data[ch]['line']
        yd_abs = rectify_line(yd)
        data = addchannel_data(data, ch_new_data=yd_abs, ch_new_name=ch + '_rectified')

    return data


def rectify_line(yd: ArrayLike) -> np.ndarray:
    """
    Take the absolute value of a signal.

    Parameters
    ----------
    yd : array_like
        Input signal.

    Returns
    -------
    yd_abs : ndarray
        Absolute value of ``yd``.
    """
    yd_abs = np.abs(yd)

    return yd_abs


