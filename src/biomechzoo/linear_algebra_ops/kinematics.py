import numpy as np
from scipy.spatial.transform import Rotation as R
from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.linear_algebra_ops.make_unit import make_unit

def _resolve_marker_label(data: dict, marker: str) -> str:

    """
    Resolve a marker label to the key that exists in the zoo data dictionary.

    Handles differing naming conventions by trying abbreviated and full
    lateral prefixes interchangeably (e.g., ``'LShank1'`` and
    ``'LeftShank1'`` are treated as equivalent).

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing marker channels.
    marker : str
        Marker label to resolve. Accepted formats include full lateral prefix
        (e.g., ``'LeftShank1'``, ``'RightHeel2'``) or abbreviated prefix
        (e.g., ``'LShank1'``, ``'RHeel2'``).

    Returns
    -------
    str
        The matching key as it exists in ``data``.

    Raises
    ------
    KeyError
        If no matching key can be found in ``data`` after trying all
        naming convention variants.
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

    raise KeyError(f"Trajectory '{marker}' not found. Available markers: {marker_keys}")

def _decomp2euler(R_rel, data:dict, prox_ch: list[str], dist_ch: list[str], sequence: str)-> dict:

    """
    Decompose a relative DCM into Euler angles and store them in a zoo
    data dictionary.

    Parameters
    ----------
    R_rel : scipy.spatial.transform.Rotation
        Relative rotation object representing the distal segment's orientation
        with respect to the proximal segment.
    data : dict
        Zoo data dictionary to store the Euler angle channels in.
    prox_ch : list[str]
        Channel names for the proximal segment. The segment label is extracted
        from the last ``'_'``-delimited token of the first channel name
        (e.g., ``'i_LSh'`` yields ``'LSh'``).
    dist_ch : list[str]
        Channel names for the distal segment. Same label extraction convention
        as ``prox_ch``.
    sequence : str
        Euler angle rotation sequence passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations
        (e.g., ``'ZXY'`` for intrinsic, ``'zxy'`` for extrinsic).

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'<prox>_<dist>_alpha'``, ``'<prox>_<dist>_beta'``,
        and ``'<prox>_<dist>_gamma'``, containing the first, second,
        and third Euler angles (in degrees) respectively.
    """
    euler = R_rel.as_euler(sequence, degrees=True)

    # Convention for finding labels assumes that bmech.combine_files is being used for combining
    # (i.e., the line data for each quaternion components contains the segment as a suffix divided by '_').
    prox_label = prox_ch[0].rsplit('_', maxsplit=1)[-1]
    dist_label = dist_ch[0].rsplit('_', maxsplit=1)[-1]

    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_alpha'), ch_new_data= euler[:,0])
    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_beta'), ch_new_data= euler[:,1])
    data = addchannel_data(data=data, ch_new_name=(f'{prox_label}_{dist_label}_gamma'), ch_new_data= euler[:,2])

    return data

def _explodedcm(data:dict, dcm:np.ndarray, seg:str)-> dict:

    """
     Store the column vectors of a direction cosine matrix (DCM) as separate
     channels in a zoo data dictionary.

     Parameters
     ----------
     data : dict
         Zoo data dictionary to store the DCM column vectors in.
     dcm : np.ndarray
         Array of shape (N, 3, 3) containing the DCM for each frame.
     seg : str
         Segment label used to name the output channels
         (e.g., ``'LSh'`` produces ``'i_LSh'``, ``'j_LSh'``, ``'k_LSh'``).

     Returns
     -------
     dict
         The input ``data`` dictionary updated with three new channels:
         ``'i_<seg>'``, ``'j_<seg>'``, and ``'k_<seg>'``, containing the
         first, second, and third column vectors of the DCM respectively.
     """

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

def rotate_dcm_data(data: dict, ch: list[str], axis: str, degrees: float)-> dict:

    """
    Apply a rotation about a principal axis to one segment's DCM.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing DCM channels for the segment
        to be rotated.
    ch : list[str]
        List of 3 channel names identifying the DCM to rotate, ordered
        i, j, k (e.g., ``['i_LSh', 'j_LSh', 'k_LSh']``).
    axis : {'X', 'Y', 'Z'}
        Principal axis to rotate about (case-insensitive).
    degrees : float
        Rotation angle in degrees.

    Returns
    -------
    dict
        The input ``data`` dictionary with the DCM channels updated in place
        to reflect the applied rotation.

    Raises
    ------
    ValueError
        If ``ch`` does not have exactly 3 elements, if all channels do not
        belong to the same segment, or if ``axis`` is not ``'X'``, ``'Y'``,
        or ``'Z'``.
    """

    if len(ch) != 3:
        raise ValueError("ch must have exactly 3 elements: [i_seg, j_seg, k_seg].")

    segs = {channel.rsplit("_", maxsplit=1)[-1] for channel in ch}

    if len(segs) != 1:
        raise ValueError(
            f"All channels must belong to the same segment. Got segments: {segs}"
        )

    seg = segs.pop()

    dcm = np.stack(arrays=[data[f"i_{seg}"]["line"], data[f"j_{seg}"]["line"], data[f"k_{seg}"]["line"]], axis=-1)
    transform = _create_rot_matrix(axis=axis, degrees=degrees)
    rotated_dcm = dcm @ transform

    data = _explodedcm(data, rotated_dcm, seg)

    return data

def quats2euler_data(data: dict, prox_ch: list[str], dist_ch: list[str], sequence: str) -> dict:

    """
    Compute Euler angles of the distal segment relative to the proximal segment
    from quaternion data stored in a zoo data dictionary.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels for the proximal and
        distal segments.
    prox_ch : list[str]
        List of 4 channel names for the proximal segment's quaternion components,
        ordered W, X, Y, Z (e.g., ``['Quat_W_LSh', 'Quat_X_LSh', 'Quat_Y_LSh', 'Quat_Z_LSh']``).
    dist_ch : list[str]
        List of 4 channel names for the distal segment's quaternion components,
        ordered W, X, Y, Z (e.g., ``['Quat_W_LH', 'Quat_X_LH', 'Quat_Y_LH', 'Quat_Z_LH']``).
    sequence : str
        Euler angle rotation sequence passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations
        (e.g., ``'ZXY'`` for intrinsic, ``'zxy'`` for extrinsic).

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'<prox>_<dist>_alpha'``, ``'<prox>_<dist>_beta'``,
        and ``'<prox>_<dist>_gamma'``, containing the first, second,
        and third Euler angles (in degrees) respectively, where ``<prox>``
        and ``<dist>`` are the segment labels extracted from ``prox_ch``
        and ``dist_ch``.

    Raises
    ------
    ValueError
        If ``prox_ch`` or ``dist_ch`` do not have exactly 4 elements.

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
    Compute Euler angles of the distal segment relative to the proximal segment
    from direction cosine matrices (DCMs) stored in a zoo data dictionary.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing DCM channels for the proximal and
        distal segments.
    prox_ch : list[str]
        List of 3 channel names for the proximal segment's DCM column vectors,
        ordered i, j, k (e.g., ``['i_LSh', 'j_LSh', 'k_LSh']``).
    dist_ch : list[str]
        List of 3 channel names for the distal segment's DCM column vectors,
        ordered i, j, k (e.g., ``['i_LH', 'j_LH', 'k_LH']``).
    sequence : str
        Euler angle rotation sequence passed to
        :meth:`scipy.spatial.transform.Rotation.as_euler`. Case determines
        intrinsic (uppercase) vs extrinsic (lowercase) rotations
        (e.g., ``'ZXY'`` for intrinsic, ``'zxy'`` for extrinsic).

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'<prox>_<dist>_alpha'``, ``'<prox>_<dist>_beta'``,
        and ``'<prox>_<dist>_gamma'``, containing the first, second,
        and third Euler angles (in degrees) respectively, where ``<prox>``
        and ``<dist>`` are the segment labels extracted from ``prox_ch``
        and ``dist_ch``.

    Raises
    ------
    ValueError
        If ``prox_ch`` or ``dist_ch`` do not have exactly 3 elements.

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

    """
    Compute a right-handed local coordinate system (LCS) from motion capture marker positions
    and store it as a direction cosine matrix (DCM) in the zoo data dictionary.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing motion capture marker channels.
    seg : str
        Segment label used to name the output DCM channels
        (e.g., ``'LSh'`` produces ``'i_LSh'``, ``'j_LSh'``, ``'k_LSh'``).
    origin : str
        Label of the marker defining the origin of the local coordinate system.
        Supports both full (e.g., ``'LeftShank1'``) and abbreviated
        (e.g., ``'LShank1'``) naming conventions.
    marker_1 : str
        Label of the marker defining the primary axis (i). Same naming
        conventions as ``origin``.
    marker_2 : str
        Label of the marker used to define the temporary vector for
        computing the orthogonal axes via cross product. Same naming
        conventions as ``origin``.

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'i_<seg>'``, ``'j_<seg>'``, and ``'k_<seg>'``, containing the
        first, second, and third column vectors of the DCM respectively.

    Notes
    -----
    The LCS is constructed as follows:

    - ``i`` = unit vector from ``origin`` to ``marker_1``
    - ``j_temp`` = unit vector from ``origin`` to ``marker_2``
    - ``k`` = unit vector of ``i`` × ``j_temp``
    - ``j`` = ``k`` × ``i``

    Orthonormality is verified by passing the resulting matrix through
    :class:`scipy.spatial.transform.Rotation` before storing.
    """

    o = np.array(data[_resolve_marker_label(data, origin)]['line'])
    m1 = np.array(data[_resolve_marker_label(data, marker_1)]['line'])
    m2 = np.array(data[_resolve_marker_label(data, marker_2)]['line'])

    i = make_unit(m1 - o)
    j_temp = make_unit(m2 - o)
    k = make_unit(np.cross(i, j_temp))
    j = np.cross(k, i)

    dcm = np.stack((i, j, k), axis=-1)

    assert np.allclose(np.linalg.det(dcm), 1.0, atol=1e-6), f"DCM is not orthonormal- det = {np.linalg.det(dcm)}."

    data = _explodedcm(data, dcm, seg)

    return data

