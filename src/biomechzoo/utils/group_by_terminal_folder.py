import os
from typing import Dict, List


def group_by_terminal_folder(
        files: List[str], root: str,
) -> Dict[str, List[str]]:
    """
    Group file paths by their containing (terminal) folder.

    Parameters
    ----------
    files : list of str
        File paths to group.
    root : str
        Unused. Reserved for future path-relativization support.

    Returns
    -------
    groups : dict of {str : list of str}
        Mapping of each unique parent folder to the list of files it
        contains.
    """
    groups = {}
    for f in files:
        folder = os.path.dirname(f)
        if folder not in groups:
            groups[folder] = []
        groups[folder].append(f)

    return groups