import os
from typing import Optional

import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.utils.common_substring import common_substring_join


def compute_magnitude_data(data:dict, ch_x:None | str, ch_y:None | str, ch_z:None | str, ch_new_name:None | str = None)->dict:
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
    dict
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
    magnitude_data = compute_magnitude_line(x, y, z)

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


def compute_magnitude_line(x:None | np.ndarray,y:None | np.ndarray, z:None | np.ndarray)-> np.ndarray:
    """
    Compute Euclidean magnitude (supports 2D by allowing y or z to be None).

    Parameters
    ----------
    x, y, z : array-like or None
        Signal components. Any component can be None.
        If a component is None, it is treated as zero (i.e., 2D or 1D data is supported).

    Returns
    -------
    magnitude : array-like
        Vector magnitude sqrt(x^2 + y^2 + z^2)
    """

    # Find a reference length from the first non-None input
    ref = x if x is not None else (y if y is not None else z)
    if ref is None:
        raise ValueError("At least one of x, y, z must be provided")
    ref = np.asarray(ref)

    x = _prep(x, ref)
    y = _prep(y, ref)
    z = _prep(z, ref)

    magnitude = np.sqrt(x**2 + y**2 + z**2)

    return magnitude

def _prep(a, ref):
    """
    Convert input to array or replace None with zeros matching ref shape.
    """
    if a is None:
        return np.zeros_like(ref)
    return np.asarray(a)


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

    mag = compute_magnitude_line(x, y, z)
    print("3D Magnitude output:")
    print(mag)
    print("Expected output:[7.07106781, 0, 0]")

    mag = compute_magnitude_line(x, y, z=None)
    print("2D Magnitude output:")
    print(mag)
    print("Expected output:[5, 0, 0]")

    mag = compute_magnitude_line(x, y=None, z=None)
    print("1D Magnitude output:")
    print(mag)
    print("Expected output:[3, 0, 0]")