def batchdisp(msg, level=1, verbose='none'):
    """ utility to control verbosity level during batch processing"""
    level = _normalize_verbose(level)
    verbose = _normalize_verbose(verbose)
    if verbose >= level:
        print(msg)

def _normalize_verbose(verbose):
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


