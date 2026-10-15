import statsmodels.tsa.stattools as stattools


def compute_autocorrelation(data, sample_rate, duration_sec=3):
    """Compute the autocorrelation for a fixed-duration window."""
    lags = int(sample_rate * duration_sec)
    return stattools.acf(data, nlags=lags, fft=True)
