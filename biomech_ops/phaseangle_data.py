from phaseangle_line import phaseangle_line

def phaseangle_data(data, channels):
    """ compute phase angle using Hilbert Transform"""
    data_new = data.copy()
    for ch in channels:
        r = data[ch]['line']
        phase_angle = phaseangle_line(r)
        data_new[ch+'_phaseangle']['line'] = phase_angle
    return data_new
