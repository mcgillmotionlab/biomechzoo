from typing import Dict, Optional

import numpy as np
from numpy.typing import ArrayLike

from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.utils.common_substring import common_substring_join
from biomechzoo.linear_algebra_ops.euclidean_norm import euclidean_norm, euclidean_norm


def compute_magnitude_data(
        data: Dict, ch_x: Optional[str], ch_y: Optional[str],
        ch_z: Optional[str], ch_new_name: Optional[str] = None,
) -> Dict:
    """
    Compute Euclidean magnitude from IMU channels stored in a BiomechZoo-style data dict.

    Parameters
    ----------
    data : dict
        BiomechZoo data structure where each channel is stored as:
        data[channel]['line'] -> np.ndarray

    ch_x, ch_y, ch_z : str or None
        Channel names for X, Y, Z components.
        Any channel can be None (treated as missing / ignored).

        Rules:
        - At least 2 channels must be provided
        - Missing channels are treated as zero contribution

    ch_new_name : str or None
        Name of output magnitude channel.
        If None, a name is automatically generated.

    Returns
    -------
    data : dict
        Updated data dictionary with added magnitude channel.
    """

    if ch_x is None:
        x = None
    else:
        x = data[ch_x]['line']

    if ch_y is None:
        y = None
    else:
        y = data[ch_y]['line']

    if ch_z is None:
        z = None
    else:
        z = data[ch_z]['line']

    # sanity check
    n_channels = sum(c is not None for c in [x, y, z])

    if n_channels == 0:
        raise ValueError("No valid channels provided for magnitude computation.")

    if n_channels < 2:
        raise ValueError(
            "At least 2 channels are required for magnitude computation."
        )

    #calculate the magnitude of the data
    magnitude_data = euclidean_norm(x, y, z)

    # get name of the new channel:
    if ch_new_name is None:
        valid_names = [ch for ch in [ch_x, ch_y, ch_z] if ch is not None]
        ch_new_name = common_substring_join(valid_names)

        if ch_new_name.startswith("_"):
            ch_new_name = ch_new_name[1:]
        ch_new_name = ch_new_name + '_mag'

    #add channels
    data = addchannel_data(data, ch_new_name=ch_new_name, ch_new_data=magnitude_data )

    return data


def _prep(a: Optional[ArrayLike], ref: np.ndarray) -> np.ndarray:
    raise NotImplementedError
    """
    Convert input to array or replace None with zeros matching ref shape.

    Parameters
    ----------
    a : array_like or None
        Value to convert. If None, a zero array matching ``ref`` is
        returned instead.
    ref : ndarray
        Reference array whose shape is used when ``a`` is None.

    Returns
    -------
    arr : ndarray
        ``a`` converted to an array, or zeros matching ``ref``'s shape.
    """
    if a is None:
        arr = np.zeros_like(ref)
    else:
        arr = np.asarray(a)

    return arr


#-------TESTING-----
if __name__ == "__main__":
    import numpy as np
    from biomechzoo.utils.get_sample_zoo_file import load_sample_zoo_file
    from biomechzoo.processing.explodechannel_data import explodechannel_data
    data = load_sample_zoo_file()
    data = explodechannel_data(data)

    # test compute_magnitude_data
    data = compute_magnitude_data(data, ch_x='SACR_x', ch_y='SACR_y', ch_z='SACR_z')
    data = compute_magnitude_data(data, ch_x='SACR_x', ch_y='SACR_y', ch_z=None)

    # test compute_magnitude_line
    x = np.array([3, 0, 0])
    y = np.array([4, 0, 0])
    z = np.array([5, 0, 0])

    mag = euclidean_norm(x, y, z)
    print("3D Magnitude output:")
    print(mag)
    print("Expected output:[7.07106781, 0, 0]")

    mag = euclidean_norm(x, y, z=None)
    print("2D Magnitude output:")
    print(mag)
    print("Expected output:[5, 0, 0]")
