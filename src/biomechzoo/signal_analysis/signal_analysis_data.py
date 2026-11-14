import copy
from typing import Dict

import numpy as np

from .compute_impact import impact_peak, loading_rate


def signal_analysis_data(
        data: Dict, channels: str | list[str], etype: str, ename: str
) -> Dict:

    """
    Calculate impact peaks or loading rates on one or more 1D channels.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    channels : str or list[str]
        One or more names of 1D channels. The selected analysis is repeated
        independently for each channel.
    etype : str
        Analysis to perform: ``'impact_peak'`` or ``'loading_rate'``.
    ename : str
        Event name used to store the result. Multiple detected peaks are
        stored with numbered event names.
    Returns
    -------
    data_new : dict
        A copy of the input zoo dictionary with detected results added as
        events.

    Raises
    ------
    ValueError

    """

    pre_peak_window = 20
    distance_ratio = 0.9
    relative_peak_height = 0.25
    autocorrelation_peak_distance = 30
    autocorrelation_duration_sec = 3
    autocorrelation_peak_height = 0
    peak_height = 0

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
                exd, eyd = impact_peak(
                    ch_line=signal,
                    freq=freq,
                    distance_ratio=distance_ratio,
                    relative_peak_height=relative_peak_height,
                    autocorrelation_peak_distance=autocorrelation_peak_distance,
                    autocorrelation_duration_sec=autocorrelation_duration_sec,
                    autocorrelation_peak_height=autocorrelation_peak_height,
                    peak_height=peak_height,
                )
            else:
                exd, eyd = loading_rate(
                    ch_line=signal,
                    freq=freq,
                    pre_peak_window=pre_peak_window,
                    distance_ratio=distance_ratio,
                    relative_peak_height=relative_peak_height,
                    autocorrelation_peak_distance=autocorrelation_peak_distance,
                    autocorrelation_duration_sec=autocorrelation_duration_sec,
                    autocorrelation_peak_height=autocorrelation_peak_height,
                    peak_height=peak_height,
                )

            if isinstance(exd, list):
                for i, ex in enumerate(exd):
                    name = '{0}_{1}'.format(ename, i + 1)
                    data_new[channel]["event"][name] = [int(ex), eyd[i], 0]
            else:
                data_new[channel]["event"][ename] = [exd, eyd, 0]
        return data_new

    raise ValueError('Unknown event type: {0}'.format(etype))
