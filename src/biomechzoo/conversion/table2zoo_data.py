import pandas as pd
import os
import re

from biomechzoo.utils.set_zoosystem import set_zoosystem
from biomechzoo.utils.compute_sampling_rate_from_time import compute_sampling_rate_from_time


def table2zoo_data(fl, extension, skip_rows=0, freq=None):

    if 'csv' in extension:
        df, metadata, freq = _csv2zoo(fl, skip_rows=skip_rows, freq=freq)

    elif 'parquet' in extension:
        df, metadata, freq = _parquet2zoo(fl, skip_rows=skip_rows, freq=freq)
    else:
        raise ValueError('extension {} not implemented'.format(extension))

    # assemble zoo data
    data = {'zoosystem': set_zoosystem()}
    for ch in df.columns:
        data[ch] = {
            'line': df[ch].values,
            'event': []
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
    data['zoosystem']['Video']['Freq'] = freq
    data['zoosystem']['Analog']['Freq'] = 'None'

    if metadata is not None:
        data['zoosystem']['Other'] = metadata

    return data


def _parquet2zoo(fl, skip_rows=0, freq=None):
    df = pd.read_parquet(fl)
    metadata = None
    return df, metadata, freq

def _csv2zoo(fl, skip_rows=0, freq=None):
    header_lines = []
    with open(fl, 'r') as f:
        for line in f:
            header_lines.append(line.strip())
            if line.strip().lower() == 'endheader':
                break
    # Parse metadata
    metadata = _parse_metadata(header_lines)

    # try to find frequency in metadata
    if freq is None:
        if 'freq' in metadata:
            freq = metadata['freq']
        elif 'sampling_rate' in metadata:
            freq = metadata['sampling_rate']
        else:
            freq = None  # or raise an error

    # read csv
    df = pd.read_csv(fl, skiprows=skip_rows)

    return df, metadata, freq




def _parse_metadata(header_lines):
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
    project_root = os.path.dirname(current_dir)
    csv_file = os.path.join(project_root, 'data', 'other', 'opencap_walking1.csv')

    data = table2zoo_data(csv_file)
