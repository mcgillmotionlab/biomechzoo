import pandas as pd
import scipy.io
import os
import re

from utils.compute_sampling_rate_from_time import compute_sampling_rate_from_time


def csv2zoo_data(csv_path, header_len=10):

    # Read header lines until 'endheader'
    header_lines = []
    with open(csv_path, 'r') as f:
        for line in f:
            print(f"Line read: '{line.rstrip()}'")  # Show exactly what is read
            header_lines.append(line.strip())
            if line.strip().lower() == 'endheader':
                print("Found endheader, stopping header read.")
                break

    # Parse metadata
    metadata = _parse_metadata(header_lines)

    # Step 3: Load data
    df = pd.read_csv(csv_path, skiprows=header_len)
    time = df.iloc[:, 0].values  # first column is Time
    data = df.iloc[:, 1:]

    # S Assemble zoo data
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
