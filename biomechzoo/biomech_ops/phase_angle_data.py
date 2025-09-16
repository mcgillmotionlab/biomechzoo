from biomechzoo.biomech_ops.phase_angle_line import phase_angle_line
from biomechzoo.processing.addchannel_data import addchannel_data


def phase_angle_data(data, channels):
    """Compute phase angle using Hilbert Transform.
    Arguments
        data: dict, zoo data to operate on
        channels, list. Channel names on which to apply calculations
    Returns:
        data: dict, zoo data with calculations appended to new channel(s)
    """
    data_new = data.copy()
    for ch in channels:
        if ch not in data_new:
            raise ValueError('Channel {} not in data. Available keys: {}'.format(ch, list(data_new.keys())))
        r = data_new[ch]['line']
        phase_angle = phase_angle_line(r)
        ch_new = ch + '_phase_angle'
        data_new = addchannel_data(data_new, ch_new_name=ch_new, ch_new_data=phase_angle)
    return data_new


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload
    from biomechzoo.utils.zplot import zplot
    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC032A18_exploded.zoo')

    # load  zoo file
    data = zload(fl)
    data = data['data']
    data = phase_angle_data(data, channels=['RKneeAngles_x', 'RHipAngles_x'])
    zplot(data, 'RKneeAngles_x_phase_angle')

