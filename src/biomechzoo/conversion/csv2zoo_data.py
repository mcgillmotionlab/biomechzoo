import pandas as pd
import os
import re

from biomechzoo.utils.compute_sampling_rate_from_time import compute_sampling_rate_from_time


def csv2zoo_data(csv_path, type='csv',skip_rows=0):
    # todo: check calculation for sampling rate

    # Read the metadata rows (if any)
    metadata = {}
    if skip_rows > 0 and type == 'csv':
        meta_df = pd.read_csv(csv_path, header=None, nrows=skip_rows, dtype=str)
        for i in meta_df.index:
            # Drop NaN and whitespace-only entries
            row_data = [x for x in meta_df.iloc[i].tolist() if pd.notna(x) and str(x).strip() != ""]
            metadata[f"row_{i}"] = row_data

    if type == 'csv':
        df = pd.read_csv(csv_path, skiprows=skip_rows)
    elif type =='parquet':
        df = pd.read_parquet(csv_path)
    else:
        raise ValueError('type must be csv or parquet')

    # Use all columns
    data = df.iloc[:, 0:]

    # assemble zoo data
    zoo_data = {}
    for ch in data.columns:
        zoo_data[ch] = {
            'line': data[ch].values,
            'event': []
        }

    # compute sampling rate
    fsamp = compute_sampling_rate_from_time(time)

    # add metadata
    # todo update zoosystem to match biomechzoo requirements
    zoo_data['zoosystem'] = metadata
    zoo_data['zoosystem']['Freq'] = fsamp

    return zoo_data


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

    data = csv2zoo_data(csv_file)
