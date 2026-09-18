"""
Script to load an mvnx

"""

import collections
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Tuple

import numpy as np

from biomechzoo.mvn.mvnx_file_accessor import MvnxFileAccessor
from biomechzoo.mvn import mvn

# Xml namespace for mvnx files
ns = {'mvn': 'http://www.xsens.com/mvn/mvnx'}

# Map for easier conversion of foot contacts
FOOT_CONTACT_MAP = {'LeftFoot_Heel': {'type': 1, 'segment_index': mvn.SEGMENT_LEFT_FOOT, 'point_index': 2},
                    'LeftFoot_Toe': {'type': 1, 'segment_index': mvn.SEGMENT_LEFT_TOE, 'point_index': 1},
                    'RightFoot_Heel': {'type': 1, 'segment_index': mvn.SEGMENT_RIGHT_FOOT, 'point_index': 2},
                    'RightFoot_Toe': {'type': 1, 'segment_index': mvn.SEGMENT_RIGHT_TOE, 'point_index': 1}}


def load_mvnx(file_name: str) -> MvnxFileAccessor:
    """
    Open and read a file as an mvnx-formatted XML file.

    Parameters
    ----------
    file_name : str
        Path to the file to open, must have a .mvnx extension.

    Returns
    -------
    mvnx_file : MvnxFileAccessor
        Accessor wrapping the parsed data from the mvnx file.
    """

    mvnx_file = MvnxFileAccessor()
    init_file_data(mvnx_file)
    tree = ET.parse(file_name)
    root = tree.getroot()

    # Get the version
    mvnx_file.file_data['meta_data']['version'] = root.get('version')

    # Find the comment element
    comment_element = root.find('mvn:comment', ns)
    if comment_element is not None:
        mvnx_file.file_data['meta_data']['comments'] = comment_element.text

    # Find the subject element
    subject_element = root.find('mvn:subject', ns)
    mvnx_file.file_data['meta_data']['name'] = subject_element.get('label')
    mvnx_file.file_data['meta_data']['color'] = subject_element.get('torsoColor')
    mvnx_file.file_data['meta_data']['sample_rate'] = subject_element.get('frameRate')
    mvnx_file.file_data['meta_data']['rec_date'] = subject_element.get('recDate')
    mvnx_file.file_data['meta_data']['original_filename'] = subject_element.get('originalFilename')
    mvnx_file.file_data['meta_data']['configuration'] = subject_element.get('configuration')
    mvnx_file.file_data['meta_data']['scenario'] = subject_element.get('userScenario')
    mvnx_file.file_data['meta_data']['quality'] = subject_element.get('processingQuality')

    # Parse the segments and their points
    segments_element = subject_element.find('mvn:segments', ns)
    segment_elements = segments_element.findall('mvn:segment', ns)
    mvnx_file.file_data['segments'] = parse_segments(segment_elements)
    mvnx_file.create_index_to_segment_dict()  # for later convenience on retrieving segment names

    # Parse sensor information
    sensors_element = subject_element.find('mvn:sensors', ns)
    if sensors_element is not None:
        mvnx_file.file_data['sensors'] = parse_sensor(sensors_element, mvnx_file.file_data['segments']['names'])

    # Parse joint information
    joints_element = subject_element.find('mvn:joints', ns)
    if joints_element is not None:
        mvnx_file.file_data['joints'] = parse_joints(joints_element, mvnx_file.file_data['segments'])

    # Parse ergo joint information
    ergo_joints_element = subject_element.find('mvn:ergonomicJointAngles', ns)
    if ergo_joints_element is not None:
        mvnx_file.file_data['ergo_joints'] = parse_ergo_joints(ergo_joints_element)

    # Parse foot contact
    foot_contact_definitions_element = subject_element.find('mvn:footContactDefinition', ns)
    if foot_contact_definitions_element is not None:
        foot_contact_definition_elements = foot_contact_definitions_element.findall('mvn:contactDefinition', ns)
        for foot_contact_definition_element in foot_contact_definition_elements:
            contact_label = foot_contact_definition_element.get('label')
            contact_index = int(foot_contact_definition_element.get('index'))
            mvnx_file.file_data['foot_contact_def'][contact_index] = FOOT_CONTACT_MAP[contact_label]

    # Parse the finger segments and their points
    for side in mvnx_file.file_data['finger_segments']['elements']:
        finger_segment_elements = subject_element.find('mvn:fingerTrackingSegments' + side.capitalize(), ns)
        if finger_segment_elements is not None:
            finger_segments = parse_segments(finger_segment_elements)
            mvnx_file.file_data['finger_segments']['elements'][side] = finger_segments['elements']
            mvnx_file.file_data['finger_segments']['names'][side] = finger_segments['names']

    # Parse finger joint information
    for side in mvnx_file.file_data['finger_joints']['elements']:
        finger_joints_element = subject_element.find('mvn:fingerTrackingJoints' + side.capitalize(), ns)
        if finger_joints_element is not None:
            finger_segments = {'names': mvnx_file.file_data['finger_segments']['names'][side],
                               'elements': mvnx_file.file_data['finger_segments']['elements'][side]}
            finger_joints = parse_joints(finger_joints_element, finger_segments)
            mvnx_file.file_data['finger_joints']['elements'][side] = finger_joints['elements']
            mvnx_file.file_data['finger_joints']['names'][side] = finger_joints['names']

    # At last, parse the actual frames
    frames_element = subject_element.find('mvn:frames', ns)
    mvnx_file.file_data['frames'], mvnx_file.file_data['tpose'],\
        mvnx_file.file_data['tpose_isb'], mvnx_file.file_data['identity'] = parse_frames(frames_element, mvnx_file)

    mvnx_file.reset_frame_window()  # Reset window so frame count displays total frame count
    return mvnx_file


