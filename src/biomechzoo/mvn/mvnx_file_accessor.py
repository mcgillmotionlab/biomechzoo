import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

from biomechzoo.mvn import mvn


class MvnxFileAccessor:
    """Read/query accessor for a parsed .mvnx (Xsens MVN) file's data tree."""

    @property
    def original_file_name(self) -> str:
        """str: Original recorded file name."""
        return self.file_data['meta_data']['original_filename']

    @property
    def actor_name(self) -> str:
        """str: Name of the recorded actor."""
        return self.file_data['meta_data']['name']

    @property
    def actor_color(self) -> str:
        """str: Display color assigned to the actor."""
        return self.file_data['meta_data']['color']

    @property
    def profile(self) -> str:
        """str: Filter profile/scenario used for the recording."""
        return self.file_data['meta_data']['scenario']

    @property
    def configuration(self) -> str:
        """str: Sensor/segment configuration used for the recording."""
        return self.file_data['meta_data']['configuration']

    @property
    def comments(self) -> str:
        """str: Free-text comments stored with the recording."""
        return self.file_data['meta_data']['comments']

    @property
    def quality(self) -> str:
        """str: Recording quality indicator."""
        return self.file_data['meta_data']['quality']

    @property
    def frame_count(self) -> int:
        """int: Number of frames in the current frame window."""
        return self._last_frame - self._first_frame

    @property
    def segment_count(self) -> int:
        """int: Number of segments in the recording."""
        return self.file_data['frames']['segment_count']

    @property
    def joint_count(self) -> int:
        """int: Number of joints in the recording."""
        return self.file_data['frames']['joint_count']

    @property
    def finger_joint_count(self) -> Optional[int]:
        """int or None: Number of finger joints in the recording, if any."""
        return self.file_data['frames']['finger_joint_count']

    @property
    def ergo_joint_count(self) -> Optional[int]:
        """int or None: Number of ergo joints, or None if not present."""
        ergo_joint_count = len(self.file_data['ergo_joints']) if self.file_data['ergo_joints'] is not None else None
        return ergo_joint_count  # 'ergoJointCount' non-existing in mvnx

    @property
    def sensor_count(self) -> int:
        """int: Number of sensors in the recording."""
        return self.file_data['frames']['sensor_count']

    @property
    def frame_rate(self) -> int:
        """int: Sample rate in Hz, or 240 (with a warning) if not recorded."""
        if 'sample_rate' in self.file_data['meta_data']:
            return int(self.file_data['meta_data']['sample_rate'])
        else:
            warnings.warn('Using default sample rate of 240')
            return 240

    @property
    def recording_date(self) -> str:
        """str: Date the recording was made."""
        return self.file_data['meta_data']['rec_date']

    @property
    def version(self) -> str:
        """str: mvnx file format version."""
        return self.file_data['meta_data']['version']

    def __init__(self) -> None:
        self.file_data = {}
        self._all_frames_slice = None
        self._first_frame = 0
        self._last_frame = 0
        self._index_to_segment = {}

    def create_index_to_segment_dict(self) -> None:
        """Populate ``self._index_to_segment`` from ``file_data``."""
        segment_index = 0
        for _, segment in self.file_data['segments']['elements'].items():
            if 'label' in segment:
                self._index_to_segment[segment_index] = segment['label']
            segment_index += 1

    def set_frame_window(self, first_frame: int, last_frame: int) -> None:
        """
        Restrict subsequent queries to a specific frame range.

        Parameters
        ----------
        first_frame : int
            Index of the first frame in the window.
        last_frame : int
            Index one past the last frame in the window.
        """
        self._first_frame = first_frame
        self._last_frame = last_frame
        self._all_frames_slice = slice(self._first_frame, self._last_frame)

    def reset_frame_window(self) -> None:
        """Reset the frame window to cover all recorded frames."""
        self._first_frame = 0
        self._last_frame = len(self.file_data['frames']['segment_data'])
        self._all_frames_slice = slice(self._first_frame, self._last_frame)

    def window_profile(self) -> str:
        """
        Determine the filter profile (scenario) for the current frame window.

        Returns
        -------
        profile : str
            The profile name (singleLevel, multiLevel, ...), or 'mixed'
            if different profiles were applied within the window.
        """
        if 'profiles' not in self.file_data['meta_data']:
            return self.profile
        else:
            profiles = set()
            for profile_spec in self.file_data['meta_data']['profiles']:
                if profile_spec[1] > self._first_frame and profile_spec[0] <= self._last_frame:
                    profiles.add(profile_spec[2])

            if len(profiles) == 1:
                return profiles.pop()
            else:
                return 'mixed'

    def frame_to_mapped_slice(
            self, frame: Union[int, slice],
    ) -> Tuple[slice, bool]:
        """
        Convert a frame parameter to a slice mapped to the current
        frame window.

        Parameters
        ----------
        frame : int or slice
            Frame index, a slice of frames, or ``mvn.FRAMES_ALL`` for
            all frames in the current window.

        Returns
        -------
        frame : slice
            The frame(s) mapped into the current window.
        single_frame : bool
            True if ``frame`` referred to a single frame.
        """
        # convert the frame parameter to a slice that is mapped to the current view on the file
        single_frame = False
        if not isinstance(frame, slice):
            if frame == mvn.FRAMES_ALL:
                # all frames slice already is mapped to the current view
                self.reset_frame_window()
                frame = self._all_frames_slice  # use the prepared 'all frames' slice
            else:
                # for a single frame, map the frame to the current view on all data by adding the virtual first frame
                frame = slice(self._first_frame + frame, self._first_frame + frame + 1)  # create a single frame slice
                single_frame = True
        else:
            # shift the slice to the current virtual 'view'
            start = frame.start + self._first_frame
            if frame.stop:
                stop = frame.stop + self._first_frame
            else:  # a slice with end given as None implies end at last frame
                stop = self._last_frame
            step = frame.step
            frame = slice(start, stop, step)

        return frame, single_frame

    def segment_name_from_index(self, segment_index: int) -> str:
        """Look up a segment's name from its index."""
        return self._index_to_segment[segment_index]

    def point_name_from_indices(
            self, segment_index: int, point_index: int,
    ) -> str:
        """Look up a point's name from its segment and point index."""
        segment_name = self.segment_name_from_index(segment_index)
        segment = self.file_data['segments']['elements'][segment_name]
        return segment['info']['point_label_from_index'][point_index]

    """ Pose methods """

    def identity_pose_is_valid(self) -> bool:
        """Check whether an identity pose is present with segments."""
        return ('identity' in self.file_data) and \
               (self.identity_pose()['segments_counts'] > 0)

    def identity_pose_segment_pos(self, segment: str) -> Any:
        """Get a segment's position in the identity pose, by segment name."""
        return self.identity_pose()['segments'][segment]['pos_g']

    def identity_pose_segment_ori(self, segment: str) -> Any:
        """Get a segment's orientation in the identity pose, by name."""
        return self.identity_pose()['segments'][segment]['q_gb']

    def t_pose_is_valid(self) -> bool:
        """Check whether a T-pose is present with segments."""
        return ('tpose' in self.file_data) and \
               (self.t_pose()['segments_counts'] > 0)

    def t_pose_segment_pos(self, segment: str) -> Any:
        """Get a segment's position in the T-pose, by segment name."""
        return self.t_pose()['segments'][segment]['pos_g']

    def t_pose_segment_ori(self, segment: str) -> Any:
        """Get a segment's orientation in the T-pose, by segment name."""
        return self.t_pose()['segments'][segment]['q_gb']

    def identity_pose(self) -> Dict:
        """Get the raw identity pose data."""
        return self.file_data['identity']

    def t_pose(self) -> Dict:
        """Get the raw T-pose data."""
        return self.file_data['tpose']

    """ Segment methods """

    def get_segment_pos(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the position information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with position values.
        """
        return self.get_segment_data('pos', segment, frame, axis)

    def get_segment_ori(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the orientation information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with orientation values.
        """
        # For orientation data, if all axes requested, return all. If specific axis requested, shift index so that w,
        # x,y,z becomes 0,1,2,3
        axis = (axis + 1) % 4 if axis != mvn.AXIS_ALL else axis
        return self.get_segment_data('ori', segment, frame, axis)

    def get_segment_point_pos(self, segment: int, point: int) -> Any:
        """
        Get a specific point's position on a segment.

        Notes
        -----
        Currently raises ``KeyError`` for any segment: it reads
        ``self.file_data['segments'][segment_name]``, but segments are
        actually nested one level deeper, under
        ``self.file_data['segments']['elements'][segment_name]`` (see
        :func:`create_index_to_segment_dict`, which uses the correct path).
        """
        segment_name = mvn.SEGMENTS[segment]
        segment_info = self.file_data['segments'][segment_name]
        points = segment_info['info']['point_label_from_index']
        point_name = points[point]
        return segment_info['points_mvn'][point_name]

    def get_point_pos(self, segment: int, point: int) -> Any:
        """
        Get a named foot/toe point's position on a segment.

        Notes
        -----
        Currently raises ``KeyError`` for any segment, for the same
        reason as :func:`get_segment_point_pos`: it is missing the
        ``['elements']`` level in the path to ``self.file_data['segments']``.
        """
        segment_name = mvn.SEGMENTS[segment]

        if segment_name == 'LeftFoot':
            point_name = mvn.POINTS_LEFT_FOOT[point]
        elif segment_name == 'RightFoot':
            point_name = mvn.POINTS_RIGHT_FOOT[point]
        elif segment_name == 'LeftToe':
            point_name = mvn.POINTS_LEFT_TOE[point]
        elif segment_name == 'RightToe':
            point_name = mvn.POINTS_RIGHT_TOE[point]

        return self.file_data['segments'][segment_name]['points_mvn'][point_name]

    def get_segment_vel(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the local velocity information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with velocity values.
        """
        return self.get_segment_data('vel', segment, frame, axis)

    def get_segment_acc(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the acceleration information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with acceleration values.
        """
        return self.get_segment_data('acc', segment, frame, axis)

    def get_segment_angular_vel(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the angular velocity information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with angular velocity values.
        """
        return self.get_segment_data('ang_vel', segment, frame, axis)

    def get_segment_angular_acc(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the angular acceleration information for a segment.

        Parameters
        ----------
        segment : int
            Index of the segment to return the data for (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with angular acceleration
        values.
        """
        return self.get_segment_data('ang_acc', segment, frame, axis)

    def get_segment_data(
            self, data_field: str, segment: int,
            frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """Get a named data field (pos/ori/vel/acc/...) for a segment."""
        return self.get_data('segment_data', data_field, segment, frame, axis)

    """ Joint methods """

    def get_joint_angle(
            self, joint: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            angle: int = mvn.ANGLE_ALL,
    ) -> Union[Any, List[Any]]:
        """Get a joint's angle(s) (mvn.JOINTS) for the given frame(s)."""
        joint_name = mvn.JOINTS[joint]
        data_set = 'joint_data'

        frame, is_single_frame = self.frame_to_mapped_slice(frame)

        if angle == mvn.ANGLE_ALL:
            return_values = [value[joint_name] for value in self.file_data['frames'][data_set][frame]]
        else:
            return_values = [value[joint_name][angle] for value in self.file_data['frames'][data_set][frame]]

        return return_values[0] if is_single_frame else return_values

    def get_joint_angle_xzy(
            self, joint: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            angle: int = mvn.ANGLE_ALL,
    ) -> Union[Any, List[Any]]:
        """Get a joint's XZY-ordered angle(s) for the given frame(s)."""
        joint_name = mvn.JOINTS[joint]
        data_set = 'joint_data_xzy'

        frame, is_single_frame = self.frame_to_mapped_slice(frame)

        if angle == mvn.ANGLE_ALL:
            return_values = [value[joint_name] for value in self.file_data['frames'][data_set][frame]]
        else:
            return_values = [value[joint_name][angle] for value in self.file_data['frames'][data_set][frame]]

        return return_values[0] if is_single_frame else return_values

    def get_ergo_joint_angle(
            self, joint: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            angle: int = mvn.ANGLE_ALL,
    ) -> Union[Any, List[Any]]:
        """Get an ergo joint's angle(s) (mvn.ERGO_JOINTS) for a frame."""
        joint_name = mvn.ERGO_JOINTS[joint]
        data_set = 'ergo_joint_data'

        frame, is_single_frame = self.frame_to_mapped_slice(frame)

        if angle == mvn.ANGLE_ALL:
            return_values = [value[joint_name] for value in self.file_data['frames'][data_set][frame]]
        else:
            return_values = [value[joint_name][angle] for value in self.file_data['frames'][data_set][frame]]

        return return_values[0] if is_single_frame else return_values

    """ Center of Mass methods """

    def get_center_of_mass_pos(
            self, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the position information for center of mass.

        Parameters
        ----------
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with position values.

        Notes
        -----
        Currently raises ``KeyError('CoM')`` unconditionally: it passes
        ``mvn.SEGMENT_CENTER_OF_MASS`` (1000) through to
        :func:`get_data`, which looks it up via ``mvn.SEGMENTS[1000]``
        ('CoM') and indexes ``self.file_data['frames']['segment_data']``
        with that name -- but center-of-mass data isn't stored under
        the regular per-segment keys there (only real segment names
        like 'Pelvis' are). ``get_data`` does have a separate special
        case for ``segment == -1`` mapped to ``'com'``, but nothing
        currently calls it with -1.
        """
        return self.get_segment_data('pos', mvn.SEGMENT_CENTER_OF_MASS, frame, axis)

    def get_center_of_mass_vel(
            self, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the velocity information for center of mass.

        Parameters
        ----------
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with velocity values.

        Notes
        -----
        Currently raises ``KeyError('CoM')`` unconditionally -- see
        :func:`get_center_of_mass_pos` for the reason.
        """
        return self.get_segment_data('vel', mvn.SEGMENT_CENTER_OF_MASS, frame, axis)

    def get_center_of_mass_acc(
            self, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the acceleration information for center of mass.

        Parameters
        ----------
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with acceleration values.

        Notes
        -----
        Currently raises ``KeyError('CoM')`` unconditionally -- see
        :func:`get_center_of_mass_pos` for the reason.
        """
        return self.get_segment_data('acc', mvn.SEGMENT_CENTER_OF_MASS, frame, axis)

    """ Sensor methods """

    def get_sensor_ori(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the orientation information for a sensor.

        Parameters
        ----------
        segment : int
            Index of the segment to return the sensor data for
            (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with orientation values.
        """
        # if all axes requested, return all. If specific axis requested, shift index so that w,x,y,z becomes 0,1,2,3
        axis = (axis + 1) % 4 if axis != mvn.AXIS_ALL else axis
        return self.get_sensor_data('ori', segment, frame, axis)

    def get_sensor_free_acc(
            self, segment: int, frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get the free acceleration information for a sensor.

        Parameters
        ----------
        segment : int
            Index of the segment to return the sensor data for
            (mvn.SEGMENT_...).
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with acceleration values.
        """
        return self.get_sensor_data('acc', segment, frame, axis)

    def get_sensor_data(
            self, data_field: str, sensor_segment: int,
            frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """Get a named data field (ori/acc/...) for a sensor segment."""
        return self.get_data('sensor_data', data_field, sensor_segment, frame, axis)

    """ Contact methods """

    def get_foot_contacts(
            self, frame: Union[int, slice],
    ) -> Union[List[Dict], List[List[Dict]]]:
        """
        Get the foot-contact events for a frame.

        Parameters
        ----------
        frame : int or slice
            The frame, or a range of frames, to retrieve contacts for.

        Returns
        -------
        contacts : list of dict, or list of list of dict
            For a single frame, a list of contact-event dicts (each
            with 'type', 'segment_index', 'point_index' keys). For a
            range of frames, one such list per frame. Note this is a
            list of events, not the integer bitmask the parameter name
            'foot_contact_flags' in :func:`has_foot_contact` implies.
        """
        frame, is_single_frame = self.frame_to_mapped_slice(frame)
        return_values = self.file_data['frames']['contacts_data'][frame] #edited Phil Dixon
        return return_values[0] if is_single_frame else return_values

    def has_foot_contact(
            self, frame: Union[int, slice], foot_contact_flags: int = 0,
    ) -> Union[bool, List[bool]]:
        """
        Check whether a frame has a foot contact.

        Parameters
        ----------
        frame : int or slice
            The frame (or range) to retrieve the contacts for.
        foot_contact_flags : int, optional
            The specific contact to check for: ``mvn.FOOT_CONTACT_LEFT_HEEL``,
            ``mvn.FOOT_CONTACT_LEFT_TOE``, ``mvn.FOOT_CONTACT_RIGHT_HEEL``,
            or ``mvn.FOOT_CONTACT_RIGHT_TOE``. Flags may be combined by
            summing them to match any of them. Passing 0 (default)
            returns True if there is any contact.

        Returns
        -------
        has_contact : bool or list of bool
            Per-frame True if a contact was found, False otherwise.

        Notes
        -----
        This method assumes :func:`get_foot_contacts` returns an
        integer bitmask per frame, but it actually returns a list of
        contact-event dicts (see that method's docstring). As a
        result the ``isinstance(frame_contacts, int)`` check below is
        never true for real data, and the bitwise comparisons in both
        branches operate on the wrong types. Calling this method with
        real parsed data currently raises a ``TypeError``.
        """
        frame_contacts = self.get_foot_contacts(frame)  # frame will be shifted in the called method

        if isinstance(frame_contacts, int):
            if foot_contact_flags == 0:
                return frame_contacts > 0
            else:
                return True if (frame_contacts & foot_contact_flags) > 0 else False
        else:
            has_contacts = []
            for contacts in frame_contacts:
                if foot_contact_flags == 0:
                    has_contacts.append(frame_contacts > 0)
                else:
                    has_contacts.append(True if (contacts & foot_contact_flags) > 0 else False)
            return has_contacts

    """ Generic methods """

    def get_data(
            self, data_set: str, data_field: str, segment: int,
            frame: Union[int, slice] = mvn.FRAMES_ALL,
            axis: int = mvn.AXIS_ALL,
    ) -> Union[Any, List[Any]]:
        """
        Get a named data field for a segment/sensor from a given data set.

        Parameters
        ----------
        data_set : str
            Data set to read from (e.g. 'segment_data', 'sensor_data',
            'joint_data').
        data_field : str
            Field within the data set to read (e.g. 'pos', 'ori').
        segment : int
            Index of the segment (mvn.SEGMENT_...), or -1 for center of mass.
        frame : int or slice, optional
            Index of the frame to return, a slice to return a range of
            frames, or ``mvn.FRAMES_ALL`` (default) to return all frames.
        axis : int, optional
            Axis to return the data for (``mvn.AXIS_...``, or
            ``mvn.AXIS_ALL`` for all axes).

        Returns
        -------
        A single value, list, or list of lists with the requested data.
        """
        if segment == -1:
            segment_name = 'com'
        else:
            segment_name = mvn.SEGMENTS[segment]

        frame, is_single_frame = self.frame_to_mapped_slice(frame)
        if data_set == 'joint_data':
            return_values = [value[data_field] for value in self.file_data['frames'][data_set][frame]]
        elif axis == mvn.AXIS_ALL:
            return_values = [value[segment_name][data_field] for value in self.file_data['frames'][data_set][frame]]
        else:
            return_values = [value[segment_name][data_field][axis] for value in
                             self.file_data['frames'][data_set][frame]]

        return return_values[0] if is_single_frame else return_values
