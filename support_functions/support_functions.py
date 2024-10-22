from pathlib import Path

import scipy.io
from scipy.io.matlab.mio5_params import mat_struct
import numpy as np
import os
from datetime import datetime
import inspect


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
    # todo: mat2struct is slow, needs to be sped up

    # Check if the file exists
    if not os.path.exists(file_path):
        print('File {} not found'.format(file_path))
        return None

    try:
        # Load the .zoo (MAT) file
        data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
        data = data['data']
        data = mat_struct_to_dict(data)

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


def initiatefxn(file, other):
    """
    Function to initiate the file matching process based on criteria.
    """
    if not other:
        return [str(file)]
    else:
        key, value = list(other.items())[0]
        if key == 'extension':
            return findextension(file, value)
        elif key == 'search_file':
            return searchfile(file, value)
        else:
            return []


def findextension(file, ext):
    """
    Find files with a specific extension.
    """
    if file.suffix == ext:
        return [str(file)]
    return []


def searchfile(file, src):
    """
    Search for a specific string in the file name.
    """
    if src in file.name:
        return [str(file)]
    return []


def fileparts(file):
    """
   Splits the file path into directory, filename, and extension.

   Arguments:
   file_path -- str. The full file path.

   Returns:
   tuple -- (directory, filename, extension)
   """

    directory = os.path.dirname(file)
    basename = os.path.basename(file)
    filename, ext = os.path.splitext(basename)

    return directory, filename, ext


def checkinput(pth, ext):
    """
    standalone function used to test whether input is list of files from engine or folder
        pth: string or list, pointing to file(s) or folder
        ext: string, extension type
    Returns:

    """
    if ext in pth:
        # this is a single path with an extension
        fld, _, _ = fileparts(pth)
        fl = pth
        saveFile = False

    elif isinstance(pth, str):
        # this is a single folder
        fld = pth
        fl = engine(path=pth, ext=ext)
        saveFile = True
    elif isinstance(pth, list):
        # this is a list of files extracted from folder using engine
        fl = pth
        fld = None
        saveFile = True

    return fld, fl, saveFile


if __name__ == "__main__":
    # For basic testing

    # save zoo file as
    fl_zoo = fl_c3d.replace('.c3d', '_temp.zoo')

    # load zoo file
    data2 = zload(fl_zoo)

    # delete test file
    os.remove(fl_zoo)


def engine(**kwargs):
    """
    File searching algorithm.

    Arguments are in pairs where the first element is the property name and the second is a property value.
    The 'path' property is required. All other properties are optional. All arguments must be strings.

    Arguments:
    'path' or 'fld' ... folder path to begin the search as string
    'extension'     ... type of file to search as string. e.g., '.c3d' or 'csv'
    'search_file'   ... return only files containing specific string e.g., '_g_'
    'search_path'   ... search for a particular string in the path name e.g., 'hello' in data/hello
    'folder'        ... search only in folders of a specific name located downstream from the path (string)

    Returns:
    list -- A list of file paths that match the criteria.
    """
    #todo: engine could probably be updated using glob module

    path = kwargs.get('path') or kwargs.get('fld', '')
    folder = kwargs.get('folder', 'all')
    search = kwargs.get('search_path', 'all')
    other = {k: v for k, v in kwargs.items() if k not in ['path', 'fld', 'folder', 'search_path']}

    if not path:
        return []

    if len(other) <= 1:
        return fldengine(path, folder, search, other)
    elif len(other) == 2:
        fl1 = fldengine(path, folder, search, {list(other.keys())[0]: list(other.values())[0]})
        fl2 = fldengine(path, folder, search, {list(other.keys())[1]: list(other.values())[1]})
        return list(set(fl1).intersection(fl2))
    else:
        raise ValueError('too many arguments for other input')


def fldengine(path, folder, search, other):
    """
    Recursive search function to handle folder and search path logic.
    """
    path = Path(path)
    if not path.is_dir():
        return []

    files = []
    if folder == 'all':
        files.extend(srcengine(path, search, other))
    else:
        for subdir in path.iterdir():
            if subdir.is_dir() and subdir.name == folder:
                files.extend(srcengine(subdir, search, other))
            else:
                files.extend(fldengine(subdir, folder, search, other))
    return files


def srcengine(path, search, other):
    """
    Search function to handle the specific search criteria.
    """
    path = Path(path)
    if not path.is_dir():
        return []

    files = []
    for file in path.iterdir():
        if file.is_file() and (search == 'all' or search in str(file)):
            files.extend(initiatefxn(file, other))
        elif file.is_dir():
            files.extend(srcengine(file, search, other))
    return files
