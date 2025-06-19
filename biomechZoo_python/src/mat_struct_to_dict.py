import numpy as np
import scipy.io


def mat_struct_to_dict(mat_struct):
    """
    Recursively converts MATLAB structs loaded from a .mat file into Python dictionaries.

    Parameters:
    mat_struct: The MATLAB struct object (or other data) to be converted.

    Returns:
    dict: A Python dictionary containing the struct's data.
    """
    #todo: speed up this process
    result = {}

    if isinstance(mat_struct, scipy.io.matlab.mio5_params.mat_struct):
        for fieldname in mat_struct._fieldnames:
            field_value = getattr(mat_struct, fieldname)
            result[fieldname] = mat_struct_to_dict(field_value)  # Recursively convert structs
    elif isinstance(mat_struct, list):
        result = [mat_struct_to_dict(item) for item in mat_struct]  # Handle list of structs
    elif isinstance(mat_struct, np.ndarray):
        if mat_struct.size == 1:
            result = mat_struct_to_dict(mat_struct.item())  # Convert single-element arrays
        else:
            result = [mat_struct_to_dict(item) for item in mat_struct]
    else:
        result = mat_struct  # Return the value directly if it's not a struct, list, or array

    return result
