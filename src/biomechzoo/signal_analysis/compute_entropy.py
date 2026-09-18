import EntropyHub as EH
import statsmodels.tsa.stattools as stattools
import numpy as np



def sample_entropy(ch_line, freq):
    autocorr = SignalUtils.compute_autocorrelation(ch_line, freq)
    tau = SignalUtils.compute_tau_from_autocorr(autocorr)
    sampen_values, _, _ = EH.SampEn(Sig=ch_line, m=2, tau=int(tau), r=None)
    return sampen_values[-1]


class SignalUtils:
    @staticmethod
    def compute_autocorrelation(data, sample_rate, duration_sec=3):
        lags = sample_rate * duration_sec
        autocorr = stattools.acf(data, nlags=lags, fft=True)
        return autocorr

    @staticmethod
    def compute_tau_from_autocorr(autocorr):
        drop_value = 1 / np.exp(1)
        tau = np.argmax(autocorr < drop_value)
        return tau