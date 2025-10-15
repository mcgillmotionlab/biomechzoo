from biomechzoo.utils.set_zoosystem import set_zoosystem

def c3d2zoo_data(c3d_obj):
    """
    Converts an ezc3d C3D object to zoo format.

    Returns:
    - data (dict): Zoo dictionary with 'line' and 'event' fields per channel.
    """
    data = {}
    data['zoosystem'] = set_zoosystem()
    video_freq = None
    analog_freq = None
    # extract "video" data
    if 'points' in c3d_obj['data']:
        points = c3d_obj['data']['points']  # shape: (4, n_markers, n_frames)
        labels = list(c3d_obj['parameters']['POINT']['LABELS']['value'])
        video_freq = int(c3d_obj['parameters']['POINT']['RATE']['value'][0])
        for i, label in enumerate(labels):
            line_data = points[:3, i, :].T  # shape: (frames, 3)
            data[label] = {
                'line': line_data,
                'event': {}  # empty for now
            }

        data['zoosystem']['Video']['Freq'] = video_freq
        data['zoosystem']['Video']['Channels'] = labels

    if 'analogs' in c3d_obj['data']:
        analog_data = c3d_obj['data']['analogs']  # shape: (subframes, n_analog_channels, n_frames)
        analog_labels = list(c3d_obj['parameters']['ANALOG']['LABELS']['value'])
        analog_freq = int(c3d_obj['parameters']['ANALOG']['RATE']['value'][0])
        # Flatten to 2D: (n_samples, n_channels)
        # ezc3d stores analogs as subframes per frame, so we flatten across all
        n_subframes, n_channels, n_frames = analog_data.shape
        analog_data = analog_data.reshape(n_subframes * n_frames, n_channels)

        for i, label in enumerate(analog_labels):
            line_data = analog_data[:, i].reshape(-1, 1)  # shape: (samples, 1)
            data[label] = {
                'line': line_data,
                'event': {},
            }

        data['zoosystem']['Analog']['Freq'] = analog_freq
        data['zoosystem']['Analog']['Channels'] = analog_labels

    # extract event information
    params = c3d_obj['parameters']
    if 'EVENT' in params and 'TIMES' in params['EVENT']:
        if 'points' in c3d_obj['data']:
            times_array = params['EVENT']['TIMES']['value']
            frames = times_array[1]  # should be time depending on C3D file

            # Extract sides, types, subjects
            contexts = params['EVENT']['CONTEXTS']['value'] if 'CONTEXTS' in params['EVENT'] else ['']
            labels = params['EVENT']['LABELS']['value']
            subjects = params['EVENT']['SUBJECTS']['value'] if 'SUBJECTS' in params['EVENT'] else ['']

            events = {}

            for i in range(len(labels)):
                side = contexts[i].strip()
                label = labels[i].strip()
                subject = subjects[i].strip()

                # Event channel name: e.g. 'Right_FootStrike' -> 'RightFootStrike'
                event_name = f"{side}_{label}".replace(' ', '')
                event_name = ''.join(c for c in event_name if c.isalnum() or c == '_')  # make it a valid field name

                if event_name not in events:
                    events[event_name] = []

                events[event_name].append(frames[i])  # This is in seconds or frame number?

            original_start = 1

            for event_name, time_list in events.items():
                # Clean and sort times
                valid_times = sorted([t for t in time_list if t != 0])
                for j, time_val in enumerate(valid_times):
                    frame = round(time_val * video_freq) - original_start + 1  # MATLAB logic
                    key_name = f"{event_name}{j + 1}"

                    # Place in correct channel
                    if 'SACR' in data:
                        data['SACR']['event'][key_name] = [frame-1, 0, 0]       # remove 1 to follow python
                    else:
                        data[labels[0]]['event'][key_name] = [frame-1, 0, 0]    # remove 1 to follow python

    # add more zoosystem
    if analog_freq is not None and video_freq is not None:
        data['zoosystem']['AVR'] = analog_freq/video_freq

    return data
