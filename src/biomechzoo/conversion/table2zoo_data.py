import os
import re
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from biomechzoo.utils.set_zoosystem import set_zoosystem
from biomechzoo.utils.compute_sampling_rate_from_time import compute_sampling_rate_from_time


def table2zoo_data(
        fl: str, extension: str, skip_rows: int = 0,
        freq: Optional[int] = None, data_type: str = 'Video',
        sep: Optional[str] = None,
) -> Dict:
    """
    Convert a CSV or Parquet table to zoo format.

    Parameters
    ----------
    fl : str
        Path to the table file.
    extension : str
        File extension/format, must contain ``'csv'`` or ``'parquet'``.
    skip_rows : int, optional
        Number of header rows to skip when reading a CSV file. Default
        is 0.
    freq : int, optional
        Sampling frequency in Hz. If None, it is inferred from a time
        column in the table.
    data_type : {'Video', 'Analog'}, optional
        Zoo section to store the channels under. Default is 'Video'.
    sep : str, optional
        Column separator for CSV files, passed to ``pandas.read_csv``.

    Returns
    -------
    data : dict
        Zoo dictionary with one channel per table column, plus a
        'zoosystem' metadata entry.

    Raises
    ------
    ValueError
        If ``extension`` is not a supported format, or if ``freq`` is
        None and no time column can be found to infer it.
    """
    if 'csv' in extension:
        df, metadata = _csv2zoo(fl, skip_rows=skip_rows, sep=sep)

    elif 'parquet' in extension:
        df, metadata= _parquet2zoo(fl)
    else:
        raise ValueError('extension {} not implemented'.format(extension))

    # assemble zoo data
    data = {'zoosystem': set_zoosystem()}
    for ch in df.columns:
        data[ch] = {
            'line': df[ch].values,
            'event': {}
        }

    # now try to calculate freq from a time column
    if freq is None:
        time_col = [col for col in df.columns if 'time' in col.lower()]
        if time_col is not None and len(time_col) > 0:
            time_data = df[time_col].to_numpy()[:, 0]
            freq = compute_sampling_rate_from_time(time_data)
        else:
            raise ValueError('Unable to compute sampling rate for time column, please specify a sampling frequency'
                             )
    # add metadata
    if data_type == 'Video':
        data['zoosystem']['Video']['Freq'] = freq
        data['zoosystem']['Video']['Channels'] = list(df.columns)
        data['zoosystem']['Analog']['Channels'] = {}
        data['zoosystem']['Analog']['Freq'] = {}

    elif data_type == 'Analog':
        data['zoosystem']['Analog']['Freq'] = freq
        data['zoosystem']['Analog']['Channels'] = list(df.columns)
        data['zoosystem']['Video']['Channels'] = {}
        data['zoosystem']['Video']['Freq'] = {}

    if metadata is not None:
        data['zoosystem']['Other'] = metadata

    return data


def _parquet2zoo(fl: str) -> Tuple[pd.DataFrame, Optional[Dict]]:
    """
    Read a Parquet file into a DataFrame.

    Parameters
    ----------
    fl : str
        Path to the Parquet file.

    Returns
    -------
    df : pandas.DataFrame
        Table data.
    metadata : dict or None
        Always None; Parquet files carry no header metadata here.
    """
    df = pd.read_parquet(fl)
    metadata = None

    return df, metadata


def _csv2zoo(
        fl: str, skip_rows: int, sep: Optional[str],
) -> Tuple[pd.DataFrame, Dict]:
    """
    Read a CSV file (with an optional metadata header) into a
    DataFrame.

    Parameters
    ----------
    fl : str
        Path to the CSV file.
    skip_rows : int
        Number of header rows to skip before the column header row.
    sep : str or None
        Column separator, passed to ``pandas.read_csv``.

    Returns
    -------
    df : pandas.DataFrame
        Table data.
    metadata : dict
        Key/value metadata parsed from any ``key=value`` header lines
        preceding an ``ENDHEADER`` line.
    """
    header_lines = []
    with open(fl, 'r') as f:
        for line in f:
            header_lines.append(line.strip())
            if line.strip().lower() == 'endheader':
                break
    # Parse metadata
    metadata = _parse_metadata(header_lines)

    # read csv
    df = pd.read_csv(fl, skiprows=skip_rows, sep=sep)

    return df, metadata




def _parse_metadata(
        header_lines: List[str],
) -> Dict[str, Union[int, float, str]]:
    """
    Parse ``key=value`` metadata from CSV header lines.

    Parameters
    ----------
    header_lines : list of str
        Lines preceding (and including) an ``ENDHEADER`` line.

    Returns
    -------
    metadata : dict of {str : int or float or str}
        Parsed key/value pairs. Values are cast to int or float when
        a leading numeric token is found, otherwise kept as a
        lowercased string.
    """
    metadata = {}
    for line in header_lines:
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()

            # Strip trailing commas and whitespace explicitly
            val = val.rstrip(',').strip()

            # Extract first numeric token if any
            match = re.search(r'[-+]?\d*\.?\d+', val)
            if match:
                num_str = match.group(0)
                try:
                    val_num = int(num_str)
                except ValueError:
                    val_num = float(num_str)
            else:
                # Now val should be clean of trailing commas, so just lower case it
                val_num = val.lower()

            metadata[key] = val_num
    return metadata




if __name__ == '__main__':
    """ for unit testing"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    csv_file = os.path.join(project_root, 'data', 'csv', 'opencap_jogging.csv')
    data = table2zoo_data(csv_file, extension='csv', freq=60)
