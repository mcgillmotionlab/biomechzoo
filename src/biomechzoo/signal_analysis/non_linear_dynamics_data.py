import copy
from typing import Dict

from .compute_entropy import sample_entropy
from .compute_smoothness import log_dimensionless_jerk_imu
from .symmetry import symmetry
from .LyE import LyE_R
from biomechzoo.processing.addchannel_data import addchannel_data


def non_linear_dynamics_data(
        data: Dict, channels: str | list[str], etype: str, ename: str,
        save_channel: str | None = None
) -> Dict:

    """
    Calculate non-linear gait-dynamic measures of movement predictability, smoothness, symmetry, and local dynamic
    stability and complexity as implemented in Emmerzaal et al.Non-Linear Gait Dynamics Are Affected by Commonly
    Occurring Outdoor Surfaces and Sex in Healthy Adults. Sensors 2025;25:4191. https://doi.org/10.3390/s25134191.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary loaded from a zoo file.
    channels : str or list[str]
        Three names of 1D signal channels, or one name of a channel containing a ``(samples, 3)`` array. In the case of
        the latter, the analyses use the Euclidean norm of this three-axis signal.
    etype : str
        Measure to calculate.
    Supported values are grouped by gait-dynamics construct:

        * Movement predictability: ``'sample_entropy'``. Sample entropy is calculated using the Richman and Moorman
        algorithm [1], with parameters based on Yentes et al. [2] and Govindan et al. [3]. Higher values indicate less
        periodic and less predictable movement.
        * Movement smoothness: ``'ldlj'``. Log dimensionless jerk is calculated using the method of Melendez-Calderon
        et al. [4]. Values closer to zero indicate smoother movement.
        * Movement symmetry:
          ``'step_symmetry'`` uses the first dominant peak in the unbiased
          autocorrelation; ``'stride_symmetry'`` uses the second. The event
          value is the peak height, representing step or stride correlation
          strength; perfect symmetry is one. The full autocorrelation is also
          added as a channel named ``{ename}_autocorr``; peak positions in that
          channel represent the corresponding phase shifts.
        * Local dynamic stability and complexity: ``'lyapanov_short'`` and ``'lyapanov_long'``. These return the short-
         and long-term maximum Lyapunov exponents (LyEs and LyEl), estimated from reconstructed state spaces using
         average mutual information and false nearest neighbors [5, 6], followed by Rosenstein's divergence method [7].
         The short-term slope is fitted over the first half of a signal period; the long-term slope is fitted from four
         signal periods to the 10-second analysis window [8]. Higher values indicate lower dynamic stability and greater
          chaos [7, 8].
    ename : str or None
        Event name used to store the result. If None, default to etype
    save_channel : str, default=None
        Channel on which to store the result. If None, the first channel in ``channels`` is used. For symmetry measures,
         the autocorrelation output channel is named using ``ename`` instead.

    Returns
    -------
    data_new : dict
        A copy of the input zoo dictionary with the calculated measure stored as an event and, for symmetry measures,
        the autocorrelation added as a channel.

    Raises
    ------
    ValueError

    Notes
    -----
    References
    [1] Yentes et al. The appropriate use of approximate entropy and sample entropy with short data sets. Ann. Biomed. Eng. 2013, 41, 349–365.
    [2] Richma et al. Physiological time-series analysis using approximate entropy and sample entropy. Am. J. -Physiol.-Heart Circ. Physiol. 2000, 278, H2039–H2049.
    [3] Govindan et al. Sample entropy analysis of heart rate variability: Dependence on signal length and sampling rate. Physiol. Meas. 2001, 22, 193–201.
    [4] Balasubramanian et al. On the analysis of movement smoothness. J. Neuroeng.  Rehabil. 2015, 12, 112.
    [5] Stergiou et al. Nonlinear Analysis for Human Movement Variability; Taylor & Francis : Boca Raton, FL, USA, 2016.
    [6] Sarwar et al. A Nonlinear Analysis Software Toolkit for Biomechanical Data. arXiv 2023, arXiv:2311.06723.
    [7] Rosenstein et al. A practical method for calculating largest Lyapunov exponents from small data sets.  Phys. D Nonlinear Phenom. 1993, 65, 117–134
    [8] Bruijn et al. Assessing the stability of human locomotion: A review of current measures. J. R.  Soc. Interface 2013, 10, 20120999

    """

    data_new = copy.deepcopy(data)
    if isinstance(channels, str):
        channels = [channels]
    else:
        channels = list(channels)
    if not channels:
        raise ValueError("At least one channel must be specified.")


    if save_channel is not None:
        channel = save_channel
    else:
        channel = channels[0]

    # run different analysis based on etype
    etype = etype.lower()

    if not ename:
        ename = etype

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
    elif etype == "step_symmetry":
        _, eyd, _, _, autocorr = symmetry(data=data_new, ch=channels)
        data_new = addchannel_data(data_new, ch_new_name='{0}_autocorr'.format(ename), ch_new_data=autocorr,)
    elif etype == "stride_symmetry":
        _, _, _, eyd, autocorr = symmetry(data=data_new, ch=channels)
        data_new = addchannel_data(data_new, ch_new_name='{0}_autocorr'.format(ename), ch_new_data=autocorr,)
    else:
        raise ValueError('Unknown event type: {0}'.format(etype))

    if isinstance(eyd, dict):
        for result_channel, value in eyd.items():
            data_new[result_channel]["event"][ename] = [0, value, 0]
    else:
        data_new[channel]["event"][ename] = [0, eyd, 0]

    return data_new