def parse_sensor(
        sensors_element: ET.Element, segment_names: List[str],
) -> Dict[str, Any]:
    """
    Parse the sensors element.

    Parameters
    ----------
    sensors_element : xml.etree.ElementTree.Element
        The sensors element to parse.
    segment_names : list of str
        Segment names, used to resolve each sensor's location.

    Returns
    -------
    result : dict
        Keys 'names' (list of str) and 'elements' (dict of str to
        dict) -- sensor data indexed by sensor name, and a list of
        sensor names.
    """
    sensor_elements = sensors_element.findall('mvn:sensor', ns)
    sensor_number = 0
    sensors = {}
    sensor_names = []
    for sensor_element in sensor_elements:
        sensor_name = sensor_element.get('label')
        sensor_names.append(sensor_name)
        sensor = {'type': 'Sensor',
                  'label': sensor_name,
                  'info': {
                      'sensor_number': sensor_number,
                      'sensor_location': segment_names.index(sensor_name) + 1}}

        sensors[sensor_name] = sensor
        sensor_number += 1

    result = {'names': sensor_names, 'elements': sensors}

    return result


def parse_joints(
        joints_element: ET.Element, segments: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Parse the joints element.

    Parameters
    ----------
    joints_element : xml.etree.ElementTree.Element
        The joints element to parse.
    segments : dict
        Segment data, as returned by :func:`parse_segments`.

    Returns
    -------
    result : dict
        Keys 'names' (list of str) and 'elements' (list of dict) --
        joint data, and a list of joint names.
    """
    joint_elements = joints_element.findall('mvn:joint', ns)

    joints = []
    joint_names = []

    for joint_element in joint_elements:
        joint = {'label': joint_element.get('label')}
        joint_names.append(joint['label'])

        segment1_index, point1_index = get_connector_indices(joint_element, 'mvn:connector1', segments)
        segment2_index, point2_index = get_connector_indices(joint_element, 'mvn:connector2', segments)
        joint['seg_points'] = np.array([[segment1_index, point1_index], [segment2_index, point2_index]])
        joints.append(joint)

    result = {'names': joint_names, 'elements': joints}

    return result


def parse_ergo_joints(ergo_joints_element: ET.Element) -> Dict[str, Any]:
    """
    Parse the ergonomic joint angles element.

    Parameters
    ----------
    ergo_joints_element : xml.etree.ElementTree.Element
        The ergonomic joint angles element to parse.

    Returns
    -------
    result : dict
        Keys 'names' (list of str) and 'elements' (list of dict) --
        ergo joint data, and a list of ergo joint names.
    """
    ergo_joint_elements = ergo_joints_element.findall('mvn:ergonomicJointAngle', ns)

    ergo_joints = []
    ergo_joint_names = []
    for ergo_joint_index in range(len(ergo_joint_elements)):
        ergo_joint_element = ergo_joint_elements[ergo_joint_index]
        ergo_joint = {'label': ergo_joint_element.get('label'),
                      'index': ergo_joint_index,
                      'parent_segment': ergo_joint_element.get('parentSegment'),
                      'child_segment': ergo_joint_element.get('childSegment')}
        ergo_joint_names.append(ergo_joint['label'])
        ergo_joints.append(ergo_joint)

    result = {'names': ergo_joint_names, 'elements': ergo_joints}

    return result


def parse_segments(segment_elements: List[ET.Element]) -> Dict[str, Any]:
    """
    Parse a list of segment elements.

    Parameters
    ----------
    segment_elements : list of xml.etree.ElementTree.Element
        The segment elements to parse.

    Returns
    -------
    result : dict
        Keys 'names' (list of str) and 'elements'
        (collections.OrderedDict) -- a list of segment names, and
        segment data indexed by segment name.
    """
    segments = collections.OrderedDict()
    segment_names = []

    for segment_index in range(len(segment_elements)):
        segment_element = segment_elements[segment_index]
        segment_name = segment_element.get('label')
        segment_names.append(segment_name)
        segment = {'points_mvn': collections.OrderedDict(),
                   'type': 'Segment',
                   'info': {},
                   'label': segment_name}

        info = {'segment_number': segment_index,
                'point_label_from_index': {},
                'point_origin': '',
                'adjacent_joints': []}

        points_element = segment_element.find('mvn:points', ns)
        point_elements = points_element.findall('mvn:point', ns)

        point_labels_from_index = {}
        for point_index in range(len(point_elements)):
            point_element = point_elements[point_index]

            point_name = point_element.get('label')
            point_labels_from_index[point_index] = point_name

            pos_b = point_element.find('mvn:pos_b', ns)
            segment['points_mvn'][point_name] = np.array([float(pos) for pos in pos_b.text.split(' ')])

            # if the point offset is really small, consider it the origin (could just pick 1st or all 0's as well)
            if np.sqrt(np.sum([sq * sq for sq in segment['points_mvn'][point_name]])) < 0.00001:
                info['point_origin'] = point_name

            # wild guess...
            if point_name[0] == 'j':
                info['adjacent_joints'].append(point_name)

        info['point_label_from_index'] = point_labels_from_index
        segment['info'] = info
        segments[segment_name] = segment

    result = {'names': segment_names, 'elements': segments}

    return result


def get_connector_indices(
        joint_element: ET.Element, connector: str, segments: Dict[str, Any],
) -> Tuple[int, int]:
    """
    Resolve a joint connector to its segment and point indices.

    Parameters
    ----------
    joint_element : xml.etree.ElementTree.Element
        The joint element containing the connector.
    connector : str
        Name of the connector sub-element (e.g. 'mvn:connector1').
    segments : dict
        Segment data, as returned by :func:`parse_segments`.

    Returns
    -------
    segment_index : int
        Index of the connected segment.
    point_index : int
        Index of the connected point on that segment, or -1 if not
        found.
    """
    connector_element = joint_element.find(connector, ns)
    tokens = connector_element.text.split('/')
    segment_index = segments['names'].index(tokens[0])
    point_index = -1
    for key, value in segments['elements'][tokens[0]]['info']['point_label_from_index'].items():
        if value == tokens[1]:
            point_index = key
            break

    return segment_index, point_index


def parse_frames(
        frames_element: ET.Element, mvnx_file: MvnxFileAccessor,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Parse the frames element.

    Parameters
    ----------
    frames_element : xml.etree.ElementTree.Element
        The frames element to parse.
    mvnx_file : MvnxFileAccessor
        Accessor whose ``file_data`` holds the segment/joint/sensor
        names already parsed from earlier in the file.

    Returns
    -------
    frames : dict
        Per-frame time series data for segments, joints, sensors,
        contacts, and finger tracking.
    tpose : dict
        T-pose frame data.
    tpose_isb : dict
        ISB-convention T-pose frame data.
    identity : dict
        Identity-pose frame data.
    """
    frames = {'time': [],
              'segment_data': [],
              'sensor_data': [],
              'joint_data': [],
              'joint_data_xzy': [],
              'ergo_joint_data': [],
              'ergo_joint_data_xzy': [],
              'contacts_data': [],
              'finger_segment_data': [],
              'finger_joint_data': {'left': [], 'right': []},
              'finger_joint_data_xzy': {'left': [], 'right': []}}
    tpose = {}
    tpose_isb = {}
    identity = {}

    get_count = lambda element: int(element) if element is not None else None
    frames['segment_count'] = get_count(frames_element.get('segmentCount'))
    frames['sensor_count'] = get_count(frames_element.get('sensorCount'))
    frames['joint_count'] = get_count(frames_element.get('jointCount'))
    frames['finger_joint_count'] = get_count(frames_element.get('fingerJointCount'))
    frame_elements = frames_element.findall('mvn:frame', ns)
    for frame_element in frame_elements:
        if frame_element.get('type') == 'normal':
            frames['time'].append(frame_element.get('time'))
            frames['joint_data'].append(
                get_joint_data_from_frame(frame_element, 'jointAngle', mvnx_file.file_data['joints']['names']))
            frames['joint_data_xzy'].append(
                get_joint_data_from_frame(frame_element, 'jointAngleXZY', mvnx_file.file_data['joints']['names']))
            frames['ergo_joint_data'].append(
                get_joint_data_from_frame(frame_element, 'jointAngleErgo', mvnx_file.file_data['ergo_joints']['names']))
            frames['ergo_joint_data_xzy'].append(
                get_joint_data_from_frame(frame_element, 'jointAngleErgoXZY', mvnx_file.file_data['ergo_joints']['names']))
            frames['segment_data'].append(
                get_segment_data_from_frame(frame_element, mvnx_file.file_data['segments']['names']))
            frames['sensor_data'].append(
                get_sensor_data_from_frame(frame_element, mvnx_file.file_data['sensors']['names']))
            frames['contacts_data'].append(
                get_contact_data_from_frame(frame_element, mvnx_file.file_data['foot_contact_def']))
            frames['finger_segment_data'].append(
                get_finger_data_from_frame(frame_element, mvnx_file.file_data['finger_segments']['names']))
            for side in frames['finger_joint_data']:
                element_name = 'jointAngleFingers' + side.capitalize()
                frames['finger_joint_data'][side].append(get_joint_data_from_frame(
                    frame_element, element_name, mvnx_file.file_data['finger_joints']['names'][side]))
                element_name = 'jointAngleFingers' + side.capitalize() + 'XZY'
                frames['finger_joint_data_xzy'][side].append(get_joint_data_from_frame(
                    frame_element, element_name, mvnx_file.file_data['finger_joints']['names'][side]))
        elif frame_element.get('type') == 'tpose':
            tpose = get_t_pose_data_from_frame(frame_element, mvnx_file.file_data['segments']['names'])
        elif frame_element.get('type') == 'tpose-isb':
            tpose_isb = get_t_pose_data_from_frame(frame_element, mvnx_file.file_data['segments']['names'])
        elif frame_element.get('type') == 'identity':
            identity = get_t_pose_data_from_frame(frame_element, mvnx_file.file_data['segments']['names'])

    return frames, tpose, tpose_isb, identity


def get_joint_data_from_frame(
        frame_element: ET.Element, joint_element_name: str,
        joint_names: List[str],
) -> Dict[str, np.ndarray]:
    """
    Extract joint data from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    joint_element_name : str
        Name of the frame sub-element to process (e.g. 'jointAngle').
    joint_names : list of str
        Joint names, in element order.

    Returns
    -------
    joint_data : dict of {str : ndarray}
        3-element angle vector per joint, indexed by joint name.
    """

    joint_data = collections.OrderedDict()

    angles = frame_element_as_floats(frame_element, joint_element_name)

    for index in range(len(joint_names)):
        joint_data[joint_names[index]] = get_3d_vector(angles, index)

    return joint_data


def get_t_pose_data_from_frame(
        frame_element: ET.Element, segment_names: List[str],
) -> Dict[str, Any]:
    """
    Extract pose data (position and orientation) from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    segment_names : list of str
        Segment names, in element order.

    Returns
    -------
    t_pose : dict
        Keys: 'segments_counts' (int) and 'segments' (list of dict,
        each with 'pos_g' and 'q_gb' ndarray entries).
    """

    t_pose = {'segments_counts': len(segment_names), 'segments': []}

    orientations = frame_element_as_floats(frame_element, 'orientation')
    offsets = frame_element_as_floats(frame_element, 'position')

    for index in range(len(segment_names)):
        segment = {'pos_g': get_3d_vector(offsets, index),
                   'q_gb': get_4d_vector(orientations, index)}
        t_pose['segments'].append(segment)

    return t_pose


def get_segment_data_from_frame(
        frame_element: ET.Element, segment_names: List[str],
) -> Dict[str, Any]:
    """
    Extract segment kinematics data from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    segment_names : list of str
        Segment names, in element order.

    Returns
    -------
    segment_data : dict of {str : dict}
        Per-segment dict with 'ori', 'pos', 'vel', 'acc', 'ang_vel',
        'ang_acc' ndarray entries, indexed by segment name. If the
        frame includes center-of-mass data, it is also present under
        the key 'com' (lowercase), with 'pos', 'vel', 'acc' entries.
    """

    segment_data = collections.OrderedDict()

    orientations = frame_element_as_floats(frame_element, 'orientation')
    offsets = frame_element_as_floats(frame_element, 'position')
    velocities = frame_element_as_floats(frame_element, 'velocity')
    accelerations = frame_element_as_floats(frame_element, 'acceleration')
    angular_velocity = frame_element_as_floats(frame_element, 'angularVelocity')
    angular_acceleration = frame_element_as_floats(frame_element, 'angularAcceleration')

    for index in range(len(segment_names)):
        segment_name = segment_names[index]
        segment_data[segment_name] = collections.OrderedDict()
        segment_data[segment_name]['ori'] = get_4d_vector(orientations, index)
        segment_data[segment_name]['pos'] = get_3d_vector(offsets, index)
        segment_data[segment_name]['vel'] = get_3d_vector(velocities, index)
        segment_data[segment_name]['acc'] = get_3d_vector(accelerations, index)
        segment_data[segment_name]['ang_vel'] = get_3d_vector(angular_velocity, index)
        segment_data[segment_name]['ang_acc'] = get_3d_vector(angular_acceleration, index)

    center_of_mass = frame_element_as_floats(frame_element, 'centerOfMass')
    if center_of_mass:
        segment_data['com'] = {'pos': [], 'vel': [], 'acc': []}
        index = 0
        for com_field in segment_data['com']:
            segment_data['com'][com_field] = get_3d_vector(center_of_mass, index)
            index += 1

    return segment_data


def get_sensor_data_from_frame(
        frame_element: ET.Element, sensor_names: List[str],
) -> Dict[str, Any]:
    """
    Extract sensor data from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    sensor_names : list of str
        Sensor names, in element order.

    Returns
    -------
    sensor_data : dict of {str : dict}
        Per-sensor dict with 'ori', 'mag', 'acc' ndarray entries,
        indexed by sensor name.
    """

    sensor_data = collections.OrderedDict()

    orientations = frame_element_as_floats(frame_element, 'sensorOrientation')
    free_accelerations = frame_element_as_floats(frame_element, 'sensorFreeAcceleration')
    magnetic_field = frame_element_as_floats(frame_element, 'sensorMagneticField')

    for index in range(len(sensor_names)):
        sensor_name = sensor_names[index]
        sensor_data[sensor_name] = collections.OrderedDict()
        sensor_data[sensor_name]["ori"] = get_4d_vector(orientations, index)
        sensor_data[sensor_name]["mag"] = get_4d_vector(magnetic_field, index)
        sensor_data[sensor_name]["acc"] = get_3d_vector(free_accelerations, index)

    return sensor_data


def get_finger_data_from_frame(
        frame_element: ET.Element, finger_segment_names: Dict[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Extract finger tracking data from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    finger_segment_names : dict of {str : list of str}
        Finger segment names per side, keyed by 'left'/'right'.

    Returns
    -------
    finger_data : dict of {str : dict}
        Per-side ('left'/'right') dict of per-segment dicts with
        'ori' and 'pos' ndarray entries, indexed by finger segment
        name.
    """

    finger_data = {'left': {}, 'right': {}}

    for side in finger_data:
        orientations = frame_element_as_floats(frame_element, 'orientationFingers' + side.capitalize())
        offsets = frame_element_as_floats(frame_element, 'positionFingers' + side.capitalize())

        for index in range(len(finger_segment_names[side])):
            finger_name = finger_segment_names[side][index]
            finger_data[side][finger_name] = collections.OrderedDict()
            finger_data[side][finger_name]["ori"] = get_4d_vector(orientations, index)
            finger_data[side][finger_name]["pos"] = get_3d_vector(offsets, index)

    return finger_data


def get_contact_data_from_frame(
        frame_element: ET.Element, foot_contact_def: Dict[int, Dict],
) -> List[Dict]:
    """
    Extract foot-contact event data from a frame.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The frame element to process.
    foot_contact_def : dict of {int : dict}
        Foot contact definitions indexed by contact index, as parsed
        by :func:`load_mvnx` from the ``footContactDefinition``
        element.

    Returns
    -------
    contact_data : list of dict
        One contact-definition dict (each with 'type',
        'segment_index', 'point_index' keys) per active contact in
        this frame.
    """

    contact_data = []
    element_value = frame_element.find('mvn:footContacts', ns)
    if element_value is not None:
        contacts = [int(value) for value in element_value.text.split(' ')]

        for index in range(len(contacts)):
            if contacts[index] == 1:
                contact_data.append(foot_contact_def[index])

    return contact_data


def frame_element_as_floats(
        frame_element: ET.Element, element: str,
) -> List[float]:
    """
    Find a named sub-element, split its text, and return the values
    as a list of floats.

    Parameters
    ----------
    frame_element : xml.etree.ElementTree.Element
        The mvnx frame element to process.
    element : str
        Name of the sub-element to find.

    Returns
    -------
    values : list of float
        Parsed values, or an empty list if the sub-element is absent.
    """

    element_value = frame_element.find('mvn:' + element, ns)
    return [float(value) for value in element_value.text.split(' ')] if element_value is not None else []


def get_4d_vector(raw_vector: List[float], index: int) -> np.ndarray:
    """Slice a 4-element (e.g. quaternion) vector at ``index``."""
    return np.array(raw_vector[index * 4:index * 4 + 4])


def get_3d_vector(raw_vector: List[float], index: int) -> np.ndarray:
    """Slice a 3-element (e.g. XYZ) vector at ``index`` from a flat list."""
    return np.array(raw_vector[index * 3:index * 3 + 3])


def init_file_data(mvnx_file: MvnxFileAccessor) -> None:
    """Initialize ``mvnx_file.file_data`` with the empty data tree."""
    meta_data = {'version': '',
                 'original_filename': '',
                 'rec_date': '',
                 'name': '',
                 'color': '',
                 'comments': '',
                 'scenario': '',
                 'quality': '',
                 'sample_rate': 240}

    mvnx_file.file_data = {'segments': {},
                           'finger_segments': {'names': {'left': {}, 'right': {}},
                                               'elements': {'left': collections.OrderedDict(),
                                                            'right': collections.OrderedDict()}},
                           'sensors': {'names': [], 'elements': collections.OrderedDict()},
                           'joints': {'names': [], 'elements': collections.OrderedDict()},
                           'ergo_joints': {'names': [], 'elements': collections.OrderedDict()},
                           'finger_joints': {'names': {'left': {}, 'right': {}},
                                             'elements': {'left': collections.OrderedDict(),
                                                          'right': collections.OrderedDict()}},
                           'foot_contact_def': {},
                           'frames': {},
                           'tpose': {},
                           'tpose_isb': {},
                           'identity': {},
                           'meta_data': meta_data}
