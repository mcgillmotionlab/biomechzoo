import scipy.io
from scipy.io.matlab.mio5_params import mat_struct
import numpy as np
import os
from datetime import datetime
import inspect
import ezc3d

import fileparts


# A set of functions to handle zoo input/output operations


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


def zload(file_path, verbose=False):
    """
    Loads a .zoo file (MAT format) and returns its contents as a Python dictionary.

    Parameters:
    file_path (str): Path to the .zoo file (MAT format).

    Returns:
    dict: A dictionary containing the contents of the .zoo file, or None if loading fails.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print('File {} not found'.format(file_path))
        return None

    try:
        # Load the .zoo (MAT) file
        data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
        data = data['data']
        data = mat_struct_to_dict(data)

        # restructure as Matlab like zoofile
        # data = _mat_to_zoo(data)

        if verbose:
            print('File {} loaded successfully'.format(file_path))

        # Return the loaded data
        return data

    except Exception as e:
        print('Error loading file {}: {}'.format(file_path, e))
        return None


def zsave(fl, data, message=None):
    """
    Save the dictionary as a special .zoo (MAT) file.

    Parameters:
    fl (str): The full path where the .zoo file will be saved.
    data (dict): The data to save as a .zoo file.
    """

    # Determine which function called zsave
    stack = inspect.stack()
    if len(stack) > 1:
        process = stack[1].function
    else:
        process = 'process'

    # Add additional processing info
    if not message:
        message = ''

    process = '{} ({})'.format(process, datetime.now().strftime('%Y-%m-%d'))

    # Write processing step to zoosystem
    if 'Processing' not in data['zoosystem']:
        data['zoosystem']['Processing'] = [process]
    else:
        # Ensure 'Processing' is a list before appending
        if isinstance(data['zoosystem']['Processing'], list):
            data['zoosystem']['Processing'].append(process)
        else:
            # If it is not a list, convert it to a list
            data['zoosystem']['Processing'] = [data['zoosystem']['Processing'], process]

    # Ensure the file has a .zoo extension
    directory, filename, ext = fileparts(fl)
    if ext is None:
        fl += '.zoo'
    if not fl.endswith('.zoo'):
        fl = os.path.join(directory, filename, '.zoo')

    # Create the .mat file
    mat_file_path = fl.replace('.zoo', '.mat')

    # Save the dictionary as a .mat file
    scipy.io.savemat(mat_file_path, data)

    # Rename the .mat file to .zoo
    os.rename(mat_file_path, fl)


def zoo_to_dict(data):
    """ restructures a zoo file saved using scipy to matlab like dict"""


    return data


if __name__ == "__main__":
    # For basic testing


    # save zoo file as
    fl_zoo = fl_c3d.replace('.c3d', '_temp.zoo')

    # load zoo file
    data2 = zload(fl_zoo)

    # delete test file
    os.remove(fl_zoo)


