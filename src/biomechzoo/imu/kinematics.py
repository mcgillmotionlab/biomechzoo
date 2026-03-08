from scipy.spatial.transform import Rotation as R
import numpy as np

def load_quats(data:dict, prefix:str) -> np.ndarray:
    """
    Load quaternion components for a segment into a stacked array.

    Assumes channel keys follow the pattern ``<prefix>_Quat_W``,
    ``<prefix>_Quat_X``, ``<prefix>_Quat_Y``, ``<prefix>_Quat_Z``.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels.
    prefix : str
        Segment prefix (e.g., ``'LF'``) identifying which sensor to load.

    Returns
    -------
    ndarray of shape (n, 4)
        Stacked quaternion components in scalar-first order [W, X, Y, Z].

    Notes
    -----
    Example: ``load_quats(data, prefix='LF')`` returns the columns
    corresponding to ``LF_Quat_W``, ``LF_Quat_X``, ``LF_Quat_Y``, ``LF_Quat_Z``.
    """

    # Define the keys to search for segment data
    base = ["W", "X", "Y", "Z"]
    keys = [f"{prefix}_Quat_{b}" for b in base]

    # Extract keys
    quat_components = [data[k]['line'] for k in keys]

    return np.column_stack(quat_components)

def imu_angles_data(data:dict, prox_prefix:str, dist_prefix:str, order:str) -> dict:
    """
    Compute Euler angles of the distal segment relative to the proximal segment.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels for each sensor.
    prox_prefix : str
        Channel prefix for the proximal segment (e.g., ``'LSh'``).
    dist_prefix : str
        Channel prefix for the distal segment (e.g., ``'LF'``).
    order : str
        Euler angle rotation order passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations.

    Returns
    -------
    dict
        Dictionary with keys ``'<prox>_<dist>_alpha'``, ``'<prox>_<dist>_beta'``,
        and ``'<prox>_<dist>_gamma'``, each containing a ``'line'`` array of
        Euler angles in degrees for the first, second, and third rotation
        in the sequence, respectively.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
    """

    # Load the quaternions from the proximal and distal segments
    q_prox = load_quats(data, prefix=prox_prefix)
    q_dist = load_quats(data, prefix=dist_prefix)

    # Convert to Rotation objects
    R_prox = R.from_quat(q_prox, scalar_first=True)
    R_dist = R.from_quat(q_dist, scalar_first=True)

    # Derive relative orientation
    R_rel = R_prox.inv() * R_dist

    # Convert to Euler angles using defined rotation order
    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_prefix}_{dist_prefix}_alpha": {"line": euler[:, 0]},
        f"{prox_prefix}_{dist_prefix}_beta":  {"line": euler[:, 1]},
        f"{prox_prefix}_{dist_prefix}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data