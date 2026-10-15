import numpy as np

from .signal_inputs import three_axis_signal


def rms_ratio_analysis(data, ch):
    signal, channels = three_axis_signal(data, ch)
    rms = np.sqrt(np.mean(signal**2, axis=0))
    ratios = rms / np.linalg.norm(rms)

    if len(channels) == 1:
        return {channels[0]: ratios.tolist()}
    return {channel: ratio for channel, ratio in zip(channels, ratios)}


def root_mean_square(ndata):
    # type check
    if not isinstance(ndata, np.ndarray):
        ndata = np.array(ndata)

    rms = np.sqrt(np.mean(ndata**2))

    return rms
