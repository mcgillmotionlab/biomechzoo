from scipy.spatial.transform import Rotation as R
import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data


def load_quats(data:dict, suffix:str) -> np.ndarray:
    """
    Load quaternion components for a segment into a stacked array.

    Assumes channel keys follow the pattern ``<prefix>_Quat_W``,
    ``<prefix>_Quat_X``, ``<prefix>_Quat_Y``, ``<prefix>_Quat_Z``.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels.
    suffix : str
        Segment suffix (e.g., ``'LF'``) identifying which sensor to load.

    Returns
    -------
    ndarray of shape (n, 4)
        Stacked quaternion components in scalar-first order [W, X, Y, Z].

    Notes
    -----
    Example: ``load_quats(data, suffix='LF')`` returns the columns
    corresponding to ``Quat_W_LF``, ``Quat_X_LF``, ``Quat_Y_LF``, ``Quat_Z_LF``.
    """

    # Define the keys to search for segment data
    base = ["W", "X", "Y", "Z"]
    keys = [f"Quat_{b}_{suffix}" for b in base]

    # Extract keys
    quat_components = [data[k]['line'] for k in keys]

    return np.column_stack(quat_components)

def create_rot_matrix(axis: str, degrees: float) -> np.ndarray:
    """
    Create a 3x3 rotation matrix for a rotation about a principal axis.

    Parameters
    ----------
    axis : {'X', 'Y', 'Z'}
        The axis to rotate about (case-insensitive).
    degrees : float
        Rotation angle in degrees.

    Returns
    -------
    ndarray of shape (3, 3)
        Rotation matrix describing the rotation about the given axis.

    Raises
    ------
    ValueError
        If ``axis`` is not ``'X'``, ``'Y'``, or ``'Z'``.
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
    q_prox = load_quats(data, suffix=prox_prefix)
    q_dist = load_quats(data, suffix=dist_prefix)

    R_prox = R.from_quat(q_prox, scalar_first=True)
    R_dist = R.from_quat(q_dist, scalar_first=True)

    R_rel = R_prox.inv() * R_dist

    euler = R_rel.as_euler(order, degrees=True)

    data = addchannel_data(data=data,ch_new_name=(f'{prox_prefix}_{dist_prefix}_alpha'), ch_new_data= euler[:,0])
    data = addchannel_data(data=data,ch_new_name=(f'{prox_prefix}_{dist_prefix}_beta'), ch_new_data= euler[:,1])
    data = addchannel_data(data=data,ch_new_name=(f'{prox_prefix}_{dist_prefix}_gamma'), ch_new_data= euler[:,2])

    return data


def dcms2euler_data(data:dict, prox_key:str, dist_key:str, order:str, rot_prox_axis:str = None,
                    rot_dist_axis:str = None, rot_deg:float = None) -> dict:
    """
    Compute joint angles from direction cosine matrices (DCMs) stored in a zoo file.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing DCM channels for the proximal and
        distal segments.
    prox_key : str
        Channel key for the proximal segment's direction cosine matrix
        (e.g., ``'Thigh'``).
    dist_key : str
        Channel key for the distal segment's direction cosine matrix
        (e.g., ``'Shank'``).
    order : str
        Euler angle rotation order passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations.
    rot_prox_axis : {'X', 'Y', 'Z'} or None, optional
        If provided, the proximal segment's coordinate system is rotated
        about this axis before computing joint angles. Requires
        ``rot_deg`` to be set. Default is ``None``.
    rot_dist_axis : {'X', 'Y', 'Z'} or None, optional
        If provided, the distal segment's coordinate system is rotated
        about this axis before computing joint angles. Requires
        ``rot_deg`` to be set. Default is ``None``.
    rot_deg : float or None, optional
        Magnitude of the coordinate system rotation in degrees. Required
        when ``rot_prox_axis`` or ``rot_dist_axis`` is specified.
        Default is ``None``.

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'<prox_key>_<dist_key>_alpha'``, ``'<prox_key>_<dist_key>_beta'``,
        and ``'<prox_key>_<dist_key>_gamma'``, containing the first, second,
        and third Euler angles (in degrees) respectively.
        The relative rotation matrix is also stored under
        ``'<prox_key>_<dist_key>_R'``.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
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

    data = addchannel_data(data=data,ch_new_name=(f'{prox_key}_{dist_key}_alpha'), ch_new_data= euler[:,0])
    data = addchannel_data(data=data,ch_new_name=(f'{prox_key}_{dist_key}_beta'), ch_new_data= euler[:,1])
    data = addchannel_data(data=data,ch_new_name=(f'{prox_key}_{dist_key}_gamma'), ch_new_data= euler[:,2])

    return data
