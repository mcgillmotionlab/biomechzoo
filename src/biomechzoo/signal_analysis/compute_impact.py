import numpy as np
import scipy.signal as signal

from .autocorrelation import compute_autocorrelation

#todo: must be checked against the literature

def impact_peak(
        ch_line: np.ndarray,
        freq: int,
        distance_ratio: float = 0.9,
        relative_peak_height: float = 0.25,
        autocorrelation_peak_distance: int = 30,
        autocorrelation_duration_sec: float = 3,
        autocorrelation_peak_height: float = 0,
        peak_height: float = 0,
) -> tuple[list[int], list[float]]:

    """Find positive impact peaks and retain those above a relative height cutoff.

    Parameters
    ----------
    ch_line : numpy.ndarray
        One-dimensional signal to analyze.
    freq : int
        Signal sampling frequency in samples per second.
    distance_ratio : float, default=0.9
        Multiplier applied to the selected autocorrelation peak lag to set the
        minimum distance between signal peaks, in samples.
    relative_peak_height : float, default=0.25
        Retain peaks whose height is strictly greater than this fraction of the
        mean height of all candidate peaks.
    autocorrelation_peak_distance : int, default=30
        Minimum separation, in samples, between peaks detected in the
        autocorrelation.
    autocorrelation_duration_sec : float, default=3
        Maximum autocorrelation lag in seconds.
    autocorrelation_peak_height : float, default=0
        Minimum height for peaks detected in the autocorrelation.
    peak_height : float, default=0
        Minimum height for peaks detected in the input signal.

    Returns
    -------
    peak_indices : list[int]
        Indices of retained peaks in ``ch_line``.
    peak_heights : list[float]
        Heights of the retained peaks.
    """

    peaks_idx, peaks_properties = peak_impacts(ch_line, freq, distance_ratio=distance_ratio,
                                               autocorrelation_peak_distance=autocorrelation_peak_distance,
                                               autocorrelation_duration_sec=autocorrelation_duration_sec,
                                               autocorrelation_peak_height=autocorrelation_peak_height,
                                               peak_height=peak_height,)
    temp_heights = peaks_properties['peak_heights']
    mask = np.where(temp_heights > relative_peak_height * np.mean(temp_heights))
    eyd = temp_heights[mask]
    exd = peaks_idx[mask]
    return exd.tolist(), eyd.tolist()


def loading_rate(
        ch_line,
        freq,
        pre_peak_window=20,
        distance_ratio: float = 0.9,
        relative_peak_height: float = 0.25,
        autocorrelation_peak_distance: int = 30,
        autocorrelation_duration_sec: float = 3,
        autocorrelation_peak_height: float = 0,
        peak_height: float = 0,
):
    """Estimate the largest pre-peak sample difference for each impact peak.

    Parameters
    ----------
    ch_line : array-like
        One-dimensional signal to analyze.
    freq : int
        Signal sampling frequency in samples per second.
    pre_peak_window : int, default=20
        Number of samples before each peak searched for the largest first
        difference. If a peak occurs earlier, the window starts at sample zero.
    distance_ratio: relative_peak_height, autocorrelation_peak_distance,
    autocorrelation_duration_sec: Default 3
    autocorrelation_peak_height: pDefault 3
        Peak-selection settings; see :func:`impact_peak`.

    Returns
    -------
    peak_indices : list[int] or list containing None
        Indices of the maximum pre-peak differences, or ``[None]`` if no
        candidate impact peaks pass the relative-height cutoff.
    values : list[float] or list containing None
        Maximum first differences in the corresponding pre-peak windows, or
        ``[None]`` if no candidate impact peaks pass the cutoff.

    Notes
    -----
    The returned value is a sample-to-sample difference, not a time-normalized
    derivative; it depends on the signal's sampling frequency and units.
    """
    peaks_idx, peaks_properties = peak_impacts(
        ch_line,
        freq,
        distance_ratio=distance_ratio,
        autocorrelation_peak_distance=autocorrelation_peak_distance,
        autocorrelation_duration_sec=autocorrelation_duration_sec,
        autocorrelation_peak_height=autocorrelation_peak_height,
        peak_height=peak_height,
    )
    temp_heights = peaks_properties['peak_heights']
    mask = np.where(temp_heights > relative_peak_height * np.mean(temp_heights))
    peaks_idx = peaks_idx[mask]
    temp_heights = temp_heights[mask]
    eyd = []
    exd = []
    if len(peaks_idx) == 0:
        return [None, None]
    else:
        loading_rate = np.diff(ch_line)
        for p in peaks_idx:
            if p < pre_peak_window:
                start_index = 0
            else:
                start_index = p - pre_peak_window
            pre_peak_segment = loading_rate[start_index:p]
            eyd.append(np.max(pre_peak_segment))

            exd.append(np.argmax(pre_peak_segment) + start_index)
    return exd, eyd


