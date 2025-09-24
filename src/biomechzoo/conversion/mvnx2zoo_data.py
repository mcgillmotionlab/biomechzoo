import numpy as np
from biomechzoo.mvn.load_mvnx import load_mvnx


def mvnx2zoo_data(fl):
    """ loads mvnx file from xsens"""
    #todo: needs to be updated for the new version of mvnx direcly loaded in biomechzoo
    mvnx_file = load_mvnx(fl)

    # create zoo data dict
    data = {}

    # Accessing joint data :
    joint_angle_data = mvnx_file.get_joint_angle()
    joint_names = mvnx_file.joints
    for i, joint in enumerate(joint_names):
        start = i * 3
        stop = start + 3
        angles = joint_angle_data[:, start:stop]  # shape: (n_frames, 3)

        data[joint] = {
            'line': angles,
            'event': {}
        }
    # get foot strike events
    # Index 0: Left Heel contact (1 for contact, 0 for no contact)
    # Index 1: Left Toe contact (1 for contact, 0 for no contact)
    # Index 2: Right Heel contact (1 for contact, 0 for no contact)
    # Index 3: Right Toe contact (1 for contact, 0 for no contact)
    left_heel_contacts = np.array(mvnx_file.footContacts[:, 0])
    right_heel_contacts = np.array(mvnx_file.footContacts[:, 2])

    # Detect transitions from no contact (0) to contact (1)
    left_contact_start = (left_heel_contacts[:-1] == 0) & (left_heel_contacts[1:] == 1)
    right_contact_start = (right_heel_contacts[:-1] == 0) & (right_heel_contacts[1:] == 1)

    # Get indices where these transitions occur (add 1 because we're checking between frames)
    left_contact_frames = np.where(left_contact_start)[0] + 1
    right_contact_frames = np.where(right_contact_start)[0] + 1

    # add to zoo
    data['jL5S1']['event'] = {}
    for i, right_contact_frame in enumerate(right_contact_frames):
        data['jL5S1']['event']['R_FS'+str(i+1)] = [right_contact_frame, 0, 0]
    for i, left_contact_frame in enumerate(left_contact_frames):
        data['jL5S1']['event']['L_FS' + str(i + 1)] = [left_contact_frame, 0, 0]

    # add meta information
    # todo: add more, see mvnx_file object
    data['zoosystem'] = {}
    data['zoosystem']['Video'] = {}
    data['zoosystem']['Video']['Freq'] = int(mvnx_file.frame_rate)
    data['zoosystem']['Version'] = mvnx_file.version
    data['zoosystem']['configuration'] = mvnx_file.configuration
    data['zoosystem']['recording_date'] = mvnx_file.recording_date
    data['zoosystem']['original_file_name'] = mvnx_file.original_file_name
    data['zoosystem']['frame_count'] = mvnx_file.frame_count
    data['zoosystem']['comments'] = mvnx_file.comments

    return data


if __name__ == '__main__':
    """ testing """
    import os
    from src.biomechzoo.utils.zplot import zplot
    # -------TESTING--------
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fl = os.path.join(project_root, 'data', 'other', 'Flat-001.mvnx')
    data = mvnx2zoo_data(fl)
    zplot(data, 'jRightKnee')
