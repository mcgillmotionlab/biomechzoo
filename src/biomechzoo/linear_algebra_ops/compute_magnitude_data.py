import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.utils.common_substring import common_substring_join

def compute_magnitude_line(x,y,z):
    magnitude = np.sqrt((x**2) + (y**2) + (z **2))
    return magnitude

def compute_magnitude_data(data, ch_x, ch_y, ch_z, ch_new_name=None):
    """
    Compute the magnitude of acceleration data from IMU channels (BiomechZoo format).

    Returns the magnitude
    """
    # extract channels from data
    x = data[ch_x]['line']
    y = data[ch_y]['line']
    z = data[ch_z]['line']

    #calculate the magnitude of the data
    magnitude_data = compute_magnitude_line(x,y,z)

    # get name of new channel:
    if ch_new_name is None:
        ch_new_name = common_substring_join([ch_x, ch_y, ch_z])

    if ch_new_name.startswith("_"):
        ch_new_name = ch_new_name[1:]

    #add channels
    data = addchannel_data(data, ch_new_name=ch_new_name + '_mag', ch_new_data=magnitude_data )

    return data



