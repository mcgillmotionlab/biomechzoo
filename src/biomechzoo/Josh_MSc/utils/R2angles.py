from scipy.spatial.transform import Rotation as R

def R2angles_data(data:dict, prox_key:str, dist_key:str, order:str) -> dict:
    """
    """

    # Load the quaternions from the proximal and distal segments
    R_prox = R.from_matrix(matrix = data[prox_key]['matrix'])
    R_dist = R.from_matrix(matrix = data[dist_key]['matrix'])

    # Derive relative orientation
    R_rel = R_prox.inv() * R_dist

    # Convert to Euler angles using defined rotation order
    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_key}_{dist_key}_alpha": {"line": euler[:, 0]},
        f"{prox_key}_{dist_key}_beta":  {"line": euler[:, 1]},
        f"{prox_key}_{dist_key}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data