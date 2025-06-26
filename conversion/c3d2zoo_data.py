def c3d2zoo_data(c3d_obj):
    """ converts a c3d obj loaded from ezc3d to zoo format"""
    data = {}

    # todo: expand this to forces, analog, etc.
    if 'points' in c3d_obj['data']:
        points = c3d_obj['data']['points']
        labels = c3d_obj['parameters']['POINT']['LABELS']['value']
        for i, label in enumerate(labels):
            data[label] = points[:3, i, :].T  # shape: (frames, 3)
    return data