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


def tilt_algorithm_line(avert, amedlat, aantpost, plot_or_not=None):
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

    :param avert: signal predominantly in vertical direction
    :param amedlat: signal predominantly in medio-lateral direction
    :param aantpost: signal predominantly in anterior-posterior direction
    :param plot_or_not: whether to plot the results
    :return: dataframe of the tilt corrected and gravity subtracted vertical, medio-lateral and anterior-posterior
    acceleration signals
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

    # if plot_or_not:
    #     f, ax = plt.subplots(nrows=3, ncols=1, sharex=True, dpi=300)
    #     sns.despine(offset=10)
    #     f.tight_layout()
    #     offset = 0.1
    #     f.subplots_adjust(left=0.15, top=0.95)
    #
    #     sns.lineplot(avert, ax=ax[0], label='Raw')
    #     sns.lineplot(avert2, ax=ax[0], label='tilt corrected')
    #     ax[0].set_ylabel('vert acc (g)')
    #     ax[0].set_title('Vertical acceleration corrected with {}'.format(np.round(a_VT_static, 2)))
    #
    #     sns.lineplot(amedlat, ax=ax[1], label='Raw')
    #     sns.lineplot(amedlat2, ax=ax[1], label='Tilt corrected')
    #     ax[1].set_ylabel('ml acc (g)')
    #     ax[1].set_title('Medio-lateral tilt angle corrected with {} degrees'.format(np.round(TiltAngle_ml_deg, 2)))
    #
    #     sns.lineplot(aantpost, ax=ax[2], label='Raw')
    #     sns.lineplot(aantpost2, ax=ax[2], label='Tilt corrected')
    #     ax[2].set_ylabel('ap acc (g)')
    #     ax[2].set_title('Anterior-posterior tilt angle corrected with {} degrees'.format(np.round(TiltAngle_ap_deg, 2)))

    return df_corrected, avert2, amedlat2, aantpost2