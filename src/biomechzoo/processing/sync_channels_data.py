import copy
import numpy as np


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

def sync_channels_data(data: dict, method: str, ch_1: list[str], ch_2: list[str], manual_lag: int = None) -> dict:
    """
    Synchronize two groups of channels within a data dictionary by estimating
    or applying a temporal lag.

    The lag is estimated from a representative subset of channels (`ch_1`, `ch_2`)
    and then applied to all channels sharing the same suffix. After alignment,
    all affected channels are trimmed to a common length.

    Parameters
    ----------
    data : dict
        Dictionary of channel data.
    method : str
        Synchronization method. Supported options:

        - ``'cross-correlation'`` : estimates lag automatically using
          normalized cross-correlation across the provided channel pairs.
        - ``'manual'`` : applies a user-specified lag via ``manual_lag``.
    ch_1 : list of str
        Channel names from the first signal group used to estimate the lag.
        Must have the same length as `ch_2`. The suffix of ``ch_1[0]``
        determines which channels in `data` are shifted.
    ch_2 : list of str
        Channel names from the second signal group used to estimate the lag.
        Must have the same length as `ch_1`. The suffix of ``ch_2[0]``
        determines which channels in `data` are shifted.
    manual_lag : int, optional
        Number of samples to shift when ``method='manual'``. Positive values
        shift `ch_1` channels forward; negative values shift `ch_2` channels
        forward. Required when ``method='manual'``, ignored otherwise.

    Returns
    -------
    dict
        A deep copy of `data` with the lagged channels shifted and all
        affected channels trimmed to a common length.

    Raises
    ------
    ValueError
        If `method` is not one of the supported options.
    ValueError
        If `ch_1` and `ch_2` have different lengths.
    ValueError
        If ``method='manual'`` and `manual_lag` is not provided.
    ValueError
        If no channels are found in `data` matching the inferred suffixes
        of `ch_1` or `ch_2`.
    """
    supported_methods = {"cross-correlation", "manual"}

    if method not in supported_methods:
        raise ValueError(f"Unknown method '{method}'. Supported: {supported_methods}")
    if len(ch_1) != len(ch_2):
        raise ValueError("ch_1 and ch_2 must have the same number of channels.")

    data_copy = copy.deepcopy(data)

    sig1_stack = [np.array(data_copy[ch]['line']) for ch in ch_1]
    sig2_stack = [np.array(data_copy[ch]['line']) for ch in ch_2]

    if method == "cross-correlation":
        max_len = max(len(s) for s in sig1_stack + sig2_stack)
        sig1 = np.stack([np.pad(s, (0, max_len - len(s))) for s in sig1_stack], axis=0)
        sig2 = np.stack([np.pad(s, (0, max_len - len(s))) for s in sig2_stack], axis=0)
        lag = _cross_correlation(sig1, sig2)

    elif method == "manual":
        if manual_lag is None:
            raise ValueError("manual_lag must be provided when method='manual'.")
        lag = manual_lag

    suffix_1 = '_' + ch_1[0].rsplit('_', 1)[-1]
    suffix_2 = '_' + ch_2[0].rsplit('_', 1)[-1]

    all_ch_1 = [k for k in data_copy if k.endswith(suffix_1)]
    all_ch_2 = [k for k in data_copy if k.endswith(suffix_2)]

    if not all_ch_1 or not all_ch_2:
        raise ValueError(f"No channels found for suffix '{suffix_1}' or '{suffix_2}'.")

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