import numpy as np
from scipy.signal import hilbert
from numpy import rad2deg

def phase_angle_line(r):
    """
    Computes the phase angle for a single kinematic waveform using the Hilbert transform method.

    Parameters:
    r : array_like
        1D array of kinematic data (e.g., joint or segment angle)

    Returns:
    PA_data : ndarray
        1D array of phase angle (in degrees) computed from input using the Hilbert transform.

    Reference:
    Lamb and Stöckl (2014). "On the use of continuous relative phase..."
    Clinical Biomechanics. https://doi.org/10.1016/j.clinbiomech.2014.03.008
    """

    # Step 1: Center the data around zero as per Lamb and Stöckl eq. 11
    #cdata = r - np.min(r) - (np.max(r) - np.min(r)) / 2
    r = np.asarray(r)
    cdata = r - np.mean(r)
    # Step 2: Hilbert transform
    X = hilbert(cdata)

    # Step 3: Phase angle calculation
    PA = np.rad2deg(np.arctan2(np.imag(X), np.real(X)))

    #phase_percent = 100 * (PA_data - PA_data[0]) / (PA_data[-1] - PA_data[0])

    return PA