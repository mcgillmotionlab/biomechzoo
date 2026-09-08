import numpy as np
import statsmodels.tsa.stattools as stattools
import scipy.signal as signal

def step_symmetry(ch_line, freq, direction=None):
    seconds = len(ch_line) / freq
    autocorr = SignalUtils.compute_autocorrelation(ch_line, freq, duration_sec=int(seconds))

    if direction == "ml":
        peaks, properties = signal.find_peaks(-autocorr, distance=15, height=0)
    else:
        peaks, properties = signal.find_peaks(autocorr, distance=15, height=0)

    try:
        d_1 = peaks[0]
        ad_1 = properties["peak_heights"][0]
        # d_2 = peaks[1]
        # ad_2 = properties["peak_heights"][1]

        if d_1 < 30:
            d_1 = peaks[1]
            ad_1 = properties["peak_heights"][1]
            # d_2 = peaks[2]
            # ad_2 = properties["peak_heights"][2]

    except IndexError:
        d_1 = np.nan
        ad_1 = np.nan
        # d_2 = np.nan
        # ad_2 = np.nan

    return [d_1, ad_1]


class SignalUtils:
    @staticmethod
    def compute_autocorrelation(data, sample_rate, duration_sec=3):
        lags = sample_rate * duration_sec
        autocorr = stattools.acf(data, nlags=lags, fft=True)
        return autocorr