import numpy as np


def movement_onset(yd, constant, etype):
    """
    Extracts movement onset based on the average and standard deviation of a sliding window
    Standard thresholds for running are mean_thresh=1.2, std_thresh=0.2. For walking mean_thresh=0.6, std_thresh=0.2.

    yd: 1d array of the vector
    constants: [sample_frequency, mean_thresh, std_thresh]
    """
    acc_mag = yd.copy()

    # ----extract the constants----
    fs = constant[0]
    mean_thresh = constant[1]
    std_thresh = constant[2]

    # ----sliding window features----
    features = []
    timestamps = []
    window_size = 2 * fs  # windows van 2 seconds
    step_size = 1 * fs  # with an overlap of 1 seconds
    min_duration = 3 # minimal duration in sec that the thresholds needs to be surpassed

    for start in range(0, len(acc_mag) - window_size, step_size):
        segment = acc_mag[start:start + window_size]
        mean_val = segment.mean()
        std_val = segment.std()
        # entropy = -np.sum((segment / np.sum(segment)) * np.log2(segment / np.sum(segment) + 1e-12))
        timestamps.append(start)
        features.append((mean_val, std_val))

    features = np.array(features)
    timestamps = np.array(timestamps)
    index = None
    # ----Check already moving else find start----
    initial_window = features[:5]  # First few seconds
    if np.all(initial_window[:, 0] > mean_thresh) and np.all(initial_window[:, 1] > std_thresh):
        print("already moving")
        if etype == 'movement_offset':
            index = 0
    else:
        movement_flags = (features[:, 0] > mean_thresh) & (features[:, 1] > std_thresh)
        for i in range(len(movement_flags) - int(min_duration * fs / 50)):
            if np.all(movement_flags[i:i + int(min_duration * fs / 50)]):
                index = i
                break

    if etype == 'movement_offset':
        index = len(yd) - index

    return timestamps[index] if index is not None else timestamps[0]
