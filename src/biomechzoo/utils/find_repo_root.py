import os

def find_repo_root(path=None, marker="README.md"):
    """
    Find the nearest parent directory containing the specified marker file.

    Parameters
    ----------
    path : str. If None, defaults to the current working directory.
        Starting file or directory.
    marker : str, optional
        File used to identify the repository root. Default README.md

    Returns
    -------
    str
        Absolute path to the repository root.

    Raises
    ------
    RuntimeError
        If the marker cannot be found.
    """

    if path is None:
        path = __file__
    else:
        path = os.path.abspath(path)

    if os.path.isfile(path):
        path = os.path.dirname(path)

    while True:

        if os.path.isfile(os.path.join(path, marker)):
            return path

        parent = os.path.dirname(path)

        if parent == path:
            raise RuntimeError(
                "Could not locate repository root containing '{}'".format(marker)
            )

        path = parent