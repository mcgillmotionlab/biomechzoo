from scipy.io import savemat
import inspect
import os

from biomechzoo.utils.batchdisp import batchdisp


def zsave(fl, data, inplace=True, out_folder=None, root_folder=None, verbose=False):
    """
    Save zoo data to a .zoo file (MATLAB MAT format).

    Parameters
    ----------
    fl : str
        Full path to the original .zoo file.
    data : dict
        Zoo data dictionary to save.
    inplace : bool, optional
        If True, overwrite the original file. Default is True.
    out_folder : str or None, optional
        Output folder name (relative to ``root_folder`` or the file's
        location) when ``inplace=False``.
    root_folder : str or None, optional
        Optional base directory used when ``inplace=False``.
    verbose : bool, optional
        If True, print save progress. Default is False.
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
        fl_new = fl
        out_dir = os.path.dirname(fl)
    else:
        if out_folder is None:
            out_folder = 'processed'

        if root_folder is None:
            root_folder = os.path.dirname(fl)

        root_path = os.path.dirname(root_folder)
        in_folder = os.path.basename(root_folder)
        out_dir = os.path.join(root_path, out_folder)
        os.makedirs(out_dir, exist_ok=True)
        fl_new = fl.replace(in_folder, out_folder)
        save_folder = os.path.dirname(fl_new)
        os.makedirs(save_folder, exist_ok=True)

    # Save the .zoo file
    savemat(fl_new, data)
    batchdisp('all files saved to ' + out_dir, level=1, verbose=verbose)


