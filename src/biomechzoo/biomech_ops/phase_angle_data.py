from biomechzoo.biomech_ops.phase_angle_line import phase_angle_line
from biomechzoo.processing.addchannel_data import addchannel_data


def phase_angle_data(data, channels):
    """
    Compute phase angle for one or more channels using the Hilbert transform.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    channels : list of str
        Channel names on which to compute the phase angle.

    Returns
    -------
    dict
        Updated data dictionary with phase angle results appended as new
        channels named '<channel>_phase_angle'.

    Raises
    ------
    ValueError
        If a specified channel is not found in the data dictionary.

    See Also
    --------
    phase_angle_line : Core line-level phase angle computation.
    continuous_relative_phase_data : Compute CRP from phase angle channels.
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

