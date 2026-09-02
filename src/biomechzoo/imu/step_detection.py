from typing import List, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.signal import butter, filtfilt, find_peaks

from kielmat.utils.preprocessing import (
    signal_decomposition_algorithm,
)


def imu_kielmat(
    vertical_acceleration: NDArray[np.floating],
    fsamp: float,
) -> Tuple[NDArray[np.int_], NDArray[np.int_]]:
    """Detect foot-strike and foot-off events using KielMAT.

    Parameters
    ----------
    vertical_acceleration : ndarray
        One-dimensional vertical acceleration signal in m/s/s.
    fsamp : float
        Sampling frequency in Hz.

    Returns
    -------
    fs : ndarray
        Foot-strike frame indices.
    fo : ndarray
        Foot-off frame indices.

    Raises
    ------
    ValueError
        If the acceleration signal is not one-dimensional, contains
        non-finite values, or if the sampling frequency is invalid.
    """
    vertical_acceleration = np.asarray(
        vertical_acceleration,
        dtype=float,
    ).squeeze()

    if vertical_acceleration.ndim != 1:
        raise ValueError(
            'Vertical acceleration must be one-dimensional'
        )

    if not np.all(np.isfinite(vertical_acceleration)):
        raise ValueError(
            'Vertical acceleration contains non-finite values'
        )

    if fsamp <= 0:
        raise ValueError(
            'Sampling frequency must be greater than zero'
        )

    fs_times, fo_times = signal_decomposition_algorithm(
        vertical_accelerarion_data=vertical_acceleration,
        initial_sampling_frequency=fsamp,
    )

    fs = _times_to_frames(fs_times, fsamp, len(vertical_acceleration))
    fo = _times_to_frames(fo_times, fsamp, len(vertical_acceleration))

    return fs, fo


def _times_to_frames(
    event_times: NDArray[np.floating],
    fsamp: float,
    n_frames: int,
) -> NDArray[np.int_]:
    """Convert event times in seconds to valid zero-based frame indices.

    Parameters
    ----------
    event_times : ndarray
        Event times in seconds relative to the signal start.
    fsamp : float
        Sampling frequency in Hz.
    n_frames : int
        Number of signal frames.

    Returns
    -------
    frames : ndarray
        Sorted, unique, zero-based frame indices.
    """
    event_times = np.asarray(event_times, dtype=float).squeeze()

    if event_times.size == 0:
        return np.array([], dtype=int)

    frames = np.rint(np.atleast_1d(event_times) * fsamp).astype(int)
    frames = frames[(frames >= 0) & (frames < n_frames)]

    return np.unique(frames)

