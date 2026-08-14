from importlib.metadata import version as get_version


def get_biomechzoo_version() -> str:
    """
    Get the installed biomechzoo package version.

    Returns
    -------
    version : str
        Installed biomechzoo version string.
    """
    version = get_version("biomechzoo")

    return version
