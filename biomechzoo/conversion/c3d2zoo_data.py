def c3d2zoo_data(c3d_obj):
    """
    Converts an ezc3d C3D object to zoo format.

    Returns:
    - data (dict): Zoo dictionary with 'line' and 'event' fields per channel.
    """
    data = {}

    if 'points' in c3d_obj['data']:
        points = c3d_obj['data']['points']  # shape: (4, n_markers, n_frames)
        labels = c3d_obj['parameters']['POINT']['LABELS']['value']
        for i, label in enumerate(labels):
            line_data = points[:3, i, :].T  # shape: (frames, 3)
            data[label] = {
                'line': line_data,
                'event': {}  # empty for now
            }

        params = c3d_obj['parameters']
        video_freq = c3d_obj['parameters']['POINT']['RATE']['value'][0]
        if 'EVENT' in params and 'TIMES' in params['EVENT']:
            times_array = params['EVENT']['TIMES']['value']
            frames = times_array[1]  # second row = frames (or time, depending on C3D file)

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
                        data['SACR']['event'][key_name] = [frame, 0, 0]
                    else:
                        data[labels[0]]['event'][key_name] = [frame, 0, 0]

    # todo add relevant meta data to zoosystem
    data['zoosystem'] = params['EVENT']

    return data
