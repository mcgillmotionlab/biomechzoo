import pandas as pd
import os
import re

from biomechzoo.utils.set_zoosystem import set_zoosystem
from biomechzoo.utils.compute_sampling_rate_from_time import compute_sampling_rate_from_time


def table2zoo_data(csv_path, type='csv', skip_rows=0, freq=None):
    # todo: check calculation for sampling rate

    if type not in ['csv', 'parquet']:
        raise NotImplementedError('Only csv and parquet currently supported')

    # Read header lines until 'endheader'
    metadata = {}
    if type == 'csv' and skip_rows > 0:
        header_lines = []
        with open(csv_path, 'r') as f:
            for line in f:
                header_lines.append(line.strip())
                if line.strip().lower() == 'endheader':
                    break
        # Parse metadata
        metadata = _parse_metadata(header_lines)

    if type == 'csv':
        df = pd.read_csv(csv_path, skiprows=skip_rows)
    elif type =='parquet':
        df = pd.read_parquet(csv_path)
    else:
        raise ValueError('type must be csv or parquet')

    # Use all columns
    df_data = df.iloc[:, 0:]

    # assemble zoo data
    data = {}
    data['zoosystem'] = set_zoosystem()

    for ch in df_data.columns:
        data[ch] = {
            'line': df_data[ch].values,
            'event': []
        }

    # try to find frequency in metadata
    if freq is None:
        if 'freq' in metadata:
            freq = metadata['freq']
        elif 'sampling_rate' in metadata:
            freq = metadata['sampling_rate']
        else:
            freq = None  # or raise an error

    # now try to calculate freq from a time column
    if freq is None:
        time_col = [col for col in df.columns if 'time' in col.lower()]
        if time_col is not None:
            time_data = df[time_col].to_numpy()[:, 0]
            freq = compute_sampling_rate_from_time(time_data)

    # add metadata
    data['zoosystem']['Video']['Freq'] = freq
    data['zoosystem']['Analog']['Freq'] = 'None'
    if 'version' in metadata:
        data['zoosystem']['collection_system_version'] = metadata['version']

    return data


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
