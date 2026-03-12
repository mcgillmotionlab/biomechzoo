from scipy.spatial.transform import Rotation as R
import numpy as np

def load_quats(data:dict, prefix:str) -> np.ndarray:
    """
    Returns a stacked np.ndarray containing the w, x, y, z components of a quaternion in scalar first order.

    Note:           the function assumes that data will have a prefix before quaternions from different segments.
                    For example:

                    data.keys() = [LSh_Quat_W, LSh_Quat_X, ... LF_Quat_W, LF_Quat_X, ...]

                    load_quats(data, prefix='LF_') -> returns LF_Quat_W, LF_Quat_X, LF_Quat_Y, LF_Quat_Z

    :param data:    dict containing the sensor data
    :param prefix:  the prefix defining the segment that is being loaded
    :return:        stacked np.ndarray containing the w, x, y, z components of the sensor from the desired sensor
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

def imu_angles_data(data:dict, prox_prefix:str, dist_prefix:str, order:str) -> dict:
    """
    Compute Euler angles describing the orientation of the distal segment with respect to the proximal segment.

    :param data:            dict containing the quaternions for each sensor
    :param prox_prefix:     prefix defining the proximal segment
    :param dist_prefix:     prefix defining the distal segment
    :param order:           order of the IMU sensors. Note, the case of the order changes between intrinsic or extrinsic rotations.
                            For more information please reference the scipy.spatial.transform documentation:
                            https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html

    :return:                dict containing the Euler angles with alpha, beta, and gamma representing the first, second,
                            and third rotations in the sequence, respectively. Results are in degrees.
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

from scipy.spatial.transform import Rotation as R
from biomechzoo.imu.kinematics import create_rot_matrix

def R2angles_data(data:dict, prox_key:str, dist_key:str, order:str, rot_prox_axis:str = None,
                  rot_dist_axis:str = None, rot_deg:float = None) -> dict:
    """
    Determines joint angles given a direction cosine matrix and a rotation order.

    :param data:            .zoo file containing the direction cosine matrix representing the orientations of the
                            proximal and distal segments with respect to a global reference frame.
    :param prox_key:        The key distinguishing the proximal segment's direction cosine matrix.
    :param dist_key:        The key distinguishing the distal segment's direction cosine matrix.
    :param order:           The rotation order to be used. Note that case determines if this rotation in intrinsic
                            or extrinsic. For more information, please refer to scipy.spatial.transform.Rotation docs:
                            https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html
    :param rot_prox_axis:   Optional. Determines if one of the segment's proximal local coordinate systems is to be
                            rotated before the calculation of joint angles. If this rotation is desired, the user must
                            input the axis they desire to rotate about (i.e., either "X", "Y" or "Z". For more
                            information, please refer to the 'create_rot_matrix' function.
    :param rot_dist_axis:   Optional. Determines if one of the segment's distal local coordinate systems is to be
                            rotated before the calculation of joint angles. If this rotation is desired, the user must
                            input the axis they desire to rotate about (i.e., either "X", "Y" or "Z". For more
                            information, please refer to the 'create_rot_matrix' function.
    :param rot_deg:         Optional. If either 'rot_prox_axis' or 'rot_dist_axis' are specified, this argument will
                            determine the magnitude of the rotation of the coordinate system (in degrees)

    :return:                The .zoo file will be returned with the addition of the joint angles added. The dictionary
                            specifies the joint angle data through its keys containing the proximal and distal segment,
                            as well as 'alpha', 'beta', and 'gamma', specifying the first, second, and third rotations
                            in the 'order' argument, respectively.
    """

    if 'matrix' in data[prox_key]:
        R_prox = R.from_matrix(
            matrix = data[prox_key]['matrix']
        )
    else:
        R_prox = R.from_matrix(
            matrix = data[prox_key]['line']
        )

    if rot_prox_axis is not None:

        transform = R.from_matrix(
            matrix = create_rot_matrix(
                axis = rot_prox_axis,
                degrees = rot_deg
            )
        )

        R_prox = R_prox * transform

    if 'matrix' in data[dist_key]:
        R_dist = R.from_matrix(
            matrix = data[dist_key]['matrix']
        )
    else:
        R_dist = R.from_matrix(
            matrix = data[dist_key]['line']
        )


    if rot_dist_axis is not None:
        transform = R.from_matrix(
            matrix = create_rot_matrix(
                axis=rot_dist_axis,
                degrees=rot_deg
            )
        )

        R_dist = R_dist * transform

    R_rel = R_prox.inv() * R_dist

    DCM = {
        f"{prox_key}_{dist_key}_R": {'matrix': R.as_matrix(R_rel)},
    }

    data.update(DCM)

    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_key}_{dist_key}_alpha": {"line": euler[:, 0]},
        f"{prox_key}_{dist_key}_beta":  {"line": euler[:, 1]},
        f"{prox_key}_{dist_key}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data