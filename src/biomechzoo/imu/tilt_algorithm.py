import numpy as np
import math
import pandas as pd
from biomechzoo.processing.addchannel_data import addchannel_data

def tilt_algorithm_data(data,ch_vert, ch_medlat, ch_antpost, plot_or_not=None):

    # extract channels from data
    avert = data[ch_vert]['line']
    amedlat = data[ch_medlat]['line']
    aantpost = data[ch_antpost]['line']

    _, avert_corr, amedlat_corr, aantpost_corr = tilt_algorithm_line(avert, amedlat, aantpost)

    data = addchannel_data(data, ch_vert + '_tilt_corr', avert_corr)
    data = addchannel_data(data, ch_medlat + '_tilt_corr', amedlat_corr)
    data = addchannel_data(data, ch_antpost + '_tilt_corr', aantpost_corr)

    return data


def tilt_algorithm_line(avert, amedlat, aantpost):
    """
    TiltAlgorithm - to account for gravity and improper tilt alignment of a tri-axial trunk accelerometer.

    Step 1: Extract raw measured (mean) accelerations
    Step 2: Calculate tilt angles
    Step 3: Calculate horizontal dynamic accelerations vectors
    Step 4: Calculate estimated provisional vertical vector
    Step 5: Calculate vertical dynamic vector
    step 6.1:  Calculate the contribution of static components
    step 6.2 Transpose static component matrices
    step 7: Remove the static components from the templates of pre and post

    Parameters
    ----------
    avert : 1D-array
        data predominantly in vertical direction. Expressed in g's
    amedlat : 1D-array:
        data predominantly in medio-lateral direction. Expressed in g's
    aantpost : 1D-array
        data predominantly in anterior-posterior direction. Expressed in g's
    Returns
    -------
    df_corrected : Nx3 DataFrame
        the tilt corrected and gravity subtracted vertical, medio-lateral and anterior-posterior
        acceleration signals
    avert2: 1D-array
        the tilt corrected acceleration data in vertical direction
    amedlat2 : 1D-array
        the tilt corrected acceleration data in medio-lateral direction
    aantpost2: 1D-array
        the tilt corrected acceleration data in anterior-posterior direction
    Notes
    -----
    -  If average acceleration is above 5m/s^2, the signal will be corrected.

    """

    a_vt = avert.mean()
    a_ml = amedlat.mean()
    a_ap = aantpost.mean()

    # if average vertical acceleration is more than 5, data is expressed in m/s^2
    # Update signals to G's
    if a_vt > 5:
        avert /= 9.81
        amedlat /= 9.81
        aantpost /= 9.81

        a_vt = avert.mean()
        a_ml = amedlat.mean()
        a_ap = aantpost.mean()



    # if avert is negative than turn the sensor around.
    if a_vt < 0.5:
        avert *= -1
        amedlat *= -1
        a_vt = avert.mean()
        a_ml = amedlat.mean()

    # Anterior tilt
    TiltAngle_ap_rad = np.arcsin(a_ap)
    TiltAngle_ap_deg = math.degrees(TiltAngle_ap_rad)

    # mediolateral tilt
    TiltAngle_ml_rad = np.arcsin(a_ml)
    TiltAngle_ml_deg = math.degrees(TiltAngle_ml_rad)

    # Anterior posterior
    a_AP = (a_ap * np.cos(TiltAngle_ap_rad)) - (a_vt * np.sin(TiltAngle_ap_rad))
    # AMediolateral
    a_ML = (a_ml * np.cos(TiltAngle_ml_rad)) - (a_vt * np.sin(TiltAngle_ml_rad))

    # a_vt_prov = a_ap*Sin(theta_ap) + a_vt*Cos(theta_ap)
    a_vt_prov = (a_ap * np.sin(TiltAngle_ap_rad)) + (a_vt * np.cos(TiltAngle_ap_rad))

    # a_VT = a_ml*sin(theta_ml) + a_vt_prov*cos(theta_ml) - 1
    a_VT = (a_ml * np.sin(TiltAngle_ml_rad)) + (a_vt_prov * np.cos(TiltAngle_ml_rad)) - 1

    a_AP_static = a_ap - a_AP
    a_ML_static = a_ml - a_ML
    a_VT_static = a_vt - a_VT

    a_AP_static = np.transpose(a_AP_static)
    a_ML_static = np.transpose(a_ML_static)
    a_VT_static = np.transpose(a_VT_static)

    amedlat2 = amedlat - a_ML_static
    avert2 = avert - a_VT_static
    aantpost2 = aantpost - a_AP_static

    data = {'avert': avert2,
            'amedlat': amedlat2,
            'aantpost': aantpost2}
    df_corrected = pd.DataFrame(data)

    return df_corrected, avert2, amedlat2, aantpost2