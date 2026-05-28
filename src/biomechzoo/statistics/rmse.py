import numpy as np

def compute_rmse(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    return np.sqrt(np.mean((a - b) ** 2))

def _export_rmse_csv(all_rmse: dict, out_folder: str):
    import csv, os

    os.makedirs(out_folder, exist_ok=True)
    out_file = os.path.join(out_folder, 'rmse_results.csv')

    all_keys = sorted({k for rmse in all_rmse.values() for k in rmse})

    with open(out_file, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file'] + all_keys)
        for filepath, rmse_vals in all_rmse.items():
            row = [filepath] + [rmse_vals.get(k, '') for k in all_keys]
            w.writerow(row)

    print(f"RMSE results exported to: {out_file}")


def rmse_data(data: dict, suff1: str, suff2: str):
    keys1 = [k for k in data.keys() if k.endswith('_' + suff1)]
    keys2 = [k for k in data.keys() if k.endswith('_' + suff2)]

    base_to_key1 = {k[:-(len(suff1) + 1)]: k for k in keys1}
    base_to_key2 = {k[:-(len(suff2) + 1)]: k for k in keys2}

    matching_bases = set(base_to_key1.keys()) & set(base_to_key2.keys())

    if not matching_bases:
        raise ValueError(f"No matching keys found for suffixes '{suff1}' and '{suff2}'")

    rmse_values = {}

    for base_name in sorted(matching_bases):
        k1 = base_to_key1[base_name]
        k2 = base_to_key2[base_name]
        rmse = compute_rmse(data[k1]['line'], data[k2]['line'])
        rmse_values[base_name] = rmse

    data['zoosystem'].setdefault('RMSE', {}).update(rmse_values)
    return data