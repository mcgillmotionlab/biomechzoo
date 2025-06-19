import os


def engine(root_folder, extension, subfolders=None, name_contains=None):
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

    return matched_files


if __name__ == '__main__':
    """ testing: use engine to search for files in any subfolder called 'Straight' for files with the substring 'HC03'
    with extension .c3d in the sample study folder (data)"""
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    sample_dir = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')
    c3d_files = engine(sample_dir, '.c3d', subfolders=['Straight'], name_contains='HC03')
    print("Found {} .c3d files in subfolders named 'Straight':".format(len(c3d_files)))
    for f in c3d_files:
        print(" - {}".format(f))