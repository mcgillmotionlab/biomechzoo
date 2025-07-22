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

    # todo add relevant meta data to zoosystem
    data['zoosystem'] = {}

    return data
