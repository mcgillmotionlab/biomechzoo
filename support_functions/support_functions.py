import os

from support_functions.engine import engine


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