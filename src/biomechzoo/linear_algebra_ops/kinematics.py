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

def create_rot_matrix(axis: str, degrees: float) -> np.ndarray:
    """
    Creates a 3 x 3 matrix describing a rotation around the given axis.

    :param      axis: 'X', 'Y', or 'Z'
    :param      degrees: rotation angle in degrees

    :return:    3 x 3 matrix
    """

    axis = axis.upper()

    if axis not in ["X", "Y", "Z"]:
        raise ValueError("axis must be 'X', 'Y', or 'Z'")

    theta = np.deg2rad(degrees)

    if axis == "X":
        R = np.array([
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta),  np.cos(theta)]
        ])

    elif axis == "Y":
        R = np.array([
            [ np.cos(theta), 0, np.sin(theta)],
            [ 0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])

    else:  #Z
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0, 0, 1]
        ])

    return R

def quats2euler(data:dict, prox_prefix:str, dist_prefix:str, order:str) -> dict:
    """
    Compute Euler angles of the distal segment relative to the proximal segment from quaterion data.

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
    q_prox = load_quats(data, prefix=prox_prefix)
    q_dist = load_quats(data, prefix=dist_prefix)

    R_prox = R.from_quat(q_prox, scalar_first=True)
    R_dist = R.from_quat(q_dist, scalar_first=True)

    R_rel = R_prox.inv() * R_dist

    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_prefix}_{dist_prefix}_alpha": {"line": euler[:, 0]},
        f"{prox_prefix}_{dist_prefix}_beta":  {"line": euler[:, 1]},
        f"{prox_prefix}_{dist_prefix}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data


def dcms2euler_data(data:dict, prox_key:str, dist_key:str, order:str, rot_prox_axis:str = None,
                    rot_dist_axis:str = None, rot_deg:float = None) -> dict:
    """
    Determines joint angles given a direction cosine matrix and a rotation order.

    #todo: fix docstrings to numpy style

    Parameters
    ----------

    data:            .zoo file containing the direction cosine matrix representing the orientations of the
                            proximal and distal segments with respect to a global reference frame.
    rox_key:        The key distinguishing the proximal segment's direction cosine matrix.
    dist_key:        The key distinguishing the distal segment's direction cosine matrix.
    order:           The rotation order to be used. Note that case determines if this rotation in intrinsic
                            or extrinsic. For more information, please refer to scipy.spatial.transform.Rotation docs:
                            https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
    rot_prox_axis:   Optional. Determines if one of the segment's proximal local coordinate systems is to be
                            rotated before the calculation of joint angles. If this rotation is desired, the user must
                            input the axis they desire to rotate about (i.e., either "X", "Y" or "Z". For more
                            information, please refer to the 'create_rot_matrix' function.
    rot_dist_axis:   Optional. Determines if one of the segment's distal local coordinate systems is to be
                            rotated before the calculation of joint angles. If this rotation is desired, the user must
                            input the axis they desire to rotate about (i.e., either "X", "Y" or "Z". For more
                            information, please refer to the 'create_rot_matrix' function.
    rot_deg:         Optional. If either 'rot_prox_axis' or 'rot_dist_axis' are specified, this argument will
                            determine the magnitude of the rotation of the coordinate system (in degrees)

    Returns
    -------
                    The .zoo file will be returned with the addition of the joint angles added. The dictionary
                            specifies the joint angle data through its keys containing the proximal and distal segment,
                            as well as 'alpha', 'beta', and 'gamma', specifying the first, second, and third rotations
                            in the 'order' argument, respectively.
    """

    R_prox_array = np.stack(
        [data[f'{prox_key}_x']['line'], data[f'{prox_key}_y']['line'], data[f'{prox_key}_z']['line']],
        axis=-1
    )

    R_prox = R.from_matrix(R_prox_array)

    if rot_prox_axis is not None:

        transform = R.from_matrix(
            matrix = create_rot_matrix(
                axis = rot_prox_axis,
                degrees = rot_deg
            )
        )

        R_prox = R_prox * transform

    R_dist_array = np.stack(
        [data[f'{dist_key}_x']['line'], data[f'{dist_key}_y']['line'], data[f'{dist_key}_z']['line']],
        axis=-1
    )

    R_dist = R.from_matrix(R_dist_array)

    if rot_dist_axis is not None:
        transform = R.from_matrix(
            matrix = create_rot_matrix(
                axis=rot_dist_axis,
                degrees=rot_deg
            )
        )

        R_dist = R_dist * transform

    R_rel = R_prox.inv() * R_dist

    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_key}_{dist_key}_alpha": {"line": euler[:, 0]},
        f"{prox_key}_{dist_key}_beta":  {"line": euler[:, 1]},
        f"{prox_key}_{dist_key}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data
