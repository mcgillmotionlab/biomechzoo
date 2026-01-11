from scipy.spatial.transform import Rotation as R
import numpy as np
from biomechzoo.conversion.table2zoo_data import table2zoo_data
import matplotlib.pyplot as plt

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

    :param axis: 'x', 'y', or 'z'
    :param degrees: rotation angle in degrees

    :return: 3 x 3 matrix
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
            [ 0,            1, 0           ],
            [-np.sin(theta), 0, np.cos(theta)]
        ])

    else:  #Z
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0,              0,             1]
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

# TESTING
if __name__ == "__main__":

    # Defining the path to the example data
    example_path_H = "/Users/joshualowery/DataspellProjects/biomechzoo_dev/data/imu_do_not_upload/raw data/long_example/123AA_RH_header.csv"
    example_path_Sh = "/Users/joshualowery/DataspellProjects/biomechzoo_dev/data/imu_do_not_upload/raw data/long_example/123AA_RSh_header.csv"

    # Creating a dictionary with the data in it
    data_H = table2zoo_data(example_path_H, ".csv", skip_rows = 0)
    data_Sh = table2zoo_data(example_path_Sh, ".csv", skip_rows = 0)

    # Loading the quaternions from our dictionary
    data_quats_H = load_quats(data_H, prefix="")
    data_quats_Sh = load_quats(data_Sh, prefix="")

    # Verify the size of the data 4 x n
    print("Size of data (Hindfoot):",len(data_quats_H[0]),",",len(data_quats_H))
    print("Size of data (Shank):",len(data_quats_Sh[0]),",",len(data_quats_Sh))

    # Create a rotation object from our quaternions
    R_data_H = R.from_quat(data_quats_H, scalar_first=True)
    R_data_Sh = R.from_quat(data_quats_Sh, scalar_first=True)

    # Define a rotation about the x-axis
    Rx = R.from_matrix(
        matrix = create_rot_matrix(axis="X", degrees=180)
    )

    # Apply the rotation to our hindfoot direction cosine matrix
    R_data_H_rotated = (R_data_H) * Rx

    # Now we want to calculate the resulting angles to see if this actual worked

    # First, lets calculate the unrotated joint angles:
    R_joint_no_rot = (R_data_Sh).inv() * R_data_H
    euler_no_rot = R_joint_no_rot.as_euler("YZX", degrees=True)

    # Next, lets calculate the rotated equivalent
    R_joint_rot = (R_data_Sh).inv() * R_data_H_rotated
    euler_rot = R_joint_rot.as_euler("YZX", degrees=True)

    # Plot the comparison:

    labels = ["Alpha", "Beta", "Gamma"]

    plt.figure(figsize=(10, 6))

    for i in range(3):
        plt.subplot(3, 1, i + 1)
        plt.plot(euler_no_rot[:, i], label="No rotation")
        plt.plot(euler_rot[:, i], label="With frame rotation")
        plt.ylabel("Angle (deg)")
        plt.title(labels[i])
        plt.legend()

    plt.xlabel("Frame")
    plt.tight_layout()
    plt.show()



