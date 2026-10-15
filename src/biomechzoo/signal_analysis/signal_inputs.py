import numpy as np


def three_axis_signal(data, channels):
    """Return a three-axis signal matrix and its source channel names."""
    if isinstance(channels, str):
        channels = [channels]
    else:
        channels = list(channels)

    if len(channels) == 1:
        name = channels[0]
        signal = np.asarray(data[name]["line"])
        if signal.ndim != 2 or signal.shape[1] != 3:
            raise ValueError(
                "A single channel for 3D analysis must have shape (samples, 3)."
            )
        return signal, channels

    if len(channels) != 3:
        raise ValueError(
            "3D analysis requires either one channel with three columns "
            "or three 1D channels."
        )

    lines = [np.asarray(data[name]["line"]) for name in channels]
    if any(line.ndim != 1 for line in lines):
        raise ValueError("Each of three separate channels must be 1D.")
    if len({len(line) for line in lines}) != 1:
        raise ValueError("All three channels must have the same length.")

    return np.column_stack(lines), channels
