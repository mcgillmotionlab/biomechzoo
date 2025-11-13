import os
import numpy as np


def engine(root_folder, extension='.zoo', subfolders=None, name_contains=None,
           match_all=False, verbose=False):
    """
    Recursively search for files with a given extension, optionally filtering by
    specific subfolders and substrings in filenames.

    Arguments:
        root_folder (str): Root directory path where the search begins.
        extension (str): File extension to search for (e.g., '.zoo', '.c3d')
        subfolders (list or str, optional): Restrict search to folders with these names.
        name_contains (str or list, optional): Substring(s) that must appear in filename.
        match_all (bool, optional):
            If False, keep file if it contains ANY substring.
            If True, keep file only if it contains ALL substrings.
        verbose (bool): Print results.
    """

    # check format of subfolders
    if subfolders is not None:
        if isinstance(subfolders, str):
            subfolders = [subfolders]

    # check format of name_contains
    if name_contains is not None:
        if isinstance(name_contains, str):
            name_contains = [name_contains]

    matched_files = []
    subfolders_set = set(subfolders) if subfolders else None

    for dirpath, _, filenames in os.walk(root_folder):

        # Restrict to allowed subfolders
        if subfolders_set is not None:
            rel_path = os.path.relpath(dirpath, root_folder)
            if rel_path != '.':
                folder_parts = rel_path.split(os.sep)
                if not any(part in subfolders_set for part in folder_parts):
                    continue

        # Check each file
        for file in filenames:
            if not file.lower().endswith(extension.lower()):
                continue

            full_path = os.path.join(dirpath, file)

            # Substring filtering
            if name_contains is not None:
                file_lower = full_path.lower()
                checks = [(substr.lower() in file_lower) for substr in name_contains]

                if match_all and not all(checks):
                    continue
                if not match_all and not any(checks):
                    continue

            matched_files.append(full_path)

    # sort list
    matched_files = np.sort(matched_files)

    if verbose:
        print("Found {} {} file(s) in subfolder(s) {} with substrings {} (match_all={}):"
              .format(len(matched_files), extension, subfolders, name_contains, match_all))
        for f in matched_files:
            print("{}".format(f))

    return matched_files


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    sample_dir = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

    # Example: match any of the substrings
    engine(sample_dir, extension='.c3d',
           subfolders=['Straight'],
           name_contains=['HC03', 'HC04'],
           match_all=False,
           verbose=True)

    # example patch match both strings
    c3d_files = engine(sample_dir, extension='.c3d',
                       subfolders=['Straight'],
                       name_contains=['HC03', '10'],
                       match_all=True,
                       verbose=True)
