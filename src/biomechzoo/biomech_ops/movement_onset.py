import numpy as np
import scipy.signal as signal

def movement_onset(yd, fsamp, constants):
    """
    Detect the time of movement onset from an acceleration magnitude signal.

    Uses sliding-window mean and standard deviation to identify when sustained
    movement begins. Thresholds are relaxed iteratively if no onset is found.

    Parameters
    ----------
    yd : ndarray
        1-D array of the acceleration magnitude signal.
    fsamp : float
        Sampling frequency in Hz.
    constants : list of float
        Threshold constants ``[mean_thresh, std_thresh]``. Recommended values:
        running — ``[1.2, 0.2]``; walking — ``[0.6, 0.2]``.

    Returns
    -------
    onset_time : int or None
        Sample index of detected movement onset, or None if not detected.

    Notes
    -----
    The signal is low-pass filtered at 20 Hz (4th-order Butterworth) before
    feature extraction. Thresholds are halved each iteration until onset is
    found or the minimum threshold (0.1) is reached.
    """
    acc_mag = yd.copy()
    acc_mag_filtered = bw_filter(data=acc_mag, fsamp=fsamp, N=4, fc=20, btype="low")
    features, timestamps = sliding_window_features(ch_data=acc_mag_filtered, fsamp=fsamp)

    mean_thresh, std_thresh = constants[0], constants[1]
    min_thresh = 0.1
    onset_time = None
    while onset_time is None and mean_thresh > min_thresh:
        # ----Check if already moving----
        if check_already_moving(features=features, mean_thresh=mean_thresh, std_thresh=std_thresh):
            onset_time = timestamps[0]

        # ----Try detecting onset----
        else:
            onset_index = detect_movement_onset(features, fsamp, mean_thresh, std_thresh)
            if onset_index is not None:
                onset_time = timestamps[onset_index]
            else:
                # relax thresholds for next iteration
                mean_thresh /=2
                std_thresh /= 2

    return onset_time


def movement_offset(yd, fsamp, constants):
    """
    Detect the time of movement offset from an acceleration magnitude signal.

    Mirrors the logic of :func:`movement_onset` by reversing the signal
    before detection, then mapping the result back to original time.

    Parameters
    ----------
    yd : ndarray
        1-D array of the acceleration magnitude signal.
    fsamp : float
        Sampling frequency in Hz.
    constants : list of float
        Threshold constants ``[mean_thresh, std_thresh]``.

    Returns
    -------
    onset_time : int or None
        Sample index of detected movement offset, or None if not detected.
    """
    # ----extract the constants----
    mean_thresh, std_thresh = constants[0], constants[1]
    min_thresh = 0.1
    onset_time = None

    # ----Reverse, filter and extract features from the signa;----
    acc_mag = yd.copy()
    acc_mag = acc_mag[::-1]

    acc_mag_filtered = bw_filter(data=acc_mag, N=4, fc=20, btype="low", fsamp=fsamp)
    features, timestamps = sliding_window_features(ch_data=acc_mag_filtered, fsamp=fsamp)

    # ----reverse timestamps----
    timestamps = timestamps[::-1]

    while onset_time is None and mean_thresh > min_thresh:
        # ----Check if already moving----
        if check_already_moving(features=features, mean_thresh=mean_thresh, std_thresh=std_thresh):
            onset_time = timestamps[0]

        # ----Try detecting onset----
        else:
            onset_index = detect_movement_onset(features, fsamp, mean_thresh, std_thresh)
            if onset_index is not None:
                onset_time = timestamps[onset_index]
            else:
                # relax thresholds for next iteration
                mean_thresh /= 2
                std_thresh /= 2

    return onset_time


def sliding_window_features(ch_data, fsamp):
    # ----sliding window features----
    features = []
    timestamps = []
    window_size = 2 * fsamp  # windows van 2 seconds
    step_size = 1 * fsamp  # with an overlap of 1 seconds

    for start in range(0, len(ch_data) - window_size, step_size):
        segment = ch_data[start:start + window_size]
        mean_val = segment.mean()
        std_val = segment.std()
        # entropy = -np.sum((segment / np.sum(segment)) * np.log2(segment / np.sum(segment) + 1e-12))
        timestamps.append(start)
        features.append((mean_val, std_val))

    return np.array(features), np.array(timestamps)


def check_already_moving(features, mean_thresh=1.2, std_thresh=0.2):
    initial_window = features[:5]  # First few seconds
    if np.all(initial_window[:, 0] > mean_thresh) and np.all(initial_window[:, 1] > std_thresh):
        return True
    return False

def detect_movement_onset(features, fs, mean_thresh=1.2, std_thresh=0.2, min_duration=3):
    movement_flags = (features[:, 0] > mean_thresh) & (features[:, 1] > std_thresh)
    onset_index = None
    for i in range(len(movement_flags) - int(min_duration * fs / 50)):
        if np.all(movement_flags[i:i + int(min_duration * fs / 50)]):
            onset_index = i
            break
    return onset_index if onset_index is not None else None

def bw_filter(data, fsamp, N, fc, btype, output="ba"):
    """
    Apply a zero-phase Butterworth filter to a 1-D signal.

    Parameters
    ----------
    data : ndarray
        1-D input signal array.
    fsamp : float
        Sampling frequency in Hz.
    N : int
        Filter order.
    fc : float
        Cutoff frequency in Hz.
    btype : str
        Filter type (e.g., 'low', 'high', 'bandpass').
    output : str, optional
        Output format for scipy.signal.butter. Default is 'ba'.

    Returns
    -------
    filtered_data : ndarray
        Zero-phase filtered signal of the same shape as input.
    """

    answer = fc
    Fn = fsamp / 2
    Fnrad = 2 * np.pi * Fn
    Fc = 2 * np.pi * answer
    Wn = [Fc / Fnrad]
    # [b, a] = butter(4, Wn, 'low');
    # local_breast = -(filtfilt(b, a, local_breast_raw(:,:)));

    [b, a] = signal.butter(N, Wn=Wn, btype=btype, output=output)
    filtered_data = signal.filtfilt(b=b, a=a, x=data)

    return filtered_data