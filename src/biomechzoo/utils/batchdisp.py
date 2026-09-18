from typing import Union


def batchdisp(
        msg: str, level: int = 1,
        verbose: int = 0,
) -> None:
    """
    Print a message if the verbosity level permits.

    Parameters
    ----------
    msg : str
        Message to print.
    level : {0, 1, 2}, optional
        Verbosity level required for ``msg`` to be printed. Default is 1.
    verbose : {0, 1, 2}, optional
        Current verbosity setting. ``msg`` is printed when ``verbose``
        is greater than or equal to ``level``. Default is 0.
    """
    # level = _normalize_verbose(level)
    # verbose = _normalize_verbose(verbose)

    if level not in (0, 1, 2):
        raise ValueError(
            'level must be 0, 1, or 2.'
        )

    if verbose not in (0, 1, 2):
        raise ValueError(
            'verbose must be 0, 1, or 2.'
        )

    if verbose >= level:
        print(msg)


if __name__ == '__main__':

    print('Testing batchdisp()')
    batchdisp(msg='This should print', level=1, verbose=1)

