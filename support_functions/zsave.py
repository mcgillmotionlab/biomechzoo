import inspect
import os
from datetime import datetime

import scipy.io

from support_functions.fileparts import fileparts


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
