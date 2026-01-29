import numpy as np

from biomechzoo.processing.explodechannel_data import explodechannel_data
from biomechzoo.biomech_ops.normalize_line import normalize_line
from biomechzoo.statistics.rmse import rmse
from biomechzoo.processing.removechannel_data import removechannel_data

def reptrial_data(gdata, channels, method='mean'):
    """
    Compute a representative trial from a set of trials for a subject/condition.

    This function can operate in two modes:

    1. 'mean': Computes the pointwise mean of each specified channel across all trials,
                 producing a synthetic representative trial.
    2. 'rmse': Computes the trial whose waveform is closest to the mean in the
                 root-mean-squared error (RMSE) sense, per channel, and returns
                 that trial as the representative.

    Arguments:
        gdata (dict): Dictionary of zoo data. Each key corresponds to a trial
                      (e.g., 'data1', 'data2', ...)
        channels (list or 'all'): List of channel names to include in the representative
                                  trial computation. If 'all', all channels in the
                                  first trial are used.
        method (str): Method to compute the representative trial. Options:
                      - 'mean': default. synthetic trial from pointwise mean
                      - 'rmse': select existing trial closest to mean waveform

    Returns:
        rep (dict): Representative trial, in the same format as a single trial in `gdata`.
        file_index (int or str): Index of the selected trial in `gdata` for 'rmse',
                                 or 'mean' if method='mean'.

    Notes:
       - events are not handled here. Rather, the user could run event detection for the representative trial
    """
    nlength = 101
    trials = list(gdata.keys())

    # in case upper case RMSE
    method = method.lower()

    # determine channels
    if channels == 'all':
        channels = [ch for ch in gdata[trials[0]].keys()
                    if ch != 'zoosystem']

    # explode any n x 3 channels
    # todo: test this functionality
    exploded = []
    for ch in list(channels):
        data = gdata[trials[0]][ch]['line']
        if data.ndim == 2 and data.shape[1] == 3:
            for t in trials:
                gdata[t] = explodechannel_data(gdata[t], ch)
            channels.remove(ch)
            channels.extend([ch+'_x', ch+'_y', ch+'_z'])
            exploded.append(ch)

    if method == 'mean':

        rep = gdata[trials[0]]

        for ch in channels:
            stk = []
            for t in trials:
                stk.append(normalize_line(gdata[t][ch]['line'], nlength))
            rep[ch]['line'] = np.mean(np.vstack(stk), axis=0)

        file_index = 'mean'

    elif method == 'rmse':
        rms_stack = np.zeros((len(trials), len(channels)))

        for i, ch in enumerate(channels):
            stk = []
            for t in trials:
                stk.append(normalize_line(gdata[t][ch]['line'], nlength))
            stk = np.vstack(stk)

            mean_val = np.mean(stk, axis=0)
            if np.isnan(mean_val).any():
                raise ValueError('NaNs found in channel {}'.format(ch))

            for j in range(len(trials)):
                rms_stack[j, i] = rmse(mean_val, stk[j, :])

        RMSvals = np.mean(rms_stack, axis=1)
        file_index = int(np.argmin(RMSvals))

        rep = gdata[trials[file_index]]
    else:
        raise ValueError('Unknown method {}, choose mean or rmse'.format(method))

    # collapse exploded channels
    for ch in exploded:
        rep = removechannel_data(rep, [ch+'_x', ch+'_y', ch+'_z'])

    # metadata
    rep['zoosystem']['CompInfo']['Reptrials'] = {
        'Trials': len(trials),
        'Method': method
    }

    return rep, file_index


if __name__ == "__main__":
    from biomechzoo.utils.set_zoosystem import set_zoosystem
    # synthetic zoo-like data
    np.random.seed(0)
    gdata = {}
    n_samples = 50
    n_trials = 5
    channels = ['HipFlexion', 'KneeAngle']

    for t in range(n_trials):
        trial_name = f"data{t+1}"
        gdata[trial_name] = {}
        for ch in channels:
            # synthetic waveform with slight random variation
            base = np.linspace(0, 30, n_samples)
            gdata[trial_name][ch] = {'line': base + np.random.randn(n_samples),
                                     'event': {}}
        gdata[trial_name]['zoosystem'] = set_zoosystem()

    # Test mean method
    # rep_mean, idx_mean = reptrial_data(gdata, channels=channels, method='mean')

    # Test rmse method
    rep_rmse, idx_rmse = reptrial_data(gdata, channels=channels, method='rmse')
