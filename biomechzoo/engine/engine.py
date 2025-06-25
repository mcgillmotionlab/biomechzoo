import os


def engine(root_folder, extension='.zoo', subfolders=None, name_contains=None, verbose=False):
    """
    Recursively search for files with a given extension, optionally filtering by
    specific subfolders and substrings in filenames.

    This function walks through every directory and subdirectory starting at
    'root_folder'. If 'subfolders' is provided, it limits the search only to those
    folders (or any of their subfolders) whose names appear in 'subfolders'. For
    example, if subfolders=['Straight'], it will only consider files inside any
    folder named 'Straight' at any depth within the root folder.

    For each file found, it checks whether the file's extension matches the given
    'extension' (case-insensitive). If 'name_contains' is specified, it also
    requires the filename to contain that substring (case-insensitive).

    Arguments:
        root_folder (str): The root directory path where the search begins.
        extension (str): File extension to search for (e.g., '.zoo', '.c3d'). Default .zoo
        subfolders (list of str, optional): List of folder names to restrict the search to.
            Only files inside these folders (or their subfolders) are included.
            If None, search all subfolders.
        name_contains (str, optional): Substring that must be present in the filename
            (case-insensitive). If None, no substring filtering is applied.
        verbose (bool, optional): If true, displays additional information to user
    Returns:
        list of str: List of full file paths matching the criteria.
    """
    matched_files = []

    subfolders_set = set(subfolders) if subfolders else None

    for dirpath, _, filenames in os.walk(root_folder):
        if subfolders_set is not None:
            rel_path = os.path.relpath(dirpath, root_folder)
            if rel_path == '.':
                continue
            # Split the relative path into all folder parts
            parts = rel_path.split(os.sep)
            # Check if any folder in the path matches one in subfolders_set
            if not any(part in subfolders_set for part in parts):
                continue

        for file in filenames:
            if not file.lower().endswith(extension.lower()):
                continue
            if name_contains and name_contains.lower() not in file.lower():
                continue
            matched_files.append(os.path.join(dirpath, file))

    if verbose:
        print("Found {} {} files in subfolders named {} with substring {}:".format(len(matched_files), extension, subfolders, name_contains))
        for f in matched_files:
            print(" - {}".format(f))

    return matched_files


if __name__ == '__main__':
    """ testing: use engine to search for files in any subfolder called 'Straight' for files with the substring 'HC03'
    with extension .c3d in the sample study folder (data)"""
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    sample_dir = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')
    c3d_files = engine(sample_dir, '.c3d', subfolders=['Straight'], name_contains='HC03', verbose=True)
