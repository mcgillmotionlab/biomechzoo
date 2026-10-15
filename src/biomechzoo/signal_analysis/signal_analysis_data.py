import copy
from typing import Dict

import numpy as np

from .compute_entropy import sample_entropy
from .compute_impact import impact_peak, loading_rate
from .compute_smoothness import log_dimensionless_jerk_imu
from .compute_rms import rms_ratio_analysis
from .symmetry import symmetry
from .LyE import LyE_R
from biomechzoo.processing.addchannel_data import addchannel_data


def signal_analysis_data(
        data: Dict, channels: str | list[str], etype: str, ename: str, constant: list = None, save_channel: bool = None
) -> Dict:

    """
    This collection of functions operates on channels to calculate linear and non-linear signal metrics.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    channels : str or list[str]
        For impact-peak and loading-rate analyses, one or more names of 1D channels can be used. If more than one,
         the calculation is repeated independently for each channel. For other analyses, either three names of 1D
         channels or one name of a channel containing a ``(samples, 3)`` array.
    etype : str
        Name of the function to call.
        Options include: 'impact_peak', 'loading_rate', 'ldlj', 'lyapanov_short', 'lyapanov_long', 'sample_entropy',
        'rmsr', 'step_symmetry', and 'stride_symmetry'.
    ename : str
        Event name for saving purposes.
    constant : list, default=None
        Any type of constants needed for a specific analysis. Used for loading-rate analysis to specify the pre-peak
        window.
    save_channel : str, default=None
        Name of the channel to save the data to. If None, the first channel in ``channels`` is used.


    Returns
    -------
    data_new : dict
        A zoo type dictionary containing the added data and events

    Raises
    ------
    ValueError

    """

    data_new = copy.deepcopy(data)
    if isinstance(channels, str):
        channels = [channels]
    else:
        channels = list(channels)
    if not channels:
        raise ValueError("At least one channel must be specified.")

    freq = data["zoosystem"]["Video"]["Freq"]
    etype = etype.lower()

    if etype in {"impact_peak", "loading_rate"}:
        for channel in channels:
            signal = np.asarray(data_new[channel]["line"])
            if signal.ndim != 1:
                raise ValueError(
                    '{0} requires a 1D signal; channel {1!r} is not 1D.'.format(etype, channel)
                )
            if etype == "impact_peak":
                exd, eyd = impact_peak(ch_line=signal, freq=freq)
            else:
                exd, eyd = loading_rate(ch_line=signal, freq=freq, pre_peak_window=constant)

            if isinstance(exd, list):
                for i, ex in enumerate(exd):
                    name = '{0}_{1}'.format(ename, i + 1)
                    data_new[channel]["event"][name] = [int(ex), eyd[i], 0]
            else:
                data_new[channel]["event"][ename] = [exd, eyd, 0]
        return data_new

    channel = save_channel if save_channel is not None else channels[0]
    if etype == "ldlj":
        eyd = log_dimensionless_jerk_imu(data=data_new, ch=channels)
    elif etype == "lyapanov_short":
        exponents, _ = LyE_R(data=data_new, ch=channels)
        eyd = exponents[0]
    elif etype == "lyapanov_long":
        exponents, _ = LyE_R(data=data_new, ch=channels)
        eyd = exponents[1]
    elif etype == "sample_entropy":
        sampen_values, _ = sample_entropy(data=data_new, ch=channels)
        eyd = sampen_values[-1]
    elif etype == "rmsr":
        eyd = rms_ratio_analysis(data=data_new, ch=channels)
    elif etype in {"step_symmetry", "stride_symmetry"}:
        d_1, _, d_2, _, autocorr = symmetry(data=data_new, ch=channels)
        eyd = d_1 if etype == "step_symmetry" else d_2
        data_new = addchannel_data(
            data_new,
            ch_new_name='{0}_autocorr'.format(ename),
            ch_new_data=autocorr,
        )
    else:
        raise ValueError('Unknown event type: {0}'.format(etype))

    if isinstance(eyd, dict):
        for result_channel, value in eyd.items():
            data_new[result_channel]["event"][ename] = [0, value, 0]
    else:
        data_new[channel]["event"][ename] = [0, eyd, 0]

    return data_new

if __name__ == '__main__':
    import os
    from biomechzoo.conversion.table2zoo_data import table2zoo_data
    # load a sample zoo file
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fl = os.path.join(project_root, 'data', 'csv', 'manheim', 'subject_1_acc_running_waist.csv')
    data = table2zoo_data(fl, extension='csv', freq=50)

    # Impact and loading-rate analyses operate on individual 1D channels.
    data = signal_analysis_data(data, channels=['attr_x'], etype='impact_peak', ename='impact_peak')
    data = signal_analysis_data(data, channels=['attr_x'], etype='loading_rate', ename='loading_rate')

    # These analyses accept either three 1D channels or one Nx3 channel.
    data = signal_analysis_data(data, channels=['attr_x', 'attr_y', 'attr_z'], etype='ldlj', ename='ldlj')
    data = signal_analysis_data(data, channels=['attr_x', 'attr_y', 'attr_z'], etype='sample_entropy', ename='sample_entropy')
    data = signal_analysis_data(data, channels=['attr_x', 'attr_y', 'attr_z'], etype='rmsr', ename='rmsr')
