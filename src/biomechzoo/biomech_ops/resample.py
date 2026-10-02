from typing import Dict

import numpy as np
from scipy.signal import resample_poly


def resample_data(
        signal_dict: Dict, up: int, down: int, axis: int = 0,
) -> Dict:
    """
    Upsample/downsample data using ``scipy.signal.resample_poly``.

    Parameters
    ----------
    signal_dict : dict
        Zoo data dictionary. Only numeric ndarray/list-valued entries
        are resampled; the 'zoosystem' entry and non-numeric or empty
        arrays are copied through unchanged.
    up : int
        Upsampling factor.
    down : int
        Downsampling factor.
    axis : int, optional
        Axis along which to resample. Default is 0.

    Returns
    -------
    new_dict : dict
        New dictionary with resampled arrays.

    Raises
    ------
    ValueError
        If both ``up`` and ``down`` are 1 (no resampling requested).
    """

    if up == 1 and down == 1:
        raise ValueError(
            'values other than 1 are required for either "up" or "down"'
        )

    new_dict = {}
    for key, subdict in signal_dict.items():
        if key == 'zoosystem':
            new_dict[key] = subdict
            continue
        new_dict[key] = {}
        for subkey, array in subdict.items():
            if isinstance(array, (np.ndarray, list)):
                array = np.asarray(array)
                if array.size == 0 or not np.issubdtype(array.dtype, np.number):
                    new_dict[key][subkey] = array
                    continue
                new_dict[key][subkey] = resample_poly(
                    array.astype(float), up, down, axis=axis
                )
            else:
                new_dict[key][subkey] = array

    return new_dict