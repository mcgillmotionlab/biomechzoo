from scipy.spatial.transform import Rotation as R
import numpy as np

def load_quats(data:dict, prefix:str) -> np.ndarray:
    """
    Returns a stacked np.ndarray containing the w, x, y, z components of a quaternion in scalar first order

    Note: the function assumes that data will have a prefix before data from different segments. For example:

    data.keys() = [LShQuat_W, LShQuat_X, ... LFQuat_W, LFQuat_X, ...]

    :param data: dict containing the sensor data
    :param prefix: the prefix defining the segment that is being loaded
    :return: stacked np.ndarray containing the w, x, y, z components of the sensor from the desired sensor
    """

    base = ["W", "X", "Y", "Z"]
    names = [f"{prefix}Quat_{c}" for c in base]
    quat_components = [data[n]['line'] for n in names]
    return np.column_stack(quat_components)

def imu_angles_data(data, prox_prefix, dist_prefix, order):
    """
    Compute Euler angles between two IMU sensors.

    :param data: dict containing the quaternions for each sensor
    :param prox_prefix: prefix defining the segment that is being loaded
    :param dist_prefix: prefix defining the segment that is being loaded
    :param order: order of the IMU sensors. Note, the case of the order changes are intrinsic or extrinsic. For more
                information please reference the scipy.spatial.transform documentation.

    :return: dict containing the Euler angles with alpha, beta, and gamma representing the first, second, and third
            rotations in the sequence, respectively. Results are in degrees.
    """

    # Load the quaternions from the desired segments
    q_prox = load_quats(data, prefix=prox_prefix)
    q_dist = load_quats(data, prefix=dist_prefix)

    # Convert to Rotation objects
    R_prox = R.from_quat(q_prox, scalar_first=True)
    R_dist = R.from_quat(q_dist, scalar_first=True)

    # Relative orientation
    R_rel = R_prox.inv() * R_dist

    # Euler angles
    euler = R_rel.as_euler(order, degrees=True)

    return {
        "alpha": {"line": euler[:, 0]},
        "beta":  {"line": euler[:, 1]},
        "gamma": {"line": euler[:, 2]},
    }