import os
import time
import inspect
from collections import defaultdict
from typing import List, NoReturn, Optional, Union

import pandas as pd

from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp


def combine_quats_to_csv() -> NoReturn:
    """
    Deprecated. Use :func:`combine_imu_to_csv` instead.

    Raises
    ------
    NotImplementedError
        Always.
    """
    raise NotImplementedError("Use combine_imu_to_csv() instead")


def combine_imu_to_csv_data(
        csv_files: List[str], prefixes: List[str],
        skip_rows: Optional[int] = None, out_folder: Optional[str] = None,
        out_filename: Optional[str] = None, verbose: int = 1,
) -> str:
    """
    Merge multiple Xsens DOT CSV files into a single combined CSV file.

    Each sensor file is identified by a prefix. Quaternion, gyroscope, and
    accelerometer columns from every file are renamed with the corresponding
    prefix and concatenated side-by-side.

    Parameters
    ----------
    csv_files : list of str
        Ordered list of paths to the individual sensor CSV files.
    prefixes : list of str
        Ordered list of sensor prefixes (e.g. ``['LF', 'RF', 'Trunk']``).
        Must be the same length as ``csv_files``.
    skip_rows : int or None, optional
        Number of header rows to skip when reading each CSV. Default is ``None``.
    out_folder : str or None, optional
        Directory to write the combined CSV. Defaults to ``'combined_csvs'``
        inside the current working directory.
    out_filename : str or None, optional
        Name of the output CSV file. Defaults to ``'combined_sensors.csv'``.
    verbose : int, optional
        If non-zero, prints the path of the saved file. Default is ``1``.

    Returns
    -------
    out_file : str
        Absolute path to the saved combined CSV file.
    """

    if out_folder is None:
        out_folder = "combined_csvs"
    if out_filename is None:
        out_filename = "combined_sensors.csv"

    save_folder = os.path.join(os.getcwd(), out_folder)
    os.makedirs(save_folder, exist_ok=True)

    sensor_columns = {
        "Quat": ["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"],
        "Gyr":  ["Gyr_X", "Gyr_Y", "Gyr_Z"],
        "Acc":  ["Acc_X", "Acc_Y", "Acc_Z"],
    }

    first_df = pd.read_csv(csv_files[0], skiprows= skip_rows) # Taking the time column from the first file, assuming they all have = lengths
    combined_dfs = [
        first_df[["PacketCounter"]].rename(columns={"PacketCounter": "time"})
    ]

    for csv_path, prefix in zip(csv_files, prefixes):
        df = pd.read_csv(csv_path, skiprows=skip_rows)
        for cols in sensor_columns.values():
            renamed = {
                c: f"{prefix}_{c}" for c in cols
            }
            combined_dfs.append(df[cols].rename(columns=renamed))

    combined_df = pd.concat(combined_dfs, axis=1)
    out_file = os.path.join(save_folder, out_filename)
    combined_df.to_csv(out_file, index=False)

    if verbose:
        print(f"Saved combined CSV to: {out_file}")

    return out_file

def combine_imu_to_csv(
        prefixes: List[str], in_folder: str,
        out_folder: Optional[str] = None, inplace: bool = False,
        name_contains: Optional[Union[str, List[str]]] = None,
        subfolders: Optional[Union[str, List[str]]] = None,
        verbose: int = 1,
) -> None:
    """
    Batch-combine Xsens DOT CSV files for multiple subjects.

    Searches ``in_folder`` recursively for CSV files, groups them by subject
    (parent folder name), matches files to ``prefixes`` by filename suffix,
    then calls :func:`combine_imu_to_csv_data` for each subject.

    Parameters
    ----------
    prefixes : list of str
        Sensor prefixes to match and order (e.g. ``['LF', 'RF', 'Trunk']``).
        Files whose basename ends with a prefix will be selected.
    in_folder : str
        Root folder to search for CSV files.
    out_folder : str or None, optional
        Root output folder. Each subject gets its own subfolder. Defaults to
        the subject's source folder.
    inplace : bool, optional
        Not currently used. Reserved for future in-place saving. Default is ``False``.
    name_contains : str or list of str or None, optional
        Only include files whose path contains this substring or all these
        substrings. Default is ``None`` (no filter).
    subfolders : str or list of str or None, optional
        Only include files located inside these subfolder names. Default is
        ``None`` (no filter).
    verbose : int, optional
        Verbosity level. ``0`` = silent, ``1`` = summary, ``2`` = per-subject.
        Default is ``1``.

    Returns
    -------
    None
        Results are saved to disk; nothing is returned.
    """

    start_time = time.time()
    files = list(engine(
        in_folder,
        extension='.csv',
        name_contains=name_contains,
        subfolders=subfolders
    ))
    subjects = defaultdict(list)
    for f in files:
        subjects[os.path.basename(os.path.dirname(f))].append(f)

    for subject, csv_files in subjects.items():
        batchdisp(
            f'combine_imu_to_csv for {subject}',
            level=2,
            verbose=verbose
        )

        prefix_map = {
            os.path.splitext(os.path.basename(f))[0].split('_')[-1]: f
            for f in csv_files
        }
        csv_sorted = []
        prefix_sorted = []

        for p in prefixes:
            if p in prefix_map:
                csv_sorted.append(prefix_map[p])
                prefix_sorted.append(p)

        if csv_sorted:
            subject_out_folder = os.path.join(out_folder, subject) if out_folder else subject
            combine_imu_to_csv_data(
                csv_files=csv_sorted,
                prefixes=prefix_sorted,
                out_folder=subject_out_folder,
                out_filename=f'{subject}_combined.csv',
                verbose=verbose
            )
    batchdisp(
        f'{inspect.currentframe().f_code.co_name} complete '
        f'for {len(subjects)} file(s) in {time.time() - start_time:.2f}s',
        level=1,verbose=verbose
    )