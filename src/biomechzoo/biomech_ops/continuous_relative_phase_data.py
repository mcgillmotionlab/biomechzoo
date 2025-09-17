from biomechzoo.biomech_ops.continuous_relative_phase_line import continuous_relative_phase_line
from biomechzoo.processing.addchannel_data import addchannel_data


def continuous_relative_phase_data(data, ch_dist, ch_prox):
    """ This function determines the CRP on a 0-180 scale, correcting for
           discontinuity in the signals >180.
    See Also phase_angle_data.py and phase_angle_line.py
    """

    data_new = data.copy()
    prox = data[ch_prox]['line']
    dist = data[ch_dist]['line']
    crp = continuous_relative_phase_line(dist, prox)
    data_new = addchannel_data(data_new, ch_new_name=ch_dist + '_' + ch_prox + '_' + 'crp', ch_new_data=crp)
    return data_new


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload
    from biomechzoo.utils.zplot import zplot
    # note: crp should be computed on phase angle data. Here we just demonstrate that it works.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC032A18_exploded.zoo')
    data = zload(fl)
    data = continuous_relative_phase_data(data, ch_dist='RKneeAngles_x', ch_prox='RHipAngles_x')
    zplot(data, 'RKneeAngles_x_RHipAngles_x_crp')

