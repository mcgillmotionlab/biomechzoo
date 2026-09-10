import copy

from compute_entropy import sample_entropy
from compute_impact import impact_peak, loading_rate
from compute_smoothness import log_dimensionless_jerk_imu
from compute_rms import rms_ratio_analysis
def signal_analysis_data(data, channels, etype, ename, single_channel, constant=None, save_channel=None):

    """
    This collection of functions operates on predetermined channels to calculate the parameter of preference on the given channel.

    Currently implemented for single channel analysis: impact peak, loading rate, sample entropy;
    Currently implemented for multichannel analysis: LDLJ, RMS ratio.

    Parameters
    ----------
    data : dict
        zoo type dictionary
    channels : str or list[str]
        channel names for the analysis
    etype : str
        Name of the function to call
    ename : str
        Event name of saving purposes.
    single_channel : bool
        if False, the analysis needs multiple channels to work.
    constant : list, default=None
        Any type of constants needed for the specific analysis.
    save_channel : str, default=None
        Name of the channel to save the data to. Useful if the analysis needs multiple channels.


    Returns
    -------
    data_new : dict
        A zoo type dictionary containing the added data

    Raises
    ------
    ValueError

    """

    data_new = copy.deepcopy(data)

    freq = data["zoosystem"]["Video"]["Freq"]

    # single channel analysis i.e. analysis only requires a single channel to compute.
    if single_channel:
        for channel in channels:
            yd = data_new[channel]['line']
            etype = etype.lower()

            if etype == 'impact_peak':
                exd, eyd = impact_peak(ch_line=yd, freq=freq)
            elif etype == 'loading_rate':
                exd, eyd = loading_rate(ch_line=yd, freq=freq, pre_peak_window=20)
            elif etype == 'sample_entropy':
                eyd = sample_entropy(ch_line=yd, freq=freq)
                exd = 0
            elif etype =="step_symmetry":
                NotImplementedError()
            elif etype == 'stride_symmetry':
                NotImplementedError()
            elif etype=="rms":
                NotImplementedError()
            else:
                raise ValueError(f'Unknown event type: {etype}')


            # Add event to the channel's event dict
            if isinstance(exd, list):
                for i, ex in enumerate(exd):
                    name = ename + '_' + str(i + 1)
                    data_new[channel]['event'][name] = [int(ex), eyd[i], 0]
            else:
                data_new[channel]['event'][ename] = [exd, eyd, 0]

    # Multiple channel analysis i.e. multiple channels are needed for the analysis.
    else:
        if save_channel is not None:
            channel = save_channel
        else:
            channel = channels[0]

        etype = etype.lower()

        if etype == 'ldlj':
            eyd = log_dimensionless_jerk_imu(data=data_new, ch=channels, event=constant)
            exd = 0
        elif etype == "rmsr":
            eyd = rms_ratio_analysis(data=data_new, ch=channels)
            exd = 0

        # Add event to the channel's event dict
        if isinstance(eyd, dict):
            for channel, ey in eyd.items():
                data_new[channel]['event'][ename] = [0, ey, 0]
        else:
            data_new[channel]['event'][ename] = [exd, eyd, 0]

    return data_new

if __name__ == '__main__':
    import os
    from biomechzoo.conversion.table2zoo_data import table2zoo_data
    # load a sample zoo file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fl = os.path.join(project_root, 'data', 'csv', 'manheim', 'subject_1_acc_running_waist.csv')
    data = table2zoo_data(fl, extension='csv', freq=50)

    # conduct signal analysis on single channels
    data = signal_analysis_data(data, channels=['attr_x'], single_channel=True, etype='impact_peak', ename='impact_peak')
    data = signal_analysis_data(data, channels=['attr_x'], single_channel=True, etype='loading_rate', ename='loading_rate')
    data = signal_analysis_data(data, channels=['attr_x'], single_channel=True, etype='sample_entropy', ename='sample_entropy')

    # conduction signal analysis of multiple (3D channels required)
    data = signal_analysis_data(data, channels=['attr_x', 'attr_y', 'attr_z'], single_channel=False, etype='ldlj', ename='ldlj')
    data = signal_analysis_data(data, channels=['attr_x', 'attr_y', 'attr_z'], single_channel=False, etype='rmsr', ename='rmsr')
