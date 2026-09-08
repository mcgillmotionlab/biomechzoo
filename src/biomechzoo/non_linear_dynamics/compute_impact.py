import numpy as np
import statsmodels.tsa.stattools as stattools
import scipy.signal as signal


def impact_peak(ch_line, freq):
    peaks_idx, peaks_properties = peak_impacts(ch_line, freq)
    temp_heights = peaks_properties['peak_heights']
    mask = np.where(temp_heights > 0.25 * np.mean(temp_heights))
    eyd = temp_heights[mask]
    exd = peaks_idx[mask]

    return exd.tolist(), eyd.tolist()


def loading_rate(ch_line, freq, pre_peak_window=20):
    peaks_idx, peaks_properties = peak_impacts(ch_line, freq)
    temp_heights = peaks_properties['peak_heights']
    mask = np.where(temp_heights > 0.25 * np.mean(temp_heights))
    peaks_idx = peaks_idx[mask]
    temp_heights = temp_heights[mask]
    eyd = []
    exd = []
    if len(peaks_idx) == 0:
        return [None, None]
    else:
        loading_rate = np.diff(ch_line)
        for p in peaks_idx:
            if p < 20:
                start_index = 0
            else:
                start_index = p - pre_peak_window
            pre_peak_segment = loading_rate[start_index:p]
            eyd.append(np.max(pre_peak_segment))

            exd.append(np.argmax(pre_peak_segment) + start_index)

    return exd, eyd


def peak_impacts(data, freq):
    min_distance = compute_distance(data, 0.9, freq)
    peaks, properties = signal.find_peaks(data, distance=min_distance, height=0)
    return peaks, properties

def compute_distance(data, distance_ratio, freq):
    autocorr = SignalUtils.compute_autocorrelation(data, freq)
    peaks, properties = signal.find_peaks(autocorr, distance=30, height=0)
    d_1 = peaks[0]
    if d_1 < 30:
        d_1 = peaks[1]

    return round(d_1 * distance_ratio)



class SignalUtils:
    @staticmethod
    def compute_autocorrelation(data, sample_rate, duration_sec=3):
        lags = sample_rate * duration_sec
        autocorr = stattools.acf(data, nlags=lags, fft=True)
        return autocorr

