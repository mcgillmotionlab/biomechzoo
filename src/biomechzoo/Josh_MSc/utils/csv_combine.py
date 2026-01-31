import os
import time
import inspect
import pandas as pd
from collections import defaultdict
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp

def combine_quats_to_csv():
    raise NotImplementedError("Use combine_imu_to_csv() instead")

def combine_imu_to_csv_data(csv_files: list[str], prefixes: list[str], out_folder: str = None, out_filename: str = None,
    verbose: int = 1) -> str:

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

    first_df = pd.read_csv(csv_files[0]) # Taking the time column from the first fiel, assuming they all have = lengths
    combined_dfs = [
        first_df[["PacketCounter"]].rename(columns={"PacketCounter": "time"})
    ]

    for csv_path, prefix in zip(csv_files, prefixes):
        df = pd.read_csv(csv_path)
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

def combine_imu_to_csv(prefixes: list[str],in_folder,out_folder=None,inplace=False,name_contains=None,subfolders=None,
    verbose=1):

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