import time
import copy
import numpy as np
import inspect
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp

def _apply_lag(sig: np.ndarray, lag: int) -> np.ndarray:
    """Trim `lag` samples from the start (positive) or end (negative) of a signal."""
    if lag > 0:
        return sig[lag:]
    elif lag < 0:
        return sig[:lag]
    return sig

def _cross_correlation(sig1: np.ndarray, sig2: np.ndarray) -> int:
    """
    Estimate the lag between two multi-channel signals using cross-correlation
    of their norms.

    Parameters
    ----------
    sig1 : np.ndarray
        Array of shape (ch, N) for the first signal group.
    sig2 : np.ndarray
        Array of shape (ch, N) for the second signal group.

    Returns
    -------
    int
        Estimated lag in samples. Positive means sig1 leads sig2;
        negative means sig2 leads sig1.
    """
    mag1 = np.linalg.norm(sig1, axis=0)
    mag2 = np.linalg.norm(sig2, axis=0)

    corr = np.correlate(mag1 - mag1.mean(), mag2 - mag2.mean(), mode='full')

    lag = int(np.argmax(corr) - (len(mag1) - 1))

    return lag

def sync_channels_data(data: dict, method: str, ch_1: list[str], ch_2: list[str]) -> dict:
    """
    Estimate the lag between two groups of channels and apply it to all
    channels in the zoo data dictionary.

    The lag is estimated using only ``ch_1`` and ``ch_2``, but the resulting
    shift is applied to every channel sharing the same system suffix as
    ``ch_1`` and ``ch_2`` respectively.

    .. note::
        Suffix-based channel grouping assumes that ``bmech.combine_files``
        was used to combine data sources. This function appends a suffix to
        all channel names (e.g. ``'LSh_LH_alpha_imu'``, ``'LSh_LH_alpha_plate'``),
        which is what this function uses to identify which channels belong to
        which system.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing the channels to synchronise.
    method : str
        Synchronisation method. Currently supported: ``'cross-correlation'``.
        The cross-correlation method computes the L2 norm across all channels
        in each group per frame, then finds the lag that maximises the
        cross-correlation of those magnitude signals.
    ch_1 : list[str]
        Channel names used to estimate the lag for the first system
        (e.g. ``['LSh_LH_alpha_imu', 'LH_LF_alpha_imu']``).
    ch_2 : list[str]
        Channel names used to estimate the lag for the second system
        (e.g. ``['LSh_LH_alpha_plate', 'LH_LF_alpha_plate']``).

    Returns
    -------
    dict
        A deep copy of ``data`` with all channels in each system shifted
        and truncated to equal length.

    Raises
    ------
    ValueError
        If ``ch_1`` and ``ch_2`` differ in length, or if ``method`` is not supported.
    """

    supported_methods = {"cross-correlation": _cross_correlation}

    if method not in supported_methods:
        raise ValueError(f"Unknown method '{method}'. Supported: {set(supported_methods)}")

    if len(ch_1) != len(ch_2):
        raise ValueError("ch_1 and ch_2 must have the same number of channels.")

    data_copy = copy.deepcopy(data)

    sig1_stack = [np.array(data_copy[ch]['line']) for ch in ch_1]
    sig2_stack = [np.array(data_copy[ch]['line']) for ch in ch_2]

    min_len = min(len(s) for s in sig1_stack + sig2_stack)
    sig1 = np.stack([s[:min_len] for s in sig1_stack], axis=0)
    sig2 = np.stack([s[:min_len] for s in sig2_stack], axis=0)

    lag = supported_methods[method](sig1, sig2)

    sync_meta = data_copy['zoosystem']['Other'].setdefault('Sync Channels', {})
    sync_meta['detected_lag'] = int(lag)

    suffix_1 = '_' + ch_1[0].rsplit('_', maxsplit=1)[-1]
    suffix_2 = '_' + ch_2[0].rsplit('_', maxsplit=1)[-1]

    all_ch_1 = [k for k in data_copy if k.endswith(suffix_1)]
    all_ch_2 = [k for k in data_copy if k.endswith(suffix_2)]

    if lag > 0:
        for ch in all_ch_1:
            data_copy[ch]['line'] = _apply_lag(np.array(data_copy[ch]['line']), lag).tolist()
    elif lag < 0:
        for ch in all_ch_2:
            data_copy[ch]['line'] = _apply_lag(np.array(data_copy[ch]['line']), -lag).tolist()

    final_len = min(len(data_copy[ch]['line']) for ch in all_ch_1 + all_ch_2)
    for ch in all_ch_1 + all_ch_2:
        data_copy[ch]['line'] = data_copy[ch]['line'][:final_len]

    return data_copy