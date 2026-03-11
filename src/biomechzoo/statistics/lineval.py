import os
import pandas as pd
import numpy as np
from typing import Any, Dict, Literal

from biomechzoo.utils.zload import zload


def lineval(root_folder: str, channel_list: list, output_format: Literal['array', 'wide', 'long'] = 'array',
            subject_level: int = 0, condition_level: int = 1) -> pd.DataFrame:
    """
    Extract time-normalized ``line`` arrays from Zoo files.

    This function recursively searches ``root_folder`` for ``.zoo`` files
    and extracts the ``line`` field from the specified channel. Folder
    levels are used to assign subject and condition labels.

    Data must already be time-normalized. The function will raise
    an error if inconsistent signal lengths are detected.

    :param root_folder: Root directory containing data.
    :type root_folder: str
    :param channel_name: Name of the channel to extract.
    :type channel_name: str
    :param output_format: Output format.
                   - ``'array'``: one column containing the full array (default)
                   - ``'wide'``: one column per timepoint (p0, p1, ...)
    :type output_format: Literal['array', 'wide']
    :param subject_level: Folder index used to define subject label
                          (0 = first folder below root).
    :type subject_level: int
    :param condition_level: Folder index used to define condition label
                            (0 = first folder below root).
    :type condition_level: int

    :raises KeyError: If the specified channel or ``line`` field is missing.
    :raises ValueError: If signals are not equal length (not normalized).
    :raises ValueError: If invalid format is provided.
    :raises IndexError: If folder depth is insufficient for specified levels.

    :return: DataFrame containing extracted line data with subject,
             condition, and trial references.
    :rtype: pandas.DataFrame
    """

    if output_format not in ['array', 'wide', 'long']:
        raise ValueError("format must be 'array', 'wide', or 'long'")

    results = []
    line_lengths = []
    line_array = pd.DataFrame()
    df = pd.DataFrame()

    for dirpath, _, files in os.walk(root_folder):

        for file in files:

            if not file.endswith('.zoo'):
                continue

            file_path = os.path.join(dirpath, file)

            relative_path = os.path.relpath(file_path, root_folder)
            parts = relative_path.split(os.sep)

            # Remove filename from parts
            folder_parts = parts[:-1]

            if len(folder_parts) <= max(subject_level, condition_level):
                raise IndexError(
                    'Folder depth is insufficient for specified '
                    'subject_level or condition_level.'
                )

            subject = folder_parts[subject_level]
            condition = folder_parts[condition_level]

            data = zload(file_path)

            for channel_name in channel_list:

                if channel_name not in data:
                    raise KeyError(
                        'Channel {} not found in {}'.format(channel_name, file_path)
                    )

                if len(channel_list) > 1:
                    line_array[channel_name] = data[channel_name]['line']
                else:
                    line_array = np.asarray(data[channel_name]['line']).squeeze()

                line_lengths.append(len(line_array))

            base_row: Dict[str, Any] = {
                'subject': subject,
                'condition': condition,
                'trial': file[:-4]
            }

            if output_format == 'array':
                base_row['line'] = line_array
                results.append(base_row)

            elif output_format == 'wide':
                for i in range(len(line_array)):
                    base_row['p{}'.format(i)] = line_array[i]
                results.append(base_row)

            if output_format == 'long':
                for channel_name in channel_list:
                    base_row[channel_name] = line_array[channel_name]
                base_data = pd.DataFrame.from_dict(base_row)

                df = pd.concat([df,base_data])

            print('Line extracted from {}'.format(file_path))

        # Strict normalization check
        if len(set(line_lengths)) > 1:
            raise ValueError(
                'Line arrays are not equal length. '
                'Data must be time-normalized before calling lineval().'
            )

    if output_format == 'long':
        None

    else:
        df = pd.DataFrame(results)

    return df


