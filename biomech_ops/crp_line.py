def crp_line(dist, prox):
    """ kai's crp code"""
    """ This function determines the CRP on a 0-180 scale, correcting for
       discontinuity in the signals >180.
       """
    temp_CRP = abs(dist - prox)
    idx = temp_CRP > 180  # This corrects discontinuity in the data and puts everything on a 0-180 scale.
    temp_CRP[idx] = 360 - temp_CRP[idx]
    crp = temp_CRP
    return crp


