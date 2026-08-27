import os
from typing import Optional


def find_repo_root(
        path: Optional[str] = None, marker: str = "README.md",
) -> str:
    """
    Find the nearest parent directory containing the specified marker file.

    Parameters
    ----------
    path : str, optional
        Starting file or directory to search upward from. If None,
        defaults to this module's file location.
    marker : str, optional
        File used to identify the repository root. Default is
        ``'README.md'``.

    Returns
    -------
    path : str
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