def quats2dcm_data(data:dict, seg:str, ch:list[str]) -> dict:

    """
    Compute a direction cosine matrix (DCM) from quaternion data and store it in the zoo data dictionary.

    Parameters
    ----------
    data : dict
        Zoo data dictionary containing quaternion channels for the segment.
    seg : str
        Segment label used to name the output DCM channels
        (e.g., ``'LSh'`` produces ``'i_LSh'``, ``'j_LSh'``, ``'k_LSh'``).
    ch : list[str]
        List of 4 quaternion channel names ordered W, X, Y, Z
        (e.g., ``['Quat_W_LSh', 'Quat_X_LSh', 'Quat_Y_LSh', 'Quat_Z_LSh']``).

    Returns
    -------
    dict
        The input ``data`` dictionary updated with three new channels:
        ``'i_<seg>'``, ``'j_<seg>'``, and ``'k_<seg>'``, containing the
        first, second, and third column vectors of the DCM respectively.

    Raises
    ------
    ValueError
        If ``ch`` does not have exactly 4 elements.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
    """

    if len(ch) != 4:
        raise ValueError("ch must have 4 elements corresponding to the W, X, Y, Z quaternion components")

    q = np.stack(arrays=[data[channel]['line'] for channel in ch], axis=-1)

    dcm = R.from_quat(quat=q, scalar_first=True).as_matrix()

    data = _explodedcm(data, dcm, seg)

    return data
