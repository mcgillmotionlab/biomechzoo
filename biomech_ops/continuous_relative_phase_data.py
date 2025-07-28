from biomech_ops.continuous_relative_phase_line import continuous_relative_phase_line
from processing.add_channel_data import add_channel_data


def continuous_relative_phase_data(data, ch_dist, ch_prox):
    data_new = data.copy()
    prox = data[ch_prox]['line']
    dist = data[ch_dist]['line']
    crp = continuous_relative_phase_line(dist, prox)
    data_new = add_channel_data(data_new, ch_new_name=ch_dist + '_' + ch_prox + '_' + 'crp', ch_new_data=crp)
    return data_new


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from utils.zload import zload
    from utils.zplot import zplot
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC032A18_exploded.zoo')
    data = zload(fl)
    data = data['data']
    data = continuous_relative_phase_data(data, ch_dist='RKneeAngles_x', ch_prox='RHipAngles_x')
    zplot(data, 'RKneeAngles_x_RHipAngles_x_crp')
