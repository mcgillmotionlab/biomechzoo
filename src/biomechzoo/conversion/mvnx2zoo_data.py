import numpy as np
from src.biomechzoo.mvn.load_mvnx import load_mvnx
from src.biomechzoo.mvn.mvn import JOINTS, SEGMENTS

def mvnx2zoo_data(fl):
    """ loads mvnx file from xsens"""

    mvnx_file = load_mvnx(fl)

    # create zoo data dict
    data = {}

    # extract joint angle data
    for key, val in JOINTS.items():
        data[val] = {
            'line': mvnx_file.get_joint_angle(joint=key),
            'event': {}
        }

    # extract segment orientations
    # todo: add segment orientations to zoo file
    # for key, val in SEGMENTS.items():
    #     data[val] = {
    #         'line': mvnx_file.get_sensor_ori(segment=key),
    #         'event': {}
    #     }

    # get foot strike events
    RHeel = np.zeros(mvnx_file.frame_count)
    LHeel = np.zeros(mvnx_file.frame_count)

    for n in range(mvnx_file.frame_count):
        list_contact = mvnx_file.get_foot_contacts(n)
        for contact in list_contact:
            if contact['segment_index'] == 17:
                RHeel[n] = True
            elif contact['segment_index'] == 21:
                LHeel[n] = True

    hs_r = []
    hs_l = []
    for i in range(1, len(LHeel)):  # Start from 1 to avoid i-1 out-of-range
        if RHeel[i - 1] == 0 and RHeel[i] == 1:
            hs_r.append(i)
        if LHeel[i - 1] == 0 and LHeel[i] == 1:
            hs_l.append(i)

    # add to zoo
    data['jL5S1']['event'] = {}
    for i, rHS in enumerate(hs_r):
        data['jL5S1']['event']['R_FS'+str(i+1)] = [rHS, 0, 0]
    for i, lHS in enumerate(hs_l):
        data['jL5S1']['event']['L_FS' + str(i + 1)] = [lHS, 0, 0]

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
