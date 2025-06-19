from support_functions.fileparts import fileparts
from support_functions.engine import engine


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
