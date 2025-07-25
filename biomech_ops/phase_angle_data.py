from biomech_ops.phase_angle_line import phase_angle_line
from utils.add_channel_data import add_channel_data

def phase_angle_data(data, channels):
    """Compute phase angle using Hilbert Transform."""
    data_new = data.copy()
    for ch in channels:
        if ch not in data_new:
            raise ValueError(f'Channel "{ch}" not in data. Available keys: {list(data_new.keys())}')
        r = data_new[ch]['line']
        phase_angle = phase_angle_line(r)
        ch_new = ch + '_phase_angle'
        data_new = add_channel_data(data_new, ch=ch_new, ndata=phase_angle)
    return data_new


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from utils.zload import zload
    from utils.zplot import zplot
    from processing.explodechannel_data import explodechannel_data
    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    data = data['data']
    data = explodechannel_data(data)
    ch = ['RKneeAngles_x']
    data=phase_angle_data(data, ch)
    zplot(data, 'RKneeAngles_x_phase_angle')

