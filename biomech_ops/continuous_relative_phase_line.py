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


