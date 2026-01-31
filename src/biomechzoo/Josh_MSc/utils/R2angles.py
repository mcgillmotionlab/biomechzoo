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

    R_prox = R.from_matrix(
        matrix = data[prox_key]['matrix']
    )

    if rot_prox_axis is not None:

        transform = R.from_matrix(
            matrix = create_rot_matrix(
                axis = rot_prox_axis,
                degrees = rot_deg
            )
        )

        R_prox = R_prox * transform

    R_dist = R.from_matrix(
        matrix = data[dist_key]['matrix']
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

    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_key}_{dist_key}_alpha": {"line": euler[:, 0]},
        f"{prox_key}_{dist_key}_beta":  {"line": euler[:, 1]},
        f"{prox_key}_{dist_key}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data