import os
import time
import inspect
import pandas as pd
from biomechzoo.utils.engine import engine
from biomechzoo.imu.kinematics import load_quats
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp

def combine_quats_to_csv():
    raise NotImplementedError("Use combine_imu_to_csv() instead")

def combine_imu_to_csv_data(
    csv_files: list[str],
    prefixes: list[str],
    out_folder: str = None,
    out_filename: str = None,
    verbose = 1
    ) -> str:

    """Concatenates time, quaternions, gyroscope, and accelerometer data
    from multiple CSV files into a single CSV file with prefixes defining segment."""

    if out_folder is None:
        out_folder = "combined_csvs"

    if out_filename is None:
        out_filename = "combined_sensors.csv"

    root = os.getcwd()
    save_folder = os.path.join(root, out_folder)
    os.makedirs(save_folder, exist_ok=True)

    time_col: str = "PacketCounter"
    quat_cols: list[str] = ["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"]
    gyr_cols: list[str] = ["Gyr_X", "Gyr_Y", "Gyr_Z"]
    acc_cols: list[str] = ["Acc_X", "Acc_Y", "Acc_Z"]

    first_df = pd.read_csv(csv_files[0])
    time_df = first_df[[time_col]].rename(columns={time_col: "time"})

    all_sensor_dfs = []

    for csv_path, prefix in zip(csv_files, prefixes):
        df = pd.read_csv(csv_path)

        quat_df = df[quat_cols].rename(columns={c: f"{prefix}_{c}" for c in quat_cols})
        gyr_df  = df[gyr_cols].rename(columns={c: f"{prefix}_{c}" for c in gyr_cols})
        acc_df  = df[acc_cols].rename(columns={c: f"{prefix}_{c}" for c in acc_cols})

        all_sensor_dfs.extend([quat_df, gyr_df, acc_df])

    combined_df = pd.concat([time_df] + all_sensor_dfs, axis=1)

    out_file = os.path.join(save_folder, out_filename)
    combined_df.to_csv(out_file, index=False)
    print(f"Saved combined CSV to: {out_file}")

    return out_file


def combine_imu_to_csv(prefixes: list[str], in_folder, out_folder=None, inplace=False, name_contains=None,
                       subfolders=None, verbose=1):
    """
    Recursive version of the combine_imu_to_csv_data function
    """

    start_time = time.time()
    in_folder = in_folder

    fl = list(engine(in_folder, extension='.csv', name_contains=name_contains, subfolders=subfolders))

    if not fl:
        batchdisp('No CSV files found in {}'.format(in_folder), level=0, verbose=verbose)
        return

    subject_groups = {}
    for csv_file in fl:
        subject_folder = os.path.dirname(csv_file)
        subject_name = os.path.basename(subject_folder)

        if subject_name not in subject_groups:
            subject_groups[subject_name] = []
        subject_groups[subject_name].append(csv_file)

    for subject_name, csv_files in subject_groups.items():
        batchdisp('combine_imu_to_csv for channel {}'.format(subject_name), level=2, verbose=verbose)

        csv_files_sorted = []
        prefixes_sorted = []
        for prefix in prefixes:
            for csv_file in csv_files:
                if csv_file.endswith('_{}.csv'.format(prefix)):
                    csv_files_sorted.append(csv_file)
                    prefixes_sorted.append(prefix)
                    break

        if csv_files_sorted:
            combine_imu_to_csv_data(
                csv_files=csv_files_sorted,
                prefixes=prefixes_sorted,
                out_folder=out_folder,
                out_filename='{}_combined.csv'.format(subject_name),
                verbose=verbose
            )

    method_name = inspect.currentframe().f_code.co_name
    batchdisp(
        '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(subject_groups),
                                                                   time.time() - start_time),
        level=1, verbose=verbose)