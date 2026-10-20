import scipy
import statsmodels.tsa.stattools as stattools
from typing import Dict
import numpy as np

from .signal_inputs import three_axis_signal

# some hardcoded variables
# deductively chosen to extract only the relevant and dominant peaks.
MIN_DISTANCE = 30
MIN_HEIGHT = 0.10


def symmetry(data: Dict, ch: str|list[str]):
    """
    This function determines the time delay and level of correlation of a given signal using the autocorrelation coefficient

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    ch : str or list[str]
        channel names for the analysis. Usually three acceleration directions

    Returns
    -------
    d_1: the time delay of the first dominant peak of the autocorrelation signal.
    ad_1: the strength of the correlation of the first dominant peak.
    d_2: time delay of the second dominant peak of the autocorrelation signal
    ad_2: strength of the correlation of the second dominant peak
    autocorr: the autocorrelation signal from the zero phase to signal length.
    """

    signal, _ = three_axis_signal(data, ch)
    norm = np.linalg.norm(signal, axis=1)
    _lags = len(norm)
    autocorr = stattools.acf(norm, nlags=_lags)
    peaks_auto, peak_properties = scipy.signal.find_peaks(autocorr, distance=MIN_DISTANCE, height=MIN_HEIGHT)

    try:
        d_1 = peaks_auto[0]
        ad_1 = peak_properties["peak_heights"][0]
        d_2 = peaks_auto[1]
        ad_2 = peak_properties["peak_heights"][1]
    except IndexError:
        d_1 = -999
        ad_1 = -999
        d_2 = -999
        ad_2 = -999
    else:
        if d_1 < 30:
            d_1 = peaks_auto[1]
            ad_1 = peak_properties["peak_heights"][1]
            d_2 = peaks_auto[2]
            ad_2 = peak_properties["peak_heights"][2]

    return d_1, ad_1, d_2, ad_2, autocorr

