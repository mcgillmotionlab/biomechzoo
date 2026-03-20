from scipy.spatial.transform import Rotation as R
import numpy as np
from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.processing.removechannel_data import removechannel_data
from biomechzoo.linear_algebra_ops.make_unit import make_unit

def _resolve_marker_label(data: dict, marker: str) -> str:

    """
    Finds the correct marker label in data -- created to handle different labelling conventions in our data (e.g., we
    want to make LShank1 and LeftShank1 work for indexing our marker data within our zoo files).

    :params data:       dictionary containing out marker data
    :params marker:     marker label

    :returns:           label, a string that exists as a key in 'data'

    """

    marker_keys = [k for k in data]

    if marker in marker_keys:
        return marker

    if marker.startswith("Left"):
        label = "L" + marker[4:]
        if label in marker_keys:
            return label

    if marker.startswith("Right"):
        label = "R" + marker[5:]
        if label in marker_keys:
            return label

    if marker.startswith("L"):
        label = "Left" + marker[1:]
        if label in marker_keys:
            return label

    if marker.startswith("R"):
        label = "Right" + marker[1:]
        if label in marker_keys:
            return label

    raise KeyError(
        f"Marker '{marker}' not found. Available markers: {marker_keys}"
    )

def _decomp2euler(R_rel, data:dict, prox_ch: list[str], dist_ch: list[str], sequence: str)-> dict:

    """
    Decomposes a direction cosine matrix (DCM) to euler angles.
    """

    euler = R_rel.as_euler(sequence, degrees=True)

    # Convention for finding labels assumes that bmech.combine_files is being used for combining
    # (i.e., the line data for each quaternion components contains the segment as a suffix divided by '_').
    prox_label = prox_ch[0].split('_')[-1]
    dist_label = dist_ch[0].split('_')[-1]

    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_alpha'), ch_new_data= euler[:,0])
    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_beta'), ch_new_data= euler[:,1])
    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_gamma'), ch_new_data= euler[:,2])

    return data

def _decompdcm(data:dict, dcm:np.ndarray, seg:str)-> dict:

    i = dcm[:, :, 0]
    j = dcm[:, :, 1]
    k = dcm[:, :, 2]

    data = addchannel_data(data=data, ch_new_name=f'i_{seg}', ch_new_data=i)
    data = addchannel_data(data=data, ch_new_name=f'j_{seg}', ch_new_data=j)
    data = addchannel_data(data=data, ch_new_name=f'k_{seg}', ch_new_data=k)

    return data

def _create_rot_matrix(axis: str, degrees: float) -> np.ndarray:
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
        R = np.array([[1, 0, 0],[0, np.cos(theta), -np.sin(theta)],[0, np.sin(theta),  np.cos(theta)]])

    elif axis == "Y":
        R = np.array([[ np.cos(theta), 0, np.sin(theta)],[ 0, 1, 0],[-np.sin(theta), 0, np.cos(theta)]])

    else:  #Z
        R = np.array([[np.cos(theta), -np.sin(theta), 0],[np.sin(theta),  np.cos(theta), 0],[0, 0, 1]])

    return R

def rotate_DCM_data(data, ch: list[str], axis: str, degrees: float):

    # TODO: make this into BMECH function

    transform = R.from_matrix(matrix=
    _create_rot_matrix( axis=axis, degrees=degrees)
    )

    segs = dict.fromkeys(channel.rsplit(sep = '_', maxsplit= 1)[0] for channel in ch)

    for seg in segs:
        dcm = np.stack(arrays=[data[f'{seg}_x']['line'], data[f'{seg}_y']['line'], data[f'{seg}_z']['line']], axis=-1)
        dcm = R.from_matrix(dcm)
        rotated_dcm = dcm * transform

        data = _decompdcm(data, dcm=rotated_dcm, seg=seg)

    return data

