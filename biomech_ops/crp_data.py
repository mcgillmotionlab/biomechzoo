from crp_line import crp_line

def crp_data(data, ch_prox, ch_dist):
    data_new = data.copy()
    prox = data[ch_prox]['line']
    dist = data[ch_dist]['line']
    crp = crp_line(dist, prox)
    data_new[ch_dist + '_' + ch_prox + '_' + 'crp']['line'] = crp
    return data_new