import os
from typing import Tuple


def fileparts(file: str) -> Tuple[str, str, str]:
    """
    Split a file path into its directory, filename, and extension.

    Parameters
    ----------
    file : str
        Full path to the file.

    Returns
    -------
    directory : str
        Directory containing the file.
    filename : str
        Base filename without extension.
    extension : str
        File extension including the leading dot (e.g. ``'.zoo'``).
    """

    directory = os.path.dirname(file)
    basename = os.path.basename(file)
    filename, extension = os.path.splitext(basename)



    return directory, filename, extension
