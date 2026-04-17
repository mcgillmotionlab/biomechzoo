import numpy as np

from biomechzoo.utils.zload import zload
from biomechzoo.utils.engine import engine

from biomechzoo.visualization.src_ensembler.utils import _get_condition_from_path



def _calculate_average(fl, channels, conditions):
    """
    Calculates the average timeseries for the channels

    Parameters
    ----------
    fl : list of str
        list containing the full path to the files
    channels : list of str
        list containing the channel names
    conditions : list of str
        list containing the condition names
        """
    # Initialize dictionary to store data

    data_new = {c: {ch: [] for ch in channels} for c in conditions}

    for f in fl:
        data = zload(f)
        con = _get_condition_from_path(f, conditions)

        # Create dataframe from the two conditions.
        for channel in channels:
            try:
                ch_data_line = data[channel]["line"]
                data_new[con][channel].append(ch_data_line)
            except KeyError:
                print(f"Channel {channel} not found in file {fl}")

    # Average per condition per channel
    average_dict = {c: {ch: {} for ch in channels} for c in conditions}
    for c, condition in enumerate(data_new):
        for i, channel in enumerate(data_new[condition]):
            line_data = data_new[condition][channel]
            array_data = np.array(line_data)
            average = np.nanmean(array_data, axis=0)
            standard_dev = np.nanstd(array_data, axis=0)

            average_dict[condition][channel].update({"average": average, "standard_dev": standard_dev})

    return average_dict



