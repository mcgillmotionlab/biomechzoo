from scipy.io import savemat
import inspect
import os


def zsave(fl, data, inplace=True, out_folder=None, root_folder=None):
    """
    Save zoo data to .zoo file (MAT format)

    Arguments:
        fl (str): Full path to original .zoo file
        data (dict): Zoo data to save
        inplace (bool): Whether to overwrite original file
        out_folder (str or None): If not inplace, output folder name (relative to root_folder or file location)
        root_folder (str or None): Optional base directory for saving when inplace=False
    """
    # Get caller function name for logging
    caller_name = inspect.stack()[1].function

    # Initialize zoosystem and processing history
    zoosystem = data.get('zoosystem', {})
    processing = zoosystem.get('Processing', [])
    if not isinstance(processing, list):
        processing = [processing]
    processing.append(caller_name)
    zoosystem['Processing'] = processing
    data['zoosystem'] = zoosystem

    # Determine save path
    if inplace:
        save_path = fl
    else:
        filename = os.path.basename(fl)
        if out_folder is None:
            out_folder = 'processed'

        if root_folder is None:
            root_folder = os.path.dirname(fl)

        root_path = os.path.dirname(root_folder)
        out_dir = os.path.join(root_path, out_folder)
        os.makedirs(out_dir, exist_ok=True)
        save_path = os.path.join(out_dir, filename)

    # Save the .zoo file
    savemat(save_path, data)

