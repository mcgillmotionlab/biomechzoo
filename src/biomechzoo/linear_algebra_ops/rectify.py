import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data

def compute_magnitude_line(x,y,z):
    magnitude = np.sqrt((x**2) + (y**2) + (z **2))
    return magnitude

def rectify_data(data, chs):
    """
    Take absolute value of channels
    """
    if type(chs) is str:
        chs = [chs]

    # extract channels from data
    for ch in chs:
        yd = data[ch]['line']
        yd_abs = rectify_line(yd)
        data = addchannel_data(data, ch_new_data=yd_abs, ch_new_name=ch + '_rectified')
    return data

def rectify_line(yd):
    return np.abs(yd)


