import numpy as np
from scipy.signal import resample_poly

def resample_data(signal_dict:dict, up:int, down:int, axis:int = 0)-> dict:
    """
    Upsamples / downsamples data using scipy.signal.resample_poly
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