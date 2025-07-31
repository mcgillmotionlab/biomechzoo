import mvnx
import numpy as np


def mvnx2zoo_data(fl):
    """ insert kai's code"""

    mvnx_file = mvnx.load(fl)

    # create zoo data dict
    data = {}

    # Accessing joint data :
    joint_angle_data = mvnx_file.jointAngle
    joint_names = mvnx_file.joints
    for i, joint in enumerate(joint_names):
        start = i * 3
        stop = start + 3
        angles = joint_angle_data[:, start:stop]  # shape: (n_frames, 3)

        data[joint] = {
            'line': angles,
            'event': {}
        }

    # add meta information
    data['zoosystem'] = {}
    data['zoosystem']['Video'] = {}
    data['zoosystem']['Video']['Freq'] = np.int(mvnx_file.frameRate)
    return data


if __name__ == '__main__':
    """ testing """
    import os
    from biomechzoo.utils.zplot import zplot
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'Flat-001.mvnx')
    data = mvnx2zoo_data(fl)
    zplot(data, 'jRightKnee')
