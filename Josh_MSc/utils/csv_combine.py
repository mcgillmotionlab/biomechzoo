import os
import pandas as pd

def combine_quats_to_csv(prox_csv, dist_csv, prox_prefix="prox_", dist_prefix="dist_", out_folder="combined_csvs", out_filename="combined_quats.csv"):

    root = os.getcwd()
    save_folder = os.path.join(root, out_folder)
    os.makedirs(save_folder, exist_ok=True)

    prox_df = pd.read_csv(prox_csv)
    dist_df = pd.read_csv(dist_csv)

    quat_cols = ["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"]

    prox_df = prox_df[quat_cols].rename(columns={c: f"{prox_prefix}{c}" for c in quat_cols})
    dist_df = dist_df[quat_cols].rename(columns={c: f"{dist_prefix}{c}" for c in quat_cols})

    combined_df = pd.concat([prox_df, dist_df], axis=1)

    out_file = os.path.join(save_folder, out_filename)
    combined_df.to_csv(out_file, index=False)
    print(f"Saved combined CSV to: {out_file}")

    return out_file


