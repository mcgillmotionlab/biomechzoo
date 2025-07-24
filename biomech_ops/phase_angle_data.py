from phase_angle_line import phase_angle_line

def phase_angle_data(data, channels):
    """ compute phase angle using Hilbert Transform"""
    data_new = data.copy()
    for ch in channels:
        r = data[ch]['line']
        phase_angle = phase_angle_line(r)
        data_new[ch +'_phase_angle']['line'] = phase_angle
    return data_new
