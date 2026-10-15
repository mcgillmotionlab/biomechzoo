import EntropyHub as EH
import statsmodels.tsa.stattools as stattools
import numpy as np

from .signal_inputs import three_axis_signal


DIM = 2


def sample_entropy(data, ch):
    """Compute sample entropy using an autocorrelation-derived time delay.

    Parameters
    ----------
    data : dict
        Biomechanical data dictionary containing the signal channels.
    ch : list[str]
        Either three names of 1D coordinate channels or one name whose channel
        contains a 2D array with shape ``(samples, 3)``.

    Returns
    -------
    tuple[list[float], np.ndarray]
        Sample entropy values returned by EntropyHub and the signal norm used
        in the calculation.

    Raises
    ------
    ValueError
        If the channels do not describe a three-axis signal in one of the
        supported formats.
    """
    signal, _ = three_axis_signal(data, ch)
    norm = np.linalg.norm(signal, axis=1)

    autocorr = stattools.acf(norm, nlags=len(norm))
    drop_value = 1 / np.exp(1)
    tau = np.argmax(autocorr < drop_value)
    sampen_values, _, _ = EH.SampEn(
        Sig=norm, m=DIM, tau=int(tau), r=None
    )

    return sampen_values.tolist(), norm