from pathlib import Path


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
