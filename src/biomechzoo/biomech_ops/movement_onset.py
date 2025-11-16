import numpy as np
import scipy.signal as signal

def movement_onset(yd, fsamp, constants):
    """
    Extracts movement onset based on the average and standard deviation of a sliding window
    Standard thresholds for running are mean_thresh=1.2, std_thresh=0.2. For walking mean_thresh=0.6, std_thresh=0.2.

    yd: 1d array of the vector
    fsamp: sampling frequency
    constants: [mean_thresh, std_thresh]
    etype: 'movement_onset' or 'movement_offset'
    """
    acc_mag = yd.copy()
    acc_mag_filtered = bw_filter(data=acc_mag, N=4, fc=20, btype="low")
    features, timestamps = sliding_window_features(ch_data=acc_mag_filtered, fs=fsamp)

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


def movement_offset(yd, fsamp, constant):
    raise NotImplementedError
    # ----extract the constants----
    fs = constant[0]
    mean_thresh = constant[1]
    std_thresh = constant[2]
    min_thresh = 0.1
    onset_time = None

    # ----Reverse, filter and extract features from the signa;----
    acc_mag = yd.copy()
    acc_mag = acc_mag[::-1]

    acc_mag_filtered = bw_filter(data=acc_mag, N=4, fc=20, btype="low", fsamp=fsamp)
    features, timestamps = sliding_window_features(ch_data=acc_mag_filtered, fs=fsamp)

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
    Basic zero-phase butterworth filter.
    :param data: 1xN array
    :param N: filter order
    :param fc: cutoff frequency
    :param btype: filter type
    :return: filtered data 1xN.

    Args:
        output:
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