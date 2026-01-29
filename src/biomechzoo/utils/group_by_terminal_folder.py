import os

def group_by_terminal_folder(files, root):
    groups = {}
    for f in files:
        folder = os.path.dirname(f)
        if folder not in groups:
            groups[folder] = []
        groups[folder].append(f)
    return groups