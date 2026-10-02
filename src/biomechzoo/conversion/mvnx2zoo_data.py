from typing import Any, Dict

import numpy as np

from biomechzoo.mvn.load_mvnx import load_mvnx
from biomechzoo.mvn.mvn import JOINTS, SEGMENTS
from biomechzoo.mvn.mvnx_file_accessor import MvnxFileAccessor
from biomechzoo.utils.set_zoosystem import set_zoosystem


def mvnx2zoo_data(fl: str) -> Dict:
    """
    Convert an Xsens .mvnx file to zoo format.

    Parameters
    ----------
    fl : str
        Path to the .mvnx file.

    Returns
    -------
    data : dict
        Zoo dictionary with joint angle and segment orientation
        channels, foot strike events, and 'zoosystem' metadata.
    """

    mvnx_file = load_mvnx(fl)

    # create zoo data dict
    data = {'zoosystem': set_zoosystem()}
    # extract joint angle data (All JOINTS may not exist in a given dataset)
    for key, val in JOINTS.items():
        try:
            r = mvnx_file.get_joint_angle(joint=key)
            data[val] = {
                'line': np.array(r),
                'event': {}
            }
            data['zoosystem']['Video']['Channels'].append(val)

        except KeyError:
            print('joint {} does not exist, skipping'.format(val))

    # extract segment orientations (All SEGMENTS may not exist in a given dataset)
    for key, val in SEGMENTS.items():
        try:
            r = mvnx_file.get_sensor_ori(segment=key)

            data[val] = {
                'line': np.array(r),
                'event': {}
            }
            data['zoosystem']['Video']['Channels'].append(val)

        except KeyError:
            print('segment {} does not exist, skipping'.format(val))

    # get foot strike events
    data = _get_foot_strike_events(mvnx_file, data)

    # add meta information
    data = _get_meta_info(fl, mvnx_file, data)

    return data


def is_valid_for_zoo(val: Any) -> bool:
    """
    Check whether a value is valid for a MATLAB-compatible zoo structure.

    Parameters
    ----------
    val : Any
        Value to check.

    Returns
    -------
    valid : bool
        True if the value is valid for a MATLAB-compatible zoo
        structure (i.e. not None and not an empty list/array).
    """
    if val is None:
        return False
    if isinstance(val, list) and len(val) == 0:
        return False
    if isinstance(val, np.ndarray) and val.size == 0:
        return False
    return True


def _get_meta_info(
        fl: str, mvnx_file: MvnxFileAccessor, data: Dict,
) -> Dict:
    """
    Add mvnx metadata to the 'zoosystem' branch of zoo data.

    Parameters
    ----------
    fl : str
        Path to the source .mvnx file. Unused; reserved for future
        metadata that requires the original file path.
    mvnx_file : MvnxFileAccessor
        Parsed mvnx file accessor.
    data : dict
        Zoo data dictionary to update.

    Returns
    -------
    data : dict
        Zoo data dictionary with mvnx metadata added to 'zoosystem'.
    """
    # todo: add more, see mvnx_file object
    data['zoosystem']['Video']['Freq'] = int(mvnx_file.frame_rate)
    data['zoosystem']['mvnx_version'] = mvnx_file.version
    data['zoosystem']['mvnx_configuration'] = mvnx_file.configuration
    data['zoosystem']['recording_date'] = mvnx_file.recording_date
    data['zoosystem']['original_file_name'] = mvnx_file.original_file_name
    data['zoosystem']['frame_count'] = mvnx_file.frame_count
    return data


def _get_foot_strike_events(
        mvnx_file: MvnxFileAccessor, data: Dict,
) -> Dict:
    """
    Detect right/left heel-strike frames and add them as events.

    Parameters
    ----------
    mvnx_file : MvnxFileAccessor
        Parsed mvnx file accessor.
    data : dict
        Zoo data dictionary to update.

    Returns
    -------
    data : dict
        Zoo data dictionary with 'R_FS<n>'/'L_FS<n>' foot-strike
        events added to one channel's 'event' branch.
    """
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

    # add to event branch of any channel
    if 'jL5S1' in data:
        ch = 'jL5S1'
    else:
        ch = next(iter(data))

    if hs_r:
        for i, rHS in enumerate(hs_r):
            data[ch]['event']['R_FS' + str(i + 1)] = [rHS, 0, 0]
    if hs_l:
        for i, lHS in enumerate(hs_l):
            data[ch]['event']['L_FS' + str(i + 1)] = [lHS, 0, 0]

    return data


if __name__ == '__main__':
    """ testing """
    import os
    from biomechzoo.processing.split_trial_data import split_trial_data
    # -------TESTING--------
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fl = os.path.join(project_root, 'data', 'other', 'Flat001.mvnx')
    fl_zoo = fl.replace('.mvnx', '.zoo')
    data = mvnx2zoo_data(fl)
