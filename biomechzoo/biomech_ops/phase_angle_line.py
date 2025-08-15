import numpy as np
from scipy.signal import hilbert


def phase_angle_line(r):
    """
    Computes the phase angle for a single kinematic waveform using the Hilbert transform method.

    Parameters:
    r : array_like
        (n, 1) array of kinematic data (e.g., joint or segment angle)

    Returns:
    PA_data : ndarray
        1D array of phase angle (in degrees) computed from input using the Hilbert transform.

    Reference:
    Lamb and Stöckl (2014). "On the use of continuous relative phase..."
    Clinical Biomechanics. https://doi.org/10.1016/j.clinbiomech.2014.03.008
    """

    # Step 1: Center the data around zero as per Lamb and Stöckl eq. 11
    cdata = r - np.min(r) - (np.max(r) - np.min(r)) / 2

    # Step 2: Hilbert transform
    X = hilbert(cdata)

    # Step 3: Phase angle calculation
    PA = np.rad2deg(np.arctan2(np.imag(X), np.real(X)))

    return PA


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload
    from matplotlib import pyplot as plt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC032A18_exploded.zoo')
    data = zload(fl)
    print(data)
    r = data['RKneeAngles_x']['line']
    phase_angle = phase_angle_line(r)
    plt.plot(phase_angle)
    plt.show()

