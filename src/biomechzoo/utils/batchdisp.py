from typing import Union


def batchdisp(
        msg: str, level: Union[int, str] = 1,
        verbose: Union[int, str] = 'none',
) -> None:
    """
    Print a message if the verbosity level permits.

    Parameters
    ----------
    msg : str
        Message to print.
    level : {0, 1, 2, 'none', 'minimal', 'all'}, optional
        Verbosity level required for ``msg`` to be printed. Default is 1.
    verbose : {0, 1, 2, 'none', 'minimal', 'all'}, optional
        Current verbosity setting. ``msg`` is printed when ``verbose``
        is greater than or equal to ``level``. Default is ``'none'``.
    """
    level = _normalize_verbose(level)
    verbose = _normalize_verbose(verbose)
    if verbose >= level:
        print(msg)


def _normalize_verbose(verbose: Union[int, str]) -> int:
    """
    Normalize a verbosity level to its integer representation.

    Parameters
    ----------
    verbose : {0, 1, 2, 'none', 'minimal', 'all'}
        Verbosity level as an integer or string.

    Returns
    -------
    level : int
        Normalized verbosity level (0, 1, or 2).
    """
    if isinstance(verbose, int):
        if verbose not in (0, 1, 2):
            raise ValueError("Integer verbose level must be 0 (none), 1 (minimal), or 2 (all)")
        return verbose
    elif isinstance(verbose, str):
        verbose_map = {'none': 0, 'minimal': 1, 'all': 2}
        if verbose.lower() not in verbose_map:
            raise ValueError("String verbose level must be 'none', 'minimal', or 'all'")
        return verbose_map[verbose.lower()]
    else:
        raise TypeError("Verbose must be an int (0–2) or str ('none', 'minimal', 'all')")


