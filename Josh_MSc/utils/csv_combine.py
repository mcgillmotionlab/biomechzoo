import os
import pandas as pd

def combine_quats_to_csv(
    csv_files: list[str],
    prefixes: list[str],
    out_folder: str = "combined_csvs",
    out_filename: str = None
    ) -> str:

    """ Concatenates quaternions from multiple CSV files into a single CSV file with prefixes defining segment."""

    root = os.getcwd()
    save_folder = os.path.join(root, out_folder)
    os.makedirs(save_folder, exist_ok=True)

    time_col: str = "PacketCounter"
    quat_cols: list[str] = ["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"]

    first_df = pd.read_csv(csv_files[0])
    time_df = first_df[[time_col]].rename(columns={time_col: "time"})

    all_quat_dfs = []

    for csv_path, prefix in zip(csv_files, prefixes):
        df = pd.read_csv(csv_path)
        df = df[quat_cols].rename(columns={c: f"{prefix}_{c}" for c in quat_cols})
        all_quat_dfs.append(df)

    # concatenate time + all quat blocks
    combined_df = pd.concat([time_df] + all_quat_dfs, axis=1)

    if out_filename is None:
        out_filename = "combined_quats.csv"

    out_file = os.path.join(save_folder, out_filename)
    combined_df.to_csv(out_file, index=False)
    print(f"Saved combined CSV to: {out_file}")

    return out_file


