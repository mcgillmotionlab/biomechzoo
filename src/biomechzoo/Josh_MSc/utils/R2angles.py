import inspect
import os
import time
import numpy as np
from scipy.spatial.transform import Rotation as R

from biomechzoo.imu.kinematics import load_quats
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp
from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo.imu.kinematics import imu_angles_data

# KEY CONVENTION:
    # all forms of data should have the following keys [LSh_R, LH_R, LF_R, LT_R] representing the DCMs for each seg.

def R2angles_data(data:dict, prox_key:str, dist_key:str, order:str) -> dict:
    """
    """

    # Load the quaternions from the proximal and distal segments
    R_prox = R.from_matrix(matrix = data[prox_key]['matrix'])
    R_dist = R.from_matrix(matrix = data[dist_key]['matrix'])

    # Derive relative orientation
    R_rel = R_prox.inv() * R_dist

    # Convert to Euler angles using defined rotation order
    euler = R_rel.as_euler(order, degrees=True)

    angles = {
        f"{prox_key}_{dist_key}_alpha": {"line": euler[:, 0]},
        f"{prox_key}_{dist_key}_beta":  {"line": euler[:, 1]},
        f"{prox_key}_{dist_key}_gamma": {"line": euler[:, 2]},
    }

    data.update(angles)

    return data