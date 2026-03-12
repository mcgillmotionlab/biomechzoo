import os

import pandas as pd


def combine_quats_to_csv(
    csv_files: list[str],
    prefixes: list[str],
    out_folder: str = None,
    out_filename: str = None
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