def peak_impacts(
        data,
        freq,
        distance_ratio: float = 0.9,
        autocorrelation_peak_distance: int = 30,
        autocorrelation_duration_sec: float = 3,
        autocorrelation_peak_height: float = 0,
        peak_height: float = 0,
) -> tuple[list[int], list[float]]:

    """Detect signal peaks using a minimum spacing estimated from autocorrelation.

    Parameters
    ----------
    data : array-like
        One-dimensional signal in which to detect peaks.
    freq : int
        Signal sampling frequency in samples per second.
    distance_ratio : float, default=0.9
        Multiplier applied to the selected autocorrelation peak lag to obtain
        the minimum separation between signal peaks, in samples.
    autocorrelation_peak_distance : int, default=30
        Minimum separation, in samples, between peaks detected in the
        autocorrelation.
    autocorrelation_duration_sec : float, default=3
        Maximum autocorrelation lag in seconds.
    autocorrelation_peak_height : float, default=0
        Minimum height for peaks detected in the autocorrelation.
    peak_height : float, default=0
        Minimum height for peaks detected in the input signal.

    Returns
    -------
    peaks : numpy.ndarray
        Indices of detected peaks.
    properties : dict
        Peak properties returned by :func:`scipy.signal.find_peaks`.
    """
    min_distance = compute_distance(
        data,
        distance_ratio,
        freq,
        autocorrelation_peak_distance=autocorrelation_peak_distance,
        autocorrelation_duration_sec=autocorrelation_duration_sec,
        autocorrelation_peak_height=autocorrelation_peak_height,
    )
    peaks, properties = signal.find_peaks(data, distance=min_distance, height=peak_height)
    return peaks, properties


def compute_distance(
        data,
        distance_ratio,
        freq,
        autocorrelation_peak_distance: int = 30,
        autocorrelation_duration_sec: float = 3,
        autocorrelation_peak_height: float = 0,
):
    """Calculate minimum signal-peak spacing from the signal autocorrelation.

    The first autocorrelation peak is used unless it occurs before
    ``autocorrelation_peak_distance`` samples, in which case the next detected
    peak is used. The selected lag is multiplied by ``distance_ratio``.

    Parameters
    ----------
    data : array-like
        One-dimensional signal used to estimate periodicity.
    distance_ratio : float
        Multiplier applied to the selected autocorrelation peak lag.
    freq : int
        Signal sampling frequency in samples per second.
    autocorrelation_peak_distance : int, default=30
        Minimum separation, in samples, between peaks detected in the
        autocorrelation.
    autocorrelation_duration_sec : float, default=3
        Maximum autocorrelation lag in seconds.
    autocorrelation_peak_height : float, default=0
        Minimum height for peaks detected in the autocorrelation.

    Returns
    -------
    int
        Minimum separation between detected signal peaks, in samples.
    """
    autocorr = compute_autocorrelation(data, freq, duration_sec=autocorrelation_duration_sec)
    peaks, _ = signal.find_peaks(
        autocorr,
        distance=autocorrelation_peak_distance,
        height=autocorrelation_peak_height,
    )
    d_1 = peaks[0]
    if d_1 < autocorrelation_peak_distance:
        d_1 = peaks[1]
    return round(d_1 * distance_ratio)
