import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data
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
        ch_new_name = common_substring_or_concat(ch_x, ch_y, ch_z)

    #add channels
    data = addchannel_data(data, ch_new_name=ch_new_name + '_mag', ch_new_data=magnitude_data )

    return data


def common_substring_or_concat(str1, str2, str3):
    common = ""
    for i in range(len(str1)):
        for j in range(i + 1, len(str1) + 1):
            sub = str1[i:j]
            if sub in str2 and sub in str3 and len(sub) > len(common):
                common = sub

    # If no common substring found, concatenate all three
    if not common:
        return str1 + str2 + str3
    return common

