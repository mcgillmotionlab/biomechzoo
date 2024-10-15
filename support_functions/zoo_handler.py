import scipy.io
import numpy as np
import os

# A set of functions to handle zoo input/output operations


def c3d_to_zoo(fl, verbose=False):
    """ convert c3d file located at fl into dictionary with easily accessible marker data

    Arguments:
        fl      ... str, full path to c3d file
        verbose ... bool, Default = False. If true, information about processing printed to screen
    Returns:
        data    ... dict, c3d file with markers as keys and coordinates as values

    Notes:
        - For details on reading c3d with ezc3d see:
        https://github.com/pyomeca/ezc3d#python-3
    """

    import ezc3d

    if verbose:
        print('converting c3d to dict for: {}'.format(fl))

    # load c3d object
    d = ezc3d.c3d(fl)

    # add all markers to a dictionary
    marker_names = d['parameters']['POINT']['LABELS']['value']  # marker names
    point_data = d['data']['points']  # 4xNxT, where 4 represent the components XYZ1
    data = {}
    for i, marker_name in enumerate(marker_names):
        data[marker_name] = point_data[0:3, i, :].T  # we only want XYZ components in N X 3 format

    # add analog data to dictionary
    analog_names = d['parameters']['ANALOG']['LABELS']['value']
    analog_data = d['data']['analogs']
    for i, analog_name in enumerate(analog_names):
        data[analog_name] = analog_data[0:3, i, :].T  # we only want XYZ components in N X 3 format

    # add meta information
    if 'parameters' in d.keys():
        data['parameters'] = {}
        params = list(d['parameters'].keys())
        for param in params:
            data['parameters'][param] = d['parameters'][param]

    # header
    if 'header' in d.keys():
        data['header'] = {}
        headers = list(d['header'].keys())
        for header in headers:
            data['header'][param] = d['header'][header]

    return data


import scipy.io
import numpy as np
from scipy.io.matlab.mio5_params import mat_struct
from collections.abc import Iterable


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


def zsave(data, file_path, message=None, verbose=False):
    """
    Save the dictionary as a special .zoo (MAT) file.

    Parameters:
    data (dict): The data to save as a .zoo file.
    file_path (str): The full path where the .zoo file will be saved.
    """

    #todo: save the process to Zoosystem

    # Ensure the file has a .zoo extension
    if not file_path.endswith('.zoo'):
        file_path += '.zoo'

    # Create the .mat file and rename to .zoo
    mat_file_path = file_path.replace('.zoo', '.mat')

    # Save the dictionary as a .mat file
    scipy.io.savemat(mat_file_path, data)

    # Rename the .mat file to .zoo
    os.rename(mat_file_path, file_path)

    if verbose:
        print('File saved successfully as {}'.format(file_path))


def zoo_to_dict(data):
    """ restructures a zoo file saved using scipy to matlab like dict"""


    return data

if __name__ == "__main__":
    # For basic testing

    # load c3d file
    current_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    fl_c3d = os.path.join(parent_dir, 'sample study/Data/raw c3d files/HC002D/Straight/HC002D06.c3d')

    # convert to zoo
    data1 = c3d_to_zoo(fl_c3d, verbose=True)

    # save zoo file as
    fl_zoo = fl_c3d.replace('.c3d', '_temp.zoo')
    zsave(data1, fl_zoo)

    # load zoo file
    data2 = zload(fl_zoo)

    # delete test file
    os.remove(fl_zoo)