def quats2euler_data(data: dict, prox_ch: list[str], dist_ch: list[str], sequence: str) -> dict:
    """
    Compute Euler angles of the distal segment relative to the proximal segment from quaterion data.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels for each sensor.
    prox_ch : list[str]
        Channels for the proximal segment (e.g., ``['Quat_W_LSh, 'Quat_X_LSh'...]``).
    dist_ch : list[str]
        Channels for the distal segment (e.g., ``'['Quat_W_LF, 'Quat_X_LF'...]'``).
    sequence : str
        Euler angle rotation sequence passed to
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

    if len(prox_ch) != 4:
        raise ValueError("prox_ch must have 4 elements corresponding to the W, X, Y, Z quaternion components")
    if len(dist_ch) != 4:
        raise ValueError("dist_ch must have 4 elements corresponding to the W, X, Y, Z quaternion components")

    q_prox = np.stack(arrays=[data[ch]['line'] for ch in prox_ch], axis=-1)
    q_dist = np.stack(arrays=[data[ch]['line'] for ch in dist_ch], axis=-1)

    R_prox = R.from_quat(q_prox, scalar_first=True)
    R_dist = R.from_quat(q_dist, scalar_first=True)

    R_rel = R_prox.inv() * R_dist

    data = _decomp2euler(R_rel, data, prox_ch, dist_ch, sequence)

    return data


def dcms2euler_data(data: dict, prox_ch: list[str], dist_ch: list[str], sequence: str) -> dict:
    """
    Compute joint angles from direction cosine matrices (DCMs) stored in a zoo file.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing DCM channels for the proximal and
        distal segments.
    prox_ch : list[str]
        Channel key for the proximal segment's direction cosine matrix
        (e.g., ``'Thigh'``).
    dist_ch : list[str]
        Channel key for the distal segment's direction cosine matrix
        (e.g., ``'Shank'``).
    sequence : str
        Euler angle rotation sequence passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations.

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

    if len(prox_ch) != 3:
        raise ValueError("prox_ch must have 3 elements corresponding to the X, Y, Z DCM components")
    if len(dist_ch) != 3:
        raise ValueError("dist_ch must have 3 elements corresponding to the X, Y, Z DCM components")

    R_prox_array = np.stack(arrays=[data[ch]['line'] for ch in prox_ch], axis=-1)
    R_dist_array = np.stack(arrays=[data[ch]['line'] for ch in dist_ch], axis=-1)

    R_prox = R.from_matrix(R_prox_array)
    R_dist = R.from_matrix(R_dist_array)

    R_rel = R_prox.inv() * R_dist

    data = _decomp2euler(R_rel, data, prox_ch, dist_ch, sequence)

    return data

def marker2dcm_data(data: dict, seg: str, origin: str, marker_1: str, marker_2: str)-> dict:
   # TODO: Update docstrings
    """
    Create a right-handed local coordinate system (LCS) using positional data from motion capture trajectories.

    Parameters
    ----------
    data : dict
        Dictionary containing motion capture marker data.
    origin : str
        Label of the origin marker for the segment.
    marker_1 : str
        Label of the first marker defining the primary axis (i axis).
    marker_2 : str
        Label of the second marker used to define the temporary vector for orthogonal axes.

    Returns
    -------
    x_axis : np.ndarray
        n_frames x 3 array of the X-axis (i) unit vectors over time.
    y_axis : np.ndarray
        n_frames x 3 array of the Y-axis (j) unit vectors over time.
    z_axis : np.ndarray
        n_frames x 3 array of the Z-axis (k) unit vectors over time.
    """

    # TODO: we want to get rid of resolve marker.
    origin = _resolve_marker_label(data, origin)
    marker_1 = _resolve_marker_label(data, marker_1)
    marker_2 = _resolve_marker_label(data, marker_2)

    o = np.array(data[origin]['line'])
    m1 = np.array(data[marker_1]['line'])
    m2 = np.array(data[marker_2]['line'])

    i = make_unit(m1 - o)
    j_temp = make_unit(m2 - o)
    k = make_unit(np.cross(i, j_temp))
    j = np.cross(k, i)

    dcm = np.stack((i, j, k), axis=-1)

    # Redundant in some sort - but turning it into a rotation object automatically checks
    # orthonormality before moving on...we can get rid of this if we wanted.
    dcm_mat = R.from_matrix(matrix = dcm).as_matrix()

    data = _decompdcm(data, dcm_mat, seg)

    return data

def quats2dcm_data(data:dict, seg:str, ch:str) -> dict:

    q = np.stack(arrays=[data[channel]['line'] for channel in ch], axis=-1)

    dcm = R.from_quat(q, scalar_first=True).as_matrix()

    data = _decompdcm(data, dcm, seg)

    return data
