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