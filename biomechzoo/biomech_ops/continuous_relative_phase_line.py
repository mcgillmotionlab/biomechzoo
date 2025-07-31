def continuous_relative_phase_line(dist, prox):
    """ This function determines the CRP on a 0-180 scale, correcting for
       discontinuity in the signals >180.

    Arguments
    dist, ndarray: data of distal segment or joint
    prox, ndarray: data of proximal segment or joibt

    Returns
    crp, ndarray: continous relative phase betweeen dist and prox data
    """
    temp_CRP = abs(dist - prox)
    idx = temp_CRP > 180  # This corrects discontinuity in the data and puts everything on a 0-180 scale.
    temp_CRP[idx] = 360 - temp_CRP[idx]
    crp = temp_CRP
    return crp


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload
    from biomechzoo.biomech_ops.phase_angle_line import phase_angle_line
    from matplotlib import pyplot as plt
    # note: crp should be computed on phase angle data. Here we just demonstrate that it works.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC032A18_exploded.zoo')
    data = zload(fl)
    knee = data['RKneeAngles_x']['line']
    hip = data['RHipAngles_x']['line']
    knee_pa = phase_angle_line(knee)
    hip_pa = phase_angle_line(hip)
    crp = continuous_relative_phase_line(knee_pa, hip_pa)
    plt.plot(crp)
    plt.show()