def imu_mcgrath(
        ch_line: ArrayLike, fsamp: float, min_stance_t: float,
        is_filtered: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detect gait events using the method of McGrath et al. (2012).

    The first minimum after a local maximum midswing peak is taken as
    initial contact (heel strike); the first valid minimum before a
    midswing peak is taken as terminal contact (toe off). Reference:
    https://doi.org/10.1007/s12283-012-0093-8

    Parameters
    ----------
    ch_line : array_like
        Vertical acceleration signal.
    fsamp : float
        Sampling frequency in Hz.
    min_stance_t : float
        Minimum stance time, in milliseconds, used to validate
        detected steps.
    is_filtered : bool, optional
        If True, ``ch_line`` is assumed to already be filtered and no
        additional low-pass filtering is applied. Default is False.

    Returns
    -------
    IC : ndarray
        Indices of detected initial contact (heel strike) events.
    TC : ndarray
        Indices of detected terminal contact (toe off) events.
    """

    if is_filtered:
        yd = ch_line
    else:
        # Butterworth filter
        order = 5
        Fc = 5
        Wn = Fc / (fsamp / 2)
        [b, a] = butter(order, Wn, btype='low')
        yd = filtfilt(b, a, ch_line)


    # Identify midswing peaks
    t1 = round(fsamp / 2)
    potential_midswing_ind, _ = find_peaks(yd, distance=t1)
    potential_midswing_mag = yd[potential_midswing_ind]

    # Thresholds for midswing
    th2 = 0.8 * np.mean(yd[yd > np.mean(yd)])
    mask = potential_midswing_mag >= th2
    potential_midswing_ind = potential_midswing_ind[mask]
    potential_midswing_mag = potential_midswing_mag[mask]

    th1 = 0.3 * potential_midswing_mag

    # Find minima
    minima_ind, _ = find_peaks(-yd)
    minima_mag = -yd[minima_ind]

    # Validate midswing peaks
    valid_inds = []
    for i in range(len(potential_midswing_ind) - 1, -1, -1):
        peak_idx = potential_midswing_ind[i]
        preceding_min = minima_ind[minima_ind < peak_idx]
        if preceding_min.size > 0:
            closest_min_idx = preceding_min[-1]
            pos = np.where(minima_ind == closest_min_idx)[0][0]
            if (potential_midswing_mag[i] - minima_mag[pos]) >= th1[i]:
                valid_inds.append(peak_idx)
    potential_midswing_ind = np.array(valid_inds)

    # Additional thresholds
    th3 = 0.8 * abs(np.mean(yd[yd < np.mean(yd)]))
    th4 = 0.8 * np.mean(yd[yd < np.mean(yd)])
    th5 = np.mean(yd)
    th6 = 2 * th3

    maxima_ind, _ = find_peaks(yd)
    maxima_mag = yd[maxima_ind]

    IC, TC = [], []
    t2 = round(1.5 * fsamp)

    # Loop through confirmed midswing peaks
    for step_idx in range(len(potential_midswing_ind) - 1, -1, -1):
        peak_idx = potential_midswing_ind[step_idx]

        # IC candidates (minima after midswing)
        end_idx = min(peak_idx + t2, len(yd))
        ic_candidates, _ = find_peaks(-yd[peak_idx:end_idx])
        ic_candidates = ic_candidates + peak_idx
        ic_mags = yd[ic_candidates]

        # Filter IC by threshold
        ic_candidates = ic_candidates[ic_mags < th5]
        ic_mags = ic_mags[ic_mags < th5]

        # Validate IC with preceding maxima
        for ic_idx in ic_candidates:
            preceding_max = maxima_ind[maxima_ind < ic_idx]
            if preceding_max.size > 0:
                closest_max_idx = preceding_max[-1]
                if yd[closest_max_idx] >= yd[ic_idx] + th3:
                    IC.append(ic_idx)
                    break

        # TC candidates (minima before midswing)
        start_idx = max(peak_idx - t2, 0)
        tc_candidates, _ = find_peaks(-yd[start_idx:peak_idx])
        tc_candidates = tc_candidates + start_idx
        tc_mags = yd[tc_candidates]

        # Filter TC by threshold
        tc_candidates = tc_candidates[tc_mags < th4]
        tc_mags = tc_mags[tc_mags < th4]

        # Validate TC with following maxima
        for tc_idx in tc_candidates:
            following_max = maxima_ind[maxima_ind > tc_idx]
            if following_max.size > 0:
                closest_max_idx = following_max[0]
                if yd[closest_max_idx] >= yd[tc_idx] + th6:
                    TC.append(tc_idx)
                    break

    # Crash handling
    IC, TC = crash_catch(int(min_stance_t * fsamp / 1000), IC, TC)

    return IC, TC

def crash_catch(
        min_stance_samples: int, IC: List[int], TC: List[int],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ensure initial and terminal contact index arrays are the same
    length, truncating any extra detections.

    Parameters
    ----------
    min_stance_samples : int
        Unused. Reserved for future stance-time validation.
    IC : list of int
        Indices of detected initial contact events.
    TC : list of int
        Indices of detected terminal contact events.

    Returns
    -------
    IC : ndarray
        Initial contact indices, truncated to match ``TC`` length.
    TC : ndarray
        Terminal contact indices, truncated to match ``IC`` length.
    """
    # Ensure IC and TC arrays are same length and valid
    IC = np.array(IC)
    TC = np.array(TC)
    if len(IC) != len(TC):
        min_len = min(len(IC), len(TC))
        IC = IC[:min_len]
        TC = TC[:min_len]
    return IC, TC