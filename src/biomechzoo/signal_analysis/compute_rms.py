import numpy as np
import pandas as pd


def rms_ratio_analysis(data, ch):
    rms = []
    for channel in ch:
        ch_data = data[channel]["line"]
        rms.append(root_mean_square(ch_data))

    rms_t = np.linalg.norm(rms)
    rms_ratio_x = rms[0]/rms_t
    rms_ratio_y = rms[1]/rms_t
    rms_ratio_z = rms[2]/rms_t


    return {ch[0]: rms_ratio_x, ch[1]: rms_ratio_y, ch[2]: rms_ratio_z}


def root_mean_square(ndata):
    # type check
    if not isinstance(ndata, np.ndarray):
        ndata = np.array(ndata)

    rms = np.sqrt(np.mean(ndata**2))

    return rms
